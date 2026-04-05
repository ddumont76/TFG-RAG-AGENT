import json
from app.rag.agent import RAGAgent
from app.rag.retriever import TicketRetriever, DocumentRetriever

# Preguntas que quieres evaluar
queries = [
    "¿Cómo resolver errores 403 en Jenkins?",
    "¿Qué es CrashLoopBackOff en Kubernetes?",
    "¿Cuáles son los errores comunes de permisos en S3?"
]

# Inicializar agente y retrievers
agent = RAGAgent(model_name="qwen2.5:0.5b")
ticket_retriever = TicketRetriever()
document_retriever = DocumentRetriever()

answers = []
contexts = []
ground_truths = []  # Si no tienes ground truth, lo dejamos vacío

for q in queries:
    print(f"\n🔍 Procesando query: {q}")

    # Recuperar contexto
    tickets = ticket_retriever.search(q, top_k=5)
    docs = document_retriever.search(q, top_k=5)

    # Llamar al agente con tickets y docs
    result = agent.query(q, tickets=tickets, docs=docs)

    answers.append(result.answer)
    contexts.append({
        "tickets": tickets,
        "docs": docs
    })

# Crear archivo JSON
data = {
    "queries": queries,
    "answers": answers,
    "contexts": contexts,
    "ground_truths": ground_truths
}

with open("evaluation_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print("\n✅ evaluation_data.json generado correctamente.")