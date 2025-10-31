#!/usr/bin/env python3
"""
Firecrawl-Based Scraper for Förder-Finder
Replaces Scrapy with AI-powered semantic scraping

Features:
- Self-hosted Firecrawl integration (VM 130.61.137.77:3002)
- LLM-ready markdown extraction
- Schema-based structured data extraction
- Automatic retry and error handling
"""

import os
import sys
import time
import uuid
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from scraper_firecrawl.funding_sources import ALL_SOURCES, FundingSource
from scraper_firecrawl.llm_extractor import extract_with_deepseek, validate_extracted_data
from utils.db_adapter import get_db_cursor

load_dotenv()


class FirecrawlScraper:
    """Firecrawl-based scraper for funding opportunities"""

    def __init__(self):
        """Initialize Firecrawl scraper"""
        self.firecrawl_url = os.getenv(
            'FIRECRAWL_API_URL',
            'http://130.61.137.77:3002'
        )
        self.firecrawl_api_key = os.getenv('FIRECRAWL_API_KEY', 'self-hosted')

        # Request headers
        self.headers = {
            'Content-Type': 'application/json'
        }
        if self.firecrawl_api_key != 'self-hosted':
            self.headers['Authorization'] = f'Bearer {self.firecrawl_api_key}'

        print(f'[INFO] Firecrawl URL: {self.firecrawl_url}')
        print(f'[INFO] API Key: {"self-hosted" if self.firecrawl_api_key == "self-hosted" else "***"}')

        # Retry configuration
        self.max_retries = 3
        self.retry_delay = 5  # seconds

    def scrape_url(
        self,
        url: str,
        extract_schema: Optional[Dict] = None,
        only_main_content: bool = True
    ) -> Dict[str, Any]:
        """
        Scrape a single URL with Firecrawl

        Args:
            url: URL to scrape
            extract_schema: Optional schema for structured data extraction
            only_main_content: Extract only main content (skip nav, footer)

        Returns:
            Dict with 'markdown' and optionally 'extracted_data'
        """
        print(f'[INFO] Scraping URL: {url}')

        for attempt in range(self.max_retries):
            try:
                if extract_schema:
                    # Try /extract endpoint for structured data
                    # Note: This might not be available in self-hosted versions
                    try:
                        response = requests.post(
                            f'{self.firecrawl_url}/v1/extract',
                            headers=self.headers,
                            json={
                                'url': url,
                                'schema': extract_schema,
                                'onlyMainContent': only_main_content
                            },
                            timeout=60
                        )
                        response.raise_for_status()
                        data = response.json()
                        print(f'[SUCCESS] Extracted structured data from {url}')
                        return data
                    except (requests.exceptions.RequestException, KeyError):
                        # Fall back to markdown-only scraping
                        print(f'[INFO] Extract endpoint failed, falling back to markdown scraping for {url}')
                        extract_schema = None
                        # Continue to markdown scraping below

                # Use /scrape endpoint for markdown
                response = requests.post(
                    f'{self.firecrawl_url}/v1/scrape',
                    headers=self.headers,
                    json={
                        'url': url,
                        'formats': ['markdown'],
                        'onlyMainContent': only_main_content,
                        'removeTags': ['*cookie*', '*gdpr*', '*cmplz*', '*banner*', '*consent*', '*popup*'],
                        'waitFor': 2000,
                        'timeout': 30000
                    },
                    timeout=90
                )

                response.raise_for_status()
                data = response.json()

                print(f'[SUCCESS] Scraped {url}')
                return data

            except requests.exceptions.RequestException as e:
                print(f'[ERROR] Attempt {attempt + 1}/{self.max_retries} failed for {url}: {e}')
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    print(f'[FAILED] Max retries reached for {url}')
                    return {}

        return {}

    def crawl_url(
        self,
        url: str,
        max_pages: int = 50,
        extract_schema: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Crawl a website with Firecrawl (follow links)

        Args:
            url: Starting URL
            max_pages: Maximum pages to crawl
            extract_schema: Optional schema for structured extraction

        Returns:
            List of scraped page data
        """
        print(f'[INFO] Crawling URL: {url} (max {max_pages} pages)')

        payload = {
            'url': url,
            'limit': max_pages,
            'scrapeOptions': {
                'formats': ['markdown'],
                'onlyMainContent': True,
                'removeTags': ['*cookie*', '*gdpr*', '*cmplz*', '*banner*', '*consent*', '*popup*'],
                'waitFor': 2000,
                'timeout': 30000
            }
        }

        if extract_schema:
            payload['scrapeOptions']['extract'] = {'schema': extract_schema}

        try:
            # Start crawl job
            response = requests.post(
                f'{self.firecrawl_url}/v1/crawl',
                headers=self.headers,
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            crawl_data = response.json()

            job_id = crawl_data.get('id')
            if not job_id:
                print(f'[ERROR] No job ID returned from crawl: {crawl_data}')
                return []

            print(f'[INFO] Crawl job started: {job_id}')

            # Poll for completion
            max_wait = 600  # 10 minutes
            start_time = time.time()

            while time.time() - start_time < max_wait:
                status_response = requests.get(
                    f'{self.firecrawl_url}/v1/crawl/{job_id}',
                    headers=self.headers,
                    timeout=30
                )
                status_response.raise_for_status()
                status_data = status_response.json()

                status = status_data.get('status')
                print(f'[INFO] Crawl status: {status}')

                if status == 'completed':
                    pages = status_data.get('data', [])
                    print(f'[SUCCESS] Crawl completed: {len(pages)} pages')
                    return pages

                elif status == 'failed':
                    print(f'[ERROR] Crawl failed: {status_data}')
                    return []

                # Wait before next poll
                time.sleep(5)

            print(f'[TIMEOUT] Crawl did not complete within {max_wait}s')
            return []

        except requests.exceptions.RequestException as e:
            print(f'[ERROR] Crawl failed for {url}: {e}')
            return []

    def process_source(self, source: FundingSource) -> List[Dict[str, Any]]:
        """
        Process a funding source (scrape or crawl)

        Args:
            source: FundingSource definition

        Returns:
            List of extracted funding opportunities
        """
        print(f'\n[START] Processing source: {source.name}')

        all_results = []

        for url in source.urls:
            if source.crawl:
                # Crawl entire site
                pages = self.crawl_url(url, max_pages=50, extract_schema=source.schema)
                for page in pages:
                    result = self._parse_page_data(page, source)
                    if result:
                        all_results.append(result)
            else:
                # Single page scrape
                page_data = self.scrape_url(url, extract_schema=source.schema)
                result = self._parse_page_data(page_data, source)
                if result:
                    all_results.append(result)

        print(f'[INFO] Extracted {len(all_results)} opportunities from {source.name}')
        return all_results

    def _parse_page_data(
        self,
        page_data: Dict[str, Any],
        source: FundingSource
    ) -> Optional[Dict[str, Any]]:
        """
        Parse Firecrawl page data into funding opportunity format

        Args:
            page_data: Raw Firecrawl response
            source: Source definition

        Returns:
            Parsed funding opportunity dict or None
        """
        if not page_data or not page_data.get('success'):
            return None

        # Extract data from response
        data = page_data.get('data', {})

        # Extract markdown content
        markdown = data.get('markdown', '')
        if not markdown or len(markdown) < 50:
            return None

        # Extract structured data (if available)
        extracted = data.get('extract', {})
        metadata = data.get('metadata', {})

        # Use LLM to extract structured data from markdown
        print(f'[LLM] Extracting from {source.name}...')
        llm_extracted = extract_with_deepseek(markdown, source.name)
        if llm_extracted:
            llm_validated = validate_extracted_data(llm_extracted)

            # Check if LLM returned null title (bad content detected)
            if llm_validated.get('title') is None:
                print(f'[LLM] ❌ Bad content detected (Cookie/404/No funding info) - Skipping')
                return None

            # Merge LLM data with Firecrawl extract (LLM takes priority)
            for key, value in llm_validated.items():
                if value is not None:
                    extracted[key] = value
            print(f'[LLM] ✅ Extracted title: {extracted.get("title", "N/A")}')
        else:
            print(f'[LLM] ⚠️  Extraction failed, using fallback')

        # Build funding opportunity
        funding = {
            'title': extracted.get('title', 'Unbekannt'),
            'source_url': metadata.get('url', metadata.get('sourceURL', '')),
            'cleaned_text': markdown,  # LLM-ready markdown!
            'provider': source.provider,
            'region': source.region,
            'funding_area': source.funding_area,
            'deadline': extracted.get('deadline'),
            'min_funding_amount': self._parse_amount(extracted.get('funding_amount')),
            'max_funding_amount': None,  # Could parse from funding_amount range
            'tags': self._extract_tags(extracted),
            'metadata_json': {
                'extracted_data': extracted,
                'source_name': source.name,
                'scraped_with': 'Firecrawl',
                'scrape_timestamp': datetime.now().isoformat()
            }
        }

        return funding

    def _parse_amount(self, amount_str: Optional[str]) -> Optional[float]:
        """Parse funding amount from string"""
        if not amount_str:
            return None

        try:
            # Remove common currency symbols and formatting
            cleaned = amount_str.replace('€', '').replace('EUR', '').replace('.', '').replace(',', '.')
            cleaned = ''.join(c for c in cleaned if c.isdigit() or c == '.')
            return float(cleaned) if cleaned else None
        except (ValueError, AttributeError):
            return None

    def _extract_tags(self, extracted_data: Dict) -> List[str]:
        """Extract tags from structured data"""
        tags = []

        # Add funding area as tag
        if 'focus_area' in extracted_data:
            tags.append(extracted_data['focus_area'])

        if 'project_types' in extracted_data:
            types = extracted_data['project_types']
            if isinstance(types, list):
                tags.extend(types)
            elif isinstance(types, str):
                tags.append(types)

        return tags[:10]  # Limit to 10 tags

    def save_to_database(self, funding_opportunities: List[Dict[str, Any]]) -> int:
        """
        Save funding opportunities to database (Oracle or SQLite)

        Args:
            funding_opportunities: List of funding dicts

        Returns:
            Number of records inserted
        """
        if not funding_opportunities:
            print('[INFO] No opportunities to save')
            return 0

        print(f'[INFO] Saving {len(funding_opportunities)} opportunities to database...')

        insert_count = 0
        with get_db_cursor() as cursor:
            for funding in funding_opportunities:
                try:
                    # Check if already exists (by source_url)
                    cursor.execute(
                        "SELECT COUNT(*) FROM FUNDING_OPPORTUNITIES WHERE source_url = :url",
                        {'url': funding['source_url']}
                    )
                    exists = cursor.fetchone()[0] > 0

                    if exists:
                        # Update existing
                        cursor.execute("""
                            UPDATE FUNDING_OPPORTUNITIES
                            SET title = :title,
                                cleaned_text = :cleaned_text,
                                provider = :provider,
                                region = :region,
                                funding_area = :funding_area,
                                deadline = :deadline,
                                min_funding_amount = :min_amount,
                                max_funding_amount = :max_amount,
                                metadata_json = :metadata,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE source_url = :url
                        """, {
                            'title': funding['title'],
                            'cleaned_text': funding['cleaned_text'],
                            'provider': funding['provider'],
                            'region': funding['region'],
                            'funding_area': funding['funding_area'],
                            'deadline': funding.get('deadline'),
                            'min_amount': funding.get('min_funding_amount'),
                            'max_amount': funding.get('max_funding_amount'),
                            'metadata': str(funding.get('metadata_json', {})),
                            'url': funding['source_url']
                        })
                        print(f'[UPDATE] {funding["title"][:50]}...')
                    else:
                        # Insert new
                        funding_id = str(uuid.uuid4()).replace('-', '').upper()
                        cursor.execute("""
                            INSERT INTO FUNDING_OPPORTUNITIES (
                                funding_id, title, source_url, cleaned_text,
                                provider, region, funding_area,
                                deadline, min_funding_amount, max_funding_amount,
                                metadata_json, last_scraped
                            ) VALUES (
                                :funding_id, :title, :url, :cleaned_text,
                                :provider, :region, :funding_area,
                                :deadline, :min_amount, :max_amount,
                                :metadata, CURRENT_TIMESTAMP
                            )
                        """, {
                            'funding_id': funding_id,
                            'title': funding['title'],
                            'url': funding['source_url'],
                            'cleaned_text': funding['cleaned_text'],
                            'provider': funding['provider'],
                            'region': funding['region'],
                            'funding_area': funding['funding_area'],
                            'deadline': funding.get('deadline'),
                            'min_amount': funding.get('min_funding_amount'),
                            'max_amount': funding.get('max_funding_amount'),
                            'metadata': str(funding.get('metadata_json', {}))
                        })
                        print(f'[INSERT] {funding["title"][:50]}...')
                        insert_count += 1

                except Exception as e:
                    print(f'[ERROR] Failed to save {funding.get("title", "Unknown")}: {e}')
                    import traceback
                    traceback.print_exc()

        print(f'[SUCCESS] Saved {insert_count} new opportunities')
        return insert_count

    def run_all(self) -> None:
        """Run scraper for all configured sources"""
        print('[START] Firecrawl Scraper - Förder-Finder')
        print(f'[INFO] Processing {len(ALL_SOURCES)} sources')

        start_time = datetime.now()
        all_opportunities = []

        for source in ALL_SOURCES:
            opportunities = self.process_source(source)
            all_opportunities.extend(opportunities)

        # Save to database
        self.save_to_database(all_opportunities)

        # Stats
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print(f'\n[COMPLETE] Scraping finished!')
        print(f'[STATS] Total opportunities: {len(all_opportunities)}')
        print(f'[STATS] Duration: {duration:.2f} seconds')


def main():
    """Main entry point"""
    scraper = FirecrawlScraper()
    scraper.run_all()


if __name__ == '__main__':
    main()
