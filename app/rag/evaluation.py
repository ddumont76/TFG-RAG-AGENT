"""
Evaluación RAG usando RAGAS (sin ground truth).

Dado que el sistema RAG opera sobre información dinámica y no dispone de un conjunto de respuestas de referencia, 
la evaluación se realiza mediante métricas RAGAS que no requieren ground truth, como faithfulness y answer relevancy,
siguiendo prácticas habituales en sistemas RAG reales.

Métricas:
- faithfulness
- answer_relevancy
"""

import asyncio
from typing import List, Optional, Dict, Any

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy

from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import HuggingFaceEmbeddings

from app.api.metric_ranges import METRIC_RANGES


class RAGEvaluator:
    """
    Evaluador RAGAS compatible con FastAPI.
    Ejecuta RAGAS fuera del event loop para evitar errores async.
    """

    def __init__(self, llm=None, embeddings=None):
        self.llm = llm or ChatOllama(model="qwen2.5:0.5b")

        self.embeddings = embeddings or HuggingFaceEmbeddings(
            model_name="BAAI/bge-m3"
        )

        # ✅ SOLO métricas sin reference
        self.metrics = [
            faithfulness,
            answer_relevancy,
        ]

        
    def _normalize_scores(self, scores: Any) -> Dict[str, float]:
        """
        Normaliza la salida de RAGAS a un dict[str, float].
        En esta pipeline RAG, RAGAS devuelve siempre una lista de diccionarios.
        """

        # Caso normal: lista de diccionarios
        if isinstance(scores, list) and scores:
            return {k: float(v) for k, v in scores[0].items()}

        # Caso alternativo: dict directo
        if isinstance(scores, dict):
            return {k: float(v) for k, v in scores.items()}

        # Cualquier otro caso no esperado
        return {}



    # ------------------------------------------------------------
    # Ejecución sync (RAGAS)
     #Dado que RAGAS devuelve los resultados de evaluación mediante 
     #objetos dinámicos sin tipado estático explícito, se emplea una
     #normalización manual del contrato de salida, tratándolo como Any 
     #y extrayendo las métricas esperadas. Esta aproximación es habitual 
     #en sistemas basados en LLMs y garantiza compatibilidad con herramientas 
     #de análisis estático sin afectar al comportamiento en tiempo de ejecución.
    # ------------------------------------------------------------
    def _evaluate_sync(
        self,
        queries: List[str],
        answers: List[str],
        contexts: List[List[str]],
    ) -> Dict[str, Any]:

        dataset = Dataset.from_dict(
            {
                "question": queries,
                "answer": answers,
                "contexts": contexts,
            }
        )
                    
                
        
        results_any: Any = evaluate(
            dataset=dataset,
            metrics=self.metrics,
            llm=self.llm,
            embeddings=self.embeddings,
        )

        metrics = self._normalize_scores(results_any.scores)

        avg_score = (
            sum(metrics.values()) / len(metrics)
            if metrics
            else 0.0
        )

        return {
            "metrics": metrics,
            "avg_score": avg_score,
            "metric_ranges": METRIC_RANGES,
        }


    # ------------------------------------------------------------
    # API pública async
    # ------------------------------------------------------------
    async def evaluate_single_query(
        self,
        query: str,
        answer: str,
        contexts: List[str],
        ground_truth: Optional[str] = None,  # intencionadamente ignorado
    ) -> Dict[str, Any]:

        if not contexts:
            return {
                "metrics": {},
                "avg_score": 0.0,
                "metric_ranges": METRIC_RANGES,
            }

        return await asyncio.to_thread(
            self._evaluate_sync,
            [query],
            [answer],
            [contexts],
        )