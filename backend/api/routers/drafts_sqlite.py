"""
AI Drafts Router (SQLite-compatible + Advanced Context-Aware Mode)
KI-generierte Antragsentwürfe mit tiefem Schulkontext
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from datetime import datetime
import uuid
import logging

from api.models import DraftGenerateRequest, DraftGenerateResponse, DraftFeedback
from api.auth_utils import get_current_user
from utils.db_adapter import get_db_cursor

# DeepSeek Integration via OpenAI SDK
from openai import OpenAI
import json

# Configure logging
logger = logging.getLogger(__name__)

# Initialize DeepSeek client (OpenAI SDK with DeepSeek endpoint)
deepseek_client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY", "sk-placeholder"),
    base_url="https://api.deepseek.com"
)

# Import advanced generator (optional fallback)
try:
    from api.routers.advanced_draft_generator import generate_advanced_draft
    USE_ADVANCED_GENERATOR = True
    print('[STARTUP] ✅ Advanced Draft Generator loaded')
except Exception as e:
    USE_ADVANCED_GENERATOR = False
    print(f'[STARTUP] ⚠️ Advanced Generator not available: {e}')

router = APIRouter()


def generate_id():
    """Generate UUID without dashes for SQLite"""
    return str(uuid.uuid4()).replace('-', '').upper()


def generate_mock_draft(funding_data: dict, user_query: str, school_profile: dict) -> str:
    """
    Generate a highly tailored, funding-specific mock draft for development/testing

    In production, this would call DeepSeek API with RAG
    """
    school_name = school_profile.get('school_name', 'Grundschule Musterberg')
    funding_title = funding_data['title']
    provider = funding_data['provider']
    categories = funding_data.get('categories', '')
    target_groups = funding_data.get('target_groups', '')
    description = funding_data.get('description', '')
    eligibility = funding_data.get('eligibility', '')
    deadline = funding_data.get('application_deadline', '')

    # Format funding amount with detailed breakdown
    max_amount = funding_data.get('funding_amount_max', 0)
    min_amount = funding_data.get('funding_amount_min', 0)

    funding_range_text = ""
    requested_amount = max_amount if max_amount else 50000  # Default if not specified

    if min_amount and max_amount:
        min_formatted = f"{min_amount:,.0f}".replace(',', '.')
        max_formatted = f"{max_amount:,.0f}".replace(',', '.')
        funding_range_text = f"**Fördersumme:** {min_formatted}€ - {max_formatted}€"
        requested_amount = max_amount  # Request maximum
    elif max_amount:
        max_formatted = f"{max_amount:,.0f}".replace(',', '.')
        funding_range_text = f"**Maximale Fördersumme:** {max_formatted}€"
        requested_amount = max_amount

    requested_formatted = f"{requested_amount:,.0f}".replace(',', '.')

    # Calculate project timeline based on deadline
    project_duration = "12 Monate"
    if deadline:
        project_duration = "12 Monate"  # Standard duration

    # Budget breakdown calculation based on requested amount
    sachmittel = int(requested_amount * 0.40)
    honorare = int(requested_amount * 0.30)
    fortbildung = int(requested_amount * 0.20)
    doku = int(requested_amount * 0.10)

    sachmittel_fmt = f"{sachmittel:,.0f}".replace(',', '.')
    honorare_fmt = f"{honorare:,.0f}".replace(',', '.')
    fortbildung_fmt = f"{fortbildung:,.0f}".replace(',', '.')
    doku_fmt = f"{doku:,.0f}".replace(',', '.')

    # Extract key concepts from user query for integration
    user_query_summary = user_query[:300] + "..." if len(user_query) > 300 else user_query

    # Build eligibility match section from actual funding requirements
    eligibility_section = ""
    if eligibility:
        eligibility_preview = eligibility[:500] + "..." if len(eligibility) > 500 else eligibility
        eligibility_section = f"""
### 2.2 Erfüllung der Förderkriterien

Unser Projekt erfüllt die spezifischen Anforderungen des Förderprogramms:

> **Förderkriterien laut Ausschreibung:**
> {eligibility_preview}

**Wie unser Projekt diese Kriterien erfüllt:**

1. **Zielgruppenkonformität:** Unser Projekt richtet sich an {target_groups or 'Grundschülerinnen und Grundschüler'}, was exakt der Förderausrichtung entspricht.

2. **Thematische Passung:** Mit dem Schwerpunkt auf {categories or 'Bildung und schulische Entwicklung'} decken wir die Kernthemen des Programms "{funding_title}" ab.

3. **Antragsberechtigung:** Als {school_profile.get('traeger', 'öffentlicher Träger')} erfüllt die {school_name} die formalen Anforderungen zur Antragstellung bei {provider}.

4. **Projektqualität:** Das beschriebene Vorhaben zeichnet sich durch Innovation, Nachhaltigkeit und messbare Wirkung aus.
"""
    else:
        eligibility_section = f"""
### 2.2 Erfüllung der Förderkriterien

Unser Projekt erfüllt die Anforderungen des Förderprogramms "{funding_title}" durch:

- **Zielgruppenausrichtung:** Das Projekt richtet sich an {target_groups or 'Schülerinnen und Schüler im Grundschulalter'}
- **Thematischer Schwerpunkt:** Fokus auf {categories or 'Bildung und Entwicklung'}
- **Antragsberechtigung:** {school_profile.get('traeger', 'Öffentlicher Träger')} mit Sitz in Deutschland
- **Innovationsgrad:** Neue Impulse für nachhaltige Schulentwicklung
"""

    # Build description context section
    description_section = ""
    if description:
        description_preview = description[:600] + "..." if len(description) > 600 else description
        description_section = f"""
### 1.3 Passung zum Förderprogramm

Das Förderprogramm "{funding_title}" von {provider} zielt darauf ab:

> {description_preview}

Unser Projektvorhaben fügt sich optimal in diese Zielsetzung ein und adressiert die beschriebenen Förderbedarfe direkt.
"""

    mock_draft = f"""# Förderantrag

## Antrag auf Förderung im Rahmen des Programms
**"{funding_title}"**

---

### Antragstellende Einrichtung

**Schulname:** {school_name}
**Schulnummer:** {school_profile.get('school_number', '123456')}
**Adresse:** {school_profile.get('address', 'Musterstraße 1, 12345 Musterstadt')}
**Schultyp:** {school_profile.get('schultyp', 'Grundschule')}
**Schülerzahl:** {school_profile.get('schuelerzahl', 250)}
**Trägerschaft:** {school_profile.get('traeger', 'Öffentlicher Träger')}

### Förderprogramm

**Fördergeber:** {provider}
**Förderprogramm:** {funding_title}
**Förderkategorie:** {categories or 'Bildung und Entwicklung'}
**Zielgruppen:** {target_groups or 'Grundschulen'}
{funding_range_text}

### Beantragte Fördersumme

**{requested_formatted}€**

### Projektlaufzeit

{project_duration}

---

## 1. Ausgangslage und Bedarfsanalyse

### 1.1 Unsere Schule

Die {school_name} ist eine {school_profile.get('schultyp', 'öffentliche Grundschule')} mit aktuell {school_profile.get('schuelerzahl', 250)} Schülerinnen und Schülern. Als {school_profile.get('traeger', 'öffentlicher Träger')} verfolgen wir das zentrale Ziel, allen Kindern bestmögliche Bildungschancen zu eröffnen und sie individuell in ihrer Entwicklung zu fördern.

Unsere Schule zeichnet sich durch ein engagiertes Kollegium, eine aktive Elternschaft und eine vielfältige Schülerschaft aus. Wir verstehen Bildung als gemeinsame Aufgabe von Schule, Familie und Gemeinschaft.

### 1.2 Projektidee und konkrete Bedarfe

{user_query}

Dieser Projektansatz adressiert konkrete, identifizierte Bedarfe unserer Schulgemeinschaft und stellt eine wichtige Weiterentwicklung unseres pädagogischen Angebots dar.
{description_section}

---

## 2. Projektziele und Förderprogrammbezug

### 2.1 Strategische Zielsetzung

**Übergeordnetes Projektziel:**

Umsetzung der beschriebenen Projektidee als strukturiertes, evaluiertes und nachhaltig wirksames Bildungsangebot an der {school_name}, in vollständiger Übereinstimmung mit den Zielsetzungen des Förderprogramms "{funding_title}" von {provider}.

**Konkrete Teilziele:**

1. **Pädagogische Wirkung:**
   Direkte Verbesserung der Lern- und Entwicklungschancen für unsere Schülerinnen und Schüler durch gezielte, bedarfsorientierte Maßnahmen.

2. **Strukturelle Nachhaltigkeit:**
   Aufbau dauerhafter Strukturen, Prozesse und Materialien, die über die Projektlaufzeit hinaus Bestand haben und in den regulären Schulbetrieb integriert werden.

3. **Organisationale Entwicklung:**
   Professionalisierung des Kollegiums, Stärkung der Schulgemeinschaft und Einbindung aller relevanten Akteure (Lehrkräfte, Eltern, externe Partner).

4. **Wissenstransfer:**
   Systematische Dokumentation der Projekterfahrungen und Ergebnisse zur Weitergabe an andere Schulen und Einrichtungen.
{eligibility_section}

---

## 3. Projektumsetzung und Maßnahmenplanung

### 3.1 Zeitplan und Projektphasen

Das Projekt ist in drei aufeinander aufbauende Phasen gegliedert:

| Phase | Zeitraum | Schwerpunkt | Zentrale Aktivitäten |
|-------|----------|-------------|---------------------|
| **Phase 1: Vorbereitung** | Monate 1-2 | Konzeption & Team-Building | Bedarfsanalyse, Projektteam-Bildung, Detailplanung |
| **Phase 2: Durchführung** | Monate 3-10 | Hauptumsetzung | Beschaffung, Aktivitäten, Fortbildungen, laufende Evaluation |
| **Phase 3: Verstetigung** | Monate 11-12 | Evaluation & Transfer | Abschlussevaluation, Dokumentation, Nachhaltigkeitskonzept |

### 3.2 Detaillierte Maßnahmenbeschreibung

**Phase 1: Vorbereitung und Konzeption (Monate 1-2)**

1. Durchführung einer detaillierten Bedarfsanalyse unter Einbeziehung von Schüler-, Eltern- und Lehrkräfteperspektiven
2. Bildung eines Projektteams bestehend aus Lehrkräften verschiedener Fachbereiche und Elternvertretern
3. Erstellung eines operativen Umsetzungsplans mit definierten Meilensteinen und Verantwortlichkeiten
4. Beschaffungsplanung und Ausschreibung notwendiger Dienstleistungen
5. Kick-off-Veranstaltung zur Information der gesamten Schulgemeinschaft

**Phase 2: Hauptumsetzung (Monate 3-10)**

1. Beschaffung und Installation notwendiger Materialien, Ausstattung und Lernmittel
2. Durchführung der geplanten Projektaktivitäten im regulären Schulbetrieb
3. Fortbildungsreihe für Lehrkräfte zur fachlichen und methodischen Qualifizierung
4. Einbindung externer Expertise durch Workshops, Coaching oder Beratungsleistungen
5. Kontinuierliche Prozessbeobachtung und formative Evaluation mit Anpassung bei Bedarf
6. Dokumentation aller Aktivitäten, Materialien und Erkenntnisse

**Phase 3: Verstetigung und Evaluation (Monate 11-12)**

1. Summative Evaluation durch standardisierte Befragungen (Schüler, Eltern, Lehrkräfte)
2. Auswertung quantitativer und qualitativer Daten zur Projektw irkung
3. Entwicklung eines Nachhaltigkeitskonzepts zur Weiterführung nach Projektende
4. Erstellung einer Abschlussdokumentation mit Handreichungen für andere Schulen
5. Öffentlichkeitswirksame Präsentation der Projektergebnisse (Abschlussveranstaltung, Pressemitteilung)
6. Transfer der Erkenntnisse in das Schulprogramm und die Schulentwicklungsplanung

---

## 4. Qualitätssicherung und Evaluation

### 4.1 Evaluationsdesign

Die Projektevaluation erfolgt nach wissenschaftlichen Standards auf drei Ebenen:

**1. Prozessevaluation (formativ, laufend)**
- Regelmäßige Projektteam-Sitzungen mit Dokumentation
- Feedback-Schleifen mit Teilnehmenden
- Anpassung von Maßnahmen bei Bedarf

**2. Ergebnisevaluation (summativ, Projektende)**
- Vorher-Nachher-Vergleich definierter Indikatoren
- Standardisierte Befragungen aller Zielgruppen
- Auswertung von Teilnahmequoten und Aktivitätsdaten

**3. Wirkungsevaluation (langfristig)**
- Nachbefragung 6 Monate nach Projektende
- Integration in reguläre Schulentwicklungsevaluation

### 4.2 Erfolgsindikatoren

Der Projekterfolg wird anhand folgender messbarer Kriterien bewertet:

**Quantitative Indikatoren:**

| Indikator | Messmethode | Zielwert |
|-----------|-------------|----------|
| Teilnahmequote Schüler/-innen | Anwesenheitslisten | ≥ 85% |
| Durchgeführte Projektaktivitäten | Aktivitätslog | 100% der geplanten Aktivitäten |
| Fortbildungsteilnahme Lehrkräfte | Teilnehmerlisten | ≥ 90% des Kollegiums |
| Zufriedenheit (Schüler/-innen) | Fragebogen (Skala 1-5) | ≥ 4,0 |
| Zufriedenheit (Eltern) | Fragebogen (Skala 1-5) | ≥ 4,0 |
| Zufriedenheit (Lehrkräfte) | Fragebogen (Skala 1-5) | ≥ 4,2 |

**Qualitative Indikatoren:**

- Dokumentierte Kompetenzentwicklung bei Schülerinnen und Schülern (Lehrkraft-Feedback)
- Sichtbare Verbesserungen im Schulalltag und Lernklima
- Positive Rückmeldungen zur Wirkung auf Motivation und Engagement
- Erfolgreiche Integration der Projektergebnisse in den Schulalltag

---

## 5. Nachhaltigkeit und Verstetigung

### 5.1 Nachhaltigkeitsstrategie

Das Projekt ist von Beginn an auf dauerhafte Wirkung über die Förderphase hinaus ausgelegt:

**Strukturelle Nachhaltigkeit:**
- Alle beschafften Materialien und Ausstattungsgegenstände verbleiben dauerhaft in der Schule
- Entwickelte Konzepte und Unterrichtsmaterialien werden digital und analog archiviert
- Projektstrukturen (z.B. AG-Angebote) werden in den Regelbet rieb überführt

**Personelle Nachhaltigkeit:**
- Fortgebildete Lehrkräfte geben ihr Wissen als Multiplikatoren im Kollegium weiter
- Projektverantwortliche bleiben auch nach Projektende als Ansprechpersonen aktiv
- Einarbeitung neuer Lehrkräfte in die Projektthematik wird institutionalisiert

**Inhaltliche Nachhaltigkeit:**
- Integration der Projektinhalte in das Schulprogramm und Schulcurriculum
- Verstetigung erfolgreicher Maßnahmen durch Aufnahme in die Schulentwicklungsplanung
- Kontinuierliche Weiterentwicklung basierend auf Evaluationsergebnissen

### 5.2 Anschlussfinanzierung

Nach Abschluss der Förderphase sind keine oder nur geringe zusätzliche Mittel erforderlich:

- **Sachkosten:** Einmalig beschaffte Ausstattung ist langfristig nutzbar
- **Personalkosten:** Integration in bestehende Stellenressourcen (keine Neueinstellungen erforderlich)
- **Fortbildungen:** Interne Multiplikation des Wissens reduziert externen Fortbildungsbedarf
- **Kleinteilige Folgekosten:** Deckung aus dem regulären Schulbudget möglich

---

## 6. Budget und Finanzierungsplan

### 6.1 Gesamtfinanzierung

**Beantragte Fördersumme:** {requested_formatted}€
**Eigenanteil / Drittmittel:** 0€
**Gesamtbudget:** {requested_formatted}€

### 6.2 Budgetaufstellung nach Kostenpositionen

Die beantragten Fördermittel werden transparent, wirtschaftlich und zielgerichtet für die Projektumsetzung eingesetzt:

| Nr. | Budgetposition | Betrag (€) | Anteil | Verwendung |
|-----|----------------|------------|--------|------------|
| 1 | **Sachmittel & Ausstattung** | {sachmittel_fmt}€ | 40% | Lernmaterialien, Medien, technische Ausstattung, Verbrauchsmaterialien |
| 2 | **Honorare & Dienstleistungen** | {honorare_fmt}€ | 30% | Externe Expertise, Workshops, Coaching, Beratung, künstlerische/pädagogische Honorare |
| 3 | **Fortbildung & Qualifizierung** | {fortbildung_fmt}€ | 20% | Lehrkräfte-Fortbildungen, Fachliteratur, Teilnahme an Fachtagungen |
| 4 | **Dokumentation & Öffentlichkeitsarbeit** | {doku_fmt}€ | 10% | Projektdokumentation, Druckkosten, Abschlussveranstaltung, Foto/Video |
| | **Gesamtsumme** | **{requested_formatted}€** | **100%** | |

### 6.3 Erläuterungen zu den Budgetpositionen

**1. Sachmittel & Ausstattung (40% / {sachmittel_fmt}€)**

Beschaffung aller notwendigen Materialien und Ausstattung zur Projektumsetzung, z.B.:
- Lernmaterialien, Spiele, Bücher für die Projektarbeit
- Technische Geräte (Tablets, Beamer, Audio-Equipment) soweit erforderlich
- Verbrauchsmaterialien für Projektaktivitäten
- Möbel oder Raumausstattung bei Bedarf

**2. Honorare & Dienstleistungen (30% / {honorare_fmt}€)**

Einbindung externer Fachkräfte zur Bereicherung und Professionalisierung des Projekts:
- Workshops mit externen Referenten/Künstlern/Pädagogen
- Coaching und Beratung für das Projektteam
- Honorare für Spezialisten im jeweiligen Projektthema
- Dienstleistungen (z.B. technischer Support, Grafikdesign)

**3. Fortbildung & Qualifizierung (20% / {fortbildung_fmt}€)**

Professionalisierung des pädagogischen Personals:
- Externe Fortbildungen für Lehrkräfte zum Projektthema
- Fachliteratur und Methodenhandbücher
- Teilnahme an Fachtagungen und Netzwerktreffen
- Interne Schulungsmaßnahmen

**4. Dokumentation & Öffentlichkeitsarbeit (10% / {doku_fmt}€)**

Sicherung der Projektergebnisse und Wissenstransfer:
- Erstellung einer umfassenden Projektdokumentation
- Druck von Handreichungen und Materialien
- Foto- und Videodokumentation
- Öffentlichkeitswirksame Abschlussveranstaltung
- Informationsmaterialien für Presse und Öffentlichkeit

Ein detaillierter Kosten- und Finanzierungsplan mit konkreten Einzelpositionen wird als Anlage beigefügt.

---

## 7. Projektorganisation und Verantwortlichkeiten

### 7.1 Projektteam

**Projektleitung:**
[Name und Funktion der Projektleitung einzufügen]
Verantwortlich für Gesamtkoordination, Budgetverwaltung, Berichtswesen gegenüber Fördergeber

**Stellvertretende Projektleitung:**
[Name und Funktion einzufügen]
Unterstützung der Projektleitung, Vertretung bei Abwesenheit

**Projektteam (5-7 Personen):**
- Lehrkräfte aus verschiedenen Fachbereichen
- Elternvertreter/-in
- ggf. Schulsozialarbeit
- ggf. externe Kooperationspartner

### 7.2 Projektsteuerung

**Projektsitzungen:** Monatlich, Dokumentation in Sitzungsprotokollen
**Berichtswesen:** Zwischenbericht nach 6 Monaten, Abschlussbericht nach Projektende
**Qualitätszirkel:** Vierteljährliche Reflexionstreffen zur Qualitätssicherung
**Schulleitung:** Unterstützung und organisatorische Rahmenbedingungen

Das Projektteam bringt umfangreiche Erfahrung in der Projektarbeit, pädagogischen Innovation und Zusammenarbeit mit externen Partnern mit.

---

## 8. Zusammenfassung und Ausblick

Mit dem beantragten Projekt möchten wir einen wesentlichen Beitrag zur Qualitätsentwicklung der {school_name} leisten und unseren Schülerinnen und Schülern neue, zukunftsweisende Lern- und Entwicklungschancen eröffnen.

Das Projekt ist perfekt auf die Zielsetzung des Förderprogramms "{funding_title}" von {provider} abgestimmt und erfüllt alle Förderkriterien. Durch die systematische Planung, professionelle Umsetzung und wissenschaftliche Evaluation erwarten wir nachhaltig positive Wirkungen für unsere gesamte Schulgemeinschaft.

Wir sind überzeugt, dass das Projekt nicht nur kurzfristige Effekte erzielen wird, sondern langfristig die Schulentwicklung prägt und als Best-Practice-Beispiel auch für andere Schulen dienen kann.

Die {school_name} verfügt über alle notwendigen Voraussetzungen für eine erfolgreiche Projektumsetzung und bittet um Förderung in Höhe von **{requested_formatted}€**.

---

**Antragsdatum:** {datetime.now().strftime('%d.%m.%Y')}
**Entwurf generiert mit KI-Unterstützung**

*Dieser Antragsentwurf wurde KI-gestützt erstellt und stellt einen professionellen Ausgangspunkt dar. Bitte überprüfen und ergänzen Sie alle Abschnitte mit schulspezifischen Details, Namen und konkreten Zahlen vor der finalen Einreichung bei {provider}.*

---

## Erforderliche Anlagen (separat beizufügen)

- [ ] Detaillierter Kosten- und Finanzierungsplan (Excel)
- [ ] Zeitplan / Gantt-Chart
- [ ] Beschluss der Schulkonferenz
- [ ] Zustimmung des Schulträgers
- [ ] Kooperationsvereinbarungen (falls externe Partner beteiligt)
- [ ] Nachweis der Gemeinnützigkeit / Trägerschaft
- [ ] ggf. weitere programmspezifische Nachweise laut Förderrichtlinie
"""

    return mock_draft.strip()


def generate_deepseek_draft(
    funding_data: dict,
    user_query: str,
    school_profile: dict
) -> str:
    """
    Generate real AI draft using DeepSeek API with enhanced prompts

    Uses multi-stage approach:
    1. Build comprehensive prompt from funding + school context
    2. Call DeepSeek with structured system/user prompts
    3. Fallback to mock if API fails

    Args:
        funding_data: Complete funding opportunity details
        user_query: User's project description
        school_profile: School information

    Returns:
        Generated markdown draft or mock fallback
    """
    # Check if API key is configured
    api_key = os.getenv("DEEPSEEK_API_KEY", "")
    if not api_key or api_key == "sk-placeholder":
        logger.warning("DeepSeek API key not configured, falling back to mock")
        return generate_mock_draft(funding_data, user_query, school_profile)

    # Build enhanced system prompt
    system_prompt = """Du bist ein erfahrener Förderantrag-Experte für deutsche Grundschulen mit 15+ Jahren Erfahrung.
Du hast über 200 erfolgreiche Anträge begleitet und kennst die Erfolgsfaktoren genau.

Deine Aufgabe: Erstelle einen professionellen, überzeugenden Förderantrag in deutscher Sprache.

QUALITÄTSKRITERIEN:
✅ Konkrete Zahlen, Fakten und messbare Ziele (SMART-Formulierung)
✅ Klare Struktur mit 8 Hauptabschnitten
✅ Positive, selbstbewusste Sprache (KEIN Konjunktiv)
✅ Budget detailliert aufgeschlüsselt und begründet
✅ Evaluation mit messbaren Indikatoren
✅ Nachhaltigkeit über Projektlaufzeit hinaus

VERMEIDE:
❌ Floskeln und Allgemeinplätze
❌ Passive Formulierungen
❌ Vage Angaben ohne Zahlen
❌ Generische Phrasen

Erstelle den Antrag als strukturiertes Markdown-Dokument."""

    # Build comprehensive user prompt with all context
    funding_title = funding_data.get('title', 'Unbekanntes Förderprogramm')
    provider = funding_data.get('provider', 'Unbekannter Anbieter')
    description = funding_data.get('description', '')
    eligibility = funding_data.get('eligibility', '')
    categories = funding_data.get('categories', '')
    target_groups = funding_data.get('target_groups', '')
    max_amount = funding_data.get('funding_amount_max', 50000)
    min_amount = funding_data.get('funding_amount_min', 0)
    deadline = funding_data.get('application_deadline', '')

    school_name = school_profile.get('school_name', 'Grundschule Musterberg')
    school_address = school_profile.get('address', 'Adresse wird nachgetragen')

    # Format amounts
    if min_amount and max_amount:
        funding_range = f"{min_amount:,.0f}€ - {max_amount:,.0f}€".replace(',', '.')
    elif max_amount:
        funding_range = f"bis {max_amount:,.0f}€".replace(',', '.')
    else:
        funding_range = "Nicht spezifiziert"

    user_prompt = f"""Erstelle einen vollständigen Förderantrag für folgende Situation:

**FÖRDERPROGRAMM:**
- Titel: {funding_title}
- Anbieter: {provider}
- Förderkategorien: {categories or 'Allgemeine Bildungsförderung'}
- Zielgruppen: {target_groups or 'Grundschulen'}
- Fördersumme: {funding_range}
- Bewerbungsfrist: {deadline or 'Siehe Ausschreibung'}

**PROGRAMMBESCHREIBUNG:**
{description[:1000] if description else 'Siehe Ausschreibung'}

**FÖRDERKRITERIEN:**
{eligibility[:800] if eligibility else 'Siehe Ausschreibung'}

**ANTRAGSTELLENDE SCHULE:**
- Name: {school_name}
- Adresse: {school_address}
- Schultyp: Grundschule
- Trägerschaft: Öffentlicher Träger

**PROJEKTIDEE (vom Nutzer beschrieben):**
{user_query}

═══════════════════════════════════════════════════════════════════

Erstelle einen überzeugenden Antrag mit folgender Struktur:

## 1. Executive Summary (max. 300 Wörter)
- Kernproblem + Lösung + erwartete Wirkung
- Beantragte Summe + Laufzeit
- Einzigartigkeit/Innovation

## 2. Ausgangslage und Bedarfsanalyse
- Schulkontext mit konkreten Zahlen
- Problemstellung messbar beschreiben
- Warum ist das Projekt jetzt dringend?

## 3. Projektziele
- 3-5 SMART-Ziele (Specific, Measurable, Achievable, Relevant, Time-bound)
- Kurz-, mittel-, langfristige Wirkung
- Tabelle mit Erfolgsindikatoren

## 4. Maßnahmenplan
- 3 Projektphasen: Vorbereitung, Durchführung, Verstetigung
- Timeline-Tabelle mit Meilensteinen
- Detaillierte Aktivitäten (keine Allgemeinplätze!)

## 5. Erfüllung der Förderkriterien
- Jedes Kriterium aus der Ausschreibung einzeln adressieren
- Konkrete Nachweise aus Schulprofil
- Alleinstellungsmerkmale hervorheben

## 6. Budget
- Gesamtsumme klar angeben
- Detaillierte Tabelle mit 4-8 Positionen
- Jede Position begründen
- Verteilung: ca. 40% Sachmittel, 30% Honorare, 20% Fortbildung, 10% Dokumentation

## 7. Qualitätssicherung und Evaluation
- Evaluationsdesign (formativ + summativ)
- Tabelle: Indikator | Messmethode | Zielwert
- Berichterstattung an Fördergeber

## 8. Nachhaltigkeit
- Wie geht es nach Projektende weiter?
- Anschlussfinanzierung
- Transferpotenzial für andere Schulen

WICHTIG:
- Nutze die Projektidee des Nutzers als Kerninhalt
- Passe Budget an max. Fördersumme an
- Integriere Förderkriterien explizit
- Verwende professionelle, aber verständliche Sprache
- Füge am Ende Hinweis ein: "Dieser Entwurf wurde KI-gestützt erstellt. Bitte ergänzen Sie schulspezifische Details vor Einreichung."

Erstelle jetzt den vollständigen Antrag:"""

    try:
        logger.info(f"Calling DeepSeek API for funding '{funding_title}' (school: {school_name})")

        response = deepseek_client.chat.completions.create(
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=float(os.getenv("DEEPSEEK_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("DEEPSEEK_MAX_TOKENS", "4096")),
            timeout=60.0
        )

        generated_content = response.choices[0].message.content

        logger.info(f"DeepSeek API success. Generated {len(generated_content)} characters")

        return generated_content.strip()

    except Exception as e:
        logger.error(f"DeepSeek API failed: {str(e)}", exc_info=True)
        logger.warning("Falling back to mock draft generator")
        return generate_mock_draft(funding_data, user_query, school_profile)


@router.post('/generate', response_model=DraftGenerateResponse)
async def generate_draft(
    request: DraftGenerateRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Generiert einen KI-Antragsentwurf (Mock-Modus für Entwicklung)

    In Production würde hier RAG + DeepSeek aufgerufen
    """
    # 1. Verify Application Access
    app_query = """
    SELECT school_id
    FROM APPLICATIONS
    WHERE application_id = ?
    """

    with get_db_cursor() as cursor:
        cursor.execute(app_query, (request.application_id,))
        app_row = cursor.fetchone()

    if not app_row:
        raise HTTPException(status_code=404, detail='Application not found')

    if app_row['school_id'] != current_user['school_id']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Access denied'
        )

    # 2. Get Full Funding Details
    funding_query = """
    SELECT
        title,
        provider,
        description,
        eligibility,
        funding_amount_min,
        funding_amount_max,
        application_deadline,
        categories,
        target_groups,
        cleaned_text
    FROM FUNDING_OPPORTUNITIES
    WHERE funding_id = ?
    """

    with get_db_cursor() as cursor:
        cursor.execute(funding_query, (request.funding_id,))
        funding_row = cursor.fetchone()

        if not funding_row:
            raise HTTPException(status_code=404, detail='Funding not found')

        funding_data = {
            'title': funding_row['title'],
            'provider': funding_row['provider'],
            'description': funding_row['description'] or '',
            'eligibility': funding_row['eligibility'] or '',
            'funding_amount_min': funding_row['funding_amount_min'],
            'funding_amount_max': funding_row['funding_amount_max'],
            'application_deadline': funding_row['application_deadline'],
            'categories': funding_row['categories'] or '',
            'target_groups': funding_row['target_groups'] or '',
            'cleaned_text': funding_row['cleaned_text'] or ''
        }

    # 3. Get School Profile from Database
    school_query = """
    SELECT name, address, postal_code, city, contact_email, contact_phone
    FROM SCHOOLS
    WHERE school_id = ?
    """

    with get_db_cursor() as cursor:
        cursor.execute(school_query, (current_user['school_id'],))
        school_row = cursor.fetchone()

        if not school_row:
            raise HTTPException(status_code=404, detail='School not found')

        # Build school profile with real data
        school_profile = {
            'school_name': school_row['name'],
            'school_number': 'wird nachgetragen',  # Optional field, not in DB yet
            'address': f"{school_row['address']}, {school_row['postal_code']} {school_row['city']}" if school_row['address'] else 'Adresse wird nachgetragen',
            'schultyp': 'Grundschule',  # Default for this project
            'schuelerzahl': 'wird nachgetragen',  # Optional field, not in DB yet
            'traeger': 'Öffentlicher Träger'  # Default for this project
        }

    # 4. Generate Draft - Priority: DeepSeek > Advanced > Mock
    # Try DeepSeek first (real AI generation)
    try:
        logger.info(f'[DRAFT] Using DeepSeek API for app {request.application_id}')
        generated_content = generate_deepseek_draft(
            funding_data=funding_data,
            user_query=request.user_query,
            school_profile=school_profile
        )
        # Check if it actually used DeepSeek (not fallback to mock)
        if os.getenv("DEEPSEEK_API_KEY", "sk-placeholder") != "sk-placeholder":
            ai_model = 'deepseek-chat'
        else:
            ai_model = 'mock-development'
    except Exception as e:
        logger.error(f'[ERROR] DeepSeek generator failed: {e}')
        # Try advanced generator as fallback
        if USE_ADVANCED_GENERATOR:
            try:
                logger.info('[DRAFT] Falling back to Advanced Context-Aware Generator')
                generated_content = generate_advanced_draft(
                    funding_id=request.funding_id,
                    user_query=request.user_query,
                    application_id=request.application_id,
                    school_id=current_user['school_id']
                )
                ai_model = 'advanced-context-aware-v2'
            except Exception as e2:
                logger.error(f'[ERROR] Advanced generator also failed: {e2}')
                logger.info('[DRAFT] Final fallback to mock generator')
                generated_content = generate_mock_draft(funding_data, request.user_query, school_profile)
                ai_model = 'mock-development'
        else:
            logger.info('[DRAFT] Falling back to mock generator')
            generated_content = generate_mock_draft(funding_data, request.user_query, school_profile)
            ai_model = 'mock-development'

    # 5. Save Draft to Database
    draft_id = generate_id()

    insert_query = """
    INSERT INTO APPLICATION_DRAFTS (
        draft_id,
        application_id,
        draft_text,
        ai_model,
        prompt_used
    ) VALUES (?, ?, ?, ?, ?)
    """

    with get_db_cursor() as cursor:
        cursor.execute(insert_query, (
            draft_id,
            request.application_id,
            generated_content,
            ai_model,  # Use the determined model name
            f'User query: {request.user_query}'
        ))

    return DraftGenerateResponse(
        draft_id=draft_id,
        application_id=request.application_id,
        generated_content=generated_content,
        model_used=ai_model,  # Show which generator was used
        created_at=datetime.now()
    )


@router.get('/application/{application_id}', response_model=List[DraftGenerateResponse])
async def get_drafts_for_application(
    application_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Holt alle Entwürfe für einen Antrag
    """
    # Verify Access (via applications router)
    from api.routers.applications_sqlite import get_application
    await get_application(application_id, current_user)

    # Get Drafts
    query = """
    SELECT
        draft_id,
        application_id,
        draft_text,
        ai_model,
        created_at
    FROM APPLICATION_DRAFTS
    WHERE application_id = ?
    ORDER BY created_at DESC
    """

    with get_db_cursor() as cursor:
        cursor.execute(query, (application_id,))

        results = []
        for row in cursor:
            # Map SQLite column names to API model field names
            data = {
                'draft_id': row['draft_id'],
                'application_id': row['application_id'],
                'generated_content': row['draft_text'],  # Map draft_text → generated_content
                'model_used': row['ai_model'],  # Map ai_model → model_used
                'created_at': row['created_at']
            }
            results.append(DraftGenerateResponse(**data))

    return results


@router.post('/feedback')
async def submit_feedback(
    feedback: DraftFeedback,
    current_user: dict = Depends(get_current_user)
):
    """
    Nutzer-Feedback zu einem generierten Entwurf
    """
    update_query = """
    UPDATE APPLICATION_DRAFTS
    SET user_feedback = ?
    WHERE draft_id = ?
    """

    with get_db_cursor() as cursor:
        cursor.execute(update_query, (
            feedback.feedback,
            feedback.draft_id
        ))

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail='Draft not found')

    return {'message': 'Feedback submitted successfully'}
