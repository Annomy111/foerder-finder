#!/usr/bin/env python3
"""
Fügt Julius Hirsch Preis manuell zur Datenbank hinzu

Basiert auf Web-Research Daten vom DFB
Quality Score: Manuell kuratiert = 1.0
"""

import sqlite3
import uuid
import json
from datetime import datetime

DB_PATH = "dev_database.db"

# Julius Hirsch Preis Daten
JULIUS_HIRSCH_DATA = {
    "title": "Julius Hirsch Preis",
    "provider": "DFB - Deutscher Fußball-Bund",
    "description": "Der Julius Hirsch Preis erinnert an den deutsch-jüdischen Nationalspieler Julius Hirsch und alle jüdischen Opfer des Nationalsozialismus. Der Preis wird an Personen und Institutionen vergeben, die sich gegen Antisemitismus, Rassismus und Diskriminierung im Fußball einsetzen.",
    "deadline": "2025-06-30",
    "min_funding_amount": None,
    "max_funding_amount": None,
    "eligibility_criteria": [
        "Vereine, Institutionen und Einzelpersonen im Fußballbereich",
        "Engagement gegen Antisemitismus und Rassismus im Fußball",
        "Projekte zwischen 1. Juli 2024 und 30. Juni 2025 durchgeführt",
        "Oder kontinuierliche Aktivitäten über mehrere Jahre"
    ],
    "target_groups": [
        "Fußballvereine aller Altersklassen",
        "Schulen mit Fußball-AGs und Sport-Projekten",
        "Anti-Diskriminierungs-Initiativen",
        "Bildungseinrichtungen mit Demokratie-Projekten",
        "Kinder- und Jugendarbeit im Fußball"
    ],
    "evaluation_criteria": [
        "Nachhaltigkeit und Langfristigkeit des Engagements",
        "Innovativer Ansatz gegen Diskriminierung",
        "Breitenwirkung und Reichweite des Projekts",
        "Authentizität und Glaubwürdigkeit",
        "Vorbildcharakter für andere Vereine/Institutionen"
    ],
    "requirements": [
        "Bewerbung über Online-Formular auf dfb.de",
        "Detaillierte Projektbeschreibung einreichen",
        "Nachweis der durchgeführten Aktivitäten",
        "Dokumentation (Fotos, Videos, Presseberichte)"
    ],
    "application_process": "Bewerbung erfolgt online über das Formular auf der DFB-Website. Nach Einreichung prüft eine Jury aus Expertinnen und Experten alle Bewerbungen. Die Preisträger werden zur feierlichen Preisverleihung nach Hamburg eingeladen.",
    "application_url": "https://www.dfb.de/preisewettbewerbe/julius-hirsch-preis/anmeldung/",
    "source_url": "https://www.dfb.de/preisewettbewerbe/julius-hirsch-preis/",
    "contact_email": None,  # Nicht öffentlich
    "contact_phone": None,
    "contact_person": "DFB Julius Hirsch Preis Jury",
    "decision_timeline": "Preisverleihung: 27. November 2025 in Hamburg",
    "funding_period": "Projekte von 1. Juli 2024 bis 30. Juni 2025",
    "co_financing_required": False,
    "co_financing_rate": None,
    "eligible_costs": [
        "Sachkosten für Anti-Rassismus-Projekte",
        "Materialien für Bildungsarbeit",
        "Veranstaltungen und Workshops",
        "Öffentlichkeitsarbeit und Dokumentation"
    ],
    "region": "Bundesweit",
    "source_type": "preis",
    "extraction_quality_score": 1.0,  # Manuell kuratiert
    "cleaned_text": """
Julius Hirsch Preis des Deutschen Fußball-Bundes

Der Deutsche Fußball-Bund erinnert mit der Stiftung des Julius Hirsch Preises seit 2005 jährlich an den
deutsch-jüdischen Nationalspieler Julius Hirsch (1892-1943) und an alle jüdischen Opfer des nationalsozialistischen
Unrechtsstaates.

Der Preis wird an Personen, Institutionen und Vereine vergeben, die sich aktiv gegen Antisemitismus, Rassismus
und jede Form von Diskriminierung im Fußball einsetzen.

Bewerbungszeitraum:
Die Bewerbungsphase endet am 30. Juni 2025. Projekte müssen zwischen dem 1. Juli 2024 und dem 30. Juni 2025
durchgeführt worden sein oder kontinuierlich über mehrere Jahre gelaufen sein.

Preisverleihung:
Die feierliche Preisverleihung findet am 27. November 2025 in Hamburg statt und wird von der DFB-Kulturstiftung
organisiert. Die Veranstaltung wird von prominenten Gästen besucht und erhält bundesweite mediale Aufmerksamkeit.

Bewerbung:
Bewerbungen erfolgen über ein Online-Formular auf der DFB-Website. Die Jury besteht aus Expertinnen und Experten
aus Sport, Politik und Gesellschaft.

Besondere Relevanz für Grundschulen:
Der Julius Hirsch Preis ist besonders relevant für Grundschulen mit Fußball-AGs, Sport-Projekten oder
Demokratie-Bildungs-Initiativen. Projekte gegen Diskriminierung und für Integration können ausgezeichnet werden.
    """.strip()
}


def main():
    print("="*80)
    print("Julius Hirsch Preis in Datenbank speichern")
    print("="*80)
    print()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check if already exists
    cursor.execute("""
        SELECT funding_id FROM FUNDING_OPPORTUNITIES
        WHERE title LIKE '%Julius Hirsch%'
    """)
    existing = cursor.fetchone()

    if existing:
        print(f"⚠️ Julius Hirsch Preis bereits vorhanden (ID: {existing[0]})")
        print("   Überschreibe Daten...")
        funding_id = existing[0]
        mode = "UPDATE"
    else:
        funding_id = str(uuid.uuid4()).replace('-', '').upper()
        mode = "INSERT"

    try:
        if mode == "INSERT":
            # INSERT new record
            cursor.execute("""
                INSERT INTO FUNDING_OPPORTUNITIES (
                    funding_id, title, description, cleaned_text, region,
                    funder_name, source_url, last_scraped, source_type, provider,
                    application_deadline, application_url,
                    eligibility, target_groups, evaluation_criteria, requirements,
                    application_process, contact_person, decision_timeline, funding_period,
                    co_financing_required, co_financing_rate, eligible_costs,
                    extraction_quality_score, last_extracted
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                funding_id,
                JULIUS_HIRSCH_DATA['title'],
                JULIUS_HIRSCH_DATA['description'],
                JULIUS_HIRSCH_DATA['cleaned_text'],
                JULIUS_HIRSCH_DATA['region'],
                JULIUS_HIRSCH_DATA['provider'],
                JULIUS_HIRSCH_DATA['source_url'],
                datetime.now(),
                JULIUS_HIRSCH_DATA['source_type'],
                JULIUS_HIRSCH_DATA['provider'],
                JULIUS_HIRSCH_DATA['deadline'],
                JULIUS_HIRSCH_DATA['application_url'],
                json.dumps(JULIUS_HIRSCH_DATA['eligibility_criteria'], ensure_ascii=False),
                json.dumps(JULIUS_HIRSCH_DATA['target_groups'], ensure_ascii=False),
                json.dumps(JULIUS_HIRSCH_DATA['evaluation_criteria'], ensure_ascii=False),
                json.dumps(JULIUS_HIRSCH_DATA['requirements'], ensure_ascii=False),
                JULIUS_HIRSCH_DATA['application_process'],
                JULIUS_HIRSCH_DATA['contact_person'],
                JULIUS_HIRSCH_DATA['decision_timeline'],
                JULIUS_HIRSCH_DATA['funding_period'],
                1 if JULIUS_HIRSCH_DATA['co_financing_required'] else 0,
                JULIUS_HIRSCH_DATA['co_financing_rate'],
                json.dumps(JULIUS_HIRSCH_DATA['eligible_costs'], ensure_ascii=False),
                JULIUS_HIRSCH_DATA['extraction_quality_score'],
                datetime.now()
            ))
        else:
            # UPDATE existing record
            cursor.execute("""
                UPDATE FUNDING_OPPORTUNITIES SET
                    description = ?,
                    cleaned_text = ?,
                    region = ?,
                    funder_name = ?,
                    source_url = ?,
                    last_scraped = ?,
                    source_type = ?,
                    provider = ?,
                    application_deadline = ?,
                    application_url = ?,
                    eligibility = ?,
                    target_groups = ?,
                    evaluation_criteria = ?,
                    requirements = ?,
                    application_process = ?,
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
                JULIUS_HIRSCH_DATA['description'],
                JULIUS_HIRSCH_DATA['cleaned_text'],
                JULIUS_HIRSCH_DATA['region'],
                JULIUS_HIRSCH_DATA['provider'],
                JULIUS_HIRSCH_DATA['source_url'],
                datetime.now(),
                JULIUS_HIRSCH_DATA['source_type'],
                JULIUS_HIRSCH_DATA['provider'],
                JULIUS_HIRSCH_DATA['deadline'],
                JULIUS_HIRSCH_DATA['application_url'],
                json.dumps(JULIUS_HIRSCH_DATA['eligibility_criteria'], ensure_ascii=False),
                json.dumps(JULIUS_HIRSCH_DATA['target_groups'], ensure_ascii=False),
                json.dumps(JULIUS_HIRSCH_DATA['evaluation_criteria'], ensure_ascii=False),
                json.dumps(JULIUS_HIRSCH_DATA['requirements'], ensure_ascii=False),
                JULIUS_HIRSCH_DATA['application_process'],
                JULIUS_HIRSCH_DATA['contact_person'],
                JULIUS_HIRSCH_DATA['decision_timeline'],
                JULIUS_HIRSCH_DATA['funding_period'],
                1 if JULIUS_HIRSCH_DATA['co_financing_required'] else 0,
                JULIUS_HIRSCH_DATA['co_financing_rate'],
                json.dumps(JULIUS_HIRSCH_DATA['eligible_costs'], ensure_ascii=False),
                JULIUS_HIRSCH_DATA['extraction_quality_score'],
                datetime.now(),
                funding_id
            ))

        conn.commit()

        print(f"✅ {mode} erfolgreich!")
        print(f"   Funding ID: {funding_id}")
        print(f"   Quality Score: {JULIUS_HIRSCH_DATA['extraction_quality_score']}")
        print()

        # Verify
        cursor.execute("""
            SELECT title, application_deadline, extraction_quality_score, application_url
            FROM FUNDING_OPPORTUNITIES
            WHERE funding_id = ?
        """, (funding_id,))

        row = cursor.fetchone()
        if row:
            print("🔍 Verifikation:")
            print(f"   Titel: {row[0]}")
            print(f"   Deadline: {row[1]}")
            print(f"   Quality Score: {row[2]}")
            print(f"   URL: {row[3]}")

    except Exception as e:
        print(f"❌ Fehler: {e}")
        conn.rollback()
    finally:
        conn.close()

    print()
    print("="*80)


if __name__ == '__main__':
    main()
