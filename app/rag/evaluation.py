"""
Módulo de evaluación RAGAS para métricas de RAG.
Calcula: Precision, Recall, Faithfulness y Answer Relevance.
"""

import os
import asyncio
from typing import List, Dict, Any
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall
)


class RAGEvaluator:
    """Evaluador de sistemas RAG usando RAGAS."""
    
    def __init__(self):
        """Inicializa el evaluador RAGAS."""
        self.metrics = [
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall
        ]
    
    def prepare_dataset(
        self,
        queries: List[str],
        answers: List[str],
        contexts: List[List[str]],
        ground_truths: List[str] = None
    ) -> Dataset:
        """
        Prepara dataset para RAGAS.
        
        Args:
            queries: Lista de consultas
            answers: Lista de respuestas generadas
            contexts: Lista de listas de contextos recuperados
            ground_truths: Lista de respuestas correctas (opcional)
        
        Returns:
            Dataset en formato RAGAS
        """
        data = {
            "question": queries,
            "answer": answers,
            "contexts": contexts,
        }
        
        if ground_truths:
            data["ground_truth"] = ground_truths
        
        return Dataset.from_dict(data)
    
    async def evaluate_async(
        self,
        queries: List[str],
        answers: List[str],
        contexts: List[List[str]],
        ground_truths: List[str] = None
    ) -> Dict[str, Any]:
        """
        Evalúa respuestas RAG de forma asincrónica.
        
        Args:
            queries: Lista de consultas
            answers: Lista de respuestas
            contexts: Lista de contextos recuperados
            ground_truths: Respuestas correctas (opcional)
        
        Returns:
            Diccionario con métricas RAGAS
        """
        dataset = self.prepare_dataset(queries, answers, contexts, ground_truths)
        
        try:
            results = evaluate(dataset, metrics=self.metrics)
            return self._format_results(results)
        except Exception as e:
            return {
                "error": f"Error en evaluación RAGAS: {str(e)}",
                "metrics": {}
            }
    
    def _format_results(self, results: Dict[str, float]) -> Dict[str, Any]:
        """Formatea resultados de RAGAS."""
        return {
            "metrics": {
                "faithfulness": results.get("faithfulness", 0),
                "answer_relevancy": results.get("answer_relevancy", 0),
                "context_precision": results.get("context_precision", 0),
                "context_recall": results.get("context_recall", 0),
            },
            "avg_score": sum(results.values()) / len(results) if results else 0,
            "status": "success"
        }
    
    def evaluate_single_query(
        self,
        query: str,
        answer: str,
        contexts: List[str],
        ground_truth: str = None
    ) -> Dict[str, Any]:
        """
        Evalúa una única consulta (sincrónico).
        
        Args:
            query: Consulta realizada
            answer: Respuesta generada
            contexts: Documentos contextuales recuperados
            ground_truth: Respuesta correcta (opcional)
        
        Returns:
            Métricas de evaluación
        """
        # Ejecutar evaluación asincrónica en loop de evento
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        results = loop.run_until_complete(
            self.evaluate_async([query], [answer], [contexts], [ground_truth] if ground_truth else None)
        )
        
        return results


def evaluate_batch(
    queries: List[str],
    answers: List[str],
    contexts: List[List[str]],
    ground_truths: List[str] = None
) -> Dict[str, Any]:
    """
    Función de conveniencia para evaluar un lote de resultados.
    
    Args:
        queries: Lista de consultas
        answers: Lista de respuestas
        contexts: Lista de contextos recuperados
        ground_truths: Respuestas correctas (opcional)
    
    Returns:
        Métricas agregadas
    """
    evaluator = RAGEvaluator()
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(
        evaluator.evaluate_async(queries, answers, contexts, ground_truths)
    )


# Métricas individuales para interpretación
METRIC_RANGES = {
    "faithfulness": {
        "desc": "Mide qué tan fiel es la respuesta a los documentos recuperados (0-1)",
        "range": "0.0 = Totalmente infiel, 1.0 = Perfectamente fiel"
    },
    "answer_relevancy": {
        "desc": "Mide qué tan relevante es la respuesta a la consulta (0-1)",
        "range": "0.0 = No relevante, 1.0 = Altamente relevante"
    },
    "context_precision": {
        "desc": "Precisión: proporción de documentos recuperados que son relevantes",
        "range": "0.0 = Ninguno relevante, 1.0 = Todos relevantes"
    },
    "context_recall": {
        "desc": "Recall: proporción de documentos relevantes que fueron recuperados",
        "range": "0.0 = Ninguno recuperado, 1.0 = Todos recuperados"
    }
}
