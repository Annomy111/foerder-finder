#!/usr/bin/env python3
"""
Ministerien & Öffentliche Förderdatenbanken Scraper

Scraped Bundes- und Landesministerien für Bildungsförderung
Erwartung: Höhere Quality Scores als Stiftungen (strukturiertere Daten)

Author: Claude Code
Version: 1.0
Date: 2025-10-29
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
import time
from dotenv import load_dotenv

# Import URLs
from scraper_firecrawl.ministerien_urls import get_all_urls, get_urls_by_priority

# Import LLM Extractor
from scraper_firecrawl.llm_extractor import (
    extract_with_deepseek,
    validate_extracted_data,
    calculate_quality_score
)

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

FIRECRAWL_URL = "http://130.61.137.77:3002"
DB_PATH = "dev_database.db"


def scrape_with_firecrawl(url):
    """
    Scraped URL mit Firecrawl

    Returns:
        Dict with 'markdown' or None on error
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
                return {'markdown': data['data']['markdown']}

        logger.error(f"   ❌ Firecrawl Error: {response.status_code}")
        return None

    except Exception as e:
        logger.error(f"   ❌ Exception: {e}")
        return None


def save_to_database(conn, ministerium_data, raw_markdown, source_url, structured_data=None):
    """
    Speichert Ministerium in FUNDING_OPPORTUNITIES

    Args:
        conn: DB connection
        ministerium_data: Metadata (name, type, bundesland)
        raw_markdown: Raw scraped markdown
        source_url: Source URL
        structured_data: Extracted structured data from LLM

    Returns:
        funding_id or None on error
    """

    cursor = conn.cursor()

    # Check if already exists
    cursor.execute("SELECT funding_id FROM FUNDING_OPPORTUNITIES WHERE source_url = ?", (source_url,))
    existing = cursor.fetchone()

    if existing:
        logger.info(f"   ⏭️ Bereits vorhanden, UPDATE strukturierte Daten")
        if structured_data:
            funding_id = existing[0]
            update_structured_fields(cursor, funding_id, structured_data)
            conn.commit()
            logger.info(f"   ✅ Strukturierte Daten aktualisiert")
        return existing[0]

    # Generate ID
    funding_id = str(uuid.uuid4()).replace('-', '').upper()

    try:
        # Insert base record
        title = ministerium_data.get('name', 'Unbekanntes Ministerium')[:500]
        description = ministerium_data.get('notes', '')[:1000]

        cursor.execute("""
            INSERT INTO FUNDING_OPPORTUNITIES (
                funding_id, title, description, cleaned_text, region,
                funder_name, source_url, last_scraped, source_type, provider
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            funding_id,
            title,
            description,
            raw_markdown,
            ministerium_data.get('bundesland', 'Bundesweit'),
            ministerium_data.get('name', ''),
            source_url,
            datetime.now(),
            'ministerium',  # source_type
            ministerium_data.get('name', '')
        ))

        # Update with structured data
        if structured_data:
            update_structured_fields(cursor, funding_id, structured_data)

        conn.commit()
        logger.info(f"   ✅ Gespeichert: {ministerium_data.get('name')}")
        return funding_id

    except Exception as e:
        logger.error(f"   ❌ DB-Fehler: {e}")
        conn.rollback()
        return None


def update_structured_fields(cursor, funding_id, structured_data):
    """
    Updates structured fields in FUNDING_OPPORTUNITIES
    """

    # Convert lists to JSON
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
    logger.info("🏛️ MINISTERIEN-SCRAPER (mit LLM-Extraktion)")
    logger.info("="*70)

    # Get URLs (start with HIGH priority)
    urls = get_urls_by_priority('high')
    logger.info(f"📋 {len(urls)} High-Priority URLs zu scrapen\n")

    # Connect to DB
    conn = sqlite3.connect(DB_PATH)

    success_count = 0
    error_count = 0
    llm_success_count = 0

    for i, url_data in enumerate(urls, 1):
        logger.info(f"[{i}/{len(urls)}] {url_data['name']}")
        logger.info(f"📄 Scrape: {url_data['url']}")

        # 1. Scrape with Firecrawl
        page_data = scrape_with_firecrawl(url_data['url'])

        if not page_data:
            error_count += 1
            logger.info("")
            continue

        # 2. LLM-Extraktion für strukturierte Daten
        logger.info(f"   🎯 Extrahiere strukturierte Daten...")
        structured_data = extract_with_deepseek(
            page_data['markdown'],
            url_data['name']
        )

        if structured_data:
            structured_data = validate_extracted_data(structured_data)
            quality_score = calculate_quality_score(structured_data)
            structured_data['extraction_quality_score'] = quality_score
            logger.info(f"   📊 Quality Score: {quality_score}")
            llm_success_count += 1
        else:
            logger.warning(f"   ⚠️ LLM-Extraktion fehlgeschlagen")
            structured_data = None

        # 3. Save to DB
        funding_id = save_to_database(
            conn,
            url_data,
            page_data['markdown'],
            url_data['url'],
            structured_data=structured_data
        )

        if funding_id:
            success_count += 1

        logger.info("")

        # Rate limiting
        time.sleep(2)

    # Close DB
    conn.close()

    # Summary
    logger.info("="*70)
    logger.info("📊 ZUSAMMENFASSUNG")
    logger.info("="*70)
    logger.info(f"✅ Erfolgreich gespeichert: {success_count}/{len(urls)}")
    logger.info(f"🤖 Mit LLM-Extraktion: {llm_success_count}/{success_count}")
    logger.info(f"❌ Fehlgeschlagen: {error_count}")
    logger.info("")

    # Quality stats
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            COUNT(*) as total,
            ROUND(AVG(extraction_quality_score), 2) as avg_quality,
            COUNT(CASE WHEN extraction_quality_score >= 0.7 THEN 1 END) as high_quality
        FROM FUNDING_OPPORTUNITIES
        WHERE source_type = 'ministerium'
        AND extraction_quality_score IS NOT NULL
    """)

    row = cursor.fetchone()
    if row and row[0] > 0:
        logger.info("📈 Datenqualität:")
        logger.info(f"   Durchschnittlicher Quality Score: {row[1]}")
        logger.info(f"   High-Quality (>=0.7): {row[2]}")

    conn.close()

    logger.info("")
    logger.info("Nächster Schritt: Testing mit AI-Draft-Generierung!")
    logger.info("  → Teste: python3 test_ministerien_extraction.py")
    logger.info("")


if __name__ == '__main__':
    main()
