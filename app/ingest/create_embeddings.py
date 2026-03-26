import os
import json
import chromadb
from sentence_transformers import SentenceTransformer

from app.ingest.load_corpus import load_tickets, load_confluence_docs


# 1. Inicializar ChromaDB local (persistencia en carpeta ./chroma_db)
client = chromadb.PersistentClient(path="chroma_db")


# 2. Cargar modelo de embeddings
print("🔄 Cargando modelo de embeddings...")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def embed_text(text: str):
    """Genera embedding para un texto usando SentenceTransformer."""
    return embedding_model.encode(text).tolist()


# 3. Crear colecciones en ChromaDB
tickets_collection = client.get_or_create_collection(
    name="tickets",
    metadata={"hnsw:space": "cosine"}
)

docs_collection = client.get_or_create_collection(
    name="docs",
    metadata={"hnsw:space": "cosine"}
)


# 4. Ingestar tickets
def ingest_tickets():
    tickets = load_tickets()
    print(f"📨 Encontrados {len(tickets)} tickets")

    for t in tickets:
        doc_text = f"{t['summary']}. {t['description']}. {'. '.join(t['comments'])}"
        embedding = embed_text(doc_text)

        tickets_collection.upsert(
            ids=[t["id"]],
            embeddings=[embedding],
            metadatas=[{"type": "ticket"}],
            documents=[doc_text]
        )

    print("✅ Tickets almacenados en ChromaDB")


# 5. Ingestar documentos de Confluence
def ingest_docs():
    docs = load_confluence_docs()
    print(f"📄 Encontrados {len(docs)} documentos")

    for d in docs:
        doc_text = f"{d['title']}. {d['content']}"
        embedding = embed_text(doc_text)

        docs_collection.upsert(
            ids=[d["id"]],
            embeddings=[embedding],
            metadatas=[{"type": "doc"}],
            documents=[doc_text]
        )

    print("✅ Documentos almacenados en ChromaDB")


# 6. Test de búsqueda
def test_search(query):
    print(f"\n🔎 Buscando similitud para: {query}")

    q_embed = embed_text(query)

    results_tickets = tickets_collection.query(
        query_embeddings=[q_embed],
        n_results=3
    )

    results_docs = docs_collection.query(
        query_embeddings=[q_embed],
        n_results=3
    )

    print("\n🎟️ Tickets similares:")
    for doc in results_tickets["documents"][0]:
        print("- ", doc)

    print("\n📚 Documentos similares:")
    for doc in results_docs["documents"][0]:
        print("- ", doc)


if __name__ == "__main__":
    ingest_tickets()
    ingest_docs()

    test_search("El pipeline de Jenkins devuelve un error 403")