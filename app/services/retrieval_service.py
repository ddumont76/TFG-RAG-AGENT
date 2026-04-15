import chromadb
from sentence_transformers import SentenceTransformer

# Variables internas (lazy initialization)
_client = None
_embedding_model = None
_tickets_collection = None
_docs_collection = None


def _init_vector_store():
    """Inicializa Chroma y el modelo de embeddings de forma lazy."""
    global _client, _embedding_model, _tickets_collection, _docs_collection

    if _client is None:
        _client = chromadb.PersistentClient(path="chroma_db")

    if _embedding_model is None:
        _embedding_model = SentenceTransformer(
            "BAAI/bge-m3",
            trust_remote_code=True,
        )

    if _tickets_collection is None:
        _tickets_collection = _client.get_or_create_collection(
            name="tickets"
        )

    if _docs_collection is None:
        _docs_collection = _client.get_or_create_collection(
            name="docs"
        )


def retrieve_documents(query: str, top_k: int = 5):
    """Recupera documentos relevantes de tickets y docs usando embeddings."""
    _init_vector_store()

    query_embedding = _embedding_model.encode(query).tolist()

    tickets_results = _tickets_collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
    )

    docs_results = _docs_collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
    )

    return tickets_results, docs_results