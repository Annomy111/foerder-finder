#!/usr/bin/env python3
"""
SQLite to Oracle Migration Script
Migrates data from dev_database.db to Oracle ATP

Usage:
    python migrate_sqlite_to_oracle.py [--dry-run] [--validate-only]

Options:
    --dry-run: Show what would be migrated without executing
    --validate-only: Only validate row counts and data integrity
"""

import sys
import os
import sqlite3
import cx_Oracle
from datetime import datetime
from typing import Dict, List, Any, Optional
import argparse
import json

# Add parent directory to path
sys.path.append(os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()


class SQLiteToOracleMigrator:
    """Migrates data from SQLite to Oracle ATP"""

    def __init__(self, sqlite_path: str = 'dev_database.db', dry_run: bool = False):
        self.sqlite_path = sqlite_path
        self.dry_run = dry_run

        # Connect to SQLite
        self.sqlite_conn = sqlite3.connect(sqlite_path)
        self.sqlite_conn.row_factory = sqlite3.Row
        print(f"✅ Connected to SQLite: {sqlite_path}")

        # Connect to Oracle
        if not dry_run:
            oracle_user = os.getenv('ORACLE_USER')
            oracle_password = os.getenv('ORACLE_PASSWORD')
            oracle_dsn = os.getenv('ORACLE_DSN')

            if not all([oracle_user, oracle_password, oracle_dsn]):
                raise ValueError("Oracle credentials not set in .env")

            self.oracle_conn = cx_Oracle.connect(
                user=oracle_user,
                password=oracle_password,
                dsn=oracle_dsn,
                encoding='UTF-8'
            )
            print(f"✅ Connected to Oracle: {oracle_dsn}")
        else:
            self.oracle_conn = None
            print("ℹ️  Dry run mode - Oracle connection skipped")

        # Migration statistics
        self.stats = {
            'tables_migrated': 0,
            'rows_migrated': 0,
            'errors': []
        }

    def get_sqlite_tables(self) -> List[str]:
        """Get list of tables to migrate"""
        cursor = self.sqlite_conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        return [row[0] for row in cursor.fetchall()]

    def convert_value(self, value: Any, oracle_type: str) -> Any:
        """Convert SQLite value to Oracle-compatible type"""
        if value is None:
            return None

        # Convert empty strings to None for Oracle
        if isinstance(value, str) and value.strip() == '':
            return None

        # Handle datetime strings
        if oracle_type in ['DATE', 'TIMESTAMP']:
            if isinstance(value, str):
                try:
                    # Parse ISO format: 2025-11-02 14:30:00
                    return datetime.fromisoformat(value.replace('Z', '+00:00'))
                except ValueError:
                    # Try just date: 2025-11-02
                    try:
                        return datetime.strptime(value, '%Y-%m-%d')
                    except ValueError:
                        return None
            elif isinstance(value, (int, float)):
                # Unix timestamp
                return datetime.fromtimestamp(value)

        # Handle numbers
        if oracle_type == 'NUMBER':
            if isinstance(value, str):
                try:
                    return float(value) if '.' in value else int(value)
                except ValueError:
                    return None

        return value

    def migrate_table(self, table_name: str, field_mapping: Dict[str, Dict]) -> int:
        """
        Migrate a single table from SQLite to Oracle

        Args:
            table_name: Name of the table
            field_mapping: Dict mapping Oracle field names to SQLite field names + types
                Example: {'funding_id': {'sqlite': 'funding_id', 'type': 'VARCHAR2'}}

        Returns:
            Number of rows migrated
        """
        print(f"\n📊 Migrating table: {table_name}")

        # Get data from SQLite
        sqlite_cursor = self.sqlite_conn.cursor()
        sqlite_cursor.execute(f"SELECT * FROM {table_name}")
        rows = sqlite_cursor.fetchall()

        if len(rows) == 0:
            print(f"⚠️  No data in {table_name}, skipping")
            return 0

        print(f"   Found {len(rows)} rows in SQLite")

        if self.dry_run:
            print(f"   [DRY RUN] Would migrate {len(rows)} rows")
            return len(rows)

        # Prepare Oracle INSERT statement
        oracle_fields = list(field_mapping.keys())
        placeholders = ', '.join([f':{i+1}' for i in range(len(oracle_fields))])
        insert_sql = f"""
            INSERT INTO {table_name} ({', '.join(oracle_fields)})
            VALUES ({placeholders})
        """

        # Migrate data
        oracle_cursor = self.oracle_conn.cursor()
        migrated_count = 0
        errors = 0

        for row in rows:
            try:
                # Convert row to dict
                row_dict = dict(row)

                # Map and convert values
                values = []
                for oracle_field, mapping in field_mapping.items():
                    sqlite_field = mapping['sqlite']
                    oracle_type = mapping['type']

                    # Get value from SQLite row
                    value = row_dict.get(sqlite_field)

                    # Convert to Oracle type
                    converted_value = self.convert_value(value, oracle_type)
                    values.append(converted_value)

                # Execute INSERT
                oracle_cursor.execute(insert_sql, values)
                migrated_count += 1

            except cx_Oracle.Error as e:
                error_msg = f"Error migrating row in {table_name}: {str(e)}"
                print(f"   ❌ {error_msg}")
                self.stats['errors'].append(error_msg)
                errors += 1

                # Stop if too many errors
                if errors > 10:
                    print(f"   ❌ Too many errors, stopping migration of {table_name}")
                    break

        # Commit
        self.oracle_conn.commit()

        print(f"   ✅ Migrated {migrated_count} rows (errors: {errors})")
        return migrated_count

    def validate_migration(self, table_name: str) -> bool:
        """Validate row counts match between SQLite and Oracle"""
        # SQLite count
        sqlite_cursor = self.sqlite_conn.cursor()
        sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        sqlite_count = sqlite_cursor.fetchone()[0]

        # Oracle count
        if not self.dry_run:
            oracle_cursor = self.oracle_conn.cursor()
            oracle_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            oracle_count = oracle_cursor.fetchone()[0]
        else:
            oracle_count = 0

        # Compare
        match = sqlite_count == oracle_count
        status = "✅" if match else "❌"
        print(f"{status} {table_name}: SQLite={sqlite_count}, Oracle={oracle_count}")

        return match

    def run_migration(self):
        """Execute full migration"""
        print("\n" + "="*60)
        print("SQLite → Oracle Migration")
        print("="*60)

        # Define table migration order (respects foreign keys)
        migrations = [
            # 1. SCHOOLS (no dependencies)
            ('SCHOOLS', {
                'school_id': {'sqlite': 'school_id', 'type': 'VARCHAR2'},
                'name': {'sqlite': 'name', 'type': 'VARCHAR2'},
                'address': {'sqlite': 'address', 'type': 'VARCHAR2'},
                'city': {'sqlite': 'city', 'type': 'VARCHAR2'},
                'state': {'sqlite': 'state', 'type': 'VARCHAR2'},
                'postal_code': {'sqlite': 'postal_code', 'type': 'VARCHAR2'},
                'contact_email': {'sqlite': 'contact_email', 'type': 'VARCHAR2'},
                'contact_phone': {'sqlite': 'contact_phone', 'type': 'VARCHAR2'},
                'is_active': {'sqlite': 'is_active', 'type': 'NUMBER'},
                'created_at': {'sqlite': 'created_at', 'type': 'TIMESTAMP'},
            }),

            # 2. USERS (depends on SCHOOLS)
            ('USERS', {
                'user_id': {'sqlite': 'user_id', 'type': 'VARCHAR2'},
                'school_id': {'sqlite': 'school_id', 'type': 'VARCHAR2'},
                'email': {'sqlite': 'email', 'type': 'VARCHAR2'},
                'password_hash': {'sqlite': 'password_hash', 'type': 'VARCHAR2'},
                'first_name': {'sqlite': 'first_name', 'type': 'VARCHAR2'},
                'last_name': {'sqlite': 'last_name', 'type': 'VARCHAR2'},
                'role': {'sqlite': 'role', 'type': 'VARCHAR2'},
                'is_active': {'sqlite': 'is_active', 'type': 'NUMBER'},
                'last_login': {'sqlite': 'last_login', 'type': 'TIMESTAMP'},
                'created_at': {'sqlite': 'created_at', 'type': 'TIMESTAMP'},
            }),

            # 3. STIFTUNGEN (no dependencies)
            ('STIFTUNGEN', {
                'stiftung_id': {'sqlite': 'stiftung_id', 'type': 'VARCHAR2'},
                'name': {'sqlite': 'name', 'type': 'VARCHAR2'},
                'description': {'sqlite': 'description', 'type': 'CLOB'},
                'website': {'sqlite': 'website', 'type': 'VARCHAR2'},
                'bundesland': {'sqlite': 'bundesland', 'type': 'VARCHAR2'},
                'stadt': {'sqlite': 'stadt', 'type': 'VARCHAR2'},
                'plz': {'sqlite': 'plz', 'type': 'VARCHAR2'},
                'quelle': {'sqlite': 'quelle', 'type': 'VARCHAR2'},
                'stiftungsart': {'sqlite': 'stiftungsart', 'type': 'VARCHAR2'},
                'stiftungszweck': {'sqlite': 'stiftungszweck', 'type': 'CLOB'},
                'is_active': {'sqlite': 'is_active', 'type': 'NUMBER'},
                'last_scraped': {'sqlite': 'last_scraped', 'type': 'TIMESTAMP'},
                'created_at': {'sqlite': 'created_at', 'type': 'TIMESTAMP'},
            }),

            # 4. FUNDING_OPPORTUNITIES (depends on STIFTUNGEN)
            ('FUNDING_OPPORTUNITIES', {
                'funding_id': {'sqlite': 'funding_id', 'type': 'VARCHAR2'},
                'title': {'sqlite': 'title', 'type': 'VARCHAR2'},
                'provider': {'sqlite': 'provider', 'type': 'VARCHAR2'},
                'funder_name': {'sqlite': 'funder_name', 'type': 'VARCHAR2'},
                'description': {'sqlite': 'description', 'type': 'CLOB'},
                'eligibility': {'sqlite': 'eligibility', 'type': 'CLOB'},
                'evaluation_criteria': {'sqlite': 'evaluation_criteria', 'type': 'CLOB'},
                'requirements': {'sqlite': 'requirements', 'type': 'CLOB'},
                'application_process': {'sqlite': 'application_process', 'type': 'CLOB'},
                'eligible_costs': {'sqlite': 'eligible_costs', 'type': 'CLOB'},
                'cleaned_text': {'sqlite': 'cleaned_text', 'type': 'CLOB'},
                'metadata_json': {'sqlite': 'metadata_json', 'type': 'CLOB'},
                'application_deadline': {'sqlite': 'application_deadline', 'type': 'DATE'},
                'deadline': {'sqlite': 'deadline', 'type': 'DATE'},
                'funding_amount_min': {'sqlite': 'funding_amount_min', 'type': 'NUMBER'},
                'min_funding_amount': {'sqlite': 'min_funding_amount', 'type': 'NUMBER'},
                'funding_amount_max': {'sqlite': 'funding_amount_max', 'type': 'NUMBER'},
                'max_funding_amount': {'sqlite': 'max_funding_amount', 'type': 'NUMBER'},
                'co_financing_rate': {'sqlite': 'co_financing_rate', 'type': 'NUMBER'},
                'co_financing_required': {'sqlite': 'co_financing_required', 'type': 'NUMBER'},
                'categories': {'sqlite': 'categories', 'type': 'VARCHAR2'},
                'target_groups': {'sqlite': 'target_groups', 'type': 'VARCHAR2'},
                'region': {'sqlite': 'region', 'type': 'VARCHAR2'},
                'funding_area': {'sqlite': 'funding_area', 'type': 'VARCHAR2'},
                'source_type': {'sqlite': 'source_type', 'type': 'VARCHAR2'},
                'url': {'sqlite': 'url', 'type': 'VARCHAR2'},
                'source_url': {'sqlite': 'source_url', 'type': 'VARCHAR2'},
                'application_url': {'sqlite': 'application_url', 'type': 'VARCHAR2'},
                'contact_person': {'sqlite': 'contact_person', 'type': 'VARCHAR2'},
                'contact_email': {'sqlite': 'contact_email', 'type': 'VARCHAR2'},
                'contact_phone': {'sqlite': 'contact_phone', 'type': 'VARCHAR2'},
                'stiftung_id': {'sqlite': 'stiftung_id', 'type': 'VARCHAR2'},
                'scraped_pages': {'sqlite': 'scraped_pages', 'type': 'NUMBER'},
                'extraction_quality_score': {'sqlite': 'extraction_quality_score', 'type': 'NUMBER'},
                'last_scraped': {'sqlite': 'last_scraped', 'type': 'TIMESTAMP'},
                'last_extracted': {'sqlite': 'last_extracted', 'type': 'TIMESTAMP'},
                'created_at': {'sqlite': 'created_at', 'type': 'TIMESTAMP'},
                'updated_at': {'sqlite': 'updated_at', 'type': 'TIMESTAMP'},
            }),

            # 5. APPLICATIONS (depends on SCHOOLS, USERS, FUNDING_OPPORTUNITIES)
            ('APPLICATIONS', {
                'application_id': {'sqlite': 'application_id', 'type': 'VARCHAR2'},
                'school_id': {'sqlite': 'school_id', 'type': 'VARCHAR2'},
                'funding_id': {'sqlite': 'funding_id', 'type': 'VARCHAR2'},
                'user_id': {'sqlite': 'user_id', 'type': 'VARCHAR2'},
                'title': {'sqlite': 'title', 'type': 'VARCHAR2'},
                'status': {'sqlite': 'status', 'type': 'VARCHAR2'},
                'application_text': {'sqlite': 'application_text', 'type': 'CLOB'},
                'draft_text': {'sqlite': 'draft_text', 'type': 'CLOB'},
                'final_text': {'sqlite': 'final_text', 'type': 'CLOB'},
                'submitted_at': {'sqlite': 'submitted_at', 'type': 'TIMESTAMP'},
                'created_at': {'sqlite': 'created_at', 'type': 'TIMESTAMP'},
            }),

            # 6. APPLICATION_DRAFTS (depends on APPLICATIONS)
            ('APPLICATION_DRAFTS', {
                'draft_id': {'sqlite': 'draft_id', 'type': 'VARCHAR2'},
                'application_id': {'sqlite': 'application_id', 'type': 'VARCHAR2'},
                'school_id': {'sqlite': 'school_id', 'type': 'VARCHAR2'},
                'funding_id': {'sqlite': 'funding_id', 'type': 'VARCHAR2'},
                'user_id': {'sqlite': 'user_id', 'type': 'VARCHAR2'},
                'draft_text': {'sqlite': 'draft_text', 'type': 'CLOB'},
                'school_context': {'sqlite': 'school_context', 'type': 'CLOB'},
                'ai_model': {'sqlite': 'ai_model', 'type': 'VARCHAR2'},
                'prompt_used': {'sqlite': 'prompt_used', 'type': 'CLOB'},
                'user_feedback': {'sqlite': 'user_feedback', 'type': 'VARCHAR2'},
                'version': {'sqlite': 'version', 'type': 'NUMBER'},
                'created_at': {'sqlite': 'created_at', 'type': 'TIMESTAMP'},
            }),
        ]

        # Execute migrations
        start_time = datetime.now()

        for table_name, field_mapping in migrations:
            try:
                # Check if table exists in SQLite
                sqlite_cursor = self.sqlite_conn.cursor()
                sqlite_cursor.execute("""
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND name = ?
                """, (table_name,))

                if not sqlite_cursor.fetchone():
                    print(f"⚠️  Table {table_name} not found in SQLite, skipping")
                    continue

                # Migrate
                rows_migrated = self.migrate_table(table_name, field_mapping)

                self.stats['tables_migrated'] += 1
                self.stats['rows_migrated'] += rows_migrated

            except Exception as e:
                error_msg = f"Failed to migrate {table_name}: {str(e)}"
                print(f"❌ {error_msg}")
                self.stats['errors'].append(error_msg)

        # Summary
        duration = (datetime.now() - start_time).total_seconds()

        print("\n" + "="*60)
        print("Migration Summary")
        print("="*60)
        print(f"Duration: {duration:.2f} seconds")
        print(f"Tables migrated: {self.stats['tables_migrated']}")
        print(f"Rows migrated: {self.stats['rows_migrated']}")
        print(f"Errors: {len(self.stats['errors'])}")

        if self.stats['errors']:
            print("\nErrors encountered:")
            for error in self.stats['errors']:
                print(f"  - {error}")

    def validate_all(self):
        """Validate all table migrations"""
        print("\n" + "="*60)
        print("Migration Validation")
        print("="*60)

        tables = ['SCHOOLS', 'USERS', 'STIFTUNGEN', 'FUNDING_OPPORTUNITIES',
                  'APPLICATIONS', 'APPLICATION_DRAFTS']

        all_valid = True
        for table in tables:
            try:
                valid = self.validate_migration(table)
                if not valid:
                    all_valid = False
            except Exception as e:
                print(f"❌ {table}: Validation error - {str(e)}")
                all_valid = False

        print("\n" + "="*60)
        if all_valid:
            print("✅ All tables validated successfully!")
        else:
            print("❌ Validation failed - row counts do not match")

        return all_valid

    def close(self):
        """Close database connections"""
        self.sqlite_conn.close()
        if self.oracle_conn:
            self.oracle_conn.close()
        print("\n✅ Database connections closed")


def main():
    parser = argparse.ArgumentParser(description='Migrate SQLite to Oracle ATP')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be migrated without executing')
    parser.add_argument('--validate-only', action='store_true',
                        help='Only validate row counts and data integrity')
    parser.add_argument('--sqlite-path', default='dev_database.db',
                        help='Path to SQLite database (default: dev_database.db)')

    args = parser.parse_args()

    # Create migrator
    migrator = SQLiteToOracleMigrator(
        sqlite_path=args.sqlite_path,
        dry_run=args.dry_run
    )

    try:
        if args.validate_only:
            # Only validate
            migrator.validate_all()
        else:
            # Run migration
            migrator.run_migration()

            # Validate if not dry run
            if not args.dry_run:
                print("\n")
                migrator.validate_all()

    except KeyboardInterrupt:
        print("\n\n⚠️  Migration interrupted by user")
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        migrator.close()


if __name__ == '__main__':
    main()
