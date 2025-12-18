"""
Module for generating embeddings for document chunks.
"""
import os
from typing import List, Dict, Any
from abc import ABC, abstractmethod
import numpy as np


class EmbeddingModel(ABC):
    """
    Abstract base class for embedding models.
    """

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Input text to embed

        Returns:
            Embedding vector as a list of floats
        """
        pass

    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of input texts to embed

        Returns:
            List of embedding vectors
        """
        pass


class OpenAIEmbedder(EmbeddingModel):
    """
    OpenAI-based embedding model.
    """

    def __init__(self, model_name: str = "text-embedding-ada-002"):
        try:
            import openai
            self.openai = openai
        except ImportError:
            raise ImportError("Please install openai: pip install openai")

        # Set API key from environment
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        self.openai.api_key = api_key
        self.model_name = model_name

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        """
        response = self.openai.Embedding.create(
            input=text,
            model=self.model_name
        )
        return response['data'][0]['embedding']

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        """
        if len(texts) == 0:
            return []

        # OpenAI API has limits, so we may need to batch
        all_embeddings = []

        # Split into batches if needed (OpenAI has 2048 max input)
        batch_size = min(2048, len(texts))
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            response = self.openai.Embedding.create(
                input=batch,
                model=self.model_name
            )

            batch_embeddings = [item['embedding'] for item in response['data']]
            all_embeddings.extend(batch_embeddings)

        return all_embeddings


class SentenceTransformerEmbedder(EmbeddingModel):
    """
    SentenceTransformer-based embedding model (local/embedded).
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        try:
            from sentence_transformers import SentenceTransformer
            import warnings
            import logging
            # Suppress warnings that might occur during model loading
            logging.getLogger().setLevel(logging.ERROR)  # Reduce logging level
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self.model = SentenceTransformer(model_name)
        except ImportError:
            raise ImportError("Please install sentence-transformers: pip install sentence-transformers")
        except Exception as e:
            # Handle potential compatibility issues with newer versions of dependencies
            import sys
            print(f"Error initializing SentenceTransformer: {e}")
            raise

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        """
        try:
            if not text.strip():
                # Return a zero vector for empty text
                return [0.0] * 384  # Default size for all-MiniLM-L6-v2
            embedding = self.model.encode([text], convert_to_numpy=True)
            return embedding[0].tolist()
        except Exception as e:
            print(f"Error embedding text: {e}")
            # Return a zero vector as fallback
            return [0.0] * 384

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        """
        if len(texts) == 0:
            return []

        try:
            # Filter out empty texts to prevent errors
            filtered_texts = [text for text in texts if text and text.strip()]
            if not filtered_texts:
                return [[0.0] * 384 for _ in texts]  # Return zeros for all inputs

            embeddings = self.model.encode(filtered_texts, convert_to_numpy=True)
            result = [embedding.tolist() for embedding in embeddings]

            # If we filtered out some texts, pad the result with zeros
            result_with_padding = []
            text_idx = 0
            for text in texts:
                if text and text.strip():
                    result_with_padding.append(result[text_idx])
                    text_idx += 1
                else:
                    result_with_padding.append([0.0] * 384)  # Zero vector for empty text

            return result_with_padding
        except Exception as e:
            print(f"Error embedding texts: {e}")
            # Return zero vectors as fallback
            return [[0.0] * 384 for _ in texts]


class Embedder:
    """
    Main embedder class that manages embedding generation.
    """

    def __init__(self, embedding_model: EmbeddingModel = None):
        if embedding_model is None:
            # Try sentence transformer as default, fallback to simple approach if it fails
            try:
                self.embedding_model = SentenceTransformerEmbedder()
            except Exception as e:
                print(f"Warning: Could not initialize SentenceTransformer: {e}")
                print("Falling back to simple embedding approach...")
                # For now, we'll raise an error since we need embeddings to work
                raise e
        else:
            self.embedding_model = embedding_model

    def embed_chunks(self, chunks: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of text chunks.

        Args:
            chunks: List of text chunks to embed

        Returns:
            List of embedding vectors
        """
        if not chunks:
            return []

        return self.embedding_model.embed_texts(chunks)

    def embed_single_chunk(self, chunk: str) -> List[float]:
        """
        Generate embedding for a single text chunk.

        Args:
            chunk: Single text chunk to embed

        Returns:
            Embedding vector as a list of floats
        """
        return self.embedding_model.embed_text(chunk)