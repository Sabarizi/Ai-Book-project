"""
Module for storing and searching embeddings using vector similarity.
"""
import os
import pickle
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
import numpy as np
from pathlib import Path


@dataclass
class SearchResult:
    content: str
    metadata: Dict[str, Any]
    similarity: float
    chunk_id: str


class VectorStore:
    """
    A simple vector store for managing embeddings and performing similarity search.
    """
    
    def __init__(self, storage_path: str = "vector_store.pkl"):
        self.storage_path = Path(storage_path)
        self.embeddings: List[List[float]] = []
        self.contents: List[str] = []
        self.metadata: List[Dict[str, Any]] = []
        self.chunk_ids: List[str] = []
        self._load_storage()
    
    def add_embeddings(self, 
                      embeddings: List[List[float]], 
                      contents: List[str], 
                      metadata: List[Dict[str, Any]], 
                      chunk_ids: List[str]):
        """
        Add embeddings with their associated content and metadata.
        
        Args:
            embeddings: List of embedding vectors
            contents: List of content texts
            metadata: List of metadata dictionaries
            chunk_ids: List of chunk IDs
        """
        self.embeddings.extend(embeddings)
        self.contents.extend(contents)
        self.metadata.extend(metadata)
        self.chunk_ids.extend(chunk_ids)
        
        # Save to storage
        self._save_storage()
    
    def similarity_search(self, 
                         query_embedding: List[float], 
                         top_k: int = 5,
                         threshold: float = 0.3) -> List[SearchResult]:
        """
        Perform similarity search using cosine similarity.
        
        Args:
            query_embedding: The embedding to search for
            top_k: Number of top results to return
            threshold: Minimum similarity threshold
            
        Returns:
            List of search results with content, metadata, and similarity scores
        """
        if not self.embeddings:
            return []
        
        # Convert to numpy arrays for efficient computation
        query_array = np.array(query_embedding)
        embedding_array = np.array(self.embeddings)
        
        # Calculate cosine similarity
        similarities = self._cosine_similarity(query_array, embedding_array)
        
        # Get top-k results
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            similarity = float(similarities[idx])
            if similarity >= threshold:
                results.append(SearchResult(
                    content=self.contents[idx],
                    metadata=self.metadata[idx],
                    similarity=similarity,
                    chunk_id=self.chunk_ids[idx]
                ))
        
        # Sort results by similarity (descending)
        results.sort(key=lambda x: x.similarity, reverse=True)
        return results
    
    def find_relevant_chunks(self, query: str, embedder, top_k: int = 5) -> List[SearchResult]:
        """
        Find relevant content chunks for a query.
        
        Args:
            query: The query string
            embedder: The embedder to use for generating query embedding
            top_k: Number of top results to return
            
        Returns:
            List of search results
        """
        query_embedding = embedder.embed_single_chunk(query)
        return self.similarity_search(query_embedding, top_k=top_k)
    
    def _cosine_similarity(self, query: np.ndarray, embeddings: np.ndarray) -> np.ndarray:
        """
        Calculate cosine similarity between query and embeddings.
        
        Args:
            query: Query embedding (1D array)
            embeddings: Embeddings matrix (2D array)
            
        Returns:
            Similarity scores array
        """
        # Normalize vectors
        query_norm = query / np.linalg.norm(query)
        embeddings_norm = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        
        # Calculate dot product (cosine similarity)
        similarities = np.dot(embeddings_norm, query_norm)
        
        # Replace NaN values with 0 (happens when vector has zero norm)
        similarities = np.nan_to_num(similarities)
        
        return similarities
    
    def _save_storage(self):
        """
        Save the vector store to disk.
        """
        data = {
            'embeddings': self.embeddings,
            'contents': self.contents,
            'metadata': self.metadata,
            'chunk_ids': self.chunk_ids
        }
        
        with open(self.storage_path, 'wb') as f:
            pickle.dump(data, f)
    
    def _load_storage(self):
        """
        Load the vector store from disk.
        """
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'rb') as f:
                    data = pickle.load(f)
                    self.embeddings = data.get('embeddings', [])
                    self.contents = data.get('contents', [])
                    self.metadata = data.get('metadata', [])
                    self.chunk_ids = data.get('chunk_ids', [])
            except Exception as e:
                print(f"Could not load vector store: {e}")
                # Initialize empty store if loading fails
                self.embeddings = []
                self.contents = []
                self.metadata = []
                self.chunk_ids = []
        else:
            # Initialize empty store
            self.embeddings = []
            self.contents = []
            self.metadata = []
            self.chunk_ids = []
    
    def clear(self):
        """
        Clear all embeddings from the store.
        """
        self.embeddings = []
        self.contents = []
        self.metadata = []
        self.chunk_ids = []
        self._save_storage()
    
    def get_count(self) -> int:
        """
        Get the number of embeddings in the store.
        
        Returns:
            Number of embeddings
        """
        return len(self.embeddings)


class QdrantVectorStore(VectorStore):
    """
    Qdrant-based vector store for more advanced use cases.
    """
    
    def __init__(self, 
                 collection_name: str = "book_embeddings",
                 location: str = ":memory:"):  # Use in-memory by default
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.http.models import Distance, VectorParams, PointStruct
        except ImportError:
            raise ImportError("Please install qdrant-client: pip install qdrant-client")
        
        self.collection_name = collection_name
        self.client = QdrantClient(location=location)
        self._initialize_collection()
    
    def _initialize_collection(self):
        """
        Initialize the Qdrant collection.
        """
        from qdrant_client.http.models import Distance, VectorParams
        import uuid
        
        # Check if collection exists
        try:
            self.client.get_collection(self.collection_name)
        except:
            # Create collection if it doesn't exist
            # We'll determine vector size from preloaded embeddings or use default
            self.client.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE)  # Default size for all-MiniLM-L6-v2
            )
    
    def add_embeddings(self,
                      embeddings: List[List[float]],
                      contents: List[str],
                      metadata: List[Dict[str, Any]],
                      chunk_ids: List[str]):
        """
        Add embeddings to Qdrant collection.
        """
        from qdrant_client.http.models import PointStruct

        points = []
        for i, (embedding, content, meta, chunk_id) in enumerate(zip(embeddings, contents, metadata, chunk_ids)):
            point = PointStruct(
                id=i,  # Use index as ID (in real app you'd want more robust IDs)
                vector=embedding,
                payload={
                    "content": content,
                    "metadata": meta,
                    "chunk_id": chunk_id
                }
            )
            points.append(point)

        # Upload points to collection - using the correct Qdrant client method
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
    
    def similarity_search(self,
                         query_embedding: List[float],
                         top_k: int = 5,
                         threshold: float = 0.3) -> List[SearchResult]:
        """
        Perform similarity search in Qdrant collection.
        """
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k,
            score_threshold=threshold
        )

        search_results = []
        for result in results:
            if result.score >= threshold:
                payload = result.payload
                search_results.append(SearchResult(
                    content=payload.get('content', ''),
                    metadata=payload.get('metadata', {}),
                    similarity=result.score,
                    chunk_id=payload.get('chunk_id', '')
                ))

        return search_results