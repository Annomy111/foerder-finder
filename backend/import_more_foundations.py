#!/usr/bin/env python3
"""
Import weitere Top-Stiftungen mit SUPER SCRAPER + Database Save
"""

import sys
import os
import sqlite3
import json
import uuid
from datetime import datetime
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scraper_firecrawl'))

from super_scraper import super_scrape

DB_PATH = "dev_database.db"

# Weitere Top-Stiftungen
FOUNDATIONS = [
    {
        "name": "Volkswagen Stiftung",
        "url": "https://www.volkswagenstiftung.de",
        "min_quality": 0.25
    },
    {
        "name": "Mercator Stiftung",
        "url": "https://www.stiftung-mercator.de",
        "min_quality": 0.25
    },
    {
        "name": "Gemeinnützige Hertie-Stiftung",
        "url": "https://www.ghst.de",
        "min_quality": 0.25
    },
    {
        "name": "Klaus Tschira Stiftung",
        "url": "https://www.klaus-tschira-stiftung.de",
        "min_quality": 0.25
    },
    {
        "name": "Freudenberg Stiftung",
        "url": "https://www.freudenbergstiftung.de",
        "min_quality": 0.25
    },
    {
        "name": "Karl Schlecht Stiftung",
        "url": "https://www.karlschlechtstiftung.de",
        "min_quality": 0.25
    }
]


def save_to_database(programs, provider):
    """
    Speichert Programme in die SQLite-Datenbank

    Args:
        programs: Liste von Programmen vom SUPER SCRAPER
        provider: Name des Anbieters

    Returns:
        Anzahl gespeicherter Programme
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
                print(f"         ⏭️ Überspringe (bereits vorhanden): {title[:40]}")
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
                datetime.now().isoformat()
            ))

            saved_count += 1
            print(f"         ✅ Gespeichert: {title[:50]}... (Score: {quality_score:.2f})")

        except Exception as e:
            print(f"         ❌ Fehler bei Programm: {e}")
            continue

    conn.commit()
    conn.close()

    return saved_count


def main():
    print("=" * 80)
    print("IMPORT WEITERE STIFTUNGEN (MIT DATABASE SAVE)")
    print("=" * 80)
    print()
    print(f"Anzahl Stiftungen: {len(FOUNDATIONS)}")
    print()

    total_programs_found = 0
    total_programs_saved = 0
    foundation_results = []

    for i, foundation in enumerate(FOUNDATIONS, 1):
        print("=" * 80)
        print(f"[{i}/{len(FOUNDATIONS)}] {foundation['name']}")
        print("=" * 80)
        print(f"   URL: {foundation['url']}")
        print(f"   Min Quality: {foundation['min_quality']}")
        print()

        try:
            # SUPER SCRAPER
            print("   🚀 SUPER SCRAPER läuft...")
            programs = super_scrape(
                base_url=foundation['url'],
                source_name=foundation['name'],
                max_urls=20,
                min_quality=foundation['min_quality'],
                delay=3.0
            )

            programs_found = len(programs)
            total_programs_found += programs_found

            if programs_found == 0:
                print()
                print(f"   ⚠️ Keine Programme gefunden (Quality Score < {foundation['min_quality']})")
                foundation_results.append({
                    'name': foundation['name'],
                    'found': 0,
                    'saved': 0
                })
                print()
                # Keine Pause nach 0 Ergebnissen
                continue

            print()
            print(f"   ✅ {programs_found} Programm(e) gefunden")
            print()

            # Datenbank-Import
            print("   💾 Speichere in Datenbank...")
            saved_count = save_to_database(programs, foundation['name'])
            total_programs_saved += saved_count

            foundation_results.append({
                'name': foundation['name'],
                'found': programs_found,
                'saved': saved_count
            })

            avg_quality = sum(p['quality_score'] for p in programs) / len(programs)
            print()
            print(f"   📊 Durchschnittliche Quality Score: {avg_quality:.2f}")
            print(f"   💾 Gespeichert: {saved_count}/{programs_found} Programme")
            print()

        except Exception as e:
            print(f"   ❌ FEHLER beim Scraping: {e}")
            import traceback
            traceback.print_exc()
            foundation_results.append({
                'name': foundation['name'],
                'found': 0,
                'saved': 0,
                'error': str(e)
            })

        # Pause zwischen Stiftungen (nur wenn nicht letzte Foundation)
        if i < len(FOUNDATIONS):
            print("   ⏸️ Pause 10 Sekunden...")
            time.sleep(10)

    # Zusammenfassung
    print()
    print("=" * 80)
    print("IMPORT ABGESCHLOSSEN")
    print("=" * 80)
    print()
    print(f"Stiftungen gescrapt: {len(FOUNDATIONS)}")
    print(f"Programme gefunden: {total_programs_found}")
    print(f"Programme gespeichert: {total_programs_saved}")
    print()

    print("Ergebnisse pro Stiftung:")
    print()
    for result in foundation_results:
        if 'error' in result:
            print(f"   ❌ {result['name']}: FEHLER - {result['error']}")
        elif result['found'] == 0:
            print(f"   ⚠️ {result['name']}: Keine Programme gefunden")
        else:
            print(f"   ✅ {result['name']}: {result['saved']}/{result['found']} Programme gespeichert")

    print()

    if total_programs_saved > 0:
        print("🎉 ERFOLG!")
        print()
        print("Nächste Schritte:")
        print("1. ChromaDB neu indexieren: python rag_indexer/build_index_advanced.py")
        print("2. Auto-Deploy ausführen: ./auto_deploy_after_scraping.sh")
        return 0
    else:
        print("⚠️ Keine neuen Programme importiert")
        return 1


if __name__ == '__main__':
    exit(main())
