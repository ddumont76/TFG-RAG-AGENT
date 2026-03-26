"""
Configuración de modelo LLM para el agente RAG (solo Mistral vía Ollama).
"""

from langchain_community.llms import Ollama


class LLMConfig:
    """Configura SOLO el modelo Mistral usando Ollama."""

    MODELS = {
        "mistral": {
            "name": "mistral",
            "type": "ollama",
            "max_tokens": 1024,
            "temperature": 0.1
        }
    }

    @staticmethod
    def get_model(model_name="mistral", use_local=True):
        """
        Devuelve el modelo Mistral (Ollama) como objeto LangChain.
        """
        config = LLMConfig.MODELS[model_name]

        print(f"🦙 Cargando Mistral via Ollama: {config['name']}")

        return Ollama(
            model=config["name"],
            temperature=config["temperature"],
            num_predict=config["max_tokens"]
        )

    @staticmethod
    def get_available_models():
        """Lista de modelos disponibles (solo uno)."""
        return ["mistral"]