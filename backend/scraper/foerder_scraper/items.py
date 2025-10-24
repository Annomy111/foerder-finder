"""
Scrapy Items für Fördermittel-Daten
"""

import scrapy


class FundingItem(scrapy.Item):
    """Item-Definition für eine Fördermittel-Ausschreibung"""

    # Pflichtfelder
    title = scrapy.Field()  # Titel der Ausschreibung
    source_url = scrapy.Field()  # URL der Quelle (eindeutiger Schlüssel)
    cleaned_text = scrapy.Field()  # Bereinigter Text für RAG (WICHTIG!)

    # Optionale strukturierte Felder
    deadline = scrapy.Field()  # Frist (wird zu TIMESTAMP normalisiert)
    provider = scrapy.Field()  # Fördergeber (BMBF, Land, etc.)
    region = scrapy.Field()  # Region (Bundesweit, Brandenburg, etc.)
    funding_area = scrapy.Field()  # Bereich (Digitalisierung, Sport, etc.)

    # Finanzielle Informationen
    min_funding_amount = scrapy.Field()  # Minimale Fördersumme
    max_funding_amount = scrapy.Field()  # Maximale Fördersumme

    # Metadaten
    tags = scrapy.Field()  # Liste von Tags/Keywords
    metadata_json = scrapy.Field()  # JSON mit allen weiteren Daten
    scraped_at = scrapy.Field()  # Zeitstempel des Scrapings
