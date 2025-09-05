import os
import sqlite3
from pathlib import Path

# Always resolve relative to this file's location (project root)
BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DB_PATH = os.environ.get("HOSPITAL_DB_PATH", str(BASE_DIR / "data" / "hospital.db"))

def _ensure_parent_dir(db_path: str):
    p = Path(db_path).expanduser().resolve()
    p.parent.mkdir(parents=True, exist_ok=True)
    return str(p)

def get_connection():
    db_path = _ensure_parent_dir(DEFAULT_DB_PATH)
    conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def get_db_path() -> str:
    return _ensure_parent_dir(DEFAULT_DB_PATH)

#Vitals table
#ALTER TABLE vitals ADD COLUMN sent_to_doctor INTEGER NOT NULL DEFAULT 0;
#CREATE INDEX IF NOT EXISTS idx_vitals_sent ON vitals (sent_to_doctor);

#Sugar table 
#-- add a frequency_days column for follow-up (default 0 = no follow-up)
#ALTER TABLE blood_sugar_tests
#ADD COLUMN IF NOT EXISTS frequency_days INTEGER DEFAULT 0;



# modules/auth/db.py
import sqlite3
import os
import hashlib
import binascii
from datetime import datetime
from typing import Optional, Tuple

DEFAULT_DB = os.path.join(os.path.dirname(__file__), "data", "hospital.db")

def get_conn(db_path: str = DEFAULT_DB):
    return sqlite3.connect(db_path, check_same_thread=False)

def init_db(db_path: str = DEFAULT_DB):
    conn = get_conn(db_path)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        name TEXT,
        role TEXT NOT NULL,
        salt TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TEXT
    )
    """)
    conn.commit()
    conn.close()

def _hash_password(password: str, salt: bytes, iterations: int = 200_000) -> str:
    # PBKDF2-HMAC-SHA256
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return binascii.hexlify(dk).decode("ascii")

def create_user(username: str, role: str, password: str, name: Optional[str] = None, db_path: str = DEFAULT_DB) -> bool:
    """
    Returns True if created, False if user exists.
    """
    init_db(db_path)
    salt = os.urandom(16)
    hash_hex = _hash_password(password, salt)
    salt_hex = binascii.hexlify(salt).decode("ascii")
    created_at = datetime.utcnow().isoformat()
    conn = get_conn(db_path)
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (username, name, role, salt, password_hash, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (username, name or username, role, salt_hex, hash_hex, created_at)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return False
    conn.close()
    return True

def get_user_by_username(username: str, db_path: str = DEFAULT_DB) -> Optional[dict]:
    init_db(db_path)
    conn = get_conn(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id, username, name, role, salt, password_hash, created_at FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "id": row[0],
        "username": row[1],
        "name": row[2],
        "role": row[3],
        "salt": row[4],
        "password_hash": row[5],
        "created_at": row[6]
    }

import hmac   # add at top

def verify_password(stored_salt_hex: str, stored_hash_hex: str, provided_password: str, iterations: int = 200_000) -> bool:
    salt = binascii.unhexlify(stored_salt_hex)
    computed = _hash_password(provided_password, salt, iterations)
    # Use constant-time comparison from hmac (not hashlib)
    return hmac.compare_digest(computed, stored_hash_hex)

