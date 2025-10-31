#!/usr/bin/env python3
"""
Quick Crawl4AI Test Script
Tests 3 sample URLs and compares with Firecrawl baseline
"""

import asyncio
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from scraper_firecrawl.llm_extractor import extract_with_deepseek, validate_extracted_data


# Test URLs (TIER 1 top performers)
TEST_URLS = [
    {
        'url': 'https://www.bosch-stiftung.de/de/projekt/wirlernen',
        'name': 'Robert Bosch Stiftung - wirlernen'
    },
    {
        'url': 'https://mbjs-fachportal.brandenburg.de/bildung/infos-fuer-schulen/startchancen-programm-schulen-saeulen-ii-und-iii.html',
        'name': 'Brandenburg - Startchancen'
    },
    {
        'url': 'https://erasmusplus.schule/foerderung',
        'name': 'Erasmus+ - Förderung'
    }
]


async def test_crawl4ai():
    """Test Crawl4AI on sample URLs"""

    print('=' * 80)
    print('CRAWL4AI QUICK TEST')
    print('=' * 80)
    print(f'Started: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'Testing {len(TEST_URLS)} URLs\n')

    results = []

    # Configure crawler
    config = CrawlerRunConfig(
        # Content extraction
        only_text=False,  # We want markdown
        remove_overlay_elements=True,  # Remove cookie banners, modals
        excluded_tags=['nav', 'footer', 'aside', 'header'],
        exclude_external_links=True,

        # JavaScript handling
        wait_until='domcontentloaded',
        delay_before_return_html=2.0,  # 2 seconds wait for dynamic content

        # Cache (disable for testing)
        cache_mode=CacheMode.BYPASS,

        # Anti-detection
        simulate_user=True,
        override_navigator=True
    )

    async with AsyncWebCrawler(headless=True, verbose=False) as crawler:
        for test in TEST_URLS:
            print(f'\n[TEST] {test["name"]}')
            print(f'[URL]  {test["url"]}')

            try:
                # Scrape with Crawl4AI
                start_time = datetime.now()
                result = await crawler.arun(
                    url=test['url'],
                    config=config
                )
                scrape_time = (datetime.now() - start_time).total_seconds()

                if not result.success:
                    print(f'[FAIL] Scrape failed: {result.error_message}')
                    results.append({
                        'url': test['url'],
                        'name': test['name'],
                        'success': False,
                        'error': result.error_message
                    })
                    continue

                # Get markdown (new API: result.markdown returns MarkdownGenerationResult)
                markdown = result.markdown.raw_markdown
                markdown_length = len(markdown)

                print(f'[SUCCESS] Scraped in {scrape_time:.2f}s')
                print(f'[MARKDOWN] Length: {markdown_length} chars')
                print(f'[PREVIEW] First 200 chars:')
                print(f'  {markdown[:200]}...\n')

                # Test LLM extraction
                if markdown_length > 100:
                    print(f'[LLM] Extracting with DeepSeek...')
                    llm_start = datetime.now()
                    extracted = extract_with_deepseek(markdown, test['name'])
                    llm_time = (datetime.now() - llm_start).total_seconds()

                    if extracted:
                        validated = validate_extracted_data(extracted)

                        # Check if bad content detected
                        if validated.get('title') is None:
                            print(f'[LLM] ❌ Bad content detected (Cookie/404/No funding)')
                            llm_success = False
                            title = None
                        else:
                            title = validated.get('title', 'N/A')
                            print(f'[LLM] ✅ Extracted in {llm_time:.2f}s')
                            print(f'[LLM] Title: {title}')
                            print(f'[LLM] Deadline: {validated.get("deadline", "N/A")}')
                            print(f'[LLM] Amount: {validated.get("min_funding_amount", "N/A")}')
                            llm_success = True
                    else:
                        print(f'[LLM] ⚠️ Extraction failed')
                        llm_success = False
                        title = None
                else:
                    print(f'[LLM] ⏭️ Skipped (markdown too short)')
                    llm_success = False
                    title = None

                results.append({
                    'url': test['url'],
                    'name': test['name'],
                    'success': True,
                    'scrape_time': scrape_time,
                    'markdown_length': markdown_length,
                    'llm_success': llm_success,
                    'title': title
                })

            except Exception as e:
                print(f'[ERROR] {e}')
                import traceback
                traceback.print_exc()
                results.append({
                    'url': test['url'],
                    'name': test['name'],
                    'success': False,
                    'error': str(e)
                })

    # Print summary
    print('\n' + '=' * 80)
    print('TEST SUMMARY')
    print('=' * 80)

    successful_scrapes = sum(1 for r in results if r.get('success'))
    successful_llm = sum(1 for r in results if r.get('llm_success'))
    total_time = sum(r.get('scrape_time', 0) for r in results)

    print(f'Total URLs tested: {len(results)}')
    print(f'Successful scrapes: {successful_scrapes}/{len(results)}')
    print(f'Successful LLM extractions: {successful_llm}/{len(results)}')
    print(f'Total scrape time: {total_time:.2f}s')
    print(f'Average per URL: {total_time/len(results) if results else 0:.2f}s')

    print('\nDetailed Results:')
    for r in results:
        status = '✅' if r.get('success') else '❌'
        llm_status = '✅' if r.get('llm_success') else '❌'
        title = r.get('title', 'N/A')
        time = r.get('scrape_time', 0)
        print(f'{status} {llm_status} {r["name"][:40]:40s} | {time:.1f}s | {title[:40] if title else "FAILED"}')

    print('\n' + '=' * 80)

    return results


if __name__ == '__main__':
    asyncio.run(test_crawl4ai())
