# blood_sugar_inserts.py
import os, sys
from datetime import datetime, timedelta
from pathlib import Path

# Ensure project root (where db.py lives) is in path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from db import get_connection, get_db_path

def seed_blood_sugars():
    print(f"📂 Using DB: {get_db_path()}")

    conn = get_connection()
    cur = conn.cursor()

    # Pick a patient to seed (Ravi Kumar with id=5)
    cur.execute("SELECT id, name FROM patients WHERE id=5")
    row = cur.fetchone()
    if not row:
        print("❌ Patient #5 not found.")
        return
    pid, name = row
    print(f"👤 Using patient #{pid}: {name}")

    now = datetime.now()

    sample_sugars = [
        # Past data
        (pid, "FBS", 95, None, "past test", "no symptoms", "fasting", 0, (now - timedelta(days=10)).isoformat()),
        (pid, "PPBS", 135, None, "past test", "mild", "post meal", 0, (now - timedelta(days=10)).isoformat()),
        (pid, "HbA1c", 5.8, None, "past test", "", "quarterly", 0, (now - timedelta(days=10)).isoformat()),

        # Current data
        (pid, "FBS", 105, None, "today test", "", "fasting", 0, now.isoformat()),
        (pid, "PPBS", 145, None, "today test", "dizzy", "post meal", 0, now.isoformat()),
        (pid, "HbA1c", 6.1, None, "today test", "", "quarterly", 0, now.isoformat()),

        # Future scheduled data
        (pid, "FBS", 100, None, "scheduled", "", "fasting", 0, (now + timedelta(days=5)).isoformat()),
        (pid, "PPBS", 130, None, "scheduled", "", "post meal", 0, (now + timedelta(days=5)).isoformat()),
        (pid, "HbA1c", 6.0, None, "scheduled", "", "quarterly", 0, (now + timedelta(days=5)).isoformat()),
    ]

    cur.executemany("""
        INSERT INTO blood_sugar_tests 
        (fk_patient_id, test_type, result_mg_dl, last_meal_time, history, symptoms, notes, sent_to_doctor, taken_at, recorded_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)
    """, sample_sugars)

    conn.commit()
    conn.close()
    print("✅ Seeded blood sugar tests successfully.")

if __name__ == "__main__":
    seed_blood_sugars()
