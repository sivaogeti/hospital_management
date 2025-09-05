# SeedData/medications_inserts.py
import os, sys
import sqlite3
from datetime import datetime, UTC

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db import get_connection, get_db_path

def seed_medications():
    conn = get_connection(); cur = conn.cursor()

    print("📂 Using DB:", get_db_path())
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    print("Tables in DB:", [r[0] for r in cur.fetchall()])

    # Get some existing patient IDs
    cur.execute("SELECT id, name FROM patients LIMIT 5")
    patients = cur.fetchall()
    if not patients:
        print("❌ No patients found. Seed patients first.")
        return

    print("👥 Found patients:", [(p["id"], p["name"]) for p in patients])

    now = datetime.now(UTC).isoformat()

    # Map sample medications to real patient IDs
    sample_meds = []
    for i, p in enumerate(patients, start=1):
        sample_meds.append((p["id"], "Metformin", "500mg", "Twice daily", "30 days", "Apollo Hospital", 30, "Diabetes management", now))
        sample_meds.append((p["id"], "Paracetamol", "650mg", "Thrice daily", "5 days", "Local Clinic", 5, "Fever", now))

    cur.executemany("""
        INSERT INTO medications
        (patient_id, drug_name, dose, frequency, duration, referral_facility, follow_up_days, reason, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, sample_meds)

    conn.commit(); conn.close()
    print("✅ Seeded medications successfully.")

if __name__ == "__main__":
    seed_medications()
