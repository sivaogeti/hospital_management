# modules/rmp/app.py
import streamlit as st
from datetime import datetime, date, timezone
from typing import Optional
from pathlib import Path
import datetime
import streamlit as st
from pathlib import Path
import time
import traceback

import streamlit as st

# Force wide layout (before any other Streamlit UI calls)
st.set_page_config(layout="wide")

RMP_CSS = """
<style>
html, body, [data-testid="stAppViewContainer"] { background: #f4f8fb; }

/* Scope container so our styles don't leak */
.rmp-scope { color: #1e293b; }

/* Dashboard grid: force two columns (desktop-style) even on narrow viewports */
.dashboard-grid {
  display: grid !important;
  grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
  gap: 20px !important;
  align-items: start !important;
}

/* Make sure the tiles keep their visual sizing inside the grid */
.dashboard-grid .rmp-card,
.dashboard-grid div[data-testid="stButton"] > button {
  width: 100% !important;
  box-sizing: border-box !important;
}

/* Optional: horizontal scroll on very small devices
@media (max-width: 420px) {
   .dashboard-grid {
      grid-template-columns: repeat(2, minmax(200px, 1fr));
      grid-auto-flow: column;
      overflow-x:auto;
   }
}
*/
</style>
"""



# place after you have rendered the tiles/columns
import streamlit.components.v1 as components

components.html("""
<script>
(function(){
  try {
    var apply = function(){
      var g = document.querySelector('.dashboard-grid') || document.querySelector('[data-testid^="stHorizontalBlock"]');
      if (!g) return;
      if (window.innerWidth >= 340) {
        g.style.gridTemplateColumns = 'repeat(2, 1fr)';
      } else {
        g.style.gridTemplateColumns = '1fr';
      }
      // reduce child min-widths
      var children = g.querySelectorAll('*');
      children.forEach(function(c){ c.style.minWidth='0'; c.style.maxWidth='100%'; c.style.boxSizing='border-box'; });
      console.log('DEBUG: applied dashboard-grid fix, width=' + window.innerWidth);
    };
    // run now and on resize
    setTimeout(apply, 600);
    window.addEventListener('resize', apply);
  } catch(e) {
    console.log('ERROR injecting dashboard fix', e);
  }
})();
</script>
""", height=1)




# --- Added to force wide layout and prevent Streamlit from stacking columns on narrow viewports ---
try:
    import streamlit as st  # ensure st is available
    st.set_page_config(layout="wide")
    st.markdown("""<style>
  
  
    /* Optional: increase min-width for column children so they stay side-by-side */
    [data-testid="stVerticalBlock"] > div {
        min-width: 0 !important;
    }
    </style>""", unsafe_allow_html=True)
except Exception:
    pass
# --- End addition ---
import streamlit as st
from pathlib import Path

def local_css(path: str):
    p = Path(path)
    if p.exists():
        css = p.read_text(encoding="utf-8")
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    else:
        # fallback inline override
        st.markdown(
            """
            <style>
            .dashboard-grid { grid-template-columns: repeat(2, 1fr) !important; }
            @media (max-width:300px) { .dashboard-grid { grid-template-columns: 1fr !important; } }
            </style>
            """,
            unsafe_allow_html=True,
        )

# call this early in your app
local_css("static/style.css")  # adjust path if you use 'style.css'

if "rmp_page" not in st.session_state:
    st.session_state["rmp_page"] = "dashboard"
    
def _go(page_key: str):
    # keep both, in case older code still reads rmp_page somewhere
    st.session_state["rmp_section"] = page_key
    st.session_state["rmp_page"] = page_key

def _kpi_card(icon, title, value):
    st.markdown(
        f"""
        <div class="rmp-card kpi-card">
            <div class="kpi-title">{icon} {title}</div>
            <div class="kpi-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def _route_from_query():
    qp = st.query_params
    dest = qp.get("rmp_section", None)
    if dest:
        st.session_state["rmp_section"] = dest
        st.session_state["rmp_page"] = dest
        # clear after consuming so refresh doesn't re-route again
        try:
            del qp["rmp_section"]
        except Exception:
            pass


# --- navigation helpers for sub-pages ---
def _set_substate(section: str, sub: str | None):
    """
    Store the parent section and an optional sub-state.
    Example: section='Patients', sub='New' -> rmp_section='Patients', patients_sub='New'
    """
    st.session_state["rmp_section"] = section
    st.session_state["rmp_page"] = section  # keep legacy compatibility
    # keep a per-section sub-state key so different sections can have their own subtabs
    key = f"{section.lower().replace(' ', '_')}_sub"
    st.session_state[key] = sub

def _current_sub(section: str, default: str = "New") -> str:
    """Read sub-state for a section (used by your router/view)."""
    key = f"{section.lower().replace(' ', '_')}_sub"
    return st.session_state.get(key, default)



def _sub_card(icon: str, title: str, btn_key: str, section: str, sub: str):
    """
    Render a sub-card as a full-tile clickable button (no separate 'Open' button).
    Uses a marker div (id `submark_{btn_key}`) so CSS can style the Streamlit button that follows.
    When clicked, sets the substate and reruns.
    """
    # resolve the target (keeps existing routing behavior)
    dest = _resolve_target(btn_key, title, None)

    # marker id so we can style only the following button via CSS
    mid = f"submark_{btn_key}"

    # place the marker
    st.markdown(f'<div id="{mid}"></div>', unsafe_allow_html=True)

    # build a simple label with icon + title (no metric)
    label = f"{icon}  {title}"

    # clickable full-card button
    if st.button(label, key=btn_key, use_container_width=True):
        # set the substate and rerun to reflect navigation
        _set_substate(section, sub)
        st.rerun()

    # inject styles targeting the button that immediately follows our marker
    st.markdown(
        f"""
        <style>
          /* style only the st.button wrapper that immediately follows this marker */
          div#{mid} + div[data-testid="stButton"] > button {{
            height: var(--sub-card-height, 200px);
            min-height: var(--sub-card-height, 200px);
            border-radius: 14px !important;
            border: 1px solid #e6e9ee;
            box-shadow: 0 6px 14px rgba(2,132,199,.06);
            background: #ffffff;
            color: #0f172a;
            text-align: center;
            font-weight: 700;
            white-space: pre-wrap;
            line-height: 1.2;
            padding: 18px;
            font-size: 1.05rem;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            gap: 6px;
          }}
          /* hover */
          div#{mid} + div[data-testid="stButton"] > button:hover {{
            box-shadow: 0 8px 18px rgba(2,132,199,.10);
            transform: translateY(-2px);
          }}
        </style>
        """,
        unsafe_allow_html=True,
    )

ROUTE_ALIASES = {
    # extend this map if your router uses specific names
    "btn_patients_new": "Patients_New",
    "btn_patients_search": "Patients_Search",
    "btn_stock_orders": "Stock_Order_List",
    "btn_stock_low":    "Stock_Low_Alert",
    # examples:
    # "btn_vitals_new": "Record_Vitals_New",
}


def _resolve_target(key: str, title: str, target: str|None):
    if target:
        return target
    if isinstance(key, str) and key.startswith("btn_"):
        # 1) explicit alias
        if key in ROUTE_ALIASES:
            return ROUTE_ALIASES[key]
        # 2) best-effort: take suffix and Title_Case with underscores
        suffix = key[4:]  # drop 'btn_'
        parts = [p.capitalize() for p in suffix.split("_")]
        return "_".join(parts)  # e.g., patients_new -> Patients_New
    return title

def _go(page_key: str):
    # set both to satisfy old & new code
    st.session_state["rmp_section"] = page_key
    st.session_state["rmp_page"] = page_key


try:
    from db import get_connection
except Exception:
    get_connection = None
    
    
# Fixed items catalog (as per your list)
RMP_STOCK_ITEMS = [
    "Test Strips",
    "Lancet tool",
    "BP cuffs",
    "Thermometer",
    "Tape",
    "Pulse Meter",
]


# =========================
# DB helpers
# =========================
def _ensure_patient_columns():
    """Add new patient columns if they don't exist (SQLite safe migration)."""
    if not get_connection:
        return
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(patients)")
    existing = {row[1] for row in cur.fetchall()}

    # column_name -> SQL type
    to_add = {
        "father_name": "TEXT",
        "mobile": "TEXT",
        "aadhar": "TEXT",
        "address": "TEXT",
        "village": "TEXT",            # <-- add this line
        "photo_path": "TEXT",
        "diet": "TEXT",
        "breakfast": "TEXT",
        "lunch": "TEXT",
        "dinner": "TEXT",
        "tobacco": "TEXT",          # Yes/No
        "alcohol": "TEXT",          # Yes/No
        "activity_level": "TEXT",   # Sedentary / Lightly / Moderate / Very
        "family_history": "TEXT",
    }

    for col, sqltype in to_add.items():
        if col not in existing:
            cur.execute(f"ALTER TABLE patients ADD COLUMN {col} {sqltype}")

    conn.commit()
    conn.close()


def _ensure_vitals_columns():
    """Add new vitals columns if they don't exist (SQLite safe migration)."""
    if not get_connection:
        return
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(vitals)")
    existing = {row[1] for row in cur.fetchall()}

    to_add = {
        "waist_cm": "REAL",   # <-- Weist
    }
    for col, sqltype in to_add.items():
        if col not in existing:
            cur.execute(f"ALTER TABLE vitals ADD COLUMN {col} {sqltype}")

    conn.commit()
    conn.close()

def _reset_vitals_form():
    """Clear vitals inputs and disable the Save button by making the form invalid."""
    for k, v in {
        "v_bp_sys": 0, "v_bp_dia": 0, "v_pulse": 0, "v_temp": 0.0,
        "v_spo2": 0, "v_height": 0.0, "v_weight": 0.0, "v_waist": 0.0,
        "v_notes": "",
    }.items():
        st.session_state[k] = v
    st.session_state["vitals_saving"] = False

def _ensure_blood_sugar_table():
    """Create blood_sugar_tests table (idempotent)."""
    if not get_connection:
        return
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS blood_sugar_tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fk_patient_id INTEGER NOT NULL,
            test_type TEXT NOT NULL,                 -- RBS/FBS/PPBS/HbA1c
            result_mg_dl REAL,                       -- mg/dL or % for HbA1c
            last_meal_time TEXT,
            history TEXT,
            symptoms TEXT,
            notes TEXT,
            sent_to_doctor INTEGER DEFAULT 0,        -- 0/1
            taken_at TEXT NOT NULL,
            recorded_by INTEGER,
            FOREIGN KEY (fk_patient_id) REFERENCES patients(id)
        )
    """)
    conn.commit(); conn.close()

def _ensure_messages_table():
    """Store chat messages between RMP and Doctor/Admin + alerts."""
    if not get_connection:
        return
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_role TEXT NOT NULL,   -- 'Health Agent', 'Doctor', 'Admin', 'System'
            recipient_role TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit(); conn.close()


def _ensure_tables():
    if not get_connection:
        return
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS patients(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, age INTEGER, gender TEXT, phone TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS vitals(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fk_patient_id INTEGER NOT NULL,
            recorded_at TEXT NOT NULL,
            bp_sys INTEGER, bp_dia INTEGER, pulse INTEGER, temperature REAL,
            resp_rate INTEGER, spo2 INTEGER, height_cm REAL, weight_kg REAL, bmi REAL,
            notes TEXT, recorded_by INTEGER,
            FOREIGN KEY (fk_patient_id) REFERENCES patients(id)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS lab_orders(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fk_patient_id INTEGER NOT NULL,
            ordered_at TEXT NOT NULL,
            test_name TEXT NOT NULL, priority TEXT, notes TEXT,
            ordered_by INTEGER, status TEXT DEFAULT 'Pending',
            FOREIGN KEY (fk_patient_id) REFERENCES patients(id)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS stock(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL UNIQUE,
            category TEXT, qty INTEGER DEFAULT 0, unit TEXT DEFAULT 'pcs',
            last_updated TEXT
        )
    """)
    cur.execute("""  
        CREATE TABLE IF NOT EXISTS medications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            drug_name TEXT NOT NULL,
            dose TEXT,
            frequency TEXT,
            duration TEXT,
            referral_facility TEXT,
            follow_up_days INTEGER,
            reason TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        );
    """)
    
    conn.commit()
    conn.close()
    _ensure_patient_columns()
    _ensure_vitals_columns()  
    _ensure_blood_sugar_table()   # <-- add this
    _ensure_stock_requests_table()  # <-- add this
    _ensure_medications_table()
    _ensure_doctor_advice_table()

def _ensure_rmp_users_table():
    if not get_connection: return
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS rmp_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            mobile TEXT,
            aadhar TEXT,
            address TEXT,
            photo_path TEXT,
            specialization TEXT,
            notes TEXT
        )
    """)
    conn.commit(); conn.close()

import sqlite3

def _get_patient_by_id(pid: int):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    row = cur.execute("SELECT * FROM patients WHERE id=?", (pid,)).fetchone()
    conn.close()
    return dict(row) if row else None


def _render_profile(user: dict):
    st.subheader("👤 My Profile")

    if not get_connection:
        st.error("Database not available.")
        return

    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT name, mobile, aadhar, address, photo_path, specialization, notes FROM rmp_users WHERE id=?", (user.get("id"),))
    row = cur.fetchone()
    conn.close()

    if not row:
        st.warning("Profile not found. Please contact Admin.")
        return

    name, mobile, aadhar, address, photo_path, specialization, notes = row

    # Layout
    col1, col2 = st.columns([2,1])
    with col1:
        st.markdown(f"**Name:** {name}")
        st.markdown(f"**Mobile:** {mobile or '-'}")
        st.markdown(f"**Aadhar:** {aadhar or '-'}")
        st.markdown(f"**Address:** {address or '-'}")
        st.markdown(f"**Specialization:** {specialization or '-'}")
        st.markdown(f"**Notes:** {notes or '-'}")

    with col2:
        st.markdown("**Photo**")
        if photo_path and Path(photo_path).exists():
            st.image(photo_path, width=180)
        else:
            st.info("📷 No photo available")


def _count_rows(table: str) -> int:
    if not get_connection:
        return 0
    conn = get_connection(); cur = conn.cursor()
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
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM vitals WHERE date(recorded_at) = date('now')")
    n = cur.fetchone()[0] or 0
    conn.close()
    return n


def _pending_tests_count() -> int:
    if not get_connection:
        return 0
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM lab_orders WHERE status != 'Completed'")
    n = cur.fetchone()[0] or 0
    conn.close()
    return n


def _low_stock_count(threshold: int = 5) -> int:
    if not get_connection:
        return 0
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM stock WHERE qty <= ?", (threshold,))
    n = cur.fetchone()[0] or 0
    conn.close()
    return n


def _load_patients():
    if not get_connection:
        return []
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT
            id, name, age, gender,
            COALESCE(mobile, phone) as mobile,
            aadhar, activity_level, village
        FROM patients
        ORDER BY id DESC
        LIMIT 200
    """)
    rows = cur.fetchall(); conn.close()
    return rows

def _load_patients_by_village(village: str):
    if not get_connection:
        return []
    conn = get_connection(); cur = conn.cursor()
    if not village or village.lower() == "all":
        cur.execute("""
            SELECT id, name, age, gender, COALESCE(mobile, phone) as mobile, aadhar, activity_level, village
            FROM patients ORDER BY id DESC LIMIT 200
        """)
    else:
        cur.execute("""
            SELECT id, name, age, gender, COALESCE(mobile, phone) as mobile, aadhar, activity_level, village
            FROM patients WHERE village = ? ORDER BY id DESC LIMIT 200
        """, (village,))
    rows = cur.fetchall(); conn.close()
    return rows


from typing import Optional

def _save_vitals(
    fk_patient_id,
    bp_sys, bp_dia, pulse,
    temperature_f, spo2, height_cm, weight_kg,
    waist_cm, bmi, notes, recorded_by,
    frequency_days=0   # NEW
):
    try:
        conn = get_connection(); cur = conn.cursor()
        cur.execute("""
            INSERT INTO vitals
              (fk_patient_id, bp_sys, bp_dia, pulse, temperature, spo2,
               height_cm, weight_kg, waist_cm, bmi, notes,
               recorded_at, recorded_by, frequency_days, sent_to_doctor)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, ?, 0)
        """, (
            fk_patient_id, bp_sys, bp_dia, pulse, temperature_f, spo2,
            height_cm, weight_kg, waist_cm, bmi, notes,
            recorded_by, int(frequency_days or 0)
        ))
        conn.commit(); conn.close()
        return True
    except Exception:
        return False


def _save_test_order(pid: int, test_name: str, priority: str, notes: str, ordered_by: Optional[int]):
    if not get_connection:
        return False
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        INSERT INTO lab_orders (fk_patient_id, ordered_at, test_name, priority, notes, ordered_by)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (pid, datetime.utcnow().isoformat(), test_name, priority, notes, ordered_by))
    conn.commit(); conn.close(); return True


def _list_villages():
    """Return distinct non-empty villages (sorted)."""
    if not get_connection:
        return []
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT village
        FROM patients
        WHERE village IS NOT NULL AND TRIM(village) <> ''
        ORDER BY village COLLATE NOCASE
    """)
    rows = [r[0] for r in cur.fetchall()]
    conn.close()
    return rows


def _upsert_stock(item_name: str, category: str, qty_delta: int, unit: str = "pcs"):
    if not get_connection:
        return False
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT id, qty FROM stock WHERE item_name=?", (item_name,))
    row = cur.fetchone()
    if row:
        new_qty = max(0, (row[1] or 0) + qty_delta)
        cur.execute("UPDATE stock SET qty=?, unit=?, category=?, last_updated=? WHERE id=?",
                    (new_qty, unit, category, datetime.utcnow().isoformat(), row[0]))
    else:
        cur.execute("INSERT INTO stock (item_name, category, qty, unit, last_updated) VALUES (?,?,?,?,?)",
                    (item_name, category, max(0, qty_delta), unit, datetime.utcnow().isoformat()))
    conn.commit(); conn.close(); return True


def _get_stock():
    if not get_connection:
        return []
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT id, item_name, category, qty, unit, last_updated FROM stock ORDER BY item_name")
    rows = cur.fetchall(); conn.close(); return rows


def _logo_path():
    for p in ("assets/Logo_upscaled.png", "static/Logo_upscaled.png", "Logo_upscaled.png"):
        if Path(p).exists():
            return p
    return None
    
from pathlib import Path
import streamlit as st

import streamlit as st

import streamlit as st

def _logo_paths():
    logos = []
    candidates = [
        # Mother Teresa logo
        ("assets/Mother-Teresa.png", "Mother Teresa Hospital"),
        ("static/Mother-Teresa.png", "Mother Teresa Hospital"),
        ("Mother-Teresa.png", "Mother Teresa Hospital"),
        ("Mother-Teresa.jpg", "Mother Teresa Hospital"),
        ("assets/Mother-Teresa.jpg", "Mother Teresa Hospital"),
        ("static/Mother-Teresa.jpg", "Mother Teresa Hospital"),

        # Hands logo
        ("assets/Hands.png", "Helping Hands"),
        ("static/Hands.png", "Helping Hands"),
        ("Hands.png", "Helping Hands"),
        ("Hands.jpg", "Helping Hands"),
        ("assets/Hands.jpg", "Helping Hands"),
        ("static/Hands.jpg", "Helping Hands"),

        # Kakatiya logo
        ("assets/kakatiya helping hands society logo.png", "Kakatiya Helping Hands"),
        ("static/kakatiya helping hands society logo.png", "Kakatiya Helping Hands"),
        ("kakatiya helping hands society logo.png", "Kakatiya Helping Hands"),
    ]
    for path, label in candidates:
        if Path(path).exists():
            logos.append((path, label))
    return logos


# =========================
# Namespaced CSS (no collisions)
# =========================
RMP_CSS = """
<style>
html, body, [data-testid="stAppViewContainer"] { background: #f4f8fb; }

/* Scope container so our styles don't leak */
.rmp-scope { color: #1e293b; }

/* Header + KPI chips */
.rmp-scope .rmp-chip {
  background: #ffffff; color: #1e293b;
  padding: 10px 14px; border-radius: 12px;
  border: 1px solid #e5e7eb;
  display: inline-flex; align-items: center; gap: .5rem; font-weight: 700;
}

/* Card (square-ish tile) */
.rmp-scope .rmp-card {
  background: #ffffff; color: #1e293b;
  border-radius: 16px; border: 1px solid #e5e7eb;
  box-shadow: 0 6px 14px rgba(2, 132, 199, .06);
  padding: 14px;
  height: 220px;
  display: flex; flex-direction: column; justify-content: space-between;
}

/* Title + number */
.rmp-scope .rmp-card h3{
  margin: 0; font-size: 1.05rem; font-weight: 800; display:flex; gap:.5rem; align-items:center;
}
.rmp-scope .rmp-card .metric{
  font-size: 2.2rem; font-weight: 800; line-height: 2.4rem; text-align:center;
}

/* Center the button and keep it compact */
.rmp-scope .rmp-card .stButton { display: flex; justify-content: center; }
.rmp-scope .rmp-card .stButton > button {
  min-width: 140px; border-radius: 10px !important;
  padding-top: 6px !important; padding-bottom: 6px !important;
}

/* Overview strip */
.rmp-scope .rmp-section {
  background: #ffffff; border: 1px solid #e5e7eb; border-radius: 14px; padding: 12px;
  box-shadow: 0 4px 10px rgba(15, 23, 42, .05);
}

/* Fixed bottom nav */
.rmp-bottom {
  position: fixed; left: 0; right: 0; bottom: 0; z-index: 1000;
  background: rgba(244,248,251,.92);
  backdrop-filter: blur(6px);
  border-top: 1px solid #e5e7eb;
  padding: 10px 10px 12px 10px;
}
.rmp-bottom .stButton > button {
  border-radius: 999px !important;
  padding-top: 6px !important; padding-bottom: 6px !important;
}
</style>
"""

def _apply_theme():
    st.markdown(RMP_CSS, unsafe_allow_html=True)


# =========================
# Cards + Bottom nav
# =========================
def _square_card(icon, title, value, btn_text, key, target=None):
    dest = _resolve_target(key, title, target)
    wid  = f"wrap_{key}"      # unique wrapper id per tile
    cid  = f"tile_{key}"      # id for the card itself
    H    = 180                # MUST match .rmp-card height in style.css

    # 1) Open a wrapper that contains BOTH the card and the button
    st.markdown(
        f"""
        <div id="{wid}" class="rmp-tile-wrap" style="position:relative; height:{H}px;">
          <div id="{cid}" class="rmp-card" style="position:relative; height:{H}px;">
            <h3 style="margin:0 0 .25rem 0;">{icon} {title}</h3>
            <div class="metric">{value}</div>
          </div>
        """,
        unsafe_allow_html=True,
    )

    # 2) Real Streamlit button (click handler)
    if st.button("open", key=f"overlay_{key}"):
        _go(dest); st.rerun()

    # 3) Close the wrapper and apply overlay CSS scoped to it
    st.markdown(
        f"""
          <style>
            /* Make the Streamlit button cover the entire wrapper */
            #{wid} > div[data-testid="stButton"] {{
              position: absolute;
              inset: 0;             /* top/right/bottom/left: 0 */
              margin: 0 !important;
              padding: 0 !important;
              z-index: 2;
            }}
            #{wid} > div[data-testid="stButton"] > button {{
              width: 100%;
              height: 100%;
              opacity: 0;           /* fully hide the 'open' label */
              border: none;
              background: transparent;
              cursor: pointer;
            }}
            /* Keep the visual card underneath */
            #{wid} > #{cid} {{ z-index: 1; }}
          </style>
        </div>  <!-- CLOSE #{wid} -->
        """,
        unsafe_allow_html=True,
    )

def _tile_button(icon: str, title: str, value: str, key: str, target: str | None = None):
    """
    A single big button styled as a card. Clicking anywhere on it navigates.
    """
    dest = _resolve_target(key, title, target)
    mid  = f"mark_{key}"   # local marker to scope CSS to THIS tile only

    # 1) A tiny marker so we can scope CSS to the NEXT st.button only
    st.markdown(f'<div id="{mid}"></div>', unsafe_allow_html=True)

    # 2) The actual Streamlit button (the whole tile)
    #    Newlines in the label are shown because we set white-space: pre-wrap via CSS below.
    label = f"{icon} {title}\n\n{value}" if value else f"{icon} {title}"
    if st.button(label, key=f"tile_{key}", use_container_width=True):
        _go(dest); st.rerun()

    # 3) Style JUST the button that immediately follows the marker.
    #    We don't rely on :has(); the adjacent sibling is the st.button wrapper Streamlit inserts.
    st.markdown(
        f"""
        <style>
          /* Style only the st.button wrapper that comes right after this marker */
          div#{mid} + div[data-testid="stButton"] > button {{
            height: 180px;                /* taller block */
            border-radius: 16px !important;
            border: 1px solid #e5e7eb;
            box-shadow: 0 6px 14px rgba(2,132,199,.06);
            background: #ffffff;
            color: #1e293b;
            text-align: center;
            font-weight: 600;
            white-space: pre-wrap;        /* allow two-line text */
            line-height: 1.3;
            padding: 14px;
            font-size: 1.1rem;
          }}
          /* Hover feel like your old .rmp-card */
          div#{mid} + div[data-testid="stButton"] > button:hover {{
            box-shadow: 0 8px 18px rgba(2,132,199,.10);
            transform: translateY(-2px);
          }}
          /*make metric bigger */
          div#{mid} + div[data-testid="stButton"] > button .metric {{
              display: block;
              font-size: 2rem;
              font-weight: 800;
              margin-top: .5rem;
          }}

        </style>
        """,
        unsafe_allow_html=True,
    )


def _bottom_nav():
    """Fixed bottom navigation visible on every RMP screen."""
    cur = st.session_state.get("rmp_section", "Dashboard")
    st.markdown('<div class="rmp-bottom rmp-scope">', unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        if st.button("🏠 Home", key="nav_home", use_container_width=True,
                     type=("primary" if cur == "Dashboard" else "secondary")):
            st.session_state["rmp_section"] = "Dashboard"; st.rerun()

    with c2:
        if st.button("💬 Messages", key="nav_msgs", use_container_width=True,
                     type=("primary" if cur == "Messages" else "secondary")):
            st.session_state["rmp_section"] = "Messages"; st.rerun()

    # with c3:
        # if st.button("📑 Reports", key="nav_reports", use_container_width=True,
                     # type=("primary" if cur == "Reports" else "secondary")):
            # st.session_state["rmp_section"] = "Reports"; st.rerun()

    with c3:
        if st.button("📘 SOPs", key="nav_sops", use_container_width=True,
                     type=("primary" if cur == "SOPs" else "secondary")):
            st.session_state["rmp_section"] = "SOPs"; st.rerun()

    with c4:
        if st.button("💊 Pharmacy", key="nav_pharmacy", use_container_width=True,
                     type=("primary" if cur == "Pharmacy" else "secondary")):
            st.session_state["rmp_section"] = "Pharmacy"; st.rerun()

    with c5:
        if st.button("⚙️ Settings", key="nav_settings", use_container_width=True,
                     type=("primary" if cur == "Settings" else "secondary")):
            st.session_state["rmp_section"] = "Settings"; st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    # spacer so bar doesn't cover content
    st.markdown("<div style='height:72px'></div>", unsafe_allow_html=True)


# =========================
# RMP Dashboard (entry)
# =========================

def render_health_agent_dashboard(user):
    from pathlib import Path
    
    # Small JS fallback to reapply a 2-column grid and reduce child min-widths.
    import streamlit.components.v1 as components
    components.html("""
    <script>
    (function(){
      var enforce = function(){
        var g = document.querySelector('.dashboard-grid') || document.querySelector('[data-testid^="stHorizontalBlock"]');
        if (!g) return;
        if (window.innerWidth >= 300) {
          g.style.gridTemplateColumns = 'repeat(2, 1fr)';
        } else {
          g.style.gridTemplateColumns = '1fr';
        }
        g.querySelectorAll('*').forEach(function(c){
          try { c.style.minWidth='0'; c.style.maxWidth='100%'; c.style.boxSizing='border-box'; } catch(e){}
        });
        console.log('DEBUG: grid fix applied, w=' + window.innerWidth + ', dpr=' + window.devicePixelRatio);
      };
      setTimeout(enforce, 500);
      window.addEventListener('resize', enforce);
    })();
    </script>
    """, height=1)


    def _find_logo_file():
        candidates = [
            "static/images/Logo_upscaled.png",
            "static/Logo_upscaled.png",
            "assets/Logo_upscaled.png",
            "Logo_upscaled.png",
            "/mnt/data/Logo_upscaled.png",
        ]
        for p in candidates:
            if Path(p).exists():
                return p
        return None

    found_logo = _find_logo_file()

    # Layout: 3 equal columns so everything is centered properly
    col1, col2, col3 = st.columns([1, 2, 1])

    # --- Welcome text ---
    with col1:
        st.markdown(
            f"""
            <div class="rmp-card header-card" style="height:100%; display:flex; flex-direction:column; justify-content:center;">
                <h2 class="header-title">Welcome, {user.get('name','rmp')}</h2>
                <p class="header-date">{date.today().strftime("%b %d, %Y")}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --- Center logo ---
    with col2:
        if found_logo and Path(found_logo).exists():
            st.image(found_logo, use_container_width=True, width=180)
        else:
            st.info("Logo not found")
            
            

    # --- Logout button, vertically centered ---
    with col3:
        st.markdown("<div style='height:100%; display:flex; align-items:center; justify-content:center;'>", unsafe_allow_html=True)
        if st.button("Logout", key="logout_btn", use_container_width=True):
            keep = {"theme"} 
            for k in list(st.session_state.keys()):
                if k not in keep:
                    del st.session_state[k]
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    # ---- DASHBOARD GRID ----
    st.markdown('<div class="dashboard-grid">', unsafe_allow_html=True)

    # --- TOP KPI ROW (side-by-side using columns) ---
    # simple Streamlit 2x2 layout (no CSS)
    cols = st.columns(2)
    with cols[0]:
        st.markdown("### Patients")
        st.markdown("4")
    with cols[1]:
        st.markdown("### Record Vitals")
        st.markdown("2931")
    
    # next row
    cols = st.columns(2)
    with cols[0]:
        st.markdown("### Sugar Blood Test")
        st.markdown("2931")
    with cols[1]:
        st.markdown("### Inventory / Stock")
        st.markdown("0")

    st.markdown('</div>', unsafe_allow_html=True)  
    st.write("")

    if "rmp_section" not in st.session_state:
        st.session_state["rmp_section"] = "Dashboard"
    if "patients_sub" not in st.session_state:
        st.session_state["patients_sub"] = "Menu"

    section = st.session_state["rmp_section"]
    
    # Compatibility: if someone set section to "Patients_New"/"Patients_Search", convert to sub-state
    if isinstance(section, str) and section.startswith("Patients_"):
        _set_substate("Patients", section)
        st.rerun()
    
    # ---- compatibility: Stock_* -> (section='Stock', stock_sub='...') ----
    if isinstance(section, str) and section.startswith("Stock_"):
        _set_substate("Stock", section)
        st.rerun()

    _route_from_query()

    # ---------- Dashboard: 2×2 tiles ----------
    if section == "Dashboard":
        # ---------- Dashboard tiles (2 x 2) ----------
        r1c1, r1c2 = st.columns(2)
        with r1c1:
            _tile_button("👥", "Patients", str(_count_rows("patients")), "dash_patients", target="Patients")
        with r1c2:
            _tile_button("🩺", "Record Vitals", str(_count_rows("vitals")), "dash_vitals", target="Record Vitals")

        r2c1, r2c2 = st.columns(2)
        with r2c1:
            _tile_button("🧪", "Sugar Blood Test", str(_count_rows("blood_sugar_tests")), "dash_sugar", target="Sugar Blood Test")
        with r2c2:
            total_stock = 0
            if get_connection:
                rows = _get_stock()
                total_stock = sum([(r[3] or 0) for r in rows])
            _tile_button("📦", "Inventory / Stock", str(total_stock), "dash_stock", target="Stock")

        r3c1, r3c2 = st.columns(2)
        with r3c1:
            _tile_button("📊", "Health Profiles", "","dash_profiles", target="Health Profiles")
        with r3c2:
            _tile_button("📑", "Reports", "", "dash_reports", target="Reports")

        _bottom_nav()
        st.markdown('</div>', unsafe_allow_html=True)
        return

        # always show bottom nav on front page
        _bottom_nav()

        st.markdown('</div>', unsafe_allow_html=True)  # close rmp-scope
        return

    # ---------- Detail pages ----------
    if st.button("← Back to dashboard", key="back_to_dash"):
        st.session_state["rmp_section"] = "Dashboard"; st.rerun()

    if section == "Patients":
        st.subheader("Patients")
        #sub = st.session_state.get("patients_sub", "Menu")
        sub = _current_sub("Patients", default="New")

        # Patients Menu (cards)
        if sub == "Menu":
            c1, c2 = st.columns(2)
            with c1:
                _sub_card("➕", "New", "btn_patients_new", section="Patients", sub="Patients_New")
            with c2:
                _sub_card("🔍", "Search", "btn_patients_search", section="Patients", sub="Patients_Search")

            # New Patient Profiles card
            # c3, _ = st.columns(2)
            # with c3:
                # _square_card("🧑‍⚕️ Profiles", "📋", "", "btn_patients_profiles", "Patients_Profiles")



        elif sub == "Patients_New":
            if st.button("← Back to Patients", key="back_patients_new"):
                st.session_state["patients_sub"] = "Menu"; st.rerun()
            st.subheader("➕ New Patient")

            # --- Form ---
            with st.form("new_patient_form"):
                # Basic identity
                name = st.text_input("Full name *")
                father_name = st.text_input("Father name")
                col1, col2, col3 = st.columns(3)
                with col1:
                    age = st.number_input("Age", min_value=0, max_value=120, step=1)
                with col2:
                    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
                with col3:
                    mobile = st.text_input("Mob no")

                aadhar = st.text_input("Aadhar no")
                address = st.text_area("Address", height=70)
                village = st.text_input("Village")  # <-- add this

                # Camera-only capture
                photo = st.camera_input("📸 Capture Photo", key="patient_cam")

                # Lifestyle & diet
                st.markdown("**Diet & Lifestyle**")
                diet = st.selectbox("Diet", ["Vegetarian", "Non-vegetarian", "Vegan", "Other"])
                cB, cL, cD = st.columns(3)
                with cB:
                    breakfast = st.text_input("Breakfast", placeholder="e.g., Idli + sambar")
                with cL:
                    lunch = st.text_input("Lunch", placeholder="e.g., Rice + dal + veggies")
                with cD:
                    dinner = st.text_input("Dinner", placeholder="e.g., Chapati + curry")

                cT, cA, cAct = st.columns(3)
                with cT:
                    tobacco = st.selectbox("Tobacco", ["No", "Yes"])
                with cA:
                    alcohol = st.selectbox("Alcohol", ["No", "Yes"])
                with cAct:
                    activity_level = st.selectbox(
                        "Activity level",
                        ["Sedentary", "Lightly active", "Moderately active", "Very active"]
                    )

                family_history = st.text_area("Family history", placeholder="e.g., Diabetes (father), Hypertension (mother)")

                submitted = st.form_submit_button("💾 Save Patient")
                if submitted:
                    if not name.strip():
                        st.warning("Full name is required.")
                    elif not get_connection:
                        st.error("DB not available.")
                    else:
                        # Save photo if provided (robust filename)
                        photo_path = None
                        if photo is not None:
                            import os, time, secrets
                            folder = "uploads/patient_photos"
                            os.makedirs(folder, exist_ok=True)
                            filename = f"{int(time.time())}_{secrets.token_hex(4)}.jpg"
                            fullpath = os.path.join(folder, filename)
                            with open(fullpath, "wb") as f:
                                f.write(photo.getbuffer())
                            photo_path = fullpath  # store relative path if preferred

                        # Insert record
                        conn = get_connection(); cur = conn.cursor()
                        cur.execute("""
                            INSERT INTO patients
                            (name, father_name, age, gender, phone, mobile, aadhar, address, village, photo_path,
                             diet, breakfast, lunch, dinner, tobacco, alcohol, activity_level, family_history)
                            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                        """, (
                            name.strip(), father_name.strip(), age, gender,
                            mobile.strip(), mobile.strip(), aadhar.strip(), address.strip(), village.strip(), photo_path,
                            diet, breakfast.strip(), lunch.strip(), dinner.strip(),
                            tobacco, alcohol, activity_level, family_history.strip()
                        ))
                        conn.commit(); conn.close()
                        st.success(f"Patient '{name}' added.")
        
        # Patients Search 
        elif sub == "Patients_Search":
            if st.button("← Back to Patients", key="back_patients_search"):
                st.session_state["patients_sub"] = "Menu"; st.rerun()

            st.subheader("🔍 Search Patients")

            # ---- Load patients
            rows = _load_patients()  # must return: [id, name, age, gender, mobile, aadhar, activity_level, village]
            if not rows:
                st.info("No patients found."); st.stop()

            # ---------------- Village list (FIX) ----------------
            # Build from the village column (index 7), not activity
            villages = sorted({(r[7] or "").strip() for r in rows if r[7]})
            q = st.text_input("Search by name/mobile/aadhar", "")
            village_filter = st.selectbox("Village", ["All"] + villages, index=0)

            # ---- Fetch latest vitals + latest sugar per patient in one go
            # We grab them per-patient via scalar subqueries (SQLite-friendly).
            conn = get_connection(); cur = conn.cursor()
            cur.execute("""
                SELECT
                    p.id, p.name, p.age, p.gender, p.mobile, p.aadhar,
                    p.activity_level, p.village,

                    -- Latest vitals
                    (SELECT v.bp_sys FROM vitals v
                       WHERE v.fk_patient_id = p.id
                       ORDER BY v.recorded_at DESC, v.id DESC LIMIT 1)        AS bp_sys,
                    (SELECT v.bp_dia FROM vitals v
                       WHERE v.fk_patient_id = p.id
                       ORDER BY v.recorded_at DESC, v.id DESC LIMIT 1)        AS bp_dia,
                    (SELECT v.pulse FROM vitals v
                       WHERE v.fk_patient_id = p.id
                       ORDER BY v.recorded_at DESC, v.id DESC LIMIT 1)        AS pulse,

                    -- Latest sugar
                    (SELECT t.result_mg_dl FROM blood_sugar_tests t
                       WHERE t.fk_patient_id = p.id
                       ORDER BY t.taken_at DESC, t.id DESC LIMIT 1)           AS sugar,
                    (SELECT t.test_type FROM blood_sugar_tests t
                       WHERE t.fk_patient_id = p.id
                       ORDER BY t.taken_at DESC, t.id DESC LIMIT 1)           AS sugar_type
                FROM patients p
                ORDER BY p.name COLLATE NOCASE
            """)
            enriched = cur.fetchall()
            conn.close()

            # ---- To DataFrame
            import pandas as pd
            df = pd.DataFrame(
                enriched,
                columns=[
                    "ID","Name","Age","Gender","Mobile","Aadhar","Activity","Village",
                    "BP Sys","BP Dia","Pulse","Sugar","Sugar Type"
                ]
            )

            # ---------------- Risk computation (same thresholds as Health Profiles) ----------------
            def compute_risk(bp_sys, bp_dia, pulse, sugar):
                try:
                    bs = float(bp_sys) if bp_sys is not None else None
                    bd = float(bp_dia) if bp_dia is not None else None
                    pu = float(pulse)  if pulse  is not None else None
                    sg = float(sugar)  if sugar  is not None else None
                except Exception:
                    bs = bd = pu = sg = None

                # Red: BP Sys >160 OR BP Dia >100 OR Pulse >120 OR Sugar(FBS proxy) >140
                if (bs and bs > 160) or (bd and bd > 100) or (pu and pu > 120) or (sg and sg > 140):
                    return "Red"
                # Amber: Sys 140–160 OR Dia 90–100 OR Pulse 100–120 OR Sugar 110–140
                if ((bs and 140 <= bs <= 160) or (bd and 90 <= bd <= 100) or
                    (pu and 100 <= pu <= 120) or (sg and 110 <= sg <= 140)):
                    return "Amber"
                # Else Green
                return "Green"

            df["Risk"] = df.apply(lambda r: compute_risk(r["BP Sys"], r["BP Dia"], r["Pulse"], r["Sugar"]), axis=1)

            # Optional: pretty badge look
            def risk_badge(val):
                if val == "Red":    return "🔴 Red"
                if val == "Amber":  return "🟠 Amber"
                return "🟢 Green"
            df["Risk"] = df["Risk"].map(risk_badge)

            # ---------------- Apply search/village filters ----------------
            if q:
                ql = q.lower()
                df = df[df.apply(lambda r: ql in str(r.values).lower(), axis=1)]
            if village_filter != "All":
                df = df[df["Village"].fillna("").str.strip() == village_filter]

            # ---- Show table with Risk column
            st.dataframe(
                df[["ID","Name","Age","Gender","Mobile","Aadhar","Activity","Village",
                    "BP Sys","BP Dia","Pulse","Sugar","Sugar Type","Risk"]],
                use_container_width=True, hide_index=True
            )

            # ---- Quick “open profile” picker below the table
            ids = df["ID"].tolist()
            if ids:
                selected_pid = st.selectbox("Select a patient to view full profile", ids, format_func=lambda x: f"#{x}")
                # load a single row safely
                conn = get_connection(); cur = conn.cursor()
                cur.execute("SELECT * FROM patients WHERE id=?", (selected_pid,))
                row = cur.fetchone(); conn.close()

                if row:
                    st.markdown("### 🧾 Full Profile")
                    st.write(f"**Name:** {row['name']}")
                    st.write(f"**Father Name:** {row['father_name']}")
                    st.write(f"**Age / Gender:** {row['age']} / {row['gender']}")
                    st.write(f"**Mobile:** {row['mobile']}")
                    st.write(f"**Aadhar:** {row['aadhar']}")
                    st.write(f"**Address:** {row['address']}")
                    st.write(f"**Diet:** {row['diet']}  🍽️")
                    st.write(f"**Breakfast:** {row['breakfast']}")
                    st.write(f"**Lunch:** {row['lunch']}")
                    st.write(f"**Dinner:** {row['dinner']}")
                    st.write(f"**Tobacco:** {row['tobacco']} / **Alcohol:** {row['alcohol']}")
                    st.write(f"**Activity level:** {row['activity_level']}")
                    st.write(f"**Family history:** {row['family_history']}")
                    if row["photo_path"]:
                        try:
                            st.image(row["photo_path"], width=200, caption="Patient Photo")
                        except Exception:
                            pass

        
        elif sub == "Patients_Profiles":
            if st.button("← Back to Patients", key="back_patients_profiles"):
                st.session_state["patients_sub"] = "Menu"; st.rerun()
            render_patient_profiles()

    elif section == "Record Vitals":
        st.subheader("Record Vitals")
        _ensure_followup_columns()  # makes sure frequency_days & sent_to_doctor exist

        # ---- ensure state keys exist with sensible defaults ----
        defaults = {
            "v_bp_sys": 0, "v_bp_dia": 0, "v_pulse": 0,
            "v_temp": 98.6,      # Fahrenheit default
            "v_spo2": 98,
            "v_height": 0.0, "v_weight": 0.0, "v_waist": 0.0,
            "v_notes": "", "vitals_saving": False,
            "v_followup_days": 0,   # NEW: default frequency
        }
        for k, v in defaults.items():
            if k not in st.session_state:
                st.session_state[k] = v

        # ---- Step 1: Village filter ----
        villages = _list_villages()
        v_col1, v_col2 = st.columns([2, 1])
        with v_col1:
            village_choice = st.selectbox("Village (filter patients)", ["All"] + villages, index=0)
        with v_col2:
            st.caption(f"Villages: {len(villages)}")

        # ---- Step 2: Patient ----
        all_rows = _load_patients()
        rows = (
            [r for r in all_rows if str(r[7] or "").strip().casefold() == village_choice.strip().casefold()]
            if village_choice != "All" else all_rows
        )
        if not rows:
            st.info("No patients found.")
            _bottom_nav()
            st.stop()

        pid_map = {f"#{r[0]} · {r[1]} ({r[3] or ''}) — {r[7] or '—'}": r[0] for r in rows}
        pid_label = st.selectbox("Patient", list(pid_map.keys()))
        fk_patient_id = pid_map[pid_label]

        # ---- Inputs ----
        c1, c2, c3 = st.columns(3)

        with c1:
            bp_sys = st.number_input("BP Systolic (mmHg)", 0, 300, int(st.session_state["v_bp_sys"]), 1)
            st.session_state["v_bp_sys"] = bp_sys

            pulse = st.number_input("Pulse (bpm)", 0, 250, int(st.session_state["v_pulse"]), 1)
            st.session_state["v_pulse"] = pulse

            height_cm = st.number_input("Height (cm)", 0.0, 300.0, float(st.session_state["v_height"]), 0.1)
            st.session_state["v_height"] = height_cm

        with c2:
            bp_dia = st.number_input("BP Diastolic (mmHg)", 0, 200, int(st.session_state["v_bp_dia"]), 1)
            st.session_state["v_bp_dia"] = bp_dia

            # ✅ Convert old Celsius values if still present in session
            temp_default = st.session_state.get("v_temp", 98.6)
            try:
                temp_val = float(temp_default)
                if temp_val < 80:  # looks like Celsius, convert
                    temp_val = (temp_val * 9/5) + 32
            except Exception:
                temp_val = 98.6

            temp_f = st.number_input("Temperature (°F)", 77.0, 113.0, float(temp_val), 0.1)
            st.session_state["v_temp"] = temp_f

            weight_kg = st.number_input("Weight (kg)", 0.0, 400.0, float(st.session_state["v_weight"]), 0.1)
            st.session_state["v_weight"] = weight_kg

        with c3:
            spo2 = st.number_input("SpO₂ (%)", 0, 100, int(st.session_state["v_spo2"]), 1)
            st.session_state["v_spo2"] = spo2

            bmi_val = None
            if height_cm and weight_kg and height_cm > 0:
                m = height_cm / 100.0
                bmi_val = round(weight_kg / (m * m), 2)
            st.number_input("BMI", value=0.0 if bmi_val is None else float(bmi_val),
                            format="%.2f", disabled=True)

            waist_cm = st.number_input("Waist (cm)", 0.0, 300.0, float(st.session_state["v_waist"]), 0.1)
            st.session_state["v_waist"] = waist_cm

        st.session_state["v_notes"] = st.text_area("Notes", value=st.session_state.get("v_notes", ""))

        # NEW: Follow-up frequency
        st.session_state["v_followup_days"] = st.number_input(
            "Follow-up in (days)", min_value=0, max_value=365, step=1,
            value=int(st.session_state.get("v_followup_days", 0))
        )
        
        # ---- Validation: ensure not all values are zero ----
        all_zero = (
            int(bp_sys) == 0 and
            int(bp_dia) == 0 and
            int(pulse) == 0 and
            float(temp_f) == 98.6 and   # default normal temp
            int(spo2) == 0 and
            float(height_cm) == 0.0 and
            float(weight_kg) == 0.0 and
            float(waist_cm) == 0.0
        )

        save_disabled = all_zero


        # ---- Save ----
        if st.button("💾 Save Vitals", type="primary", disabled=save_disabled):
            ok = _save_vitals(
                fk_patient_id,
                int(bp_sys), int(bp_dia), int(pulse),
                float(temp_f), int(spo2), float(height_cm), float(weight_kg),
                float(waist_cm), float(bmi_val) if bmi_val else None,
                st.session_state["v_notes"].strip(),
                user.get("id"),
                frequency_days=int(st.session_state.get("v_followup_days", 0))
            )
            if ok:
                st.success("Vitals saved.")
                st.session_state.update(defaults)
                st.rerun()
            else:
                st.error("Could not save vitals.")


        # ---- Recent Vitals (with Send to Doctor) ----
        st.markdown("### Recent Vitals")

        # Check whether 'sent_to_doctor' exists; show a hint if not
        def _vitals_has_sent_flag() -> bool:
            try:
                conn = get_connection(); cur = conn.cursor()
                cur.execute("PRAGMA table_info('vitals');")
                cols = [r[1] for r in cur.fetchall()]   # r[1] is column name
                conn.close()
                return "sent_to_doctor" in {c.lower() for c in cols}
            except Exception:
                return False

        has_sent_flag = _vitals_has_sent_flag()

        show_unsent_only = st.toggle(
            "Show only unsent",
            value=True,
            key="vitals_show_unsent",
            help="Show only vitals that have not been sent to doctor yet."
        )

        # Build SELECT – includes frequency_days (for Next record)
        select_cols = """
            v.id, p.name, v.bp_sys, v.bp_dia, v.pulse, v.temperature,
            v.spo2, v.height_cm, v.weight_kg, v.waist_cm, v.bmi,
            v.notes, v.recorded_at, v.frequency_days
        """
        if has_sent_flag:
            select_cols = select_cols + ", v.sent_to_doctor"

        base_sql = f"""
            SELECT {select_cols}
            FROM vitals v
            JOIN patients p ON p.id = v.fk_patient_id
        """

        where_clause = ""
        if has_sent_flag and show_unsent_only:
            where_clause = " WHERE v.sent_to_doctor = 0 "

        sql = base_sql + where_clause + " ORDER BY v.id DESC LIMIT 100"

        conn = get_connection(); cur = conn.cursor()
        try:
            cur.execute(sql)
            vitals_rows = cur.fetchall()
        finally:
            conn.close()

        if vitals_rows:
            import pandas as pd
            from datetime import timedelta

            # Columns list depends on whether we have sent flag
            base_cols = [
                "ID", "Patient", "BP Sys", "BP Dia", "Pulse", "Temp (°F)",
                "SpO₂", "Height (cm)", "Weight (kg)", "Waist (cm)", "BMI",
                "Notes", "Recorded At", "frequency_days"
            ]
            cols = base_cols + (["Sent to Dr"] if has_sent_flag else [])

            df_vitals = pd.DataFrame(vitals_rows, columns=cols)

            # Format datetime
            def _format_dt(val):
                if not val:
                    return None
                try:
                    s = str(val).strip()
                    if len(s) == 10:  # YYYY-MM-DD
                        return pd.to_datetime(s, format="%Y-%m-%d").strftime("%d %B %Y, %I:%M %p")
                    return pd.to_datetime(s, errors="coerce").strftime("%d %B %Y, %I:%M %p")
                except Exception:
                    return None

            # Compute Next record (Recorded At + frequency_days)
            def _next_due(rec_at, days):
                """Recorded_at + days; returns '' if any piece invalid."""
                import pandas as pd
                from datetime import timedelta
                # parse date
                d = pd.to_datetime(str(rec_at), errors="coerce")
                if pd.isna(d):
                    return ""
                n = _coerce_pos_int(days)
                if n is None:
                    return ""
                return (d + timedelta(days=n)).strftime("%d %B %Y")

            df_vitals["Recorded At (raw)"] = df_vitals["Recorded At"]
            df_vitals["Recorded At"] = df_vitals["Recorded At"].apply(_format_dt)
            df_vitals["Next record"] = df_vitals.apply(
                lambda r: _next_due(r["Recorded At (raw)"], r["frequency_days"]), axis=1
            )

            # Build the view table with Next record just after Recorded At, before Sent to Dr
            view_cols = [
                "ID", "Patient", "BP Sys", "BP Dia", "Pulse", "Temp (°F)", "SpO₂",
                "Height (cm)", "Weight (kg)", "Waist (cm)", "BMI",
                "Notes", "Recorded At", "Next record"
            ] + (["Sent to Dr"] if has_sent_flag else [])
            df_view = df_vitals[view_cols].copy()

            # Add a selectable column
            df_view.insert(0, "Select", False)

            # Configure disabled columns (everything except the Select)
            disabled_cols = [c for c in df_view.columns if c != "Select"]

            if not has_sent_flag:
                st.info(
                    "To enable 'Send to doctor' for vitals, add "
                    "`sent_to_doctor INTEGER DEFAULT 0` to the `vitals` table. "
                    "Migration runs via _ensure_followup_columns()."
                )

            edited = st.data_editor(
                df_view,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Select": st.column_config.CheckboxColumn("Select"),
                    **({"Sent to Dr": st.column_config.CheckboxColumn("Sent to Dr", disabled=True)}
                       if has_sent_flag else {})
                },
                disabled=disabled_cols,
                key="recent_vitals_editor",
            )

            if has_sent_flag:
                # Determine selected rows that are eligible to send (not already sent)
                selected_df = edited[edited["Select"] == True]
                eligible_ids = selected_df.loc[
                    selected_df.get("Sent to Dr", False) != True, "ID"
                ].astype(int).tolist()
                already_sent_ids = selected_df.loc[
                    selected_df.get("Sent to Dr", False) == True, "ID"
                ].astype(int).tolist()

                # Right aligned action button
                spacer, right = st.columns([6, 1])
                with right:
                    disabled_btn = (len(eligible_ids) == 0)
                    if st.button("📨 Send to doctor", key="btn_vitals_send_bulk", disabled=disabled_btn):
                        placeholders = ",".join(["?"] * len(eligible_ids))
                        try:
                            conn = get_connection(); cur = conn.cursor()
                            cur.execute(
                                f"UPDATE vitals SET sent_to_doctor = 1 WHERE id IN ({placeholders})",
                                eligible_ids
                            )
                            conn.commit(); conn.close()
                            st.success(f"Sent {len(eligible_ids)} record(s) to doctor.")
                            if already_sent_ids:
                                st.info(f"Ignored already-sent ID(s): {', '.join(map(str, already_sent_ids))}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to send: {e}")

                if already_sent_ids and len(eligible_ids) == 0:
                    st.caption("Some selected rows are already sent; they can’t be sent again.")
        else:
            st.info("No vitals recorded yet.")

    
    
    elif section == "Sugar Blood Test":
        st.subheader("Sugar Blood Test")
        _ensure_followup_columns()

        # --- init state (so disabled buttons work on first render) ---
        ss_defaults = {
            "s_village": "All",
            "s_test_type": "RBS",
            "s_result": 0.0,
            "s_last_meal": "",
            "s_history": "",
            "s_symptoms": "",
            "s_notes": "",
            "s_saving": False,
            "s_saving_ts": None,   # << added: timestamp when saving started (epoch seconds)
        }
        for k, v in ss_defaults.items():
            if k not in st.session_state:
                st.session_state[k] = v

        # --- reference image on top (your sketch) ---
        try:
            st.image("WhatsApp Image 2025-08-29 at 12.37.23 PM.jpeg", use_container_width=True)
        except Exception:
            pass

        # --- Village filter, then patient select ---
        villages = _list_villages()
        v1, v2 = st.columns([2, 1])
        with v1:
            st.session_state["s_village"] = st.selectbox(
                "Village (filter patients)", ["All"] + villages,
                index=(["All"] + villages).index(st.session_state.get("s_village","All"))
            )
        with v2:
            st.write(""); st.caption(f"Villages: {len(villages)}")

        all_rows = _load_patients()  # includes village at index 7
        if st.session_state["s_village"] != "All":
            rows = [r for r in all_rows if str(r[7] or "").strip().casefold()
                    == st.session_state["s_village"].strip().casefold()]
        else:
            rows = all_rows

        if not rows:
            st.info("No patients for the selected village.")
            _bottom_nav(); st.markdown("</div>", unsafe_allow_html=True); st.stop()

        pid_map = {f"#{r[0]} · {r[1]} ({r[3] or ''}) — {r[7] or '—'}": r[0] for r in rows}
        patient_label = st.selectbox("Patient", list(pid_map.keys()))
        fk_patient_id = pid_map[patient_label]

        # # --- safe defaults for result and follow-up (do this before widgets) ---
        # if "s_result" not in st.session_state:
            # st.session_state["s_result"] = 0.0
            
        # # create widget bound to st.session_state["s_result"] (no value= argument)
        # st.number_input(
            # "Result (mg/dL) or % for HbA1c",
            # min_value=0.0, max_value=1000.0, step=0.1,
            # key="s_result"   # <- do NOT pass value= when using key= and session_state
        # )
        
        # --- ensure defaults BEFORE creating widgets ---
        if "s_result_num" not in st.session_state:
            st.session_state["s_result_num"] = 0.0
        if "s_followup_days" not in st.session_state:
            st.session_state["s_followup_days"] = 0

        # --- Form fields (left/right columns) ---
        cA, cB = st.columns(2)
        with cA:
            st.session_state["s_test_type"] = st.selectbox(
                "Test Type *", ["RBS", "FBS", "PPBS", "HbA1c"],
                index=["RBS","FBS","PPBS","HbA1c"].index(st.session_state.get("s_test_type","RBS"))
            )

            # Create the number_input and bind it to s_result key directly (do NOT assign its return)
            st.number_input(
                "Result (mg/dL) or % for HbA1c",
                min_value=0.0, max_value=1000.0, step=0.1,                
                key="s_result"   # <-- use the same key you read later
            )

            st.session_state["s_last_meal"] = st.text_input(
                "Last meal time *",
                value=st.session_state.get("s_last_meal",""),
                placeholder="e.g., 2 hours ago, 07:30 AM",
                key="s_last_meal_txt"
            )
        with cB:
            st.session_state["s_history"] = st.text_area(
                "Any history", height=90, value=st.session_state.get("s_history",""),
                placeholder="Known diabetes, on medication, etc.", key="s_hist_txt"
            )
            st.session_state["s_symptoms"] = st.text_area(
                "Any other symptoms", height=90, value=st.session_state.get("s_symptoms",""),
                placeholder="Polyuria, polydipsia, weight loss, etc.", key="s_symp_txt"
            )

        st.session_state["s_notes"] = st.text_area(
            "Notes", value=st.session_state.get("s_notes",""),
            placeholder="Anything else to add…", key="s_notes_txt"
        )

        # --- follow-up days input (safe pattern) ---
        st.number_input(
            "Follow-up in (days)",
            min_value=0, max_value=3650, step=1,            
            key="s_followup_days"
        )

        # --- validation: Save enabled only when required are present and result > 0 ---
        # read result from the widget-key (s_result)
        result_val = 0.0
        try:
            result_val = float(st.session_state.get("s_result") or 0.0)
        except Exception:
            result_val = 0.0

        required_ok = all([
            fk_patient_id is not None,
            bool(st.session_state["s_test_type"]),
            bool(st.session_state["s_last_meal"].strip()),
        ])
        
        # st.write("DEBUG:", {
            # "required_ok": required_ok,
            # "result_val": result_val,
            # "s_saving": st.session_state.get("s_saving"),
            # "s_result_in_state": st.session_state.get("s_result"),
            # "s_followup_days": st.session_state.get("s_followup_days"),
        # })
        
        # --- defensive: clear 'saving' flag if it's stale (left true by a previous crash) ---
        import time
        MAX_SAVE_SECONDS = 30   # adjust as you like (30s is reasonable)
        if st.session_state.get("s_saving", False):
            ts = st.session_state.get("s_saving_ts")
            if not ts:
                # if we have True but no timestamp, clear (unexpected state)
                st.session_state["s_saving"] = False
            else:
                try:
                    if time.time() - float(ts) > MAX_SAVE_SECONDS:
                        # stale: clear it so UI is usable again
                        st.session_state["s_saving"] = False
                        st.session_state["s_saving_ts"] = None
                except Exception:
                    # if timestamp parse fails, clear both
                    st.session_state["s_saving"] = False
                    st.session_state["s_saving_ts"] = None


        save_disabled = (not required_ok) or (result_val <= 0.0) or st.session_state.get("s_saving", False)

        if not save_disabled and result_val <= 0:
            st.caption("Enter a valid test result (> 0).")

        
        # Optional gentle hint
        if not save_disabled and result_val <= 0:
            st.caption("Enter a valid test result (> 0).")
        
        
        # --- Save button near the form (single test) ---
        if st.button("💾 Save", key="btn_sugar_save", type="primary", disabled=save_disabled):
            st.session_state["s_saving"] = True
            st.session_state["s_saving_ts"] = time.time()
            try:
                ok = _save_blood_sugar(
                    fk_patient_id,
                    st.session_state["s_test_type"],
                    result_val,  # already validated > 0
                    st.session_state["s_last_meal"].strip(),
                    st.session_state["s_history"],
                    st.session_state["s_symptoms"],
                    st.session_state["s_notes"],              
                    sent_to_doctor=0,
                    recorded_by=user.get("id"),
                    frequency_days=int(st.session_state.get("s_followup_days", 0))
                )
                if ok:
                    st.success("Saved.")
                    # reset form and disable again
                    st.session_state.update({
                        "s_test_type": "RBS",
                        "s_result_num": 0.0,          # <-- use s_result_num, not s_result
                        "s_last_meal": "",
                        "s_history": "",
                        "s_symptoms": "",
                        "s_notes": "",                        
                        "s_saving": False,
                        "s_saving_ts": None,
                    })
                    st.rerun()
                else:
                    st.session_state["s_saving"] = False
                    st.session_state["s_saving_ts"] = None
                    st.error("Save failed (DB unavailable).")
            except Exception as e:
                # show error and ensure saving flag is cleared
                st.error("Save failed — database error (see details below).")
                st.text(traceback.format_exc())
            finally:
                # make sure we always clear the 'saving' flag if we didn't rerun
                # (if we called st.rerun() on success, this won't be reached in that run)
                if st.session_state.get("s_saving", False):
                    st.session_state["s_saving"] = False
                    st.session_state["s_saving_ts"] = None

        # --- Recent tests table + bulk 'Send to doctor' (right aligned) ---
        st.markdown("### Recent tests")
        show_unsent_only = st.toggle(
            "Show only unsent", value=True, key="s_show_unsent",
            help="Show only tests that have not been sent to doctor yet."
        )

        tests_rows = []
        if get_connection:
            conn = get_connection(); cur = conn.cursor()
            base_sql = """
                SELECT t.id, p.name, t.test_type, t.result_mg_dl, t.last_meal_time, t.sent_to_doctor, t.taken_at,t.frequency_days
                FROM blood_sugar_tests t
                JOIN patients p ON p.id = t.fk_patient_id
            """
            if show_unsent_only:
                cur.execute(base_sql + " WHERE t.sent_to_doctor = 0 ORDER BY t.id DESC LIMIT 100")
            else:
                cur.execute(base_sql + " ORDER BY t.id DESC LIMIT 100")
            tests_rows = cur.fetchall()
            conn.close()

        if tests_rows:
            import pandas as pd
            df = pd.DataFrame(
                tests_rows,
                columns=["ID", "Patient", "Type", "Result", "Last meal", "Sent to Dr", "Taken at" , "Follow-up (days)"]
            )
                          
            
            if "Taken at" in df.columns:
                df["Taken at"] = pd.to_datetime(df["Taken at"], format="ISO8601", errors="coerce")
                df["Taken at"] = df["Taken at"].dt.strftime("%d %B %Y, %I:%M %p")
            
            # Compute Next record
            df["Next record"] = df.apply(
                lambda r: _sugar_next_due(r["Taken at"], r.get("Follow-up (days)", 0)),
                axis=1
            )
            
            # user-selectable column
            df.insert(0, "Select", False)

            edited = st.data_editor(
                df,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Select": st.column_config.CheckboxColumn("Select"),
                    "Sent to Dr": st.column_config.CheckboxColumn("Sent to Dr", disabled=True),
                },
                # make data read-only except the Select column
                disabled=["ID", "Patient", "Type", "Result", "Last meal", "Sent to Dr", "Taken at"],
                key="sugar_recent_editor",
            )

            # anything already sent is NOT eligible to send again
            selected_df = edited[edited["Select"] == True]
            selected_eligible_ids = selected_df.loc[selected_df["Sent to Dr"] != True, "ID"].astype(int).tolist()
            selected_already_sent = selected_df.loc[selected_df["Sent to Dr"] == True, "ID"].tolist()

            # right-aligned bulk action
            spacer, right = st.columns([6, 1])
            with right:
                disabled_btn = (len(selected_eligible_ids) == 0)
                if st.button("📨 Send to doctor", key="btn_sugar_send_bulk", disabled=disabled_btn):
                    placeholders = ",".join(["?"] * len(selected_eligible_ids))
                    try:
                        conn = get_connection(); cur = conn.cursor()
                        cur.execute(
                            f"UPDATE blood_sugar_tests SET sent_to_doctor = 1 WHERE id IN ({placeholders})",
                            selected_eligible_ids
                        )
                        conn.commit(); conn.close()
                        st.success(f"Sent {len(selected_eligible_ids)} test(s) to doctor.")
                        if selected_already_sent:
                            st.info(f"Ignored already-sent ID(s): {', '.join(map(str, selected_already_sent))}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to send: {e}")

            # small hint if user ticked any already-sent rows
            if selected_already_sent and len(selected_eligible_ids) == 0:
                st.caption("Some selected rows are already sent; they can’t be sent again.")
        else:
            st.info("No tests found.")

    
    elif section == "Stock":
        st.subheader("Inventory / Stock")

        if "stock_sub" not in st.session_state:
            st.session_state["stock_sub"] = "Menu"

        sub = st.session_state["stock_sub"]

        # ---------- Stock menu (two sub-cards) ----------
        if sub == "Menu":
            c1, c2 = st.columns(2)
            with c1:
                _sub_card("🧾", "Stock Order List", "btn_stock_orders",section="Stock", sub="Stock_Order_List")
            with c2:
                _sub_card("⚠️", "Low Stock Alert", "btn_stock_low",
                          section="Stock", sub="Stock_Low_Alert")

        # ---------- Sub-page: Order List ----------
        elif sub == "Stock_Order_List":
            if st.button("← Back to Inventory", key="back_stock_menu_1"):
                st.session_state["stock_sub"] = "Menu"; st.rerun()
            _render_stock_order_list(user)

        # ---------- Sub-page: Low Stock Alert ----------
        elif sub == "Stock_Low_Alert":
            if st.button("← Back to Inventory", key="back_stock_menu_2"):
                st.session_state["stock_sub"] = "Menu"; st.rerun()
            _render_low_stock_alert()

    elif section == "Health Profiles":
        st.subheader("📊 Health Profiles")

        # ✅ Call the unified function
        render_health_profiles()
        
    # elif section == "Reports":
        # st.subheader("📑 Reports")
 
    elif section == "Messages":
        st.markdown("### 💬 Messages")

        _ensure_messages_table()

        conn = get_connection(); cur = conn.cursor()
        rows = cur.execute(
            "SELECT * FROM messages ORDER BY created_at ASC LIMIT 100"
        ).fetchall()
        conn.close()

        # --- Chat Display ---
        st.subheader("Chat with Doctor/Admin")
        if rows:
            for r in rows:  # show oldest → newest
                sender = r["sender_role"]
                msg = r["message"]
                ts = r["created_at"]

                if sender == "Health Agent":
                    align = "right"
                    color = "#d1f7c4"  # light green
                elif sender in ("Doctor", "Admin"):
                    align = "left"
                    color = "#f0f2f6"  # light gray
                else:  # System alerts
                    align = "center"
                    color = "#e6f0ff"

                st.markdown(
                    f"""
                    <div style="text-align:{align}; margin:6px;">
                        <div style="display:inline-block; background:{color};
                                    padding:8px 12px; border-radius:10px; max-width:70%;">
                            <b>{sender}:</b> {msg}<br>
                            <span style="font-size:10px; color:gray;">{ts}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("No messages yet.")

        # --- Send New Message ---
        with st.form("send_msg", clear_on_submit=True):
            new_msg = st.text_input("Type your message")
            recipient = st.selectbox("Send To", ["Doctor", "Admin"])
            submitted = st.form_submit_button("Send")
            if submitted and new_msg.strip():
                conn = get_connection(); cur = conn.cursor()
                
                cur.execute(
                    "INSERT INTO messages (sender_role, recipient_role, message, created_at) VALUES (?,?,?,?)",
                    ("Health Agent", recipient, new_msg.strip(), datetime.utcnow().isoformat())
                )
                conn.commit(); conn.close()
                st.rerun()

        st.markdown("---")

        # --- Stock Alerts (system messages) ---
        st.subheader("📦 Stock Alerts")
        conn = get_connection(); cur = conn.cursor()
        stock_alerts = cur.execute(
            "SELECT * FROM stock_requests WHERE status!='Pending' ORDER BY requested_at DESC LIMIT 20"
        ).fetchall()
        conn.close()

        if stock_alerts:
            for s in stock_alerts:
                st.markdown(
                    f"""
                    ⚠️ <b>{s['item_name']}</b> request of {s['qty']} units 
                    → <b>{s['status']}</b> (requested at {s['requested_at']})
                    """, unsafe_allow_html=True
                )
        else:
            st.info("No stock alerts yet.")


    # =========================
    # Reports render (aligned header + advice)
    # ========================    
    elif section == "Reports":
        st.markdown("### 📄 Reports")

        conn = get_connection(); cur = conn.cursor()
        patients = cur.execute("SELECT id, name, gender FROM patients ORDER BY id DESC").fetchall()
        conn.close()

        if not patients:
            st.info("No patients available.")
            return

        # --- Header row: Patient | Doctor Advice ---
        hcol1, hcol2 = st.columns([1, 2])
        with hcol1:
            st.markdown("#### Patient")
        with hcol2:
            st.markdown("#### 🩺 Doctor Advice")

        # --- Content row: Dropdown | Advice Card + call actions ---
        col1, col2 = st.columns([1, 2], vertical_alignment="center")

        with col1:
            pid = st.selectbox(
                "",  # keep clean alignment
                [p["id"] for p in patients],
                format_func=lambda i: f"#{i} · {next(p['name'] for p in patients if p['id']==i)} ({next(p['gender'] for p in patients if p['id']==i)})",
                key="reports_patient_select"
            )

        with col2:
            # Fetch advice
            conn = get_connection(); cur = conn.cursor()
            advice_row = cur.execute(
                "SELECT advice, created_at FROM doctor_advice WHERE patient_id=? ORDER BY id DESC LIMIT 1",
                (pid,)
            ).fetchone()

            # Fetch patient name + mobile for call actions
            pinfo = cur.execute(
                "SELECT name, COALESCE(mobile, phone) FROM patients WHERE id=?",
                (pid,)
            ).fetchone()
            conn.close()

            if advice_row:
                advice_text = advice_row["advice"]
                created_at = advice_row["created_at"]
                st.markdown(
                    f"""
                    <div style='background-color:#e6f7f1; padding:10px 15px; 
                                border-radius:8px;'>
                        {advice_text}
                    </div>
                    <div style='font-size:12px; color:gray; margin-top:4px;'>🕒 {created_at}</div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.info("No advice recorded for this patient.")

            # --- Audio / WhatsApp / Video call actions ---
            patient_name = pinfo[0] if pinfo else "Patient"
            patient_mobile = pinfo[1] if (pinfo and pinfo[1]) else None
            _call_actions_block(patient_name, patient_mobile, pid)


        # ---- Medications ----
        st.markdown("### 💊 Medications")
        conn = get_connection(); cur = conn.cursor()
        meds = cur.execute("""
            SELECT drug_name, dose, frequency, duration, referral_facility, follow_up_days, reason, created_at
            FROM medications WHERE patient_id=? ORDER BY id DESC
        """, (pid,)).fetchall()
        conn.close()

        if meds:
            import pandas as pd
            df = pd.DataFrame(meds, columns=[
                "Drug", "Dose", "Frequency", "Duration", "Referral Facility",
                "Follow-up (days)", "Reason", "Created At"
            ])
            df["Created At"] = pd.to_datetime(df["Created At"], errors="coerce").dt.strftime("%Y-%m-%d %H:%M")

            # --- Mapping Frequency → Timings ---
            def frequency_to_timings(freq: str) -> str:
                if not freq:
                    return "—"
                f = freq.strip().lower()
                if "thrice" in f:
                    return "9:00 AM, 3:00 PM, 9:00 PM (after food)"
                elif "twice" in f:
                    return "9:00 AM, 9:00 PM (before/after food)"
                elif "once" in f or "daily" in f:
                    return "9:00 AM (before/after food)"
                elif "four" in f:
                    return "6:00 AM, 12:00 PM, 6:00 PM, 12:00 AM"
                else:
                    return "Custom / As directed"

            df["Timings"] = df["Frequency"].apply(frequency_to_timings)

            # --- Table 1: Prescription Details ---
            st.markdown("#### 🧾 Prescription Details")
            df1 = df[["Drug", "Dose", "Frequency", "Duration", "Timings"]]
            st.dataframe(df1, use_container_width=True, hide_index=True)

            # --- Table 2: Referral/Follow-up Details ---
            st.markdown("#### 🏥 Referral & Follow-up")
            df2 = df[["Referral Facility", "Follow-up (days)", "Reason", "Created At"]]
            st.dataframe(df2, use_container_width=True, hide_index=True)

        else:
            st.info("No medications recorded yet for this patient.")

        
            
    elif section == "SOPs":
        st.subheader("Standard Operating Procedures")
        st.info("Upload or link SOP PDFs here.")
        
    elif section == "Pharmacy":
        render_pharmacy()

    elif section == "Profile":
        st.subheader("Profile")
        _render_profile(user)

    # bottom nav appears on every screen
    _bottom_nav()

    # close scope
    st.markdown('</div>', unsafe_allow_html=True)

from typing import Optional

from datetime import datetime, timezone
from typing import Optional

from datetime import datetime, timezone
from typing import Optional

def _save_blood_sugar(
    pid: int,
    test_type: str,
    result_mg_dl: Optional[float],
    last_meal_time: str,
    history: str,
    symptoms: str,
    notes: str,
    sent_to_doctor: int,
    recorded_by: Optional[int],
    frequency_days: int = 0,
) -> bool:
    if not get_connection:
        raise RuntimeError("get_connection is not configured (returned falsy).")
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO blood_sugar_tests
            (fk_patient_id, test_type, result_mg_dl, last_meal_time, history, symptoms, notes,
             sent_to_doctor, taken_at, frequency_days, recorded_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            pid,
            test_type,
            result_mg_dl,
            last_meal_time,
            history.strip(),
            symptoms.strip(),
            notes.strip(),
            sent_to_doctor,
            datetime.now(timezone.utc).isoformat(),
            int(frequency_days or 0),
            recorded_by
        ))
        conn.commit()
        conn.close()
        return True
    except Exception:
        # Make debugging visible by re-raising the original exception.
        # (Temporary change — revert when issue is fixed.)
        try:
            if conn:
                conn.close()
        except Exception:
            pass
        raise


def _ensure_stock_requests_table():
    """Requests raised by RMP to Admin for inventory items."""
    if not get_connection:
        return
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS stock_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            qty INTEGER NOT NULL CHECK(qty >= 0),
            requested_by INTEGER,
            requested_at TEXT NOT NULL,
            status TEXT DEFAULT 'Pending'   -- Pending / Approved / Rejected
        )
    """)
    conn.commit(); conn.close()
    

#Table for doctor advice
def _ensure_doctor_advice_table():
    """Doctor Advice"""
    if not get_connection:
        return
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""    
        CREATE TABLE IF NOT EXISTS doctor_advice (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            advice TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        );
    """)
    conn.commit(); conn.close()
    
#Table for medications
def _ensure_medications_table():
    """Medications"""
    if not get_connection:
        return
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""  
        CREATE TABLE IF NOT EXISTS medications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            drug_name TEXT NOT NULL,
            dose TEXT,
            frequency TEXT,
            duration TEXT,
            referral_facility TEXT,
            follow_up_days INTEGER,
            reason TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        );
    """)
    conn.commit(); conn.close()
    


def _save_stock_requests(requests: list[tuple[str, int]], user_id: int | None) -> bool:
    """requests = [(item_name, qty), ...]"""
    if not get_connection or not requests:
        return False
    now = datetime.utcnow().isoformat()
    rows = [(name, int(q), user_id, now) for (name, q) in requests if int(q) >= 0]
    if not rows:
        return False
    conn = get_connection(); cur = conn.cursor()
    cur.executemany("""
        INSERT INTO stock_requests (item_name, qty, requested_by, requested_at)
        VALUES (?,?,?,?)
    """, rows)
    conn.commit(); conn.close()
    return True



def _low_stock_alert_df(items: list[str], threshold: int = 5):
    """Return a DataFrame with Current, Requested (Pending), Received (Approved), Total."""
    import pandas as pd
    if not get_connection:
        return pd.DataFrame({
            "Item": items,
            "Current": [0]*len(items),
            "Requested Order": [0]*len(items),
            "Received Order": [0]*len(items),
            "Total": [0]*len(items),
            "Low? (≤thr)": [False]*len(items),
        })

    conn = get_connection(); cur = conn.cursor()

    # Current stock
    cur.execute("SELECT item_name, COALESCE(qty,0) FROM stock")
    stock_map = {row[0]: int(row[1] or 0) for row in cur.fetchall()}

    # Requests (Pending)
    cur.execute("""
        SELECT item_name, COALESCE(SUM(qty),0)
        FROM stock_requests
        WHERE status='Pending'
        GROUP BY item_name
    """)
    req_map = {row[0]: int(row[1] or 0) for row in cur.fetchall()}

    # Received (Approved)
    cur.execute("""
        SELECT item_name, COALESCE(SUM(qty),0)
        FROM stock_requests
        WHERE status='Approved'
        GROUP BY item_name
    """)
    rec_map = {row[0]: int(row[1] or 0) for row in cur.fetchall()}

    conn.close()

    rows = []
    for name in items:
        cur_qty = stock_map.get(name, 0)
        req_qty = req_map.get(name, 0)
        rec_qty = rec_map.get(name, 0)
        total   = cur_qty + rec_qty
        rows.append([name, cur_qty, req_qty, rec_qty, total, total <= threshold])

    import pandas as pd
    return pd.DataFrame(rows, columns=[
        "Item", "Current", "Requested Order", "Received Order", "Total", "Low? (≤thr)"
    ])



def _render_stock_order_list(user):
    import pandas as pd

    st.markdown("<h3>🧾 Stock Order List</h3>", unsafe_allow_html=True)

    base_df = pd.DataFrame({"Item": RMP_STOCK_ITEMS, "Quantity": [0]*len(RMP_STOCK_ITEMS)})
    edited = st.data_editor(
        base_df,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Item": st.column_config.SelectboxColumn("Item", options=RMP_STOCK_ITEMS, disabled=True),
            "Quantity": st.column_config.NumberColumn("Quantity", min_value=0, step=1, format="%d"),
        },
        key="stock_items_editor",
    )

    rows_to_send = []
    for _, row in edited.iterrows():
        try:
            q = int(row["Quantity"])
        except Exception:
            q = 0
        if q > 0:
            rows_to_send.append((row["Item"], q))

    disabled_submit = len(rows_to_send) == 0
    if st.button("📨 Submit request to Admin", key="btn_stock_submit", disabled=disabled_submit, type="primary"):
        ok = _save_stock_requests(rows_to_send, user.get("id"))
        if ok:
            st.success(f"Request sent to Admin for {len(rows_to_send)} item(s).")
            st.rerun()
        else:
            st.error("Could not send request (DB unavailable or empty).")

    st.write("")
    st.markdown("#### Your recent requests")
    if get_connection:
        conn = get_connection(); cur = conn.cursor()
        cur.execute("""
            SELECT id, item_name, qty, status, requested_at
            FROM stock_requests
            WHERE requested_by IS ?
            ORDER BY id DESC
            LIMIT 50
        """, (user.get("id"),))
        my_rows = cur.fetchall(); conn.close()

        if my_rows:
            df = pd.DataFrame(my_rows, columns=["ID", "Item", "Qty", "Status", "Requested At"])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No requests yet. Fill quantities above and click Submit.")
    else:
        st.warning("DB connection not configured.")


def _render_low_stock_alert():
    st.markdown("<h3>⚠️ Low Stock Alert</h3>", unsafe_allow_html=True)

    threshold = st.number_input("Low stock threshold (≤)", min_value=0, max_value=1000, step=1, value=5, key="low_thr")
    df_alert = _low_stock_alert_df(RMP_STOCK_ITEMS, threshold=threshold)

    only_low = st.toggle("Show only low items", value=False, key="low_only")
    df_show = df_alert[df_alert["Low? (≤thr)"]] if only_low else df_alert
    st.dataframe(df_show.drop(columns=["Low? (≤thr)"]), use_container_width=True, hide_index=True)

    csv = df_show.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, file_name="low_stock_alert.csv", mime="text/csv", key="dl_low_stock_alert")

def render_stock_alerts():
    """Show stock alerts merged from messages table (System messages)."""
    if not get_connection:
        return
    conn = get_connection(); cur = conn.cursor()

    # Get only system-generated stock alerts
    cur.execute("""
        SELECT message, created_at
        FROM messages
        WHERE sender_role = 'System'
          AND message LIKE 'Stock alert:%'
        ORDER BY created_at DESC
    """)
    alerts = cur.fetchall()
    conn.close()

    st.subheader("📦 Stock Alerts")
    if not alerts:
        st.info("No stock alerts yet.")
        return

    for a in alerts:
        msg = a["message"]
        created_at = a["created_at"]

        # Extract quantity if present
        qty = None
        for token in msg.split():
            if token.isdigit():
                qty = int(token); break

        # Color coding
        if "Out of stock" in msg or (qty is not None and qty == 0):
            st.error(f"❌ {msg}\n\n🕒 {created_at}")
        elif qty is not None and qty <= 2:
            st.warning(f"⚠️ {msg}\n\n🕒 {created_at}")
        elif qty is not None and qty <= 5:
            st.info(f"ℹ️ {msg}\n\n🕒 {created_at}")
        else:
            st.success(f"✅ {msg}\n\n🕒 {created_at}")



def render_pharmacy():
    st.subheader("💊 Pharmacy")

    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT id, drug_name, supplied, distributed, amount_due, amount_collected
        FROM pharmacy
    """)
    rows = cur.fetchall()
    conn.close()

    # Header row
    header_cols = st.columns([2, 1, 1, 1, 1, 1, 1])
    headers = ["Drug", "Supplied", "Distributed", "Balance", "Amount Due", "Collected", "Balance Amount"]
    for col, head in zip(header_cols, headers):
        col.markdown(f"**{head}**")

    # Data rows
    for rid, drug, supplied, distributed, amt_due, amt_collected in rows:
        balance = supplied - distributed
        balance_amt = amt_due - amt_collected

        cols = st.columns([2, 1, 1, 1, 1, 1, 1])

        # Drug name
        cols[0].write(drug)

        # Supplied
        cols[1].write(supplied)

        # Distributed (editable integer)
        new_distributed = cols[2].number_input(
            "", min_value=0, value=int(distributed), step=1, key=f"dist_{rid}", label_visibility="collapsed"
        )

        # Balance
        cols[3].write(supplied - new_distributed)

        # Amount Due
        cols[4].write(float(amt_due))

        # Collected (editable float)
        new_amt_collected = cols[5].number_input(
            "", min_value=0.0, value=float(amt_collected), step=1.0, key=f"amt_{rid}", label_visibility="collapsed"
        )

        # Balance Amount
        cols[6].write(float(amt_due - new_amt_collected))

        # If updated → save to DB
        if new_distributed != distributed or new_amt_collected != amt_collected:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("""
                UPDATE pharmacy
                SET distributed=?, amount_collected=?
                WHERE id=?
            """, (new_distributed, new_amt_collected, rid))
            conn.commit(); conn.close()

import pandas as pd
import streamlit as st

# =========================
# New function definition
# =========================
def render_health_profiles():
    """
    Health Profiles
    - Filters row: Search | Risk | Select Patient  (Select Patient includes "All patients")
    - Results table for the current filter set
    - Health Metrics chart controlled by: Select metrics + Group by (single instance)
      * When Select Patient == "All patients", the chart overlays all filtered patients
      * Otherwise it shows the selected patient's metrics
    """
    import pandas as pd
    import altair as alt

    if not get_connection:
        st.error("Database not available.")
        return

    # ---------- Load patients ----------
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT id, name, age, gender, COALESCE(mobile, phone) AS mobile, aadhar FROM patients ORDER BY name")
    patients = cur.fetchall()
    conn.close()

    if not patients:
        st.info("No patients found.")
        return

    # ---------- Helpers ----------
    def _latest_vitals_for(pid: int):
        """Return (date, bp_sys, bp_dia, pulse, temp) or None row if missing."""
        conn = get_connection(); c = conn.cursor()
        c.execute("""
            SELECT recorded_at, bp_sys, bp_dia, pulse, temperature
            FROM vitals WHERE fk_patient_id=?
            ORDER BY recorded_at DESC LIMIT 1
        """, (pid,))
        row = c.fetchone()
        conn.close()
        return row

    def _latest_sugar_for(pid: int):
        """Prefer latest FBS; otherwise latest of any type. Return (date, test_type, value) or None."""
        conn = get_connection(); c = conn.cursor()
        # latest FBS first
        c.execute("""
            SELECT taken_at, test_type, result_mg_dl
            FROM blood_sugar_tests
            WHERE fk_patient_id=? AND test_type='FBS'
            ORDER BY taken_at DESC LIMIT 1
        """, (pid,))
        row = c.fetchone()
        if not row:
            c = get_connection().cursor()
            c.execute("""
                SELECT taken_at, test_type, result_mg_dl
                FROM blood_sugar_tests
                WHERE fk_patient_id=?
                ORDER BY taken_at DESC LIMIT 1
            """, (pid,))
            row = c.fetchone()
        conn.close()
        return row

    def _risk_label(pid: int) -> str:
        """
        🔴 Red:    BP Sys >160 or BP Dia >100 or Pulse >120 or FBS >140
        🟠 Amber:  BP Sys 140–160 or BP Dia 90–100 or Pulse 100–120 or FBS 110–140
        🟢 Green:  otherwise / no data
        """
        v = _latest_vitals_for(pid)
        s = _latest_sugar_for(pid)
        bp_sys = (v[1] if v else None) or 0
        bp_dia = (v[2] if v else None) or 0
        pulse  = (v[3] if v else None) or 0
        fbs = 0
        if s and s[1] == "FBS" and s[2] is not None:
            fbs = float(s[2])

        # Red
        if bp_sys > 160 or bp_dia > 100 or pulse > 120 or fbs > 140:
            return "Red"
        # Amber
        if (140 <= bp_sys <= 160) or (90 <= bp_dia <= 100) or (100 <= pulse <= 120) or (110 <= fbs <= 140):
            return "Amber"
        # Green (default)
        return "Green"

    # ---------- Top filters: Search | Risk | Select Patient ----------
    col1, col2, col3 = st.columns([2, 1, 2])
    with col1:
        q = st.text_input("Search (name / mobile / aadhar)", key="hp_search").strip().lower()
    with col2:
        risk_choice = st.selectbox("Risk level", ["All", "Red", "Amber", "Green"], key="hp_risk")
    with col3:
        # Build labels for dropdown (with “All patients” on top)
        options = ["All patients"]
        label_to_pid = {}
        for p in patients:
            pid, name, age, gender, mobile, aadhar = p
            label = f"#{pid} · {name} ({gender}, {age} yrs)"
            label_to_pid[label] = pid
            options.append(label)
        sel_label = st.selectbox("Select Patient", options, index=0, key="hp_patient_select")

    # ---------- Apply filters for table ----------
    filtered = patients
    if q:
        filtered = [p for p in filtered if q in f"{p[1]} {p[4] or ''} {p[5] or ''}".lower()]

    if risk_choice != "All":
        filtered = [p for p in filtered if _risk_label(p[0]) == risk_choice]

    # ---------- Build results table ----------
    rows = []
    for p in filtered:
        pid, name, age, gender, mobile, aadhar = p
        v = _latest_vitals_for(pid)
        s = _latest_sugar_for(pid)
        bp_sys = v[1] if v else None
        bp_dia = v[2] if v else None
        pulse  = v[3] if v else None
        sugar  = s[2] if s else None
        sugar_type = s[1] if s else None
        rows.append({
            "ID": pid,
            "Patient": name,
            "Mobile": mobile,
            "Aadhar": aadhar,
            "BP Sys": bp_sys,
            "BP Dia": bp_dia,
            "Pulse": pulse,
            "Sugar": sugar,
            "Sugar Type": sugar_type,
            "Risk": _risk_label(pid),
        })

    df_tbl = pd.DataFrame(rows)
    st.dataframe(df_tbl, use_container_width=True, hide_index=True)

    # ---------- Chart Controls (metrics + group-by) ----------
    st.markdown("### 📈 Health Metrics")
    cc1, cc2 = st.columns([3, 2])
    with cc1:
        metrics_choices = ["BP Sys", "BP Dia", "Pulse", "FBS", "PPBS", "HbA1c", "RBS"]
        sel_metrics = st.multiselect(
            "Select metrics",
            metrics_choices,
            default=["BP Sys", "BP Dia"],
            key="hp_metrics"
        )
    with cc2:
        group_by = st.selectbox(
            "Group by",
            ["Daily", "Monthly", "Yearly"],
            index=0,
            key="hp_group_by"
        )

    # ---------- Build chart dataframe ----------
    # Determine which patients to plot: single or all
    plot_pids = []
    if sel_label == "All patients":
        plot_pids = [p[0] for p in filtered]
    else:
        plot_pids = [label_to_pid.get(sel_label)]

    if not plot_pids:
        st.info("No data to plot for the current filters.")
        return

    # Collect time series per patient
    all_parts = []
    for pid in plot_pids:
        # vitals
        conn = get_connection(); c = conn.cursor()
        c.execute("""
            SELECT recorded_at, bp_sys, bp_dia, pulse, temperature
            FROM vitals WHERE fk_patient_id=? ORDER BY recorded_at
        """, (pid,))
        vit = c.fetchall()

        # sugars (wide → FBS/PPBS/HbA1c/RBS)
        c.execute("""
            SELECT taken_at, test_type, result_mg_dl
            FROM blood_sugar_tests WHERE fk_patient_id=? ORDER BY taken_at
        """, (pid,))
        sug = c.fetchall()
        conn.close()

        df_v = pd.DataFrame(vit, columns=["Date", "BP Sys", "BP Dia", "Pulse", "Temp"])
        if not df_v.empty:
            df_v["Date"] = pd.to_datetime(df_v["Date"], errors="coerce")

        df_s = pd.DataFrame(sug, columns=["Date", "Test", "Result"])
        if not df_s.empty:
            df_s["Date"] = pd.to_datetime(df_s["Date"], errors="coerce")
            # Use an aggregation to handle potential duplicate (Date, Test) rows.
            # Choose 'mean' or 'last' depending on desired behavior.
            df_s = df_s.pivot_table(index="Date", columns="Test", values="Result", aggfunc='mean').reset_index()


        # merge wide
        if not df_v.empty or not df_s.empty:
            if df_v.empty:
                df = df_s.rename_axis(None, axis=1)
            elif df_s.empty:
                df = df_v.rename_axis(None, axis=1)
            else:
                df = pd.merge(df_v, df_s, on="Date", how="outer")

            # group by
            if group_by == "Monthly":
                df["Date"] = df["Date"].dt.to_period("M").dt.to_timestamp()
                df = df.groupby("Date").mean(numeric_only=True).reset_index()
            elif group_by == "Yearly":
                df["Date"] = df["Date"].dt.to_period("Y").dt.to_timestamp()
                df = df.groupby("Date").mean(numeric_only=True).reset_index()

            df["PatientID"] = pid
            all_parts.append(df)

    if not all_parts:
        st.info("No vitals/tests recorded for the selection.")
        return

    df_all = pd.concat(all_parts, ignore_index=True).sort_values("Date")
    # keep only requested metrics that exist
    keep_cols = ["Date", "PatientID"] + [m for m in sel_metrics if m in df_all.columns]
    df_all = df_all[[c for c in keep_cols if c in df_all.columns]]

    if len(keep_cols) <= 2:
        st.info("No data available for the selected metrics.")
        return

    # Melt to long for Altair
    df_long = df_all.melt(id_vars=["Date", "PatientID"], var_name="Metric", value_name="Value").dropna()

    # If plotting many patients, color by Metric and stroke-dash by Patient
    color = alt.Color("Metric:N")
    if len(plot_pids) > 1:
        line = alt.Chart(df_long).mark_line(point=True).encode(
            x="Date:T",
            y="Value:Q",
            color=color,
            strokeDash=alt.StrokeDash("PatientID:N", legend=alt.Legend(title="Patient")),
            tooltip=["Date:T", "Metric:N", "Value:Q", "PatientID:N"]
        )
    else:
        line = alt.Chart(df_long).mark_line(point=True).encode(
            x="Date:T",
            y="Value:Q",
            color=color,
            tooltip=["Date:T", "Metric:N", "Value:Q"]
        )

    st.altair_chart(line.properties(height=420, width="container"), use_container_width=True)

# =========================
# Helper for risk badges
# =========================
def _risk_badge_for_patient(pid: int) -> str:
    """Return 🔴/🟠/🟢 based on last recorded vitals/sugar."""
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT bp_sys, bp_dia, pulse FROM vitals WHERE fk_patient_id=? ORDER BY recorded_at DESC LIMIT 1", (pid,))
    v = cur.fetchone()

    cur.execute("SELECT result_mg_dl FROM blood_sugar_tests WHERE fk_patient_id=? AND test_type='FBS' ORDER BY taken_at DESC LIMIT 1", (pid,))
    s = cur.fetchone()
    conn.close()

    risk = "Green"
    if v:
        bp_sys, bp_dia, pulse = v[0], v[1], v[2]
        if bp_sys and bp_sys > 160 or bp_dia and bp_dia > 100 or pulse and pulse > 120:
            risk = "Red"
        elif bp_sys and bp_sys >= 140 or bp_dia and bp_dia >= 90 or pulse and pulse >= 100:
            risk = "Amber"

    if s:
        sugar_val = s[0]
        if sugar_val and sugar_val > 140:
            risk = "Red"
        elif sugar_val and sugar_val >= 110:
            risk = "Amber"

    return {"Red":"🔴","Amber":"🟠","Green":"🟢"}.get(risk, "🟢")


from datetime import datetime
import streamlit as st
import urllib.parse
def _call_actions_block(name: str, mobile: str | None, patient_id: int):
    tel_url = f"tel:{mobile}" if mobile else "#"
    wa_url = f"https://wa.me/{mobile}" if mobile else "#"
    meet_url = f"https://meet.jit.si/{patient_id}_{name.replace(' ', '_')}"  # unique video link

    st.markdown(
        f"""
        <style>
        .action-row {{
            display:flex;
            gap:1rem;
            flex-wrap:wrap;
            margin-top:.5rem;
            align-items:center;
        }}
        .action-btn {{
            display:inline-block;
            padding:.5rem 1.2rem;
            border:1px solid rgba(0,0,0,.1);
            border-radius:10px;
            background:#f7f9fc;
            font-weight:600;
            text-decoration:none;
            color:#1d4ed8;
            white-space:nowrap;
        }}
        .action-btn:hover {{
            background:#eef2f7;
        }}
        .action-note {{
            color:#6b7280;
            font-size:12px;
            margin-top:.25rem
        }}
        </style>

        <div class='action-row'>
            {"<a class='action-btn' href='" + tel_url + "'>📞 Audio</a>" if mobile else "<span class='action-note'>No mobile number</span>"}
            {"<a class='action-btn' href='" + wa_url + "' target='_blank'>💬 WhatsApp</a>" if mobile else ""}
            <a class='action-btn' href='{meet_url}' target='_blank'>🎥 Video</a>
        </div>
        """,
        unsafe_allow_html=True,
    )


    st.markdown("**Contact options**")
    st.markdown("<div class='action-row'>", unsafe_allow_html=True)

    
def _ensure_followup_columns():
    # Adds frequency_days + sent_to_doctor (for vitals) if missing
    try:
        conn = get_connection(); cur = conn.cursor()

        def _has_col(table, col):
            cur.execute(f"PRAGMA table_info({table})")
            return any(r[1].lower() == col.lower() for r in cur.fetchall())

        if not _has_col("vitals", "frequency_days"):
            cur.execute("ALTER TABLE vitals ADD COLUMN frequency_days INTEGER")
        if not _has_col("vitals", "sent_to_doctor"):
            cur.execute("ALTER TABLE vitals ADD COLUMN sent_to_doctor INTEGER DEFAULT 0")

        if not _has_col("blood_sugar_tests", "frequency_days"):
            cur.execute("ALTER TABLE blood_sugar_tests ADD COLUMN frequency_days INTEGER")

        conn.commit(); conn.close()
    except Exception:
        pass

# put this near where you build the vitals table
def _coerce_pos_int(value):
    """Return a positive int or None (handles '', None, NaN, non-numeric)."""
    import pandas as pd
    if value is None:
        return None
    # pd.isna covers NaN/NaT
    try:
        if isinstance(value, float) and pd.isna(value):
            return None
    except Exception:
        pass
    s = str(value).strip()
    if not s or s.lower() == "nan":
        return None
    try:
        n = int(float(s))
        return n if n > 0 else None
    except Exception:
        return None


from datetime import datetime, timedelta

from datetime import datetime, timedelta
import math

def _sugar_next_due(recorded_at_str: str, frequency_days) -> str:
    """Return next due date string for sugar test, or empty if no follow-up.
    Handles None/NaN/invalid inputs gracefully.
    """
    # Normalize frequency_days: accept ints, numeric strings, None, NaN
    try:
        # If it's a pandas NA/np.nan, math.isnan will work for floats
        if frequency_days is None:
            return ""
        # frequency_days might be numpy.nan (float) or a float; handle that
        try:
            if isinstance(frequency_days, float) and math.isnan(frequency_days):
                return ""
        except Exception:
            pass

        freq = int(frequency_days)
        if freq <= 0:
            return ""
    except Exception:
        return ""

    # Parse recorded_at_str safely
    if not recorded_at_str:
        return ""
    try:
        # Try the app format first
        dt = datetime.strptime(recorded_at_str, "%d %B %Y, %I:%M %p")
    except Exception:
        try:
            # try generic pandas-like ISO parsing fallback
            # recorded_at_str might already be a Timestamp/datetime object
            if hasattr(recorded_at_str, "to_pydatetime"):
                dt = recorded_at_str.to_pydatetime()
            else:
                dt = datetime.fromisoformat(str(recorded_at_str))
        except Exception:
            return ""

    next_dt = dt + timedelta(days=freq)
    return next_dt.strftime("%d %B %Y")
