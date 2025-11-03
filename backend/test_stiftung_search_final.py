#!/usr/bin/env python3
import sqlite3

# Test direkt in DB
conn = sqlite3.connect('dev_database.db')
cursor = conn.cursor()

print("📊 STATISTIK\n" + "="*70)

cursor.execute("SELECT COUNT(*) FROM STIFTUNGEN")
print(f"Stiftungen (strukturiert): {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM FUNDING_OPPORTUNITIES WHERE source_type='stiftung'")
print(f"Stiftungen in RAG-Index: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM FUNDING_OPPORTUNITIES")
print(f"Gesamt Fördermöglichkeiten: {cursor.fetchone()[0]}")

print("\n🎯 TOP 10 STIFTUNGEN\n" + "="*70)
cursor.execute("""
    SELECT name, bundesland, foerdersumme_min, foerdersumme_max, 
           json_extract(foerderbereiche, '$[0]') as bereich1
    FROM STIFTUNGEN
    ORDER BY created_at DESC
    LIMIT 10
""")

for row in cursor.fetchall():
    name, land, min_sum, max_sum, bereich = row
    foerderung = f"{int(min_sum) if min_sum else '?'}€ - {int(max_sum) if max_sum else '?'}€" if min_sum or max_sum else "Keine Angabe"
    print(f"\n✅ {name}")
    print(f"   Region: {land or 'N/A'}")
    print(f"   Fördersumme: {foerderung}")
    if bereich:
        print(f"   Bereich: {bereich}")

print("\n\n🔍 TEST-SUCHE: 'MINT Bildung Grundschule'\n" + "="*70)
cursor.execute("""
    SELECT title, funder_name, region, source_type
    FROM FUNDING_OPPORTUNITIES
    WHERE source_type = 'stiftung'
    AND (
        cleaned_text LIKE '%MINT%' OR
        cleaned_text LIKE '%Grundschule%' OR
        cleaned_text LIKE '%Bildung%'
    )
    LIMIT 5
""")

for row in cursor.fetchall():
    print(f"\n📌 {row[0]}")
    print(f"   Förderer: {row[1]}")
    print(f"   Region: {row[2]}")

conn.close()
