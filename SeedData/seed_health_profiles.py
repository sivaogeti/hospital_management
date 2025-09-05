import sys, os
from datetime import datetime, timedelta
import random

# 🔧 Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# seed_health_profiles.py
from db import get_connection

def seed_health_profiles():
    conn = get_connection()
    cur = conn.cursor()

    # Fetch all patients
    cur.execute("SELECT id, name FROM patients")
    patients = cur.fetchall()
    if not patients:
        print("❌ No patients found. Please seed patients first.")
        return

    # Clear old vitals and sugar tests
    cur.execute("DELETE FROM vitals")
    cur.execute("DELETE FROM blood_sugar_tests")

    start_date = datetime.now() - timedelta(days=730)  # 2 years back
    today = datetime.now()

    for pid, name in patients:
        print(f"👤 Seeding data for patient {pid}: {name}")
        date_cursor = start_date

        while date_cursor <= today:
            # --- vitals ---
            bp_sys = random.randint(100, 160)
            bp_dia = random.randint(65, 100)
            pulse = random.randint(55, 110)
            temp_f = round(random.uniform(97.0, 99.5), 1)
            spo2 = random.randint(94, 100)
            height = random.choice([160.0, 165.0, 170.0])  # keep constant
            weight = round(random.uniform(55, 80), 1)
            waist = round(random.uniform(70, 95), 1)
            bmi = round(weight / ((height/100)**2), 1)

            cur.execute("""
                INSERT INTO vitals (fk_patient_id, recorded_at, bp_sys, bp_dia, pulse, temperature,
                                    spo2, height_cm, weight_kg, waist_cm, bmi, notes, recorded_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pid, date_cursor.isoformat(), bp_sys, bp_dia, pulse, temp_f,
                spo2, height, weight, waist, bmi, "Seeded data", 1
            ))

            # --- blood sugar test ---
            sugar_type = random.choice(["FBS", "PPBS", "RBS"])
            if sugar_type == "FBS":
                sugar_val = random.randint(70, 160)
            elif sugar_type == "PPBS":
                sugar_val = random.randint(90, 220)
            else:
                sugar_val = random.randint(90, 220)

            cur.execute("""
                INSERT INTO blood_sugar_tests
                (fk_patient_id, test_type, result_mg_dl, last_meal_time, history,
                 symptoms, notes, sent_to_doctor, taken_at, recorded_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pid, sugar_type, sugar_val, "2 hrs ago", "", "", "Seeded test", 0,
                date_cursor.isoformat(), 1
            ))

            # Increment by 1 day
            date_cursor += timedelta(days=1)

    conn.commit()
    conn.close()
    print("✅ Seeded 2 years health profile data for all patients.")

if __name__ == "__main__":
    seed_health_profiles()
