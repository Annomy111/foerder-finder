"""
GGS Sandstraße Duisburg - ORACLE CLOUD PRODUCTION DEPLOYMENT
Verwendet passlib (Backend-kompatibel) + Oracle DB
"""

import os
import sys
import uuid
from passlib.context import CryptContext
import cx_Oracle
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Password hashing - EXACTLY wie im Backend
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def hash_password(password: str) -> str:
    """Hash password using passlib CryptContext (matches backend)"""
    return pwd_context.hash(password)

def add_ggs_sandstrasse_oracle():
    """Legt die GGS Sandstraße in der Oracle Cloud Production DB an"""

    # Database connection
    oracle_user = os.getenv('ORACLE_USER', 'ADMIN')
    oracle_password = os.getenv('ORACLE_PASSWORD')
    oracle_dsn = os.getenv('ORACLE_DSN', 'ainoveldb_medium')

    if not oracle_password:
        print('[ERROR] ORACLE_PASSWORD nicht gesetzt in .env!')
        sys.exit(1)

    print('=' * 80)
    print('GGS SANDSTRASSE DUISBURG - ORACLE CLOUD PRODUCTION DEPLOYMENT')
    print('=' * 80)
    print(f'[INFO] Verbinde mit Oracle Cloud Database: {oracle_dsn}')
    print(f'[INFO] User: {oracle_user}')

    try:
        # Oracle Connection
        conn = cx_Oracle.connect(oracle_user, oracle_password, oracle_dsn)
        cursor = conn.cursor()
        print('[SUCCESS] Datenbankverbindung erfolgreich')

        # 1. Create school
        school_id = str(uuid.uuid4()).replace('-', '').upper()

        school_data = {
            'school_id': school_id,
            'name': 'Gemeinschaftsgrundschule Sandstraße',
            'address': 'Sandstraße 46, Duisburg-Marxloh',
            'city': 'Duisburg',
            'state': 'Nordrhein-Westfalen',
            'postal_code': '47169',
            'contact_email': 'ggs.sandstr@stadt-duisburg.de',
            'contact_phone': '0203-403688',
            'logo_url': 'https://www.ggs-sandstrasse.de/wp-content/uploads/2022/04/Logo_mSchrift-e1672838922106.jpg'
        }

        print('\n[SCHULE] Lege Schule an...')
        print(f'  Name: {school_data["name"]}')
        print(f'  Adresse: {school_data["address"]}, {school_data["postal_code"]} {school_data["city"]}')
        print(f'  Bundesland: {school_data["state"]}')
        print(f'  Email: {school_data["contact_email"]}')
        print(f'  Telefon: {school_data["contact_phone"]}')
        print(f'  Logo: {school_data["logo_url"]}')

        cursor.execute("""
            INSERT INTO SCHOOLS (school_id, name, address, city, state, postal_code, contact_email, contact_phone, logo_url)
            VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9)
        """, (
            school_data['school_id'],
            school_data['name'],
            school_data['address'],
            school_data['city'],
            school_data['state'],
            school_data['postal_code'],
            school_data['contact_email'],
            school_data['contact_phone'],
            school_data['logo_url']
        ))
        print(f'[SUCCESS] Schule angelegt mit ID: {school_id}')

        # 2. Create admin user
        admin_id = str(uuid.uuid4()).replace('-', '').upper()
        admin_email = 'admin@ggs-sandstrasse.de'
        admin_password = 'GGS2025!Admin'
        admin_password_hash = hash_password(admin_password)

        print('\n[ADMIN] Lege Admin-User an...')
        print(f'  Email: {admin_email}')
        print(f'  Passwort: {admin_password}')
        print(f'  Name: Klaus Hagge (Schulleitung)')
        print(f'  Hash (first 30 chars): {admin_password_hash[:30]}...')

        # Check if USERS table uses full_name or first_name/last_name
        cursor.execute("SELECT column_name FROM user_tab_columns WHERE table_name = 'USERS' AND column_name IN ('FULL_NAME', 'FIRST_NAME', 'LAST_NAME')")
        columns = [row[0] for row in cursor.fetchall()]

        if 'FULL_NAME' in columns:
            print('[INFO] Using FULL_NAME column')
            cursor.execute("""
                INSERT INTO USERS (user_id, school_id, email, password_hash, full_name, role, is_active)
                VALUES (:1, :2, :3, :4, :5, :6, :7)
            """, (
                admin_id,
                school_id,
                admin_email,
                admin_password_hash,
                'Klaus Hagge',
                'admin',
                1
            ))
        else:
            print('[INFO] Using FIRST_NAME/LAST_NAME columns')
            cursor.execute("""
                INSERT INTO USERS (user_id, school_id, email, password_hash, first_name, last_name, role, is_active)
                VALUES (:1, :2, :3, :4, :5, :6, :7, :8)
            """, (
                admin_id,
                school_id,
                admin_email,
                admin_password_hash,
                'Klaus',
                'Hagge',
                'admin',
                1
            ))
        print(f'[SUCCESS] Admin-User angelegt mit ID: {admin_id}')

        # 3. Create teacher user
        teacher_id = str(uuid.uuid4()).replace('-', '').upper()
        teacher_email = 'lehrer@ggs-sandstrasse.de'
        teacher_password = 'Lehrer2025!'
        teacher_password_hash = hash_password(teacher_password)

        print('\n[LEHRKRAFT] Lege Lehrkraft-User an...')
        print(f'  Email: {teacher_email}')
        print(f'  Passwort: {teacher_password}')

        if 'FULL_NAME' in columns:
            cursor.execute("""
                INSERT INTO USERS (user_id, school_id, email, password_hash, full_name, role, is_active)
                VALUES (:1, :2, :3, :4, :5, :6, :7)
            """, (
                teacher_id,
                school_id,
                teacher_email,
                teacher_password_hash,
                'Lehrkraft Test',
                'lehrkraft',
                1
            ))
        else:
            cursor.execute("""
                INSERT INTO USERS (user_id, school_id, email, password_hash, first_name, last_name, role, is_active)
                VALUES (:1, :2, :3, :4, :5, :6, :7, :8)
            """, (
                teacher_id,
                school_id,
                teacher_email,
                teacher_password_hash,
                'Lehrkraft',
                'Test',
                'lehrkraft',
                1
            ))
        print(f'[SUCCESS] Lehrkraft-User angelegt mit ID: {teacher_id}')

        # Commit changes
        conn.commit()
        print('\n[COMMIT] Alle Änderungen erfolgreich gespeichert')

        # Verify password works
        print('\n[VERIFY] Teste Passwort-Verifikation...')
        verification_result = pwd_context.verify(admin_password, admin_password_hash)
        print(f'  Password verification: {verification_result}')

        if not verification_result:
            print('[ERROR] PASSWORD VERIFICATION FAILED!')
            raise Exception('Password hash verification failed')

        # Print summary
        print('\n' + '=' * 80)
        print('ZUSAMMENFASSUNG - GGS SANDSTRASSE ORACLE CLOUD PRODUCTION')
        print('=' * 80)
        print(f'\n✅ Schule angelegt:')
        print(f'   ID: {school_id}')
        print(f'   Name: {school_data["name"]}')
        print(f'   Adresse: {school_data["address"]}, {school_data["postal_code"]} {school_data["city"]}')
        print(f'   Bundesland: {school_data["state"]}')
        print(f'   Email: {school_data["contact_email"]}')
        print(f'   Telefon: {school_data["contact_phone"]}')
        print(f'   Logo: {school_data["logo_url"]}')

        print(f'\n✅ Admin-Zugang (PRODUCTION):')
        print(f'   Email: {admin_email}')
        print(f'   Passwort: {admin_password}')
        print(f'   Name: Klaus Hagge (Schulleitung)')

        print(f'\n✅ Lehrkraft-Zugang (PRODUCTION):')
        print(f'   Email: {teacher_email}')
        print(f'   Passwort: {teacher_password}')

        print(f'\n🌐 PRODUCTION Login URL: https://edufunds.org/login')
        print('=' * 80)

        # Close connection
        cursor.close()
        conn.close()
        print('\n[INFO] Datenbankverbindung geschlossen')

    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print(f'\n[ERROR] Oracle Datenbankfehler: {error.message}')
        print('[INFO] Möglicherweise existiert die Schule oder Email bereits.')
        sys.exit(1)
    except Exception as e:
        print(f'\n[ERROR] Fehler: {str(e)}')
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    add_ggs_sandstrasse_oracle()
