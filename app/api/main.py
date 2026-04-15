from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.routes import (
    query,
    search,
    evaluation,
    chunking,
    home,
    health  
)


app = FastAPI(title="RAG Agent API", description="API for Data & IA RAG Agent", version="1.0.0")

# Static & templates
app.mount("/static", StaticFiles(directory="app/api/static"), name="static")


app.include_router(query.router)
app.include_router(search.router)
app.include_router(evaluation.router)
app.include_router(chunking.router)
app.include_router(home.router)
app.include_router(health.router)


# Importar rutas
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.api.main:app", host="0.0.0.0", port=8000, reload=True)