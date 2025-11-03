#!/usr/bin/env python3
"""
Scrape weitere Top-Stiftungen mit SUPER SCRAPER
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scraper_firecrawl'))

from super_scraper import super_scrape
import time

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
        "name": "Stiftung Mercator",
        "url": "https://www.mercator-stiftung.de",
        "min_quality": 0.25
    },
    {
        "name": "Klaus Tschira Stiftung",
        "url": "https://www.klaus-tschira-stiftung.de",
        "min_quality": 0.25
    },
    {
        "name": "Gemeinnützige Hertie-Stiftung",
        "url": "https://www.ghst.de",
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

def main():
    print("=" * 80)
    print("WEITERE STIFTUNGEN SCRAPEN")
    print("=" * 80)
    print()

    all_results = []

    for i, foundation in enumerate(FOUNDATIONS, 1):
        print(f"\n[{i}/{len(FOUNDATIONS)}] {foundation['name']}")
        print(f"URL: {foundation['url']}")
        print("-" * 80)

        try:
            programs = super_scrape(
                base_url=foundation['url'],
                source_name=foundation['name'],
                max_urls=20,
                min_quality=foundation['min_quality'],
                delay=3.0
            )

            print(f"\n✅ {len(programs)} Programme gefunden")
            all_results.append({
                'foundation': foundation['name'],
                'programs': programs,
                'count': len(programs)
            })

        except Exception as e:
            print(f"\n❌ Fehler: {e}")
            all_results.append({
                'foundation': foundation['name'],
                'programs': [],
                'count': 0,
                'error': str(e)
            })

        # Pause zwischen Stiftungen
        if i < len(FOUNDATIONS):
            print(f"\n⏸️ Pause 15 Sekunden...")
            time.sleep(15)

    # Summary
    print("\n" + "=" * 80)
    print("ZUSAMMENFASSUNG")
    print("=" * 80)
    total_programs = sum(r['count'] for r in all_results)

    for result in all_results:
        if 'error' in result:
            print(f"❌ {result['foundation']}: FEHLER")
        else:
            print(f"✅ {result['foundation']}: {result['count']} Programme")

    print(f"\n📊 TOTAL: {total_programs} neue Programme gefunden")

    return 0

if __name__ == '__main__':
    exit(main())
