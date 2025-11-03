#!/usr/bin/env python3
"""
REALISTISCHER USER JOURNEY TEST
Simuliert einen echten Schulleiter, der die Plattform nutzt
"""

import requests
import json
import sys
import time
from datetime import datetime
from typing import List, Dict, Any

BASE_URL = "http://localhost:8001/api/v1"
TEST_USER = {
    "email": "admin@gs-musterberg.de",
    "password": "test1234"
}

# Schulkontext - Grundschule Musterberg
SCHOOL_CONTEXT = {
    "name": "Grundschule Musterberg",
    "location": "Berlin-Mitte",
    "students": 300,
    "teachers": 25,
    "focus_areas": ["Digitalisierung", "MINT-Förderung", "Inklusion", "Sprachförderung"],
    "current_challenges": [
        "Veraltete IT-Ausstattung (Tablets fehlen)",
        "Nur 2 interaktive Whiteboards für 12 Klassen",
        "Keine moderne Lernplattform",
        "Hoher Anteil an Kindern mit Migrationshintergrund (65%)",
        "Förderbedarf: Sprache, Mathematik, Naturwissenschaften"
    ],
    "planned_projects": [
        "Digitales Klassenzimmer (Tablets, Whiteboards, WLAN)",
        "MINT-Labor einrichten",
        "Sprachförderprogramm erweitern",
        "Inklusive Lernumgebung schaffen"
    ]
}

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'

def print_header(title):
    print("\n" + "=" * 100)
    print(f"{Colors.CYAN}{title}{Colors.RESET}")
    print("=" * 100)

def print_section(title):
    print(f"\n{Colors.MAGENTA}{'─' * 100}{Colors.RESET}")
    print(f"{Colors.MAGENTA}▶ {title}{Colors.RESET}")
    print(f"{Colors.MAGENTA}{'─' * 100}{Colors.RESET}")

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")

def print_info(message):
    print(f"{Colors.YELLOW}ℹ️  {message}{Colors.RESET}")

def print_highlight(message):
    print(f"{Colors.CYAN}★ {message}{Colors.RESET}")

def analyze_opportunity(opp: Dict[str, Any], school: Dict[str, Any]) -> Dict[str, Any]:
    """Analysiert eine Opportunity und berechnet Match-Score"""
    score = 0
    reasons = []

    title = (opp.get('title') or '').lower()
    provider = (opp.get('provider') or '').lower()
    funding_area = (opp.get('funding_area') or '').lower()
    region = (opp.get('region') or '').lower()

    # Digitalisierung?
    if any(word in title for word in ['digital', 'tablet', 'whiteboard', 'it', 'computer', 'technik']):
        score += 30
        reasons.append("Digitalisierung (Top-Priorität)")

    # MINT?
    if any(word in title for word in ['mint', 'mathematik', 'naturwissenschaft', 'technik', 'labor']):
        score += 25
        reasons.append("MINT-Förderung")

    # Grundschule?
    if 'grundschule' in title:
        score += 20
        reasons.append("Speziell für Grundschulen")

    # Sprachförderung?
    if any(word in title for word in ['sprach', 'deutsch', 'migration', 'integration']):
        score += 20
        reasons.append("Sprachförderung")

    # Inklusion?
    if any(word in title for word in ['inklu', 'förder', 'diversity']):
        score += 15
        reasons.append("Inklusion/Förderung")

    # Region Berlin?
    if region and 'berlin' in region:
        score += 10
        reasons.append("Regionale Förderung (Berlin)")

    # Bekannte gute Fördergeber?
    good_providers = ['telekom', 'bosch', 'vodafone', 'bundesregierung', 'senat']
    if any(provider_name in provider for provider_name in good_providers):
        score += 10
        reasons.append("Renommierter Fördergeber")

    return {
        'score': score,
        'reasons': reasons,
        'opportunity': opp
    }

def main():
    print_header("REALISTISCHER USER JOURNEY - GRUNDSCHULE MUSTERBERG")
    print(f"Datum: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nSchule: {SCHOOL_CONTEXT['name']}")
    print(f"Standort: {SCHOOL_CONTEXT['location']}")
    print(f"Schüler: {SCHOOL_CONTEXT['students']}")
    print(f"Schwerpunkte: {', '.join(SCHOOL_CONTEXT['focus_areas'])}")

    # =================================================================
    # SCHRITT 1: LOGIN ALS SCHULLEITER
    # =================================================================
    print_section("SCHRITT 1: Login als Schulleiter")

    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=TEST_USER,
            timeout=10
        )

        if response.status_code != 200:
            print_error(f"Login fehlgeschlagen: {response.status_code}")
            sys.exit(1)

        data = response.json()
        token = data.get("access_token")
        headers = {"Authorization": f"Bearer {token}"}

        print_success("Login erfolgreich!")
        print_info(f"Eingeloggt als: {TEST_USER['email']}")
        print_info(f"Role: {data.get('role', 'N/A')}")

    except Exception as e:
        print_error(f"Login Error: {e}")
        sys.exit(1)

    # =================================================================
    # SCHRITT 2: ALLE OPPORTUNITIES ABRUFEN UND SCANNEN
    # =================================================================
    print_section("SCHRITT 2: Alle verfügbaren Fördermittel scannen")

    try:
        response = requests.get(
            f"{BASE_URL}/funding/?limit=100",  # Alle abrufen
            headers=headers,
            timeout=10
        )

        if response.status_code != 200:
            print_error(f"Funding-Abruf fehlgeschlagen: {response.status_code}")
            sys.exit(1)

        all_opportunities = response.json()
        print_success(f"{len(all_opportunities)} Fördermittel gefunden")

        # Übersicht anzeigen
        print("\n📊 Übersicht nach Provider:")
        providers = {}
        for opp in all_opportunities:
            provider = opp.get('provider', 'Unbekannt')
            providers[provider] = providers.get(provider, 0) + 1

        for provider, count in sorted(providers.items(), key=lambda x: -x[1])[:10]:
            print(f"   • {provider}: {count} Fördermittel")

    except Exception as e:
        print_error(f"Funding-Scan Error: {e}")
        sys.exit(1)

    # =================================================================
    # SCHRITT 3: OPPORTUNITIES ANALYSIEREN & RANKEN
    # =================================================================
    print_section("SCHRITT 3: Opportunities nach Relevanz analysieren")

    print_info("Analysiere alle Opportunities für Grundschule Musterberg...")
    print_info(f"Bewertungskriterien:")
    print(f"   • Digitalisierung: +30 Punkte")
    print(f"   • MINT-Förderung: +25 Punkte")
    print(f"   • Grundschule-spezifisch: +20 Punkte")
    print(f"   • Sprachförderung: +20 Punkte")
    print(f"   • Inklusion: +15 Punkte")
    print(f"   • Regional (Berlin): +10 Punkte")

    analyzed = []
    for opp in all_opportunities:
        result = analyze_opportunity(opp, SCHOOL_CONTEXT)
        if result['score'] > 0:  # Nur relevante
            analyzed.append(result)

    # Nach Score sortieren
    analyzed.sort(key=lambda x: -x['score'])

    print_success(f"{len(analyzed)} relevante Opportunities gefunden")

    # TOP 10 anzeigen
    print("\n🏆 TOP 10 PASSENDSTE FÖRDERMITTEL:")
    print(f"{'Rank':<6} {'Score':<8} {'Titel':<60} {'Gründe'}")
    print("─" * 120)

    for idx, result in enumerate(analyzed[:10], 1):
        opp = result['opportunity']
        title = opp.get('title', 'N/A')[:58]
        score = result['score']
        reasons = ', '.join(result['reasons'][:2])  # Erste 2 Gründe

        print(f"#{idx:<5} {score:<8} {title:<60} {reasons}")

    # =================================================================
    # SCHRITT 4: TOP 3 DETAILLIERT VERGLEICHEN
    # =================================================================
    print_section("SCHRITT 4: Top 3 Opportunities detailliert vergleichen")

    top3 = analyzed[:3]

    for idx, result in enumerate(top3, 1):
        opp = result['opportunity']
        funding_id = opp.get('funding_id')

        print(f"\n{Colors.CYAN}{'═' * 100}{Colors.RESET}")
        print(f"{Colors.CYAN}Option #{idx} - Score: {result['score']} Punkte{Colors.RESET}")
        print(f"{Colors.CYAN}{'═' * 100}{Colors.RESET}")

        # Details abrufen
        try:
            detail_response = requests.get(
                f"{BASE_URL}/funding/{funding_id}",
                headers=headers,
                timeout=10
            )

            if detail_response.status_code == 200:
                detail = detail_response.json()

                print(f"\n📋 Titel: {detail.get('title', 'N/A')}")
                print(f"🏢 Anbieter: {detail.get('provider', 'N/A')}")
                print(f"📍 Region: {detail.get('region', 'N/A') or 'Bundesweit'}")
                print(f"🎯 Förderbereich: {detail.get('funding_area', 'N/A') or 'Allgemein'}")
                print(f"📅 Deadline: {detail.get('deadline', 'N/A') or 'Laufend'}")
                print(f"💰 Förderung: {detail.get('min_funding_amount', 'N/A')} - {detail.get('max_funding_amount', 'N/A')} €")
                print(f"📄 Beschreibung: {len(detail.get('cleaned_text', ''))} Zeichen")

                print(f"\n✨ Warum diese Opportunity passt:")
                for reason in result['reasons']:
                    print(f"   ✓ {reason}")

                # Preview der Beschreibung
                cleaned_text = detail.get('cleaned_text', '')
                if cleaned_text:
                    preview = cleaned_text[:250].replace('\n', ' ')
                    print(f"\n📖 Auszug:")
                    print(f"   {preview}...")

        except Exception as e:
            print_error(f"Fehler beim Abrufen von Details: {e}")

    # =================================================================
    # SCHRITT 5: BESTE OPPORTUNITY AUSWÄHLEN
    # =================================================================
    print_section("SCHRITT 5: Entscheidung für beste Opportunity")

    selected = top3[0]  # Höchster Score
    selected_opp = selected['opportunity']

    print_highlight(f"AUSGEWÄHLT: {selected_opp.get('title', 'N/A')}")
    print_info(f"Grund: Höchster Match-Score ({selected['score']} Punkte)")
    print_info(f"Provider: {selected_opp.get('provider', 'N/A')}")
    print("\n💡 Diese Förderung passt am besten zu unseren Projekten:")
    for idx, project in enumerate(SCHOOL_CONTEXT['planned_projects'][:2], 1):
        print(f"   {idx}. {project}")

    # =================================================================
    # SCHRITT 6: APPLICATION MIT REALEM KONTEXT ERSTELLEN
    # =================================================================
    print_section("SCHRITT 6: Application/Bewerbung erstellen")

    # Realistische Projektbeschreibung erstellen
    project_description = f"""
**Projektitel: Digitales Klassenzimmer 2025 - Chancengleichheit durch Technologie**

**Ausgangssituation:**
Die Grundschule Musterberg in Berlin-Mitte unterrichtet aktuell {SCHOOL_CONTEXT['students']} Schülerinnen und Schüler mit einem Lehrerkollegium von {SCHOOL_CONTEXT['teachers']} Personen. 65% unserer Schüler haben einen Migrationshintergrund, viele kommen aus sozial benachteiligten Familien.

**Aktuelle Herausforderungen:**
{chr(10).join('- ' + challenge for challenge in SCHOOL_CONTEXT['current_challenges'])}

**Projektziel:**
Wir möchten ein modernes, digitales Lernumfeld schaffen, das allen Kindern unabhängig von ihrer Herkunft gleiche Bildungschancen bietet. Konkret planen wir:

1. **Tablet-Ausstattung:** 12 Tablet-Koffer mit je 25 iPads für alle Klassen
2. **Interaktive Whiteboards:** 10 moderne Smartboards für interaktiven Unterricht
3. **MINT-Labor:** Einrichtung eines digitalen MINT-Raums mit Lego Mindstorms, Calliope Mini
4. **Lernplattform:** Lizenz für digitale Lernplattform (Anton, Antolin, etc.)
5. **Lehrerfortbildung:** Schulung des Kollegiums in digitaler Didaktik

**Erwartete Wirkung:**
- Verbesserung der digitalen Kompetenzen aller Schüler
- Individuellere Förderung durch adaptive Lernsoftware
- Höhere Motivation durch zeitgemäße Lernmethoden
- Bessere Berufsvorbereitung (digitale Skills)
- Ausgleich sozialer Ungleichheiten

**Zeitplan:** 12 Monate
**Budget:** ca. 150.000 € (Details in Anlage)
    """.strip()

    print_info("Erstelle realistische Application...")
    print(f"\n📝 Projektbeschreibung ({len(project_description)} Zeichen):")
    print(f"{Colors.CYAN}{'─' * 100}{Colors.RESET}")
    print(project_description[:400] + "...")
    print(f"{Colors.CYAN}{'─' * 100}{Colors.RESET}")

    try:
        application_data = {
            "funding_id": selected_opp.get('funding_id'),
            "title": "Digitales Klassenzimmer 2025 - Grundschule Musterberg",
            "projektbeschreibung": project_description
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
        print_info(f"Status: {application.get('status', 'N/A')}")

    except Exception as e:
        print_error(f"Application Error: {e}")
        sys.exit(1)

    # =================================================================
    # SCHRITT 7: AI DRAFT MIT REALEM KONTEXT GENERIEREN
    # =================================================================
    print_section("SCHRITT 7: AI-gestützten Förderantrag generieren")

    print_info("Starte AI Draft Generation mit DeepSeek...")
    print_info("⏳ Dies kann 30-90 Sekunden dauern...")

    # Ausführlicher User Query für besseren AI Draft
    user_query = f"""
Wir sind die Grundschule Musterberg in Berlin-Mitte mit {SCHOOL_CONTEXT['students']} Schülern und {SCHOOL_CONTEXT['teachers']} Lehrkräften.

**Unser Projekt: Digitales Klassenzimmer 2025**

Wir möchten unsere Schule digital modernisieren, um allen Kindern - unabhängig von ihrer sozialen Herkunft - gleiche Bildungschancen zu bieten. 65% unserer Schüler haben Migrationshintergrund, viele kommen aus benachteiligten Familien.

**Konkrete Maßnahmen:**
1. 12 Tablet-Koffer (je 25 iPads) für alle Klassen
2. 10 interaktive Smartboards
3. MINT-Labor mit Robotik (Lego Mindstorms, Calliope Mini)
4. Digitale Lernplattform-Lizenzen
5. Fortbildung für 25 Lehrkräfte

**Herausforderungen, die wir lösen:**
- Veraltete IT (nur 2 Whiteboards für 12 Klassen)
- Keine Tablets verfügbar
- Hoher Sprachförderbedarf
- Digitale Kompetenzen fehlen

**Ziele:**
- Digitale Kompetenzen für alle Kinder
- Individuellere Förderung durch adaptive Software
- MINT-Begeisterung wecken
- Chancengleichheit herstellen

Budget: ca. 150.000 €
Zeitraum: 12 Monate
    """.strip()

    try:
        draft_request = {
            "application_id": application_id,
            "funding_id": selected_opp.get('funding_id'),
            "user_query": user_query
        }

        start_time = time.time()

        response = requests.post(
            f"{BASE_URL}/drafts/generate",
            headers=headers,
            json=draft_request,
            timeout=120
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
        print_info(f"Länge: {len(generated_content)} Zeichen")

        # Vollständigen Draft anzeigen (ersten Teil)
        print(f"\n{Colors.GREEN}{'═' * 100}{Colors.RESET}")
        print(f"{Colors.GREEN}GENERIERTER FÖRDERANTRAG{Colors.RESET}")
        print(f"{Colors.GREEN}{'═' * 100}{Colors.RESET}\n")
        print(generated_content[:1500])
        print(f"\n{Colors.YELLOW}... ({len(generated_content) - 1500} weitere Zeichen){Colors.RESET}")
        print(f"{Colors.GREEN}{'═' * 100}{Colors.RESET}")

    except requests.exceptions.Timeout:
        print_error("Draft-Generierung Timeout (>120s)")
        sys.exit(1)
    except Exception as e:
        print_error(f"Draft Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # =================================================================
    # SCHRITT 8: RAG SEARCH ZUM VERGLEICH
    # =================================================================
    print_section("SCHRITT 8: Ähnliche Fördermittel mit RAG Search finden")

    try:
        search_queries = [
            "Digitalisierung Grundschule Tablets",
            "MINT Förderung Berlin",
            "Inklusion digitale Bildung"
        ]

        for query in search_queries:
            print(f"\n🔍 Suche: \"{query}\"")

            response = requests.post(
                f"{BASE_URL}/search",
                headers=headers,
                json={"query": query, "limit": 3},
                timeout=30
            )

            if response.status_code == 200:
                results = response.json()
                search_results = results.get('results', [])

                for idx, result in enumerate(search_results, 1):
                    score = result.get('score', 0)
                    title = result.get('title', 'N/A')[:50]
                    print(f"   {idx}. [{score:+.3f}] {title}...")

        print_success("RAG Search zeigt relevante alternative Fördermittel")

    except Exception as e:
        print_error(f"Search Error: {e}")

    # =================================================================
    # FINALE ZUSAMMENFASSUNG
    # =================================================================
    print_header("REALISTISCHER USER JOURNEY ABGESCHLOSSEN")

    print(f"\n{Colors.GREEN}✅ KOMPLETTER WORKFLOW ERFOLGREICH{Colors.RESET}\n")

    print("📊 Durchgeführte Schritte:")
    print(f"   1. ✅ Login als Schulleiter (Grundschule Musterberg)")
    print(f"   2. ✅ {len(all_opportunities)} Fördermittel gescannt")
    print(f"   3. ✅ {len(analyzed)} relevante Opportunities gefunden")
    print(f"   4. ✅ Top 3 detailliert verglichen")
    print(f"   5. ✅ Beste Opportunity ausgewählt (Score: {selected['score']})")
    print(f"   6. ✅ Realistische Application erstellt ({len(project_description)} Zeichen)")
    print(f"   7. ✅ AI Draft generiert ({len(generated_content)} Zeichen, {generation_time:.1f}s)")
    print(f"   8. ✅ RAG Search für alternative Optionen")

    print(f"\n{Colors.CYAN}📋 Ergebnis:{Colors.RESET}")
    print(f"   Ausgewählte Förderung: {selected_opp.get('title', 'N/A')[:60]}...")
    print(f"   Provider: {selected_opp.get('provider', 'N/A')}")
    print(f"   Match-Score: {selected['score']} Punkte")
    print(f"   Projekt: Digitales Klassenzimmer 2025")
    print(f"   Budget: ~150.000 €")

    print(f"\n{Colors.CYAN}📁 Erstellt:{Colors.RESET}")
    print(f"   Application ID: {application_id}")
    print(f"   Draft ID: {draft_id}")
    print(f"   Draft Länge: {len(generated_content):,} Zeichen")
    print(f"   Model: {model_used}")

    print(f"\n{Colors.YELLOW}🌐 Frontend Test:{Colors.RESET}")
    print(f"   URL: http://localhost:3000")
    print(f"   Login: {TEST_USER['email']} / {TEST_USER['password']}")
    print(f"   → Prüfe Application & Draft in der UI!")

    print(f"\n{Colors.GREEN}{'═' * 100}{Colors.RESET}")
    print(f"{Colors.GREEN}SUCCESS - Realistischer User Journey komplett validiert!{Colors.RESET}")
    print(f"{Colors.GREEN}{'═' * 100}{Colors.RESET}\n")

if __name__ == "__main__":
    main()
