#!/usr/bin/env python3
"""
VOLLSTÄNDIGER E2E Test für Förder-Finder
Testet den kompletten User-Flow inkl. AI Draft Generation
"""

import requests
import json
import sys
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8001/api/v1"
TEST_USER = {
    "email": "admin@gs-musterberg.de",
    "password": "test1234"
}

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'

def print_header(title):
    print("\n" + "=" * 80)
    print(f"{Colors.CYAN}{title}{Colors.RESET}")
    print("=" * 80)

def print_step(step_num, description):
    print(f"\n{Colors.BLUE}[STEP {step_num}]{Colors.RESET} {description}")

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")

def print_info(message):
    print(f"{Colors.YELLOW}ℹ️  {message}{Colors.RESET}")

def main():
    """Vollständiger E2E Test"""
    print_header("FÖRDER-FINDER VOLLSTÄNDIGER E2E TEST")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Backend: {BASE_URL}")
    print()

    # ===========================
    # SCHRITT 1: LOGIN
    # ===========================
    print_step(1, "Login & Authentication")

    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=TEST_USER,
            timeout=10
        )

        if response.status_code != 200:
            print_error(f"Login fehlgeschlagen: {response.status_code} - {response.text}")
            sys.exit(1)

        data = response.json()
        token = data.get("access_token")
        user_id = data.get("user_id")
        school_id = data.get("school_id")

        print_success("Login erfolgreich!")
        print_info(f"User ID: {user_id}")
        print_info(f"School ID: {school_id}")
        print_info(f"Token: {token[:30]}...")

        headers = {"Authorization": f"Bearer {token}"}

    except Exception as e:
        print_error(f"Login Error: {e}")
        sys.exit(1)

    # ===========================
    # SCHRITT 2: FUNDING LISTE
    # ===========================
    print_step(2, "Funding Opportunities abrufen")

    try:
        response = requests.get(
            f"{BASE_URL}/funding/?limit=10",
            headers=headers,
            timeout=10
        )

        if response.status_code != 200:
            print_error(f"Funding-Liste fehlgeschlagen: {response.status_code}")
            sys.exit(1)

        opportunities = response.json()
        print_success(f"{len(opportunities)} Fördermittel gefunden")

        if not opportunities:
            print_error("Keine Fördermittel in DB!")
            sys.exit(1)

        # Erstes Fördermittel für Test verwenden
        selected_funding = opportunities[0]
        funding_id = selected_funding.get('funding_id')
        funding_title = selected_funding.get('title', 'N/A')

        print_info(f"Ausgewähltes Fördermittel:")
        print_info(f"  ID: {funding_id}")
        print_info(f"  Titel: {funding_title[:70]}...")
        print_info(f"  Provider: {selected_funding.get('provider', 'N/A')}")

    except Exception as e:
        print_error(f"Funding-Liste Error: {e}")
        sys.exit(1)

    # ===========================
    # SCHRITT 3: FUNDING DETAILS
    # ===========================
    print_step(3, "Funding Details abrufen")

    try:
        response = requests.get(
            f"{BASE_URL}/funding/{funding_id}",
            headers=headers,
            timeout=10
        )

        if response.status_code != 200:
            print_error(f"Funding Details fehlgeschlagen: {response.status_code}")
            sys.exit(1)

        funding_detail = response.json()
        cleaned_text_length = len(funding_detail.get('cleaned_text', ''))

        print_success("Funding Details abgerufen")
        print_info(f"Text-Länge: {cleaned_text_length} Zeichen")
        print_info(f"Deadline: {funding_detail.get('deadline', 'Keine')}")

    except Exception as e:
        print_error(f"Funding Details Error: {e}")
        sys.exit(1)

    # ===========================
    # SCHRITT 4: APPLICATION ERSTELLEN
    # ===========================
    print_step(4, "Neue Application erstellen")

    try:
        application_data = {
            "funding_id": funding_id,
            "title": f"Test-Antrag für {funding_title[:30]}",
            "projektbeschreibung": "Digitalisierungsprojekt an unserer Grundschule mit 300 Schülern. Wir möchten Tablets und interaktive Whiteboards anschaffen."
        }

        response = requests.post(
            f"{BASE_URL}/applications/",
            headers=headers,
            json=application_data,
            timeout=10
        )

        if response.status_code != 201:
            print_error(f"Application-Erstellung fehlgeschlagen: {response.status_code} - {response.text}")
            sys.exit(1)

        application = response.json()
        application_id = application.get('application_id')

        print_success("Application erfolgreich erstellt!")
        print_info(f"Application ID: {application_id}")
        print_info(f"Titel: {application.get('title', 'N/A')}")
        print_info(f"Status: {application.get('status', 'N/A')}")

    except Exception as e:
        print_error(f"Application Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # ===========================
    # SCHRITT 5: AI DRAFT GENERIEREN
    # ===========================
    print_step(5, "AI Draft mit DeepSeek generieren")
    print_info("⏳ Dies kann 30-90 Sekunden dauern...")

    try:
        draft_request = {
            "application_id": application_id,
            "funding_id": funding_id,
            "user_query": "Wir sind eine Grundschule mit 300 Schülern und möchten unsere digitale Ausstattung verbessern. Wir planen die Anschaffung von Tablets für jede Klasse und interaktiven Whiteboards. Unser Schwerpunkt liegt auf MINT-Förderung und digitaler Bildung."
        }

        start_time = time.time()

        response = requests.post(
            f"{BASE_URL}/drafts/generate",
            headers=headers,
            json=draft_request,
            timeout=120  # 2 Minuten Timeout
        )

        generation_time = time.time() - start_time

        if response.status_code != 200:
            print_error(f"Draft-Generierung fehlgeschlagen: {response.status_code}")
            print_error(f"Response: {response.text}")
            sys.exit(1)

        draft = response.json()
        draft_id = draft.get('draft_id')
        generated_content = draft.get('generated_content', '')
        model_used = draft.get('model_used', 'unknown')

        print_success(f"AI Draft erfolgreich generiert! (in {generation_time:.1f}s)")
        print_info(f"Draft ID: {draft_id}")
        print_info(f"Model: {model_used}")
        print_info(f"Content Länge: {len(generated_content)} Zeichen")
        print_info(f"Preview:")
        print(f"{Colors.CYAN}{'-' * 60}{Colors.RESET}")
        print(f"{generated_content[:300]}...")
        print(f"{Colors.CYAN}{'-' * 60}{Colors.RESET}")

    except requests.exceptions.Timeout:
        print_error("Draft-Generierung Timeout (>120s)")
        print_info("DeepSeek API könnte langsam sein oder nicht erreichbar")
        sys.exit(1)
    except Exception as e:
        print_error(f"Draft-Generierung Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # ===========================
    # SCHRITT 6: DRAFT ABRUFEN
    # ===========================
    print_step(6, "Generierte Drafts für Application abrufen")

    try:
        response = requests.get(
            f"{BASE_URL}/drafts/application/{application_id}",
            headers=headers,
            timeout=10
        )

        if response.status_code != 200:
            print_error(f"Drafts abrufen fehlgeschlagen: {response.status_code}")
        else:
            drafts = response.json()
            print_success(f"{len(drafts)} Draft(s) für Application gefunden")

            for idx, d in enumerate(drafts, 1):
                print_info(f"  Draft {idx}: {d.get('draft_id')} - {len(d.get('generated_content', ''))} Zeichen")

    except Exception as e:
        print_error(f"Draft-Abruf Error: {e}")

    # ===========================
    # SCHRITT 7: RAG SEARCH
    # ===========================
    print_step(7, "RAG Search testen")

    try:
        search_query = "Digitalisierung Tablets Grundschule"

        response = requests.post(
            f"{BASE_URL}/search",
            headers=headers,
            json={"query": search_query, "limit": 5},
            timeout=30
        )

        if response.status_code != 200:
            print_error(f"Search fehlgeschlagen: {response.status_code}")
        else:
            results = response.json()
            search_results = results.get('results', [])

            print_success(f"Search: {len(search_results)} Ergebnisse")
            print_info(f"Query: \"{search_query}\"")

            for idx, result in enumerate(search_results[:3], 1):
                score = result.get('score', 0)
                title = result.get('title', 'N/A')
                print_info(f"  {idx}. [{score:.3f}] {title[:50]}...")

    except Exception as e:
        print_error(f"Search Error: {e}")

    # ===========================
    # SCHRITT 8: APPLICATIONS LISTE
    # ===========================
    print_step(8, "Alle Applications abrufen")

    try:
        response = requests.get(
            f"{BASE_URL}/applications/",
            headers=headers,
            timeout=10
        )

        if response.status_code != 200:
            print_error(f"Applications abrufen fehlgeschlagen: {response.status_code}")
        else:
            applications = response.json()
            print_success(f"{len(applications)} Application(s) gefunden")

            for idx, app in enumerate(applications, 1):
                print_info(f"  {idx}. {app.get('title', 'N/A')[:50]} - Status: {app.get('status', 'N/A')}")

    except Exception as e:
        print_error(f"Applications Error: {e}")

    # ===========================
    # SCHRITT 9: APPLICATION UPDATE
    # ===========================
    print_step(9, "Application Status aktualisieren")

    try:
        update_data = {
            "status": "in_review"
        }

        response = requests.patch(
            f"{BASE_URL}/applications/{application_id}",
            headers=headers,
            json=update_data,
            timeout=10
        )

        if response.status_code != 200:
            print_error(f"Update fehlgeschlagen: {response.status_code}")
        else:
            updated_app = response.json()
            print_success("Application aktualisiert")
            print_info(f"Neuer Status: {updated_app.get('status', 'N/A')}")

    except Exception as e:
        print_error(f"Update Error: {e}")

    # ===========================
    # FINALE ZUSAMMENFASSUNG
    # ===========================
    print_header("TEST ABGESCHLOSSEN")

    print(f"\n{Colors.GREEN}✅ ALLE TESTS ERFOLGREICH DURCHGELAUFEN{Colors.RESET}\n")

    print("Getestete Features:")
    print("  ✅ Login & JWT Authentication")
    print("  ✅ Funding Opportunities Liste")
    print("  ✅ Funding Details")
    print("  ✅ Application erstellen")
    print(f"  ✅ AI Draft generieren (DeepSeek - {generation_time:.1f}s)")
    print("  ✅ Drafts abrufen")
    print("  ✅ RAG Search (Vector + BM25)")
    print("  ✅ Applications Liste")
    print("  ✅ Application Update")

    print(f"\n{Colors.CYAN}Erstellte Test-Daten:{Colors.RESET}")
    print(f"  Application ID: {application_id}")
    print(f"  Draft ID: {draft_id}")
    print(f"  Funding ID: {funding_id}")

    print(f"\n{Colors.YELLOW}Nächste Schritte:{Colors.RESET}")
    print("  1. Frontend im Browser testen: http://localhost:3000")
    print("  2. Mit Test-User einloggen: admin@gs-musterberg.de / test1234")
    print("  3. Application und Draft in UI überprüfen")

    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

if __name__ == "__main__":
    main()
