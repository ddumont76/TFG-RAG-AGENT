import chromadb
from sentence_transformers import SentenceTransformer

from app.ingest.load_corpus import load_tickets, load_confluence_docs

CHROMA_DIR = "chroma_db"


def setup_chroma_client():
    return chromadb.PersistentClient(path=CHROMA_DIR)


def count_collection(collection):
    try:
        return collection.count()
    except Exception:
        # older chromadb versions may not support count() on collection
        # Workaround: query all ids
        r = collection.query(query_embeddings=[[0]*384], n_results=1)
        return len(r["ids"][0]) if "ids" in r and r["ids"] else 0


def main():
    print("=== Corpus raw counts ===")
    tickets = load_tickets()
    docs = load_confluence_docs()
    print(f"Tickets file count (data/tickets): {len(tickets)}")
    print(f"Confluence docs file count (data/confluence): {len(docs)}")

    print("\n=== ChromaDB index status ===")
    client = setup_chroma_client()

    for collection_name in ["tickets", "docs"]:
        try:
            collection = client.get_collection(collection_name)
            total = count_collection(collection)
            print(f"Collection '{collection_name}' exists: {total} items")
        except Exception as exc:
            print(f"Collection '{collection_name}' error: {exc}")

    print("\n=== Semantics smoke test ===")
    # Use same model as ingestion
    model = SentenceTransformer("all-MiniLM-L6-v2")
    query_text = "Error en Jenkins al desplegar en Kubernetes"
    q_embedding = model.encode(query_text).tolist()

    for collection_name in ["tickets", "docs"]:
        try:
            collection = client.get_collection(collection_name)
            results = collection.query(query_embeddings=[q_embedding], n_results=3)
            docs_out = results.get("documents", [[]])[0]
            print(f"\nTop matches in '{collection_name}':")
            if not docs_out:
                print("  (no documents found)")
            for i, d in enumerate(docs_out, start=1):
                print(f"  {i}. {d}")
        except Exception as exc:
            print(f"Error querying '{collection_name}': {exc}")


if __name__ == "__main__":
    main()
