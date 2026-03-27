import chromadb

client = chromadb.PersistentClient(path="chroma_db")
tickets_collection = client.get_collection("tickets")
docs_collection = client.get_collection("docs")

print("=== TICKETS COLLECTION ===")
print("Total tickets:", tickets_collection.count())
results = tickets_collection.get(limit=5)
for i, doc in enumerate(results["documents"]):
    print(f"{i+1}. ID: {results['ids'][i]}")
    print(f"   Content: {doc[:100]}...")
    print()

print("=== DOCS COLLECTION ===")
print("Total docs:", docs_collection.count())
results = docs_collection.get(limit=5)
for i, doc in enumerate(results["documents"]):
    print(f"{i+1}. ID: {results['ids'][i]}")
    print(f"   Content: {doc[:100]}...")
    print()