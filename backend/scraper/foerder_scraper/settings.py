"""
Scrapy Settings für Förder-Scraper
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Scrapy Project Settings
BOT_NAME = 'foerder_scraper'
SPIDER_MODULES = ['foerder_scraper.spiders']
NEWSPIDER_MODULE = 'foerder_scraper.spiders'

# Crawl responsibly
ROBOTSTXT_OBEY = True
USER_AGENT = os.getenv('SCRAPER_USER_AGENT', 'Mozilla/5.0 (compatible; FoerderFinderBot/1.0)')

# Configure maximum concurrent requests
CONCURRENT_REQUESTS = int(os.getenv('SCRAPER_CONCURRENT_REQUESTS', 8))
CONCURRENT_REQUESTS_PER_DOMAIN = 2

# Configure a delay for requests (in seconds)
DOWNLOAD_DELAY = float(os.getenv('SCRAPER_DELAY', 2.0))
RANDOMIZE_DOWNLOAD_DELAY = True

# AutoThrottle - automatische Drosselung
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0

# Cookies und Session
COOKIES_ENABLED = True

# Retry Settings
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# Timeout
DOWNLOAD_TIMEOUT = 30

# Item Pipelines
# Die Reihenfolge ist wichtig! (niedrigere Nummer = früher)
ITEM_PIPELINES = {
    'foerder_scraper.pipelines.DuplicatesPipeline': 100,
    'foerder_scraper.pipelines.CleaningPipeline': 200,
    'foerder_scraper.pipelines.OracleWriterPipeline': 300,
}

# Downloader Middlewares (für Proxy)
DOWNLOADER_MIDDLEWARES = {
    'foerder_scraper.middlewares.BrightDataProxyMiddleware': 350,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 400,
}

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = '/var/log/foerder-scraper.log'  # Nur auf OCI VM

# Request Fingerprinter (für Duplikatserkennung)
REQUEST_FINGERPRINTER_IMPLEMENTATION = '2.7'

# Twisted Reactor
TWISTED_REACTOR = 'twisted.internet.asyncioreactor.AsyncioSelectorReactor'

# Feed Export (optional - für Debugging)
FEEDS = {
    # 'output/%(name)s_%(time)s.json': {
    #     'format': 'json',
    #     'encoding': 'utf8',
    #     'indent': 4,
    # },
}
