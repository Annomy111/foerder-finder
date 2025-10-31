#!/usr/bin/env python3
"""
Stiftungen MVP Scraper
Zweck: Schnelles Scraping von Stiftungen direkt in FUNDING_OPPORTUNITIES

Strategie:
- Scrape Stiftungsseiten mit Firecrawl
- Speichere rohen Markdown in FUNDING_OPPORTUNITIES
- Setze source_type='stiftung' zur Unterscheidung
- LLM-Nachbearbeitung später möglich

Vorteil: Sofort nutzbar, RAG funktioniert auch mit rohen Texten!
"""

import sys
import os
import logging
import requests
from datetime import datetime
from urllib.parse import urlparse

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.database import get_db_cursor
from dotenv import load_dotenv

load_dotenv()

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StiftungenMVPScraper:
    """MVP Scraper für Stiftungen"""

    def __init__(self):
        self.firecrawl_url = "http://130.61.137.77:3002"

        # Stiftungs-URLs (handkuratiert für MVP)
        self.stiftung_urls = [
            # Deutsches Stiftungszentrum
            "https://www.deutsches-stiftungszentrum.de",
            "https://www.deutsches-stiftungszentrum.de/leistungen",

            # Bundesverband
            "https://www.stiftungen.org",
            "https://www.stiftungen.org/stiftungen/zahlen-und-daten",

            # Deutsche Kinder- und Jugendstiftung
            "https://www.dkjs.de",
            "https://www.dkjs.de/themen/alle-programme",

            # Robert Bosch Stiftung
            "https://www.bosch-stiftung.de",
            "https://www.bosch-stiftung.de/de/projekt",

            # Bertelsmann Stiftung
            "https://www.bertelsmann-stiftung.de",
            "https://www.bertelsmann-stiftung.de/de/themen",

            # Weitere wichtige Stiftungen
            "https://www.joachim-herz-stiftung.de",
            "https://www.buergerstiftungen.org",
            "https://www.software-ag-stiftung.de",
        ]

    def scrape_page(self, url: str) -> dict:
        """
        Scrape eine Seite mit Firecrawl

        Args:
            url: URL zum Scrapen

        Returns:
            dict mit 'success', 'url', 'markdown', 'title'
        """
        logger.info(f"📄 Scrape: {url}")

        try:
            response = requests.post(
                f"{self.firecrawl_url}/v1/scrape",
                json={
                    "url": url,
                    "formats": ["markdown"],
                    "onlyMainContent": True
                },
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                page_data = data.get('data', {})

                return {
                    'success': True,
                    'url': url,
                    'markdown': page_data.get('markdown', ''),
                    'title': page_data.get('title', self.extract_title_from_url(url))
                }
            else:
                logger.error(f"   ❌ Fehler: {response.status_code}")
                return {'success': False, 'url': url}

        except Exception as e:
            logger.error(f"   ❌ Exception: {e}")
            return {'success': False, 'url': url}

    def extract_title_from_url(self, url: str) -> str:
        """Extrahiere einen Titel aus der URL"""
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '')

        # Konvertiere Domain zu Titel
        name_map = {
            'deutsches-stiftungszentrum.de': 'Deutsches Stiftungszentrum',
            'stiftungen.org': 'Bundesverband Deutscher Stiftungen',
            'dkjs.de': 'Deutsche Kinder- und Jugendstiftung',
            'bosch-stiftung.de': 'Robert Bosch Stiftung',
            'bertelsmann-stiftung.de': 'Bertelsmann Stiftung',
            'joachim-herz-stiftung.de': 'Joachim Herz Stiftung',
            'buergerstiftungen.org': 'Bürgerstiftungen Deutschland',
            'software-ag-stiftung.de': 'Software AG Stiftung',
        }

        return name_map.get(domain, domain.split('.')[0].title() + ' Stiftung')

    def save_to_database(self, page_data: dict):
        """
        Speichere gescrapte Seite in FUNDING_OPPORTUNITIES

        Args:
            page_data: Dict mit url, markdown, title
        """
        if not page_data.get('success'):
            return

        try:
            with get_db_cursor() as cursor:
                # Prüfe ob URL bereits existiert
                cursor.execute("""
                    SELECT funding_id FROM FUNDING_OPPORTUNITIES
                    WHERE source_url = :url
                """, {'url': page_data['url']})

                existing = cursor.fetchone()
                if existing:
                    logger.info(f"   ⏭️ Bereits vorhanden: {page_data['url']}")
                    return

                # Bereite Daten vor
                title = page_data['title'][:500]  # Max 500 chars
                markdown = page_data['markdown']
                description = markdown[:1000] if len(markdown) > 1000 else markdown
                cleaned_text = markdown  # Voller Text für RAG

                # Extrahiere Funder Name aus Titel
                funder_name = page_data['title']

                # Insert
                cursor.execute("""
                    INSERT INTO FUNDING_OPPORTUNITIES (
                        title, description, cleaned_text, region,
                        funder_name, source_url, scraped_at,
                        source_type
                    ) VALUES (
                        :title, :description, :cleaned_text, :region,
                        :funder_name, :source_url, :scraped_at,
                        'stiftung'
                    )
                """, {
                    'title': title,
                    'description': description,
                    'cleaned_text': cleaned_text,
                    'region': 'Bundesweit',  # Default
                    'funder_name': funder_name,
                    'source_url': page_data['url'],
                    'scraped_at': datetime.now()
                })

                logger.info(f"   ✅ Gespeichert: {title}")

        except Exception as e:
            logger.error(f"   ❌ DB-Fehler: {e}")

    def run(self):
        """Führe kompletten Scraping-Prozess aus"""
        logger.info("="*70)
        logger.info("🚀 STIFTUNGEN MVP SCRAPER")
        logger.info("="*70)
        logger.info(f"📋 {len(self.stiftung_urls)} URLs zum Scrapen\n")

        success_count = 0
        fail_count = 0

        for i, url in enumerate(self.stiftung_urls, 1):
            logger.info(f"\n[{i}/{len(self.stiftung_urls)}] {url}")

            # Scrape
            page_data = self.scrape_page(url)

            # Save to DB
            if page_data.get('success'):
                self.save_to_database(page_data)
                success_count += 1
            else:
                fail_count += 1

        # Summary
        logger.info("\n" + "="*70)
        logger.info("📊 ZUSAMMENFASSUNG")
        logger.info("="*70)
        logger.info(f"✅ Erfolgreich: {success_count}")
        logger.info(f"❌ Fehlgeschlagen: {fail_count}")
        logger.info(f"📈 Erfolgsquote: {success_count/len(self.stiftung_urls)*100:.1f}%")
        logger.info("\nNächster Schritt: RAG-Index neu bauen!")
        logger.info("  → python3 rag_indexer/build_index.py")


def main():
    """Entry Point"""
    scraper = StiftungenMVPScraper()
    scraper.run()


if __name__ == "__main__":
    main()
