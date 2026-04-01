"""
Configuración de modelo LLM para el agente RAG (Ollama + OpenAI + fallback).
"""

import os
from langchain_community.llms import Ollama
from langchain_openai import OpenAI


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
            "openai_model": "gpt-4o",
            "max_tokens": 1024,
            "temperature": 0.1
        },
        "phi-4": {
            "ollama_model": "phi-4",
            "openai_model": "gpt-4o",
            "max_tokens": 1024,
            "temperature": 0.1
        },
        "openai": {
            "ollama_model": "phi-4",
            "openai_model": "gpt-4o-mini",
            "max_tokens": 1024,
            "temperature": 0.1
        }
    }

    @staticmethod
    def get_model(model_name="mistral", provider: str | None = None, use_local: bool = True):
        provider = (provider or os.getenv("LLM_PROVIDER", "ollama")).strip().lower()
        model_name = (model_name or os.getenv("LLM_MODEL", "mistral")).strip().lower()

        config = LLMConfig.MODELS.get(model_name)
        if config is None:
            raise ValueError(f"Modelo desconocido: {model_name}. Usa 'mistral' o 'phi-4'.")

        if provider == "ollama":
            model_id = config.get("ollama_model", "mistral")
            print(f"🦙 Cargando {model_name} via Ollama ({model_id})")
            return Ollama(
                model=model_id,
                temperature=config["temperature"],
                num_predict=config["max_tokens"]
            )

        if provider == "openai":
            model_id = config.get("openai_model", "gpt-4o-mini")
            print(f"☁️ Cargando {model_name} via OpenAI ({model_id})")
            return OpenAI(
                model=model_id,
                temperature=config["temperature"],
                max_tokens=config["max_tokens"]
            )

        if provider in {"mock", "none"}:
            print("🛠️  Usando modelo de fallback MockLLM (sin motor real).")
            return MockLLM()

        raise ValueError(f"Proveedor LLM desconocido: {provider}. Usa 'ollama', 'openai' o 'mock'.")

    @staticmethod
    def get_available_models():
        """Lista de modelos disponibles."""
        return list(LLMConfig.MODELS.keys())
