"""
Agente RAG principal para consultas sobre Data & IA.
"""

import time
import os
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

    def __init__(self, model_name: str = "mistral", provider: str | None = None, use_local: bool = True):
        """
        Inicializa el agente RAG.

        Args:
            model_name: Nombre del modelo LLM a usar (mistral / phi-4 / phi4).
            provider: Proveedor de LLM (ollama / mock).
            use_local: Si usar modelo local (principalmente para Ollama).
        """
        self.model_name = model_name
        self.provider = provider or os.getenv("LLM_PROVIDER", "ollama")
        self.use_local = use_local
        self.llm = LLMConfig.get_model(model_name, provider=self.provider, use_local=use_local)
        print(f"[RAGAgent] Agente RAG inicializado con modelo: {model_name} (provider={self.provider})")

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
        Devuelve siempre una respuesta serializable y coherente con las fuentes encontradas.
        """
        start_time = time.time()

        try:
            # 1️⃣ Preparar contexto
            context = self._prepare_context(tickets, docs)

            prompt = RAG_PROMPT_TEMPLATE.format(
                query=query,
                tickets_context=context["tickets_context"],
                docs_context=context["docs_context"]
            )

            print(f"[RAGAgent] Generando respuesta con {self.model_name}...")
            raw_answer = self.llm.invoke(prompt)

            # 2️⃣ NORMALIZACIÓN ESTRICTA A STRING (OBLIGATORIA)
            # LangChain/Ollama pueden devolver AIMessage u otros objetos no serializables
            if hasattr(raw_answer, "content"):
                answer = str(raw_answer.content)
            else:
                answer = str(raw_answer)

            # 3️⃣ Protección semántica:
            # Si hay fuentes, el agente NO puede decir que no hay información
            if (tickets or docs) and "no se han encontrado" in answer.lower():
                answer = (
                    "Se ha encontrado información relevante en tickets y documentos "
                    "relacionados con la incidencia. A continuación se detallan los "
                    "principales hallazgos y recomendaciones."
                )

            # 4️⃣ Calcular confianza y metadatos
            confidence = self._calculate_confidence(tickets, docs)
            sources_info = self._extract_sources_info(tickets, docs)

            # 5️⃣ Metadata SEGURA (solo tipos JSON simples)
            metadata = {
                "model": str(self.model_name),
                "timestamp": datetime.now().isoformat(),
                "prompt_length": int(len(prompt)),
                "context_length": int(
                    len(context["tickets_context"]) + len(context["docs_context"])
                ),
                "total_tickets": int(len(tickets)),
                "total_docs": int(len(docs)),
                "ticket_ids": [str(t.get("id")) for t in tickets],
                "doc_ids": [str(d.get("id")) for d in docs],
                "avg_ticket_score": float(
                    sum(t.get("score", 0) for t in tickets) / len(tickets)
                ) if tickets else 0.0,
                "avg_doc_score": float(
                    sum(d.get("score", 0) for d in docs) / len(docs)
                ) if docs else 0.0,
            }

            processing_time = time.time() - start_time

            return RAGResult(
                query=query,
                answer=answer,                 # ✅ SIEMPRE string
                tickets_used=tickets,
                docs_used=docs,
                model_name=str(self.model_name),
                processing_time=float(processing_time),
                total_sources=len(tickets) + len(docs),
                confidence_score=float(confidence),
                metadata=metadata
            )

        except Exception as e:
            # Fallback absolutamente seguro
            processing_time = time.time() - start_time

            return RAGResult(
                query=query,
                answer=(
                    "Lo siento, ocurrió un error procesando tu consulta. "
                    "Consulta los tickets y documentos encontrados para más información."
                ),
                tickets_used=tickets,
                docs_used=docs,
                model_name=str(self.model_name),
                processing_time=float(processing_time),
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
            
            result = self.llm.invoke(prompt)
            return str(result.content if hasattr(result, "content") else result)


        except Exception as e:
            raise e