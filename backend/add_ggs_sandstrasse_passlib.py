"""
GGS Sandstraße Duisburg - Deployment mit passlib (Backend-kompatibel)
Verwendet passlib.context.CryptContext wie das Backend
"""

import os
import sys
import sqlite3
import uuid
from passlib.context import CryptContext
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Password hashing - EXACTLY wie im Backend
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def hash_password(password: str) -> str:
    """Hash password using passlib CryptContext (matches backend)"""
    return pwd_context.hash(password)

def add_ggs_sandstrasse():
    """Legt die GGS Sandstraße Duisburg im System an"""

    # Database connection
    db_path = 'dev_database.db'

    print('=' * 80)
    print('GGS SANDSTRASSE DUISBURG - SCHULANLAGE (PASSLIB VERSION)')
    print('=' * 80)
    print(f'[INFO] Verbinde mit SQLite Database: {db_path}')

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        print('[SUCCESS] Datenbankverbindung erfolgreich')

        # 1. Create school
        school_id = str(uuid.uuid4()).replace('-', '').upper()

        school_data = {
            'school_id': school_id,
            'name': 'Gemeinschaftsgrundschule Sandstraße',
            'address': 'Sandstraße 46, Duisburg-Marxloh',
            'city': 'Duisburg',
            'postal_code': '47169',
            'contact_email': 'ggs.sandstr@stadt-duisburg.de',
            'contact_phone': '0203-403688'
        }

        print('\n[SCHULE] Lege Schule an...')
        print(f'  Name: {school_data["name"]}')
        print(f'  Adresse: {school_data["address"]}, {school_data["postal_code"]} {school_data["city"]}')
        print(f'  Email: {school_data["contact_email"]}')
        print(f'  Telefon: {school_data["contact_phone"]}')

        cursor.execute("""
            INSERT INTO SCHOOLS (school_id, name, address, postal_code, city, contact_email, contact_phone)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            school_data['school_id'],
            school_data['name'],
            school_data['address'],
            school_data['postal_code'],
            school_data['city'],
            school_data['contact_email'],
            school_data['contact_phone']
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

        cursor.execute("""
            INSERT INTO USERS (user_id, school_id, email, password_hash, first_name, last_name, role, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
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

        cursor.execute("""
            INSERT INTO USERS (user_id, school_id, email, password_hash, first_name, last_name, role, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
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
        from api.auth_utils import verify_password
        verification_result = verify_password(admin_password, admin_password_hash)
        print(f'  Password verification: {verification_result}')

        if not verification_result:
            print('[ERROR] PASSWORD VERIFICATION FAILED!')
            raise Exception('Password hash verification failed')

        # Print summary
        print('\n' + '=' * 80)
        print('ZUSAMMENFASSUNG - GGS SANDSTRASSE DUISBURG')
        print('=' * 80)
        print(f'\n✅ Schule angelegt:')
        print(f'   ID: {school_id}')
        print(f'   Name: {school_data["name"]}')
        print(f'   Adresse: {school_data["address"]}, {school_data["postal_code"]} {school_data["city"]}')
        print(f'   Email: {school_data["contact_email"]}')
        print(f'   Telefon: {school_data["contact_phone"]}')

        print(f'\n✅ Admin-Zugang:')
        print(f'   Email: {admin_email}')
        print(f'   Passwort: {admin_password}')
        print(f'   Name: Klaus Hagge (Schulleitung)')

        print(f'\n✅ Lehrkraft-Zugang:')
        print(f'   Email: {teacher_email}')
        print(f'   Passwort: {teacher_password}')

        print(f'\n🌐 Login URL: https://edufunds.org')
        print('=' * 80)

        # Close connection
        cursor.close()
        conn.close()
        print('\n[INFO] Datenbankverbindung geschlossen')

    except sqlite3.IntegrityError as e:
        print(f'\n[ERROR] Datenbankfehler (Unique Constraint): {str(e)}')
        print('[INFO] Möglicherweise existiert die Schule oder Email bereits.')
        sys.exit(1)
    except Exception as e:
        print(f'\n[ERROR] Fehler: {str(e)}')
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    add_ggs_sandstrasse()
