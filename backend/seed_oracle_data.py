"""
Seed Oracle Database with Demo Data
Förder-Finder Grundschule
"""

import os
import sys
import uuid
from datetime import datetime, timedelta
from passlib.context import CryptContext
import cx_Oracle
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Password hashing
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def seed_database():
    """Seed Oracle database with demo data"""

    # Database connection
    oracle_user = os.getenv('ORACLE_USER', 'ADMIN')
    oracle_password = os.getenv('ORACLE_PASSWORD', 'FoerderFinder2025!Secure')
    oracle_dsn = os.getenv('ORACLE_DSN', 'ainoveldb_medium')

    print(f'[SEED] Connecting to Oracle Database: {oracle_dsn}')

    try:
        conn = cx_Oracle.connect(oracle_user, oracle_password, oracle_dsn)
        cursor = conn.cursor()
        print('[SEED] Connected successfully')

        # 1. Create demo school
        school_id = str(uuid.uuid4()).replace('-', '').upper()
        cursor.execute("""
            INSERT INTO SCHOOLS (school_id, name, address, city, state, postal_code, contact_email, contact_phone)
            VALUES (:1, :2, :3, :4, :5, :6, :7, :8)
        """, (
            school_id,
            'Grundschule Musterberg',
            'Schulstraße 123',
            'Musterberg',
            'Nordrhein-Westfalen',
            '12345',
            'kontakt@gs-musterberg.de',
            '+49 123 456789'
        ))
        print(f'[SEED] Created school: {school_id}')

        # 2. Create demo users
        admin_id = str(uuid.uuid4()).replace('-', '').upper()
        teacher_id = str(uuid.uuid4()).replace('-', '').upper()

        # Use shorter passwords for bcrypt (max 72 bytes)
        admin_password = hash_password('admin123'[:72])
        teacher_password = hash_password('lehrer123'[:72])

        cursor.execute("""
            INSERT INTO USERS (user_id, school_id, email, password_hash, full_name, role, is_active)
            VALUES (:1, :2, :3, :4, :5, :6, :7)
        """, (
            admin_id,
            school_id,
            'admin@gs-musterberg.de',
            admin_password,
            'Max Mustermann',
            'admin',
            1
        ))

        cursor.execute("""
            INSERT INTO USERS (user_id, school_id, email, password_hash, full_name, role, is_active)
            VALUES (:1, :2, :3, :4, :5, :6, :7)
        """, (
            teacher_id,
            school_id,
            'lehrer@gs-musterberg.de',
            teacher_password,
            'Anna Schmidt',
            'lehrkraft',
            1
        ))
        print(f'[SEED] Created admin user: admin@gs-musterberg.de (password: admin123)')
        print(f'[SEED] Created teacher user: lehrer@gs-musterberg.de (password: lehrer123)')

        # 3. Create demo funding opportunities
        funding_data = [
            {
                'title': 'Digitalisierung an Grundschulen',
                'description': 'Förderung für digitale Ausstattung und Infrastruktur an Grundschulen',
                'funding_type': 'Infrastruktur',
                'provider': 'Bundesministerium für Bildung',
                'amount_min': 5000,
                'amount_max': 50000,
                'deadline': datetime.now() + timedelta(days=60),
                'url': 'https://example.com/digitalisierung',
                'eligibility_criteria': 'Grundschulen in Deutschland mit digitalem Konzept',
                'application_process': 'Online-Antrag über Förderportal'
            },
            {
                'title': 'Sprachförderung für Migranten',
                'description': 'Unterstützung von Sprachförderprogrammen für Kinder mit Migrationshintergrund',
                'funding_type': 'Bildungsprogramme',
                'provider': 'Landesregierung NRW',
                'amount_min': 2000,
                'amount_max': 20000,
                'deadline': datetime.now() + timedelta(days=90),
                'url': 'https://example.com/sprachfoerderung',
                'eligibility_criteria': 'Grundschulen mit hohem Anteil an Kindern mit Migrationshintergrund',
                'application_process': 'Schriftlicher Antrag mit pädagogischem Konzept'
            },
            {
                'title': 'Bewegung und Gesundheit',
                'description': 'Förderung von Sport- und Bewegungsangeboten an Grundschulen',
                'funding_type': 'Sport & Gesundheit',
                'provider': 'Stiftung Kindergesundheit',
                'amount_min': 1000,
                'amount_max': 10000,
                'deadline': datetime.now() + timedelta(days=45),
                'url': 'https://example.com/bewegung',
                'eligibility_criteria': 'Grundschulen mit Bewegungskonzept',
                'application_process': 'Online-Bewerbung mit Projektskizze'
            }
        ]

        funding_ids = []
        for data in funding_data:
            funding_id = str(uuid.uuid4()).replace('-', '').upper()
            funding_ids.append(funding_id)

            cursor.execute("""
                INSERT INTO FUNDING_OPPORTUNITIES
                (funding_id, title, description, funding_type, provider, amount_min, amount_max,
                 deadline, url, eligibility_criteria, application_process, cleaned_text)
                VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12)
            """, (
                funding_id,
                data['title'],
                data['description'],
                data['funding_type'],
                data['provider'],
                data['amount_min'],
                data['amount_max'],
                data['deadline'],
                data['url'],
                data['eligibility_criteria'],
                data['application_process'],
                f"{data['title']} {data['description']} {data['eligibility_criteria']}"
            ))
            print(f'[SEED] Created funding: {data["title"]}')

        # 4. Create demo draft
        draft_id = str(uuid.uuid4()).replace('-', '').upper()
        cursor.execute("""
            INSERT INTO APPLICATION_DRAFTS
            (draft_id, school_id, funding_id, user_id, draft_text, school_context, ai_model)
            VALUES (:1, :2, :3, :4, :5, :6, :7)
        """, (
            draft_id,
            school_id,
            funding_ids[0],
            admin_id,
            'Dies ist ein KI-generierter Musterantrag für Digitalisierung...',
            'Grundschule Musterberg mit 300 Schülern',
            'deepseek-chat'
        ))
        print(f'[SEED] Created demo draft')

        conn.commit()
        print('[SEED] Database seeded successfully!')
        print()
        print('=== LOGIN CREDENTIALS ===')
        print(f'School: Grundschule Musterberg')
        print(f'Admin: admin@gs-musterberg.de / admin123')
        print(f'Teacher: lehrer@gs-musterberg.de / lehrer123')
        print('=========================')

        cursor.close()
        conn.close()

    except Exception as e:
        print(f'[ERROR] Failed to seed database: {e}')
        sys.exit(1)

if __name__ == '__main__':
    # Set environment variables
    os.environ['LD_LIBRARY_PATH'] = '/opt/oracle'
    os.environ['TNS_ADMIN'] = '/opt/oracle_wallet'

    seed_database()
