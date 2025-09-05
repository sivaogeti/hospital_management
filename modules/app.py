import streamlit as st
from datetime import date, datetime

try:
    from db import get_connection
except Exception:
    get_connection = None


# -----------------------------
# DB helpers
# -----------------------------

def _ensure_tables():
    if not get_connection:
        return
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            phone TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS vitals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fk_patient_id INTEGER NOT NULL,
            recorded_at TEXT NOT NULL,
            bp_sys INTEGER,
            bp_dia INTEGER,
            pulse INTEGER,
            temperature REAL,
            resp_rate INTEGER,
            spo2 INTEGER,
            height_cm REAL,
            weight_kg REAL,
            bmi REAL,
            notes TEXT,
            recorded_by INTEGER,
            FOREIGN KEY (fk_patient_id) REFERENCES patients(id)
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS lab_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fk_patient_id INTEGER NOT NULL,
            ordered_at TEXT NOT NULL,
            test_name TEXT NOT NULL,
            priority TEXT,
            notes TEXT,
            ordered_by INTEGER,
            status TEXT DEFAULT 'Pending',
            FOREIGN KEY (fk_patient_id) REFERENCES patients(id)
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL UNIQUE,
            category TEXT,
            qty INTEGER DEFAULT 0,
            unit TEXT DEFAULT 'pcs',
            last_updated TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def _count_rows(table: str) -> int:
    if not get_connection:
        return 0
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        n = cur.fetchone()[0] or 0
    except Exception:
        n = 0
    conn.close()
    return n


def _today_visits_count() -> int:
    if not get_connection:
        return 0
    conn = get_connection()
    cur = conn.cursor()
    # recorded_at is ISO text; use date() extraction for SQLite
    cur.execute("SELECT COUNT(*) FROM vitals WHERE date(recorded_at) = date('now')")
    n = cur.fetchone()[0] or 0
    conn.close()
    return n


def _low_stock(threshold: int = 5):
    if not get_connection:
        return []
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, item_name, category, qty, unit, last_updated FROM stock WHERE qty <= ? ORDER BY qty ASC, item_name",
        (threshold,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


# -----------------------------
# UI helpers
# -----------------------------

def _kpi_card(title: str, value: str):
    st.markdown(
        f"""
        <div style=\"background:#fff;border:1px solid #e5e7eb;border-radius:14px;padding:14px;box-shadow:0 4px 12px rgba(0,0,0,.06);\">
            <div style=\"font-size:.85rem;color:#6b7280;font-weight:600;\">{title}</div>
            <div style=\"font-size:1.6rem;font-weight:800;line-height:2.2rem;\">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------
# Main entry
# -----------------------------

def render_management_dashboard(user: dict):
    """Front page for Management login."""
    _ensure_tables()

    st.markdown("### 🧭 Management Dashboard")
    st.caption(f"Welcome, {user.get('name','Management')} · {date.today().strftime('%b %d, %Y')}")

    # KPI row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        _kpi_card("Total Patients", str(_count_rows("patients")))
    with c2:
        _kpi_card("Today's Visits", str(_today_visits_count()))
    with c3:
        # Pending tests = lab orders not completed
        pending = 0
        if get_connection:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM lab_orders WHERE status != 'Completed'")
            pending = cur.fetchone()[0] or 0
            conn.close()
        _kpi_card("Pending Tests", str(pending))
    with c4:
        # Total stock items (sum of qty)
        total_stock = 0
        if get_connection:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT COALESCE(SUM(qty),0) FROM stock")
            total_stock = cur.fetchone()[0] or 0
            conn.close()
        _kpi_card("Items in Stock", str(total_stock))

    st.write("")

    # Tabs
    tab_overview, tab_stock, tab_users, tab_reports = st.tabs([
        "Overview",
        "Stock",
        "Users",
        "Reports",
    ])

    # ---------------- Overview ----------------
    with tab_overview:
        st.subheader("Today at a glance")
        if get_connection:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                """
                SELECT v.id, p.name, v.recorded_at, v.bp_sys, v.bp_dia, v.pulse, v.temperature
                FROM vitals v JOIN patients p ON p.id = v.fk_patient_id
                WHERE date(v.recorded_at) = date('now')
                ORDER BY v.id DESC
                """
            )
            rows = cur.fetchall()
            conn.close()
            if rows:
                import pandas as pd
                df = pd.DataFrame(
                    rows,
                    columns=["Visit ID", "Patient", "Recorded At", "BP Sys", "BP Dia", "Pulse", "Temp (°C)"],
                )
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No visits recorded today yet.")
        else:
            st.warning("DB connection not configured.")

    # ---------------- Stock ----------------
    with tab_stock:
        st.subheader("Low Stock Alerts")
        threshold = st.number_input("Alert threshold (qty <=)", min_value=0, max_value=1000, step=1, value=5)
        rows = _low_stock(threshold)
        if rows:
            import pandas as pd
            df = pd.DataFrame(rows, columns=["ID", "Item", "Category", "Qty", "Unit", "Updated"])
            st.dataframe(df, use_container_width=True, hide_index=True)
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("Download CSV", csv, file_name=f"low_stock_{threshold}.csv", mime="text/csv")
        else:
            st.success("All stock above threshold.")

    # ---------------- Users ----------------
    with tab_users:
        st.subheader("Users & Roles (placeholder)")
        st.info(
            "Integrate with your auth/user table here to manage staff (RMP/Doctor/Management) and patient portal accounts."
        )

    # ---------------- Reports ----------------
    with tab_reports:
        st.subheader("Reports (quick export)")
        st.caption("Export simple counts for external reporting.")
        if get_connection:
            import pandas as pd
            today = date.today().isoformat()
            counts = {
                "date": [today],
                "total_patients": [_count_rows("patients")],
                "today_visits": [_today_visits_count()],
                "pending_tests": [pending],
                "items_in_stock": [total_stock],
            }
            df = pd.DataFrame(counts)
            st.dataframe(df, use_container_width=True, hide_index=True)
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("Download Counts CSV", csv, file_name=f"mgmt_counts_{today}.csv", mime="text/csv")
        else:
            st.warning("DB connection not configured.")
