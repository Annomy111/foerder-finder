#!/usr/bin/env python3
"""
Quick Stiftungen Scraper für SQLite (MVP)
"""

import sqlite3
import requests
import logging
from datetime import datetime
from urllib.parse import urlparse
import uuid

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

FIRECRAWL_URL = "http://130.61.137.77:3002"
DB_PATH = "dev_database.db"

STIFTUNG_URLS = [
    "https://www.deutsches-stiftungszentrum.de",
    "https://www.stiftungen.org",
    "https://www.dkjs.de",
    "https://www.bosch-stiftung.de",
    "https://www.bertelsmann-stiftung.de",
    "https://www.joachim-herz-stiftung.de",
    "https://www.buergerstiftungen.org",
    "https://www.software-ag-stiftung.de",
]

NAME_MAP = {
    'deutsches-stiftungszentrum.de': 'Deutsches Stiftungszentrum',
    'stiftungen.org': 'Bundesverband Deutscher Stiftungen',
    'dkjs.de': 'Deutsche Kinder- und Jugendstiftung',
    'bosch-stiftung.de': 'Robert Bosch Stiftung',
    'bertelsmann-stiftung.de': 'Bertelsmann Stiftung',
    'joachim-herz-stiftung.de': 'Joachim Herz Stiftung',
    'buergerstiftungen.org': 'Bürgerstiftungen Deutschland',
    'software-ag-stiftung.de': 'Software AG Stiftung',
}

def get_title_from_url(url):
    """Extrahiere Titel aus URL"""
    domain = urlparse(url).netloc.replace('www.', '')
    return NAME_MAP.get(domain, domain.split('.')[0].title() + ' Stiftung')

def scrape_page(url):
    """Scrape mit Firecrawl"""
    logger.info(f"📄 Scrape: {url}")
    try:
        response = requests.post(
            f"{FIRECRAWL_URL}/v1/scrape",
            json={"url": url, "formats": ["markdown"], "onlyMainContent": True},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json().get('data', {})
            return {
                'success': True,
                'url': url,
                'markdown': data.get('markdown', ''),
                'title': data.get('title', get_title_from_url(url))
            }
        else:
            logger.error(f"   ❌ Error: {response.status_code}")
            return {'success': False}
    except Exception as e:
        logger.error(f"   ❌ Exception: {e}")
        return {'success': False}

def save_to_db(conn, page_data):
    """Save to SQLite"""
    if not page_data.get('success'):
        return False

    cursor = conn.cursor()

    # Check if exists
    cursor.execute("SELECT funding_id FROM FUNDING_OPPORTUNITIES WHERE source_url = ?", (page_data['url'],))
    if cursor.fetchone():
        logger.info(f"   ⏭️ Bereits vorhanden")
        return False

    # Insert
    funding_id = str(uuid.uuid4())
    title = page_data['title'][:500]
    markdown = page_data['markdown']
    description = markdown[:1000] if len(markdown) > 1000 else markdown

    cursor.execute("""
        INSERT INTO FUNDING_OPPORTUNITIES (
            funding_id, title, description, cleaned_text, region,
            funder_name, source_url, last_scraped, source_type
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        funding_id, title, description, markdown, 'Bundesweit',
        page_data['title'], page_data['url'], datetime.now(), 'stiftung'
    ))

    conn.commit()
    logger.info(f"   ✅ Gespeichert: {title}")
    return True

def main():
    """Main"""
    logger.info("="*70)
    logger.info("🚀 STIFTUNGEN SCRAPER (MVP)")
    logger.info("="*70)
    logger.info(f"📋 {len(STIFTUNG_URLS)} URLs\n")

    conn = sqlite3.connect(DB_PATH)
    success_count = 0

    for i, url in enumerate(STIFTUNG_URLS, 1):
        logger.info(f"[{i}/{len(STIFTUNG_URLS)}]")
        page_data = scrape_page(url)
        if save_to_db(conn, page_data):
            success_count += 1

    conn.close()

    logger.info("\n" + "="*70)
    logger.info(f"✅ {success_count}/{len(STIFTUNG_URLS)} erfolgreich gespeichert")
    logger.info("Nächster Schritt: RAG-Index neu bauen!")

if __name__ == "__main__":
    main()
