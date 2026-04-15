from app.rag.agent import RAGAgent

# Cache del agente RAG (lazy)
_rag_agent = None
_current_provider = None
_current_model = None


def get_rag_agent(provider: str = "mock", model: str = "mistral"):
    """
    Obtiene el agente RAG, inicializándolo si es necesario.

    El agente se reutiliza mientras provider y model no cambien.
    """
    global _rag_agent, _current_provider, _current_model

    provider = provider.strip().lower()
    model = model.strip().lower()
    use_local = provider == "ollama"

    if (
        _rag_agent is None
        or _current_provider != provider
        or _current_model != model
    ):
        try:
            _rag_agent = RAGAgent(
                model_name=model,
                provider=provider,
                use_local=use_local,
            )
            _current_provider = provider
            _current_model = model
        except Exception as e:
            # Si falla, no rompemos la API
            _rag_agent = None
            _current_provider = None
            _current_model = None

    return _rag_agent