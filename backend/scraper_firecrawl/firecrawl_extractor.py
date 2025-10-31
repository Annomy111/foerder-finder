#!/usr/bin/env python3
"""
Firecrawl /extract Endpoint Integration

BREAKTHROUGH: Nutzt Firecrawls /extract endpoint statt /scrape + DeepSeek
- Ein API-Call statt zwei (schneller, günstiger)
- Firecrawls internes LLM ist für Web-Extraktion trainiert
- Schema-basierte Extraktion ist deterministischer
- onlyMainContent filtert automatisch Navigation/Footer

Erwartete Verbesserung: Quality Score 0.0 → 0.5-0.8

Author: Claude Code
Version: 2.0 (Firecrawl Native)
Date: 2025-10-29
"""

import requests
import logging
from typing import Optional, Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)

FIRECRAWL_URL = "http://130.61.137.77:3002"

# JSON Schema für Förderungsdaten
FUNDING_EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {
            "type": "string",
            "description": "Vollständiger Titel der Förderung"
        },
        "deadline": {
            "type": "string",
            "description": "Bewerbungsfrist im Format YYYY-MM-DD oder 'laufend' oder 'keine Angabe'"
        },
        "min_funding_amount": {
            "type": "number",
            "description": "Minimale Fördersumme in Euro (nur Zahl ohne Währung)"
        },
        "max_funding_amount": {
            "type": "number",
            "description": "Maximale Fördersumme in Euro (nur Zahl ohne Währung)"
        },
        "eligibility_criteria": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Liste der Zulassungskriterien (wer kann sich bewerben?)"
        },
        "target_groups": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Zielgruppen der Förderung (z.B. Grundschulen, Lehrkräfte)"
        },
        "evaluation_criteria": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Bewertungskriterien für Anträge (wonach wird bewertet?)"
        },
        "requirements": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Formale Anforderungen für Antragstellung (notwendige Unterlagen, Fristen)"
        },
        "application_process": {
            "type": "string",
            "description": "Beschreibung des Bewerbungsprozesses (Schritt für Schritt)"
        },
        "application_url": {
            "type": "string",
            "description": "URL zur Bewerbung oder zu weiteren Details"
        },
        "contact_person": {
            "type": "string",
            "description": "Ansprechperson für Rückfragen"
        },
        "contact_email": {
            "type": "string",
            "description": "E-Mail-Adresse für Kontakt"
        },
        "contact_phone": {
            "type": "string",
            "description": "Telefonnummer für Kontakt"
        },
        "decision_timeline": {
            "type": "string",
            "description": "Zeitraum bis zur Entscheidung (z.B. '3 Monate nach Einreichung')"
        },
        "funding_period": {
            "type": "string",
            "description": "Förderzeitraum (z.B. '12 Monate', '2025-2027')"
        },
        "co_financing_required": {
            "type": "boolean",
            "description": "Ist eine Kofinanzierung erforderlich? (true/false)"
        },
        "co_financing_rate": {
            "type": "number",
            "description": "Erforderliche Kofinanzierungsrate in Prozent (z.B. 20 für 20%)"
        },
        "eligible_costs": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Liste förderfähiger Kosten (z.B. Personal, Material, Reisen)"
        }
    },
    "required": []  # Nichts required - wir nehmen was wir bekommen
}


def extract_with_firecrawl(url: str, source_name: str = "Unknown") -> Optional[Dict]:
    """
    Extrahiert strukturierte Förderdaten mit Firecrawl /extract endpoint

    Args:
        url: URL der Webseite
        source_name: Name der Quelle (für Logging)

    Returns:
        Dict mit extrahierten Daten oder None bei Fehler
    """

    try:
        logger.info(f"   🎯 Firecrawl /extract: {source_name}")
        logger.info(f"      URL: {url[:70]}...")

        response = requests.post(
            f"{FIRECRAWL_URL}/v1/extract",
            json={
                "url": url,
                "schema": FUNDING_EXTRACTION_SCHEMA,
                "onlyMainContent": True,  # Filtert Navigation/Footer automatisch
            },
            timeout=90  # /extract kann länger dauern als /scrape
        )

        if response.status_code != 200:
            logger.error(f"      ❌ HTTP Error {response.status_code}")
            logger.error(f"      Response: {response.text[:200]}")
            return None

        data = response.json()

        # Firecrawl /extract response structure:
        # {
        #   "success": true,
        #   "data": { ...extracted fields... }
        # }

        if not data.get('success'):
            logger.warning(f"      ⚠️ Firecrawl returned success=false")
            return None

        extracted_data = data.get('data', {})

        if not extracted_data:
            logger.warning(f"      ⚠️ Keine Daten extrahiert")
            return None

        # Validate and clean
        extracted_data = validate_extracted_data(extracted_data)

        # Calculate quality score
        quality_score = calculate_quality_score(extracted_data)
        extracted_data['extraction_quality_score'] = quality_score

        logger.info(f"      ✅ Quality Score: {quality_score:.2f}")
        logger.info(f"      📊 Felder gefunden: {count_filled_fields(extracted_data)}")

        return extracted_data

    except requests.exceptions.Timeout:
        logger.error(f"      ❌ Timeout nach 90 Sekunden")
        return None

    except Exception as e:
        logger.error(f"      ❌ Exception: {e}")
        return None


def validate_extracted_data(data: Dict) -> Dict:
    """
    Validiert und bereinigt extrahierte Daten

    Args:
        data: Rohdaten von Firecrawl

    Returns:
        Bereinigte und validierte Daten
    """

    validated = {}

    # String fields
    for field in ['title', 'deadline', 'application_process', 'application_url',
                  'contact_person', 'contact_email', 'contact_phone',
                  'decision_timeline', 'funding_period']:
        value = data.get(field)
        if value and isinstance(value, str) and value.strip():
            validated[field] = value.strip()
        else:
            validated[field] = None

    # Numeric fields
    for field in ['min_funding_amount', 'max_funding_amount', 'co_financing_rate']:
        value = data.get(field)
        if value is not None:
            try:
                validated[field] = float(value)
            except (ValueError, TypeError):
                validated[field] = None
        else:
            validated[field] = None

    # Boolean field
    co_financing = data.get('co_financing_required')
    if isinstance(co_financing, bool):
        validated['co_financing_required'] = co_financing
    elif isinstance(co_financing, str):
        validated['co_financing_required'] = co_financing.lower() in ['true', 'yes', 'ja', '1']
    else:
        validated['co_financing_required'] = False

    # Array fields
    for field in ['eligibility_criteria', 'target_groups', 'evaluation_criteria',
                  'requirements', 'eligible_costs']:
        value = data.get(field)
        if value and isinstance(value, list) and len(value) > 0:
            # Filter empty strings
            validated[field] = [str(item).strip() for item in value if item and str(item).strip()]
        else:
            validated[field] = []

    # Validate min <= max
    min_amt = validated.get('min_funding_amount')
    max_amt = validated.get('max_funding_amount')
    if min_amt and max_amt and min_amt > max_amt:
        logger.warning(f"      ⚠️ min > max, tausche: {min_amt} <-> {max_amt}")
        validated['min_funding_amount'] = max_amt
        validated['max_funding_amount'] = min_amt

    # Validate email format
    email = validated.get('contact_email')
    if email and '@' not in email:
        logger.warning(f"      ⚠️ Ungültige E-Mail: {email}")
        validated['contact_email'] = None

    # Normalize deadline
    deadline = validated.get('deadline')
    if deadline:
        deadline_lower = deadline.lower()
        if 'laufend' in deadline_lower or 'rolling' in deadline_lower or 'keine' in deadline_lower:
            validated['deadline'] = 'laufend'

    return validated


def calculate_quality_score(extracted_data: Dict) -> float:
    """
    Berechnet Quality Score (0.0 - 1.0) basierend auf gefüllten Feldern

    Gewichtung:
    - Critical (60%): deadline, min/max_funding_amount, eligibility_criteria, application_url
    - Important (30%): evaluation_criteria, requirements, contact_email
    - Nice-to-have (10%): funding_period, eligible_costs, contact_person

    Args:
        extracted_data: Validierte Daten

    Returns:
        Quality Score zwischen 0.0 und 1.0
    """

    score = 0.0

    # Critical fields (60% total)
    critical_fields = {
        'deadline': 0.15,
        'min_funding_amount': 0.10,
        'max_funding_amount': 0.10,
        'eligibility_criteria': 0.15,
        'application_url': 0.10
    }

    for field, weight in critical_fields.items():
        value = extracted_data.get(field)
        if value:
            if isinstance(value, list) and len(value) > 0:
                score += weight
            elif isinstance(value, (str, int, float)):
                score += weight

    # Important fields (30% total)
    important_fields = {
        'evaluation_criteria': 0.10,
        'requirements': 0.10,
        'contact_email': 0.10
    }

    for field, weight in important_fields.items():
        value = extracted_data.get(field)
        if value:
            if isinstance(value, list) and len(value) > 0:
                score += weight
            elif isinstance(value, (str, int, float)):
                score += weight

    # Nice-to-have fields (10% total)
    nice_fields = {
        'funding_period': 0.03,
        'eligible_costs': 0.04,
        'contact_person': 0.03
    }

    for field, weight in nice_fields.items():
        value = extracted_data.get(field)
        if value:
            if isinstance(value, list) and len(value) > 0:
                score += weight
            elif isinstance(value, (str, int, float)):
                score += weight

    return round(score, 2)


def count_filled_fields(data: Dict) -> int:
    """
    Zählt wie viele Felder gefüllt sind

    Args:
        data: Extrahierte Daten

    Returns:
        Anzahl gefüllter Felder
    """

    count = 0
    for key, value in data.items():
        if key == 'extraction_quality_score':
            continue
        if value:
            if isinstance(value, list) and len(value) > 0:
                count += 1
            elif isinstance(value, (str, int, float, bool)):
                count += 1
    return count


# Test function
if __name__ == '__main__':
    import sys

    logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

    if len(sys.argv) < 2:
        print("Usage: python firecrawl_extractor.py <url> [source_name]")
        print()
        print("Example:")
        print("  python firecrawl_extractor.py https://www.telekom-stiftung.de 'Telekom Stiftung'")
        sys.exit(1)

    test_url = sys.argv[1]
    test_name = sys.argv[2] if len(sys.argv) > 2 else "Test Source"

    print("="*80)
    print("FIRECRAWL /EXTRACT TEST")
    print("="*80)
    print(f"URL: {test_url}")
    print(f"Source: {test_name}")
    print()

    result = extract_with_firecrawl(test_url, test_name)

    print()
    print("="*80)
    print("ERGEBNIS")
    print("="*80)

    if result:
        print(f"✅ Extraktion erfolgreich!")
        print(f"Quality Score: {result.get('extraction_quality_score', 0.0)}")
        print(f"Gefüllte Felder: {count_filled_fields(result)}")
        print()
        print("Extrahierte Daten:")
        for key, value in result.items():
            if key == 'extraction_quality_score':
                continue
            if value:
                if isinstance(value, list):
                    print(f"  {key}: [{len(value)} items]")
                    for item in value[:3]:  # Show first 3
                        print(f"    - {item}")
                    if len(value) > 3:
                        print(f"    ... ({len(value) - 3} more)")
                else:
                    print(f"  {key}: {value}")
    else:
        print("❌ Extraktion fehlgeschlagen")

    print()
    print("="*80)
