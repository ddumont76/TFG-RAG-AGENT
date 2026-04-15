from typing import List, Dict, Any

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str
    top_k: int = Field(default=5, ge=1)
    provider: str = "mock"  # ollama, mock
    model: str = "mistral"  # mistral, phi-4, qwen-2.5


class QueryResponse(BaseModel):
    query: str
    answer: str
    tickets: List[Dict[str, Any]]
    docs: List[Dict[str, Any]]
    model_name: str
    processing_time: float
    total_sources: int
    confidence_score: float
    metadata: Dict[str, Any]
    metrics: Dict[str, float] = Field(default_factory=dict)


class EvaluationRequest(BaseModel):
    query: str
    answer: str
    contexts: List[str]
    ground_truth: str = ""


class EvaluationResponse(BaseModel):
    query: str
    answer: str
    metrics: Dict[str, float]
    avg_score: float
    metric_descriptions: Dict[str, Dict[str, str]]


class ChunkingCompareRequest(BaseModel):
    text: str
    strategies: List[str] = Field(
        default_factory=lambda: [
            "fixed_size",
            "fixed_size_overlap",
            "sentence",
            "paragraph",
        ]
    )


class ChunkingCompareResponse(BaseModel):
    results: Dict[str, Dict[str, Any]]
    comparison: Dict[str, Any]


class QueryWithChunkingRequest(BaseModel):
    query: str
    top_k: int = Field(default=2, ge=1)
    provider: str = "mock"
    model: str = "mistral"
    chunking_strategy: str = "fixed_size"
    chunk_size: int = Field(default=512, ge=1)