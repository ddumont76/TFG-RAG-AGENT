#!/usr/bin/env python3
"""
Script para ejecutar la API FastAPI del RAG Agent.
"""

import uvicorn
from app.api.main import app

if __name__ == "__main__":
    print("🚀 Iniciando RAG Agent API...")
    print("📖 Documentación disponible en: http://localhost:8000/docs")
    print("🔗 Health check: http://localhost:8000/health")
    
    uvicorn.run(
        "app.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload en desarrollo
        log_level="info"
    )