from fastapi import APIRouter, HTTPException
from app.services.retrieval_service import retrieve_documents

router = APIRouter()


@router.get("/health")
async def health_check():
    """Verifica el estado básico del sistema (API + vector store)."""
    try:
        # Prueba mínima: asegurarse de que Chroma + embeddings responden
        retrieve_documents("health_check", top_k=1)

        return {
            "status": "healthy",
            "message": "RAG Agent API está funcionando correctamente y puede acceder al vector store.",
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"System unhealthy: {str(e)}",
        )