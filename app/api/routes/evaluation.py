from fastapi import APIRouter, HTTPException
from app.api.schemas import EvaluationRequest, EvaluationResponse
from app.api.metric_ranges import METRIC_RANGES
from app.rag.evaluation import RAGEvaluator

router = APIRouter()


@router.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_response(request: EvaluationRequest):
    """Evalúa la calidad de una respuesta RAG usando métricas RAGAS.

    Calcula:
    - Faithfulness: Fidelidad de la respuesta a los documentos
    - Answer Relevancy: Relevancia de la respuesta a la consulta
 
    """
    try:
        evaluator = RAGEvaluator()

        results = await evaluator.evaluate_single_query(
            query=request.query,
            answer=request.answer,
            contexts=request.contexts,
            ground_truth=request.ground_truth,
        ) or {}

        return EvaluationResponse(
            query=request.query,
            answer=request.answer,
            metrics=results.get("metrics", {}),
            avg_score=results.get("avg_score", 0),
            metric_descriptions=METRIC_RANGES,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error evaluando respuesta: {str(e)}",
        )
