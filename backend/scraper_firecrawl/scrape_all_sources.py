#!/usr/bin/env python3
"""
Scrape All Funding Sources
Scrapes all configured funding sources and saves to database
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from scraper_firecrawl.firecrawl_scraper import FirecrawlScraper
from scraper_firecrawl.funding_sources import ALL_SOURCES

def main():
    """Scrape all funding sources"""

    print('\n' + '=' * 70)
    print('SCRAPING ALL FUNDING SOURCES')
    print('=' * 70 + '\n')

    scraper = FirecrawlScraper()

    total_scraped = 0
    total_saved = 0

    for i, source in enumerate(ALL_SOURCES, 1):
        print(f'\n[{i}/{len(ALL_SOURCES)}] Processing: {source.name}')
        print(f'  Provider: {source.provider}')
        print(f'  Region: {source.region}')
        print(f'  URLs: {len(source.urls)}')

        try:
            opportunities = scraper.process_source(source)

            if opportunities:
                print(f'  ✅ Extracted: {len(opportunities)} opportunities')

                # Save to database
                saved_count = scraper.save_to_database(opportunities)
                print(f'  ✅ Saved: {saved_count} new opportunities')

                total_scraped += len(opportunities)
                total_saved += saved_count
            else:
                print(f'  ⚠️  No opportunities extracted')

        except Exception as e:
            print(f'  ❌ Error: {e}')
            continue

    print('\n' + '=' * 70)
    print('SCRAPING COMPLETE')
    print('=' * 70)
    print(f'✅ Total opportunities scraped: {total_scraped}')
    print(f'✅ Total new opportunities saved: {total_saved}')
    print('\n')

if __name__ == '__main__':
    main()
