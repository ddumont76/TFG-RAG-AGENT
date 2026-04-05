"""
Evaluación RAGAS para RAG local con ChatOllama + BGE-M3.
Compatible con RAGAS 0.1.4 (sin API async).
"""

from typing import List, Dict, Any, Optional

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    # context_precision,   # ❌ requiere ground_truth
    # context_recall,      # ❌ requiere ground_truth
    context_utilization
)

from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import HuggingFaceEmbeddings


class RAGEvaluator:
    """Evaluador de sistemas RAG usando RAGAS."""

         
    def __init__(self, llm=None, embeddings=None):
        if llm is None:
            llm = ChatOllama(model="qwen2.5:0.5b")

        if embeddings is None:
            embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")

        self.llm = llm
        self.embeddings = embeddings

        self.metrics = [
            faithfulness,
            answer_relevancy,
            context_utilization
            ]


    def prepare_dataset(self, queries, answers, contexts, ground_truths=None):
        data = {
            "question": queries,
            "answer": answers,
            "contexts": contexts,
        }

        if ground_truths:
            data["ground_truth"] = ground_truths

        # RAGAS 0.1.4 requiere Dataset, no dict
        return Dataset.from_dict(data)

    def evaluate_sync(self, queries, answers, contexts, ground_truths=None):
        dataset = self.prepare_dataset(queries, answers, contexts, ground_truths)
        print(">>> MÉTRICAS ACTIVAS:", self.metrics)
        
        results = evaluate(
            dataset,
            metrics=self.metrics,
            llm=self.llm,
            embeddings=self.embeddings
        )

        return self._format_results(results)

    def _format_results(self, results):
        return {
            "metrics": results,
            "avg_score": sum(results.values()) / len(results),
            "status": "success"
        }


    def evaluate_batch(queries, answers, contexts, ground_truths=None, llm=None, embeddings=None):
        evaluator = RAGEvaluator(llm=llm, embeddings=embeddings)
        return evaluator.evaluate_sync(queries, answers, contexts, ground_truths)

    def evaluate_single_query(
            self,
            query: str,
            answer: str,
            contexts: list,
            ground_truth: Optional[str] = None
        ) -> Dict[str, Any]:

            queries = [query]
            answers = [answer]
            contexts_list = [contexts]   # RAGAS requiere lista de listas
            ground_truths = [ground_truth] if ground_truth else None

            return self.evaluate_sync(
                queries=queries,
                answers=answers,
                contexts=contexts_list,
                ground_truths=ground_truths
            )


METRIC_RANGES = {
    "faithfulness": {
        "desc": "¿Qué tan fiel es la respuesta al contexto recuperado?",
        "range": "0.0 = infiel, 1.0 = totalmente fiel"
    },
    "answer_relevancy": {
        "desc": "¿Qué tan relevante es la respuesta respecto a la pregunta?",
        "range": "0.0 = no relevante, 1.0 = muy relevante"
    },
    "context_utilization": {
        "desc": "¿Cuánto del contexto recuperado fue realmente usado en la respuesta?",
        "range": "0.0 = nada usado, 1.0 = todo usado"
    }
}