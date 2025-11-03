#!/usr/bin/env python3
"""
Advanced Embedder using BGE-M3
State-of-the-art multilingual embeddings for RAG

BGE-M3 Features:
- Multilingual: 100+ languages (German optimized)
- Long context: Up to 8192 tokens
- High dimension: 1024 (vs 384 in old model)
- Top 3 on MTEB multilingual benchmark
"""

import os
import sys
from typing import List, Union
import numpy as np
from dotenv import load_dotenv

# Try to import FlagEmbedding (BGE-M3)
try:
    from FlagEmbedding import BGEM3FlagModel
    BGE_AVAILABLE = True
except ImportError:
    BGE_AVAILABLE = False
    print('[WARNING] FlagEmbedding not installed. Run: pip install -U FlagEmbedding')
    # Fallback to sentence-transformers
    from sentence_transformers import SentenceTransformer

load_dotenv()


class AdvancedEmbedder:
    """
    Advanced embedding model using BGE-M3
    Fallback to sentence-transformers if BGE not available
    """

    def __init__(
        self,
        model_name: str = None,
        device: str = 'cpu',
        use_fp16: bool = True
    ):
        """
        Initialize embedder

        Args:
            model_name: Model to use (default: BGE-M3 or fallback)
            device: 'cpu' or 'cuda'
            use_fp16: Use half precision (faster, less memory)
        """
        self.device = device
        self.use_fp16 = use_fp16 and device == 'cuda'

        if BGE_AVAILABLE and (model_name is None or 'bge' in model_name.lower()):
            # Use BGE-M3 (state-of-the-art)
            self.model_name = model_name or 'BAAI/bge-m3'
            self.embedding_dim = 1024
            self.max_length = 8192
            self.model_type = 'bge-m3'

            print(f'[INFO] Loading BGE-M3 model: {self.model_name}')
            print(f'[INFO] Device: {device}, FP16: {self.use_fp16}')

            self.model = BGEM3FlagModel(
                self.model_name,
                use_fp16=self.use_fp16,
                device=device
            )

            print('[SUCCESS] BGE-M3 model loaded')

        else:
            # Fallback to sentence-transformers
            self.model_name = model_name or os.getenv(
                'EMBEDDING_MODEL_NAME',
                'sentence-transformers/all-MiniLM-L6-v2'
            )
            self.model_type = 'sentence-transformers'

            print(f'[INFO] Loading sentence-transformer model: {self.model_name}')

            self.model = SentenceTransformer(self.model_name, device=device)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            self.max_length = self.model.max_seq_length

            print(f'[SUCCESS] Sentence-transformer model loaded (dim={self.embedding_dim})')

    def embed_documents(
        self,
        texts: List[str],
        batch_size: int = 32,
        show_progress: bool = False
    ) -> np.ndarray:
        """
        Embed multiple documents

        Args:
            texts: List of texts to embed
            batch_size: Batch size for processing
            show_progress: Show progress bar

        Returns:
            Numpy array of embeddings (shape: [len(texts), embedding_dim])
        """
        if not texts:
            return np.array([])

        if self.model_type == 'bge-m3':
            # BGE-M3 encoding
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                max_length=self.max_length,
                return_dense=True,
                return_sparse=False,
                return_colbert_vecs=False
            )
            return embeddings['dense_vecs']

        else:
            # Sentence-transformers encoding
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=show_progress,
                convert_to_numpy=True,
                normalize_embeddings=True
            )
            return embeddings

    def embed_query(self, query: str) -> np.ndarray:
        """
        Embed a single query

        Args:
            query: Query text

        Returns:
            Numpy array embedding (shape: [embedding_dim])
        """
        if self.model_type == 'bge-m3':
            # BGE-M3: queries are embedded the same as documents
            embeddings = self.model.encode(
                [query],
                batch_size=1,
                max_length=512,  # Queries are typically shorter
                return_dense=True,
                return_sparse=False,
                return_colbert_vecs=False
            )
            return embeddings['dense_vecs'][0]

        else:
            # Sentence-transformers
            embedding = self.model.encode(
                query,
                convert_to_numpy=True,
                normalize_embeddings=True
            )
            return embedding

    def get_embedding_dimension(self) -> int:
        """Get embedding dimension"""
        return self.embedding_dim

    def get_model_info(self) -> dict:
        """Get model information"""
        return {
            'model_name': self.model_name,
            'model_type': self.model_type,
            'embedding_dim': self.embedding_dim,
            'max_length': self.max_length,
            'device': self.device,
            'use_fp16': self.use_fp16
        }


def test_embedder():
    """Test embedder"""
    print('\n[TEST] Testing Advanced Embedder\n')

    embedder = AdvancedEmbedder()

    # Test documents
    docs = [
        "Fördermittel für Tablets in Grundschulen",
        "Digitalisierung im Bildungsbereich",
        "BMBF Förderung für MINT-Projekte"
    ]

    # Test query
    query = "Tablets für Schüler"

    # Embed documents
    print('[TEST] Embedding documents...')
    doc_embeddings = embedder.embed_documents(docs)
    print(f'[INFO] Document embeddings shape: {doc_embeddings.shape}')

    # Embed query
    print('[TEST] Embedding query...')
    query_embedding = embedder.embed_query(query)
    print(f'[INFO] Query embedding shape: {query_embedding.shape}')

    # Compute similarities
    print('\n[TEST] Computing similarities:')
    from numpy.linalg import norm

    for i, doc in enumerate(docs):
        similarity = np.dot(query_embedding, doc_embeddings[i]) / (
            norm(query_embedding) * norm(doc_embeddings[i])
        )
        print(f'{i+1}. "{doc[:50]}..." → Similarity: {similarity:.4f}')

    # Model info
    print(f'\n[INFO] Model Info: {embedder.get_model_info()}')


if __name__ == '__main__':
    test_embedder()
