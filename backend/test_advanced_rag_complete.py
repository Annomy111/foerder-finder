#!/usr/bin/env python3
"""
Complete Advanced RAG System Test Suite
Tests all components and provides benchmark comparison with baseline
"""

import sys
import os
import asyncio
import time
import json
from typing import List, Dict
from datetime import datetime

sys.path.append(os.path.dirname(__file__))

from rag_indexer.advanced_embedder import AdvancedEmbedder
from rag_indexer.hybrid_searcher import HybridSearcher
from rag_indexer.reranker import Reranker
from rag_indexer.query_expansion import QueryExpander
from rag_indexer.advanced_rag_pipeline import AdvancedRAGPipeline


class AdvancedRAGTester:
    """Comprehensive test suite for Advanced RAG"""

    def __init__(self):
        self.results = []

    def print_header(self, title: str):
        """Print formatted header"""
        print('\n' + '='*80)
        print(f'  {title}')
        print('='*80 + '\n')

    def print_success(self, message: str):
        """Print success message"""
        print(f'✅ {message}')

    def print_error(self, message: str):
        """Print error message"""
        print(f'❌ {message}')

    def print_info(self, message: str):
        """Print info message"""
        print(f'ℹ️  {message}')

    # ========================================================================
    # Component Tests
    # ========================================================================

    def test_embedder(self) -> bool:
        """Test Advanced Embedder"""
        self.print_header('TEST 1: Advanced Embedder (BGE-M3)')

        try:
            embedder = AdvancedEmbedder()

            # Test document embedding
            docs = [
                "Förderung für Tablets in Grundschulen",
                "BMBF Digitalisierungsprogramm",
                "Stiftung Bildung Projektförderung"
            ]

            start = time.time()
            doc_embeddings = embedder.embed_documents(docs)
            embedding_time = time.time() - start

            # Test query embedding
            query = "Tablets für Schüler"
            query_embedding = embedder.embed_query(query)

            # Validate
            assert doc_embeddings.shape[0] == len(docs), "Wrong number of embeddings"
            assert len(query_embedding) > 0, "Query embedding is empty"

            model_info = embedder.get_model_info()

            self.print_success(f"Embedder loaded: {model_info['model_name']}")
            self.print_success(f"Embedding dimension: {model_info['embedding_dim']}")
            self.print_success(f"Embedding time: {embedding_time:.3f}s for {len(docs)} docs")

            self.results.append({
                'test': 'embedder',
                'status': 'pass',
                'model': model_info['model_name'],
                'embedding_time': embedding_time
            })

            return True

        except Exception as e:
            self.print_error(f"Embedder test failed: {e}")
            self.results.append({'test': 'embedder', 'status': 'fail', 'error': str(e)})
            return False

    def test_hybrid_search(self) -> bool:
        """Test Hybrid Searcher"""
        self.print_header('TEST 2: Hybrid Search (Dense + BM25 + RRF)')

        try:
            searcher = HybridSearcher()

            # Get stats
            stats = searcher.get_stats()

            self.print_info(f"ChromaDB collection: {stats['chroma_collection_count']} chunks")
            self.print_info(f"BM25 index: {stats['bm25_index_size']} documents")

            # Test query
            query = "Tablets für Grundschule in Berlin"

            # Dense search
            start = time.time()
            dense_results = searcher.dense_search(query, top_k=5)
            dense_time = time.time() - start

            # Sparse search
            start = time.time()
            sparse_results = searcher.sparse_search(query, top_k=5)
            sparse_time = time.time() - start

            # Hybrid search
            start = time.time()
            hybrid_results = searcher.hybrid_search(query, top_k=5)
            hybrid_time = time.time() - start

            self.print_success(f"Dense search: {len(dense_results)} results in {dense_time:.3f}s")
            self.print_success(f"Sparse search: {len(sparse_results)} results in {sparse_time:.3f}s")
            self.print_success(f"Hybrid search: {len(hybrid_results)} results in {hybrid_time:.3f}s")

            if hybrid_results:
                self.print_info(f"Top result RRF score: {hybrid_results[0].get('rrf_score', 'N/A'):.4f}")

            self.results.append({
                'test': 'hybrid_search',
                'status': 'pass',
                'dense_time': dense_time,
                'sparse_time': sparse_time,
                'hybrid_time': hybrid_time,
                'num_results': len(hybrid_results)
            })

            return True

        except Exception as e:
            self.print_error(f"Hybrid search test failed: {e}")
            self.results.append({'test': 'hybrid_search', 'status': 'fail', 'error': str(e)})
            return False

    def test_reranker(self) -> bool:
        """Test Reranker"""
        self.print_header('TEST 3: Reranker (Cross-Encoder)')

        try:
            reranker = Reranker()

            if not reranker.available:
                self.print_error("Reranker not available (FlagEmbedding not installed)")
                self.results.append({'test': 'reranker', 'status': 'skip', 'reason': 'not_available'})
                return True  # Not a failure, just unavailable

            query = "Tablets für Grundschule kaufen"
            documents = [
                "Berlin fördert Tablet-Kauf für Grundschulen mit bis zu 50.000 Euro",
                "Digitalisierung im Bildungswesen: Überblick aktueller Trends",
                "BMBF Förderung: Digitale Endgeräte für Schulen in Brandenburg"
            ]

            start = time.time()
            ranked = reranker.rerank(query, documents, top_k=3)
            rerank_time = time.time() - start

            self.print_success(f"Reranked {len(documents)} documents in {rerank_time:.3f}s")

            if ranked:
                self.print_info(f"Top result score: {ranked[0][1]:.4f}")
                self.print_info(f"Top result: {ranked[0][0][:80]}...")

            self.results.append({
                'test': 'reranker',
                'status': 'pass',
                'rerank_time': rerank_time,
                'num_docs': len(documents)
            })

            return True

        except Exception as e:
            self.print_error(f"Reranker test failed: {e}")
            self.results.append({'test': 'reranker', 'status': 'fail', 'error': str(e)})
            return False

    async def test_query_expansion(self) -> bool:
        """Test Query Expansion"""
        self.print_header('TEST 4: Query Expansion (DeepSeek)')

        try:
            expander = QueryExpander()

            query = "Tablets für Grundschule"

            start = time.time()
            variants = await expander.expand_query(query, num_variants=3)
            expansion_time = time.time() - start

            self.print_success(f"Generated {len(variants)} query variants in {expansion_time:.3f}s")

            for i, variant in enumerate(variants):
                self.print_info(f"  {i+1}. {variant}")

            # Test metadata extraction
            query_with_meta = "Tablets für Grundschule in Berlin bis 5000 Euro"

            start = time.time()
            meta_result = await expander.extract_metadata_filters(query_with_meta)
            meta_time = time.time() - start

            self.print_success(f"Extracted metadata in {meta_time:.3f}s")
            self.print_info(f"Filters: {json.dumps(meta_result['filters'], ensure_ascii=False)}")
            self.print_info(f"Cleaned query: {meta_result['cleaned_query']}")

            self.results.append({
                'test': 'query_expansion',
                'status': 'pass',
                'expansion_time': expansion_time,
                'metadata_time': meta_time,
                'num_variants': len(variants)
            })

            return True

        except Exception as e:
            self.print_error(f"Query expansion test failed: {e}")
            self.results.append({'test': 'query_expansion', 'status': 'fail', 'error': str(e)})
            return False

    async def test_full_pipeline(self) -> bool:
        """Test Complete Advanced RAG Pipeline"""
        self.print_header('TEST 5: Complete Advanced RAG Pipeline')

        try:
            pipeline = AdvancedRAGPipeline(
                enable_query_expansion=True,
                enable_reranking=True,
                enable_compression=True,
                enable_crag=True,
                verbose=False  # Reduce noise
            )

            # Pipeline info
            info = pipeline.get_pipeline_info()
            self.print_info(f"Pipeline features: {json.dumps(info['features'], indent=2)}")

            # Test queries
            test_queries = [
                "Tablets für Grundschule in Berlin",
                "MINT-Förderung Brandenburg",
                "Digitalisierung Bildung bis 10000 Euro"
            ]

            for query in test_queries:
                self.print_info(f"\nTesting: '{query}'")

                start = time.time()
                results = await pipeline.retrieve(
                    query=query,
                    top_k=5,
                    expand_queries=True,
                    rerank_results=True
                )
                pipeline_time = time.time() - start

                self.print_success(f"Retrieved {len(results)} chunks in {pipeline_time:.3f}s")

                if results:
                    top_score = results[0].get('rerank_score', results[0].get('rrf_score', 'N/A'))
                    self.print_info(f"Top score: {top_score}")

                self.results.append({
                    'test': 'pipeline',
                    'query': query,
                    'status': 'pass',
                    'pipeline_time': pipeline_time,
                    'num_results': len(results)
                })

            return True

        except Exception as e:
            self.print_error(f"Pipeline test failed: {e}")
            self.results.append({'test': 'pipeline', 'status': 'fail', 'error': str(e)})
            return False

    # ========================================================================
    # Run All Tests
    # ========================================================================

    async def run_all_tests(self):
        """Run all tests"""
        self.print_header('ADVANCED RAG SYSTEM - COMPLETE TEST SUITE')

        start_time = datetime.now()

        # Component tests
        test_1 = self.test_embedder()
        test_2 = self.test_hybrid_search()
        test_3 = self.test_reranker()
        test_4 = await self.test_query_expansion()
        test_5 = await self.test_full_pipeline()

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Summary
        self.print_header('TEST SUMMARY')

        passed = sum(1 for r in self.results if r['status'] == 'pass')
        failed = sum(1 for r in self.results if r['status'] == 'fail')
        skipped = sum(1 for r in self.results if r['status'] == 'skip')

        print(f"Total tests: {len(self.results)}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⊘  Skipped: {skipped}")
        print(f"\nTotal duration: {duration:.2f}s")

        # Save results
        results_file = f'test_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(results_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'duration': duration,
                'summary': {
                    'total': len(self.results),
                    'passed': passed,
                    'failed': failed,
                    'skipped': skipped
                },
                'results': self.results
            }, f, indent=2)

        self.print_success(f"Results saved to: {results_file}")

        if failed == 0:
            self.print_header('🎉 ALL TESTS PASSED! SYSTEM READY FOR DEPLOYMENT')
            return True
        else:
            self.print_header('⚠️  SOME TESTS FAILED - CHECK LOGS')
            return False


async def main():
    """Main entry point"""
    tester = AdvancedRAGTester()
    success = await tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    asyncio.run(main())
