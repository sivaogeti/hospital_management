import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))  # add project root

from db import get_connection, get_db_path

def seed_rmp_users():
    print("📂 Using DB:", get_db_path())  # <--- show full path

    conn = get_connection()
    cur = conn.cursor()

    # Show tables
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    print("Tables in DB:", [r[0] for r in cur.fetchall()])

    sample_users = [
        ("Dr. Ramesh Kumar", "9876543210", "123456789012", "Madhurawada, Vizag",
         None, "General Practitioner", "Available 9am–5pm"),
        ("Dr. Priya Verma", "9123456780", "234567890123", "Gajuwaka, Vizag",
         None, "Community Medicine", "Handles outreach camps"),
        ("Dr. Anil Sharma", "9988776655", "345678901234", "Seethammadhara, Vizag",
         None, "Family Medicine", "Special interest in diabetes care"),
    ]

    cur.executemany("""
        INSERT INTO rmp_users (name, mobile, aadhar, address, photo_path, specialization, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, sample_users)

    conn.commit(); conn.close()
    print("✅ Seeded RMP users successfully.")

if __name__ == "__main__":
    seed_rmp_users()
