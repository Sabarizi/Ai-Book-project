"""
Main module that orchestrates the RAG pipeline.
"""
from typing import List, Dict, Any, Optional
import os
from pathlib import Path

from .loader import DocusaurusLoader
from .chunker import SemanticChunker, DocumentChunk
from .embedder import Embedder, SentenceTransformerEmbedder
from .vector_store import VectorStore
from .retriever import Retriever
from .responder import Responder
from .authentication import Authentication


class RAGSystem:
    """
    Main RAG system that orchestrates loading, embedding, storing, and retrieval.
    """

    def __init__(self, docs_path: str = "../../../docs"):
        self.docs_path = Path(docs_path)
        self.loader = DocusaurusLoader(docs_path)
        self.chunker = SemanticChunker(max_chunk_size=1000, overlap=100)

        # Use local embedding model by default to avoid API dependencies
        embedder_model = SentenceTransformerEmbedder()
        self.embedder = Embedder(embedder_model)

        # Use the existing embeddings pickle file
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        embeddings_path = os.path.join(current_dir, "..", "book_embeddings.pkl")
        self.vector_store = VectorStore(storage_path=embeddings_path)
        self.retriever = Retriever(self.vector_store, self.embedder)
        self.responder = Responder()
        self.auth = Authentication()

        # Flag to track if embeddings are loaded
        self.embeddings_loaded = len(self.vector_store.embeddings) > 0

    def load_and_embed_documents(self, force_reload: bool = False):
        """
        Load documents, chunk them, and create embeddings.

        Args:
            force_reload: Whether to force reloading even if embeddings exist
        """
        if self.vector_store.get_count() > 0 and not force_reload:
            print(f"Found {self.vector_store.get_count()} existing embeddings. Skipping reload.")
            self.embeddings_loaded = True
            return

        print("Loading documents...")
        documents = self.loader.load_documents()
        print(f"Loaded {len(documents)} documents")

        print("Chunking documents...")
        doc_chunks = self.chunker.chunk_documents(documents)
        print(f"Created {len(doc_chunks)} chunks")

        # Extract content and metadata for embedding
        chunk_contents = [chunk.content for chunk in doc_chunks]
        chunk_metadata = [chunk.metadata for chunk in doc_chunks]
        chunk_ids = [chunk.chunk_id for chunk in doc_chunks]

        print("Generating embeddings...")
        embeddings = self.embedder.embed_chunks(chunk_contents)
        print(f"Generated {len(embeddings)} embeddings")

        # Add to vector store
        self.vector_store.add_embeddings(
            embeddings=embeddings,
            contents=chunk_contents,
            metadata=chunk_metadata,
            chunk_ids=chunk_ids
        )

        print(f"Stored {len(embeddings)} embeddings in vector store")
        self.embeddings_loaded = True

    def query(self,
              user_query: str,
              selected_text: Optional[str] = None,
              api_key: Optional[str] = None,
              top_k: int = 5,
              threshold: float = 0.3) -> Dict[str, Any]:
        """
        Process a user query through the RAG pipeline.

        Args:
            user_query: The user's query
            selected_text: Optional selected text for explanation
            api_key: API key for authentication
            top_k: Number of top results to retrieve
            threshold: Similarity threshold for retrieval

        Returns:
            Dictionary with response and metadata
        """
        try:
            # Check authentication
            if not self.auth.is_authenticated(api_key):
                return {
                    "reply": self.auth.get_auth_required_message(),
                    "sources": [],
                    "retrieved_chunks": 0,
                    "authenticated": False
                }

            # If selected_text is provided, explain that instead of doing RAG
            if selected_text and selected_text.strip():
                # Limit selected text length for safety
                if len(selected_text) > 5000:
                    selected_text = selected_text[:5000] + "... [truncated]"

                response = self.responder.generate_response(
                    query=user_query,
                    context="",  # No context needed when explaining selected text
                    selected_text=selected_text
                )

                return {
                    "reply": response,
                    "sources": [],
                    "retrieved_chunks": 0,
                    "authenticated": True,
                    "selected_text_explanation": True
                }

            # For normal queries, retrieve relevant context and generate response
            context = self.retriever.retrieve_and_format(
                user_query,
                top_k=top_k,
                threshold=threshold
            )

            search_results = self.retriever.retrieve_relevant_chunks(
                user_query,
                top_k=top_k,
                threshold=threshold
            )

            response = self.responder.generate_response(
                query=user_query,
                context=context,
                selected_text=None
            )

            # Get source information
            sources = self.responder.format_sources(search_results)
            if sources:
                response += sources

            # Get metadata about the retrieval
            metadata = self.retriever.get_chunk_metadata(search_results)

            return {
                "reply": response,
                "sources": metadata,
                "retrieved_chunks": len(search_results),
                "authenticated": True,
                "selected_text_explanation": False
            }
        except Exception as e:
            print(f"Error in RAG query: {e}")
            return {
                "reply": "I'm sorry, I encountered an error processing your request. Please try again.",
                "sources": [],
                "retrieved_chunks": 0,
                "authenticated": False,
                "selected_text_explanation": False
            }

    def has_relevant_content(self, query: str, threshold: float = 0.3) -> bool:
        """
        Check if there's relevant content for a query in the knowledge base.

        Args:
            query: The query to check
            threshold: Similarity threshold

        Returns:
            True if relevant content exists, False otherwise
        """
        return self.retriever.has_relevant_content(query, threshold)

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the RAG system.

        Returns:
            Dictionary with system statistics
        """
        return {
            "total_embeddings": self.vector_store.get_count(),
            "embeddings_loaded": self.embeddings_loaded,
            "docs_path": str(self.docs_path)
        }

    def clear_embeddings(self):
        """
        Clear all embeddings from the vector store.
        """
        self.vector_store.clear()
        self.embeddings_loaded = False