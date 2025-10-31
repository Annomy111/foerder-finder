#!/usr/bin/env python3
"""
LLM-based Information Extraction for Funding Opportunities
Uses DeepSeek API to extract structured data from scraped markdown

Author: Claude Code
Version: 1.0
Date: 2025-10-29
"""

import os
import json
import re
import requests
from typing import Dict, Optional, List
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_API_URL = 'https://api.deepseek.com/v1/chat/completions'

EXTRACTION_PROMPT_TEMPLATE = """
Du bist ein Experte für deutsche Förderprogramme im Bildungsbereich.

Analysiere die folgende Webseite über ein Förderprogramm und extrahiere ALLE verfügbaren Informationen als strukturiertes JSON.

WICHTIGE REGELN:
1. Nutze null wenn eine Information nicht verfügbar ist
2. Beträge IMMER in Euro (numerisch, ohne Währung)
3. Daten im ISO-Format (YYYY-MM-DD) oder als Text ("laufend", "jährlich im Januar")
4. Arrays für Listen
5. Sei SEHR gründlich - extrahiere auch Details aus dem Kleingedruckten
6. KEINE Erfindungen - nur Daten die wirklich im Text stehen
7. Wenn Beträge als Range angegeben sind (z.B. "10.000-15.000 €"), extrahiere Min und Max separat

⚠️ KRITISCHE VALIDIERUNG - STOPPE BEI SCHLECHTEM CONTENT:
8. Wenn der Text NUR Cookie-Banner/GDPR-Hinweise/Datenschutz enthält → Gib {{"title": null}} zurück
9. Wenn der Text eine 404/Fehlerseite/Nicht gefunden-Meldung ist → Gib {{"title": null}} zurück
10. Wenn KEINE konkreten Förderinformationen erkennbar sind → Gib {{"title": null}} zurück
11. Wenn der Text nur Navigation/Menü/Footer ist → Gib {{"title": null}} zurück
12. Ein valides Förderprogramm MUSS mindestens Titel UND entweder Beträge ODER Antragsinfos enthalten

JSON-Schema:
{{
  "title": "Vollständiger Titel des Programms",
  "deadline": "YYYY-MM-DD or 'laufend' or 'jährlich'",
  "min_funding_amount": 5000,
  "max_funding_amount": 50000,
  "eligibility_criteria": ["Wer darf beantragen? Liste alle Voraussetzungen"],
  "target_groups": ["Grundschulen", "Klasse 1-4", "Ganztagsschulen"],
  "region_restrictions": "Bundesweit oder spezifisches Bundesland",
  "evaluation_criteria": ["Wonach wird bewertet? Innovation, Nachhaltigkeit, etc."],
  "requirements": ["Formale Anforderungen: Seitenzahl, Anlagen, Format"],
  "application_process": "Wie stellt man den Antrag? Portal, Email, Post?",
  "application_url": "https://... direkter Link zum Antragsformular",
  "contact_email": "email@example.com",
  "contact_phone": "+49 ...",
  "contact_person": "Name der Ansprechperson",
  "decision_timeline": "Wann wird über Anträge entschieden?",
  "funding_period": "Projektlaufzeit (z.B. '12 Monate', 'Schuljahr 2025/26')",
  "co_financing_required": true/false,
  "co_financing_rate": 0.1,
  "eligible_costs": ["Was ist förderfähig? Personal, Sachmittel, etc."]
}}

TEXT ZUR ANALYSE:
{text}

Gib NUR valides JSON zurück, keine Markdown-Blöcke, keine Erklärungen.
""".strip()


def clean_json_response(text: str) -> str:
    """Remove markdown code blocks from LLM response"""
    text = text.strip()

    # Remove ```json ... ``` blocks
    if '```json' in text:
        start = text.find('```json') + 7
        end = text.find('```', start)
        if end != -1:
            text = text[start:end].strip()
    elif '```' in text:
        start = text.find('```') + 3
        end = text.find('```', start)
        if end != -1:
            text = text[start:end].strip()

    return text.strip()


def extract_with_deepseek(
    markdown_text: str,
    source_name: str,
    max_tokens: int = 2000,
    temperature: float = 0.1
) -> Optional[Dict]:
    """
    Extract structured data using DeepSeek API

    Args:
        markdown_text: Scraped markdown content
        source_name: Name of funding source (for logging)
        max_tokens: Max tokens for response
        temperature: LLM temperature (lower = more deterministic)

    Returns:
        Extracted data as dict or None on error
    """

    if not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY == 'your_key_here_optional':
        print('[ERROR] DEEPSEEK_API_KEY not set in .env')
        return None

    # Truncate text if too long (to fit in context window)
    text_sample = markdown_text[:12000] if len(markdown_text) > 12000 else markdown_text

    prompt = EXTRACTION_PROMPT_TEMPLATE.format(text=text_sample)

    try:
        response = requests.post(
            DEEPSEEK_API_URL,
            headers={
                'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'deepseek-chat',
                'messages': [
                    {
                        'role': 'system',
                        'content': 'Du bist ein präziser Datenextraktor für Förderprogramme.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'temperature': temperature,
                'max_tokens': max_tokens
            },
            timeout=90
        )

        if response.status_code != 200:
            print(f'[ERROR] DeepSeek API returned {response.status_code}: {response.text[:200]}')
            return None

        result = response.json()
        extracted_text = result['choices'][0]['message']['content']

        # Clean and parse JSON
        cleaned = clean_json_response(extracted_text)
        data = json.loads(cleaned)

        print(f'[SUCCESS] Extracted {len(data)} fields for {source_name}')
        return data

    except json.JSONDecodeError as e:
        print(f'[ERROR] JSON parse error for {source_name}: {e}')
        print(f'[DEBUG] Raw response: {extracted_text[:300] if "extracted_text" in locals() else "N/A"}')
        return None

    except Exception as e:
        print(f'[ERROR] Extraction failed for {source_name}: {e}')
        return None


def calculate_quality_score(extracted_data: Dict) -> float:
    """
    Calculate quality score (0.0 - 1.0)

    1.0 = All critical fields present
    0.0 = No structured data

    Args:
        extracted_data: Extracted data dictionary

    Returns:
        Quality score between 0.0 and 1.0
    """

    weights = {
        # Critical fields (60%)
        'deadline': 0.15,
        'min_funding_amount': 0.10,
        'max_funding_amount': 0.10,
        'eligibility_criteria': 0.15,
        'application_url': 0.10,

        # Important fields (30%)
        'evaluation_criteria': 0.08,
        'requirements': 0.08,
        'contact_email': 0.07,
        'funding_period': 0.07,

        # Nice-to-have (10%)
        'eligible_costs': 0.04,
        'contact_person': 0.03,
        'decision_timeline': 0.03
    }

    score = 0.0
    for field, weight in weights.items():
        value = extracted_data.get(field)

        # Check if field is populated
        if value is not None:
            if isinstance(value, list) and len(value) > 0:
                score += weight
            elif isinstance(value, str) and value.strip():
                score += weight
            elif isinstance(value, (int, float)) and value > 0:
                score += weight
            elif isinstance(value, bool):
                score += weight

    return round(score, 2)


def validate_extracted_data(data: Dict) -> Dict:
    """
    Validate and clean extracted data

    Args:
        data: Raw extracted data

    Returns:
        Cleaned data dict
    """

    cleaned = data.copy()

    # Normalize deadline
    if cleaned.get('deadline'):
        deadline = str(cleaned['deadline']).strip()
        deadline_lower = deadline.lower()

        if deadline_lower in ['laufend', 'jährlich', 'rolling', 'annual', 'kontinuierlich']:
            cleaned['deadline'] = deadline_lower
        elif 'jährlich' in deadline_lower or 'annual' in deadline_lower:
            cleaned['deadline'] = deadline
        else:
            # Try to parse as date
            try:
                from datetime import datetime
                # Try different formats
                for fmt in ['%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y']:
                    try:
                        datetime.strptime(deadline, fmt)
                        if fmt != '%Y-%m-%d':
                            # Convert to ISO format
                            dt = datetime.strptime(deadline, fmt)
                            cleaned['deadline'] = dt.strftime('%Y-%m-%d')
                        break
                    except:
                        continue
            except:
                # Keep as-is if can't parse
                pass

    # Validate amounts
    for field in ['min_funding_amount', 'max_funding_amount']:
        if cleaned.get(field):
            try:
                amount = float(cleaned[field])
                if amount < 0:
                    print(f'[WARN] Negative amount for {field}: {amount}')
                    cleaned[field] = None
                elif amount > 100_000_000:  # 100M seems unreasonable
                    print(f'[WARN] Suspiciously high amount for {field}: {amount}')
                    cleaned[field] = None
                else:
                    cleaned[field] = amount
            except:
                cleaned[field] = None

    # Ensure min <= max
    min_amt = cleaned.get('min_funding_amount')
    max_amt = cleaned.get('max_funding_amount')
    if min_amt and max_amt and min_amt > max_amt:
        print(f'[WARN] Min ({min_amt}) > Max ({max_amt}), swapping')
        cleaned['min_funding_amount'] = max_amt
        cleaned['max_funding_amount'] = min_amt

    # Validate email
    if cleaned.get('contact_email'):
        email = cleaned['contact_email'].strip()
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            print(f'[WARN] Invalid email: {email}')
            cleaned['contact_email'] = None

    # Validate URL
    if cleaned.get('application_url'):
        url = cleaned['application_url'].strip()
        if not url.startswith(('http://', 'https://')):
            print(f'[WARN] Invalid URL: {url}')
            cleaned['application_url'] = None

    # Validate co-financing rate
    if cleaned.get('co_financing_rate'):
        rate = cleaned['co_financing_rate']
        try:
            rate = float(rate)
            if rate < 0 or rate > 1:
                print(f'[WARN] Co-financing rate out of range (0-1): {rate}')
                cleaned['co_financing_rate'] = None
            else:
                cleaned['co_financing_rate'] = rate
        except:
            cleaned['co_financing_rate'] = None

    # Ensure lists are actually lists
    for field in ['eligibility_criteria', 'target_groups', 'evaluation_criteria',
                  'requirements', 'eligible_costs']:
        if field in cleaned and cleaned[field] is not None:
            if not isinstance(cleaned[field], list):
                # Convert to list
                if isinstance(cleaned[field], str):
                    cleaned[field] = [cleaned[field]]
                else:
                    cleaned[field] = []

    return cleaned


def extract_from_funding_opportunity(funding_id: str, cleaned_text: str, db_cursor) -> Optional[Dict]:
    """
    Extract structured data from a funding opportunity's cleaned_text

    Args:
        funding_id: ID of funding opportunity
        cleaned_text: Markdown text from database
        db_cursor: Database cursor for updates

    Returns:
        Extracted and validated data or None
    """

    if not cleaned_text or len(cleaned_text) < 100:
        print(f'[SKIP] {funding_id}: No cleaned_text or too short')
        return None

    # Extract
    extracted = extract_with_deepseek(cleaned_text, funding_id)

    if not extracted:
        return None

    # Validate
    validated = validate_extracted_data(extracted)

    # Calculate quality
    quality_score = calculate_quality_score(validated)
    validated['extraction_quality_score'] = quality_score

    print(f'[QUALITY] {funding_id}: Score = {quality_score}')

    return validated


# Main function for testing
if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print('Usage: python llm_extractor.py <markdown_file>')
        print('Example: python llm_extractor.py test_data/telekom_stiftung.md')
        sys.exit(1)

    # Read markdown file
    try:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            markdown = f.read()
    except FileNotFoundError:
        print(f'[ERROR] File not found: {sys.argv[1]}')
        sys.exit(1)

    print(f'[INFO] Extracting from {sys.argv[1]}...')
    print(f'[INFO] Text length: {len(markdown)} characters')
    print('')

    # Extract
    data = extract_with_deepseek(markdown, os.path.basename(sys.argv[1]))

    if data:
        # Validate
        validated = validate_extracted_data(data)

        # Calculate quality
        quality = calculate_quality_score(validated)

        print(f'\n{"="*80}')
        print(f'EXTRACTION RESULT')
        print(f'{"="*80}')
        print(f'\nQuality Score: {quality}')
        print(f'\n{json.dumps(validated, indent=2, ensure_ascii=False)}')
        print(f'\n{"="*80}')
    else:
        print('\n[FAILED] Extraction failed')
        sys.exit(1)
