"""
Seed Demo Funding Data
Populates the database with realistic German funding opportunities for elementary schools
"""

import sqlite3
import uuid
from datetime import datetime, timedelta

def generate_id():
    return str(uuid.uuid4()).replace('-', '').upper()

def seed_funding_data():
    """Add realistic German funding opportunities"""

    # Connect to SQLite database
    conn = sqlite3.connect('dev_database.db')
    cursor = conn.cursor()

    # Sample funding opportunities (realistic German programs)
    funding_opportunities = [
        {
            'title': 'DigitalPakt Schule 2.0',
            'provider': 'Bundesministerium für Bildung und Forschung (BMBF)',
            'description': 'Förderung der digitalen Infrastruktur und Ausstattung von Schulen. Finanzierung von interaktiven Tafeln, Tablets, WLAN-Ausbau und IT-Support.',
            'eligibility': 'Grundschulen in ganz Deutschland. Antragstellung über das zuständige Bundesland.',
            'application_deadline': (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d'),
            'funding_amount_min': 10000.0,
            'funding_amount_max': 100000.0,
            'categories': 'Digitalisierung,IT-Infrastruktur,Ausstattung',
            'target_groups': 'Grundschulen,Lehrkräfte',
            'url': 'https://www.digitalpaktschule.de',
            'source_url': 'https://www.bmbf.de/digitalpakt',
            'cleaned_text': 'DigitalPakt Schule unterstützt Schulen bei der digitalen Transformation durch Finanzierung moderner Technologie.'
        },
        {
            'title': 'Demokratie leben! - Projekte für Kinder',
            'provider': 'Bundesministerium für Familie, Senioren, Frauen und Jugend (BMFSFJ)',
            'description': 'Förderung von Projekten zur Demokratiebildung, Vielfaltgestaltung und Extremismusprävention an Grundschulen.',
            'eligibility': 'Grundschulen und Träger der freien Jugendhilfe. Projekte mit Beteiligung von Kindern im Grundschulalter.',
            'application_deadline': (datetime.now() + timedelta(days=120)).strftime('%Y-%m-%d'),
            'funding_amount_min': 5000.0,
            'funding_amount_max': 25000.0,
            'categories': 'Demokratiebildung,Soziales Lernen,Prävention',
            'target_groups': 'Grundschulen,Schüler',
            'url': 'https://www.demokratie-leben.de',
            'source_url': 'https://www.bmfsfj.de/demokratie-leben',
            'cleaned_text': 'Demokratie leben fördert Projekte zur Stärkung demokratischer Werte bei Kindern.'
        },
        {
            'title': 'Bildung für nachhaltige Entwicklung (BNE)',
            'provider': 'Deutsche Bundesstiftung Umwelt (DBU)',
            'description': 'Unterstützung von Umweltbildungsprojekten, Schulgärten, Nachhaltigkeitsprojekten und Klimaschutzmaßnahmen.',
            'eligibility': 'Grundschulen mit innovativen BNE-Konzepten. Projekte mit messbarem Umweltimpact.',
            'application_deadline': (datetime.now() + timedelta(days=150)).strftime('%Y-%m-%d'),
            'funding_amount_min': 8000.0,
            'funding_amount_max': 50000.0,
            'categories': 'Nachhaltigkeit,Umweltbildung,Klimaschutz',
            'target_groups': 'Grundschulen,Umwelt-AGs',
            'url': 'https://www.dbu.de/bne',
            'source_url': 'https://www.dbu.de/foerderung',
            'cleaned_text': 'BNE-Förderung für Umweltbildung und Nachhaltigkeitsprojekte an Schulen.'
        },
        {
            'title': 'Kultur macht stark - Bündnisse für Bildung',
            'provider': 'Bundesministerium für Bildung und Forschung (BMBF)',
            'description': 'Förderung außerschulischer kultureller Bildungsangebote: Musik, Theater, Tanz, Literatur, Kunst für bildungsbenachteiligte Kinder.',
            'eligibility': 'Bündnisse von mindestens 3 Partnern (Schulen + Kultureinrichtungen + lokale Träger).',
            'application_deadline': (datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d'),
            'funding_amount_min': 3000.0,
            'funding_amount_max': 30000.0,
            'categories': 'Kulturelle Bildung,Musik,Theater,Kunst',
            'target_groups': 'Grundschulen,Bildungsbenachteiligte Kinder',
            'url': 'https://www.buendnisse-fuer-bildung.de',
            'source_url': 'https://www.bmbf.de/kultur-macht-stark',
            'cleaned_text': 'Kultur macht stark fördert kulturelle Bildungsprojekte für benachteiligte Kinder.'
        },
        {
            'title': 'Sprachförderung für mehrsprachige Kinder',
            'provider': 'Mercator-Stiftung',
            'description': 'Finanzierung von Sprachförderprogrammen, DaZ-Materialien (Deutsch als Zweitsprache) und Fortbildungen für Lehrkräfte.',
            'eligibility': 'Grundschulen mit hohem Anteil mehrsprachiger Schüler. Nachweis eines pädagogischen Konzepts erforderlich.',
            'application_deadline': (datetime.now() + timedelta(days=75)).strftime('%Y-%m-%d'),
            'funding_amount_min': 5000.0,
            'funding_amount_max': 20000.0,
            'categories': 'Sprachbildung,Integration,DaZ',
            'target_groups': 'Grundschulen,mehrsprachige Schüler',
            'url': 'https://www.mercator-institut-sprachfoerderung.de',
            'source_url': 'https://www.stiftung-mercator.de/sprachfoerderung',
            'cleaned_text': 'Mercator-Förderung für Sprachbildung und DaZ an Grundschulen.'
        },
        {
            'title': 'Bewegte Schule - Gesundheitsförderung',
            'provider': 'AOK Bundesverband',
            'description': 'Förderung von Bewegungs- und Gesundheitsprojekten: Pausenhofgestaltung, Sportgeräte, Gesundheitstage, gesunde Ernährung.',
            'eligibility': 'Alle Grundschulen. Fokus auf nachhaltige Gesundheitskonzepte.',
            'application_deadline': (datetime.now() + timedelta(days=100)).strftime('%Y-%m-%d'),
            'funding_amount_min': 2000.0,
            'funding_amount_max': 15000.0,
            'categories': 'Gesundheit,Bewegung,Sport,Ernährung',
            'target_groups': 'Grundschulen,Schüler',
            'url': 'https://www.aok.de/pk/uni/inhalt/bewegte-schule',
            'source_url': 'https://www.aok.de/schulprogramme',
            'cleaned_text': 'AOK fördert Bewegungs- und Gesundheitsprojekte an Grundschulen.'
        },
        {
            'title': 'MINT-Förderung für Grundschulen',
            'provider': 'Stiftung Haus der kleinen Forscher',
            'description': 'Unterstützung von MINT-Projekten (Mathematik, Informatik, Naturwissenschaften, Technik): Forscherwerkstätten, Experimentier-Sets, Lehrerfortbildungen.',
            'eligibility': 'Grundschulen mit MINT-Schwerpunkt. Zertifizierung als "Haus der kleinen Forscher" von Vorteil.',
            'application_deadline': (datetime.now() + timedelta(days=45)).strftime('%Y-%m-%d'),
            'funding_amount_min': 3000.0,
            'funding_amount_max': 18000.0,
            'categories': 'MINT,Naturwissenschaften,Forschendes Lernen',
            'target_groups': 'Grundschulen,MINT-interessierte Schüler',
            'url': 'https://www.haus-der-kleinen-forscher.de',
            'source_url': 'https://www.haus-der-kleinen-forscher.de/foerderung',
            'cleaned_text': 'Haus der kleinen Forscher fördert MINT-Bildung an Grundschulen.'
        },
        {
            'title': 'Leseförderung und Bibliotheksausstattung',
            'provider': 'Stiftung Lesen',
            'description': 'Finanzierung von Schulbibliotheken, Leseclubs, Autorenlesungen und Lese-Events. Kostenlose Bücher und Materialien.',
            'eligibility': 'Grundschulen ohne eigene Bibliothek oder mit Ausbaubedarf.',
            'application_deadline': (datetime.now() + timedelta(days=110)).strftime('%Y-%m-%d'),
            'funding_amount_min': 4000.0,
            'funding_amount_max': 22000.0,
            'categories': 'Leseförderung,Bibliothek,Literatur',
            'target_groups': 'Grundschulen,Leseclubs',
            'url': 'https://www.stiftunglesen.de',
            'source_url': 'https://www.stiftunglesen.de/schulen',
            'cleaned_text': 'Stiftung Lesen fördert Lesekultur und Bibliotheken an Grundschulen.'
        },
        {
            'title': 'Inklusion gestalten - Barrierefreie Schule',
            'provider': 'Aktion Mensch',
            'description': 'Förderung baulicher Maßnahmen (Rampen, Fahrstühle) und inklusiver Lernmaterialien für Kinder mit Behinderungen.',
            'eligibility': 'Grundschulen mit inklusivem Schulkonzept. Ko-Finanzierung möglich.',
            'application_deadline': (datetime.now() + timedelta(days=135)).strftime('%Y-%m-%d'),
            'funding_amount_min': 10000.0,
            'funding_amount_max': 80000.0,
            'categories': 'Inklusion,Barrierefreiheit,Sonderpädagogik',
            'target_groups': 'Grundschulen,Kinder mit Behinderungen',
            'url': 'https://www.aktion-mensch.de/foerderung/foerderprogramme/barrierefreiheit',
            'source_url': 'https://www.aktion-mensch.de/schule',
            'cleaned_text': 'Aktion Mensch fördert Inklusion und Barrierefreiheit an Schulen.'
        },
        {
            'title': 'Gewaltprävention und soziales Lernen',
            'provider': 'Robert Bosch Stiftung',
            'description': 'Projekte zur Gewaltprävention, Konfliktlösung, Streitschlichterprogramme und sozial-emotionales Lernen.',
            'eligibility': 'Grundschulen mit Präventionskonzept. Evaluation der Maßnahmen erforderlich.',
            'application_deadline': (datetime.now() + timedelta(days=80)).strftime('%Y-%m-%d'),
            'funding_amount_min': 6000.0,
            'funding_amount_max': 28000.0,
            'categories': 'Gewaltprävention,Soziales Lernen,Konfliktlösung',
            'target_groups': 'Grundschulen,Schulsozialarbeit',
            'url': 'https://www.bosch-stiftung.de',
            'source_url': 'https://www.bosch-stiftung.de/bildung',
            'cleaned_text': 'Robert Bosch Stiftung fördert Gewaltprävention und soziales Lernen.'
        }
    ]

    # Insert funding opportunities
    inserted_count = 0
    for funding in funding_opportunities:
        funding_id = generate_id()

        try:
            cursor.execute('''
                INSERT INTO FUNDING_OPPORTUNITIES (
                    funding_id, title, provider, description, eligibility,
                    application_deadline, funding_amount_min, funding_amount_max,
                    categories, target_groups, url, source_url, cleaned_text,
                    last_scraped
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                funding_id,
                funding['title'],
                funding['provider'],
                funding['description'],
                funding['eligibility'],
                funding['application_deadline'],
                funding['funding_amount_min'],
                funding['funding_amount_max'],
                funding['categories'],
                funding['target_groups'],
                funding['url'],
                funding['source_url'],
                funding['cleaned_text']
            ))
            inserted_count += 1
            print(f"✅ Inserted: {funding['title']}")
        except Exception as e:
            print(f"❌ Error inserting {funding['title']}: {e}")

    conn.commit()
    conn.close()

    print(f"\n🎉 Successfully inserted {inserted_count} funding opportunities!")
    print(f"💡 Refresh your browser to see the data!")

if __name__ == '__main__':
    seed_funding_data()
