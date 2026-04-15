"""
Evaluación RAGAS para RAG local con ChatOllama + BGE-M3.
Las métricas RAGAS se ejecutan en un contexto asíncrono independiente mediante asyncio.to_thread, evitando conflictos con el event loop de FastAPI (uvloop).
 Esta aproximación mantiene la arquitectura del sistema y asegura compatibilidad con entornos de producción
"""
"""
Evaluación RAGAS para RAG local con ChatOllama + BGE-M3.
Compatible con FastAPI + uvicorn (sin nested event loop).
"""

from typing import Dict, Any, Optional
import asyncio

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)

from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import HuggingFaceEmbeddings


class RAGEvaluator:
    """Evaluador RAGAS con interfaz asíncrona segura para FastAPI."""

    def __init__(self, llm=None, embeddings=None):
        self.llm = llm or ChatOllama(model="qwen2.5:0.5b")
        self.embeddings = embeddings or HuggingFaceEmbeddings(
            model_name="BAAI/bge-m3"
        )

        self.metrics = [
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall,
        ]

    # ------------------------
    # Dataset preparation
    # ------------------------
    def _prepare_dataset(self, queries, answers, contexts, ground_truths=None):
        data = {
            "question": queries,
            "answer": answers,
            "contexts": contexts,
        }

        if ground_truths:
            data["ground_truth"] = ground_truths

        return Dataset.from_dict(data)

    # ------------------------
    # Sync evaluation (RAGAS)
    # ------------------------
    def _evaluate_sync(self, queries, answers, contexts, ground_truths=None):
        dataset = self._prepare_dataset(
            queries, answers, contexts, ground_truths
        )

        results = evaluate(
            dataset=dataset,
            metrics=self.metrics,
            llm=self.llm,
            embeddings=self.embeddings,
        )

        return {
            "metrics": results,
            "avg_score": sum(results.values()) / len(results),
            "status": "success",
        }

    # ------------------------
    # Async public API (SAFE)
    # ------------------------
    async def evaluate_async(self, queries, answers, contexts, ground_truths=None):
        """
        Ejecuta RAGAS en un thread separado para evitar conflictos
        con el event loop de FastAPI / uvicorn.
        """
        return await asyncio.to_thread(
            self._evaluate_sync,
            queries,
            answers,
            contexts,
            ground_truths,
        )

    # ------------------------
    # Batch evaluation
    # ------------------------
    @classmethod
    async def evaluate_batch(
        cls,
        queries,
        answers,
        contexts,
        ground_truths=None,
        llm=None,
        embeddings=None,
    ):
        evaluator = cls(llm=llm, embeddings=embeddings)
        return await evaluator.evaluate_async(
            queries, answers, contexts, ground_truths
        )

    # ------------------------
    # Single query evaluation
    # ------------------------
    async def evaluate_single_query(
        self,
        query: str,
        answer: str,
        contexts: list,
        ground_truth: Optional[str] = None,
    ) -> Dict[str, Any]:

        return await self.evaluate_async(
            queries=[query],
            answers=[answer],
            contexts=[contexts],  # lista de listas
            ground_truths=[ground_truth] if ground_truth else None,
        )


# ------------------------
# Metadata for UI / Docs
# ------------------------
METRIC_RANGES = {
    "faithfulness": {
        "desc": "¿Qué tan fiel es la respuesta al contexto recuperado?",
        "range": "0.0 = infiel, 1.0 = totalmente fiel",
    },
    "answer_relevancy": {
        "desc": "¿Qué tan relevante es la respuesta respecto a la pregunta?",
        "range": "0.0 = no relevante, 1.0 = muy relevante",
    },
    "context_precision": {
        "desc": "¿Cuánto del contexto recuperado fue realmente usado?",
        "range": "0.0 = nada usado, 1.0 = todo usado",
    },
    "context_recall": {
        "desc": "¿Qué tan completo es el contexto respecto a la respuesta?",
        "range": "0.0 = incompleto, 1.0 = completo",
    },
}
