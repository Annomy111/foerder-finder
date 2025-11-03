#!/usr/bin/env python3
"""
Cross-Encoder Reranker
Reranks retrieved documents using cross-encoder model

Research shows reranking improves precision by 15-25%
"""

import os
import sys
from typing import List, Tuple, Dict, Any
import numpy as np

# Try to import FlagEmbedding reranker
try:
    from FlagEmbedding import FlagReranker
    RERANKER_AVAILABLE = True
except ImportError:
    RERANKER_AVAILABLE = False
    print('[WARNING] FlagEmbedding not installed. Reranking unavailable.')
    print('[INFO] Run: pip install -U FlagEmbedding')


class Reranker:
    """
    Cross-encoder reranker for better precision

    Cross-encoders jointly encode query and document,
    providing more accurate relevance scores than bi-encoders
    """

    def __init__(
        self,
        model_name: str = 'BAAI/bge-reranker-base',
        device: str = 'cpu',
        use_fp16: bool = True
    ):
        """
        Initialize reranker

        Args:
            model_name: Reranker model name
            device: 'cpu' or 'cuda'
            use_fp16: Use half precision (faster)
        """
        self.model_name = model_name
        self.device = device
        self.use_fp16 = use_fp16 and device == 'cuda'

        if RERANKER_AVAILABLE:
            print(f'[INFO] Loading reranker model: {model_name}')
            print(f'[INFO] Device: {device}, FP16: {self.use_fp16}')

            self.model = FlagReranker(
                model_name,
                use_fp16=self.use_fp16,
                device=device
            )

            print('[SUCCESS] Reranker model loaded')
            self.available = True
        else:
            print('[WARNING] Reranker not available (FlagEmbedding not installed)')
            self.model = None
            self.available = False

    def rerank(
        self,
        query: str,
        documents: List[str],
        top_k: int = 5,
        batch_size: int = 32,
        max_length: int = 1024
    ) -> List[Tuple[str, float]]:
        """
        Rerank documents using cross-encoder

        Args:
            query: Search query
            documents: List of document texts
            top_k: Number of top documents to return
            batch_size: Batch size for processing
            max_length: Max sequence length (query + doc)

        Returns:
            List of (document, score) tuples, sorted by score (descending)
        """
        if not self.available:
            # Fallback: return documents as-is with dummy scores
            return [(doc, 1.0) for doc in documents[:top_k]]

        if not documents:
            return []

        # Prepare query-document pairs
        pairs = [[query, doc] for doc in documents]

        # Score all pairs
        scores = self.model.compute_score(
            pairs,
            batch_size=batch_size,
            max_length=max_length
        )

        # Convert to list if single score
        if isinstance(scores, (float, np.floating)):
            scores = [scores]

        # Sort by score (descending)
        ranked = sorted(
            zip(documents, scores),
            key=lambda x: x[1],
            reverse=True
        )

        # Return top-k
        return ranked[:top_k]

    def rerank_with_metadata(
        self,
        query: str,
        results: List[Dict[str, Any]],
        text_key: str = 'text',
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Rerank results that include metadata

        Args:
            query: Search query
            results: List of result dicts (must have text_key)
            text_key: Key for document text in result dict
            top_k: Number of top results

        Returns:
            Reranked results with 'rerank_score' added
        """
        if not results:
            return []

        # Extract texts
        documents = [r[text_key] for r in results]

        # Rerank
        ranked_docs = self.rerank(query, documents, top_k=top_k)

        # Match back to original results
        ranked_results = []
        for doc, score in ranked_docs:
            # Find matching result
            for result in results:
                if result[text_key] == doc:
                    result_copy = result.copy()
                    result_copy['rerank_score'] = float(score)
                    ranked_results.append(result_copy)
                    break

        return ranked_results


def test_reranker():
    """Test reranker"""
    print('\n[TEST] Testing Reranker\n')

    reranker = Reranker()

    if not reranker.available:
        print('[SKIP] Reranker not available, test skipped')
        return

    # Test query
    query = "Tablets für Grundschule kaufen"

    # Test documents (varying relevance)
    documents = [
        "Die Stadt Berlin fördert den Kauf von Tablets für Grundschulen mit bis zu 50.000 Euro.",
        "Digitalisierung im Bildungswesen: Ein Überblick über aktuelle Trends.",
        "iPad Pro 2024: Technische Spezifikationen und Preise.",
        "BMBF Förderung: Digitale Endgeräte für Schulen in Brandenburg.",
        "Grundschule am See sucht neue Lehrkräfte für Mathematik."
    ]

    # Rerank
    print(f'[TEST] Query: "{query}"')
    print(f'[TEST] Reranking {len(documents)} documents...\n')

    ranked = reranker.rerank(query, documents, top_k=5)

    # Print results
    print('[RESULTS] Reranked documents:')
    for i, (doc, score) in enumerate(ranked):
        print(f'\n{i+1}. Score: {score:.4f}')
        print(f'   Text: {doc[:100]}...')

    # Test with metadata
    print('\n\n[TEST] Reranking with metadata...\n')

    results_with_metadata = [
        {'id': '1', 'text': doc, 'original_rank': i}
        for i, doc in enumerate(documents)
    ]

    reranked_with_metadata = reranker.rerank_with_metadata(
        query,
        results_with_metadata,
        text_key='text',
        top_k=3
    )

    print('[RESULTS] Reranked results with metadata:')
    for i, result in enumerate(reranked_with_metadata):
        print(f'\n{i+1}. Rerank Score: {result["rerank_score"]:.4f}')
        print(f'   Original Rank: {result["original_rank"]}')
        print(f'   Text: {result["text"][:80]}...')


if __name__ == '__main__':
    test_reranker()
