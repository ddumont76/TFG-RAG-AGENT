from fastapi import APIRouter, HTTPException
from app.services.retrieval_service import retrieve_documents
from app.services.enrichment_service import enrich_ticket_results, enrich_docs_results

router = APIRouter(prefix="/search")

@router.get("/tickets")
async def search_tickets(query: str, top_k: int = 5, score_threshold: float = 0.6):
    """Buscar únicamente en tickets.

    Filtra resultados con similitud baja (score > threshold se descartan).
    Los scores más bajos indican mayor similitud.
    """
    try:
        tickets_results, _ = retrieve_documents(query, top_k * 2)

        enriched_tickets = enrich_ticket_results(tickets_results)

        filtered_tickets = [
            ticket
            for ticket in enriched_tickets
            if ticket["score"] is None or ticket["score"] > score_threshold
        ][:top_k]

        return {
            "query": query,
            "tickets": filtered_tickets,
            "count": len(filtered_tickets),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error buscando tickets: {str(e)}",
        )


@router.get("/docs")
async def search_docs(query: str, top_k: int = 5, score_threshold: float = 0.6):
    """Buscar únicamente en documentos de Confluence."""
    try:
        _, docs_results = retrieve_documents(query, top_k * 2)

        enriched_docs = enrich_docs_results(docs_results)

        filtered_docs = [
            doc
            for doc in enriched_docs
            if doc["score"] is None or doc["score"] > score_threshold
        ][:top_k]

        return {
            "query": query,
            "docs": filtered_docs,
            "count": len(filtered_docs),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error buscando documentos: {str(e)}",
        )