import sys, os
from datetime import datetime

# Add project root to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(BASE_DIR)

from db import get_connection, get_db_path

def seed_messages():
    db_path = get_db_path()
    print(f"📂 Using DB: {db_path}")

    conn = get_connection()
    cur = conn.cursor()

    # Ensure messages table exists
    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_role TEXT NOT NULL,
            recipient_role TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    now = datetime.now().isoformat()

    sample_msgs = [
        # RMP to Doctor
        ("RMP", "Doctor", "Hello Doctor, I have uploaded blood sugar reports for patient Priya Verma.", now),
        ("Doctor", "RMP", "Thanks. I reviewed them, please advise the patient to continue medication.", now),

        # RMP to Admin
        ("RMP", "Admin", "I have placed a stock request for test strips. Please check.", now),
        ("Admin", "RMP", "Received your request. It has been approved, delivery in 2 days.", now),

        # System generated alert → deliver to RMP
        ("System", "RMP", "Stock alert: Lancets running low (≤5 units).", now),
    ]

    cur.executemany("""
        INSERT INTO messages (sender_role, recipient_role, message, created_at)
        VALUES (?, ?, ?, ?)
    """, sample_msgs)

    conn.commit()
    conn.close()
    print("✅ Seeded messages successfully.")

if __name__ == "__main__":
    seed_messages()
