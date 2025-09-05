# SeedData/doctor_advice_inserts.py
import os, sys
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from db import get_connection, get_db_path

def seed_doctor_advice():
    conn = get_connection()
    cur = conn.cursor()

    # Check which patients exist
    cur.execute("SELECT id, name FROM patients LIMIT 5")
    patients = cur.fetchall()
    print("👥 Found patients:", [(p["id"], p["name"]) for p in patients])

    if not patients:
        print("⚠️ No patients found. Please seed patients first.")
        return

    now = datetime.utcnow().isoformat()

    sample_advice = [
        (patients[0]["id"], "Continue regular exercise and reduce salt intake", now),
        (patients[1]["id"], "Start vitamin supplements, recheck after 1 month", now),
        (patients[2]["id"], "Monitor blood sugar daily, follow up next week", now),
    ]

    cur.executemany("""
        INSERT INTO doctor_advice (patient_id, advice, created_at)
        VALUES (?, ?, ?)
    """, sample_advice)

    conn.commit()
    conn.close()
    print("✅ Seeded doctor advice successfully.")

if __name__ == "__main__":
    print("📂 Using DB:", get_db_path())
    seed_doctor_advice()
