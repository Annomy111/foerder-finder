#!/usr/bin/env python3
"""
Import Roland Berger Programme in die Datenbank

Nutzt den SUPER SCRAPER um 8 Roland Berger Programme zu finden
und in dev_database.db zu speichern.
"""

import sys
import os
import sqlite3
import json
import uuid
from datetime import datetime

# Füge scraper_firecrawl zum Python Path hinzu
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scraper_firecrawl'))

from super_scraper import super_scrape

DB_PATH = "dev_database.db"

def save_to_database(programs, provider="Roland Berger Stiftung"):
    """
    Speichert Programme in die SQLite-Datenbank

    Args:
        programs: Liste von Programmen vom SUPER SCRAPER
        provider: Name des Anbieters
    """

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    saved_count = 0

    for prog in programs:
        try:
            data = prog['extracted_data']

            # Generiere UUID
            funding_id = uuid.uuid4().hex.upper()

            # Prepare data
            title = data.get('title', 'Unbekanntes Programm')
            description = data.get('description', '')
            deadline = data.get('deadline')
            min_amount = data.get('min_funding_amount')
            max_amount = data.get('max_funding_amount')
            source_url = prog['url']
            application_url = data.get('application_url') or source_url

            # JSON Arrays
            eligibility = json.dumps(data.get('eligibility_criteria', []), ensure_ascii=False)
            target_groups = json.dumps(data.get('target_groups', []), ensure_ascii=False)
            eval_criteria = json.dumps(data.get('evaluation_criteria', []), ensure_ascii=False)
            requirements = json.dumps(data.get('requirements', []), ensure_ascii=False)
            eligible_costs = json.dumps(data.get('eligible_costs', []), ensure_ascii=False)

            # Text fields
            app_process = data.get('application_process', '')
            funding_period = data.get('funding_period', '')
            contact_person = data.get('contact_person', '')
            decision_timeline = data.get('decision_timeline', '')

            # Quality Score
            quality_score = prog['quality_score']

            # Cleaned Text (Markdown)
            cleaned_text = prog.get('markdown', '')[:50000]  # Max 50k chars

            # Check if already exists
            cursor.execute("SELECT funding_id FROM FUNDING_OPPORTUNITIES WHERE source_url = ?", (source_url,))
            existing = cursor.fetchone()

            if existing:
                print(f"   ⏭️ Überspringe (bereits vorhanden): {title[:50]}")
                continue

            # Insert
            cursor.execute("""
                INSERT INTO FUNDING_OPPORTUNITIES (
                    funding_id, title, provider, description,
                    application_deadline, min_funding_amount, max_funding_amount,
                    source_url, application_url,
                    eligibility, target_groups, evaluation_criteria, requirements,
                    application_process, funding_period, eligible_costs,
                    contact_person, decision_timeline,
                    extraction_quality_score, cleaned_text,
                    created_at
                ) VALUES (
                    ?, ?, ?, ?,
                    ?, ?, ?,
                    ?, ?,
                    ?, ?, ?, ?,
                    ?, ?, ?,
                    ?, ?,
                    ?, ?,
                    ?
                )
            """, (
                funding_id, title, provider, description,
                deadline, min_amount, max_amount,
                source_url, application_url,
                eligibility, target_groups, eval_criteria, requirements,
                app_process, funding_period, eligible_costs,
                contact_person, decision_timeline,
                quality_score, cleaned_text,
                datetime.utcnow().isoformat()
            ))

            saved_count += 1
            print(f"   ✅ Gespeichert: {title[:60]}... (Score: {quality_score:.2f})")

        except Exception as e:
            print(f"   ❌ Fehler bei Programm: {e}")
            import traceback
            traceback.print_exc()
            continue

    conn.commit()
    conn.close()

    return saved_count


def main():
    print("=" * 80)
    print("ROLAND BERGER STIFTUNG - DATENIMPORT")
    print("=" * 80)
    print()
    print("Nutzt SUPER SCRAPER um Programme zu finden und zu importieren")
    print()

    # STEP 1: SUPER SCRAPER laufen lassen
    print("📊 STEP 1: SUPER SCRAPER starten...")
    print("   URL: https://www.rolandbergerstiftung.org")
    print("   Min Quality: 0.3")
    print()

    programs = super_scrape(
        base_url="https://www.rolandbergerstiftung.org",
        source_name="Roland Berger Stiftung",
        max_urls=20,
        min_quality=0.3,
        delay=3.0
    )

    if not programs:
        print()
        print("❌ FEHLER: Keine Programme gefunden!")
        print("   Möglicherweise ist Quality Score zu hoch gesetzt")
        return 1

    print()
    print(f"✅ SUPER SCRAPER fertig: {len(programs)} Programme gefunden")
    print()

    # STEP 2: In Datenbank speichern
    print("=" * 80)
    print("STEP 2: DATENBANK-IMPORT")
    print("=" * 80)
    print()

    saved_count = save_to_database(programs, provider="Roland Berger Stiftung")

    # STEP 3: Zusammenfassung
    print()
    print("=" * 80)
    print("IMPORT ABGESCHLOSSEN")
    print("=" * 80)
    print(f"Programme gefunden: {len(programs)}")
    print(f"Programme gespeichert: {saved_count}")
    print(f"Programme übersprungen: {len(programs) - saved_count} (bereits vorhanden)")
    print()

    if saved_count > 0:
        # Quality Stats
        avg_quality = sum(p['quality_score'] for p in programs) / len(programs)
        print(f"📊 Durchschnittliche Quality Score: {avg_quality:.2f}")
        print()

        print("🎉 ERFOLG!")
        print()
        print("Nächste Schritte:")
        print("1. ChromaDB neu indexieren: python rag_indexer/build_index_advanced.py")
        print("2. Production deployment")
        print("3. Testing")
        return 0
    else:
        print("⚠️ Keine neuen Programme importiert (alle bereits vorhanden)")
        return 0


if __name__ == '__main__':
    exit(main())
