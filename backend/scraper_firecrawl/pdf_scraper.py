#!/usr/bin/env python3
"""
PDF-Scraper für Förderrichtlinien

Findet und scraped PDFs mit Förder-Details
Das ist der GAMECHANGER für Quality Scores!

Author: Claude Code
Version: 1.0
Date: 2025-10-29
"""

import re
import requests
from urllib.parse import urljoin, urlparse
from typing import List, Optional, Dict
import logging

logger = logging.getLogger(__name__)

FIRECRAWL_URL = "http://130.61.137.77:3002"

# PDF-Keywords (deutsch)
PDF_KEYWORDS = [
    'förderrichtlinie',
    'foerderrichtlinie',
    'förderrichtlinien',
    'ausschreibung',
    'bewerbung',
    'antrag',
    'richtlinien',
    'merkblatt',
    'leitfaden',
    'informationen',
]


def find_pdf_links(markdown_text: str, base_url: str) -> List[Dict[str, str]]:
    """
    Findet PDF-Links im Markdown-Text

    Args:
        markdown_text: Gescraptes Markdown
        base_url: Base URL für relative Links

    Returns:
        List of dicts with 'url', 'text', 'score'
    """

    pdf_links = []

    # Regex für Markdown-Links: [text](url)
    pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
    matches = re.findall(pattern, markdown_text)

    for text, url in matches:
        # Only PDFs
        if not url.lower().endswith('.pdf'):
            continue

        # Convert to absolute URL
        absolute_url = urljoin(base_url, url)

        # Skip external domains
        base_domain = urlparse(base_url).netloc
        link_domain = urlparse(absolute_url).netloc
        if base_domain not in link_domain:
            continue

        # Calculate relevance score
        text_lower = text.lower()
        url_lower = url.lower()
        combined = text_lower + ' ' + url_lower

        score = 0
        for keyword in PDF_KEYWORDS:
            if keyword in combined:
                score += 1

        if score > 0:  # Only relevant PDFs
            pdf_links.append({
                'url': absolute_url,
                'text': text,
                'score': score
            })

    # Sort by score (highest first)
    pdf_links.sort(key=lambda x: x['score'], reverse=True)

    # Deduplicate by URL
    seen = set()
    unique_links = []
    for link in pdf_links:
        if link['url'] not in seen:
            seen.add(link['url'])
            unique_links.append(link)

    return unique_links


def scrape_pdf_with_firecrawl(pdf_url: str) -> Optional[str]:
    """
    Scraped PDF mit Firecrawl

    Firecrawl kann PDFs zu Markdown konvertieren!

    Args:
        pdf_url: URL des PDFs

    Returns:
        Markdown text or None on error
    """

    try:
        logger.info(f"   📄 Scrape PDF: {pdf_url[:70]}...")

        response = requests.post(
            f"{FIRECRAWL_URL}/v1/scrape",
            json={"url": pdf_url, "formats": ["markdown"]},
            timeout=90  # PDFs können länger dauern
        )

        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'markdown' in data['data']:
                markdown = data['data']['markdown']
                logger.info(f"      ✅ PDF gescraped: {len(markdown)} chars")
                return markdown

        logger.warning(f"      ❌ Firecrawl Error {response.status_code}")
        return None

    except Exception as e:
        logger.error(f"      ❌ Exception: {e}")
        return None


def scrape_with_pdf_fallback(base_url: str) -> Dict[str, any]:
    """
    Scraped URL mit PDF-Fallback

    1. Scrape Homepage
    2. Suche nach PDF-Links
    3. Falls gefunden: Scrape PDF statt Homepage

    Args:
        base_url: URL der Webseite

    Returns:
        Dict with:
            - text: Combined markdown text
            - source: 'homepage' or 'pdf'
            - pdf_url: URL des PDFs (falls verwendet)
    """

    # 1. Scrape Homepage
    try:
        response = requests.post(
            f"{FIRECRAWL_URL}/v1/scrape",
            json={"url": base_url, "formats": ["markdown"]},
            timeout=60
        )

        if response.status_code != 200:
            logger.error(f"   ❌ Homepage scraping failed: {response.status_code}")
            return {'text': '', 'source': 'error'}

        data = response.json()
        homepage_text = data.get('data', {}).get('markdown', '')

        if not homepage_text:
            return {'text': '', 'source': 'error'}

        logger.info(f"   ✅ Homepage gescraped: {len(homepage_text)} chars")

    except Exception as e:
        logger.error(f"   ❌ Exception: {e}")
        return {'text': '', 'source': 'error'}

    # 2. Suche nach PDFs
    pdf_links = find_pdf_links(homepage_text, base_url)

    if not pdf_links:
        logger.info(f"   ℹ️ Keine relevanten PDFs gefunden → Nutze Homepage")
        return {
            'text': homepage_text,
            'source': 'homepage',
            'pdf_url': None
        }

    logger.info(f"   🎯 {len(pdf_links)} PDFs gefunden!")

    # Log top PDFs
    for i, pdf in enumerate(pdf_links[:3], 1):
        logger.info(f"      {i}. [{pdf['score']}] {pdf['text'][:50]}...")

    # 3. Scrape best PDF
    best_pdf = pdf_links[0]
    pdf_text = scrape_pdf_with_firecrawl(best_pdf['url'])

    if not pdf_text:
        logger.warning(f"   ⚠️ PDF scraping failed → Nutze Homepage")
        return {
            'text': homepage_text,
            'source': 'homepage',
            'pdf_url': None
        }

    # Success!
    logger.info(f"   ✅ Nutze PDF statt Homepage!")
    logger.info(f"      PDF: {len(pdf_text)} chars")
    logger.info(f"      Homepage: {len(homepage_text)} chars")
    logger.info(f"      Faktor: {len(pdf_text) / len(homepage_text):.1f}x mehr Text")

    return {
        'text': pdf_text,
        'source': 'pdf',
        'pdf_url': best_pdf['url']
    }


# Test function
if __name__ == '__main__':
    import sys
    logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

    if len(sys.argv) < 2:
        print("Usage: python pdf_scraper.py <url>")
        print("Example: python pdf_scraper.py https://www.telekom-stiftung.de")
        sys.exit(1)

    test_url = sys.argv[1]

    print("="*80)
    print("PDF-SCRAPER TEST")
    print("="*80)
    print(f"URL: {test_url}")
    print()

    result = scrape_with_pdf_fallback(test_url)

    print()
    print("="*80)
    print("ERGEBNIS")
    print("="*80)
    print(f"Source: {result['source']}")
    print(f"Text Length: {len(result['text'])} chars")
    if result.get('pdf_url'):
        print(f"PDF URL: {result['pdf_url']}")
    print()
    print("Text preview (first 500 chars):")
    print(result['text'][:500])
    print("...")
