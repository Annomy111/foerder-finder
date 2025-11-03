#!/usr/bin/env python3
"""
Test LLM-based Information Extraction

Tests the llm_extractor.py with real funding data from the database

Usage:
    python test_llm_extraction.py --sources "Telekom,Brandenburg,BMBF"
    python test_llm_extraction.py --all  # Test all sources
    python test_llm_extraction.py --limit 5  # Test first 5 sources
"""

import sys
import os
import argparse
import sqlite3
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from scraper_firecrawl.llm_extractor import (
    extract_with_deepseek,
    validate_extracted_data,
    calculate_quality_score
)


def get_funding_opportunities(db_path='./dev_database.db', limit=None, sources=None):
    """
    Get funding opportunities from database

    Args:
        db_path: Path to SQLite database
        limit: Limit number of results
        sources: List of source names to filter (partial match)

    Returns:
        List of (funding_id, title, provider, cleaned_text) tuples
    """

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = """
    SELECT
        funding_id,
        title,
        provider,
        cleaned_text
    FROM FUNDING_OPPORTUNITIES
    WHERE cleaned_text IS NOT NULL
    AND LENGTH(cleaned_text) > 100
    """

    params = []

    # Filter by sources if provided
    if sources:
        conditions = []
        for source in sources:
            conditions.append("(provider LIKE ? OR title LIKE ?)")
            params.extend([f'%{source}%', f'%{source}%'])

        query += f" AND ({' OR '.join(conditions)})"

    query += " ORDER BY created_at DESC"

    if limit:
        query += f" LIMIT {limit}"

    cursor.execute(query, params)
    results = cursor.fetchall()

    conn.close()

    return [
        (row['funding_id'], row['title'], row['provider'], row['cleaned_text'])
        for row in results
    ]


def test_extraction(funding_id, title, provider, cleaned_text, verbose=False):
    """
    Test extraction for a single funding opportunity

    Returns:
        Dict with results
    """

    print(f"\n{'='*80}")
    print(f"Testing: {title}")
    print(f"Provider: {provider}")
    print(f"Text Length: {len(cleaned_text)} chars")
    print(f"{'='*80}\n")

    # Extract
    start_time = datetime.now()
    extracted = extract_with_deepseek(cleaned_text, title)
    duration = (datetime.now() - start_time).total_seconds()

    if not extracted:
        print(f"❌ Extraction FAILED for {title}\n")
        return {
            'success': False,
            'funding_id': funding_id,
            'title': title,
            'quality_score': 0.0,
            'duration': duration
        }

    # Validate
    validated = validate_extracted_data(extracted)

    # Calculate quality
    quality_score = calculate_quality_score(validated)

    # Print results
    print(f"✅ Extraction SUCCESS")
    print(f"Quality Score: {quality_score}")
    print(f"Duration: {duration:.2f}s")
    print(f"\nExtracted Fields:")
    print(f"  - Deadline: {validated.get('deadline', 'N/A')}")
    print(f"  - Min Amount: {validated.get('min_funding_amount', 'N/A')}")
    print(f"  - Max Amount: {validated.get('max_funding_amount', 'N/A')}")

    eligibility = validated.get('eligibility_criteria', [])
    print(f"  - Eligibility: {len(eligibility) if eligibility else 0} criteria")

    evaluation = validated.get('evaluation_criteria', [])
    print(f"  - Evaluation: {len(evaluation) if evaluation else 0} criteria")

    requirements = validated.get('requirements', [])
    print(f"  - Requirements: {len(requirements) if requirements else 0} items")

    print(f"  - Application URL: {validated.get('application_url', 'N/A')}")
    print(f"  - Contact Email: {validated.get('contact_email', 'N/A')}")

    if verbose:
        import json
        print(f"\n{'-'*80}")
        print("Full Extracted Data:")
        print(json.dumps(validated, indent=2, ensure_ascii=False))
        print(f"{'-'*80}")

    return {
        'success': True,
        'funding_id': funding_id,
        'title': title,
        'provider': provider,
        'quality_score': quality_score,
        'duration': duration,
        'extracted_data': validated
    }


def main():
    parser = argparse.ArgumentParser(description='Test LLM Information Extraction')
    parser.add_argument('--sources', help='Comma-separated list of sources to test (e.g., "Telekom,Brandenburg,BMBF")')
    parser.add_argument('--all', action='store_true', help='Test all sources')
    parser.add_argument('--limit', type=int, help='Limit number of sources to test')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output (show full extracted data)')
    parser.add_argument('--db', default='./dev_database.db', help='Path to SQLite database')

    args = parser.parse_args()

    # Parse sources
    sources_list = None
    if args.sources:
        sources_list = [s.strip() for s in args.sources.split(',')]

    # Get funding opportunities
    print(f"\n🔍 Loading funding opportunities from database...")
    print(f"   DB: {args.db}")

    if sources_list:
        print(f"   Sources filter: {', '.join(sources_list)}")

    if args.limit:
        print(f"   Limit: {args.limit}")

    fundings = get_funding_opportunities(
        db_path=args.db,
        limit=args.limit,
        sources=sources_list
    )

    if not fundings:
        print("\n❌ No funding opportunities found matching criteria")
        sys.exit(1)

    print(f"\n✅ Found {len(fundings)} funding opportunities to test\n")

    # Test each one
    results = []
    for funding_id, title, provider, cleaned_text in fundings:
        result = test_extraction(funding_id, title, provider, cleaned_text, verbose=args.verbose)
        results.append(result)

    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}\n")

    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]

    print(f"Total Tests: {len(results)}")
    print(f"Successful: {len(successful)} ({len(successful)/len(results)*100:.1f}%)")
    print(f"Failed: {len(failed)} ({len(failed)/len(results)*100:.1f}%)")

    if successful:
        avg_quality = sum(r['quality_score'] for r in successful) / len(successful)
        avg_duration = sum(r['duration'] for r in successful) / len(successful)

        print(f"\nAverage Quality Score: {avg_quality:.2f}")
        print(f"Average Duration: {avg_duration:.2f}s")

        # Quality distribution
        high_quality = [r for r in successful if r['quality_score'] >= 0.7]
        medium_quality = [r for r in successful if 0.5 <= r['quality_score'] < 0.7]
        low_quality = [r for r in successful if r['quality_score'] < 0.5]

        print(f"\nQuality Distribution:")
        print(f"  High (>=0.7):   {len(high_quality)} ({len(high_quality)/len(successful)*100:.1f}%)")
        print(f"  Medium (0.5-0.7): {len(medium_quality)} ({len(medium_quality)/len(successful)*100:.1f}%)")
        print(f"  Low (<0.5):     {len(low_quality)} ({len(low_quality)/len(successful)*100:.1f}%)")

        # Top performers
        print(f"\nTop 3 Quality Sources:")
        top_3 = sorted(successful, key=lambda x: x['quality_score'], reverse=True)[:3]
        for i, r in enumerate(top_3, 1):
            print(f"  {i}. {r['title'][:50]}... (Score: {r['quality_score']})")

    if failed:
        print(f"\nFailed Extractions:")
        for r in failed:
            print(f"  ❌ {r['title'][:70]}...")

    # Overall verdict
    print(f"\n{'='*80}")

    if successful and (len(successful) / len(results)) >= 0.8 and avg_quality >= 0.7:
        print("✅ SUCCESS! Extraction quality is EXCELLENT")
        print("   Ready for production rollout")
    elif successful and avg_quality >= 0.5:
        print("⚠️  PARTIAL SUCCESS - Quality needs improvement")
        print("   Consider adjusting extraction prompt or adding more training data")
    else:
        print("❌ FAILED - Extraction quality is too low")
        print("   Review DeepSeek API configuration and prompt template")

    print(f"{'='*80}\n")


if __name__ == '__main__':
    main()
