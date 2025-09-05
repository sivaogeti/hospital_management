import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))  # add project root to sys.path

from db import get_connection, get_db_path

def migrate_vitals_temp_to_fahrenheit():
    db_path = get_db_path()
    print(f"📂 Using DB: {db_path}")
    conn = get_connection(); cur = conn.cursor()

    # Check tables
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    print("Tables in DB:", [r[0] for r in cur.fetchall()])

    # Inspect schema
    cur.execute("PRAGMA table_info(vitals)")
    cols = [c[1].lower() for c in cur.fetchall()]
    print("Columns in vitals:", cols)

    if "temperature" not in cols:
        print("❌ No 'temperature' column found.")
        conn.close()
        return

    # Fetch and update
    cur.execute("SELECT id, temperature FROM vitals WHERE temperature IS NOT NULL")
    rows = cur.fetchall()

    updated = 0
    for vid, temp_c in rows:
        if temp_c < 80:
            temp_f = round((float(temp_c) * 9 / 5) + 32, 1)
            cur.execute("UPDATE vitals SET temperature = ? WHERE id = ?", (temp_f, vid))
            updated += 1

    conn.commit(); conn.close()
    print(f"✅ Migrated {updated} rows Celsius → Fahrenheit.")

if __name__ == "__main__":
    migrate_vitals_temp_to_fahrenheit()
