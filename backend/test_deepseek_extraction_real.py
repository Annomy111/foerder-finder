#!/usr/bin/env python3
"""
Test DeepSeek LLM-Extraktion mit echtem API-Key
"""

import json
import requests
from dotenv import load_dotenv
import os

load_dotenv()

SAMPLE_TEXT = """
Robert Bosch Stiftung

Die Robert Bosch Stiftung fördert Bildungsprojekte an Grundschulen in ganz Deutschland.

Förderbereiche:
- MINT-Bildung
- Digitale Bildung
- Demokratiebildung

Zielgruppen:
- Grundschulen
- Sekundarstufe I

Fördersummen:
Zwischen 10.000 und 50.000 Euro pro Projekt

Bewerbungsfrist: Laufend

Kontakt:
Email: foerderung@bosch-stiftung.de
Telefon: +49 711 46084-0

Standort: Stuttgart, Baden-Württemberg

Anforderungen:
- Projektskizze (max. 5 Seiten)
- Finanzierungsplan
- Nachweis Gemeinnützigkeit
"""

LLM_PROMPT = """Analysiere diesen Text über eine Stiftung und extrahiere strukturierte Informationen.

Gib die Daten als valides JSON zurück:
{
    "name": "Name der Stiftung",
    "beschreibung": "Kurzbeschreibung (max 300 Zeichen)",
    "foerderbereiche": ["Bildung", "MINT"],
    "foerdersumme_min": 10000,
    "foerdersumme_max": 50000,
    "zielgruppen": ["Grundschule"],
    "bewerbungsfrist": "laufend",
    "kontakt_email": "...",
    "kontakt_telefon": "...",
    "bundesland": "Baden-Württemberg",
    "stadt": "Stuttgart",
    "anforderungen": ["Projektskizze", "Budget"]
}

WICHTIG: Nur valides JSON ohne Markdown-Formatierung!"""

def test_extraction():
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ DEEPSEEK_API_KEY nicht in .env!")
        return
    
    print(f"🤖 Teste DeepSeek mit API-Key: {api_key[:10]}...\n")

    try:
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": LLM_PROMPT},
                    {"role": "user", "content": SAMPLE_TEXT}
                ],
                "temperature": 0.3,
                "max_tokens": 1500
            },
            timeout=30
        )

        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            extracted = result['choices'][0]['message']['content']
            
            print("\n✅ LLM-Response:\n")
            print("="*70)
            print(extracted)
            print("="*70)
            
            # Parse JSON
            try:
                # Remove markdown code blocks if present
                if "```json" in extracted:
                    start = extracted.find("```json") + 7
                    end = extracted.find("```", start)
                    extracted = extracted[start:end].strip()
                elif "```" in extracted:
                    start = extracted.find("```") + 3
                    end = extracted.find("```", start)
                    extracted = extracted[start:end].strip()
                
                data = json.loads(extracted)
                print("\n✅ JSON erfolgreich geparst:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                
            except json.JSONDecodeError as e:
                print(f"\n⚠️ JSON-Parsing fehlgeschlagen: {e}")
        else:
            print(f"❌ API Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_extraction()
