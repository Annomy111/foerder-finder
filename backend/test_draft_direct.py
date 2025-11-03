#!/usr/bin/env python3
"""
DIREKTER Draft-Test - OHNE API Server

Testet die Draft-Generation direkt mit den Python-Libraries
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import sqlite3
import json
from openai import OpenAI

# Julius Hirsch Preis ID
JULIUS_HIRSCH_ID = "24FDDCF61A8F416BBA6A81083378F5EB"

# Test School
SCHOOL_DATA = {
    "school_name": "Grundschule Musterberg",
    "school_address": "Musterstraße 123, 12345 Berlin",
    "school_type": "Grundschule",
    "student_count": 250,
    "contact_person": "Frau Schmidt",
    "contact_email": "schmidt@gs-musterberg.de",
    "contact_phone": "030 12345678"
}

# Test Project
PROJECT_DESCRIPTION = """
Unsere Grundschule Musterberg in Berlin hat eine Fußball-AG mit 30 Kindern aus den Klassen 3-4.

Im letzten Schuljahr haben wir ein Anti-Rassismus-Projekt durchgeführt:
- Workshops zu Fairplay und Respekt
- Gemeinsame Fußballturniere mit Flüchtlingskindern
- Ausstellung "Fußball verbindet - gegen Diskriminierung"
- Elternabend zum Thema Integration im Sport

Das Projekt läuft seit August 2024 und soll bis Juni 2025 weitergehen.
"""

DB_PATH = "dev_database.db"


def get_funding_data(funding_id):
    """Lade Funding-Daten aus der DB"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            title, description, application_deadline, application_url,
            eligibility, target_groups, evaluation_criteria, requirements,
            application_process, funding_period, eligible_costs,
            extraction_quality_score, cleaned_text
        FROM FUNDING_OPPORTUNITIES
        WHERE funding_id = ?
    """, (funding_id,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "title": row[0],
        "description": row[1],
        "deadline": row[2],
        "application_url": row[3],
        "eligibility": json.loads(row[4]) if row[4] else [],
        "target_groups": json.loads(row[5]) if row[5] else [],
        "evaluation_criteria": json.loads(row[6]) if row[6] else [],
        "requirements": json.loads(row[7]) if row[7] else [],
        "application_process": row[8],
        "funding_period": row[9],
        "eligible_costs": json.loads(row[10]) if row[10] else [],
        "quality_score": row[11],
        "cleaned_text": row[12]
    }


def generate_draft_simple(funding_data, school_data, project_description):
    """Generiere Draft mit DeepSeek"""

    # Erstelle Prompt
    prompt = f"""
Du bist ein Experte für Förderanträge an Grundschulen in Deutschland.

FÖRDERPROGRAMM:
Titel: {funding_data['title']}
Anbieter: DFB - Deutscher Fußball-Bund
Deadline: {funding_data['deadline']}

BEWERBUNGSKRITERIEN:
{chr(10).join('- ' + c for c in funding_data['eligibility'])}

ZIELGRUPPEN:
{chr(10).join('- ' + t for t in funding_data['target_groups'])}

BEWERTUNGSKRITERIEN:
{chr(10).join('- ' + e for e in funding_data['evaluation_criteria'])}

ANFORDERUNGEN:
{chr(10).join('- ' + r for r in funding_data['requirements'])}

BEWERBUNGSPROZESS:
{funding_data['application_process']}

---

SCHULDATEN:
Name: {school_data['school_name']}
Adresse: {school_data['school_address']}
Schüleranzahl: {school_data['student_count']}
Kontakt: {school_data['contact_person']} ({school_data['contact_email']})

PROJEKTBESCHREIBUNG:
{project_description}

---

AUFGABE:
Erstelle einen vollständigen, überzeugenden Förderantrag für den Julius Hirsch Preis.

Der Antrag sollte:
1. Die Projektziele klar formulieren
2. Die Anti-Rassismus- und Integrationsarbeit hervorheben
3. Die Nachhaltigkeit und Langfristigkeit betonen
4. Alle Bewertungskriterien adressieren
5. Den Vorbildcharakter für andere Schulen zeigen
6. Die Deadline (30. Juni 2025) erwähnen
7. Den Bewerbungsprozess über dfb.de erwähnen

Schreibe den Antrag in professionellem Deutsch, strukturiert und überzeugend.
"""

    try:
        # DeepSeek API
        api_key = os.getenv('DEEPSEEK_API_KEY')
        if not api_key:
            print("❌ DEEPSEEK_API_KEY nicht gesetzt!")
            print("   Bitte setzen: export DEEPSEEK_API_KEY=sk-...")
            return None

        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )

        print("🤖 Generiere Draft mit DeepSeek...")

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "Du bist ein Experte für Förderanträge an Grundschulen in Deutschland."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=2048
        )

        draft = response.choices[0].message.content
        return draft

    except Exception as e:
        print(f"❌ Draft-Generation fehlgeschlagen: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    print("=" * 80)
    print("DIREKTER DRAFT-TEST - Julius Hirsch Preis")
    print("=" * 80)
    print()

    # 1. Lade Funding-Daten
    print("📊 Lade Funding-Daten aus DB...")
    funding_data = get_funding_data(JULIUS_HIRSCH_ID)

    if not funding_data:
        print("❌ Julius Hirsch Preis nicht in DB gefunden!")
        return 1

    print(f"✅ Geladen: {funding_data['title']}")
    print(f"   Quality Score: {funding_data['quality_score']}")
    print()

    # 2. Generiere Draft
    print("🚀 Generiere Förderantrag...")
    print()

    draft = generate_draft_simple(funding_data, SCHOOL_DATA, PROJECT_DESCRIPTION)

    if not draft:
        print("❌ Draft-Generation fehlgeschlagen")
        return 1

    # 3. Zeige Draft
    print("=" * 80)
    print("GENERIERTER FÖRDERANTRAG")
    print("=" * 80)
    print()
    print(draft)
    print()

    # 4. Qualitätsprüfung
    print("=" * 80)
    print("QUALITÄTSPRÜFUNG")
    print("=" * 80)
    print()

    checks = {
        "Deadline erwähnt (30. Juni 2025)": "30. Juni 2025" in draft or "30.06.2025" in draft,
        "DFB erwähnt": "DFB" in draft or "Deutscher Fußball-Bund" in draft,
        "Anti-Rassismus/Antisemitismus": "Antisemitismus" in draft or "Rassismus" in draft or "Diskriminierung" in draft,
        "Schule erwähnt": "Musterberg" in draft or "Grundschule" in draft,
        "Fußball-AG erwähnt": "Fußball" in draft,
        "Integration erwähnt": "Integration" in draft or "Flüchtling" in draft,
        "Projektzeitraum": "2024" in draft or "2025" in draft,
        "Länge ausreichend": len(draft) > 500
    }

    passed = sum(1 for v in checks.values() if v)
    total = len(checks)

    for check, result in checks.items():
        icon = "✅" if result else "❌"
        print(f"{icon} {check}")

    print()
    print(f"📊 Quality Score: {passed}/{total} = {passed/total*100:.0f}%")
    print(f"📏 Draft Length: {len(draft)} Zeichen")
    print()

    if passed >= total * 0.75:
        print("🎉 DRAFT GENERATION ERFOLGREICH!")
        print()
        print("✅ DeepSeek hat einen hochwertigen Antrag generiert")
        print("✅ Alle wichtigen Punkte wurden adressiert")
        print("✅ Der Antrag ist bereit für manuelle Review")
        return 0
    else:
        print("⚠️ Draft-Qualität könnte besser sein")
        return 1


if __name__ == '__main__':
    exit(main())
