#!/usr/bin/env python3
"""
Test-Script für Stiftungen-Scraper
Testet Firecrawl-Integration ohne DB-Abhängigkeit
"""

import json
import requests
import sys
from datetime import datetime

# Firecrawl Configuration
FIRECRAWL_URL = "http://130.61.137.77:3002"

# Test URLs für Stiftungen
TEST_URLS = {
    'dsz': 'https://www.deutsches-stiftungszentrum.de',
    'bundesverband': 'https://www.stiftungen.org',
    'dkjs': 'https://www.dkjs.de'
}


def test_firecrawl_connection():
    """Teste Firecrawl-Verbindung"""
    print("🔍 Teste Firecrawl-Verbindung...")
    try:
        response = requests.get(f"{FIRECRAWL_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ Firecrawl ist erreichbar!")
            return True
        else:
            print(f"⚠️ Firecrawl Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Firecrawl nicht erreichbar: {e}")
        return False


def scrape_single_page(url: str):
    """
    Scrape eine einzelne Seite mit Firecrawl

    Args:
        url: URL zum Scrapen

    Returns:
        Scraped content als dict
    """
    print(f"\n📄 Scrape: {url}")

    try:
        response = requests.post(
            f"{FIRECRAWL_URL}/v1/scrape",
            json={
                "url": url,
                "formats": ["markdown"],
                "onlyMainContent": True
            },
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Erfolgreich gescraped!")
            print(f"   Content-Länge: {len(data.get('data', {}).get('markdown', ''))} Zeichen")
            return data.get('data', {})
        else:
            print(f"❌ Fehler: {response.status_code}")
            print(response.text)
            return None

    except Exception as e:
        print(f"❌ Exception: {e}")
        return None


def crawl_website(url: str, max_pages: int = 5):
    """
    Crawle eine Website mit mehreren Unterseiten

    Args:
        url: Basis-URL
        max_pages: Maximale Anzahl Seiten

    Returns:
        Liste von gecrawlten Seiten
    """
    print(f"\n🚀 Starte Crawl: {url} (max {max_pages} Seiten)")

    try:
        response = requests.post(
            f"{FIRECRAWL_URL}/v1/crawl",
            json={
                "url": url,
                "limit": max_pages,
                "maxDepth": 2,
                "excludePaths": [
                    "*/impressum*",
                    "*/datenschutz*",
                    "*/privacy*",
                    "*/cookies*"
                ],
                "formats": ["markdown"],
                "onlyMainContent": True
            },
            timeout=120
        )

        if response.status_code == 200:
            data = response.json()
            pages = data.get('data', [])
            print(f"✅ {len(pages)} Seiten gecrawlt!")

            # Zeige Übersicht
            for i, page in enumerate(pages, 1):
                print(f"   {i}. {page.get('url', 'N/A')} ({len(page.get('markdown', ''))} chars)")

            return pages
        else:
            print(f"❌ Fehler: {response.status_code}")
            print(response.text)
            return []

    except Exception as e:
        print(f"❌ Exception: {e}")
        return []


def extract_stiftung_info_sample(markdown_content: str):
    """
    Einfache Extraktion von Stiftungsinformationen (ohne LLM)
    Nur für Tests - echte Extraktion erfolgt mit DeepSeek
    """
    # Einfache Keyword-basierte Erkennung
    keywords = {
        'bildung': markdown_content.lower().count('bildung'),
        'förderung': markdown_content.lower().count('förder'),
        'grundschule': markdown_content.lower().count('grundschule'),
        'stiftung': markdown_content.lower().count('stiftung'),
        'antrag': markdown_content.lower().count('antrag')
    }

    return {
        'content_length': len(markdown_content),
        'keywords_found': keywords,
        'is_relevant': keywords['bildung'] > 2 or keywords['grundschule'] > 0
    }


def main():
    """Main Test Runner"""
    print("="*70)
    print("🧪 STIFTUNGEN-SCRAPER TEST")
    print("="*70)

    # Test 1: Firecrawl-Verbindung
    if not test_firecrawl_connection():
        print("\n❌ Firecrawl nicht verfügbar. Teste lokal: http://130.61.137.77:3002")
        sys.exit(1)

    # Test 2: Einzelne Seite scrapen
    print("\n" + "="*70)
    print("TEST 2: Einzelne Seite scrapen")
    print("="*70)

    page_data = scrape_single_page(TEST_URLS['dsz'])
    if page_data:
        # Analysiere Content
        analysis = extract_stiftung_info_sample(page_data.get('markdown', ''))
        print(f"\n📊 Analyse:")
        print(f"   Content-Länge: {analysis['content_length']}")
        print(f"   Keywords gefunden: {analysis['keywords_found']}")
        print(f"   Relevant für Bildung: {'✅ Ja' if analysis['is_relevant'] else '❌ Nein'}")

        # Speichere Sample
        with open('/tmp/stiftung_sample.md', 'w', encoding='utf-8') as f:
            f.write(page_data.get('markdown', ''))
        print("\n💾 Sample gespeichert: /tmp/stiftung_sample.md")

    # Test 3: Website crawlen (nur 3 Seiten zum Testen)
    print("\n" + "="*70)
    print("TEST 3: Website crawlen (3 Seiten)")
    print("="*70)

    pages = crawl_website(TEST_URLS['dsz'], max_pages=3)

    if pages:
        print(f"\n📊 Crawl-Statistik:")
        print(f"   Gesamt-Seiten: {len(pages)}")

        relevant_count = 0
        for page in pages:
            analysis = extract_stiftung_info_sample(page.get('markdown', ''))
            if analysis['is_relevant']:
                relevant_count += 1

        print(f"   Relevante Seiten: {relevant_count}/{len(pages)}")

        # Speichere alle Seiten als JSON
        output_file = f'/tmp/stiftungen_crawl_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(pages, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Crawl-Ergebnis gespeichert: {output_file}")

    print("\n" + "="*70)
    print("✅ TESTS ABGESCHLOSSEN")
    print("="*70)
    print("\nNächste Schritte:")
    print("1. LLM-Extraktion implementieren (DeepSeek)")
    print("2. DB-Integration testen")
    print("3. Produktiv-Crawl starten (DSZ, Bundesverband, etc.)")


if __name__ == "__main__":
    main()
