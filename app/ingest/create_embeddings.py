import os
import json
import chromadb
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.ingest.load_corpus import load_tickets, load_confluence_docs


# 1. Inicializar ChromaDB local
client = chromadb.PersistentClient(path="chroma_db")


# 2. Cargar modelo de embeddings
print("🔄 Cargando modelo de embeddings...")
#
#bge‑m3 requiere dos ajustes adicionales: trust_remote_code=True
embedding_model = SentenceTransformer(
    "BAAI/bge-m3",
    trust_remote_code=True
)
# bge-m3 funciona mejor si normalizas el vector, añado .normalize_embeddings=True.
 
#Esto mejora la calidad del retrieval y evita que Chroma reciba vectores desbalanceados.
def embed_text(text: str):
    emb = embedding_model.encode(text, normalize_embeddings=True)
    return emb.tolist()

# 3. Crear colecciones
tickets_collection = client.get_or_create_collection(
    name="tickets",
    metadata={"hnsw:space": "cosine"}
)

docs_collection = client.get_or_create_collection(
    name="docs",
    metadata={"hnsw:space": "cosine"}
)


# 4. Configurar chunking
splitter = RecursiveCharacterTextSplitter(
    chunk_size=350,
    chunk_overlap=80
)

# 5. Ingestar tickets con chunking
def ingest_tickets():
    tickets = load_tickets()
    print(f"📨 Encontrados {len(tickets)} tickets")

    for t in tickets:
        full_text = f"{t['summary']}. {t['description']}. {'. '.join(t['comments'])}"
        chunks = splitter.split_text(full_text)

        for i, chunk in enumerate(chunks):
            embedding = embed_text(chunk)

            tickets_collection.upsert(
                ids=[f"{t['id']}_chunk_{i}"],
                embeddings=[embedding],
                metadatas=[{"type": "ticket", "ticket_id": t["id"]}],
                documents=[chunk]
            )

    print("✅ Tickets almacenados en ChromaDB con chunking")


# 6. Ingestar documentos de Confluence con chunking
def ingest_docs():
    docs = load_confluence_docs()
    print(f"📄 Encontrados {len(docs)} documentos")

    for d in docs:
        full_text = f"{d['title']}. {d['content']}"
        chunks = splitter.split_text(full_text)

        for i, chunk in enumerate(chunks):
            embedding = embed_text(chunk)

            docs_collection.upsert(
                ids=[f"{d['id']}_chunk_{i}"],
                embeddings=[embedding],
                metadatas=[{"type": "doc", "doc_id": d["id"]}],
                documents=[chunk]
            )

    print("✅ Documentos almacenados en ChromaDB con chunking")


# 7. Test de búsqueda
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
    if results_tickets and results_tickets["documents"] and results_tickets["documents"][0]:
        for doc in results_tickets["documents"][0]:
            print("- ", doc)
    else:
        print("Ningún ticket encontrado")

    print("\n📚 Documentos similares:")
    if results_docs and results_docs["documents"] and results_docs["documents"][0]:
        for doc in results_docs["documents"][0]:
            print("- ", doc)
    else:
        print("Ningún documento encontrado")


if __name__ == "__main__":
    ingest_tickets()
    ingest_docs()

    test_search("El pipeline de Jenkins devuelve un error 403")