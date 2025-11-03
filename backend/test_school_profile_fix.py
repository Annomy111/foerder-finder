#!/usr/bin/env python3
"""
Test Script: Verify School Profile Data
Validates that real school data exists in database before the fix
"""

import sqlite3

# Test Case 1: GGS Sandstraße
school_id = "F4B41CD6900B4F62B152669C1E0B5109"
db = sqlite3.connect("dev_database.db")
db.row_factory = sqlite3.Row

cursor = db.cursor()
cursor.execute(
    "SELECT name, address, postal_code, city, contact_email, contact_phone FROM SCHOOLS WHERE school_id = ?",
    (school_id,)
)
school_data = cursor.fetchone()

if not school_data:
    print(f"❌ ERROR: School not found with ID {school_id}")
    exit(1)

print("=" * 60)
print("DATABASE VERIFICATION TEST")
print("=" * 60)
print(f"School ID: {school_id}")
print(f"School Name: {school_data['name']}")
print(f"Address: {school_data['address']}")
print(f"Postal Code: {school_data['postal_code']}")
print(f"City: {school_data['city']}")
print(f"Email: {school_data['contact_email']}")
print(f"Phone: {school_data['contact_phone']}")
print("=" * 60)

# Validate expected values
assert "Sandstraße" in school_data['name'] or "Sandstrasse" in school_data['name'], \
    f"Wrong school name! Expected 'GGS Sandstraße', got '{school_data['name']}'"
assert school_data['city'] == "Duisburg", \
    f"Wrong city! Expected 'Duisburg', got '{school_data['city']}'"

print("✅ TEST PASSED - School data is correct in database!")
print("\nNow proceeding to fix the hardcoded school_profile in drafts_sqlite.py...")

db.close()
