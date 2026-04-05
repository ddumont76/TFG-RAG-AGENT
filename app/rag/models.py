"""
Configuración de modelo LLM para el agente RAG (Ollama + fallback).
"""

import os
from langchain_community.llms import Ollama


class MockLLM:
    def invoke(self, prompt: str) -> str:
        return (
            "[MockLLM] No hay motor LLM disponible. "
            "Revisa `LLM_PROVIDER` y `LLM_MODEL`, o ejecuta Ollama en localhost:11434."
        )


class LLMConfig:
    """
    Configura diversos proveedores de LLM.
    Esta versión acepta cualquier modelo válido de Ollama sin validación rígida.
    """

    @staticmethod
    def get_model(model_name="mistral", provider: str | None = None, use_local: bool = True):
        provider = (provider or os.getenv("LLM_PROVIDER", "ollama")).strip().lower()
        model_name = (model_name or os.getenv("LLM_MODEL", "mistral")).strip()

        # Normalización mínima (solo si quieres alias)
        if model_name in {"qwen-2.5", "qwen2.5", "qwen25"}:
            model_name = "qwen2.5:0.5b"

        if provider == "ollama":
            print(f"[Ollama] Cargando modelo: {model_name}")
            return Ollama(
                model=model_name,
                temperature=0.1,
                num_predict=1024
            )

        if provider in {"mock", "none"}:
            print("[MockLLM] Usando modelo de fallback MockLLM (sin motor real).")
            return MockLLM()

        raise ValueError(f"Proveedor LLM desconocido: {provider}. Usa 'ollama' o 'mock'.")

    @staticmethod
    def get_available_models():
        """Lista de modelos disponibles (solo informativa)."""
        return ["mistral", "qwen2.5:0.5b", "qwen2.5:latest"]