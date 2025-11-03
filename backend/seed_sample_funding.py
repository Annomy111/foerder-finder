#!/usr/bin/env python3
"""
Seed sample funding data for testing Advanced RAG
"""

import sqlite3
import uuid
from datetime import datetime

# Sample funding opportunities (German)
SAMPLE_FUNDING = [
    {
        "title": "DigitalPakt Schule 2.0 - Tablets für Grundschulen",
        "provider": "DigitalPakt Schule",
        "region": "Berlin",
        "funding_area": "Digitalisierung",
        "min_funding_amount": 5000.0,
        "max_funding_amount": 50000.0,
        "source_url": "https://digitalpaktschule.de/tablets",
        "cleaned_text": """
# DigitalPakt Schule 2.0 - Tablets für Grundschulen

## Förderziel
Unterstützung von Grundschulen bei der Anschaffung digitaler Endgeräte zur Verbesserung der digitalen Bildung.

## Zielgruppe
- Öffentliche Grundschulen in Berlin
- Träger von Grundschulen

## Förderfähige Maßnahmen
- Anschaffung von Tablets (iPads oder Android)
- Schutzhüllen und Zubehör
- Ladewagen oder Aufbewahrungssysteme
- Lehrerfortbildung (bis zu 10% der Fördersumme)

## Förderhöhe
- Mindestfördersumme: 5.000 Euro
- Höchstfördersumme: 50.000 Euro
- Fördersatz: bis zu 90% der zuwendungsfähigen Ausgaben

## Voraussetzungen
- Vorhandenes oder in Entwicklung befindliches Medienkonzept
- Technische Infrastruktur (WLAN) muss vorhanden sein
- Fortbildungskonzept für Lehrkräfte

## Bewerbungsfrist
Laufend bis 31.12.2025

## Kontakt
digitalpakt@senbjf.berlin.de
Tel: 030 90227-5000
        """
    },
    {
        "title": "BMBF Förderung - MINT-Projekte an Grundschulen",
        "provider": "BMBF",
        "region": "Bundesweit",
        "funding_area": "MINT-Bildung",
        "min_funding_amount": 2000.0,
        "max_funding_amount": 25000.0,
        "source_url": "https://bmbf.de/mint-grundschule",
        "cleaned_text": """
# BMBF Förderung - MINT-Projekte an Grundschulen

## Programmbeschreibung
Das Bundesministerium für Bildung und Forschung (BMBF) fördert innovative MINT-Projekte (Mathematik, Informatik, Naturwissenschaften, Technik) an Grundschulen.

## Förderschwerpunkte
- Experimentier- und Forscherworkshops
- Anschaffung von MINT-Materialien (Robotik, Mikroskope, etc.)
- Kooperationen mit außerschulischen MINT-Lernorten
- Entwicklung digitaler MINT-Lernmaterialien

## Antragsberechtigt
- Grundschulen aller Bundesländer
- Gemeinnützige Träger von Grundschulen
- Schulfördervereine in Kooperation mit Schulen

## Förderumfang
- 2.000 € - 25.000 € je Projekt
- Projektlaufzeit: 6-24 Monate
- Eigenmittel: mindestens 10%

## Bewertungskriterien
- Innovationsgehalt des Projekts
- Einbindung der Schüler*innen
- Nachhaltigkeit und Verstetigung
- Geschlechtergerechte Ansprache

## Antragsverfahren
1. Projektskizze (max. 5 Seiten) einreichen
2. Bei positivem Bescheid: Vollantrag stellen
3. Bewilligungszeitraum: ca. 3 Monate

## Fristen
- Einreichung Projektskizzen: laufend
- Hauptantragsfrist: 30.06.2025

## Kontakt
mint-foerderung@bmbf.bund.de
        """
    },
    {
        "title": "Stiftung Bildung - Förderung von Bildungsprojekten",
        "provider": "Stiftung Bildung",
        "region": "Bundesweit",
        "funding_area": "Bildungsprojekte",
        "min_funding_amount": 500.0,
        "max_funding_amount": 5000.0,
        "source_url": "https://stiftungbildung.org/projekte",
        "cleaned_text": """
# Stiftung Bildung - Förderung von Bildungsprojekten

## Über die Förderung
Die Stiftung Bildung unterstützt Projekte, die das Lernen und Leben von Kindern und Jugendlichen nachhaltig verbessern.

## Förderfähige Projekte
- Pausenhofgestaltung
- Leseförderung und Bibliotheken
- Umwelt- und Nachhaltigkeitsprojekte
- Kulturelle Bildung (Musik, Theater, Kunst)
- Inklusion und Integration
- Gesundheitsförderung

## Antragstellung
- Anträge können von Schulfördervereinen gestellt werden
- Formloser Antrag mit Projektbeschreibung
- Budget- und Finanzierungsplan erforderlich

## Förderhöhe
- Kleinprojekte: 500 € - 1.500 €
- Größere Projekte: 1.500 € - 5.000 €
- Besondere Projekte: bis zu 15.000 €

## Förderquote
- Bis zu 100% der Projektkosten
- Eigenleistungen werden anerkannt

## Entscheidungszeitraum
- Schnellverfahren (< 1.000 €): 2-4 Wochen
- Reguläres Verfahren: 6-8 Wochen

## Besonderheiten
- Unbürokratisches Verfahren
- Beratung und Begleitung durch Stiftung
- Vernetzung mit anderen Projekten möglich

## Kontakt
foerderung@stiftungbildung.org
Tel: 030 8096 2701
        """
    },
    {
        "title": "Land Brandenburg - Schulausstattung und Digitalisierung",
        "provider": "Land Brandenburg",
        "region": "Brandenburg",
        "funding_area": "Digitalisierung",
        "min_funding_amount": 10000.0,
        "max_funding_amount": 100000.0,
        "source_url": "https://mbjs.brandenburg.de/foerderung",
        "cleaned_text": """
# Land Brandenburg - Schulausstattung und Digitalisierung

## Förderzweck
Verbesserung der digitalen Ausstattung von Grundschulen in Brandenburg zur Umsetzung des Basiscurriculums Medienbildung.

## Fördergegenstände
- Endgeräte (Tablets, Notebooks, Convertibles)
- Interaktive Displays und digitale Tafeln
- Dokumentenkameras
- Server und Netzwerkkomponenten
- Software und Lizenzen (max. 20%)

## Antragsberechtigt
- Schulträger (Kommunen, Landkreise)
- Freie Träger von Grundschulen

## Förderung
- Mindestzuwendung: 10.000 €
- Höchstzuwendung: 100.000 € pro Schule
- Zuwendung: bis zu 90% der zuwendungsfähigen Ausgaben

## Fördervoraussetzungen
- Technisch-pädagogisches Einsatzkonzept (TPEK)
- Fortbildungsplan für Lehrkräfte
- Wartungs- und Supportkonzept
- Kofinanzierung gesichert

## Nicht förderfähig
- Ersatzbeschaffungen für defekte Geräte
- Schulungen ohne direkten Projektbezug
- Allgemeine Verwaltungsausgaben

## Antragsverfahren
1. Beratungsgespräch mit MBJS
2. Antragstellung über ProFIS
3. Verwendungsnachweis nach Projektende

## Fristen
Antragstellung: bis 30.09.2025 für Maßnahmen im Folgejahr

## Kontakt
digitalisierung-schule@mbjs.brandenburg.de
Tel: 0331 866-3841
        """
    },
    {
        "title": "Deutsche Telekom Stiftung - Digitales Lernen Grundschule",
        "provider": "Deutsche Telekom Stiftung",
        "region": "Bundesweit",
        "funding_area": "MINT-Bildung",
        "min_funding_amount": 0.0,
        "max_funding_amount": 15000.0,
        "source_url": "https://telekom-stiftung.de/grundschule",
        "cleaned_text": """
# Deutsche Telekom Stiftung - Digitales Lernen Grundschule

## Programmziele
Förderung von MINT-Bildung und digitalen Kompetenzen in der Grundschule durch modellhafte Projekte.

## Schwerpunkte
- Programmieren und Coding in der Grundschule
- Robotik und Making
- Naturwissenschaftliches Experimentieren mit digitalen Tools
- Medienbildung und Informatik

## Förderformat
- Ausschreibungsverfahren (jährlich)
- Auswahl von Modellschulen
- Paket aus Materialien, Fortbildung und Vernetzung

## Leistungen
- Materialpaket (z.B. Calliope mini, LEGO Education)
- Fortbildungen für Lehrkräfte (vor Ort und online)
- Begleitung durch Projektteam
- Vernetzung mit anderen Schulen

## Wert pro Schule
Sachleistungen im Wert von ca. 10.000-15.000 €

## Teilnahmevoraussetzungen
- Grundschule mit Klassen 1-4 (oder 1-6)
- Bereitschaft zur Teilnahme an Evaluation
- Engagement der Schulleitung
- Mindestens 2 interessierte Lehrkräfte

## Bewerbungsverfahren
- Ausschreibung: November
- Bewerbungsfrist: Januar
- Auswahl: März
- Projektstart: Nach den Sommerferien

## Evaluation
Wissenschaftliche Begleitung durch Universität Duisburg-Essen

## Kontakt
grundschule@telekom-stiftung.de
        """
    }
]

def seed_database():
    """Seed sample funding data"""
    conn = sqlite3.connect('dev_database.db')
    cursor = conn.cursor()

    print('[INFO] Seeding sample funding data...')

    inserted = 0
    for funding in SAMPLE_FUNDING:
        funding_id = uuid.uuid4().hex.upper()

        try:
            cursor.execute("""
                INSERT INTO FUNDING_OPPORTUNITIES (
                    funding_id, title, provider, region, funding_area,
                    min_funding_amount, max_funding_amount, source_url,
                    cleaned_text, last_scraped, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                funding_id,
                funding['title'],
                funding['provider'],
                funding['region'],
                funding['funding_area'],
                funding['min_funding_amount'],
                funding['max_funding_amount'],
                funding['source_url'],
                funding['cleaned_text'],
                datetime.now(),
                datetime.now(),
                datetime.now()
            ))

            inserted += 1
            print(f'[✓] {funding["title"][:60]}...')

        except sqlite3.IntegrityError:
            print(f'[SKIP] {funding["title"][:60]}... (already exists)')

    conn.commit()
    conn.close()

    print(f'\n[SUCCESS] Inserted {inserted} funding opportunities')
    print(f'[INFO] Total funding opportunities in database: {inserted + 2}')  # +2 for existing test records


if __name__ == '__main__':
    seed_database()
