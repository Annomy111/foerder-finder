#!/usr/bin/env python3
"""
Advanced Stiftungen Scraper mit LLM-Extraktion
- Scraped mit Firecrawl
- Extrahiert strukturierte Daten mit DeepSeek
- Speichert in STIFTUNGEN + FUNDING_OPPORTUNITIES
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import sqlite3
import requests
import logging
import json
import uuid
from datetime import datetime
from urllib.parse import urlparse
from dotenv import load_dotenv
import time

# Import new LLM extractor
from scraper_firecrawl.llm_extractor import (
    extract_with_deepseek,
    validate_extracted_data,
    calculate_quality_score
)

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

FIRECRAWL_URL = "http://130.61.137.77:3002"
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DB_PATH = "dev_database.db"

# Erweiterte Liste wichtiger Stiftungen
STIFTUNG_URLS = [
    # Bereits gescraped (Re-scrape mit LLM)
    "https://www.deutsches-stiftungszentrum.de",
    "https://www.stiftungen.org",
    "https://www.dkjs.de",
    "https://www.bosch-stiftung.de",
    "https://www.bertelsmann-stiftung.de",
    "https://www.joachim-herz-stiftung.de",
    "https://www.buergerstiftungen.org",

    # Neue Stiftungen
    "https://www.software-ag-stiftung.de",
    "https://www.stiftung-lesen.de",
    "https://www.vodafone-stiftung.de",
    "https://www.telekom-stiftung.de",
    "https://www.heraeus-bildungsstiftung.de",
    "https://www.stiftung-bildung.de",
    "https://www.claussen-simon-stiftung.de",
    "https://www.koerber-stiftung.de",
    "https://www.mercator-stiftung.de",
    "https://www.stifterverband.de",
    "https://www.schering-stiftung.de",
    "https://www.roland-berger-stiftung.de",
    "https://www.reemtsma-stiftung.de",
    "https://www.volkswagenstiftung.de",
    "https://www.freudenberg-stiftung.de",
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
    'stiftung-lesen.de': 'Stiftung Lesen',
    'vodafone-stiftung.de': 'Vodafone Stiftung',
    'telekom-stiftung.de': 'Deutsche Telekom Stiftung',
    'heraeus-bildungsstiftung.de': 'Heraeus Bildungsstiftung',
    'stiftung-bildung.de': 'Stiftung Bildung',
    'claussen-simon-stiftung.de': 'Claussen-Simon-Stiftung',
    'koerber-stiftung.de': 'Körber-Stiftung',
    'mercator-stiftung.de': 'Mercator-Stiftung',
    'stifterverband.de': 'Stifterverband',
    'schering-stiftung.de': 'Schering Stiftung',
    'roland-berger-stiftung.de': 'Roland Berger Stiftung',
    'reemtsma-stiftung.de': 'Reemtsma Begabtenförderungswerk',
    'volkswagenstiftung.de': 'VolkswagenStiftung',
    'freudenberg-stiftung.de': 'Freudenberg Stiftung',
}

LLM_PROMPT = """Analysiere diese Webseite über eine deutsche Stiftung und extrahiere strukturierte Informationen.

WICHTIG: Achte besonders auf Bildungs- und Grundschulbezug!

Gib die Daten als valides JSON zurück (NUR JSON, keine Markdown-Blöcke):
{
    "name": "Vollständiger Name der Stiftung",
    "website": "https://...",
    "beschreibung": "Kurzbeschreibung max 300 Zeichen",
    "foerderbereiche": ["Bildung", "MINT", "..."],
    "foerdersumme_min": 5000,
    "foerdersumme_max": 50000,
    "zielgruppen": ["Grundschule", "Kinder", "..."],
    "bewerbungsfrist": "31.12.2025 oder 'laufend' oder 'jährlich'",
    "kontakt_email": "email@stiftung.de",
    "kontakt_telefon": "+49 ...",
    "kontakt_ansprechpartner": "Dr. Name",
    "bundesland": "Baden-Württemberg oder 'Bundesweit'",
    "stadt": "Stuttgart",
    "plz": "70173",
    "anforderungen": ["Projektskizze", "Budget", "..."]
}

Falls keine Stiftung erkennbar oder keine relevanten Daten: {"error": "no_data"}
"""

def get_quelle_from_url(url):
    """Extrahiere Kurzbezeichnung aus URL"""
    domain = urlparse(url).netloc.replace('www.', '')
    return domain.split('.')[0].upper()

def get_title_from_url(url):
    """Extrahiere Titel aus URL"""
    domain = urlparse(url).netloc.replace('www.', '')
    return NAME_MAP.get(domain, domain.split('.')[0].title() + ' Stiftung')

def scrape_with_firecrawl(url):
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
            markdown = data.get('markdown', '')
            if len(markdown) < 100:
                logger.warning(f"   ⚠️ Zu wenig Content ({len(markdown)} chars)")
                return None
            return {
                'success': True,
                'url': url,
                'markdown': markdown,
                'title': data.get('title', get_title_from_url(url))
            }
        else:
            logger.error(f"   ❌ Firecrawl Error: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"   ❌ Exception: {e}")
        return None

def extract_with_llm(markdown, url):
    """Extrahiere Stiftungsdaten mit DeepSeek LLM"""
    logger.info(f"   🤖 LLM-Extraktion...")

    if not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY == 'your_key_here_optional':
        logger.error("   ❌ DeepSeek API-Key fehlt!")
        return None

    try:
        # Kürze Text wenn nötig (max 8000 chars für Token-Limit)
        text_sample = markdown[:8000] if len(markdown) > 8000 else markdown

        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": LLM_PROMPT},
                    {"role": "user", "content": text_sample}
                ],
                "temperature": 0.2,
                "max_tokens": 1500
            },
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            extracted_text = result['choices'][0]['message']['content']

            # Parse JSON
            try:
                # Remove markdown if present
                if "```json" in extracted_text:
                    start = extracted_text.find("```json") + 7
                    end = extracted_text.find("```", start)
                    extracted_text = extracted_text[start:end].strip()
                elif "```" in extracted_text:
                    start = extracted_text.find("```") + 3
                    end = extracted_text.find("```", start)
                    extracted_text = extracted_text[start:end].strip()

                data = json.loads(extracted_text)

                if "error" in data:
                    logger.warning(f"   ⚠️ LLM: {data['error']}")
                    return None

                logger.info(f"   ✅ LLM-Extraktion erfolgreich!")
                return data

            except json.JSONDecodeError as e:
                logger.error(f"   ❌ JSON-Parse-Fehler: {e}")
                logger.debug(f"   Raw: {extracted_text[:200]}")
                return None
        else:
            logger.error(f"   ❌ DeepSeek API Error: {response.status_code}")
            return None

    except Exception as e:
        logger.error(f"   ❌ LLM Exception: {e}")
        return None

def save_to_database(conn, stiftung_data, raw_markdown, source_url, structured_data=None):
    """
    Speichere Stiftung in DB (STIFTUNGEN + FUNDING_OPPORTUNITIES)

    Args:
        conn: DB connection
        stiftung_data: Extracted stiftung data (old format)
        raw_markdown: Raw markdown text
        source_url: Source URL
        structured_data: New structured data from llm_extractor (optional)

    Returns:
        tuple: (stiftung_id, funding_id) oder (None, None) bei Fehler
    """
    cursor = conn.cursor()

    # Check if already exists
    cursor.execute("SELECT stiftung_id FROM STIFTUNGEN WHERE quelle_url = ?", (source_url,))
    existing = cursor.fetchone()

    if existing:
        logger.info(f"   ⏭️ Stiftung bereits vorhanden, UPDATE strukturierte Daten")
        # Update FUNDING_OPPORTUNITIES with new structured data
        if structured_data:
            # Try multiple methods to find funding_id
            # Method 1: By stiftung_id (for new records)
            cursor.execute("SELECT funding_id FROM FUNDING_OPPORTUNITIES WHERE stiftung_id = ?", (existing[0],))
            funding_row = cursor.fetchone()

            # Method 2: By source_url (for old records without stiftung_id)
            if not funding_row:
                cursor.execute("SELECT funding_id FROM FUNDING_OPPORTUNITIES WHERE source_url = ?", (source_url,))
                funding_row = cursor.fetchone()

            # Method 3: By provider name match
            if not funding_row and stiftung_data.get('name'):
                stiftung_name = stiftung_data.get('name')
                cursor.execute("SELECT funding_id FROM FUNDING_OPPORTUNITIES WHERE provider = ? OR title LIKE ?",
                             (stiftung_name, f"%{stiftung_name}%"))
                funding_row = cursor.fetchone()

            if funding_row:
                funding_id = funding_row[0]
                update_structured_fields(cursor, funding_id, structured_data)
                # Also set stiftung_id if it was NULL
                cursor.execute("UPDATE FUNDING_OPPORTUNITIES SET stiftung_id = ? WHERE funding_id = ?",
                             (existing[0], funding_id))
                conn.commit()
                logger.info(f"   ✅ Strukturierte Daten aktualisiert (funding_id: {funding_id[:8]}...)")
            else:
                logger.warning(f"   ⚠️ Keine FUNDING_OPPORTUNITY gefunden für UPDATE")
        return existing[0], None

    # Generate IDs
    stiftung_id = str(uuid.uuid4()).replace('-', '').upper()
    funding_id = str(uuid.uuid4()).replace('-', '').upper()

    try:
        # Insert into STIFTUNGEN
        cursor.execute("""
            INSERT INTO STIFTUNGEN (
                stiftung_id, name, website, beschreibung,
                foerderbereiche, foerdersumme_min, foerdersumme_max,
                bewerbungsfrist, kontakt_email, kontakt_telefon,
                kontakt_ansprechpartner, bundesland, stadt, plz,
                zielgruppen, anforderungen, quelle, quelle_url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            stiftung_id,
            stiftung_data.get('name', 'Unbekannte Stiftung'),
            stiftung_data.get('website', source_url),
            stiftung_data.get('beschreibung', ''),
            json.dumps(stiftung_data.get('foerderbereiche', []), ensure_ascii=False),
            stiftung_data.get('foerdersumme_min'),
            stiftung_data.get('foerdersumme_max'),
            stiftung_data.get('bewerbungsfrist', ''),
            stiftung_data.get('kontakt_email', ''),
            stiftung_data.get('kontakt_telefon', ''),
            stiftung_data.get('kontakt_ansprechpartner', ''),
            stiftung_data.get('bundesland', 'Bundesweit'),
            stiftung_data.get('stadt', ''),
            stiftung_data.get('plz', ''),
            json.dumps(stiftung_data.get('zielgruppen', []), ensure_ascii=False),
            json.dumps(stiftung_data.get('anforderungen', []), ensure_ascii=False),
            get_quelle_from_url(source_url),
            source_url
        ))

        # Insert into FUNDING_OPPORTUNITIES (with structured data)
        title = stiftung_data.get('name', 'Unbekannte Stiftung')[:500]
        description = stiftung_data.get('beschreibung', '')[:1000]

        # Base insert
        cursor.execute("""
            INSERT INTO FUNDING_OPPORTUNITIES (
                funding_id, title, description, cleaned_text, region,
                funder_name, source_url, last_scraped, source_type, stiftung_id,
                provider
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            funding_id,
            title,
            description,
            raw_markdown,
            stiftung_data.get('bundesland', 'Bundesweit'),
            stiftung_data.get('name', ''),
            source_url,
            datetime.now(),
            'stiftung',
            stiftung_id,
            stiftung_data.get('name', '')
        ))

        # Update with structured data if available
        if structured_data:
            update_structured_fields(cursor, funding_id, structured_data)

        conn.commit()
        logger.info(f"   ✅ Gespeichert: {stiftung_data.get('name')}")
        return stiftung_id, funding_id

    except Exception as e:
        logger.error(f"   ❌ DB-Fehler: {e}")
        conn.rollback()
        return None, None


def update_structured_fields(cursor, funding_id, structured_data):
    """
    Update FUNDING_OPPORTUNITIES with structured data from llm_extractor

    Args:
        cursor: DB cursor
        funding_id: Funding opportunity ID
        structured_data: Validated structured data dict
    """

    # Convert lists to JSON strings
    eligibility_json = json.dumps(structured_data.get('eligibility_criteria', []), ensure_ascii=False) \
        if structured_data.get('eligibility_criteria') else None

    evaluation_json = json.dumps(structured_data.get('evaluation_criteria', []), ensure_ascii=False) \
        if structured_data.get('evaluation_criteria') else None

    requirements_json = json.dumps(structured_data.get('requirements', []), ensure_ascii=False) \
        if structured_data.get('requirements') else None

    eligible_costs_json = json.dumps(structured_data.get('eligible_costs', []), ensure_ascii=False) \
        if structured_data.get('eligible_costs') else None

    target_groups_json = json.dumps(structured_data.get('target_groups', []), ensure_ascii=False) \
        if structured_data.get('target_groups') else None

    # Update query
    cursor.execute("""
        UPDATE FUNDING_OPPORTUNITIES
        SET
            application_deadline = ?,
            funding_amount_min = ?,
            funding_amount_max = ?,
            eligibility = ?,
            target_groups = ?,
            evaluation_criteria = ?,
            requirements = ?,
            application_process = ?,
            application_url = ?,
            contact_email = ?,
            contact_phone = ?,
            contact_person = ?,
            decision_timeline = ?,
            funding_period = ?,
            co_financing_required = ?,
            co_financing_rate = ?,
            eligible_costs = ?,
            extraction_quality_score = ?,
            last_extracted = ?
        WHERE funding_id = ?
    """, (
        structured_data.get('deadline'),
        structured_data.get('min_funding_amount'),
        structured_data.get('max_funding_amount'),
        eligibility_json,
        target_groups_json,
        evaluation_json,
        requirements_json,
        structured_data.get('application_process'),
        structured_data.get('application_url'),
        structured_data.get('contact_email'),
        structured_data.get('contact_phone'),
        structured_data.get('contact_person'),
        structured_data.get('decision_timeline'),
        structured_data.get('funding_period'),
        1 if structured_data.get('co_financing_required') else 0,
        structured_data.get('co_financing_rate'),
        eligible_costs_json,
        structured_data.get('extraction_quality_score', 0.0),
        datetime.now(),
        funding_id
    ))

def main():
    """Main Scraper"""
    logger.info("="*70)
    logger.info("🚀 ADVANCED STIFTUNGEN SCRAPER (mit LLM)")
    logger.info("="*70)
    logger.info(f"📋 {len(STIFTUNG_URLS)} URLs zu scrapen\n")

    if not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY == 'your_key_here_optional':
        logger.error("❌ DEEPSEEK_API_KEY nicht gesetzt in .env!")
        return

    conn = sqlite3.connect(DB_PATH)

    success_count = 0
    llm_success = 0
    fail_count = 0

    for i, url in enumerate(STIFTUNG_URLS, 1):
        logger.info(f"\n[{i}/{len(STIFTUNG_URLS)}] {url}")

        # Scrape
        page_data = scrape_with_firecrawl(url)
        if not page_data:
            fail_count += 1
            continue

        # LLM-Extraktion für Stiftungsdaten (alte Methode)
        stiftung_data = extract_with_llm(page_data['markdown'], url)
        if not stiftung_data:
            logger.warning(f"   ⚠️ Fallback: Speichere nur Roh-Daten")
            # Speichere wenigstens Roh-Daten in FUNDING_OPPORTUNITIES
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO FUNDING_OPPORTUNITIES (
                    funding_id, title, description, cleaned_text, region,
                    funder_name, source_url, last_scraped, source_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(uuid.uuid4()).replace('-', '').upper(),
                page_data['title'][:500],
                page_data['markdown'][:1000],
                page_data['markdown'],
                'Bundesweit',
                page_data['title'],
                url,
                datetime.now(),
                'stiftung'
            ))
            conn.commit()
            success_count += 1
            continue

        # NEW: Advanced LLM-Extraktion für strukturierte Daten (llm_extractor.py)
        logger.info(f"   🎯 Extrahiere strukturierte Daten...")
        structured_data = extract_with_deepseek(page_data['markdown'], stiftung_data.get('name', url))

        if structured_data:
            # Validate and calculate quality score
            structured_data = validate_extracted_data(structured_data)
            quality_score = calculate_quality_score(structured_data)
            structured_data['extraction_quality_score'] = quality_score
            logger.info(f"   📊 Quality Score: {quality_score}")
        else:
            logger.warning(f"   ⚠️ Strukturierte Extraktion fehlgeschlagen, nutze Fallback")
            structured_data = None

        # Save to DB (with structured data)
        stiftung_id, funding_id = save_to_database(
            conn, stiftung_data, page_data['markdown'], url,
            structured_data=structured_data
        )

        if stiftung_id:
            success_count += 1
            llm_success += 1
        else:
            fail_count += 1

        # Rate limit (max 60 requests/min bei DeepSeek)
        time.sleep(1.5)

    # Calculate average quality score
    conn2 = sqlite3.connect(DB_PATH)
    cursor2 = conn2.cursor()
    cursor2.execute("""
        SELECT AVG(extraction_quality_score)
        FROM FUNDING_OPPORTUNITIES
        WHERE extraction_quality_score IS NOT NULL
        AND source_type = 'stiftung'
    """)
    avg_quality = cursor2.fetchone()[0] or 0.0

    cursor2.execute("""
        SELECT COUNT(*)
        FROM FUNDING_OPPORTUNITIES
        WHERE extraction_quality_score >= 0.7
        AND source_type = 'stiftung'
    """)
    high_quality_count = cursor2.fetchone()[0]

    conn2.close()
    conn.close()

    # Summary
    logger.info("\n" + "="*70)
    logger.info("📊 ZUSAMMENFASSUNG")
    logger.info("="*70)
    logger.info(f"✅ Erfolgreich gespeichert: {success_count}/{len(STIFTUNG_URLS)}")
    logger.info(f"🤖 Mit LLM-Extraktion: {llm_success}/{success_count}")
    logger.info(f"❌ Fehlgeschlagen: {fail_count}")
    logger.info(f"\n📈 Datenqualität:")
    logger.info(f"   Durchschnittlicher Quality Score: {avg_quality:.2f}")
    logger.info(f"   High-Quality (>=0.7): {high_quality_count}")
    logger.info("\nNächster Schritt: RAG-Index neu bauen!")
    logger.info("  → python3 rag_indexer/build_index_advanced.py")

if __name__ == "__main__":
    main()
