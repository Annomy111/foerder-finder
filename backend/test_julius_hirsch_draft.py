#!/usr/bin/env python3
"""
Test AI Draft Generation mit Julius Hirsch Preis

Testet ob:
1. RAG den Julius Hirsch Preis findet
2. AI einen guten Antrag generiert
3. Strukturierte Daten genutzt werden
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import requests
import json

# Test School Data
SCHOOL_DATA = {
    "school_name": "Grundschule Musterberg",
    "school_address": "Musterstraße 123, 12345 Berlin",
    "school_type": "Grundschule",
    "student_count": 250,
    "contact_person": "Frau Schmidt",
    "contact_email": "schmidt@gs-musterberg.de",
    "contact_phone": "030 12345678"
}

# Test Project Request
PROJECT_REQUEST = """
Unsere Grundschule Musterberg in Berlin hat eine Fußball-AG mit 30 Kindern aus den Klassen 3-4.

Im letzten Schuljahr haben wir ein Anti-Rassismus-Projekt durchgeführt:
- Workshops zu Fairplay und Respekt
- Gemeinsame Fußballturniere mit Flüchtlingskindern
- Ausstellung "Fußball verbindet - gegen Diskriminierung"
- Elternabend zum Thema Integration im Sport

Das Projekt läuft seit August 2024 und soll bis Juni 2025 weitergehen.

Wir suchen eine Förderung für:
- Materialien für weitere Workshops
- Trikots für das gemeinsame Team
- Busfahrten zu Begegnungsspielen
- Dokumentation und Öffentlichkeitsarbeit

Gibt es eine passende Fördermöglichkeit?
"""

API_URL = "http://localhost:8000"

# Login credentials for test user
TEST_EMAIL = "admin@gs-musterberg.de"
TEST_PASSWORD = "admin123"  # Default test password

# Julius Hirsch Preis ID (local SQLite)
JULIUS_HIRSCH_ID = "24FDDCF61A8F416BBA6A81083378F5EB"

def get_auth_token():
    """Get JWT token for authentication"""
    try:
        response = requests.post(
            f"{API_URL}/api/v1/auth/login",
            json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            },
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            return data.get('access_token')
        else:
            print(f"❌ Login failed: HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return None
    except Exception as e:
        print(f"❌ Login exception: {e}")
        return None


def test_rag_search():
    """Test 1: Prüfe ob RAG den Julius Hirsch Preis findet"""

    print("="*80)
    print("TEST 1: RAG SEARCH")
    print("="*80)
    print()

    # Get authentication token
    print("🔐 Authenticating...")
    token = get_auth_token()
    if not token:
        print("❌ Could not authenticate - test cannot proceed")
        return False
    print("✅ Authenticated successfully")
    print()

    print("Query: Fußball-AG Anti-Rassismus-Projekt Grundschule")
    print()

    try:
        response = requests.post(
            f"{API_URL}/api/v1/search",
            json={
                "query": "Fußball-AG Anti-Rassismus-Projekt Grundschule Integration",
                "top_k": 5
            },
            headers={
                "Authorization": f"Bearer {token}"
            },
            timeout=30
        )

        if response.status_code == 200:
            results = response.json()
            print(f"✅ RAG Search erfolgreich!")
            print(f"   Gefunden: {len(results.get('results', []))} Ergebnisse")
            print()

            # Check if Julius Hirsch Preis is in results
            found_julius_hirsch = False
            for i, result in enumerate(results.get('results', [])[:3], 1):
                print(f"{i}. {result.get('title', 'N/A')}")
                print(f"   Provider: {result.get('provider', 'N/A')}")
                print(f"   Score: {result.get('score', 0):.3f}")

                if 'Julius Hirsch' in result.get('title', ''):
                    found_julius_hirsch = True
                    print(f"   🎯 JULIUS HIRSCH PREIS GEFUNDEN!")

                print()

            if found_julius_hirsch:
                print("✅ SUCCESS: Julius Hirsch Preis wurde von RAG gefunden!")
            else:
                print("❌ FAIL: Julius Hirsch Preis wurde NICHT gefunden")

            return found_julius_hirsch
        else:
            print(f"❌ RAG Search fehlgeschlagen: HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def test_ai_draft():
    """Test 2: Generiere AI Draft für Julius Hirsch Preis"""

    print()
    print("="*80)
    print("TEST 2: AI DRAFT GENERATION")
    print("="*80)
    print()

    # Get authentication token
    print("🔐 Authenticating...")
    token = get_auth_token()
    if not token:
        print("❌ Could not authenticate - test cannot proceed")
        return False
    print("✅ Authenticated successfully")
    print()

    print("Generating draft for Julius Hirsch Preis...")
    print()

    try:
        response = requests.post(
            f"{API_URL}/api/v1/drafts/generate",
            json={
                "school_data": SCHOOL_DATA,
                "project_description": PROJECT_REQUEST,
                "funding_id": JULIUS_HIRSCH_ID
            },
            headers={
                "Authorization": f"Bearer {token}"
            },
            timeout=120  # Draft generation can take time
        )

        if response.status_code == 200:
            draft_data = response.json()

            print("✅ Draft generiert!")
            print()
            print("="*80)
            print("GENERATED DRAFT")
            print("="*80)
            print()

            draft_text = draft_data.get('draft', '')

            # Print first 2000 chars
            print(draft_text[:2000])
            if len(draft_text) > 2000:
                print(f"\n... ({len(draft_text) - 2000} more characters)")

            print()
            print("="*80)
            print("DRAFT ANALYSIS")
            print("="*80)

            # Analyze draft quality
            checks = {
                "Deadline erwähnt (30. Juni 2025)": "30. Juni 2025" in draft_text or "30.06.2025" in draft_text,
                "Eligibility Kriterien adressiert": "Projektzeitraum" in draft_text or "Juli 2024" in draft_text,
                "Anti-Rassismus erwähnt": "Antisemitismus" in draft_text or "Rassismus" in draft_text,
                "Bewerbung über dfb.de erwähnt": "dfb.de" in draft_text or "DFB" in draft_text,
                "Jury erwähnt": "Jury" in draft_text,
                "Preisverleihung Hamburg erwähnt": "Hamburg" in draft_text or "Preisverleihung" in draft_text,
                "Projektumsetzung beschrieben": len(draft_text) > 500,
                "Grundschule Musterberg erwähnt": "Musterberg" in draft_text,
            }

            passed = sum(1 for v in checks.values() if v)
            total = len(checks)

            print(f"\nQuality Checks: {passed}/{total} passed")
            print()

            for check, result in checks.items():
                icon = "✅" if result else "❌"
                print(f"{icon} {check}")

            print()
            print(f"Draft Length: {len(draft_text)} characters")
            print(f"Quality Score: {passed/total*100:.0f}%")

            return passed >= total * 0.7  # 70% pass rate

        else:
            print(f"❌ Draft Generation fehlgeschlagen: HTTP {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return False

    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("="*80)
    print("AI DRAFT GENERATION TEST - JULIUS HIRSCH PREIS")
    print("="*80)
    print()
    print(f"API URL: {API_URL}")
    print(f"Test School: {SCHOOL_DATA['school_name']}")
    print()

    # Test 1: RAG Search
    rag_success = test_rag_search()

    # Test 2: AI Draft (only if RAG found the prize)
    if rag_success:
        draft_success = test_ai_draft()
    else:
        print()
        print("⏭️ Skipping Draft Generation Test (RAG didn't find Julius Hirsch Preis)")
        draft_success = False

    # Summary
    print()
    print("="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"RAG Search: {'✅ PASS' if rag_success else '❌ FAIL'}")
    print(f"Draft Generation: {'✅ PASS' if draft_success else '❌ FAIL'}")
    print()

    if rag_success and draft_success:
        print("🎉 ALL TESTS PASSED!")
        print()
        print("Der Julius Hirsch Preis wurde erfolgreich gefunden und ein")
        print("hochwertiger Antrag wurde generiert!")
        return 0
    else:
        print("⚠️ SOME TESTS FAILED")
        return 1


if __name__ == '__main__':
    exit(main())
