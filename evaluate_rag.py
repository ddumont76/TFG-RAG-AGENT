"""
Evaluación RAGAS para  sistema RAG local.
Versión completamente síncrona (compatible con RAGAS 0.1.4).
"""

import json
from datetime import datetime
from sentence_transformers import SentenceTransformer
import chromadb

from app.rag.evaluation import evaluate_batch, METRIC_RANGES
from app.rag.agent import RAGAgent

from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import HuggingFaceEmbeddings


# Modelos para RAGAS
ragas_llm = ChatOllama(model="qwen2.5:0.5b")
ragas_embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")


def retrieve_contexts(query: str, top_k: int = 5):
    """Recupera documentos contextuales desde ChromaDB."""
    client = chromadb.PersistentClient(path="chroma_db")

    embedding_model = SentenceTransformer(
        "BAAI/bge-m3",
        trust_remote_code=True
    )

    tickets_collection = client.get_collection("tickets")
    docs_collection = client.get_collection("docs")

    query_embedding = embedding_model.encode(query).tolist()

    tickets_results = tickets_collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    docs_results = docs_collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    contexts = []

    if tickets_results.get("documents"):
        contexts.extend(tickets_results["documents"][0])

    if docs_results.get("documents"):
        contexts.extend(docs_results["documents"][0])

    return contexts


def generate_answer(query: str, contexts: list) -> str:
    """Genera respuesta usando el agente RAG local."""
    try:
        rag_agent = RAGAgent(model_name="qwen2.5:0.5b", use_local=True)

        tickets = [{"id": f"ticket_{i}", "content": ctx} for i, ctx in enumerate(contexts)]
        docs = [{"id": f"doc_{i}", "content": ctx} for i, ctx in enumerate(contexts)]

        result = rag_agent.query(query, tickets, docs)
        return result.answer

    except Exception as e:
        return f"Error generando respuesta: {str(e)}"


def run_evaluation_batch():
    """Ejecuta evaluación en lote sobre consultas predefinidas."""

    test_queries = [
        "¿Cómo resolver errores 403 en Jenkins?",
        "¿Qué es CrashLoopBackOff en Kubernetes?",
        "¿Cuáles son los errores comunes de permisos en S3?",
    ]

    print("=" * 80)
    print("🧪 EVALUACIÓN RAGAS - Sistema RAG")
    print("=" * 80)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    queries = []
    answers = []
    contexts_list = []

    print("📊 Procesando consultas...\n")

    for i, query in enumerate(test_queries, 1):
        print(f"{i}. Query: {query}")

        contexts = retrieve_contexts(query, top_k=3)
        print(f"   Contextos recuperados: {len(contexts)}")

        answer = generate_answer(query, contexts)
        print(f"   Respuesta generada: {answer[:100]}...\n")

        queries.append(query)
        answers.append(answer)
        contexts_list.append(contexts)

    print("\n📈 Calculando métricas RAGAS...\n")
    
    print(">>> RESPUESTAS QUE SE VAN A EVALUAR:")
    for r in answers:           print("-", r)


    results = evaluate_batch(
        queries,
        answers,
        contexts_list,
        llm=ragas_llm,
        embeddings=ragas_embeddings
    )

    print("\n" + "=" * 80)
    print("📊 RESULTADOS DE EVALUACIÓN")
    print("=" * 80 + "\n")

    metrics = results.get("metrics", {})
    avg_score = results.get("avg_score", 0)

    print(f"Score promedio general: {avg_score:.4f}\n")

    for metric_name, metric_value in metrics.items():
        info = METRIC_RANGES.get(metric_name, {})
        print(f"🎯 {metric_name.upper()}: {metric_value:.4f}")
        print(f"   Descripción: {info.get('desc', 'N/A')}")
        print(f"   Rango: {info.get('range', 'N/A')}")
        print()

    report = {
        "timestamp": datetime.now().isoformat(),
        "total_queries": len(queries),
        "metrics": metrics,
        "average_score": avg_score,
        "queries": queries,
        "answers": [ans[:200] for ans in answers],
    }

    report_file = "evaluation_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"📄 Reporte guardado en: {report_file}\n")

    return results


if __name__ == "__main__":
    run_evaluation_batch()