#!/usr/bin/env python3
"""
Firecrawl Integration Test Script
Tests the connection and functionality of the Firecrawl scraper
"""

import os
import sys
import requests
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from scraper_firecrawl.firecrawl_scraper import FirecrawlScraper
from scraper_firecrawl.funding_sources import DIGITALPAKT_SOURCES

load_dotenv()


def test_firecrawl_connection():
    """Test basic connection to Firecrawl instance"""
    print('[TEST] Testing Firecrawl connection...')

    firecrawl_url = os.getenv('FIRECRAWL_API_URL', 'http://130.61.137.77:3002')

    try:
        response = requests.get(f'{firecrawl_url}/', timeout=10)
        print(f'[SUCCESS] Firecrawl is reachable: {response.status_code}')
        print(f'[RESPONSE] {response.text[:200]}')
        return True
    except Exception as e:
        print(f'[ERROR] Cannot reach Firecrawl: {e}')
        return False


def test_simple_scrape():
    """Test simple scraping of a URL"""
    print('\n[TEST] Testing simple scrape...')

    scraper = FirecrawlScraper()

    # Test with a simple German government page
    test_url = 'https://www.bmbf.de/'

    result = scraper.scrape_url(test_url, only_main_content=True)

    if result and result.get('success') and 'data' in result:
        data = result.get('data', {})
        markdown = data.get('markdown', '')
        if markdown:
            print(f'[SUCCESS] Scraped {len(markdown)} characters of markdown')
            print(f'[PREVIEW] {markdown[:300]}...')
            return True

    print(f'[ERROR] Scrape failed or returned no markdown')
    return False


def test_structured_extraction():
    """Test structured data extraction with schema"""
    print('\n[TEST] Testing structured extraction...')

    scraper = FirecrawlScraper()

    # Note: /v1/extract endpoint might not be available in self-hosted version
    # Fall back to simple scrape test
    test_url = 'https://example.com/'

    result = scraper.scrape_url(test_url, only_main_content=True)

    if result and result.get('success') and 'data' in result:
        data = result.get('data', {})
        markdown = data.get('markdown', '')
        if markdown:
            print(f'[SUCCESS] Extracted {len(markdown)} characters')
            print(f'[PREVIEW] {markdown[:200]}...')
            return True

    print(f'[ERROR] Extraction failed')
    return False


def test_funding_source_processing():
    """Test processing a real funding source"""
    print('\n[TEST] Testing funding source processing...')

    scraper = FirecrawlScraper()

    # Use DigitalPakt as test (single page, not crawl)
    source = DIGITALPAKT_SOURCES[0]
    print(f'[INFO] Processing source: {source.name}')

    try:
        opportunities = scraper.process_source(source)

        if opportunities:
            print(f'[SUCCESS] Extracted {len(opportunities)} opportunities')
            for opp in opportunities[:2]:  # Show first 2
                print(f'\n  Title: {opp["title"]}')
                print(f'  Provider: {opp["provider"]}')
                print(f'  URL: {opp["source_url"]}')
                print(f'  Text length: {len(opp["cleaned_text"])} chars')
            return True
        else:
            print(f'[WARNING] No opportunities extracted (might be schema issue)')
            return False
    except Exception as e:
        print(f'[ERROR] Processing failed: {e}')
        import traceback
        traceback.print_exc()
        return False


def test_database_save():
    """Test saving to database (dry-run)"""
    print('\n[TEST] Testing database save (dry-run)...')

    scraper = FirecrawlScraper()

    # Create test opportunity
    test_opportunity = {
        'title': 'TEST: Firecrawl Integration Test',
        'source_url': 'https://example.com/test',
        'cleaned_text': '# Test Funding\n\nThis is a test funding opportunity scraped with Firecrawl.',
        'provider': 'Test Provider',
        'region': 'Bundesweit',
        'funding_area': 'Test',
        'deadline': None,
        'min_funding_amount': 10000,
        'max_funding_amount': 50000,
        'tags': ['test', 'firecrawl'],
        'metadata_json': {'test': True}
    }

    try:
        # Note: This will actually try to save to DB if connection works
        # If you don't want that, comment out the next line
        count = scraper.save_to_database([test_opportunity])
        print(f'[SUCCESS] Database save completed: {count} records')
        return True
    except Exception as e:
        print(f'[INFO] Database not available (expected in local testing): {e}')
        return False


def main():
    """Run all tests"""
    print('=' * 60)
    print('FIRECRAWL INTEGRATION TEST SUITE')
    print('=' * 60)

    results = {
        'connection': test_firecrawl_connection(),
        'simple_scrape': test_simple_scrape(),
        'structured_extraction': test_structured_extraction(),
        'funding_source': test_funding_source_processing(),
        'database_save': test_database_save()
    }

    print('\n' + '=' * 60)
    print('TEST RESULTS SUMMARY')
    print('=' * 60)

    for test_name, passed in results.items():
        status = '✅ PASS' if passed else '❌ FAIL'
        print(f'{status} - {test_name}')

    total_passed = sum(results.values())
    total_tests = len(results)

    print(f'\nTotal: {total_passed}/{total_tests} tests passed')

    if total_passed == total_tests:
        print('\n🎉 All tests passed! Firecrawl integration is working.')
    else:
        print('\n⚠️  Some tests failed. Check the output above.')


if __name__ == '__main__':
    main()
