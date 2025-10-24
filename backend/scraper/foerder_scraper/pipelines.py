"""
Scrapy Pipelines für Datenverarbeitung
"""

import json
import re
from datetime import datetime
from typing import Optional

import cx_Oracle
from bs4 import BeautifulSoup
from dateutil import parser
from itemadapter import ItemAdapter

# Import der DB-Utilities (aus parent directory)
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
from utils.database import get_db_manager


class CleaningPipeline:
    """Pipeline für Text-Bereinigung und Normalisierung"""

    # Keywords für Funding-Area-Tagging
    AREA_KEYWORDS = {
        'Digitalisierung': ['digital', 'tablet', 'computer', 'software', 'internet', 'wlan'],
        'Sport': ['sport', 'bewegung', 'turnhalle', 'sportplatz', 'schwimmen'],
        'MINT': ['mint', 'mathematik', 'informatik', 'naturwissenschaft', 'technik'],
        'Inklusion': ['inklusion', 'behinderung', 'barrierefrei', 'förderung'],
        'Kunst': ['kunst', 'musik', 'theater', 'kultur', 'kreativ'],
        'Infrastruktur': ['sanierung', 'gebäude', 'renovierung', 'neubau', 'ausstattung']
    }

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # 1. HTML-Tags aus cleaned_text entfernen
        if adapter.get('cleaned_text'):
            cleaned = self._clean_html(adapter['cleaned_text'])
            adapter['cleaned_text'] = cleaned

        # 2. Deadline normalisieren
        if adapter.get('deadline'):
            normalized_date = self._normalize_date(adapter['deadline'])
            adapter['deadline'] = normalized_date

        # 3. Funding Area taggen
        if not adapter.get('funding_area') and adapter.get('cleaned_text'):
            area = self._detect_funding_area(adapter['cleaned_text'])
            if area:
                adapter['funding_area'] = area

        # 4. Tags erstellen (JSON-Array)
        if adapter.get('tags') and isinstance(adapter['tags'], list):
            adapter['tags'] = json.dumps(adapter['tags'], ensure_ascii=False)

        # 5. Metadata als JSON bündeln (falls vorhanden)
        metadata = {}
        if adapter.get('metadata_json'):
            if isinstance(adapter['metadata_json'], str):
                try:
                    metadata = json.loads(adapter['metadata_json'])
                except json.JSONDecodeError:
                    pass
            elif isinstance(adapter['metadata_json'], dict):
                metadata = adapter['metadata_json']

        adapter['metadata_json'] = json.dumps(metadata, ensure_ascii=False)

        # 6. Scraped_at setzen
        adapter['scraped_at'] = datetime.now()

        return item

    def _clean_html(self, text: str) -> str:
        """Entfernt HTML-Tags und bereinigt Text"""
        # Parse HTML
        soup = BeautifulSoup(text, 'lxml')

        # Entferne Scripts und Styles
        for script in soup(['script', 'style']):
            script.decompose()

        # Extrahiere Text
        cleaned = soup.get_text(separator=' ', strip=True)

        # Mehrfache Leerzeichen reduzieren
        cleaned = re.sub(r'\s+', ' ', cleaned)

        # Sonderzeichen normalisieren
        cleaned = cleaned.replace('\xa0', ' ')
        cleaned = cleaned.replace('\u200b', '')

        return cleaned.strip()

    def _normalize_date(self, date_str: str) -> Optional[datetime]:
        """Normalisiert Datumsstring zu datetime"""
        if not date_str:
            return None

        try:
            # Versuche automatisches Parsing
            parsed = parser.parse(date_str, dayfirst=True, fuzzy=True)
            return parsed
        except (ValueError, TypeError):
            # Fallback: Regex für deutsche Datumsformate
            patterns = [
                r'(\d{1,2})\.(\d{1,2})\.(\d{4})',  # 31.12.2024
                r'(\d{4})-(\d{2})-(\d{2})',         # 2024-12-31
            ]
            for pattern in patterns:
                match = re.search(pattern, date_str)
                if match:
                    try:
                        if '.' in pattern:
                            day, month, year = match.groups()
                            return datetime(int(year), int(month), int(day))
                        else:
                            year, month, day = match.groups()
                            return datetime(int(year), int(month), int(day))
                    except ValueError:
                        continue

        return None

    def _detect_funding_area(self, text: str) -> Optional[str]:
        """Erkennt Förderbereich anhand von Keywords"""
        text_lower = text.lower()

        # Zähle Keyword-Treffer pro Area
        scores = {}
        for area, keywords in self.AREA_KEYWORDS.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            if count > 0:
                scores[area] = count

        # Gebe Area mit den meisten Treffern zurück
        if scores:
            return max(scores, key=scores.get)

        return None


class OracleWriterPipeline:
    """Pipeline für Schreiben in Oracle Autonomous Database"""

    def __init__(self):
        self.db_manager = None
        self.connection = None
        self.cursor = None

    def open_spider(self, spider):
        """Initialisiert DB-Verbindung beim Spider-Start"""
        try:
            self.db_manager = get_db_manager()
            self.connection = self.db_manager.get_connection()
            self.cursor = self.connection.cursor()
            spider.logger.info('Oracle DB Verbindung erfolgreich')
        except Exception as e:
            spider.logger.error(f'Fehler beim Verbinden mit Oracle DB: {e}')
            raise

    def close_spider(self, spider):
        """Schließt DB-Verbindung beim Spider-Ende"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        spider.logger.info('Oracle DB Verbindung geschlossen')

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # MERGE (UPSERT) Statement
        merge_sql = """
        MERGE INTO FUNDING_OPPORTUNITIES f
        USING (SELECT :source_url AS url FROM dual) d
        ON (f.source_url = d.url)
        WHEN MATCHED THEN
            UPDATE SET
                title = :title,
                cleaned_text = :cleaned_text,
                deadline = :deadline,
                provider = :provider,
                region = :region,
                funding_area = :funding_area,
                tags = :tags,
                min_funding_amount = :min_funding_amount,
                max_funding_amount = :max_funding_amount,
                metadata_json = :metadata_json,
                updated_at = SYSTIMESTAMP
        WHEN NOT MATCHED THEN
            INSERT (
                funding_id, title, source_url, cleaned_text, deadline,
                provider, region, funding_area, tags,
                min_funding_amount, max_funding_amount,
                metadata_json, scraped_at
            )
            VALUES (
                SYS_GUID(), :title, :source_url, :cleaned_text, :deadline,
                :provider, :region, :funding_area, :tags,
                :min_funding_amount, :max_funding_amount,
                :metadata_json, SYSTIMESTAMP
            )
        """

        # Prepare parameters
        params = {
            'source_url': adapter.get('source_url'),
            'title': adapter.get('title'),
            'cleaned_text': adapter.get('cleaned_text'),
            'deadline': adapter.get('deadline'),
            'provider': adapter.get('provider'),
            'region': adapter.get('region'),
            'funding_area': adapter.get('funding_area'),
            'tags': adapter.get('tags'),
            'min_funding_amount': adapter.get('min_funding_amount'),
            'max_funding_amount': adapter.get('max_funding_amount'),
            'metadata_json': adapter.get('metadata_json')
        }

        try:
            self.cursor.execute(merge_sql, params)
            self.connection.commit()
            spider.logger.info(f'Gespeichert: {adapter.get("title")}')
        except cx_Oracle.Error as e:
            spider.logger.error(f'DB-Fehler: {e}')
            self.connection.rollback()

        return item


class DuplicatesPipeline:
    """Pipeline zum Filtern von Duplikaten (basierend auf source_url)"""

    def __init__(self):
        self.seen_urls = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        url = adapter.get('source_url')

        if url in self.seen_urls:
            spider.logger.info(f'Duplikat gefunden: {url}')
            from scrapy.exceptions import DropItem
            raise DropItem(f'Duplikat: {url}')

        self.seen_urls.add(url)
        return item
