# SeedData/pharmacy_inserts.py

import os
import sqlite3
from datetime import datetime
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from db import get_connection, get_db_path

def seed_pharmacy():
    db_path = get_db_path()
    print(f"📂 Using DB: {db_path}")

    conn = get_connection()
    cur = conn.cursor()

    # Ensure pharmacy table exists
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pharmacy (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            drug_name TEXT NOT NULL,
            supplied INTEGER DEFAULT 0,
            distributed INTEGER DEFAULT 0,
            amount_due REAL DEFAULT 0.0,
            amount_collected REAL DEFAULT 0.0
        )
    """)
    conn.commit()

    # Clear any old dummy data to avoid duplicates
    cur.execute("DELETE FROM pharmacy")

    # Dummy data: Supplied by Admin, Amount Due from Admin
    sample_drugs = [
        ("Paracetamol", 200, 40, 1500.0, 600.0),
        ("Metformin", 100, 20, 2500.0, 1000.0),
        ("Amoxicillin", 50, 10, 1800.0, 300.0),
        ("Vitamin D", 80, 15, 1200.0, 400.0),
    ]

    cur.executemany("""
        INSERT INTO pharmacy (drug_name, supplied, distributed, amount_due, amount_collected)
        VALUES (?, ?, ?, ?, ?)
    """, sample_drugs)

    conn.commit()
    conn.close()
    print("✅ Seeded pharmacy drugs successfully.")

if __name__ == "__main__":
    seed_pharmacy()
