"""
Study Pilot AI - Embeddings Module
Sentence-transformers for CPU-only semantic embeddings
"""

import numpy as np
from pathlib import Path
from typing import List, Union, Optional
import json

# Try to import sentence-transformers
try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False


class EmbeddingModel:
    """
    Wrapper for sentence-transformers embedding model.
    Falls back to simple TF-IDF-like embeddings if not available.
    """
    
    # Default model - small and efficient for CPU
    DEFAULT_MODEL = "all-MiniLM-L6-v2"
    EMBEDDING_DIM = 384  # Dimension for MiniLM
    
    def __init__(self, model_name: str = None, cache_dir: Path = None):
        self.model_name = model_name or self.DEFAULT_MODEL
        self.cache_dir = cache_dir or Path(__file__).parent.parent / "data" / "models"
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the embedding model."""
        if HAS_SENTENCE_TRANSFORMERS:
            try:
                self.model = SentenceTransformer(
                    self.model_name,
                    cache_folder=str(self.cache_dir)
                )
                print(f"Loaded embedding model: {self.model_name}")
            except Exception as e:
                print(f"Error loading model: {e}")
                self.model = None
        else:
            print("sentence-transformers not installed. Using fallback embeddings.")
    
    def embed(self, texts: Union[str, List[str]], 
              show_progress: bool = False) -> np.ndarray:
        """
        Generate embeddings for text(s).
        
        Args:
            texts: Single text or list of texts
            show_progress: Show progress bar for batch
            
        Returns:
            numpy array of shape (n_texts, embedding_dim)
        """
        if isinstance(texts, str):
            texts = [texts]
        
        if self.model is not None:
            embeddings = self.model.encode(
                texts,
                show_progress_bar=show_progress,
                convert_to_numpy=True
            )
            return embeddings
        else:
            # Fallback: simple bag-of-words style embedding
            return self._fallback_embed(texts)
    
    def _fallback_embed(self, texts: List[str]) -> np.ndarray:
        """
        Fallback embedding using simple word hashing.
        Not as good as transformers but works without dependencies.
        """
        embeddings = []
        
        for text in texts:
            # Simple hash-based embedding
            words = text.lower().split()
            vec = np.zeros(self.EMBEDDING_DIM)
            
            for word in words:
                # Hash word to dimension index
                idx = hash(word) % self.EMBEDDING_DIM
                vec[idx] += 1
            
            # Normalize
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            
            embeddings.append(vec)
        
        return np.array(embeddings, dtype=np.float32)
    
    def embed_query(self, query: str) -> np.ndarray:
        """Embed a single query text."""
        return self.embed([query])[0]
    
    def embed_documents(self, documents: List[str], 
                        batch_size: int = 32) -> np.ndarray:
        """
        Embed a list of documents with batching.
        
        Args:
            documents: List of document texts
            batch_size: Batch size for processing
            
        Returns:
            numpy array of embeddings
        """
        all_embeddings = []
        
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            embeddings = self.embed(batch)
            all_embeddings.append(embeddings)
        
        return np.vstack(all_embeddings)
    
    def similarity(self, query_embedding: np.ndarray, 
                   doc_embeddings: np.ndarray) -> np.ndarray:
        """
        Calculate cosine similarity between query and documents.
        
        Args:
            query_embedding: Query embedding (1D or 2D)
            doc_embeddings: Document embeddings (2D)
            
        Returns:
            Similarity scores for each document
        """
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)
        
        # Normalize
        query_norm = query_embedding / np.linalg.norm(query_embedding, axis=1, keepdims=True)
        doc_norm = doc_embeddings / np.linalg.norm(doc_embeddings, axis=1, keepdims=True)
        
        # Cosine similarity via dot product
        similarities = np.dot(query_norm, doc_norm.T).flatten()
        
        return similarities
    
    @property
    def dimension(self) -> int:
        """Get embedding dimension."""
        if self.model is not None:
            return self.model.get_sentence_embedding_dimension()
        return self.EMBEDDING_DIM


class EmbeddingCache:
    """Cache embeddings to disk to avoid recomputation."""
    
    def __init__(self, cache_dir: Path = None):
        self.cache_dir = cache_dir or Path(__file__).parent.parent / "data" / "embedding_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.cache_dir / "metadata.json"
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> dict:
        """Load cache metadata."""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_metadata(self):
        """Save cache metadata."""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f)
    
    def get(self, key: str) -> Optional[np.ndarray]:
        """Get cached embedding by key."""
        if key in self.metadata:
            cache_file = self.cache_dir / f"{key}.npy"
            if cache_file.exists():
                return np.load(cache_file)
        return None
    
    def set(self, key: str, embedding: np.ndarray, text_hash: str = None):
        """Cache an embedding."""
        cache_file = self.cache_dir / f"{key}.npy"
        np.save(cache_file, embedding)
        
        self.metadata[key] = {
            'text_hash': text_hash,
            'shape': list(embedding.shape)
        }
        self._save_metadata()
    
    def has(self, key: str, text_hash: str = None) -> bool:
        """Check if key exists in cache (with optional hash validation)."""
        if key not in self.metadata:
            return False
        
        if text_hash and self.metadata[key].get('text_hash') != text_hash:
            return False
        
        return (self.cache_dir / f"{key}.npy").exists()
    
    def clear(self):
        """Clear all cached embeddings."""
        for f in self.cache_dir.glob("*.npy"):
            f.unlink()
        self.metadata = {}
        self._save_metadata()
