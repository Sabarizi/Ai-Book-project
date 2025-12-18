"""
Module for retrieving relevant documents based on queries.
"""
from typing import List, Dict, Any
from .vector_store import VectorStore, SearchResult
from .embedder import Embedder


class Retriever:
    """
    Handles the retrieval of relevant documents based on user queries.
    """
    
    def __init__(self, vector_store: VectorStore, embedder: Embedder):
        self.vector_store = vector_store
        self.embedder = embedder
    
    def retrieve_relevant_chunks(self, 
                                query: str, 
                                top_k: int = 5, 
                                threshold: float = 0.3) -> List[SearchResult]:
        """
        Retrieve the most relevant content chunks for a given query.
        
        Args:
            query: The user's query
            top_k: Number of top results to return
            threshold: Minimum similarity threshold
            
        Returns:
            List of relevant search results
        """
        return self.vector_store.find_relevant_chunks(
            query, 
            self.embedder, 
            top_k=top_k
        )
    
    def format_context(self, results: List[SearchResult]) -> str:
        """
        Format retrieval results into a context string for the LLM.
        
        Args:
            results: List of search results
            
        Returns:
            Formatted context string
        """
        if not results:
            return ""
        
        context_parts = []
        
        for result in results:
            # Extract relevant metadata
            title = result.metadata.get('title', 'Untitled')
            section = result.metadata.get('section', 'General Section')
            source = result.metadata.get('source_file', 'Unknown')
            
            context = f"""
Source: {source}
Section: {section}
Title: {title}

Content: {result.content}

Relevance Score: {result.similarity:.3f}
---
            """.strip()
            
            context_parts.append(context)
        
        return "\n\n".join(context_parts)
    
    def retrieve_and_format(self, 
                           query: str, 
                           top_k: int = 5, 
                           threshold: float = 0.3) -> str:
        """
        Retrieve relevant chunks and format them as context for the LLM.
        
        Args:
            query: The user's query
            top_k: Number of top results to return
            threshold: Minimum similarity threshold
            
        Returns:
            Formatted context string
        """
        results = self.retrieve_relevant_chunks(query, top_k, threshold)
        return self.format_context(results)
    
    def get_chunk_metadata(self, results: List[SearchResult]) -> List[Dict[str, Any]]:
        """
        Extract metadata from search results for additional context.
        
        Args:
            results: List of search results
            
        Returns:
            List of metadata dictionaries
        """
        return [
            {
                'source_file': result.metadata.get('source_file', ''),
                'section': result.metadata.get('section', ''),
                'title': result.metadata.get('title', ''),
                'chapter': result.metadata.get('chapter', ''),
                'similarity': result.similarity
            }
            for result in results
        ]
    
    def has_relevant_content(self, 
                            query: str, 
                            threshold: float = 0.3) -> bool:
        """
        Check if there's relevant content for the query.
        
        Args:
            query: The user's query
            threshold: Minimum similarity threshold
            
        Returns:
            True if relevant content exists, False otherwise
        """
        results = self.retrieve_relevant_chunks(query, top_k=1, threshold=threshold)
        return len(results) > 0