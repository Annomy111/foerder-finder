#!/usr/bin/env python3
"""
Test Multi-Page Extraktion vs. Single-Page

Vergleicht Quality Scores:
- Single-Page: Homepage only
- Multi-Page: Homepage + 4 Detail-Seiten

Author: Claude Code
Date: 2025-10-29
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from scraper_firecrawl.multi_page_scraper import scrape_multi_page
from scraper_firecrawl.llm_extractor import (
    extract_with_deepseek,
    validate_extracted_data,
    calculate_quality_score
)
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_single_vs_multi_page(url: str, stiftung_name: str):
    """
    Vergleicht Single-Page vs. Multi-Page Extraktion

    Args:
        url: Stiftungs-URL
        stiftung_name: Name der Stiftung
    """

    print("="*80)
    print(f"TEST: {stiftung_name}")
    print("="*80)
    print(f"URL: {url}")
    print()

    # 1. Multi-Page Scraping
    logger.info("🔄 Multi-Page Scraping...")
    result = scrape_multi_page(url, max_pages=5, delay=2.0)

    if not result['combined_text']:
        logger.error("❌ Multi-Page Scraping failed")
        return

    logger.info(f"✅ Scraped {result['pages_scraped']} pages, {len(result['combined_text'])} chars")
    print()

    # 2. LLM-Extraktion auf kombiniertem Text
    logger.info("🤖 LLM-Extraktion (Multi-Page)...")
    extracted_multi = extract_with_deepseek(result['combined_text'], stiftung_name)

    if not extracted_multi:
        logger.error("❌ LLM-Extraktion failed")
        return

    validated_multi = validate_extracted_data(extracted_multi)
    quality_multi = calculate_quality_score(validated_multi)

    logger.info(f"✅ Quality Score (Multi-Page): {quality_multi}")
    print()

    # 3. Vergleich mit Single-Page (nur Homepage)
    logger.info("📊 Vergleich mit Single-Page...")

    # Für Vergleich: Nur Homepage-Text (erster Teil vor "---")
    homepage_text = result['combined_text'].split('\n\n---\n\n')[0]
    logger.info(f"   Homepage-Text: {len(homepage_text)} chars")

    extracted_single = extract_with_deepseek(homepage_text, stiftung_name)

    if extracted_single:
        validated_single = validate_extracted_data(extracted_single)
        quality_single = calculate_quality_score(validated_single)
        logger.info(f"   Quality Score (Single-Page): {quality_single}")
    else:
        quality_single = 0.0
        logger.warning("   Quality Score (Single-Page): 0.0 (Extraction failed)")

    print()
    print("="*80)
    print("ERGEBNIS")
    print("="*80)
    print(f"Single-Page (Homepage):    Quality Score = {quality_single:.2f}")
    print(f"Multi-Page (5 Seiten):     Quality Score = {quality_multi:.2f}")
    print(f"Verbesserung:              +{quality_multi - quality_single:.2f} ({(quality_multi - quality_single) / (quality_single + 0.01) * 100:.0f}%)")
    print()

    # Details
    print("Extrahierte Felder (Multi-Page):")
    print(f"  - Deadline: {validated_multi.get('deadline', 'N/A')}")
    print(f"  - Budget: {validated_multi.get('min_funding_amount', 'N/A')} - {validated_multi.get('max_funding_amount', 'N/A')} €")
    print(f"  - Eligibility: {len(validated_multi.get('eligibility_criteria', [])) if validated_multi.get('eligibility_criteria') else 0} Kriterien")
    print(f"  - Evaluation: {len(validated_multi.get('evaluation_criteria', [])) if validated_multi.get('evaluation_criteria') else 0} Kriterien")
    print(f"  - Requirements: {len(validated_multi.get('requirements', [])) if validated_multi.get('requirements') else 0} Anforderungen")
    print(f"  - Contact Email: {validated_multi.get('contact_email', 'N/A')}")
    print(f"  - Application URL: {validated_multi.get('application_url', 'N/A')}")

    if validated_multi.get('evaluation_criteria'):
        print(f"\n  Evaluation Criteria:")
        for crit in validated_multi.get('evaluation_criteria', [])[:5]:
            print(f"    - {crit}")

    if validated_multi.get('requirements'):
        print(f"\n  Requirements:")
        for req in validated_multi.get('requirements', [])[:5]:
            print(f"    - {req}")

    print()
    print("="*80)


if __name__ == '__main__':
    # Test mit 3 Low-Quality Stiftungen
    test_cases = [
        ("https://www.telekom-stiftung.de", "Deutsche Telekom Stiftung"),
        ("https://www.bosch-stiftung.de", "Robert Bosch Stiftung"),
        ("https://www.vodafone-stiftung.de", "Vodafone Stiftung"),
    ]

    for url, name in test_cases:
        test_single_vs_multi_page(url, name)
        print("\n\n")
