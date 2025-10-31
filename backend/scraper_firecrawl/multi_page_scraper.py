#!/usr/bin/env python3
"""
Multi-Page Scraper für bessere LLM-Extraktion

Scraped bis zu 5 relevante Unterseiten pro Stiftung
Kombiniert Text für bessere Quality Scores

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

# Keywords für relevante Links (prioritisiert)
LINK_KEYWORDS = {
    'high_priority': [
        'förder',
        'foerder',
        'antrag',
        'bewerbung',
        'stipendium',
        'ausschreibung',
        'programm',
        'finanzierung',
    ],
    'medium_priority': [
        'unterstützung',
        'unterstuetzung',
        'bildung',
        'schule',
        'grundschule',
        'projekt',
    ],
    'low_priority': [
        'kontakt',
        'über uns',
        'about',
    ]
}


def extract_links_from_markdown(markdown_text: str, base_url: str) -> List[Dict[str, str]]:
    """
    Extrahiert Links aus Markdown-Text

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

        # Skip PDFs, images, etc.
        if absolute_url.lower().endswith(('.pdf', '.jpg', '.png', '.zip', '.doc', '.docx')):
            continue

        # Calculate priority
        text_lower = text.lower()
        url_lower = url.lower()
        combined = text_lower + ' ' + url_lower

        priority = 0
        for keyword in LINK_KEYWORDS['high_priority']:
            if keyword in combined:
                priority = 3
                break

        if priority == 0:
            for keyword in LINK_KEYWORDS['medium_priority']:
                if keyword in combined:
                    priority = 2
                    break

        if priority == 0:
            for keyword in LINK_KEYWORDS['low_priority']:
                if keyword in combined:
                    priority = 1

        if priority > 0:  # Only include relevant links
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


def scrape_page_firecrawl(url: str) -> Optional[str]:
    """
    Scraped eine einzelne Seite mit Firecrawl

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

        logger.warning(f"Firecrawl Error {response.status_code} for {url}")
        return None

    except Exception as e:
        logger.error(f"Exception scraping {url}: {e}")
        return None


def scrape_multi_page(
    base_url: str,
    max_pages: int = 5,
    delay: float = 2.0
) -> Dict[str, any]:
    """
    Scraped mehrere Seiten einer Stiftung

    Args:
        base_url: Homepage URL
        max_pages: Maximale Anzahl zu scrapender Seiten (inkl. Homepage)
        delay: Delay zwischen Requests in Sekunden

    Returns:
        Dict with:
            - combined_text: Kombinierter Markdown-Text
            - pages_scraped: Anzahl erfolgreich gescrapeter Seiten
            - urls: List der gescrapten URLs
    """

    import time

    scraped_pages = []
    urls_scraped = []

    # 1. Scrape Homepage
    logger.info(f"   📄 Scrape Homepage: {base_url}")
    homepage_text = scrape_page_firecrawl(base_url)

    if not homepage_text:
        logger.error(f"   ❌ Homepage scraping failed: {base_url}")
        return {
            'combined_text': '',
            'pages_scraped': 0,
            'urls': []
        }

    scraped_pages.append(homepage_text)
    urls_scraped.append(base_url)

    # 2. Find relevant links
    logger.info(f"   🔍 Suche relevante Links...")
    links = extract_links_from_markdown(homepage_text, base_url)

    if not links:
        logger.info(f"   ⚠️ Keine relevanten Links gefunden")
        return {
            'combined_text': homepage_text,
            'pages_scraped': 1,
            'urls': [base_url]
        }

    logger.info(f"   ✅ Gefunden: {len(links)} relevante Links")

    # Log top links
    for i, link in enumerate(links[:5], 1):
        logger.info(f"      {i}. [{link['priority']}] {link['text'][:50]}... → {link['url'][:60]}...")

    # 3. Scrape detail pages (max_pages - 1, da Homepage schon gescrapet)
    remaining_pages = max_pages - 1

    for i, link in enumerate(links[:remaining_pages]):
        time.sleep(delay)  # Rate limiting

        logger.info(f"   📄 Scrape [{i+1}/{remaining_pages}]: {link['text'][:40]}...")
        detail_text = scrape_page_firecrawl(link['url'])

        if detail_text:
            scraped_pages.append(detail_text)
            urls_scraped.append(link['url'])
            logger.info(f"      ✅ {len(detail_text)} chars")
        else:
            logger.warning(f"      ❌ Failed")

    # 4. Combine text
    combined_text = "\n\n---\n\n".join(scraped_pages)

    logger.info(f"   ✅ Multi-Page Scraping abgeschlossen:")
    logger.info(f"      Pages: {len(scraped_pages)}/{max_pages}")
    logger.info(f"      Total chars: {len(combined_text)}")

    return {
        'combined_text': combined_text,
        'pages_scraped': len(scraped_pages),
        'urls': urls_scraped
    }


def test_multi_page_scraper():
    """Test mit einer Beispiel-Stiftung"""

    logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

    # Test mit Telekom Stiftung (Quality Score = 0.0)
    test_url = "https://www.telekom-stiftung.de"

    print("="*80)
    print("MULTI-PAGE SCRAPER TEST")
    print("="*80)
    print(f"URL: {test_url}")
    print()

    result = scrape_multi_page(test_url, max_pages=5, delay=2.0)

    print()
    print("="*80)
    print("ERGEBNIS")
    print("="*80)
    print(f"Pages scraped: {result['pages_scraped']}")
    print(f"Total text length: {len(result['combined_text'])} chars")
    print()
    print("URLs:")
    for i, url in enumerate(result['urls'], 1):
        print(f"  {i}. {url}")
    print()
    print("Text preview (first 500 chars):")
    print(result['combined_text'][:500])
    print("...")


if __name__ == '__main__':
    test_multi_page_scraper()
