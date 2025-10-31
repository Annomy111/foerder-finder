#!/usr/bin/env python3
"""
Stiftungen Scraper mit Firecrawl
Zweck: Automatisches Scraping von Stiftungsdatenbanken für Bildungsförderung

Unterstützte Quellen:
- Deutsches Stiftungszentrum (DSZ)
- Bundesverband Deutscher Stiftungen
- Deutsche Kinder- und Jugendstiftung (DKJS)
- Robert Bosch Stiftung
- Bertelsmann Stiftung
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional
import requests
import cx_Oracle

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StiftungenScraper:
    """Scraper für Stiftungsdatenbanken mit Firecrawl"""

    def __init__(self):
        """Initialisiere Scraper mit Firecrawl und Datenbank"""
        self.firecrawl_url = "http://130.61.137.77:3002"
        self.db_connection = None

        # Stiftungsquellen-Konfiguration
        self.sources = {
            'deutsches_stiftungszentrum': {
                'name': 'Deutsches Stiftungszentrum',
                'base_url': 'https://www.deutsches-stiftungszentrum.de',
                'crawl_paths': [
                    '/stiftungen',
                    '/foerderung/bildung'
                ],
                'max_depth': 3,
                'priority': 'HIGH'
            },
            'bundesverband_stiftungen': {
                'name': 'Bundesverband Deutscher Stiftungen',
                'base_url': 'https://www.stiftungen.org',
                'crawl_paths': [
                    '/stiftungssuche',
                    '/verzeichnis/bildung'
                ],
                'max_depth': 2,
                'priority': 'HIGH'
            },
            'dkjs': {
                'name': 'Deutsche Kinder- und Jugendstiftung',
                'base_url': 'https://www.dkjs.de',
                'crawl_paths': [
                    '/programme',
                    '/foerderung'
                ],
                'max_depth': 2,
                'priority': 'HIGH'
            },
            'robert_bosch_stiftung': {
                'name': 'Robert Bosch Stiftung',
                'base_url': 'https://www.bosch-stiftung.de',
                'crawl_paths': [
                    '/foerderung/bildung',
                    '/programme'
                ],
                'max_depth': 2,
                'priority': 'MEDIUM'
            },
            'bertelsmann_stiftung': {
                'name': 'Bertelsmann Stiftung',
                'base_url': 'https://www.bertelsmann-stiftung.de',
                'crawl_paths': [
                    '/themen/bildung',
                    '/projekte'
                ],
                'max_depth': 2,
                'priority': 'MEDIUM'
            }
        }

        self.llm_extraction_prompt = """
        Analysiere diese Webseite und extrahiere strukturierte Informationen über die Stiftung:

        WICHTIG: Extrahiere NUR, wenn es sich um eine echte Stiftung/Förderorganisation handelt!

        Extrahiere folgende Informationen:
        1. Name der Stiftung
        2. Website/Kontakt
        3. Beschreibung (max 500 Zeichen)
        4. Förderbereiche (Liste)
        5. Fördersummen (Min/Max in EUR)
        6. Zielgruppen (speziell: Grundschule erwähnt?)
        7. Bewerbungsfristen
        8. Kontaktdaten (Email, Telefon)
        9. Bundesland/Region
        10. Anforderungen für Bewerbung

        Gib die Daten im folgenden JSON-Format zurück:
        {
            "name": "Name der Stiftung",
            "website": "https://...",
            "beschreibung": "Kurzbeschreibung",
            "foerderbereiche": ["Bildung", "MINT", ...],
            "foerdersumme_min": 5000,
            "foerdersumme_max": 50000,
            "zielgruppen": ["Grundschule", ...],
            "bewerbungsfrist": "31.12.2025 oder 'laufend'",
            "kontakt_email": "...",
            "kontakt_telefon": "...",
            "kontakt_ansprechpartner": "...",
            "bundesland": "Berlin oder 'Bundesweit'",
            "stadt": "...",
            "anforderungen": ["Projektkonzept", "Budget", ...]
        }

        Falls keine Stiftung erkannt wird, gib zurück: {"error": "keine_stiftung"}
        """

    def connect_db(self):
        """Verbinde mit Oracle-Datenbank"""
        try:
            # Oracle Connection (anpassen an deine Wallet/Config)
            dsn = cx_Oracle.makedsn(
                "your-db-host",
                1521,
                service_name="your-service"
            )
            self.db_connection = cx_Oracle.connect(
                user=os.getenv("ORACLE_USER"),
                password=os.getenv("ORACLE_PASSWORD"),
                dsn=dsn
            )
            logger.info("✅ Datenbankverbindung hergestellt")
        except Exception as e:
            logger.error(f"❌ DB-Verbindung fehlgeschlagen: {e}")
            raise

    def crawl_with_firecrawl(self, source_config: Dict) -> List[Dict]:
        """
        Crawle eine Stiftungsquelle mit Firecrawl

        Args:
            source_config: Konfiguration der Quelle

        Returns:
            Liste von gecrawlten Seiten
        """
        logger.info(f"🔍 Crawle: {source_config['name']}")

        crawl_results = []

        for path in source_config['crawl_paths']:
            url = source_config['base_url'] + path

            try:
                # Firecrawl API Call
                response = requests.post(
                    f"{self.firecrawl_url}/v1/crawl",
                    json={
                        "url": url,
                        "crawlerOptions": {
                            "maxDepth": source_config['max_depth'],
                            "limit": 100,
                            "excludes": [
                                "*/impressum*",
                                "*/datenschutz*",
                                "*/cookies*"
                            ]
                        },
                        "pageOptions": {
                            "onlyMainContent": True,
                            "includeHtml": False,
                            "waitFor": 2000
                        }
                    },
                    timeout=300
                )

                if response.status_code == 200:
                    data = response.json()
                    crawl_results.extend(data.get('data', []))
                    logger.info(f"  ✅ {len(data.get('data', []))} Seiten gecrawlt von {url}")
                else:
                    logger.warning(f"  ⚠️ Fehler beim Crawlen von {url}: {response.status_code}")

            except Exception as e:
                logger.error(f"  ❌ Exception beim Crawlen von {url}: {e}")
                continue

        return crawl_results

    def extract_stiftung_with_llm(self, page_content: str, source_url: str) -> Optional[Dict]:
        """
        Extrahiere Stiftungsinformationen mit LLM

        Args:
            page_content: Markdown-Content der Seite
            source_url: URL der Quelle

        Returns:
            Strukturierte Stiftungsdaten oder None
        """
        try:
            # DeepSeek API Call für Extraktion
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": self.llm_extraction_prompt},
                        {"role": "user", "content": page_content[:4000]}  # Limit für Token
                    ],
                    "temperature": 0.3,
                    "max_tokens": 1000
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                extracted_text = result['choices'][0]['message']['content']

                # Parse JSON aus LLM Response
                stiftung_data = json.loads(extracted_text)

                if "error" not in stiftung_data:
                    stiftung_data['quelle_url'] = source_url
                    stiftung_data['scraped_at'] = datetime.now().isoformat()
                    return stiftung_data

        except Exception as e:
            logger.debug(f"LLM-Extraktion fehlgeschlagen: {e}")

        return None

    def save_stiftung_to_db(self, stiftung: Dict, quelle: str):
        """
        Speichere Stiftung in Oracle-Datenbank

        Args:
            stiftung: Stiftungsdaten (Dict)
            quelle: Name der Quelle (z.B. 'DSZ')
        """
        if not self.db_connection:
            logger.error("Keine DB-Verbindung!")
            return

        try:
            cursor = self.db_connection.cursor()

            # Prüfe ob Stiftung bereits existiert (Name + Website)
            cursor.execute("""
                SELECT stiftung_id FROM STIFTUNGEN
                WHERE UPPER(name) = UPPER(:name)
                AND (website = :website OR :website IS NULL)
            """, {
                'name': stiftung.get('name', ''),
                'website': stiftung.get('website')
            })

            existing = cursor.fetchone()

            if existing:
                logger.info(f"  ⏭️ Stiftung existiert bereits: {stiftung.get('name')}")
                return

            # Inseriere neue Stiftung
            cursor.execute("""
                INSERT INTO STIFTUNGEN (
                    name, website, beschreibung, foerderbereiche,
                    foerdersumme_min, foerdersumme_max, bewerbungsfrist,
                    kontakt_email, kontakt_telefon, kontakt_ansprechpartner,
                    bundesland, stadt, zielgruppen, anforderungen,
                    quelle, quelle_url
                ) VALUES (
                    :name, :website, :beschreibung, :foerderbereiche,
                    :foerdersumme_min, :foerdersumme_max, :bewerbungsfrist,
                    :kontakt_email, :kontakt_telefon, :kontakt_ansprechpartner,
                    :bundesland, :stadt, :zielgruppen, :anforderungen,
                    :quelle, :quelle_url
                )
            """, {
                'name': stiftung.get('name', 'Unbekannte Stiftung'),
                'website': stiftung.get('website'),
                'beschreibung': stiftung.get('beschreibung'),
                'foerderbereiche': json.dumps(stiftung.get('foerderbereiche', []), ensure_ascii=False),
                'foerdersumme_min': stiftung.get('foerdersumme_min'),
                'foerdersumme_max': stiftung.get('foerdersumme_max'),
                'bewerbungsfrist': stiftung.get('bewerbungsfrist'),
                'kontakt_email': stiftung.get('kontakt_email'),
                'kontakt_telefon': stiftung.get('kontakt_telefon'),
                'kontakt_ansprechpartner': stiftung.get('kontakt_ansprechpartner'),
                'bundesland': stiftung.get('bundesland'),
                'stadt': stiftung.get('stadt'),
                'zielgruppen': json.dumps(stiftung.get('zielgruppen', []), ensure_ascii=False),
                'anforderungen': json.dumps(stiftung.get('anforderungen', []), ensure_ascii=False),
                'quelle': quelle,
                'quelle_url': stiftung.get('quelle_url')
            })

            self.db_connection.commit()
            logger.info(f"  ✅ Gespeichert: {stiftung.get('name')}")

        except Exception as e:
            logger.error(f"  ❌ DB-Fehler beim Speichern: {e}")
            self.db_connection.rollback()

    def scrape_source(self, source_key: str):
        """
        Scrape eine einzelne Stiftungsquelle

        Args:
            source_key: Key der Quelle (z.B. 'deutsches_stiftungszentrum')
        """
        source_config = self.sources.get(source_key)
        if not source_config:
            logger.error(f"Quelle '{source_key}' nicht gefunden!")
            return

        logger.info(f"\n{'='*60}")
        logger.info(f"🚀 Starte Scraping: {source_config['name']}")
        logger.info(f"{'='*60}\n")

        # Crawle mit Firecrawl
        pages = self.crawl_with_firecrawl(source_config)
        logger.info(f"📄 {len(pages)} Seiten gecrawlt")

        # Extrahiere Stiftungen mit LLM
        stiftungen_found = 0
        for i, page in enumerate(pages, 1):
            logger.info(f"🔍 Analysiere Seite {i}/{len(pages)}...")

            stiftung_data = self.extract_stiftung_with_llm(
                page.get('markdown', ''),
                page.get('url', '')
            )

            if stiftung_data:
                self.save_stiftung_to_db(stiftung_data, source_key.upper())
                stiftungen_found += 1

        logger.info(f"\n✅ {stiftungen_found} Stiftungen aus {source_config['name']} gespeichert\n")

    def scrape_all(self, priority_filter: Optional[str] = None):
        """
        Scrape alle konfigurierten Quellen

        Args:
            priority_filter: Nur Quellen mit dieser Priorität (HIGH, MEDIUM, LOW)
        """
        sources_to_scrape = []

        for key, config in self.sources.items():
            if priority_filter is None or config.get('priority') == priority_filter:
                sources_to_scrape.append(key)

        logger.info(f"🎯 Scrape {len(sources_to_scrape)} Quellen...")

        for source_key in sources_to_scrape:
            try:
                self.scrape_source(source_key)
            except Exception as e:
                logger.error(f"❌ Fehler bei {source_key}: {e}")
                continue

    def close(self):
        """Schließe Datenbankverbindung"""
        if self.db_connection:
            self.db_connection.close()
            logger.info("DB-Verbindung geschlossen")


def main():
    """Main Entry Point"""
    scraper = StiftungenScraper()

    try:
        # Verbinde DB
        scraper.connect_db()

        # Scrape HIGH-Priority Quellen
        # scraper.scrape_all(priority_filter='HIGH')

        # ODER: Teste nur eine Quelle
        scraper.scrape_source('deutsches_stiftungszentrum')

    except Exception as e:
        logger.error(f"❌ Scraping fehlgeschlagen: {e}")
    finally:
        scraper.close()


if __name__ == "__main__":
    main()
