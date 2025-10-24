"""
BMBF Spider - Beispiel-Spider für Bundesministerium für Bildung und Forschung
WICHTIG: Dies ist ein Template. Die tatsächlichen URLs und Selektoren müssen
an die echten Zielseiten angepasst werden!
"""

import scrapy
from foerder_scraper.items import FundingItem


class BMBFSpider(scrapy.Spider):
    """
    Spider für BMBF Fördermittel
    Scrapt Ausschreibungen für Schulen vom BMBF
    """

    name = 'bmbf'
    allowed_domains = ['bmbf.de']

    # WICHTIG: Diese URLs sind Platzhalter!
    # Echte URLs müssen recherchiert werden
    start_urls = [
        'https://www.bmbf.de/bmbf/de/forschung/bildung/foerderungen/foerderungen_node.html',
    ]

    custom_settings = {
        'DOWNLOAD_DELAY': 3,  # Höflich sein bei Behörden-Websites
    }

    def parse(self, response):
        """
        Parse die Übersichtsseite und folge Links zu einzelnen Ausschreibungen
        """
        # BEISPIEL: Selektoren müssen angepasst werden!
        for funding_link in response.css('div.funding-item a::attr(href)').getall():
            yield response.follow(funding_link, callback=self.parse_funding)

        # Pagination (falls vorhanden)
        next_page = response.css('a.next-page::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_funding(self, response):
        """
        Parse eine einzelne Förderausschreibung
        """
        item = FundingItem()

        # BEISPIEL: Selektoren müssen an echte Website angepasst werden!
        item['title'] = response.css('h1.title::text').get()
        item['source_url'] = response.url

        # Extrahiere den Haupttext (alle Absätze)
        paragraphs = response.css('div.content p::text').getall()
        item['cleaned_text'] = ' '.join(paragraphs)

        # Deadline (Beispiel-Selektor)
        deadline_text = response.css('span.deadline::text').get()
        if deadline_text:
            item['deadline'] = deadline_text

        # Provider
        item['provider'] = 'BMBF'
        item['region'] = 'Bundesweit'

        # Extrahiere weitere Metadaten
        metadata = {
            'raw_html': response.text[:5000],  # Erste 5000 Zeichen
            'contact': response.css('div.contact::text').get(),
        }
        item['metadata_json'] = metadata

        # Tags (Beispiel)
        tags = response.css('span.tag::text').getall()
        item['tags'] = tags

        yield item


class DigitalPaktSpider(scrapy.Spider):
    """
    Spider für DigitalPakt Schule Ausschreibungen
    """

    name = 'digitalpakt'
    allowed_domains = ['digitalpaktschule.de']

    start_urls = [
        'https://www.digitalpaktschule.de/foerderung',
    ]

    def parse(self, response):
        """Parse DigitalPakt Seiten"""
        item = FundingItem()

        item['title'] = response.css('h1::text').get()
        item['source_url'] = response.url
        item['cleaned_text'] = ' '.join(response.css('article p::text').getall())
        item['provider'] = 'DigitalPakt Schule'
        item['region'] = 'Bundesweit'
        item['funding_area'] = 'Digitalisierung'
        item['tags'] = ['Digital', 'Infrastruktur']

        yield item


class BrandenburgSpider(scrapy.Spider):
    """
    Spider für Fördermittel des Landes Brandenburg
    """

    name = 'brandenburg'
    allowed_domains = ['brandenburg.de']

    start_urls = [
        'https://mbjs.brandenburg.de/bildung/schulen/foerderung.html',
    ]

    def parse(self, response):
        """Parse Brandenburg Förderprogramme"""
        # Beispiel-Implementation
        for section in response.css('div.funding-section'):
            item = FundingItem()

            item['title'] = section.css('h3::text').get()
            item['source_url'] = response.url
            item['cleaned_text'] = ' '.join(section.css('p::text').getall())
            item['provider'] = 'Land Brandenburg'
            item['region'] = 'Brandenburg'

            yield item


class AllFundingSpider(scrapy.Spider):
    """
    Meta-Spider der alle anderen Spiders aufruft
    Nützlich für cronjob: scrapy crawl all_spiders
    """

    name = 'all_spiders'

    def start_requests(self):
        """Startet alle verfügbaren Spiders"""
        spiders = [BMBFSpider, DigitalPaktSpider, BrandenburgSpider]

        for spider_class in spiders:
            spider = spider_class()
            for url in spider.start_urls:
                yield scrapy.Request(
                    url,
                    callback=spider.parse,
                    meta={'spider_name': spider.name}
                )
