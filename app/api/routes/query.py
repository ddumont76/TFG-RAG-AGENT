from fastapi import APIRouter, HTTPException
from app.api.schemas import QueryRequest, QueryResponse, QueryWithChunkingRequest
from app.services.retrieval_service import retrieve_documents
from app.services.enrichment_service import enrich_ticket_results, enrich_docs_results
from app.services.rag_agent_service import get_rag_agent

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    """
    Ejecuta una consulta RAG completa (retrieval + generación).
    La evaluación RAGAS se realiza en un endpoint independiente (/evaluate).
    """
    try:
        # 1️⃣ Retrieval
        tickets_results, docs_results = retrieve_documents(
            request.query, request.top_k
        )

        enriched_tickets = enrich_ticket_results(tickets_results)
        enriched_docs = enrich_docs_results(docs_results)

        # 2️⃣ Generación
        current_rag_agent = get_rag_agent(request.provider, request.model)

        if current_rag_agent is None:
            answer = (
                f"Lo siento, el agente RAG no está disponible. "
                f"Se encontraron {len(enriched_tickets)} tickets y "
                f"{len(enriched_docs)} documentos relacionados con "
                f"'{request.query}'."
            )
            model_name = "N/A"
        else:
            rag_result = current_rag_agent.query(
                request.query, enriched_tickets, enriched_docs
            )
            answer = rag_result.answer
            model_name = current_rag_agent.model_name

        # 3️⃣ Métricas básicas (NO RAGAS)
        confidence = min(
            (len(enriched_tickets) + len(enriched_docs)) * 0.1,
            1.0
        )

        basic_metrics = {
            "tickets_found": len(enriched_tickets),
            "docs_found": len(enriched_docs),
            "total_sources": len(enriched_tickets) + len(enriched_docs),
            "avg_ticket_score": (
                sum(t.get("score", 0) for t in enriched_tickets)
                / len(enriched_tickets)
                if enriched_tickets else 0
            ),
            "avg_doc_score": (
                sum(d.get("score", 0) for d in enriched_docs)
                / len(enriched_docs)
                if enriched_docs else 0
            ),
            "processing_time": 0.1  # placeholder
        }

        # 4️⃣ Respuesta final
        return QueryResponse(
            query=request.query,
            answer=answer,
            tickets=enriched_tickets,
            docs=enriched_docs,
            model_name=model_name,
            processing_time=basic_metrics["processing_time"],
            total_sources=basic_metrics["total_sources"],
            confidence_score=confidence,
            metadata={
                "rag_agent_available": current_rag_agent is not None,
                "provider": request.provider,
                "model": request.model
            },
            metrics=basic_metrics
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando la consulta: {str(e)}",
        )


@router.get("/ask")
async def ask_rag(query: str, top_k: int = 5):
    """Endpoint alternativo para consultas RAG vía GET."""
    try:
        tickets_results, docs_results = retrieve_documents(query, top_k)

        enriched_tickets = enrich_ticket_results(tickets_results)
        enriched_docs = enrich_docs_results(docs_results)

        current_rag_agent = get_rag_agent()

        if current_rag_agent is None:
            answer = (
                f"Agente RAG no disponible. "
                f"Encontrados {len(enriched_tickets)} tickets y "
                f"{len(enriched_docs)} documentos."
            )
            model_name = "N/A"
        else:
            rag_result = current_rag_agent.query(
                query, enriched_tickets, enriched_docs
            )
            answer = rag_result.answer
            model_name = current_rag_agent.model_name

        return QueryResponse(
            query=query,
            answer=answer,
            tickets=enriched_tickets,
            docs=enriched_docs,
            model_name=model_name,
            processing_time=0.1,
            total_sources=len(enriched_tickets) + len(enriched_docs),
            confidence_score=min(
                (len(enriched_tickets) + len(enriched_docs)) * 0.1,
                1.0
            ),
            metadata={"rag_agent_available": current_rag_agent is not None},
            metrics={}
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando la consulta: {str(e)}",
        )


@router.post("/query-with-chunking", response_model=QueryResponse)
async def query_with_chunking(request: QueryWithChunkingRequest):
    """Ejecuta una consulta RAG usando una estrategia de chunking específica."""
    try:
        base_request = QueryRequest(
            query=request.query,
            top_k=request.top_k,
            provider=request.provider,
            model=request.model,
        )
        return await query_rag(base_request)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en consulta con chunking: {str(e)}",
        )