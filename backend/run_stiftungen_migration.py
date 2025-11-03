#!/usr/bin/env python3
"""
Führt Stiftungen-Migration auf Oracle DB aus
"""

import sys
from utils.database import get_db_cursor

def run_migration():
    """Führe Migration aus"""
    print("🔧 Starte Migration: Add Stiftungen Fields...")

    migrations = [
        # Add columns
        """
        ALTER TABLE FUNDING_OPPORTUNITIES ADD (
            region VARCHAR2(100)
        )
        """,
        """
        ALTER TABLE FUNDING_OPPORTUNITIES ADD (
            funder_name VARCHAR2(255)
        )
        """,
        """
        ALTER TABLE FUNDING_OPPORTUNITIES ADD (
            source_url VARCHAR2(1000)
        )
        """,
        """
        ALTER TABLE FUNDING_OPPORTUNITIES ADD (
            source_type VARCHAR2(50) DEFAULT 'website'
        )
        """,
        # Add indexes
        """
        CREATE INDEX idx_funding_source_type ON FUNDING_OPPORTUNITIES(source_type)
        """,
        """
        CREATE INDEX idx_funding_region ON FUNDING_OPPORTUNITIES(region)
        """,
        # Update existing
        """
        UPDATE FUNDING_OPPORTUNITIES
        SET source_type = 'website'
        WHERE source_type IS NULL
        """,
    ]

    try:
        with get_db_cursor() as cursor:
            for i, sql in enumerate(migrations, 1):
                try:
                    print(f"[{i}/{len(migrations)}] Executing...")
                    cursor.execute(sql)
                    print(f"   ✅ Success")
                except Exception as e:
                    # Ignoriere "column already exists" Fehler
                    error_msg = str(e).lower()
                    if 'already exists' in error_msg or 'oca-01430' in error_msg:
                        print(f"   ⏭️ Already exists, skipping")
                    else:
                        print(f"   ❌ Error: {e}")
                        raise

        print("\n✅ Migration erfolgreich abgeschlossen!")

    except Exception as e:
        print(f"\n❌ Migration fehlgeschlagen: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_migration()
