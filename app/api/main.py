from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import chromadb
import os
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any

from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.ingest.load_corpus import load_tickets, load_confluence_docs
from app.rag.agent import RAGAgent

# Variables globales para cache de datos (cargadas de forma lazy)
TICKETS_DATA = None
DOCS_DATA = None

def get_tickets_data():
    """Carga datos de tickets de forma lazy."""
    global TICKETS_DATA
    if TICKETS_DATA is None:
        TICKETS_DATA = {ticket['id']: ticket for ticket in load_tickets()}
    return TICKETS_DATA

def get_docs_data():
    """Carga datos de documentos de forma lazy."""
    global DOCS_DATA
    if DOCS_DATA is None:
        DOCS_DATA = {doc['id']: doc for doc in load_confluence_docs()}
    return DOCS_DATA


def enrich_ticket_results(tickets_results):
    """Enriquece resultados de tickets con información completa."""
    tickets_data = get_tickets_data()
    enriched_tickets = []
    for i, doc in enumerate(tickets_results["documents"][0]):
        ticket_id = tickets_results["ids"][0][i]
        score = tickets_results["distances"][0][i] if "distances" in tickets_results else None
        
        # Obtener información completa del ticket
        ticket_info = tickets_data.get(ticket_id, {})
        
        enriched_tickets.append({
            "id": ticket_id,
            "summary": ticket_info.get('summary', 'N/A'),
            "description": ticket_info.get('description', ''),
            "comments": ticket_info.get('comments', []),
            "content": doc,
            "score": score
        })
    
    return enriched_tickets


def enrich_docs_results(docs_results):
    """Enriquece resultados de documentos con información completa."""
    docs_data = get_docs_data()
    enriched_docs = []
    for i, doc in enumerate(docs_results["documents"][0]):
        doc_id = docs_results["ids"][0][i]
        score = docs_results["distances"][0][i] if "distances" in docs_results else None
        
        # Obtener información completa del documento
        doc_info = docs_data.get(doc_id, {})
        
        enriched_docs.append({
            "id": doc_id,
            "title": doc_info.get('title', 'N/A'),
            "content": doc_info.get('content', doc),
            "score": score
        })
    
    return enriched_docs

app = FastAPI(title="RAG Agent API", description="API for Data & IA RAG Agent", version="1.0.0")
templates = Jinja2Templates(directory="app/api/templates")

# Static & templates
app.mount("/static", StaticFiles(directory="app/api/static"), name="static")
templates = Jinja2Templates(directory="app/api/templates")


# Inicializar componentes
client = chromadb.PersistentClient(path="chroma_db")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

tickets_collection = client.get_or_create_collection(name="tickets")
docs_collection = client.get_or_create_collection(name="docs")

# Agente RAG (inicialización diferida)
rag_agent = None

def get_rag_agent(provider: str = "mock", model: str = "mistral"):
    """Obtiene el agente RAG, inicializándolo si es necesario."""
    global rag_agent
    print(f"🔍 Solicitando agente con provider={provider}, model={model}")
    print(f"🔍 Agente actual: {rag_agent.provider if rag_agent else 'None'}, {rag_agent.model_name if rag_agent else 'None'}")
    
    if rag_agent is None or rag_agent.provider != provider or rag_agent.model_name != model:
        print(f"🔄 Reinicializando agente...")
        provider = provider.strip().lower()
        model_name = model.strip().lower()
        use_local = provider == "ollama"

        try:
            rag_agent = RAGAgent(model_name=model_name, provider=provider, use_local=use_local)
            print(f"✅ Agente RAG inicializado correctamente con provider: {provider}, model: {model_name}")
        except Exception as e:
            print(f"⚠️ Error inicializando agente RAG: {e}")
            print("Continuando sin agente RAG - endpoints de búsqueda funcionarán")
    else:
        print(f"♻️ Reutilizando agente existente")
    return rag_agent


@app.get("/health")
async def health_check():
    """Verifica el estado del sistema y cuenta de documentos indexados."""
    try:
        tickets_count = tickets_collection.count()
        docs_count = docs_collection.count()
        return {
            "status": "healthy",
            "tickets_indexed": tickets_count,
            "docs_indexed": docs_count,
            "total_sources": tickets_count + docs_count
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


class QueryRequest(BaseModel):
    query: str
    top_k: int = 5
    provider: str = "mock"  # ollama, openai, mock
    model: str = "mistral"  # mistral, phi-4


class QueryResponse(BaseModel):
    query: str
    answer: str
    tickets: List[Dict[str, Any]]
    docs: List[Dict[str, Any]]
    model_name: str
    processing_time: float
    total_sources: int
    confidence_score: float
    metadata: Dict[str, Any]
    metrics: Dict[str, float] = {}


class EvaluationRequest(BaseModel):
    query: str
    answer: str
    contexts: List[str]
    ground_truth: str = None


class EvaluationResponse(BaseModel):
    query: str
    answer: str
    metrics: Dict[str, float]
    avg_score: float
    metric_descriptions: Dict[str, Dict[str, str]]


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


@app.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    try:
        tickets_results, docs_results = retrieve_documents(request.query, request.top_k)

        # Enriquecer resultados con información completa
        enriched_tickets = enrich_ticket_results(tickets_results)
        enriched_docs = enrich_docs_results(docs_results)

        # Obtener agente RAG con el provider y model especificados
        current_rag_agent = get_rag_agent(request.provider, request.model)
        
        if current_rag_agent is None:
            # Respuesta básica sin LLM
            answer = f"Lo siento, el agente RAG no está disponible. Se encontraron {len(enriched_tickets)} tickets y {len(enriched_docs)} documentos relacionados con: '{request.query}'"
            model_name = "N/A"
        else:
            rag_result = current_rag_agent.query(request.query, enriched_tickets, enriched_docs)
            answer = rag_result.answer
            model_name = current_rag_agent.model_name

        # Calcular confianza básica
        confidence = min((len(enriched_tickets) + len(enriched_docs)) * 0.1, 1.0)

        # Calcular métricas básicas
        metrics = {
            "tickets_found": len(enriched_tickets),
            "docs_found": len(enriched_docs),
            "total_sources": len(enriched_tickets) + len(enriched_docs),
            "avg_ticket_score": sum(t.get("score", 0) for t in enriched_tickets) / len(enriched_tickets) if enriched_tickets else 0,
            "avg_doc_score": sum(d.get("score", 0) for d in enriched_docs) / len(enriched_docs) if enriched_docs else 0,
            "processing_time": 0.1  # Placeholder, se puede medir real
        }

        return QueryResponse(
            query=request.query,
            answer=answer,
            tickets=enriched_tickets,
            docs=enriched_docs,
            model_name=model_name,
            processing_time=metrics["processing_time"],
            total_sources=metrics["total_sources"],
            confidence_score=confidence,
            metadata={"rag_agent_available": current_rag_agent is not None, "provider": request.provider, "model": request.model},
            metrics=metrics
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando la consulta: {str(e)}")

@app.get("/ask")
async def ask_rag(query: str, top_k: int = 5):
    """Endpoint alternativo para consultas RAG via GET (útil para navegadores)."""
    try:
        tickets_results, docs_results = retrieve_documents(query, top_k)

        # Enriquecer resultados con información completa
        enriched_tickets = enrich_ticket_results(tickets_results)
        enriched_docs = enrich_docs_results(docs_results)

        # Obtener agente RAG (inicialización lazy)
        current_rag_agent = get_rag_agent()

        if current_rag_agent is None:
            # Respuesta básica sin LLM
            answer = f"Agente RAG no disponible. Encontrados {len(enriched_tickets)} tickets y {len(enriched_docs)} documentos."
        else:
            rag_result = current_rag_agent.query(query, enriched_tickets, enriched_docs)
            answer = rag_result.answer

        return QueryResponse(
            query=query,
            answer=answer,
            tickets=enriched_tickets,
            docs=enriched_docs,
            model_name="mistral" if current_rag_agent else "N/A",
            processing_time=0.1,
            total_sources=len(enriched_tickets) + len(enriched_docs),
            confidence_score=min((len(enriched_tickets) + len(enriched_docs)) * 0.1, 1.0),
            metadata={"rag_agent_available": current_rag_agent is not None}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando la consulta: {str(e)}")

'''Por defecto que filtra resultados con similitud baja (score > 0.6 se descartan).
Los scores más bajos indican mayor similitud. Ahora solo devuelve resultados realmente relevantes.
Puedes ajustar la precisión:

score_threshold=0.5 → Más estricto (menos resultados)
score_threshold=0.7 → Más permisivo (más resultados)
Ejemplo: GET /search/tickets?query=jenkins&score_threshold=0.5'''
@app.get("/search/tickets")
async def search_tickets(query: str, top_k: int = 5, score_threshold: float = 0.6):
    """Buscar únicamente en tickets."""
    try:
        tickets_results, _ = retrieve_documents(query, top_k * 2)  # Buscar más para filtrar
        
        # Enriquecer resultados con información completa
        enriched_tickets = enrich_ticket_results(tickets_results)
        
        # Filtrar por umbral de similitud
        filtered_tickets = [
            ticket for ticket in enriched_tickets 
            if ticket['score'] is None or ticket['score'] > score_threshold
        ][:top_k]  # Limitar a top_k
        
        return {
            "query": query,
            "tickets": filtered_tickets,
            "count": len(filtered_tickets)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error buscando tickets: {str(e)}")

@app.get("/search/docs")
async def search_docs(query: str, top_k: int = 5, score_threshold: float = 0.6):
    """Buscar únicamente en documentos de Confluence."""
    try:
        _, docs_results = retrieve_documents(query, top_k * 2)  # Buscar más para filtrar
        
        # Enriquecer resultados con información completa
        enriched_docs = enrich_docs_results(docs_results)
        
        # Filtrar por umbral de similitud
        filtered_docs = [
            doc for doc in enriched_docs 
            if doc['score'] is None or doc['score'] > score_threshold
        ][:top_k]  # Limitar a top_k
        
        return {
            "query": query,
            "docs": filtered_docs,
            "count": len(filtered_docs)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error buscando documentos: {str(e)}")

@app.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_response(request: EvaluationRequest):
    """Evalúa la calidad de una respuesta RAG usando métricas RAGAS.
    
    Calcula:
    - Faithfulness: Fidelidad de la respuesta a los documentos
    - Answer Relevancy: Relevancia de la respuesta a la consulta
    - Context Precision: Precisión de los documentos recuperados
    - Context Recall: Recall de los documentos recuperados
    """
    try:
        evaluator = RAGEvaluator()
        
        # Evaluar la respuesta
        results = evaluator.evaluate_single_query(
            query=request.query,
            answer=request.answer,
            contexts=request.contexts,
            ground_truth=request.ground_truth
        )
        
        metrics = results.get("metrics", {})
        avg_score = results.get("avg_score", 0)
        
        return EvaluationResponse(
            query=request.query,
            answer=request.answer,
            metrics=metrics,
            avg_score=avg_score,
            metric_descriptions=METRIC_RANGES
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evaluando respuesta: {str(e)}")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request, "index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.api.main:app", host="0.0.0.0", port=8000, reload=True)