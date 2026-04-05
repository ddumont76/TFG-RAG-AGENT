import chromadb

client = chromadb.PersistentClient(path="chroma_db")
tickets = client.get_collection("tickets")

print("Count:", tickets.count())


print(len(tickets.get(include=["embeddings"], limit=1)["embeddings"][0]))

