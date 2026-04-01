"""
Módulo de evaluación RAGAS para métricas de RAG.
Calcula: Precision, Recall, Faithfulness y Answer Relevance.
"""

import os
import asyncio
from typing import List, Dict, Any, Optional

# Intentar importar RAGAS, con fallback si no está disponible
try:
    from datasets import Dataset
    from ragas import evaluate
    from ragas.metrics import (
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall
    )
    RAGAS_AVAILABLE = True
except ImportError as e:
    print(f"Advertencia: RAGAS no está disponible ({str(e)}). Las métricas RAGAS no estarán disponibles.")
    RAGAS_AVAILABLE = False
    Dataset = None  # type: ignore
    evaluate = None  # type: ignore
    faithfulness = None  # type: ignore
    answer_relevancy = None  # type: ignore
    context_precision = None  # type: ignore
    context_recall = None  # type: ignore


class RAGEvaluator:
    """Evaluador de sistemas RAG usando RAGAS."""
    
    def __init__(self):
        """Inicializa el evaluador RAGAS."""
        if not RAGAS_AVAILABLE:
            print("Advertencia: RAGAS no está disponible. Las evaluaciones usarán valores simulados.")
        
        self.metrics = []
        if RAGAS_AVAILABLE:
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
        ground_truths: Optional[List[str]] = None
    ) -> Optional[Any]:
        """
        Prepara dataset para RAGAS.
        
        Args:
            queries: Lista de consultas
            answers: Lista de respuestas generadas
            contexts: Lista de listas de contextos recuperados
            ground_truths: Lista de respuestas correctas (opcional)
        
        Returns:
            Dataset en formato RAGAS o None si RAGAS no está disponible
        """
        if not RAGAS_AVAILABLE or Dataset is None:
            return None
        
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
        ground_truths: Optional[List[str]] = None
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
        if not RAGAS_AVAILABLE or evaluate is None:
            # Retornar métricas simuladas cuando RAGAS no está disponible
            return {
                "metrics": {
                    "faithfulness": 0.75,
                    "answer_relevancy": 0.80,
                    "context_precision": 0.70,
                    "context_recall": 0.65,
                },
                "avg_score": 0.725,
                "status": "simulated",
                "note": "RAGAS no disponible - métricas simuladas"
            }
        
        try:
            dataset = self.prepare_dataset(queries, answers, contexts, ground_truths)
            if dataset is None:
                raise RuntimeError("No se pudo preparar el dataset")
            results = evaluate(dataset, metrics=self.metrics)  # type: ignore
            return self._format_results(results)
        except Exception as e:
            return {
                "error": f"Error en evaluación RAGAS: {str(e)}",
                "metrics": {},
                "status": "error"
            }
    
    def _format_results(self, results: Optional[Dict[str, float]]) -> Dict[str, Any]:
        """Formatea resultados de RAGAS."""
        if results is None:
            return {
                "metrics": {},
                "avg_score": 0,
                "status": "no_data"
            }
        
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
        ground_truth: Optional[str] = None
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
    ground_truths: Optional[List[str]] = None
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
