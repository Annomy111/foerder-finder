"""
Database Adapter - Auto-detects Oracle or SQLite
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Auto-detect database type
USE_SQLITE = os.getenv('USE_SQLITE', 'false').lower() == 'true'

if USE_SQLITE:
    print("[DB] Using SQLite (Development Mode)")
    from utils.database_sqlite import (
        get_db_cursor,
        get_db_connection,
        get_db_manager,
        init_sqlite_schema,
        seed_demo_data
    )
else:
    print("[DB] Using Oracle Database (Production Mode)")
    try:
        from utils.database import (
            get_db_cursor,
            get_db_connection,
            get_db_manager
        )
        # Oracle doesn't need init functions
        init_sqlite_schema = None
        seed_demo_data = None
    except Exception as e:
        print(f"[DB] Oracle import failed: {e}")
        print("[DB] Falling back to SQLite")
        USE_SQLITE = True
        from utils.database_sqlite import (
            get_db_cursor,
            get_db_connection,
            get_db_manager,
            init_sqlite_schema,
            seed_demo_data
        )


__all__ = [
    'get_db_cursor',
    'get_db_connection',
    'get_db_manager',
    'init_sqlite_schema',
    'seed_demo_data',
    'USE_SQLITE'
]
