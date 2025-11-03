#!/usr/bin/env python3
"""
Test RAG Search with Real Queries
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), './'))

# Set environment
os.environ['USE_SQLITE'] = 'true'

from rag_indexer.advanced_rag_pipeline import AdvancedRAGPipeline

def test_query(pipeline, query, top_k=3):
    """Test a single query"""
    print(f'\n📝 Query: "{query}"')
    print('-' * 70)

    try:
        results = pipeline.search(query, top_k=top_k)

        if not results:
            print('  ⚠️  No results found')
            return

        print(f'  ✅ Found {len(results)} results:')
        for i, result in enumerate(results, 1):
            score = result.get('score', 'N/A')
            content = result['content'][:150].replace('\n', ' ')
            metadata = result.get('metadata', {})
            funding_id = metadata.get('funding_id', 'Unknown')

            print(f'\n  [{i}] Score: {score:.4f} | Funding ID: {funding_id}')
            print(f'      {content}...')

    except Exception as e:
        print(f'  ❌ Error: {e}')

def main():
    """Run test queries"""
    print('\n' + '=' * 70)
    print('🔍 ADVANCED RAG SEARCH TEST')
    print('=' * 70)

    # Initialize pipeline
    print('\n[INIT] Loading RAG Pipeline...')
    pipeline = AdvancedRAGPipeline(
        enable_query_expansion=False,  # Disable for faster testing
        enable_reranking=True,
        enable_compression=True,
        enable_crag=False
    )
    print('[SUCCESS] Pipeline loaded\n')

    # Test queries
    test_queries = [
        "Förderung für Tablets und digitale Endgeräte",
        "MINT Bildung Grundschule",
        "DigitalPakt Schule Brandenburg",
        "Telekom Stiftung Projekte",
        "Bildungsprojekte finanzieren"
    ]

    for query in test_queries:
        test_query(pipeline, query, top_k=3)

    print('\n' + '=' * 70)
    print('✅ RAG SEARCH TEST COMPLETE')
    print('=' * 70 + '\n')

if __name__ == '__main__':
    main()
