"""
Evaluación RAG en modo FAST — versión totalmente independiente.
No importa FastAPI ni main.py.
Replica EXACTAMENTE el pipeline real.
"""

import os
import json
import chromadb
from sentence_transformers import SentenceTransformer
from ragas import evaluate
from ragas.metrics import answer_relevancy
from langchain_community.chat_models import ChatOllama

# ============================
# 1. CARGA DE DATOS (igual que en main.py)
# ============================

from app.ingest.load_corpus import load_tickets, load_confluence_docs
from app.rag.agent import RAGAgent

TICKETS_DATA = {t["id"]: t for t in load_tickets()}
DOCS_DATA = {d["id"]: d for d in load_confluence_docs()}

# ============================
# 2. INICIALIZACIÓN DE CHROMA Y EMBEDDINGS
# ============================

client = chromadb.PersistentClient(path="chroma_db")
embedding_model = SentenceTransformer("BAAI/bge-m3")

tickets_collection = client.get_or_create_collection(name="tickets")
docs_collection = client.get_or_create_collection(name="docs")

# ============================
# 3. FUNCIONES DE ENRIQUECIMIENTO (copiadas de main.py)
# ============================

def enrich_ticket_results(tickets_results):
    enriched = []
    for i, doc in enumerate(tickets_results["documents"][0]):
        ticket_id = tickets_results["ids"][0][i]
        score = tickets_results["distances"][0][i] if "distances" in tickets_results else None
        info = TICKETS_DATA.get(ticket_id, {})
        enriched.append({
            "id": ticket_id,
            "summary": info.get("summary", "N/A"),
            "description": info.get("description", ""),
            "comments": info.get("comments", []),
            "content": doc,
            "score": score
        })
    return enriched


def enrich_docs_results(docs_results):
    enriched = []
    for i, doc in enumerate(docs_results["documents"][0]):
        doc_id = docs_results["ids"][0][i]
        score = docs_results["distances"][0][i] if "distances" in docs_results else None
        info = DOCS_DATA.get(doc_id, {})
        enriched.append({
            "id": doc_id,
            "title": info.get("title", "N/A"),
            "content": info.get("content", doc),
            "score": score
        })
    return enriched

# ============================
# 4. RETRIEVAL REAL (copiado de main.py)
# ============================

def retrieve_documents(query: str, top_k: int = 5):
    query_embedding = embedding_model.encode(query).tolist()

    tickets_results = tickets_collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    docs_results = docs_collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    return tickets_results, docs_results

# ============================
# 5. AGENTE RAG REAL (copiado de main.py)
# ============================

def get_rag_agent(provider="ollama", model="qwen2.5:0.5b"):
    use_local = provider == "ollama"
    return RAGAgent(model_name=model, provider=provider, use_local=use_local)

# ============================
# 6. CONFIGURACIÓN RAGAS
# ============================

os.environ["RAGAS_MAX_WORKERS"] = "2"

ragas_llm = ChatOllama(
    model="qwen2.5:0.5b",
    options={"temperature": 0.0}
)

# ============================
# 7. QUERIES PARA FAST MODE
# ============================

queries = [
    "¿Cómo resolver errores 403 en Jenkins?",
    "¿Qué es CrashLoopBackOff en Kubernetes?",
    "¿Cuáles son los errores comunes de permisos en S3?"
]

answers = []
contexts = []

print("\n🚀 Ejecutando evaluación FAST independiente...\n")

# ============================
# 8. PIPELINE REAL
# ============================

agent = get_rag_agent()

for q in queries:
    print(f"🔍 Query: {q}")

    tickets_results, docs_results = retrieve_documents(q, top_k=5)

    enriched_tickets = enrich_ticket_results(tickets_results)
    enriched_docs = enrich_docs_results(docs_results)

    rag_result = agent.query(q, enriched_tickets, enriched_docs)
    answers.append(rag_result.answer)

    ctx = [t["content"] for t in enriched_tickets] + \
          [d["content"] for d in enriched_docs]

    contexts.append(ctx)

# ============================
# 9. EVALUACIÓN RAGAS
# ============================

print("\n📈 Calculando métricas RAGAS...\n")

dataset = {
    "question": queries,
    "answer": answers,
    "contexts": contexts,
    "ground_truth": []
}

results = evaluate(
    dataset,
    metrics=[answer_relevancy],
    llm=ragas_llm,
    n_samples=1,
    raise_exceptions=False
)

# ============================
# 10. RESULTADOS
# ============================

print("\n==============================================")
print("📊 RESULTADOS FAST MODE (INDEPENDIENTE)")
print("==============================================\n")

for metric, score in results.items():
    print(f"{metric.upper()}: {score:.4f}")

with open("evaluation_report_fast.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=4, ensure_ascii=False)

print("\n📄 Reporte guardado en: evaluation_report_fast.json\n")
print("✨ Evaluación rápida completada.")