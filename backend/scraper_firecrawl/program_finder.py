#!/usr/bin/env python3
"""
Intelligent Program Finder

ROOT CAUSE: Wir scrapen Marketing-Homepages statt konkrete Förderprogramm-Seiten!

Lösung: Intelligenter Crawler der:
1. Homepage analyzed
2. Links zu Förderprogramm-Seiten findet
3. Jede Seite auf konkrete Details testet (Quality Score)
4. Nur Seiten mit echten Förderdaten speichert (Score > 0.3)

Author: Claude Code
Version: 3.0 (The Real Fix)
Date: 2025-10-29
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import re
import requests
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional
import logging
import time

from scraper_firecrawl.llm_extractor import (
    extract_with_deepseek,
    validate_extracted_data,
    calculate_quality_score
)

logger = logging.getLogger(__name__)

FIRECRAWL_URL = "http://130.61.137.77:3002"

# Keywords für Förderprogramm-Links (priorisiert)
PROGRAM_KEYWORDS = {
    'high_priority': [
        'förder',
        'foerder',
        'programm',
        'stipendium',
        'ausschreibung',
        'bewerbung',
        'antrag',
        'finanzierung',
    ],
    'medium_priority': [
        'projekt',
        'unterstützung',
        'unterstuetzung',
        'engagement',
        'initiative',
    ],
}

# Blacklist für irrelevante Links
BLACKLIST_KEYWORDS = [
    'presse',
    'news',
    'impressum',
    'datenschutz',
    'kontakt',
    'team',
    'über uns',
    'karriere',
    'jobs',
    'veranstaltung',
    'termine',
]


def scrape_page_firecrawl(url: str) -> Optional[str]:
    """
    Scraped eine Seite mit Firecrawl

    Args:
        url: URL to scrape

    Returns:
        Markdown text or None on error
    """

    try:
        response = requests.post(
            f"{FIRECRAWL_URL}/v1/scrape",
            json={"url": url, "formats": ["markdown"]},
            timeout=60
        )

        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'markdown' in data['data']:
                return data['data']['markdown']

        logger.warning(f"      Firecrawl Error {response.status_code} for {url[:60]}...")
        return None

    except Exception as e:
        logger.error(f"      Exception scraping {url[:60]}...: {e}")
        return None


def extract_links_from_markdown(markdown_text: str, base_url: str) -> List[Dict[str, any]]:
    """
    Extrahiert und priorisiert Links aus Markdown

    Args:
        markdown_text: Gescraptes Markdown
        base_url: Base URL für relative Links

    Returns:
        List of dicts with 'url', 'text', 'priority'
    """

    links = []

    # Regex für Markdown-Links: [text](url)
    pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
    matches = re.findall(pattern, markdown_text)

    for text, url in matches:
        # Skip anchors, mailto, tel
        if url.startswith('#') or url.startswith('mailto:') or url.startswith('tel:'):
            continue

        # Convert to absolute URL
        absolute_url = urljoin(base_url, url)

        # Skip external domains
        base_domain = urlparse(base_url).netloc
        link_domain = urlparse(absolute_url).netloc
        if base_domain not in link_domain:
            continue

        # Skip files
        if absolute_url.lower().endswith(('.pdf', '.jpg', '.png', '.zip', '.doc', '.docx')):
            continue

        # Check if blacklisted
        text_lower = text.lower()
        url_lower = url.lower()
        combined = text_lower + ' ' + url_lower

        is_blacklisted = False
        for keyword in BLACKLIST_KEYWORDS:
            if keyword in combined:
                is_blacklisted = True
                break

        if is_blacklisted:
            continue

        # Calculate priority
        priority = 0
        for keyword in PROGRAM_KEYWORDS['high_priority']:
            if keyword in combined:
                priority = 3
                break

        if priority == 0:
            for keyword in PROGRAM_KEYWORDS['medium_priority']:
                if keyword in combined:
                    priority = 2
                    break

        if priority > 0:  # Only relevant links
            links.append({
                'url': absolute_url,
                'text': text,
                'priority': priority
            })

    # Sort by priority (high first)
    links.sort(key=lambda x: x['priority'], reverse=True)

    # Deduplicate by URL
    seen = set()
    unique_links = []
    for link in links:
        if link['url'] not in seen:
            seen.add(link['url'])
            unique_links.append(link)

    return unique_links


def test_page_quality(url: str, source_name: str) -> float:
    """
    Testet ob eine Seite konkrete Förderdaten enthält

    Args:
        url: URL der Seite
        source_name: Name für Logging

    Returns:
        Quality Score (0.0 - 1.0) oder 0.0 bei Fehler
    """

    # Scrape page
    markdown = scrape_page_firecrawl(url)
    if not markdown:
        return 0.0

    # Extract structured data
    extracted = extract_with_deepseek(markdown, source_name)
    if not extracted:
        return 0.0

    # Validate and score
    validated = validate_extracted_data(extracted)
    quality_score = calculate_quality_score(validated)

    return quality_score


def find_funding_programs(
    base_url: str,
    source_name: str,
    max_pages: int = 10,
    min_quality: float = 0.3,
    delay: float = 3.0
) -> List[Dict[str, any]]:
    """
    Findet konkrete Förderprogramm-Seiten

    Prozess:
    1. Scrape Homepage
    2. Finde relevante Links
    3. Teste jede Seite auf konkrete Details (Quality Score)
    4. Gebe nur Seiten mit Score >= min_quality zurück

    Args:
        base_url: Homepage URL
        source_name: Name der Stiftung/Organisation
        max_pages: Maximale Anzahl zu testender Seiten
        min_quality: Minimaler Quality Score (default: 0.3)
        delay: Delay zwischen Requests in Sekunden

    Returns:
        List of dicts with:
            - url: URL der Programm-Seite
            - title: Link-Text
            - quality_score: Gemessener Quality Score
            - extracted_data: Extrahierte strukturierte Daten
    """

    logger.info(f"   🔍 Suche Förderprogramme: {source_name}")
    logger.info(f"      Homepage: {base_url}")

    # 1. Scrape Homepage
    logger.info(f"      Scrape Homepage...")
    homepage_markdown = scrape_page_firecrawl(base_url)

    if not homepage_markdown:
        logger.error(f"      ❌ Homepage scraping failed")
        return []

    logger.info(f"      ✅ Homepage gescraped: {len(homepage_markdown)} chars")

    # 2. Find links
    logger.info(f"      Suche relevante Links...")
    links = extract_links_from_markdown(homepage_markdown, base_url)

    if not links:
        logger.warning(f"      ⚠️ Keine relevanten Links gefunden")
        return []

    logger.info(f"      ✅ Gefunden: {len(links)} relevante Links")

    # Log top links
    for i, link in enumerate(links[:5], 1):
        logger.info(f"         {i}. [{link['priority']}] {link['text'][:40]}...")

    # 3. Test each page
    found_programs = []
    pages_tested = 0

    for link in links[:max_pages]:
        if pages_tested >= max_pages:
            break

        time.sleep(delay)  # Rate limiting
        pages_tested += 1

        logger.info(f"      [{pages_tested}/{min(len(links), max_pages)}] Teste: {link['text'][:40]}...")
        logger.info(f"         URL: {link['url'][:70]}...")

        # Scrape page
        page_markdown = scrape_page_firecrawl(link['url'])
        if not page_markdown:
            logger.warning(f"         ❌ Scraping failed")
            continue

        logger.info(f"         ✅ Gescraped: {len(page_markdown)} chars")

        # Extract structured data
        logger.info(f"         🤖 LLM-Extraktion...")
        extracted = extract_with_deepseek(page_markdown, f"{source_name} - {link['text']}")

        if not extracted:
            logger.warning(f"         ❌ Extraktion failed")
            continue

        # Validate and score
        validated = validate_extracted_data(extracted)
        quality_score = calculate_quality_score(validated)

        logger.info(f"         📊 Quality Score: {quality_score:.2f}")

        if quality_score >= min_quality:
            logger.info(f"         ✅ ACCEPTED (>= {min_quality})")
            found_programs.append({
                'url': link['url'],
                'title': link['text'],
                'quality_score': quality_score,
                'extracted_data': validated
            })
        else:
            logger.info(f"         ⏭️ REJECTED (< {min_quality})")

    # Summary
    logger.info(f"   📊 Ergebnis:")
    logger.info(f"      Getestete Seiten: {pages_tested}")
    logger.info(f"      Gefundene Programme: {len(found_programs)}")

    if found_programs:
        avg_quality = sum(p['quality_score'] for p in found_programs) / len(found_programs)
        logger.info(f"      Durchschn. Quality Score: {avg_quality:.2f}")
        logger.info(f"")
        logger.info(f"   🎯 Gefundene Programme:")
        for i, prog in enumerate(found_programs, 1):
            logger.info(f"      {i}. [{prog['quality_score']:.2f}] {prog['title'][:50]}...")

    return found_programs


# Test function
if __name__ == '__main__':
    import sys

    logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

    if len(sys.argv) < 2:
        print("Usage: python program_finder.py <url> [source_name]")
        print()
        print("Example:")
        print("  python program_finder.py https://www.telekom-stiftung.de 'Telekom Stiftung'")
        sys.exit(1)

    test_url = sys.argv[1]
    test_name = sys.argv[2] if len(sys.argv) > 2 else "Test Foundation"

    print("="*80)
    print("INTELLIGENT PROGRAM FINDER TEST")
    print("="*80)
    print(f"URL: {test_url}")
    print(f"Source: {test_name}")
    print()

    programs = find_funding_programs(
        test_url,
        test_name,
        max_pages=10,
        min_quality=0.3,
        delay=3.0
    )

    print()
    print("="*80)
    print("ERGEBNIS")
    print("="*80)

    if programs:
        print(f"✅ {len(programs)} Förderprogramm(e) gefunden!")
        print()
        for i, prog in enumerate(programs, 1):
            print(f"{i}. {prog['title']}")
            print(f"   URL: {prog['url']}")
            print(f"   Quality Score: {prog['quality_score']:.2f}")

            # Show key extracted data
            data = prog['extracted_data']
            if data.get('deadline'):
                print(f"   Deadline: {data['deadline']}")
            if data.get('min_funding_amount') or data.get('max_funding_amount'):
                min_amt = data.get('min_funding_amount', 0)
                max_amt = data.get('max_funding_amount', 0)
                print(f"   Budget: {min_amt:,.0f} - {max_amt:,.0f} €")
            if data.get('eligibility_criteria'):
                print(f"   Eligibility: {len(data['eligibility_criteria'])} Kriterien")
            print()
    else:
        print("❌ Keine Förderprogramme gefunden (alle Seiten Quality Score < 0.3)")

    print("="*80)
