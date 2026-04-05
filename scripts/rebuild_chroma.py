import os
import chromadb
from sentence_transformers import SentenceTransformer

# Embedding model BGE-M3 (1024 dims)
embedding_model = SentenceTransformer(
    "BAAI/bge-m3",
    trust_remote_code=True
)

# Ruta donde se guardará la nueva base
CHROMA_PATH = "chroma_db"

# Crear cliente
client = chromadb.PersistentClient(path=CHROMA_PATH)

# Crear colecciones nuevas
tickets = client.create_collection(name="tickets")
docs = client.create_collection(name="docs")

# Aquí cargas tus datos reales
# Ejemplo:
ticket_texts = [
    "Error 403 en Jenkins al acceder a la API",
    "Pipeline fallando por permisos insuficientes"
]

doc_texts = [
    "CrashLoopBackOff ocurre cuando un contenedor falla repetidamente",
    "S3 AccessDenied suele deberse a políticas IAM incorrectas"
]

# Indexar tickets
ticket_embeddings = embedding_model.encode(ticket_texts).tolist()
tickets.add(
    ids=[f"ticket_{i}" for i in range(len(ticket_texts))],
    documents=ticket_texts,
    embeddings=ticket_embeddings
)

# Indexar docs
doc_embeddings = embedding_model.encode(doc_texts).tolist()
docs.add(
    ids=[f"doc_{i}" for i in range(len(doc_texts))],
    documents=doc_texts,
    embeddings=doc_embeddings
)

print("Chroma reconstruido correctamente con embeddings BGE-M3 (1024 dims)")