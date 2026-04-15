from fastapi import APIRouter, HTTPException
from app.ingest.chunking_strategies import ChunkingFactory, compare_chunking_strategies
from app.api.schemas import ChunkingCompareRequest, ChunkingCompareResponse

router = APIRouter()


@router.get("/chunking-strategies")
async def get_chunking_strategies():
    """Devuelve las estrategias de chunking disponibles."""
    try:
        strategies = ChunkingFactory.get_available_strategies()
        return {
            "available_strategies": strategies,
            "count": len(strategies),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo estrategias: {str(e)}",
        )


@router.post("/compare-chunking", response_model=ChunkingCompareResponse)
async def compare_chunking(request: ChunkingCompareRequest):
    """Compara múltiples estrategias de chunking."""
    try:
        results = compare_chunking_strategies(
            request.text, request.strategies
        )

        if results:
            num_chunks_list = [
                r.get("num_chunks", 0)
                for r in results.values()
                if "error" not in r
            ]

            comparison = {
                "best_strategy_for_chunks": min(
                    (
                        (k, v["num_chunks"])
                        for k, v in results.items()
                        if "error" not in v
                    ),
                    key=lambda x: x[1],
                    default=(None, 0),
                )[0],
                "best_strategy_for_avg_size": min(
                    (
                        (k, v["avg_chunk_size"])
                        for k, v in results.items()
                        if "error" not in v
                    ),
                    key=lambda x: x[1],
                    default=(None, 0),
                )[0],
                "min_chunks": min(num_chunks_list) if num_chunks_list else 0,
                "max_chunks": max(num_chunks_list) if num_chunks_list else 0,
                "avg_chunks": (
                    sum(num_chunks_list) / len(num_chunks_list)
                    if num_chunks_list
                    else 0
                ),
            }
        else:
            comparison = {}

        return ChunkingCompareResponse(
            results=results, comparison=comparison
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error comparando chunking: {str(e)}",
        )