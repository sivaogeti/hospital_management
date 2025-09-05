import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "hospital.db"

def seed_vitals():
    print(f"📂 Using DB: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Check patients
    cur.execute("SELECT id, name FROM patients")
    patients = cur.fetchall()
    if not patients:
        print("⚠️ No patients found. Please seed patients first.")
        return

    pid = patients[0][0]  # use first patient for demo
    print(f"👤 Using patient #{pid}: {patients[0][1]}")

    today = datetime.now().date()

    sample_vitals = [
        # Old dates
        (pid, (today - timedelta(days=10)).isoformat(), 120, 80, 72, 36.6),
        (pid, (today - timedelta(days=5)).isoformat(), 130, 85, 75, 36.8),
        (pid, (today - timedelta(days=2)).isoformat(), 118, 78, 70, 36.7),
        # Today
        (pid, today.isoformat(), 125, 82, 74, 36.9),
        # Future dates (to simulate scheduled monitoring)
        (pid, (today + timedelta(days=2)).isoformat(), 128, 84, 76, 37.0),
        (pid, (today + timedelta(days=5)).isoformat(), 122, 79, 73, 36.5),
    ]

    cur.executemany("""
        INSERT INTO vitals (fk_patient_id, recorded_at, bp_sys, bp_dia, pulse, temperature)
        VALUES (?, ?, ?, ?, ?, ?)
    """, sample_vitals)

    conn.commit()
    conn.close()
    print("✅ Seeded vitals successfully.")

if __name__ == "__main__":
    seed_vitals()
