# ✅ STUFE 2: URLs Kuratieren - ABGESCHLOSSEN

**Datum**: 2025-10-30
**Status**: Kuratierung erfolgreich, aber Firecrawl instabil

---

## 📊 Analyse-Ergebnisse

### Vor Kuratierung (34 Quellen)
- **Total**: 34 konfigurierte Funding-Sources
- **Produktiv**: 27 Quellen liefern Daten (51 Programme)
- **Unproduktiv**: 7 Quellen liefern 0 Einträge
- **Erfolgsrate**: 79%

### Nach Kuratierung (22 Quellen)
- **Total**: 22 kuratierte Top-Performer
- **Reduktion**: 35% weniger Quellen
- **Erwartete Erfolgsrate**: ~85-90%
- **Erwartete Programme**: 50-70 high-quality entries

---

## 🎯 Kuratierte Quellen (22)

### TIER 1: Top Performer (≥4 Einträge)
1. **Robert Bosch Stiftung** (5 Einträge)
2. **Land Brandenburg / MBJS** (5 Einträge)
3. **Stiftung Bildung** (4 Einträge)
4. **Bertelsmann Stiftung** (4 Einträge)

### TIER 2: Gute Performer (2-3 Einträge)
5. **EU / PAD (Erasmus+)** (3 Einträge)
6. **Deutsche Telekom Stiftung** (3 Einträge)
7. **Thüringen / Kultusministerium** (2 Einträge)
8. **Rheinland-Pfalz / Bildungsministerium** (2 Einträge)
9. **Kulturstiftung der Länder** (2 Einträge)
10. **JeKits-Stiftung / Land NRW** (2 Einträge)
11. **Deutsche Bundesstiftung Umwelt** (2 Einträge)
12. **Bremen / Bildungssenatorin** (2 Einträge)

### TIER 3: Strategisch wichtig (1 Eintrag)
13. **BMBF / BMFSFJ** (Startchancen-Programm)
14. **DigitalPakt Schule**
15. **Baden-Württemberg**
16. **Hessen**
17. **Niedersachsen**
18. **Berlin**
19. **Stiftung Kinder forschen**
20. **DZLM Mathematik**
21. **Fitness für Kids**
22. **Verschiedene Regionalstiftungen**

---

## ❌ Entfernte Quellen (0 Einträge)

1. **Joachim Herz Stiftung** - Keine Grundschul-Programme gefunden
2. **Bayern / Kultusministerium** - URLs nicht produktiv
3. **NRW / Schulministerium** - URLs nicht produktiv
4. **Sachsen / Kultusministerium** - URLs nicht produktiv
5. **Saarland / Bildungsministerium** - URLs nicht produktiv
6. **Hamburg / Schulbehörde** - URLs nicht produktiv
7. **Stiftung Lesen** - URLs nicht produktiv
8. **Land NRW Lese-Programme** - Duplicate/unproduktiv
9. **Schleswig-Holstein** - Niedrige Priorität
10. **Mecklenburg-Vorpommern** - Niedrige Priorität
11. **Sachsen-Anhalt** - Niedrige Priorität (später: 1 Eintrag gefunden)

---

## 🚀 Deployment Status

✅ **Kuratierte funding_sources.py erstellt**
- 22 Quellen (reduziert von 34)
- Fokus auf Top-Performer
- Backup der alten Version: `funding_sources_old_backup.py`

✅ **Deployed zu Production**
- Server: 130.61.76.199
- Pfad: `/opt/foerder-finder-backend/scraper_firecrawl/funding_sources.py`
- Verifiziert: 22 Quellen auf Production aktiv

---

## ⚠️ Firecrawl Problem Identifiziert

### Symptome
- **400 Bad Request** Errors von Firecrawl API
- **SCRAPE_ALL_ENGINES_FAILED** - Playwright + Fetch schlagen beide fehl
- **SCRAPE_TIMEOUT** - Requests laufen in Timeout
- Restart hilft nur kurzzeitig

### Root Cause
Self-hosted Firecrawl (130.61.137.77:3002) ist **instabil**:
- Beide Scraping-Engines versagen systematisch
- Playwright kann Seiten nicht rendern
- Fetch engine kann URLs auch nicht laden
- Möglicherweise Ressourcenproblem (Memory/CPU)

### Getestete Fixes
- ✅ Firecrawl Container Restart → Funktioniert kurz, dann wieder Fehler
- ✅ Manueller Test: `curl` Requests funktionieren → Problem ist im Firecrawl Worker
- ❌ Systematische Batch-Scrapes schlagen fehl

---

## 💡 EMPFEHLUNG: STUFE 3 - Migration zu Crawl4AI

### Warum Crawl4AI?
1. **Production-Ready**: Im Gegensatz zu self-hosted Firecrawl
2. **Schneller**: Optimiert für Batch-Scraping
3. **Ressourcenschonend**: Geringerer Memory/CPU Footprint
4. **Besser maintained**: Aktive Community, regelmäßige Updates
5. **Kostenlos & Open Source**: Apache 2.0 License
6. **LLM-Integration**: Native Support für OpenAI/DeepSeek extraction
7. **Keine Infrastruktur**: Läuft direkt im Python-Prozess (keine Docker)

### Migration-Aufwand
- **Geschätzte Zeit**: 2-3 Stunden
- **Änderungen**:
  - `firecrawl_scraper.py` → `crawl4ai_scraper.py` (Adapter)
  - `requirements.txt` ergänzen
  - `scrape_all_sources.py` minimal anpassen
- **Risiko**: Niedrig (alte Version bleibt als Backup)

### Alternative
- Firecrawl Cloud Service nutzen ($$$)
- Firecrawl Server upgraden/debuggen (zeitaufwändig)
- Zu Scrapy zurückkehren (verlieren LLM-Fähigkeit)

---

## 📈 Erwartete Verbesserungen mit Crawl4AI

| Metrik | Firecrawl | Crawl4AI (erwartet) |
|--------|-----------|---------------------|
| Erfolgsrate | 0% (aktuell instabil) | 85-90% |
| Scrape-Zeit | n/a (schlägt fehl) | ~3-5 Min für 22 Quellen |
| Ressourcen | Dedizierter VM Server | Inline (Backend Server) |
| Wartung | Docker + Worker Management | Zero (Python Library) |
| Kosten | VM + Maintenance | $0 |
| Stabilität | Instabil | Production-ready |

---

## 🎯 Nächste Schritte

### Option A: STUFE 3 Migration (Empfohlen)
1. Crawl4AI installieren & testen
2. `crawl4ai_scraper.py` implementieren
3. Vergleichstest: Crawl4AI vs. Firecrawl
4. Bei Erfolg: Production Deployment
5. Firecrawl Server deaktivieren

### Option B: Firecrawl Debugging
1. Playwright Worker Logs analysieren
2. Memory/CPU Monitoring einrichten
3. Ressourcenlimits erhöhen
4. Retry-Logic optimieren
5. (Zeitaufwändig, unsichere Erfolgsaussicht)

---

## ✅ Was wurde erreicht (STUFE 2)

1. ✅ **Analyse abgeschlossen**: 34 → 22 Quellen kuratiert
2. ✅ **Kuratierte Liste erstellt**: Fokus auf Top-Performer
3. ✅ **Deployment**: Production Server aktualisiert
4. ✅ **Problem identifiziert**: Firecrawl instabil → Migration nötig

---

**FAZIT**: STUFE 2 Kuratierung erfolgreich, aber Firecrawl zeigt sich als Blocker. **Migration zu Crawl4AI (STUFE 3) dringend empfohlen** für stabilen Production-Betrieb.

**Status**: ⚠️ Teilweise erfolgreich (Kuratierung ✅, Scraping ❌)
**Nächster Schritt**: STUFE 3 - Crawl4AI Migration
