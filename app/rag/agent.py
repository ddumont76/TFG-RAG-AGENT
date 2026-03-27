"""
Agente RAG principal para consultas sobre Data & IA.
"""

import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from app.rag.models import LLMConfig
from app.rag.prompts import RAG_PROMPT_TEMPLATE, SUMMARY_PROMPT_TEMPLATE, EXPLANATION_PROMPT_TEMPLATE


@dataclass
class RAGResult:
    """Resultado de una consulta RAG."""
    query: str
    answer: str
    tickets_used: List[Dict[str, Any]]
    docs_used: List[Dict[str, Any]]
    model_name: str
    processing_time: float
    total_sources: int
    confidence_score: float
    metadata: Dict[str, Any]


class RAGAgent:
    """
    Agente RAG que combina búsqueda vectorial con generación de lenguaje.
    """

    def __init__(self, model_name: str = "local_mistral", use_local: bool = True):
        """
        Inicializa el agente RAG.

        Args:
            model_name: Nombre del modelo LLM a usar
            use_local: Si usar modelo descargado localmente
        """
        self.model_name = model_name
        self.llm = LLMConfig.get_model(model_name, use_local)
        print(f"🤖 Agente RAG inicializado con modelo: {model_name}")

    def _prepare_context(self, tickets: List[Dict], docs: List[Dict], max_length: int = 3000) -> Dict[str, str]:
        """
        Prepara el contexto de tickets y documentos para el LLM.

        Args:
            tickets: Lista de tickets relevantes
            docs: Lista de documentos relevantes
            max_length: Longitud máxima del contexto

        Returns:
            Diccionario con contexto de tickets y docs
        """
        # Preparar contexto de tickets con información completa
        tickets_context = ""
        if tickets:
            tickets_context = "\n=== TICKETS RELACIONADOS ==="
            for i, ticket in enumerate(tickets[:5], 1):  # Máximo 5 tickets
                ticket_id = ticket.get('id', 'N/A')
                summary = ticket.get('summary', 'N/A')
                description = ticket.get('description', '')
                comments = ticket.get('comments', [])
                
                tickets_context += f"\n\n{i}. **Ticket ID: {ticket_id}**"
                tickets_context += f"\n   **Summary**: {summary}"
                if description:
                    tickets_context += f"\n   **Description**: {description[:200]}..."
                if comments:
                    tickets_context += f"\n   **Comments**: {'; '.join(comments)[:200]}..."

        # Preparar contexto de documentos con información completa
        docs_context = ""
        if docs:
            docs_context = "\n=== DOCUMENTOS DE CONFLUENCE ==="
            for i, doc in enumerate(docs[:5], 1):  # Máximo 5 docs
                doc_id = doc.get('id', 'N/A')
                title = doc.get('title', 'N/A')
                content = doc.get('content', '')
                
                docs_context += f"\n\n{i}. **Documento ID: {doc_id}**"
                docs_context += f"\n   **Title**: {title}"
                docs_context += f"\n   **Content**: {content[:400]}..."

        # Limitar longitud total
        total_context = tickets_context + docs_context
        if len(total_context) > max_length:
            total_context = total_context[:max_length] + "..."

        return {
            "tickets_context": tickets_context.strip(),
            "docs_context": docs_context.strip()
        }

    def _calculate_confidence(self, tickets: List[Dict], docs: List[Dict]) -> float:
        """
        Calcula un score de confianza basado en la calidad de los resultados.

        Args:
            tickets: Tickets encontrados
            docs: Documentos encontrados

        Returns:
            Score de confianza entre 0 y 1
        """
        if not tickets and not docs:
            return 0.0

        # Factores de confianza
        ticket_score = min(len(tickets) * 0.3, 0.6)  # Hasta 0.6 por tickets
        doc_score = min(len(docs) * 0.2, 0.4)        # Hasta 0.4 por docs

        # Bonus por diversidad de contenido
        total_content = sum(len(t.get("content", "")) for t in tickets) + \
                       sum(len(d.get("content", "")) for d in docs)
        content_bonus = min(total_content / 2000, 0.3)  # Bonus por contenido rico

        confidence = ticket_score + doc_score + content_bonus
        return min(confidence, 1.0)

    def _extract_sources_info(self, tickets: List[Dict], docs: List[Dict]) -> Dict[str, Any]:
        """Extrae información estadística de las fuentes."""
        return {
            "total_tickets": len(tickets),
            "total_docs": len(docs),
            "ticket_ids": [t.get("id") for t in tickets],
            "doc_ids": [d.get("id") for d in docs],
            "avg_ticket_score": sum(t.get("score", 0) for t in tickets) / len(tickets) if tickets else 0,
            "avg_doc_score": sum(d.get("score", 0) for d in docs) / len(docs) if docs else 0
        }

    def query(self, query: str, tickets: List[Dict], docs: List[Dict]) -> RAGResult:
        """
        Realiza una consulta RAG completa.

        Args:
            query: Pregunta del usuario
            tickets: Tickets relevantes encontrados
            docs: Documentos relevantes encontrados

        Returns:
            RAGResult con respuesta generada y metadata
        """
        start_time = time.time()

        try:
            # Preparar contexto
            context = self._prepare_context(tickets, docs)

            # Crear prompt
            prompt = RAG_PROMPT_TEMPLATE.format(
                query=query,
                tickets_context=context["tickets_context"],
                docs_context=context["docs_context"]
            )

            # Generar respuesta con LLM
            print(f"🧠 Generando respuesta con {self.model_name}...")
            answer = self.llm.invoke(prompt)

            # Calcular confianza
            confidence = self._calculate_confidence(tickets, docs)

            # Extraer info de fuentes
            sources_info = self._extract_sources_info(tickets, docs)

            # Metadata adicional
            metadata = {
                "model": self.model_name,
                "timestamp": datetime.now().isoformat(),
                "prompt_length": len(prompt),
                "context_length": len(context["tickets_context"]) + len(context["docs_context"]),
                **sources_info
            }

            processing_time = time.time() - start_time

            return RAGResult(
                query=query,
                answer=answer,
                tickets_used=tickets,
                docs_used=docs,
                model_name=self.model_name,
                processing_time=processing_time,
                total_sources=len(tickets) + len(docs),
                confidence_score=confidence,
                metadata=metadata
            )

        except Exception as e:
            # Fallback en caso de error
            processing_time = time.time() - start_time
            error_answer = f"Lo siento, ocurrió un error procesando tu consulta: {str(e)}. " \
                          f"Te recomiendo revisar los tickets y documentos encontrados manualmente."

            return RAGResult(
                query=query,
                answer=error_answer,
                tickets_used=tickets,
                docs_used=docs,
                model_name=self.model_name,
                processing_time=processing_time,
                total_sources=len(tickets) + len(docs),
                confidence_score=0.0,
                metadata={"error": str(e)}
            )

    def summarize_results(self, query: str, tickets: List[Dict], docs: List[Dict]) -> str:
        """
        Genera un resumen conciso de los resultados encontrados.

        Args:
            query: Consulta original
            tickets: Tickets encontrados
            docs: Documentos encontrados

        Returns:
            Resumen generado
        """
        try:
            # Preparar textos
            tickets_text = "\n".join([f"- {t.get('content', '')[:200]}..." for t in tickets[:3]])
            docs_text = "\n".join([f"- {d.get('content', '')[:200]}..." for d in docs[:3]])

            # Crear prompt
            prompt = SUMMARY_PROMPT_TEMPLATE.format(
                query=query,
                tickets_text=tickets_text,
                docs_text=docs_text
            )

            # Generar resumen
            return self.llm.invoke(prompt)

        except Exception as e:
            return f"Error generando resumen: {str(e)}. Total fuentes: {len(tickets) + len(docs)}"