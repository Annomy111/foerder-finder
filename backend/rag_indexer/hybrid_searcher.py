#!/usr/bin/env python3
"""
Hybrid Search System
Combines Dense (Vector) + Sparse (BM25) retrieval with RRF fusion

Research shows hybrid search improves recall by 30-40% vs dense-only
"""

# CRITICAL: pysqlite3-binary workaround MUST be at the very top
# ChromaDB requires SQLite 3.35+, but system SQLite may be older
# This substitutes pysqlite3 module before ChromaDB imports sqlite3
try:
    __import__('pysqlite3')
    import sys as _sys
    _sys.modules['sqlite3'] = _sys.modules.pop('pysqlite3')
except ImportError:
    # pysqlite3-binary not installed, will use system SQLite (may fail)
    pass

import os
import sys
from typing import List, Dict, Tuple, Any
import numpy as np
import json
import pickle
from pathlib import Path
from collections import defaultdict

# BM25 for sparse retrieval
try:
    from rank_bm25 import BM25Okapi
    BM25_AVAILABLE = True
except ImportError:
    BM25_AVAILABLE = False
    print('[WARNING] rank-bm25 not installed. Run: pip install rank-bm25')

import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
from rag_indexer.advanced_embedder import AdvancedEmbedder

load_dotenv()


class HybridSearcher:
    """
    Hybrid search combining dense (embeddings) and sparse (BM25) retrieval
    with Reciprocal Rank Fusion (RRF)
    """

    def __init__(
        self,
        chroma_path: str = None,
        collection_name: str = None,
        bm25_index_path: str = None
    ):
        """
        Initialize hybrid searcher

        Args:
            chroma_path: Path to ChromaDB
            collection_name: ChromaDB collection name
            bm25_index_path: Path to save/load BM25 index
        """
        # ChromaDB setup
        self.chroma_path = chroma_path or os.getenv('CHROMA_DB_PATH', '/opt/chroma_db')
        self.collection_name = collection_name or os.getenv('CHROMA_COLLECTION_NAME', 'funding_docs')

        print(f'[INFO] ChromaDB Path: {self.chroma_path}')
        print(f'[INFO] Collection: {self.collection_name}')

        self.chroma_client = chromadb.PersistentClient(
            path=self.chroma_path,
            settings=Settings(anonymized_telemetry=False)
        )

        self.collection = self.chroma_client.get_collection(name=self.collection_name)

        # Embedder
        self.embedder = AdvancedEmbedder()

        # BM25 setup
        self.bm25_index_path = bm25_index_path or os.path.join(
            self.chroma_path,
            'bm25_index.pkl'
        )

        if BM25_AVAILABLE:
            self.bm25_index = None
            self.bm25_corpus = []
            self.bm25_ids = []
            self.load_bm25_index()
        else:
            print('[WARNING] BM25 not available, using dense-only search')

    def build_bm25_index(self, documents: List[Dict[str, Any]]) -> None:
        """
        Build BM25 index from documents

        Args:
            documents: List of dicts with 'id' and 'text' keys
        """
        if not BM25_AVAILABLE:
            print('[ERROR] BM25 not available')
            return

        print(f'[INFO] Building BM25 index for {len(documents)} documents...')

        # Tokenize documents (simple whitespace + lowercase)
        tokenized_corpus = []
        self.bm25_ids = []

        for doc in documents:
            # Simple tokenization (German-aware tokenization can be added later)
            tokens = doc['text'].lower().split()
            tokenized_corpus.append(tokens)
            self.bm25_ids.append(doc['id'])

        # Build BM25 index
        self.bm25_index = BM25Okapi(tokenized_corpus)
        self.bm25_corpus = [doc['text'] for doc in documents]

        # Save index
        self.save_bm25_index()

        print(f'[SUCCESS] BM25 index built and saved to {self.bm25_index_path}')

    def save_bm25_index(self) -> None:
        """Save BM25 index to disk"""
        if self.bm25_index is None:
            return

        index_data = {
            'bm25_index': self.bm25_index,
            'bm25_corpus': self.bm25_corpus,
            'bm25_ids': self.bm25_ids
        }

        Path(self.bm25_index_path).parent.mkdir(parents=True, exist_ok=True)

        with open(self.bm25_index_path, 'wb') as f:
            pickle.dump(index_data, f)

        print(f'[INFO] BM25 index saved ({len(self.bm25_ids)} documents)')

    def load_bm25_index(self) -> bool:
        """
        Load BM25 index from disk

        Returns:
            True if loaded successfully
        """
        if not os.path.exists(self.bm25_index_path):
            print(f'[INFO] BM25 index not found at {self.bm25_index_path}')
            return False

        try:
            with open(self.bm25_index_path, 'rb') as f:
                index_data = pickle.load(f)

            self.bm25_index = index_data['bm25_index']
            self.bm25_corpus = index_data['bm25_corpus']
            self.bm25_ids = index_data['bm25_ids']

            print(f'[SUCCESS] BM25 index loaded ({len(self.bm25_ids)} documents)')
            return True

        except Exception as e:
            print(f'[ERROR] Failed to load BM25 index: {e}')
            return False

    def dense_search(
        self,
        query: str,
        top_k: int = 20,
        where_filter: Dict = None
    ) -> List[Dict]:
        """
        Dense semantic search using embeddings

        Args:
            query: Search query
            top_k: Number of results
            where_filter: ChromaDB where filter

        Returns:
            List of results with scores
        """
        # Embed query
        query_embedding = self.embedder.embed_query(query)

        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            where=where_filter
        )

        # Format results
        formatted_results = []
        if results and results['ids']:
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    'id': results['ids'][0][i],
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None,
                    'score': 1 - results['distances'][0][i] if 'distances' in results else 1.0
                })

        return formatted_results

    def sparse_search(
        self,
        query: str,
        top_k: int = 20
    ) -> List[Dict]:
        """
        Sparse keyword search using BM25

        Args:
            query: Search query
            top_k: Number of results

        Returns:
            List of results with scores
        """
        if not BM25_AVAILABLE or self.bm25_index is None:
            return []

        # Tokenize query
        tokenized_query = query.lower().split()

        # Get BM25 scores
        scores = self.bm25_index.get_scores(tokenized_query)

        # Get top-k indices
        top_indices = np.argsort(scores)[::-1][:top_k]

        # Format results
        results = []
        for rank, idx in enumerate(top_indices):
            if scores[idx] > 0:  # Only include non-zero scores
                results.append({
                    'id': self.bm25_ids[idx],
                    'text': self.bm25_corpus[idx],
                    'score': float(scores[idx]),
                    'rank': rank
                })

        return results

    def reciprocal_rank_fusion(
        self,
        results_list: List[List[Dict]],
        k: int = 60,
        weights: List[float] = None
    ) -> List[Dict]:
        """
        Reciprocal Rank Fusion (RRF)
        Combines multiple ranked result lists

        Formula: RRF_score(doc) = Σ(weight / (k + rank))

        Args:
            results_list: List of result lists (each is list of dicts with 'id')
            k: RRF constant (default 60, standard value)
            weights: Optional weights for each result list (default: equal weights)

        Returns:
            Fused and re-ranked results
        """
        if weights is None:
            weights = [1.0] * len(results_list)

        # RRF scores
        rrf_scores = defaultdict(float)
        doc_data = {}  # Store document data

        # Process each result list
        for weight, results in zip(weights, results_list):
            for rank, result in enumerate(results):
                doc_id = result['id']
                rrf_scores[doc_id] += weight / (k + rank)

                # Store document data (from first occurrence)
                if doc_id not in doc_data:
                    doc_data[doc_id] = result

        # Sort by RRF score
        ranked_docs = sorted(
            rrf_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Format results
        fused_results = []
        for doc_id, rrf_score in ranked_docs:
            result = doc_data[doc_id].copy()
            result['rrf_score'] = rrf_score
            fused_results.append(result)

        return fused_results

    def hybrid_search(
        self,
        query: str,
        top_k: int = 5,
        dense_weight: float = 0.6,
        sparse_weight: float = 0.4,
        where_filter: Dict = None
    ) -> List[Dict]:
        """
        Hybrid search combining dense and sparse retrieval with RRF

        Args:
            query: Search query
            top_k: Final number of results to return
            dense_weight: Weight for dense retrieval (0-1)
            sparse_weight: Weight for sparse retrieval (0-1)
            where_filter: ChromaDB metadata filter

        Returns:
            Fused and re-ranked results
        """
        # Retrieve from both systems (get more candidates)
        candidate_k = top_k * 4

        # 1. Dense retrieval
        dense_results = self.dense_search(query, top_k=candidate_k, where_filter=where_filter)

        # 2. Sparse retrieval
        sparse_results = self.sparse_search(query, top_k=candidate_k)

        # Apply metadata filter to sparse results (if provided)
        if where_filter and sparse_results:
            # Filter sparse results by metadata
            # Note: This is simplified - production should handle complex where filters
            filtered_sparse = []
            for result in sparse_results:
                # Get metadata from ChromaDB
                chroma_result = self.collection.get(ids=[result['id']])
                if chroma_result and chroma_result['metadatas']:
                    metadata = chroma_result['metadatas'][0]
                    # Check if matches filter (simplified)
                    matches = all(
                        metadata.get(key) == value
                        for key, value in where_filter.items()
                    )
                    if matches:
                        result['metadata'] = metadata
                        filtered_sparse.append(result)
            sparse_results = filtered_sparse

        # 3. Reciprocal Rank Fusion
        fused_results = self.reciprocal_rank_fusion(
            [dense_results, sparse_results],
            weights=[dense_weight, sparse_weight]
        )

        # 4. Return top-k
        return fused_results[:top_k]

    def get_stats(self) -> Dict:
        """Get searcher statistics"""
        stats = {
            'chroma_collection_count': self.collection.count(),
            'bm25_index_size': len(self.bm25_ids) if self.bm25_index else 0,
            'bm25_available': BM25_AVAILABLE,
            'embedder_info': self.embedder.get_model_info()
        }
        return stats


def test_hybrid_search():
    """Test hybrid searcher"""
    print('\n[TEST] Testing Hybrid Searcher\n')

    # Initialize
    searcher = HybridSearcher()

    # Stats
    stats = searcher.get_stats()
    print(f'[INFO] Searcher stats: {json.dumps(stats, indent=2)}')

    # Test query
    query = "Tablets für Grundschule"

    print(f'\n[TEST] Query: "{query}"')

    # Dense search
    print('\n--- Dense Search (Top 3) ---')
    dense_results = searcher.dense_search(query, top_k=3)
    for i, result in enumerate(dense_results):
        print(f'{i+1}. Score: {result["score"]:.4f} | {result["text"][:100]}...')

    # Sparse search (if available)
    if BM25_AVAILABLE and searcher.bm25_index:
        print('\n--- Sparse Search (BM25, Top 3) ---')
        sparse_results = searcher.sparse_search(query, top_k=3)
        for i, result in enumerate(sparse_results):
            print(f'{i+1}. Score: {result["score"]:.4f} | {result["text"][:100]}...')

    # Hybrid search
    print('\n--- Hybrid Search (RRF, Top 5) ---')
    hybrid_results = searcher.hybrid_search(query, top_k=5)
    for i, result in enumerate(hybrid_results):
        print(f'{i+1}. RRF Score: {result["rrf_score"]:.4f} | {result["text"][:100]}...')


if __name__ == '__main__':
    test_hybrid_search()
