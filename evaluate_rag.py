"""
Script de evaluación RAGAS para pruebas batch.
Evalúa múltiples consultas y genera reporte de métricas.
"""

import json
import asyncio
from datetime import datetime
from app.rag.evaluation import evaluate_batch, METRIC_RANGES
from app.rag.agent import RAGAgent
from app.ingest.load_corpus import load_tickets, load_confluence_docs
import chromadb
from sentence_transformers import SentenceTransformer


def retrieve_contexts(query: str, top_k: int = 5):
    """Recupera documentos contextuales para una consulta."""
    client = chromadb.PersistentClient(path="chroma_db")
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    
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
    tickets_docs = tickets_results.get("documents", [[]])
    if tickets_docs and len(tickets_docs) > 0:
        contexts.extend([doc for doc in tickets_docs[0]])
    
    docs_docs = docs_results.get("documents", [[]])
    if docs_docs and len(docs_docs) > 0:
        contexts.extend([doc for doc in docs_docs[0]])
    
    return contexts


def generate_answer(query: str, contexts: list) -> str:
    """Genera respuesta usando el agente RAG."""
    try:
        rag_agent = RAGAgent(model_name="mistral", use_local=True)
        
        # Convertir contextos a formato esperado
        tickets = [{"id": f"ticket_{i}", "content": ctx} for i, ctx in enumerate(contexts)]
        docs = [{"id": f"doc_{i}", "content": ctx} for i, ctx in enumerate(contexts)]
        
        result = rag_agent.query(query, tickets, docs)
        return result.answer
    except Exception as e:
        return f"Error generando respuesta: {str(e)}"


async def run_evaluation_batch():
    """Ejecuta evaluación en lote sobre consultas predefinidas."""
    
    # Consultas de prueba
    test_queries = [
        "¿Cómo resolver errores 403 en Jenkins?",
        "¿Qué es CrashLoopBackOff en Kubernetes?",
        "¿Cuáles son los errores comunes de permisos en S3?",
    ]
    
    print("=" * 80)
    print("🧪 EVALUACIÓN RAGAS - Sistema RAG")
    print("=" * 80)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Preparar datos
    queries = []
    answers = []
    contexts_list = []
    
    print("📊 Procesando consultas...\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f"{i}. Query: {query}")
        
        # Recuperar contextos
        contexts = retrieve_contexts(query, top_k=3)
        print(f"   Contextos recuperados: {len(contexts)}")
        
        # Generar respuesta
        answer = generate_answer(query, contexts)
        print(f"   Respuesta generada: {answer[:100]}...\n")
        
        queries.append(query)
        answers.append(answer)
        contexts_list.append(contexts)
    
    # Evaluar batch
    print("\n📈 Calculando métricas RAGAS...\n")
    
    if asyncio.iscoroutinefunction(evaluate_batch):
        results = await evaluate_batch(queries, answers, contexts_list)
    else:
        results = evaluate_batch(queries, answers, contexts_list)
    
    # Mostrar resultados
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
    
    # Guardar reporte
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_queries": len(queries),
        "metrics": metrics,
        "average_score": avg_score,
        "queries": queries,
        "answers": [ans[:200] for ans in answers],  # Truncar para el reporte
    }
    
    report_file = "evaluation_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"📄 Reporte guardado en: {report_file}\n")
    
    return results


if __name__ == "__main__":
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(run_evaluation_batch())
    except Exception as e:
        print(f"❌ Error en evaluación: {str(e)}")
        import traceback
        traceback.print_exc()
