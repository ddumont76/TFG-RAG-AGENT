from fastapi.templating import Jinja2Templates
from fastapi import Request

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any

from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.rag.agent import RAGAgent

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

# Agente RAG
rag_agent = RAGAgent(model_name="mistral", use_local=True)


class QueryRequest(BaseModel):
    query: str
    top_k: int = 5


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

        tickets = []
        for i, doc in enumerate(tickets_results["documents"][0]):
            tickets.append({
                "id": tickets_results["ids"][0][i],
                "content": doc,
                "score": tickets_results["distances"][0][i] if "distances" in tickets_results else None
            })

        docs = []
        for i, doc in enumerate(docs_results["documents"][0]):
            docs.append({
                "id": docs_results["ids"][0][i],
                "content": doc,
                "score": docs_results["distances"][0][i] if "distances" in docs_results else None
            })

        rag_result = rag_agent.query(request.query, tickets, docs)

        return QueryResponse(
            query=rag_result.query,
            answer=rag_result.answer,
            tickets=rag_result.tickets_used,
            docs=rag_result.docs_used,
            model_name=rag_result.model_name,
            processing_time=rag_result.processing_time,
            total_sources=rag_result.total_sources,
            confidence_score=rag_result.confidence_score,
            metadata=rag_result.metadata
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando la consulta: {str(e)}")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.api.main:app", host="0.0.0.0", port=8000, reload=True)