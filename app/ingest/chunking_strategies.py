"""
Módulo de estrategias de chunking para procesar documentos.
Permite comparar diferentes técnicas de división de documentos.
"""

from typing import List, Dict, Any
from abc import ABC, abstractmethod


class ChunkingStrategy(ABC):
    """Clase base para estrategias de chunking."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    def chunk(self, text: str) -> List[str]:
        """Divide el texto en chunks."""
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """Retorna metadatos de la estrategia."""
        return {
            "name": self.name,
            "description": self.description
        }


class FixedSizeChunking(ChunkingStrategy):
    """Divide el texto en chunks de tamaño fijo sin overlap."""
    
    def __init__(self, chunk_size: int = 512):
        super().__init__(
            name="fixed_size",
            description=f"Chunks de tamaño fijo ({chunk_size} caracteres, sin overlap)"
        )
        self.chunk_size = chunk_size
    
    def chunk(self, text: str) -> List[str]:
        """Divide en chunks de tamaño fijo."""
        chunks = []
        for i in range(0, len(text), self.chunk_size):
            chunk = text[i:i + self.chunk_size].strip()
            if chunk:
                chunks.append(chunk)
        return chunks


class FixedSizeWithOverlapChunking(ChunkingStrategy):
    """Divide el texto en chunks de tamaño fijo con overlap."""
    
    def __init__(self, chunk_size: int = 512, overlap: int = 128):
        super().__init__(
            name="fixed_size_overlap",
            description=f"Chunks de {chunk_size} chars con overlap de {overlap} chars"
        )
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk(self, text: str) -> List[str]:
        """Divide con overlap para mantener contexto."""
        if self.overlap >= self.chunk_size:
            raise ValueError("Overlap debe ser menor que chunk_size")
        
        chunks = []
        step = self.chunk_size - self.overlap
        
        for i in range(0, len(text), step):
            chunk = text[i:i + self.chunk_size].strip()
            if chunk:
                chunks.append(chunk)
            
            # Evitar último chunk duplicado
            if i + self.chunk_size >= len(text):
                break
        
        return chunks


class SentenceChunking(ChunkingStrategy):
    """Divide por oraciones, intentando respetar límites naturales."""
    
    def __init__(self, max_chunk_size: int = 512):
        super().__init__(
            name="sentence",
            description=f"Chunks basados en oraciones (máx {max_chunk_size} chars)"
        )
        self.max_chunk_size = max_chunk_size
    
    def chunk(self, text: str) -> List[str]:
        """Divide por oraciones respetando límites naturales."""
        # Dividir por puntuación
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Si el chunk actual + la oración cabe, añadir
            if len(current_chunk) + len(sentence) + 1 <= self.max_chunk_size:
                current_chunk += (" " + sentence) if current_chunk else sentence
            else:
                # Si el chunk actual tiene contenido, guardarlo
                if current_chunk:
                    chunks.append(current_chunk)
                # Comenzar nuevo chunk
                current_chunk = sentence
                
                # Si la oración sola es muy larga, forzar división
                if len(current_chunk) > self.max_chunk_size:
                    chunks.append(current_chunk)
                    current_chunk = ""
        
        # Añadir último chunk
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks


class ParagraphChunking(ChunkingStrategy):
    """Divide por párrafos, agrupando cuando sea necesario."""
    
    def __init__(self, max_chunk_size: int = 512):
        super().__init__(
            name="paragraph",
            description=f"Chunks basados en párrafos (máx {max_chunk_size} chars)"
        )
        self.max_chunk_size = max_chunk_size
    
    def chunk(self, text: str) -> List[str]:
        """Divide por párrafos."""
        # Dividir por líneas en blanco
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) + 2 <= self.max_chunk_size:
                current_chunk += ("\n\n" + paragraph) if current_chunk else paragraph
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = paragraph
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks


class SemanticChunking(ChunkingStrategy):
    """Divide basado en similitud semántica usando embeddings."""
    
    def __init__(self, embedding_model=None, similarity_threshold: float = 0.8):
        super().__init__(
            name="semantic",
            description=f"Chunks basados en similitud semántica (threshold: {similarity_threshold})"
        )
        self.embedding_model = embedding_model
        self.similarity_threshold = similarity_threshold
    
    def chunk(self, text: str) -> List[str]:
        """Divide basado en cambios semánticos."""
        if self.embedding_model is None:
            # Fallback a sentence chunking si no hay modelo
            return SentenceChunking().chunk(text)
        
        from sentence_transformers import util
        import re
        
        # Dividir en oraciones primero
        sentences = re.split(r'(?<=[.!?])\s+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return [text]
        
        # Generar embeddings
        embeddings = self.embedding_model.encode(sentences, convert_to_tensor=True)
        
        chunks = []
        current_chunk = [sentences[0]]
        
        for i in range(1, len(sentences)):
            # Calcular similitud con la última oración del chunk
            similarity = util.pytorch_cos_sim(embeddings[i], embeddings[i-1])[0][0].item()
            
            if similarity >= self.similarity_threshold:
                current_chunk.append(sentences[i])
            else:
                # Cambio semántico detectado
                chunk_text = " ".join(current_chunk)
                chunks.append(chunk_text)
                current_chunk = [sentences[i]]
        
        # Añadir último chunk
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks


class ChunkingFactory:
    """Factory para crear estrategias de chunking."""
    
    _strategies = {
        "fixed_size": FixedSizeChunking,
        "fixed_size_overlap": FixedSizeWithOverlapChunking,
        "sentence": SentenceChunking,
        "paragraph": ParagraphChunking,
        "semantic": SemanticChunking
    }
    
    @classmethod
    def get_available_strategies(cls) -> Dict[str, str]:
        """Retorna diccionario de estrategias disponibles."""
        strategies = {}
        for name, strategy_class in cls._strategies.items():
            # Crear instancia temporal para obtener descripción
            if name == "semantic":
                temp_instance = strategy_class()
            elif name in ["fixed_size", "fixed_size_overlap"]:
                temp_instance = strategy_class()
            else:
                temp_instance = strategy_class()
            
            strategies[name] = temp_instance.get_metadata()
        
        return strategies
    
    @classmethod
    def create(cls, strategy_name: str, **kwargs) -> ChunkingStrategy:
        """Crea una instancia de la estrategia especificada."""
        if strategy_name not in cls._strategies:
            raise ValueError(f"Estrategia desconocida: {strategy_name}")
        
        strategy_class = cls._strategies[strategy_name]
        return strategy_class(**kwargs)


def compare_chunking_strategies(text: str, strategies: List[str] = None) -> Dict[str, Any]:
    """
    Compara múltiples estrategias de chunking.
    
    Args:
        text: Texto a procesar
        strategies: Lista de nombres de estrategias (default: todas)
    
    Returns:
        Diccionario con resultados comparativos
    """
    if strategies is None:
        strategies = list(ChunkingFactory._strategies.keys())
    
    results = {}
    
    for strategy_name in strategies:
        try:
            strategy = ChunkingFactory.create(strategy_name)
            chunks = strategy.chunk(text)
            
            results[strategy_name] = {
                "name": strategy.name,
                "description": strategy.description,
                "num_chunks": len(chunks),
                "avg_chunk_size": sum(len(c) for c in chunks) / len(chunks) if chunks else 0,
                "min_chunk_size": min(len(c) for c in chunks) if chunks else 0,
                "max_chunk_size": max(len(c) for c in chunks) if chunks else 0,
                "chunks_sample": chunks[:3] if chunks else []  # Primeros 3 como ejemplo
            }
        except Exception as e:
            results[strategy_name] = {
                "error": str(e)
            }
    
    return results
