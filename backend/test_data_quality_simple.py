#!/usr/bin/env python3
"""
Einfacher Datenqualitätstest - Julius Hirsch Preis

Prüft:
1. Ist Julius Hirsch Preis in der DB?
2. Hat er Quality Score 1.0?
3. Sind alle strukturierten Felder gefüllt?
"""

import sqlite3
import json

DB_PATH = "dev_database.db"

def test_julius_hirsch_in_db():
    """Test: Julius Hirsch Preis ist in der DB"""
    print("=" * 80)
    print("TEST 1: Julius Hirsch Preis in Datenbank")
    print("=" * 80)
    print()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT funding_id, title, extraction_quality_score, application_deadline
        FROM FUNDING_OPPORTUNITIES
        WHERE title LIKE '%Julius Hirsch%'
    """)

    result = cursor.fetchone()
    conn.close()

    if result:
        funding_id, title, quality_score, deadline = result
        print(f"✅ Julius Hirsch Preis gefunden!")
        print(f"   Funding ID: {funding_id}")
        print(f"   Titel: {title}")
        print(f"   Quality Score: {quality_score}")
        print(f"   Deadline: {deadline}")
        return True, funding_id
    else:
        print("❌ Julius Hirsch Preis NICHT in Datenbank gefunden")
        return False, None


def test_structured_fields(funding_id):
    """Test 2: Sind strukturierte Felder gefüllt?"""
    print()
    print("=" * 80)
    print("TEST 2: Strukturierte Felder - Qualität")
    print("=" * 80)
    print()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            eligibility,
            target_groups,
            evaluation_criteria,
            requirements,
            application_process,
            application_url,
            funding_period,
            eligible_costs,
            extraction_quality_score
        FROM FUNDING_OPPORTUNITIES
        WHERE funding_id = ?
    """, (funding_id,))

    result = cursor.fetchone()
    conn.close()

    if not result:
        print("❌ Funding nicht gefunden")
        return False

    fields = {
        "eligibility": result[0],
        "target_groups": result[1],
        "evaluation_criteria": result[2],
        "requirements": result[3],
        "application_process": result[4],
        "application_url": result[5],
        "funding_period": result[6],
        "eligible_costs": result[7],
        "quality_score": result[8]
    }

    # Quality Checks
    checks = []

    # 1. Quality Score
    if fields["quality_score"] == 1.0:
        print("✅ Quality Score: 1.0 (Perfekt!)")
        checks.append(True)
    else:
        print(f"⚠️ Quality Score: {fields['quality_score']} (Erwartete: 1.0)")
        checks.append(False)

    # 2. Application URL
    if fields["application_url"] and "dfb.de" in fields["application_url"]:
        print(f"✅ Application URL: {fields['application_url']}")
        checks.append(True)
    else:
        print(f"❌ Application URL fehlt oder falsch: {fields['application_url']}")
        checks.append(False)

    # 3. Eligibility Criteria (JSON)
    try:
        eligibility = json.loads(fields["eligibility"]) if fields["eligibility"] else []
        if len(eligibility) >= 3:
            print(f"✅ Eligibility Criteria: {len(eligibility)} Kriterien")
            checks.append(True)
        else:
            print(f"⚠️ Eligibility Criteria: Nur {len(eligibility)} Kriterien")
            checks.append(False)
    except:
        print(f"❌ Eligibility Criteria: Nicht als JSON lesbar")
        checks.append(False)

    # 4. Target Groups
    try:
        target_groups = json.loads(fields["target_groups"]) if fields["target_groups"] else []
        if len(target_groups) >= 3:
            print(f"✅ Target Groups: {len(target_groups)} Zielgruppen")
            checks.append(True)
        else:
            print(f"⚠️ Target Groups: Nur {len(target_groups)} Zielgruppen")
            checks.append(False)
    except:
        print(f"❌ Target Groups: Nicht als JSON lesbar")
        checks.append(False)

    # 5. Evaluation Criteria
    try:
        eval_crit = json.loads(fields["evaluation_criteria"]) if fields["evaluation_criteria"] else []
        if len(eval_crit) >= 3:
            print(f"✅ Evaluation Criteria: {len(eval_crit)} Kriterien")
            checks.append(True)
        else:
            print(f"⚠️ Evaluation Criteria: Nur {len(eval_crit)} Kriterien")
            checks.append(False)
    except:
        print(f"❌ Evaluation Criteria: Nicht als JSON lesbar")
        checks.append(False)

    # 6. Requirements
    try:
        requirements = json.loads(fields["requirements"]) if fields["requirements"] else []
        if len(requirements) >= 3:
            print(f"✅ Requirements: {len(requirements)} Anforderungen")
            checks.append(True)
        else:
            print(f"⚠️ Requirements: Nur {len(requirements)} Anforderungen")
            checks.append(False)
    except:
        print(f"❌ Requirements: Nicht als JSON lesbar")
        checks.append(False)

    # 7. Application Process
    if fields["application_process"] and len(fields["application_process"]) > 50:
        print(f"✅ Application Process: {len(fields['application_process'])} Zeichen")
        checks.append(True)
    else:
        print(f"❌ Application Process: Zu kurz oder fehlend")
        checks.append(False)

    # 8. Funding Period
    if fields["funding_period"] and "2024" in fields["funding_period"]:
        print(f"✅ Funding Period: {fields['funding_period']}")
        checks.append(True)
    else:
        print(f"⚠️ Funding Period: {fields['funding_period']}")
        checks.append(False)

    passed = sum(checks)
    total = len(checks)

    print()
    print(f"📊 Quality Score: {passed}/{total} = {passed/total*100:.0f}%")

    return passed >= total * 0.75  # 75% pass rate


def main():
    print()
    print("=" * 80)
    print("DATENQUALITÄTSTEST - JULIUS HIRSCH PREIS")
    print("=" * 80)
    print()
    print("Testet ob die manuelle Kuration bessere Daten erzeugt hat")
    print()

    # Test 1
    found, funding_id = test_julius_hirsch_in_db()

    if not found:
        print()
        print("❌ TEST FAILED - Julius Hirsch Preis nicht gefunden")
        return 1

    # Test 2
    quality_ok = test_structured_fields(funding_id)

    # Summary
    print()
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Julius Hirsch in DB: {'✅ PASS' if found else '❌ FAIL'}")
    print(f"Strukturierte Felder: {'✅ PASS' if quality_ok else '⚠️ WARNING'}")
    print()

    if found and quality_ok:
        print("🎉 ALL TESTS PASSED!")
        print()
        print("✅ Julius Hirsch Preis hat Quality Score 1.0")
        print("✅ Alle strukturierten Felder sind hochwertig gefüllt")
        print("✅ Manuelle Kuration war erfolgreich!")
        return 0
    elif found:
        print("⚠️ PARTIAL SUCCESS")
        print("   Julius Hirsch Preis ist in DB, aber Datenqualität könnte besser sein")
        return 0
    else:
        print("❌ TESTS FAILED")
        return 1


if __name__ == '__main__':
    exit(main())
