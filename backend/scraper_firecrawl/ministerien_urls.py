#!/usr/bin/env python3
"""
Ministerien & öffentliche Förderdatenbanken für Grundschulen

Fokus: Bundesweite und landesspezifische Bildungsförderung
Priorisierung: Strukturierte Förder-Datenbanken (bessere Quality Scores)

Author: Claude Code
Version: 1.0
Date: 2025-10-29
"""

# URLs für Ministerien, Ämter und öffentliche Förderdatenbanken
MINISTERIEN_URLS = {
    # ===== BUNDESEBENE (Priorität: HOCH) =====
    'bund': [
        {
            'url': 'https://www.bmbf.de/bmbf/de/forschung/bildungsforschung/bildungsforschung_node.html',
            'name': 'BMBF - Bildungsforschung',
            'type': 'bund',
            'priority': 'high',
            'notes': 'Bundesministerium für Bildung und Forschung - Hauptquelle für MINT-Förderung'
        },
        {
            'url': 'https://www.foerderdatenbank.de/FDB/DE/Home/home.html',
            'name': 'Förderdatenbank des Bundes',
            'type': 'bund',
            'priority': 'high',
            'notes': 'Zentrale Datenbank aller Bundesförderungen - sehr strukturiert'
        },
        {
            'url': 'https://www.kmk.org/themen/allgemeinbildende-schulen/digitale-bildung.html',
            'name': 'KMK - Digitale Bildung',
            'type': 'bund',
            'priority': 'high',
            'notes': 'Kultusministerkonferenz - DigitalPakt Schule'
        },
    ],

    # ===== BUNDESLÄNDER (alphabetisch) =====

    # Baden-Württemberg
    'bw': [
        {
            'url': 'https://km-bw.de/,Lde/startseite/schule/Foerderung',
            'name': 'Kultusministerium Baden-Württemberg',
            'type': 'land',
            'bundesland': 'Baden-Württemberg',
            'priority': 'medium'
        },
    ],

    # Bayern
    'by': [
        {
            'url': 'https://www.km.bayern.de/ministerium/foerderungen.html',
            'name': 'Kultusministerium Bayern',
            'type': 'land',
            'bundesland': 'Bayern',
            'priority': 'medium'
        },
    ],

    # Berlin
    'be': [
        {
            'url': 'https://www.berlin.de/sen/bildung/schule/foerderung/',
            'name': 'Senatsverwaltung für Bildung Berlin',
            'type': 'land',
            'bundesland': 'Berlin',
            'priority': 'medium'
        },
    ],

    # Brandenburg
    'bb': [
        {
            'url': 'https://mbjs.brandenburg.de/bildung/foerderung.html',
            'name': 'Ministerium für Bildung Brandenburg',
            'type': 'land',
            'bundesland': 'Brandenburg',
            'priority': 'medium'
        },
    ],

    # Bremen
    'hb': [
        {
            'url': 'https://www.bildung.bremen.de/foerderung-3744',
            'name': 'Senatorin für Kinder und Bildung Bremen',
            'type': 'land',
            'bundesland': 'Bremen',
            'priority': 'medium'
        },
    ],

    # Hamburg
    'hh': [
        {
            'url': 'https://www.hamburg.de/bsb/foerderung/',
            'name': 'Behörde für Schule und Berufsbildung Hamburg',
            'type': 'land',
            'bundesland': 'Hamburg',
            'priority': 'medium'
        },
    ],

    # Hessen
    'he': [
        {
            'url': 'https://kultusministerium.hessen.de/Schulsystem/Foerderangebote',
            'name': 'Kultusministerium Hessen',
            'type': 'land',
            'bundesland': 'Hessen',
            'priority': 'medium'
        },
    ],

    # Mecklenburg-Vorpommern
    'mv': [
        {
            'url': 'https://www.regierung-mv.de/Landesregierung/bm/Bildung/Schule/Foerderung/',
            'name': 'Bildungsministerium Mecklenburg-Vorpommern',
            'type': 'land',
            'bundesland': 'Mecklenburg-Vorpommern',
            'priority': 'medium'
        },
    ],

    # Niedersachsen
    'ni': [
        {
            'url': 'https://www.mk.niedersachsen.de/startseite/schule/unsere_schulen/foerderung/',
            'name': 'Kultusministerium Niedersachsen',
            'type': 'land',
            'bundesland': 'Niedersachsen',
            'priority': 'medium'
        },
    ],

    # Nordrhein-Westfalen
    'nw': [
        {
            'url': 'https://www.schulministerium.nrw/schulsystem/foerderung',
            'name': 'Ministerium für Schule NRW',
            'type': 'land',
            'bundesland': 'Nordrhein-Westfalen',
            'priority': 'high',  # Größtes Bundesland
            'notes': 'Größtes Bundesland - viele Programme'
        },
    ],

    # Rheinland-Pfalz
    'rp': [
        {
            'url': 'https://bm.rlp.de/de/bildung/schule/foerderung/',
            'name': 'Bildungsministerium Rheinland-Pfalz',
            'type': 'land',
            'bundesland': 'Rheinland-Pfalz',
            'priority': 'medium'
        },
    ],

    # Saarland
    'sl': [
        {
            'url': 'https://www.saarland.de/mbk/DE/portale/bildungundkultur/bildungsserver/schule/foerderung/foerderung_node.html',
            'name': 'Ministerium für Bildung und Kultur Saarland',
            'type': 'land',
            'bundesland': 'Saarland',
            'priority': 'low'
        },
    ],

    # Sachsen
    'sn': [
        {
            'url': 'https://www.schule.sachsen.de/foerderung-4596.html',
            'name': 'SMK Sachsen - Förderung',
            'type': 'land',
            'bundesland': 'Sachsen',
            'priority': 'medium'
        },
    ],

    # Sachsen-Anhalt
    'st': [
        {
            'url': 'https://mb.sachsen-anhalt.de/themen/schule-und-unterricht/foerderung/',
            'name': 'Bildungsministerium Sachsen-Anhalt',
            'type': 'land',
            'bundesland': 'Sachsen-Anhalt',
            'priority': 'medium'
        },
    ],

    # Schleswig-Holstein
    'sh': [
        {
            'url': 'https://www.schleswig-holstein.de/DE/landesregierung/ministerien-behoerden/III/Service/Broschueren/Broschueren_Bildung/_documents/foerderung.html',
            'name': 'Bildungsministerium Schleswig-Holstein',
            'type': 'land',
            'bundesland': 'Schleswig-Holstein',
            'priority': 'medium'
        },
    ],

    # Thüringen
    'th': [
        {
            'url': 'https://bildung.thueringen.de/schule/foerderung/',
            'name': 'TMBJS Thüringen - Förderung',
            'type': 'land',
            'bundesland': 'Thüringen',
            'priority': 'medium'
        },
    ],

    # ===== WEITERE ÖFFENTLICHE INSTITUTIONEN =====
    'oeffentlich': [
        {
            'url': 'https://www.kfw.de/inlandsfoerderung/Privatpersonen/Neubau/F%C3%B6rderprodukte/Altersgerecht-Umbauen-Zuschuss-(455)/',
            'name': 'KfW - Bildungskredit',
            'type': 'bund',
            'priority': 'low',
            'notes': 'Fokus auf Infrastruktur, weniger auf Grundschulen'
        },
    ],
}


def get_all_urls():
    """
    Gibt flache Liste aller URLs zurück (für Scraping)

    Returns:
        List of dicts with url, name, type, priority
    """
    urls = []
    for category, entries in MINISTERIEN_URLS.items():
        for entry in entries:
            urls.append(entry)

    # Sortiere nach Priorität (high > medium > low)
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    urls.sort(key=lambda x: priority_order.get(x.get('priority', 'medium'), 1))

    return urls


def get_urls_by_priority(priority='high'):
    """
    Filtert URLs nach Priorität

    Args:
        priority: 'high', 'medium', 'low'

    Returns:
        List of URL dicts
    """
    all_urls = get_all_urls()
    return [u for u in all_urls if u.get('priority') == priority]


def get_urls_by_type(type_filter='bund'):
    """
    Filtert URLs nach Typ

    Args:
        type_filter: 'bund' oder 'land'

    Returns:
        List of URL dicts
    """
    all_urls = get_all_urls()
    return [u for u in all_urls if u.get('type') == type_filter]


if __name__ == '__main__':
    # Test: Zeige alle URLs
    print("="*80)
    print("MINISTERIEN & ÖFFENTLICHE FÖRDERDATENBANKEN")
    print("="*80)
    print()

    urls = get_all_urls()
    print(f"Total: {len(urls)} URLs\n")

    # Nach Priorität gruppiert
    for prio in ['high', 'medium', 'low']:
        prio_urls = get_urls_by_priority(prio)
        if prio_urls:
            print(f"\n{'='*80}")
            print(f"PRIORITÄT: {prio.upper()} ({len(prio_urls)} URLs)")
            print(f"{'='*80}")
            for u in prio_urls:
                print(f"\n{u['name']}")
                print(f"  URL: {u['url']}")
                print(f"  Typ: {u.get('type', 'N/A')}")
                if 'bundesland' in u:
                    print(f"  Bundesland: {u['bundesland']}")
                if 'notes' in u:
                    print(f"  Notiz: {u['notes']}")

    print(f"\n{'='*80}\n")
