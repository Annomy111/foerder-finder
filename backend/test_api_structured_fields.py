#!/usr/bin/env python3
"""
Test script to verify API returns structured fields correctly
"""
import os
import sys
import sqlite3
import json
from pathlib import Path

# Set environment to use SQLite
os.environ['USE_SQLITE'] = 'true'

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

def test_structured_fields():
    """Test that structured fields are properly stored and can be retrieved"""

    db_path = "dev_database.db"

    if not os.path.exists(db_path):
        print("❌ Database not found!")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get a funding opportunity with high quality score
    cursor.execute("""
        SELECT
            funding_id,
            title,
            eligibility,
            target_groups,
            eligible_costs,
            extraction_quality_score
        FROM FUNDING_OPPORTUNITIES
        WHERE extraction_quality_score > 0.5
        ORDER BY extraction_quality_score DESC
        LIMIT 1
    """)

    row = cursor.fetchone()

    if not row:
        print("❌ No high-quality funding opportunities found!")
        return False

    funding_id, title, eligibility, target_groups, eligible_costs, quality = row

    print("=" * 80)
    print(f"Testing: {title}")
    print(f"Quality Score: {quality}")
    print("=" * 80)
    print()

    # Test eligibility parsing
    if eligibility:
        try:
            eligibility_list = json.loads(eligibility)
            print(f"✅ Eligibility ({len(eligibility_list)} items):")
            for item in eligibility_list[:3]:  # Show first 3
                print(f"   - {item}")
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse eligibility: {e}")
            return False
    else:
        print("⚠️ No eligibility data")

    print()

    # Test target_groups parsing
    if target_groups:
        try:
            groups_list = json.loads(target_groups)
            print(f"✅ Target Groups ({len(groups_list)} items):")
            for item in groups_list[:3]:
                print(f"   - {item}")
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse target_groups: {e}")
            return False
    else:
        print("⚠️ No target groups data")

    print()

    # Test eligible_costs parsing
    if eligible_costs:
        try:
            costs_list = json.loads(eligible_costs)
            print(f"✅ Eligible Costs ({len(costs_list)} items):")
            for item in costs_list[:3]:
                print(f"   - {item}")
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse eligible_costs: {e}")
            return False
    else:
        print("⚠️ No eligible costs data")

    print()
    print("=" * 80)
    print("✅ All structured fields can be parsed successfully!")
    print("=" * 80)

    conn.close()
    return True

if __name__ == '__main__':
    success = test_structured_fields()
    sys.exit(0 if success else 1)
