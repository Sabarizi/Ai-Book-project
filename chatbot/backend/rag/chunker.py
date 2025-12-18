"""
Module for chunking documents into semantic chunks for embedding.
"""
import re
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class DocumentChunk:
    content: str
    metadata: Dict[str, Any]
    chunk_id: str


class SemanticChunker:
    """
    Splits documents into semantic chunks based on document structure.
    """
    
    def __init__(self, max_chunk_size: int = 1000, overlap: int = 100):
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap
    
    def chunk_documents(self, documents: List[Dict[str, Any]]) -> List[DocumentChunk]:
        """
        Chunk a list of documents into semantic chunks.
        
        Args:
            documents: List of document dictionaries with content and metadata
            
        Returns:
            List of DocumentChunk objects
        """
        chunks = []
        
        for i, doc in enumerate(documents):
            doc_chunks = self._chunk_single_document(doc)
            for j, chunk in enumerate(doc_chunks):
                chunk_id = f"doc_{i}_chunk_{j}"
                chunks.append(DocumentChunk(
                    content=chunk['content'],
                    metadata=chunk['metadata'],
                    chunk_id=chunk_id
                ))
        
        return chunks
    
    def _chunk_single_document(self, document: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Chunk a single document based on its structure.
        
        Args:
            document: Document with content and metadata
            
        Returns:
            List of chunk dictionaries
        """
        content = document['content']
        metadata = document['metadata']
        
        # If content is already structured into sections (from loader), use those
        # Otherwise, implement fallback chunking
        chunks = []
        
        # Check if content is already a semantic unit (like a section with heading)
        if content.count('\n') < 5 or self._is_single_section(content):
            # This is already a semantic unit, no need to split further
            chunks.append({
                'content': content,
                'metadata': metadata
            })
        else:
            # Fallback: split into overlapping chunks based on semantic boundaries
            semantic_chunks = self._split_by_semantic_boundaries(content)
            
            for chunk_content in semantic_chunks:
                chunk_metadata = metadata.copy()
                chunk_metadata['chunk_size'] = len(chunk_content)
                chunks.append({
                    'content': chunk_content,
                    'metadata': chunk_metadata
                })
        
        return chunks
    
    def _is_single_section(self, content: str) -> bool:
        """
        Determine if content represents a single semantic section.
        """
        # Check if content has a clear heading at the beginning
        lines = content.strip().split('\n')
        if not lines:
            return True
            
        first_line = lines[0].strip()
        # If first line looks like a heading or the content is short
        if (first_line.startswith('#') or 
            len(content) < 500 or 
            (len(lines) < 10 and any(keyword in content.lower() for keyword in 
                                    ['overview', 'introduction', 'summary', 'conclusion']))):
            return True
            
        return False
    
    def _split_by_semantic_boundaries(self, content: str) -> List[str]:
        """
        Split content by semantic boundaries like paragraphs, lists, etc.
        """
        chunks = []
        
        # Split by paragraphs (double newline)
        paragraphs = content.split('\n\n')
        
        current_chunk = ""
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
                
            # If adding this paragraph would exceed the limit
            if len(current_chunk) + len(paragraph) > self.max_chunk_size:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                
                # If the paragraph itself is too long, split it
                if len(paragraph) > self.max_chunk_size:
                    sub_chunks = self._split_long_paragraph(paragraph)
                    chunks.extend(sub_chunks[:-1])  # Add all but the last one
                    current_chunk = sub_chunks[-1]  # Keep the last one
                else:
                    current_chunk = paragraph
            else:
                current_chunk += f"\n\n{paragraph}" if current_chunk else paragraph
        
        # Add the last chunk if it exists
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        # Further split any chunks that are still too large
        final_chunks = []
        for chunk in chunks:
            if len(chunk) > self.max_chunk_size:
                final_chunks.extend(self._force_split_chunk(chunk))
            else:
                final_chunks.append(chunk)
        
        return final_chunks
    
    def _split_long_paragraph(self, paragraph: str) -> List[str]:
        """
        Split a long paragraph into smaller chunks.
        """
        chunks = []
        sentences = re.split(r'(?<=[.!?])\s+', paragraph)
        
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) > self.max_chunk_size:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk += f" {sentence}" if current_chunk else sentence
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks if chunks else [paragraph[:self.max_chunk_size]]
    
    def _force_split_chunk(self, chunk: str) -> List[str]:
        """
        Force split a chunk that is too large, preserving semantic meaning where possible.
        """
        # Try to split by sentences first
        sentences = re.split(r'(?<=[.!?])\s+', chunk)
        
        if len(sentences) == 1 or len(max(sentences, key=len)) > self.max_chunk_size:
            # If sentences are too long, fall back to character-level splitting
            return self._split_by_characters(chunk)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) > self.max_chunk_size:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk += f" {sentence}" if current_chunk else sentence
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _split_by_characters(self, chunk: str) -> List[str]:
        """
        Split a chunk by characters as a last resort.
        """
        if len(chunk) <= self.max_chunk_size:
            return [chunk]
        
        chunks = []
        for i in range(0, len(chunk), self.max_chunk_size - self.overlap):
            chunk_end = min(i + self.max_chunk_size, len(chunk))
            chunks.append(chunk[chunk_end - self.max_chunk_size:chunk_end])
        
        return chunks