"""
Scrapy Middlewares
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from scrapy import signals
from utils.oci_secrets import get_brightdata_proxy


class BrightDataProxyMiddleware:
    """
    Middleware für Bright Data Rotating Proxies
    Verhindert IP-Blockaden beim Scraping
    """

    def __init__(self):
        self.proxy_url = None

    @classmethod
    def from_crawler(cls, crawler):
        # Initialisiere Middleware mit Crawler-Signals
        middleware = cls()
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        return middleware

    def spider_opened(self, spider):
        """Wird beim Start des Spiders aufgerufen"""
        try:
            # Hole Proxy-URL aus OCI Vault
            self.proxy_url = get_brightdata_proxy()
            spider.logger.info('Bright Data Proxy erfolgreich geladen')
        except Exception as e:
            spider.logger.warning(f'Proxy konnte nicht geladen werden: {e}')
            spider.logger.warning('Fahre ohne Proxy fort (nur für Testing!)')

    def process_request(self, request, spider):
        """Setzt Proxy für jeden Request"""
        if self.proxy_url:
            request.meta['proxy'] = self.proxy_url
            spider.logger.debug(f'Proxy gesetzt für: {request.url}')
        return None


class RandomUserAgentMiddleware:
    """
    Middleware für rotierende User Agents
    Ergänzung zu Bright Data Proxies
    """

    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    ]

    def process_request(self, request, spider):
        """Setzt zufälligen User Agent"""
        import random
        request.headers['User-Agent'] = random.choice(self.USER_AGENTS)
        return None
