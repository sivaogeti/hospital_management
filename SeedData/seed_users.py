# seed_users.py
import os
import sys

# 🔧 Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from db import create_user, init_db, DEFAULT_DB


def seed():
    # Ensure DB created
    init_db()

    users = [
        {"username": "patient1", "name": "Patient One", "role": "Patient", "password": "patientpass"},
        {"username": "agent1", "name": "Health Agent One", "role": "Health Agent", "password": "agentpass"},
        {"username": "doctor1", "name": "Doctor One", "role": "Doctor", "password": "doctorpass"},
        {"username": "manager1", "name": "Manager One", "role": "Management", "password": "managerpass"},
    ]

    for u in users:
        ok = create_user(u["username"], u["role"], u["password"], name=u["name"])
        if ok:
            print(f"Created: {u['username']} / {u['password']} ({u['role']})")
        else:
            print(f"Skipped (exists): {u['username']}")

if __name__ == "__main__":
    print("Seeding DB:", DEFAULT_DB)
    seed()
