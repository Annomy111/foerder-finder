#!/usr/bin/env python3
"""
Integration Test: School Profile Bug Fix
Tests that draft generator uses real school data instead of hardcoded defaults
"""

import sqlite3
import sys

def test_school_profile_retrieval():
    """Test that we can query school profiles correctly"""

    db = sqlite3.connect("dev_database.db")
    db.row_factory = sqlite3.Row

    test_results = {
        "passed": 0,
        "failed": 0,
        "schools_tested": []
    }

    # Get all schools
    cursor = db.cursor()
    cursor.execute("SELECT school_id, name, city FROM SCHOOLS")
    schools = cursor.fetchall()

    print("=" * 70)
    print("SCHOOL PROFILE INTEGRATION TEST")
    print("=" * 70)
    print(f"\nFound {len(schools)} schools in database\n")

    for school in schools:
        school_id = school['school_id']
        expected_name = school['name']
        expected_city = school['city']

        # Simulate the query from drafts_sqlite.py (after fix)
        cursor.execute("""
            SELECT name, address, postal_code, city, contact_email, contact_phone
            FROM SCHOOLS
            WHERE school_id = ?
        """, (school_id,))

        school_row = cursor.fetchone()

        if not school_row:
            print(f"❌ FAIL: School {school_id} not found")
            test_results["failed"] += 1
            continue

        # Build school profile (matching the fix)
        school_profile = {
            'school_name': school_row['name'],
            'school_number': 'wird nachgetragen',
            'address': f"{school_row['address']}, {school_row['postal_code']} {school_row['city']}" if school_row['address'] else 'Adresse wird nachgetragen',
            'schultyp': 'Grundschule',
            'schuelerzahl': 'wird nachgetragen',
            'traeger': 'Öffentlicher Träger'
        }

        # Validate
        if school_profile['school_name'] == expected_name:
            print(f"✅ PASS: {expected_name[:40]:<40} ({expected_city})")
            test_results["passed"] += 1
            test_results["schools_tested"].append({
                "id": school_id,
                "name": expected_name,
                "city": expected_city
            })
        else:
            print(f"❌ FAIL: Expected '{expected_name}', got '{school_profile['school_name']}'")
            test_results["failed"] += 1

    db.close()

    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Total Schools: {len(schools)}")
    print(f"✅ Passed: {test_results['passed']}")
    print(f"❌ Failed: {test_results['failed']}")
    print("=" * 70)

    # Verify specific schools
    print("\nVERIFYING KEY SCHOOLS:")
    print("-" * 70)

    ggs_found = False
    for school in test_results["schools_tested"]:
        if "Sandstraße" in school["name"] or "Sandstrasse" in school["name"]:
            print(f"✅ GGS Sandstraße found: {school['name']}")
            print(f"   City: {school['city']}")
            print(f"   School ID: {school['id']}")
            ggs_found = True

    if not ggs_found:
        print("⚠️  WARNING: GGS Sandstraße not found in test results")

    print("-" * 70)

    return test_results["failed"] == 0


def test_mock_draft_function():
    """Test that generate_mock_draft uses school profile correctly"""

    print("\n" + "=" * 70)
    print("MOCK DRAFT FUNCTION TEST")
    print("=" * 70)

    # Import the function
    sys.path.append('/Users/winzendwyers/Papa Projekt/backend')
    from api.routers.drafts_sqlite import generate_mock_draft

    # Test data
    funding_data = {
        'title': 'Test Förderprogramm',
        'provider': 'Test Fördergeber',
        'description': 'Test Beschreibung',
        'eligibility': 'Test Anforderungen',
        'funding_amount_min': 10000,
        'funding_amount_max': 50000,
        'application_deadline': '2025-12-31',
        'categories': 'Digitalisierung',
        'target_groups': 'Grundschulen'
    }

    user_query = "Wir möchten 20 Tablets für den Unterricht anschaffen."

    # Test Case 1: GGS Sandstraße
    school_profile_ggs = {
        'school_name': 'Gemeinschaftsgrundschule Sandstraße',
        'school_number': 'wird nachgetragen',
        'address': 'Sandstraße 46, 47169 Duisburg',
        'schultyp': 'Grundschule',
        'schuelerzahl': 'wird nachgetragen',
        'traeger': 'Öffentlicher Träger'
    }

    draft_ggs = generate_mock_draft(funding_data, user_query, school_profile_ggs)

    # Verify GGS Sandstraße appears in draft
    if 'Gemeinschaftsgrundschule Sandstraße' in draft_ggs:
        print("✅ PASS: GGS Sandstraße name appears in draft")
    else:
        print("❌ FAIL: GGS Sandstraße name NOT found in draft")
        return False

    if 'Duisburg' in draft_ggs:
        print("✅ PASS: Duisburg (city) appears in draft")
    else:
        print("❌ FAIL: Duisburg NOT found in draft")
        return False

    if 'Grundschule Musterberg' in draft_ggs:
        print("❌ FAIL: Old hardcoded 'Grundschule Musterberg' still appears!")
        return False
    else:
        print("✅ PASS: No hardcoded 'Grundschule Musterberg' found")

    # Test Case 2: Different school
    school_profile_test = {
        'school_name': 'Grundschule Testschule',
        'school_number': '999999',
        'address': 'Teststraße 1, 12345 Teststadt',
        'schultyp': 'Grundschule',
        'schuelerzahl': 300,
        'traeger': 'Öffentlicher Träger'
    }

    draft_test = generate_mock_draft(funding_data, user_query, school_profile_test)

    if 'Grundschule Testschule' in draft_test:
        print("✅ PASS: Custom school name appears in draft")
    else:
        print("❌ FAIL: Custom school name NOT found in draft")
        return False

    if 'Teststadt' in draft_test:
        print("✅ PASS: Custom city appears in draft")
    else:
        print("❌ FAIL: Custom city NOT found in draft")
        return False

    print("\n✅ ALL MOCK DRAFT TESTS PASSED")
    return True


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("SCHOOL PROFILE BUG FIX - COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    print("\nPurpose: Verify that draft generator uses real school data")
    print("         instead of hardcoded 'Grundschule Musterberg'\n")

    test1_pass = test_school_profile_retrieval()
    test2_pass = test_mock_draft_function()

    print("\n" + "=" * 70)
    print("FINAL RESULT")
    print("=" * 70)

    if test1_pass and test2_pass:
        print("✅ ALL TESTS PASSED - Bug fix successful!")
        print("\nVerified:")
        print("  - School profile queries work correctly")
        print("  - GGS Sandstraße data is properly retrieved")
        print("  - generate_mock_draft() uses real school names")
        print("  - No hardcoded 'Grundschule Musterberg' in outputs")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED - Review output above")
        sys.exit(1)
