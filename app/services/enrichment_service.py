from app.ingest.load_corpus import load_tickets, load_confluence_docs

# Cache lazy en memoria
_TICKETS_DATA = None
_DOCS_DATA = None


def _get_tickets_data():
    """Carga datos de tickets de forma lazy."""
    global _TICKETS_DATA
    if _TICKETS_DATA is None:
        _TICKETS_DATA = {
            ticket["id"]: ticket
            for ticket in load_tickets()
        }
    return _TICKETS_DATA


def _get_docs_data():
    """Carga datos de documentos de forma lazy."""
    global _DOCS_DATA
    if _DOCS_DATA is None:
        _DOCS_DATA = {
            doc["id"]: doc
            for doc in load_confluence_docs()
        }
    return _DOCS_DATA


def enrich_ticket_results(tickets_results):
    """Enriquece resultados de tickets con información completa."""
    tickets_data = _get_tickets_data()
    enriched_tickets = []

    for i, content in enumerate(tickets_results["documents"][0]):
        ticket_id = tickets_results["ids"][0][i]
        score = (
            tickets_results["distances"][0][i]
            if "distances" in tickets_results
            else None
        )

        ticket_info = tickets_data.get(ticket_id, {})

        enriched_tickets.append(
            {
                "id": ticket_id,
                "summary": ticket_info.get("summary", "N/A"),
                "description": ticket_info.get("description", ""),
                "comments": ticket_info.get("comments", []),
                "content": content,
                "score": score,
            }
        )

    return enriched_tickets


def enrich_docs_results(docs_results):
    """Enriquece resultados de documentos con información completa."""
    docs_data = _get_docs_data()
    enriched_docs = []

    for i, content in enumerate(docs_results["documents"][0]):
        doc_id = docs_results["ids"][0][i]
        score = (
            docs_results["distances"][0][i]
            if "distances" in docs_results
            else None
        )

        doc_info = docs_data.get(doc_id, {})

        enriched_docs.append(
            {
                "id": doc_id,
                "title": doc_info.get("title", "N/A"),
                "content": doc_info.get("content", content),
                "score": score,
            }
        )

    return enriched_docs