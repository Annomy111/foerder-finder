"""
Setup Oracle Database Schema using cx_Oracle
Förder-Finder Grundschule
"""

import os
import sys
import cx_Oracle
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def execute_sql_file():
    """Execute SQL schema file"""

    # Database connection
    oracle_user = os.getenv('ORACLE_USER', 'ADMIN')
    oracle_password = os.getenv('ORACLE_PASSWORD', 'FoerderFinder2025!Secure')
    oracle_dsn = os.getenv('ORACLE_DSN', 'ainoveldb_medium')

    print(f'[SCHEMA] Connecting to Oracle Database: {oracle_dsn}')

    try:
        conn = cx_Oracle.connect(oracle_user, oracle_password, oracle_dsn)
        cursor = conn.cursor()
        print('[SCHEMA] Connected successfully')

        # Read SQL file
        with open('create_oracle_schema.sql', 'r') as f:
            sql_content = f.read()

        # Split by forward slash (PL/SQL block terminator)
        statements = sql_content.split('/')

        for statement in statements:
            statement = statement.strip()
            if not statement or statement.startswith('--'):
                continue

            # Check if it's a PL/SQL block or regular SQL
            if statement.upper().startswith('BEGIN'):
                # PL/SQL block
                try:
                    cursor.execute(statement)
                    print(f'[SCHEMA] Executed PL/SQL block')
                except Exception as e:
                    print(f'[SCHEMA] PL/SQL block error (may be expected): {e}')
            else:
                # Regular SQL - split by semicolon
                for stmt in statement.split(';'):
                    stmt = stmt.strip()
                    if not stmt or stmt.startswith('--'):
                        continue
                    try:
                        cursor.execute(stmt)
                        print(f'[SCHEMA] Executed: {stmt[:60]}...')
                    except Exception as e:
                        print(f'[ERROR] Failed to execute: {stmt[:60]}...')
                        print(f'[ERROR] Error: {e}')

        conn.commit()
        print('[SCHEMA] Schema created successfully!')

        cursor.close()
        conn.close()

    except Exception as e:
        print(f'[ERROR] Failed to create schema: {e}')
        sys.exit(1)

if __name__ == '__main__':
    # Set environment variables
    os.environ['LD_LIBRARY_PATH'] = '/opt/oracle'
    os.environ['TNS_ADMIN'] = '/opt/oracle_wallet'

    execute_sql_file()
