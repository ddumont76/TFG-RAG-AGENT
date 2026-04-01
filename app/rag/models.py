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
    """Configura diversos proveedores de LLM."""

    MODELS = {
        "mistral": {
            "ollama_model": "mistral",
            "max_tokens": 1024,
            "temperature": 0.1
        },
        "phi-4": {
            "ollama_model": "phi-4",
            "max_tokens": 1024,
            "temperature": 0.1
        },
        "qwen-2.5": {
            "ollama_model": "qwen2.5",  # Llamado como qwen2.5 en Ollama
            "max_tokens": 1024,
            "temperature": 0.1
        }
    }

    @staticmethod
    def get_model(model_name="mistral", provider: str | None = None, use_local: bool = True):
        provider = (provider or os.getenv("LLM_PROVIDER", "ollama")).strip().lower()
        model_name = (model_name or os.getenv("LLM_MODEL", "mistral")).strip().lower()

        # Normalizar variantes de nombres de modelo
        if model_name in {"phi4", "phi-4"}:
            model_name = "phi-4"
        if model_name in {"qwen2.5", "qwen-2.5", "qwen25"}:
            model_name = "qwen-2.5"

        config = LLMConfig.MODELS.get(model_name)
        if config is None:
            raise ValueError(
                f"Modelo desconocido: {model_name}. Usa 'mistral', 'phi-4' o 'qwen-2.5'."
            )

        if provider == "ollama":
            model_id = config.get("ollama_model", "mistral")
            print(f"[Ollama] Cargando {model_name} via Ollama ({model_id})")
            return Ollama(
                model=model_id,
                temperature=config["temperature"],
                num_predict=config["max_tokens"]
            )

        if provider in {"mock", "none"}:
            print("[MockLLM] Usando modelo de fallback MockLLM (sin motor real).")
            return MockLLM()

        raise ValueError(f"Proveedor LLM desconocido: {provider}. Usa 'ollama' o 'mock'.")

    @staticmethod
    def get_available_models():
        """Lista de modelos disponibles."""
        return list(LLMConfig.MODELS.keys())
