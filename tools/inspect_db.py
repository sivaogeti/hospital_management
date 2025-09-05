# tools/inspect_db.py
"""
Quick DB inspector for your hospital app.
Usage (from project root):
> python tools/inspect_db.py
"""
from data.db import get_connection, get_db_path

def main():
    conn = get_connection()
    cur = conn.cursor()

    print(f"DB path : {get_db_path()}")

    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = [r[0] for r in cur.fetchall()]
    if not tables:
        print("No tables found.")
        return
    print("\nTables:")
    for t in tables:
        print(f" - {t}")

    print("\nSchemas:\n---------")
    for t in tables:
        print(f"\n[{t}]")
        cur.execute(f"PRAGMA table_info({t});")
        for cid, name, ctype, notnull, dflt, pk in cur.fetchall():
            nn = " NOT NULL" if notnull else ""
            pkflag = " PRIMARY KEY" if pk else ""
            print(f"  {name} {ctype}{nn}{pkflag} default={dflt}")

    conn.close()

if __name__ == "__main__":
    main()
