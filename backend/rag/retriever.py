"""
Study Pilot AI - FAISS Vector Store Retriever
Local vector search for RAG with citations
"""

import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# Try to import FAISS
try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False

from .embeddings import EmbeddingModel
from .ingestion import DocumentChunk


@dataclass
class RetrievalResult:
    """A single retrieval result with citation."""
    chunk_id: str
    content: str
    score: float
    source_file: str
    source_type: str
    page_or_slide: int
    course_id: Optional[int]
    topic_id: Optional[int]
    citation: str


class VectorRetriever:
    """
    FAISS-based vector store for semantic retrieval.
    Falls back to brute-force numpy search if FAISS not available.
    """
    
    def __init__(self, index_path: Path = None, embedding_model: EmbeddingModel = None):
        self.index_path = index_path or Path(__file__).parent.parent / "data" / "faiss_index"
        self.index_path.mkdir(parents=True, exist_ok=True)
        
        self.embedding_model = embedding_model or EmbeddingModel()
        
        self.index = None
        self.chunk_metadata: List[dict] = []
        self.dimension = self.embedding_model.dimension
        
        self._load_index()
    
    def _create_index(self):
        """Create a new FAISS index."""
        if HAS_FAISS:
            # Use IndexFlatIP for inner product (cosine similarity with normalized vectors)
            self.index = faiss.IndexFlatIP(self.dimension)
        else:
            # Fallback: store embeddings in numpy array
            self.index = None
            self._embeddings = np.array([]).reshape(0, self.dimension)
    
    def _load_index(self):
        """Load existing index from disk, or create new one."""
        index_file = self.index_path / "index.faiss"
        metadata_file = self.index_path / "metadata.json"
        
        if index_file.exists() and metadata_file.exists():
            try:
                if HAS_FAISS:
                    self.index = faiss.read_index(str(index_file))
                else:
                    embeddings_file = self.index_path / "embeddings.npy"
                    if embeddings_file.exists():
                        self._embeddings = np.load(embeddings_file)
                
                with open(metadata_file, 'r') as f:
                    self.chunk_metadata = json.load(f)
                
                print(f"Loaded index with {len(self.chunk_metadata)} chunks")
                return
            except Exception as e:
                print(f"Error loading index: {e}")
        
        self._create_index()
    
    def save_index(self):
        """Save index to disk."""
        index_file = self.index_path / "index.faiss"
        metadata_file = self.index_path / "metadata.json"
        
        if HAS_FAISS and self.index is not None:
            faiss.write_index(self.index, str(index_file))
        elif hasattr(self, '_embeddings'):
            np.save(self.index_path / "embeddings.npy", self._embeddings)
        
        with open(metadata_file, 'w') as f:
            json.dump(self.chunk_metadata, f)
        
        print(f"Saved index with {len(self.chunk_metadata)} chunks")
    
    def add_documents(self, chunks: List[DocumentChunk], save: bool = True):
        """
        Add document chunks to the index.
        
        Args:
            chunks: List of DocumentChunk objects
            save: Whether to save index after adding
        """
        if not chunks:
            return
        
        # Extract text and metadata
        texts = [chunk.content for chunk in chunks]
        
        # Generate embeddings
        embeddings = self.embedding_model.embed_documents(texts)
        
        # Normalize for cosine similarity
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1  # Avoid division by zero
        embeddings = embeddings / norms
        embeddings = embeddings.astype(np.float32)
        
        # Add to index
        if HAS_FAISS and self.index is not None:
            self.index.add(embeddings)
        else:
            if len(self._embeddings) == 0:
                self._embeddings = embeddings
            else:
                self._embeddings = np.vstack([self._embeddings, embeddings])
        
        # Store metadata
        for chunk in chunks:
            self.chunk_metadata.append({
                'id': chunk.id,
                'content': chunk.content,
                'source_file': chunk.source_file,
                'source_type': chunk.source_type,
                'page_or_slide': chunk.page_or_slide,
                'course_id': chunk.course_id,
                'topic_id': chunk.topic_id,
                'metadata': chunk.metadata
            })
        
        if save:
            self.save_index()
    
    def search(self, query: str, top_k: int = 5, 
               course_id: int = None,
               min_score: float = 0.0) -> List[RetrievalResult]:
        """
        Search for relevant chunks.
        
        Args:
            query: Search query
            top_k: Number of results to return
            course_id: Optional filter by course
            min_score: Minimum similarity score
            
        Returns:
            List of RetrievalResult objects with citations
        """
        if len(self.chunk_metadata) == 0:
            return []
        
        # Embed query
        query_embedding = self.embedding_model.embed_query(query)
        query_embedding = query_embedding / np.linalg.norm(query_embedding)
        query_embedding = query_embedding.astype(np.float32).reshape(1, -1)
        
        # Search
        if HAS_FAISS and self.index is not None:
            # FAISS search
            scores, indices = self.index.search(query_embedding, min(top_k * 2, len(self.chunk_metadata)))
            scores = scores[0]
            indices = indices[0]
        else:
            # Numpy fallback
            similarities = np.dot(self._embeddings, query_embedding.T).flatten()
            indices = np.argsort(similarities)[::-1][:top_k * 2]
            scores = similarities[indices]
        
        # Build results with filtering
        results = []
        for idx, score in zip(indices, scores):
            if idx < 0 or idx >= len(self.chunk_metadata):
                continue
            
            if score < min_score:
                continue
            
            meta = self.chunk_metadata[idx]
            
            # Filter by course if specified
            if course_id is not None and meta.get('course_id') != course_id:
                continue
            
            # Generate citation
            citation = self._generate_citation(meta)
            
            results.append(RetrievalResult(
                chunk_id=meta['id'],
                content=meta['content'],
                score=float(score),
                source_file=meta['source_file'],
                source_type=meta['source_type'],
                page_or_slide=meta['page_or_slide'],
                course_id=meta.get('course_id'),
                topic_id=meta.get('topic_id'),
                citation=citation
            ))
            
            if len(results) >= top_k:
                break
        
        return results
    
    def _generate_citation(self, meta: dict) -> str:
        """Generate a citation string for a chunk."""
        source = meta['source_file']
        source_type = meta['source_type']
        page = meta['page_or_slide']
        
        if source_type == 'pdf':
            return f"[{source}, Page {page}]"
        elif source_type == 'pptx':
            return f"[{source}, Slide {page}]"
        elif source_type == 'syllabus':
            return f"[{source}, Topic {page}]"
        else:
            return f"[{source}]"
    
    def search_with_context(self, query: str, top_k: int = 3,
                            course_id: int = None) -> Dict:
        """
        Search and return formatted context for answering.
        
        Returns:
            Dict with 'context', 'citations', 'sources'
        """
        results = self.search(query, top_k, course_id)
        
        if not results:
            return {
                'context': '',
                'citations': [],
                'sources': [],
                'has_results': False
            }
        
        # Build context string
        context_parts = []
        citations = []
        sources = set()
        
        for i, result in enumerate(results, 1):
            context_parts.append(f"[{i}] {result.content}")
            citations.append({
                'index': i,
                'citation': result.citation,
                'source_file': result.source_file,
                'page': result.page_or_slide,
                'score': result.score
            })
            sources.add(result.source_file)
        
        return {
            'context': "\n\n".join(context_parts),
            'citations': citations,
            'sources': list(sources),
            'has_results': True
        }
    
    def clear(self):
        """Clear the index."""
        self._create_index()
        self.chunk_metadata = []
        self.save_index()
    
    @property
    def size(self) -> int:
        """Get number of chunks in index."""
        return len(self.chunk_metadata)


class AnswerGenerator:
    """
    Generate answers from retrieved context.
    Uses template-based generation (no LLM API required).
    """
    
    ANSWER_TEMPLATES = {
        'definition': "Based on the course materials: {context}\n\n{citation}",
        'explanation': "According to the course content:\n\n{context}\n\nSource: {citation}",
        'comparison': "The course materials indicate:\n\n{context}\n\nReferences: {citation}",
        'procedure': "The procedure according to course materials:\n\n{context}\n\n{citation}",
        'not_found': "I couldn't find information about this in the course materials. The query '{query}' doesn't match any content in the indexed documents."
    }
    
    def __init__(self, retriever: VectorRetriever):
        self.retriever = retriever
    
    def answer(self, query: str, course_id: int = None, top_k: int = 3) -> Dict:
        """
        Answer a query using RAG.
        
        Returns:
            Dict with 'answer', 'citations', 'confidence'
        """
        # Retrieve relevant context
        search_result = self.retriever.search_with_context(query, top_k, course_id)
        
        if not search_result['has_results']:
            return {
                'answer': self.ANSWER_TEMPLATES['not_found'].format(query=query),
                'citations': [],
                'confidence': 0.0,
                'sources': []
            }
        
        # Determine answer type based on query
        query_lower = query.lower()
        if any(w in query_lower for w in ['what is', 'define', 'definition']):
            template = self.ANSWER_TEMPLATES['definition']
        elif any(w in query_lower for w in ['how to', 'steps', 'procedure']):
            template = self.ANSWER_TEMPLATES['procedure']
        elif any(w in query_lower for w in ['compare', 'difference', 'vs']):
            template = self.ANSWER_TEMPLATES['comparison']
        else:
            template = self.ANSWER_TEMPLATES['explanation']
        
        # Format citations
        citation_str = ', '.join([c['citation'] for c in search_result['citations']])
        
        # Generate answer
        answer = template.format(
            context=search_result['context'],
            citation=citation_str
        )
        
        # Calculate confidence from retrieval scores
        avg_score = sum(c['score'] for c in search_result['citations']) / len(search_result['citations'])
        
        return {
            'answer': answer,
            'citations': search_result['citations'],
            'confidence': min(1.0, avg_score),
            'sources': search_result['sources']
        }
