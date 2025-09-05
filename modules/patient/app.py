# modules/patient/app.py
# Cleaned Patient module (safe to import). Provides render_patient_dashboard(user)
import streamlit as st
from datetime import datetime, date, timedelta
from pathlib import Path

# -----------------------------
# Small helpers / UI pieces
# -----------------------------
def _patient_tile_button(icon: str, title: str, value: str, key: str):
    """
    Tile-like button for the patient dashboard.
    Clicking sets patient_section in session_state to the key.
    """
    mid = f"ptile_{key}"
    st.markdown(f'<div id="{mid}"></div>', unsafe_allow_html=True)
    label = f"{icon} {title}\n\n{value}" if value else f"{icon} {title}"
    if st.button(label, key=f"patient_tile_{key}", use_container_width=True):
        st.session_state["patient_section"] = key
        st.rerun()

    # Scoped minimal tile CSS so the button looks like a card
    st.markdown(
        f"""
        <style>
        div#{mid} + div[data-testid="stButton"] > button {{
            height: 160px;
            border-radius: 12px !important;
            border: 1px solid #e5e7eb;
            box-shadow: 0 6px 14px rgba(0,0,0,0.04);
            background: #ffffff;
            color: #0f172a;
            font-weight: 600;
            white-space: pre-wrap;
            padding: 12px;
            font-size: 1rem;
            text-align: left;
        }}
        div#{mid} + div[data-testid="stButton"] > button:hover {{
            transform: translateY(-3px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.06);
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _ensure_patient_section_state():
    if "patient_section" not in st.session_state:
        st.session_state["patient_section"] = "Patient_Dashboard"


def _set_patient_section(key: str):
    st.session_state["patient_section"] = key
    st.rerun()


# -----------------------------
# Sub-pages (stubs + case allocation)
# -----------------------------
def render_patient_profile(user: dict):
    """
    Enhanced Patient Profile view (fixed for forms & numeric types).
    """
    import streamlit as st
    from datetime import datetime, date, timedelta
    from copy import deepcopy

    # --- Ensure storage exists ---
    if "patient_profiles" not in st.session_state:
        now = datetime.now()
        st.session_state.patient_profiles = {
            "P-1001": {
                "id": "P-1001",
                "name": "Ravi Kumar",
                "village": "Iskapalem",
                "age": 56,
                "gender": "M",
                "phone": "9999999999",
                "email": "",
                "disability": False,
                "chronic_conditions": ["Hypertension"],
                "allergies": "None",
                "created_at": now.isoformat(),
                "vitals": [
                    {"when": (now - timedelta(days=3)).isoformat(), "height_cm": 170.0, "weight_kg": 72.0, "bp": "130/85", "rbs_mgdl": 110},
                    {"when": (now - timedelta(days=1)).isoformat(), "height_cm": 170.0, "weight_kg": 71.5, "bp": "128/84", "rbs_mgdl": 105},
                ],
                "visits": [
                    {"date": (now - timedelta(days=3)).strftime("%Y-%m-%d"), "reason": "Fever", "notes": "Given symptomatic treatment", "reviewed": True},
                    {"date": (now - timedelta(days=1)).strftime("%Y-%m-%d"), "reason": "Follow-up", "notes": "Improving", "reviewed": False},
                ],
                "appointments": [
                    {"date": (now + timedelta(days=2)).strftime("%Y-%m-%d"), "reason": "Lab test"}
                ],
            },
            "P-1002": {
                "id": "P-1002",
                "name": "Sunita Devi",
                "village": "Mangalapet",
                "age": 34,
                "gender": "F",
                "phone": "9888888888",
                "email": "",
                "disability": False,
                "chronic_conditions": [],
                "allergies": "Penicillin",
                "created_at": now.isoformat(),
                "vitals": [],
                "visits": [],
                "appointments": [],
            }
        }

    profiles = st.session_state.patient_profiles
    patient_ids = sorted(list(profiles.keys()))

    # Determine which patient we're viewing
    viewing_patient_id = None
    if user.get("role", "").lower() == "patient":
        # Try to match by name or fallback to first
        match = next((k for k, v in profiles.items() if v.get("name", "").lower() == user.get("name", "").lower()), None)
        viewing_patient_id = match or (patient_ids[0] if patient_ids else None)
    else:
        st.subheader("Patient profiles (staff view)")
        viewing_patient_id = st.selectbox("Select patient", options=["(new)"] + patient_ids, index=1 if patient_ids else 0)
        if viewing_patient_id == "(new)":
            maxn = 0
            for pid in patient_ids:
                try:
                    n = int(pid.split("-")[-1])
                    if n > maxn:
                        maxn = n
                except Exception:
                    pass
            new_id = f"P-{maxn+101}"
            profiles[new_id] = {
                "id": new_id,
                "name": "",
                "village": "",
                "age": 0,
                "gender": "",
                "phone": "",
                "email": "",
                "disability": False,
                "chronic_conditions": [],
                "allergies": "",
                "created_at": datetime.now().isoformat(),
                "vitals": [],
                "visits": [],
                "appointments": [],
            }
            viewing_patient_id = new_id

    if not viewing_patient_id:
        st.warning("No patient profile available.")
        if st.button("← Back"):
            _set_patient_section("Patient_Dashboard")
        return

    profile = deepcopy(profiles.get(viewing_patient_id, {
        "id": viewing_patient_id,
        "name": "",
        "village": "",
        "age": 0,
        "gender": "",
        "phone": "",
        "email": "",
        "disability": False,
        "chronic_conditions": [],
        "allergies": "",
        "created_at": datetime.now().isoformat(),
        "vitals": [],
        "visits": [],
        "appointments": [],
    }))

    # Header
    st.markdown(f"## 👤 Profile — {profile.get('name') or profile.get('id')}")
    cols = st.columns([3, 1])
    with cols[0]:
        st.write(f"**Patient ID:** `{profile.get('id')}`")
        st.write(f"**Created:** {profile.get('created_at')}")
        st.write(f"**Village:** {profile.get('village') or '-'}")
        st.write(f"**Phone:** {profile.get('phone') or '-'}  ·  **Email:** {profile.get('email') or '-'}")
        st.write(f"**Age / Gender:** {profile.get('age') or '-'} / {profile.get('gender') or '-'}")
    with cols[1]:
        if profile.get("disability"):
            st.markdown("**⚠️ Disability**")
        if profile.get("chronic_conditions"):
            st.markdown(f"**Chronic:** {', '.join(profile.get('chronic_conditions'))}")

    st.markdown("---")

    left, right = st.columns([2, 1])

    # Left: editable fields
    with left:
        st.subheader("Personal details")
        name = st.text_input("Name", value=profile.get("name", ""), key=f"profile_name_{viewing_patient_id}")
        village = st.text_input("Village", value=profile.get("village", ""), key=f"profile_village_{viewing_patient_id}")
        age = st.number_input("Age", min_value=0, max_value=120, value=int(profile.get("age", 0)), key=f"profile_age_{viewing_patient_id}")
        gender = st.selectbox("Gender", options=["", "M", "F", "Other"], index=(["", "M", "F", "Other"].index(profile.get("gender", "")) if profile.get("gender", "") in ["", "M", "F", "Other"] else 0), key=f"profile_gender_{viewing_patient_id}")
        phone = st.text_input("Phone", value=profile.get("phone", ""), key=f"profile_phone_{viewing_patient_id}")
        email = st.text_input("Email", value=profile.get("email", ""), key=f"profile_email_{viewing_patient_id}")

        st.markdown("### Medical flags")
        disability = st.checkbox("Disability / special needs", value=profile.get("disability", False), key=f"profile_disability_{viewing_patient_id}")

        chronic_opts = ["Hypertension", "Diabetes", "COPD", "Asthma", "Heart disease"]
        existing = profile.get("chronic_conditions", [])
        chronic = st.multiselect("Chronic conditions", options=chronic_opts, default=[c for c in existing if c in chronic_opts], key=f"profile_chronic_{viewing_patient_id}")
        custom_conds = [c for c in existing if c not in chronic_opts]
        custom_input = st.text_input("Other conditions (comma separated)", value=",".join(custom_conds) if custom_conds else "", key=f"profile_customcond_{viewing_patient_id}")
        if custom_input.strip():
            extras = [x.strip() for x in custom_input.split(",") if x.strip()]
            chronic = chronic + extras
        allergies = st.text_area("Allergies / drug reactions", value=profile.get("allergies", ""), key=f"profile_allergies_{viewing_patient_id}")

        # Save personal details (not inside st.form; immediate button)
        if st.button("Save profile"):
            profiles[viewing_patient_id].update({
                "name": name,
                "village": village,
                "age": int(age),
                "gender": gender,
                "phone": phone,
                "email": email,
                "disability": bool(disability),
                "chronic_conditions": chronic,
                "allergies": allergies,
            })
            st.success("Profile saved")
            st.rerun()

    # Right: vitals & appointments
    with right:
        st.subheader("Vitals & quick actions")
        vitals = profile.get("vitals", [])
        latest = vitals[-1] if vitals else None
        st.markdown("**Latest**")
        if latest:
            st.write(f"Height: {latest.get('height_cm','-')} cm")
            st.write(f"Weight: {latest.get('weight_kg','-')} kg")
            st.write(f"BP: {latest.get('bp','-')}")
            st.write(f"RBS: {latest.get('rbs_mgdl','-')} mg/dL")
            st.write(f"When: {latest.get('when')}")
        else:
            st.info("No vitals recorded.")

        st.markdown("Add new vitals")
        # IMPORTANT: make numeric types consistent (floats for height/weight; int for RBS)
        with st.form(key=f"vital_form_{viewing_patient_id}"):
            # cast default values explicitly to float for height & weight
            default_h = float(latest.get("height_cm", 170.0)) if latest else 0.0
            default_w = float(latest.get("weight_kg", 70.0)) if latest else 0.0
            default_bp = latest.get("bp", "") if latest else ""
            default_rbs = int(latest.get("rbs_mgdl", 0)) if latest else 0

            h = st.number_input("Height (cm)", value=default_h, min_value=0.0, step=0.1, format="%.1f", key=f"v_height_{viewing_patient_id}")
            w = st.number_input("Weight (kg)", value=default_w, min_value=0.0, step=0.1, format="%.1f", key=f"v_weight_{viewing_patient_id}")
            bp = st.text_input("BP (e.g. 120/80)", value=default_bp, key=f"v_bp_{viewing_patient_id}")
            rbs = st.number_input("RBS (mg/dL)", value=default_rbs, min_value=0, step=1, key=f"v_rbs_{viewing_patient_id}")

            add_v = st.form_submit_button("Add vitals")
            if add_v:
                new_v = {"when": datetime.now().isoformat(), "height_cm": float(h), "weight_kg": float(w), "bp": bp, "rbs_mgdl": int(rbs)}
                profiles[viewing_patient_id].setdefault("vitals", []).append(new_v)
                st.success("Vitals added")
                st.rerun()

        st.markdown("---")
        st.subheader("Appointments")
        appts = profile.get("appointments", [])
        if appts:
            for a in appts:
                st.write(f"- {a.get('date')} — {a.get('reason')}")
        else:
            st.write("No upcoming appointments")

        # Appointment form must also include a submit button (it does)
        with st.form(key=f"appt_form_{viewing_patient_id}"):
            ap_date = st.date_input("Appointment date", value=date.today(), key=f"appt_date_{viewing_patient_id}")
            ap_reason = st.text_input("Reason", key=f"appt_reason_{viewing_patient_id}")
            add_ap = st.form_submit_button("Add appointment")
            if add_ap:
                profiles[viewing_patient_id].setdefault("appointments", []).append({"date": ap_date.strftime("%Y-%m-%d"), "reason": ap_reason})
                st.success("Appointment added")
                st.rerun()

    st.markdown("---")

    # Visits
    st.subheader("Visit history")
    visits = profile.get("visits", [])
    if visits:
        for idx, v in enumerate(visits[::-1]):
            real_idx = len(visits) - 1 - idx
            with st.expander(f"{v.get('date')} — {v.get('reason')}"):
                st.markdown(f"**Notes:**  \n{v.get('notes','-')}")
                st.write(f"Reviewed: {'Yes' if v.get('reviewed') else 'No'}")
                cols = st.columns([2, 1, 1])
                with cols[0]:
                    new_note = st.text_area("Append note", key=f"visit_note_{viewing_patient_id}_{real_idx}")
                with cols[1]:
                    if st.button("Append note", key=f"append_note_btn_{viewing_patient_id}_{real_idx}"):
                        if new_note.strip():
                            profiles[viewing_patient_id]["visits"][real_idx]["notes"] = profiles[viewing_patient_id]["visits"][real_idx].get("notes", "") + "\n" + new_note.strip()
                            st.success("Note appended")
                            st.rerun()
                with cols[2]:
                    if st.button("Mark reviewed", key=f"mark_reviewed_{viewing_patient_id}_{real_idx}"):
                        profiles[viewing_patient_id]["visits"][real_idx]["reviewed"] = True
                        st.success("Marked reviewed")
                        st.rerun()
    else:
        st.info("No visits recorded.")

    st.markdown("---")
    if st.button("← Back"):
        _set_patient_section("Patient_Dashboard")


def render_doctor_workload_monitor():
    """
    Doctor Workload Monitor
    - Filter by doctor(s) and date (today default)
    - Shows KPIs, per-doctor table + bar chart
    - Per-doctor drilldown (list of assigned patients)
    """
    import streamlit as st
    import pandas as pd
    from datetime import date, datetime, timedelta

    # --- sample data creation (safe: only created if not present) ---
    # If you already have case_rows in session_state (from Case Allocation), reuse them
    if "case_rows" not in st.session_state:
        now = datetime.now()
        st.session_state.case_rows = [
            {"id": "P-1001", "name": "Ravi Kumar", "age": 56, "gender": "M", "risk": "Red", "village": "Iskapalem",
             "reported_time": now - timedelta(hours=1, minutes=12), "rmp_proposed": "Dr. A", "assigned_doctor": "Dr. A"},
            {"id": "P-1002", "name": "Sunita Devi", "age": 34, "gender": "F", "risk": "Amber", "village": "Mangalapet",
             "reported_time": now - timedelta(hours=3, minutes=5), "rmp_proposed": None, "assigned_doctor": "Dr. B"},
            {"id": "P-1003", "name": "Karan Yadav", "age": 42, "gender": "M", "risk": "Green", "village": "Iskapalem",
             "reported_time": now - timedelta(days=1, hours=2), "rmp_proposed": "Dr. B", "assigned_doctor": "Dr. B"},
            {"id": "P-1004", "name": "Meena Thomas", "age": 29, "gender": "F", "risk": "Red", "village": "Padur",
             "reported_time": now - timedelta(minutes=40), "rmp_proposed": None, "assigned_doctor": "Dr. C"},
            {"id": "P-1005", "name": "Ajay Singh", "age": 61, "gender": "M", "risk": "Red", "village": "Iskapalem",
             "reported_time": now - timedelta(hours=2, minutes=20), "rmp_proposed": None, "assigned_doctor": "Dr. A"},
        ]

    # Build doctors list from assignments (fallback to sample list)
    doctors_from_cases = sorted({r["assigned_doctor"] for r in st.session_state.case_rows if r["assigned_doctor"]})
    if not doctors_from_cases:
        doctors = ["Dr. A", "Dr. B", "Dr. C"]
    else:
        doctors = doctors_from_cases

    # Create per-doctor stats (compute from case_rows; replace with DB aggregations in prod)
    def compute_doctor_stats(selected_date: date):
        stats = []
        for d in doctors:
            assigned = [r for r in st.session_state.case_rows if r.get("assigned_doctor") == d]
            # optionally filter by reported_time date
            assigned_by_date = [r for r in assigned if r["reported_time"].date() == selected_date]
            active = len(assigned_by_date)
            red = sum(1 for r in assigned_by_date if r["risk"] == "Red")
            amber = sum(1 for r in assigned_by_date if r["risk"] == "Amber")
            green = sum(1 for r in assigned_by_date if r["risk"] == "Green")
            # avg response time: now - reported_time in minutes (for assigned_by_date)
            if assigned_by_date:
                resp_mins = sum((datetime.now() - r["reported_time"]).total_seconds() / 60.0 for r in assigned_by_date) / len(assigned_by_date)
                resp_mins = int(resp_mins)
            else:
                resp_mins = None
            # load % heuristic: active cases / 10 * 100 (assume capacity 10)
            capacity = 10
            load_pct = round(min(100, (active / capacity) * 100), 0)
            stats.append({
                "doctor": d,
                "specialty": "General",  # placeholder
                "active_cases": active,
                "red": red,
                "amber": amber,
                "green": green,
                "avg_response_mins": resp_mins,
                "load_pct": load_pct,
                "patients": assigned_by_date,
            })
        return stats

    # --- UI: filters ---
    st.header("📊 Doctor Workload Monitor")
    st.caption("Monitor active cases, red/amber/green counts and per-doctor load.")

    cols = st.columns([2, 1, 1, 1])
    with cols[0]:
        selected_doctors = st.multiselect("Doctors (choose to filter)", options=doctors, default=doctors)
    with cols[1]:
        selected_date = st.date_input("Date", value=date.today())
    with cols[2]:
        only_red = st.checkbox("Show only doctors with Red cases", value=False)
    with cols[3]:
        if st.button("Refresh"):
            # in real app: re-fetch data here
            st.rerun()

    st.markdown("---")

    # --- Compute stats and build dataframe for chart/table ---
    doctor_stats = compute_doctor_stats(selected_date)
    # filter doctors selection
    doctor_stats = [s for s in doctor_stats if s["doctor"] in selected_doctors]
    if only_red:
        doctor_stats = [s for s in doctor_stats if s["red"] > 0]

    if not doctor_stats:
        st.info("No doctor data for the selected filters/date.")
        if st.button("← Back"):
            _set_patient_section("Patient_Dashboard")
        return

    # KPIs row
    total_doctors = len(doctor_stats)
    total_active = sum(s["active_cases"] for s in doctor_stats)
    avg_load = int(sum(s["load_pct"] for s in doctor_stats) / total_doctors) if total_doctors else 0

    k1, k2, k3 = st.columns(3)
    with k1:
        st.metric("Doctors", total_doctors)
    with k2:
        st.metric("Active cases", total_active)
    with k3:
        st.metric("Avg load %", f"{avg_load}%")

    st.markdown("### Workload by doctor")
    # DataFrame for table / chart
    df = pd.DataFrame([{
        "Doctor": s["doctor"],
        "Specialty": s["specialty"],
        "Active": s["active_cases"],
        "Red": s["red"],
        "Amber": s["amber"],
        "Green": s["green"],
        "AvgResp(mins)": s["avg_response_mins"] if s["avg_response_mins"] is not None else "-",
        "Load%": f"{s['load_pct']}%"
    } for s in doctor_stats])

    # Show table and chart side-by-side
    left, right = st.columns([2, 1])
    with left:
        st.dataframe(df, use_container_width=True)
    with right:
        # Bar chart of active cases per doctor
        chart_df = pd.DataFrame({"Active cases": [s["active_cases"] for s in doctor_stats]}, index=[s["doctor"] for s in doctor_stats])
        st.bar_chart(chart_df)

    st.markdown("---")

    # --- Per-doctor drilldowns: expanders with patient lists and quick actions ---
    st.markdown("### Doctor details")
    for s in doctor_stats:
        with st.expander(f"{s['doctor']} — Active: {s['active_cases']}  ·  Red: {s['red']}  ·  Load: {s['load_pct']}%"):
            # Show small doctor summary
            st.write(f"**Specialty:** {s['specialty']}  ·  **Avg response:** {s['avg_response_mins'] or '-'} mins")
            # Patients list
            if s["patients"]:
                for p in s["patients"]:
                    cols = st.columns([3, 1, 1, 1])
                    with cols[0]:
                        st.markdown(f"**{p['name']}**  \n`{p['id']}`  \n{p['village']}")
                    with cols[1]:
                        st.markdown(f"Risk: **{p['risk']}**")
                    with cols[2]:
                        st.markdown(f"Reported: {p['reported_time'].strftime('%Y-%m-%d %H:%M')}")
                    with cols[3]:
                        # Quick action: reassign to other doctor
                        new_doc = st.selectbox(f"Reassign_{p['id']}", options=["(keep)"] + doctors, index=0, key=f"reassign_{p['id']}")
                        if new_doc and new_doc != "(keep)":
                            # apply reassign to session_state dataset
                            for idx, rr in enumerate(st.session_state.case_rows):
                                if rr["id"] == p["id"]:
                                    st.session_state.case_rows[idx]["assigned_doctor"] = new_doc
                                    st.success(f"{p['name']} reassigned to {new_doc}")
                                    break
                            st.rerun()
            else:
                st.write("No patients assigned for selected date.")

    st.markdown("---")
    if st.button("← Back"):
        _set_patient_section("Patient_Dashboard")


def render_patient_doctor_drilldown():
    """
    Patient & Doctor Drilldown view.
    - Left: search + filters (Patient Name / ID, Risk, Village, Assigned Doctor)
    - Center: filtered patients list with per-row details, reassign and mark-resolved
    - Right: doctor selector: shows doctor stats, assigned patients, and CSV download
    """
    import streamlit as st
    import pandas as pd
    from datetime import datetime, timedelta
    from copy import deepcopy

    # --- sample fallback data if not present ---
    if "case_rows" not in st.session_state:
        now = datetime.now()
        st.session_state.case_rows = [
            {"id": "P-1001", "name": "Ravi Kumar", "age": 56, "gender": "M", "risk": "Red", "village": "Iskapalem",
             "reported_time": now - timedelta(hours=1, minutes=12), "assigned_doctor": None, "status": "open", "notes": ""},
            {"id": "P-1002", "name": "Sunita Devi", "age": 34, "gender": "F", "risk": "Amber", "village": "Mangalapet",
             "reported_time": now - timedelta(hours=3, minutes=5), "assigned_doctor": "Dr. A", "status": "open", "notes": ""},
            {"id": "P-1003", "name": "Karan Yadav", "age": 42, "gender": "M", "risk": "Green", "village": "Iskapalem",
             "reported_time": now - timedelta(days=1, hours=2), "assigned_doctor": "Dr. B", "status": "open", "notes": ""},
            {"id": "P-1004", "name": "Meena Thomas", "age": 29, "gender": "F", "risk": "Red", "village": "Padur",
             "reported_time": now - timedelta(minutes=40), "assigned_doctor": None, "status": "open", "notes": ""},
        ]

    if "doctors" not in st.session_state:
        st.session_state.doctors = [
            {"name": "Dr. A", "region": "North", "is_senior": False},
            {"name": "Dr. B", "region": "North", "is_senior": False},
            {"name": "Dr. C", "region": "South", "is_senior": True},
            {"name": "On-call", "region": "", "is_senior": False},
        ]

    # helper to get doctor name list
    def _doctor_names():
        return [d["name"] for d in st.session_state.doctors]

    # header
    st.header("🔎 Patient & Doctor Drilldown")
    st.caption("Search patients, view assigned doctor details and reassign quickly.")

    # top-level layout: filters + results + doctor panel
    left, center, right = st.columns([2, 3, 2])

    # ---- LEFT: search + filters ----
    with left:
        st.subheader("Search & Filters")
        q = st.text_input("Search (Patient name or ID)", value="", key="drill_q")
        risk_sel = st.multiselect("Risk", options=["Red", "Amber", "Green"], default=[], key="drill_risk")
        village_filter = st.text_input("Village contains", value="", key="drill_village")
        doctor_filter = st.selectbox("Assigned doctor", options=["(any)"] + _doctor_names(), index=0, key="drill_doc")
        status_filter = st.selectbox("Status", options=["(any)", "open", "resolved"], index=0, key="drill_status")
        st.markdown("### Actions")
        if st.button("Reset filters"):
            st.session_state["drill_q"] = ""
            st.session_state["drill_risk"] = []
            st.session_state["drill_village"] = ""
            st.session_state["drill_doc"] = "(any)"
            st.session_state["drill_status"] = "(any)"
            st.rerun()

    # ---- apply filters to case_rows ----
    rows = deepcopy(st.session_state.case_rows)
    def _match_row(r):
        if q and q.strip():
            qq = q.strip().lower()
            if qq not in r.get("name","").lower() and qq not in r.get("id","").lower():
                return False
        if risk_sel:
            if r.get("risk") not in risk_sel:
                return False
        if village_filter and village_filter.strip():
            if village_filter.strip().lower() not in r.get("village","").lower():
                return False
        if doctor_filter and doctor_filter != "(any)":
            if (r.get("assigned_doctor") or "(none)") != doctor_filter:
                return False
        if status_filter and status_filter != "(any)":
            if r.get("status") != status_filter:
                return False
        return True

    filtered = [r for r in rows if _match_row(r)]
    # allow sorting by reported_time (newest first)
    filtered = sorted(filtered, key=lambda x: x.get("reported_time", datetime.min), reverse=True)

    # ---- CENTER: filtered patient list + per-row details ----
    with center:
        st.subheader(f"Patients ({len(filtered)})")
        if filtered:
            # show quick table
            df = pd.DataFrame([{
                "id": r["id"],
                "name": r["name"],
                "age": r.get("age","-"),
                "gender": r.get("gender","-"),
                "risk": r.get("risk"),
                "village": r.get("village"),
                "assigned": r.get("assigned_doctor") or "-",
                "status": r.get("status","-"),
                "reported": r.get("reported_time").strftime("%Y-%m-%d %H:%M") if r.get("reported_time") else "-"
            } for r in filtered])
            st.dataframe(df, use_container_width=True)

            # per-row expander with actions
            st.markdown("---")
            for r in filtered:
                with st.expander(f"{r['name']}  —  {r['id']}  ·  Risk: {r.get('risk')}  ·  Assigned: {r.get('assigned_doctor') or '-'}", expanded=False):
                    col_a, col_b = st.columns([3,1])
                    with col_a:
                        st.markdown(f"**Name:** {r['name']}")
                        st.markdown(f"**Patient ID:** `{r['id']}`")
                        st.markdown(f"**Age / Gender:** {r.get('age','-')} / {r.get('gender','-')}")
                        st.markdown(f"**Village:** {r.get('village')}")
                        st.markdown(f"**Reported:** {r.get('reported_time').strftime('%Y-%m-%d %H:%M') if r.get('reported_time') else '-'}")
                        st.markdown(f"**Status:** {r.get('status','-')}")
                        st.markdown("**Notes:**")
                        st.write(r.get("notes","(no notes)"))
                        st.markdown("**Timeline / events**")
                        # placeholder timeline: reported + assigned events (expand as needed)
                        tl = []
                        tl.append({"event": "Reported", "when": r.get("reported_time").strftime("%Y-%m-%d %H:%M") if r.get("reported_time") else "-"})
                        if r.get("assigned_doctor"):
                            tl.append({"event": f"Assigned to {r.get('assigned_doctor')}", "when": "— (timestamp not tracked)"})
                        st.table(tl)
                    with col_b:
                        # Reassign control
                        doctors = ["(none)"] + _doctor_names()
                        current = r.get("assigned_doctor") or "(none)"
                        # unique key per patient
                        sel_key = f"reassign_select_{r['id']}"
                        new_doc = st.selectbox("Reassign to", options=doctors, index=(doctors.index(current) if current in doctors else 0), key=sel_key)
                        if st.button("Apply reassign", key=f"apply_reassign_{r['id']}"):
                            # update session_state
                            for idx, rr in enumerate(st.session_state.case_rows):
                                if rr.get("id") == r["id"]:
                                    st.session_state.case_rows[idx]["assigned_doctor"] = None if new_doc == "(none)" else new_doc
                                    st.success(f"{r['name']} reassigned to {new_doc if new_doc!='(none)' else 'no one'}")
                                    break
                            st.rerun()
                        if st.button("Mark resolved", key=f"mark_resolved_{r['id']}"):
                            for idx, rr in enumerate(st.session_state.case_rows):
                                if rr.get("id") == r["id"]:
                                    st.session_state.case_rows[idx]["status"] = "resolved"
                                    st.success(f"{r['name']} marked resolved")
                                    break
                            st.rerun()
                        if st.button("Add note", key=f"add_note_{r['id']}"):
                            # open small text_input modal-like via session key (simple approach)
                            txt = st.text_area("Enter note", key=f"note_input_{r['id']}")
                            if st.button("Save note", key=f"save_note_{r['id']}"):
                                for idx, rr in enumerate(st.session_state.case_rows):
                                    if rr.get("id") == r["id"]:
                                        existing = st.session_state.case_rows[idx].get("notes","")
                                        st.session_state.case_rows[idx]["notes"] = (existing + "\n" + txt).strip()
                                        st.success("Note saved")
                                        break
                                st.rerun()
        else:
            st.info("No patients match the current filters.")

        # CSV download for filtered list
        if filtered:
            df_down = pd.DataFrame([{
                "id": r["id"],
                "name": r["name"],
                "risk": r.get("risk"),
                "village": r.get("village"),
                "assigned": r.get("assigned_doctor") or "-",
                "status": r.get("status"),
                "reported": r.get("reported_time").strftime("%Y-%m-%d %H:%M") if r.get("reported_time") else "-"
            } for r in filtered])
            csv = df_down.to_csv(index=False).encode("utf-8")
            st.download_button("Download filtered patients (CSV)", data=csv, file_name="patients_filtered.csv", mime="text/csv")

    # ---- RIGHT: doctor drilldown panel ----
    with right:
        st.subheader("Doctor view")
        doctors = _doctor_names()
        sel_doc = st.selectbox("Select doctor", options=["(any)"] + doctors, index=0, key="drill_doc_view")
        if sel_doc and sel_doc != "(any)":
            # compute stats for this doctor
            assigned = [r for r in st.session_state.case_rows if r.get("assigned_doctor") == sel_doc]
            active = len(assigned)
            red = sum(1 for r in assigned if r.get("risk") == "Red")
            amber = sum(1 for r in assigned if r.get("risk") == "Amber")
            green = sum(1 for r in assigned if r.get("risk") == "Green")

            st.markdown(f"**Doctor:** {sel_doc}")
            st.metric("Active cases", active)
            st.markdown(f"Red: **{red}** · Amber: **{amber}** · Green: **{green}**")

            if assigned:
                st.markdown("**Assigned patients**")
                df_doc = pd.DataFrame([{
                    "id": r["id"], "name": r["name"], "risk": r.get("risk"), "village": r.get("village"),
                    "status": r.get("status"), "reported": r.get("reported_time").strftime("%Y-%m-%d %H:%M")
                } for r in assigned])
                st.dataframe(df_doc, use_container_width=True)

                # Download CSV of assigned patients
                csv2 = df_doc.to_csv(index=False).encode("utf-8")
                st.download_button("Download assigned patients (CSV)", data=csv2, file_name=f"{sel_doc}_assigned.csv", mime="text/csv")
                # Quick action: bulk reassign all to another doctor
                st.markdown("**Bulk actions**")
                target = st.selectbox("Reassign all to", options=["(none)"] + doctors, index=0, key="bulk_reassign_target")
                if st.button("Reassign all"):
                    if target == "(none)":
                        st.warning("Pick a doctor to reassign to.")
                    else:
                        count = 0
                        for idx, rr in enumerate(st.session_state.case_rows):
                            if rr.get("assigned_doctor") == sel_doc:
                                st.session_state.case_rows[idx]["assigned_doctor"] = target
                                count += 1
                        st.success(f"Reassigned {count} patient(s) from {sel_doc} to {target}.")
                        st.rerun()
            else:
                st.info("No patients assigned to this doctor.")
        else:
            st.info("Select a doctor to view assigned patients and stats.")

    # Footer back button
    st.markdown("---")
    if st.button("← Back"):
        _set_patient_section("Patient_Dashboard")




# def render_doctor_assignment_rules():
    # """
    # Doctor Assignment Rules UI
    # - Manage rules (create, edit, delete)
    # - Preview matched patients for a rule
    # - Bulk assign matched patients to a doctor based on the rule
    # """
    # import streamlit as st
    # from datetime import datetime
    # from copy import deepcopy
    # from pathlib import Path

    # # --- initialize storage for rules ---
    # if "assignment_rules" not in st.session_state:
        # # sample starter rules (id is integer)
        # st.session_state.assignment_rules = [
            # {
                # "id": 1,
                # "name": "High priority red cases",
                # "specialty": "General",
                # "priority": 1,
                # "risk_levels": ["Red"],
                # "villages": ["Iskapalem"],
                # "max_active_cases": 5,
                # "default_doctor": "Dr. A",
                # "active": True,
                # "created_at": datetime.now().isoformat()
            # },
        # ]
        # st.session_state._next_rule_id = 2

    # # Helper to persist new id
    # def _next_rule_id():
        # if "_next_rule_id" not in st.session_state:
            # st.session_state._next_rule_id = max((r["id"] for r in st.session_state.assignment_rules), default=0) + 1
        # val = st.session_state._next_rule_id
        # st.session_state._next_rule_id += 1
        # return val

    # # Utility: find doctors list from current data or fallback
    # def _doctor_list():
        # docs = sorted({r["assigned_doctor"] for r in st.session_state.get("case_rows", []) if r.get("assigned_doctor")})
        # if not docs:
            # return ["Dr. A", "Dr. B", "Dr. C", "On-call"]
        # return docs

    # st.header("⚖️ Doctor Assignment Rules")
    # st.caption("Create and manage rules that decide which doctor a case should be assigned to.")

    # # Layout: left = rules list, right = create/edit form & preview
    # left, right = st.columns([2, 3])

    # # --- Left: rules list with edit/delete ---
    # with left:
        # st.subheader("Existing rules")
        # rules = st.session_state.assignment_rules
        # if not rules:
            # st.info("No rules defined yet.")
        # else:
            # # Display compact table of rules
            # quick_rows = [
                # {
                    # "id": r["id"],
                    # "name": r["name"],
                    # "priority": r.get("priority", ""),
                    # "risk": ",".join(r.get("risk_levels", [])),
                    # "villages": ",".join(r.get("villages", [])),
                    # "default_doc": r.get("default_doctor", ""),
                    # "active": "Yes" if r.get("active") else "No"
                # }
                # for r in rules
            # ]
            # st.table(quick_rows)

            # # Select a rule to edit / preview / delete
            # sel_id = st.selectbox("Select rule to manage", options=[r["id"] for r in rules], format_func=lambda x: next((rr["name"] for rr in rules if rr["id"]==x), str(x)))
            # sel_rule = next((r for r in rules if r["id"] == sel_id), None)

            # if sel_rule:
                # st.markdown("**Rule details**")
                # st.write(sel_rule)

                # col_e1, col_e2 = st.columns([1,1])
                # with col_e1:
                    # if st.button("Edit selected"):
                        # # copy to edit buffer
                        # st.session_state["_editing_rule"] = deepcopy(sel_rule)
                        # # show edit form on right via flag
                        # st.session_state["_show_edit_form"] = True
                        # st.rerun()
                # with col_e2:
                    # if st.button("Delete selected"):
                        # # confirm delete
                        # if st.confirm(f"Are you sure you want to delete rule '{sel_rule['name']}'?"):
                            # st.session_state.assignment_rules = [r for r in st.session_state.assignment_rules if r["id"] != sel_rule["id"]]
                            # st.success("Rule deleted.")
                            # st.rerun()

    # # --- Right: create / edit form ---
    # with right:
        # st.subheader("Create new rule")

        # # If editing, pre-fill form with the editing buffer
        # editing = False
        # edit_buf = None
        # if st.session_state.get("_show_edit_form") and st.session_state.get("_editing_rule"):
            # editing = True
            # edit_buf = st.session_state["_editing_rule"]

        # # Use a form so Save happens atomically
        # form_key = "assignment_rule_form_edit" if editing else "assignment_rule_form_new"
        # with st.form(form_key, clear_on_submit=not editing):
            # if editing:
                # st.markdown(f"**Editing rule:** {edit_buf['name']}")
                # name = st.text_input("Rule name", value=edit_buf.get("name", ""))
                # priority = st.number_input("Priority (lower = higher priority)", min_value=1, max_value=100, value=edit_buf.get("priority", 1))
                # specialty = st.text_input("Specialty (optional)", value=edit_buf.get("specialty", ""))
                # risk_levels = st.multiselect("Risk levels to match", options=["Red","Amber","Green"], default=edit_buf.get("risk_levels", []))
                # villages = st.text_input("Villages (comma separated)", value=",".join(edit_buf.get("villages", [])))
                # max_active = st.number_input("Max active cases for doctor (0 = unlimited)", min_value=0, value=edit_buf.get("max_active_cases", 0))
                # default_doc = st.selectbox("Default doctor to assign", options=["(none)"] + _doctor_list(), index=(0 if not edit_buf.get("default_doctor") else (_doctor_list().index(edit_buf.get("default_doctor"))+1) if edit_buf.get("default_doctor") in _doctor_list() else 0))
                # active = st.checkbox("Rule active", value=bool(edit_buf.get("active", True)))
            # else:
                # name = st.text_input("Rule name")
                # priority = st.number_input("Priority (lower = higher priority)", min_value=1, max_value=100, value=10)
                # specialty = st.text_input("Specialty (optional)")
                # risk_levels = st.multiselect("Risk levels to match", options=["Red","Amber","Green"], default=[])
                # villages = st.text_input("Villages (comma separated)")
                # max_active = st.number_input("Max active cases for doctor (0 = unlimited)", min_value=0, value=0)
                # default_doc = st.selectbox("Default doctor to assign", options=["(none)"] + _doctor_list(), index=0)
                # active = st.checkbox("Rule active", value=True)

            # save = st.form_submit_button("Save rule")
            # if save:
                # villages_list = [v.strip() for v in villages.split(",") if v.strip()]
                # if editing:
                    # # update the rule in session_state
                    # for idx, r in enumerate(st.session_state.assignment_rules):
                        # if r["id"] == edit_buf["id"]:
                            # st.session_state.assignment_rules[idx].update({
                                # "name": name,
                                # "priority": int(priority),
                                # "specialty": specialty,
                                # "risk_levels": risk_levels,
                                # "villages": villages_list,
                                # "max_active_cases": int(max_active),
                                # "default_doctor": None if default_doc == "(none)" else default_doc,
                                # "active": bool(active),
                            # })
                            # break
                    # # clear editing buffer
                    # st.session_state.pop("_editing_rule", None)
                    # st.session_state.pop("_show_edit_form", None)
                    # st.success("Rule updated.")
                    # st.rerun()
                # else:
                    # new_rule = {
                        # "id": _next_rule_id(),
                        # "name": name or f"Rule {datetime.now().isoformat()}",
                        # "priority": int(priority),
                        # "specialty": specialty,
                        # "risk_levels": risk_levels,
                        # "villages": villages_list,
                        # "max_active_cases": int(max_active),
                        # "default_doctor": None if default_doc == "(none)" else default_doc,
                        # "active": bool(active),
                        # "created_at": datetime.now().isoformat()
                    # }
                    # st.session_state.assignment_rules.append(new_rule)
                    # st.success("Rule created.")
                    # st.rerun()

        # st.markdown("---")
        # st.subheader("Preview & apply a rule")

        # # Choose a rule to preview (reuse rules list)
        # rule_opts = st.session_state.assignment_rules
        # if not rule_opts:
            # st.info("No rules to preview.")
            # return

        # preview_choice = st.selectbox("Choose rule to preview", options=[r["id"] for r in rule_opts], format_func=lambda x: next((rr["name"] for rr in rule_opts if rr["id"]==x), str(x)))
        # rule = next((r for r in rule_opts if r["id"] == preview_choice), None)

        # if not rule:
            # st.warning("Selected rule not found.")
            # return

        # st.markdown(f"**Previewing:** {rule['name']}  ·  Priority {rule['priority']}  ·  Active: {'Yes' if rule['active'] else 'No'}")

        # # Build matching logic on current case_rows
        # case_rows = st.session_state.get("case_rows", [])
        # def matches_rule(case, rule):
            # if not rule.get("active", True):
                # return False
            # # risk filter
            # if rule.get("risk_levels"):
                # if case.get("risk") not in rule["risk_levels"]:
                    # return False
            # # villages
            # if rule.get("villages"):
                # if case.get("village", "").strip() not in rule["villages"]:
                    # return False
            # # specialty filter (skip here, as sample cases don't have specialty)
            # # other checks may go here
            # return True

        # matched = [c for c in case_rows if matches_rule(c, rule)]

        # st.write(f"Matched **{len(matched)}** patient(s) for this rule.")
        # if matched:
            # # show simple table of matched patients
            # display = [{"id": m["id"], "name": m["name"], "risk": m["risk"], "village": m["village"], "reported": m["reported_time"].strftime("%Y-%m-%d %H:%M"), "assigned": m.get("assigned_doctor") or "-"} for m in matched]
            # st.table(display)

            # # Option to assign matched patients to a doctor
            # assign_to = st.selectbox("Assign matched patients to doctor", options=["(keep)"] + _doctor_list(), index=0)
            # if st.button("Assign matched patients"):
                # if assign_to == "(keep)":
                    # st.warning("Pick a doctor to assign (or set default doctor in the rule).")
                # else:
                    # count = 0
                    # for idx, rr in enumerate(st.session_state.case_rows):
                        # if rr["id"] in [m["id"] for m in matched]:
                            # st.session_state.case_rows[idx]["assigned_doctor"] = assign_to
                            # count += 1
                    # st.success(f"Assigned {count} patient(s) to {assign_to}.")
                    # st.rerun()

        # else:
            # st.info("No matching patients found for current rule and data.")

    # # Footer back button
    # st.markdown("---")
    # if st.button("← Back"):
        # _set_patient_section("Patient_Dashboard")

def render_doctor_assignment_rules():
    """
    Enhanced Doctor Assignment Rules screen (robust).
    Normalizes older rules (fills missing keys) and avoids KeyError by using .get().
    """
    import streamlit as st
    from datetime import datetime, timedelta
    from copy import deepcopy

    # --- Ensure sample doctors & cases exist (only if real data isn't present) ---
    if "doctors" not in st.session_state:
        st.session_state.doctors = [
            {"name": "Dr. A", "region": "North", "is_senior": False},
            {"name": "Dr. B", "region": "North", "is_senior": False},
            {"name": "Dr. C", "region": "South", "is_senior": False},
            {"name": "Dr. Senior", "region": "North", "is_senior": True},
            {"name": "On-call", "region": "", "is_senior": False},
        ]

    if "case_rows" not in st.session_state:
        now = datetime.now()
        st.session_state.case_rows = [
            {"id": "P-1001", "name": "Ravi Kumar", "risk": "Red", "village": "Iskapalem", "reported_time": now - timedelta(hours=3), "assigned_doctor": None},
            {"id": "P-1002", "name": "Sunita Devi", "risk": "Amber", "village": "Mangalapet", "reported_time": now - timedelta(hours=5), "assigned_doctor": "Dr. A"},
            {"id": "P-1003", "name": "Karan Yadav", "risk": "Green", "village": "Iskapalem", "reported_time": now - timedelta(hours=26), "assigned_doctor": "Dr. B"},
            {"id": "P-1004", "name": "Meena Thomas", "risk": "Red", "village": "Padur", "reported_time": now - timedelta(minutes=40), "assigned_doctor": None},
        ]

    # ensure assignment_rules storage
    if "assignment_rules" not in st.session_state:
        st.session_state.assignment_rules = []
        st.session_state._next_rule_id = 1
    if "_rr_counters" not in st.session_state:
        st.session_state._rr_counters = {}  # rule_id -> counter int

    # --- NORMALIZE existing rules: fill default fields to avoid KeyError ---
    def _normalize_rules():
        changed = False
        for idx, r in enumerate(st.session_state.assignment_rules):
            # defaults
            default = {
                "type": "Default",
                "region": "",
                "active": True,
                "mapping": {"Red": {"mode": "Workload balance", "doctor": None},
                            "Amber": {"mode": "Workload balance", "doctor": None},
                            "Green": {"mode": "Workload balance", "doctor": None}},
                "max_active_cases": 0,
                "reassign_after_hours": 0,
                "rr_scope": "All doctors",
                "created_at": datetime.now().isoformat(),
            }
            # if mapping exists but missing risk keys, fill them
            merged = {}
            merged.update(default)
            merged.update(r)  # r overrides defaults
            # ensure mapping shape
            mapping = merged.get("mapping") or {}
            for risk in ["Red", "Amber", "Green"]:
                if risk not in mapping:
                    mapping[risk] = {"mode": "Workload balance", "doctor": None}
                else:
                    # ensure each mapping entry has mode and doctor keys
                    mapping[risk].setdefault("mode", "Workload balance")
                    mapping[risk].setdefault("doctor", None)
            merged["mapping"] = mapping
            # write back only if changed to avoid unnecessary reruns
            if merged != r:
                st.session_state.assignment_rules[idx] = merged
                changed = True
        return changed

    _normalize_rules()

    def _next_rule_id():
        if "_next_rule_id" not in st.session_state:
            st.session_state._next_rule_id = max((r.get("id", 0) for r in st.session_state.assignment_rules), default=0) + 1
        val = st.session_state._next_rule_id
        st.session_state._next_rule_id += 1
        return val

    # helper: get doctor names filtered by region (if region empty, all)
    def _doctor_names_in_region(region=None):
        docs = st.session_state.doctors
        if region and region.strip():
            return [d["name"] for d in docs if d.get("region", "").strip().lower() == region.strip().lower()]
        else:
            return [d["name"] for d in docs]

    # compute active case counts per doctor
    def _active_counts():
        counts = {}
        for d in _doctor_names_in_region(None):
            counts[d] = sum(1 for c in st.session_state.case_rows if c.get("assigned_doctor") == d)
        return counts

    st.header("⚖️ Doctor Assignment Rules (Robust)")

    # Layout: left = rules list, right = rule editor / preview
    left, right = st.columns([2, 4])

    # ---- Left panel: list / manage rules ----
    with left:
        st.subheader("Rule set")
        if not st.session_state.assignment_rules:
            st.info("No rules defined yet. Create one on the right.")
        else:
            view = []
            for r in st.session_state.assignment_rules:
                view.append({
                    "id": r.get("id"),
                    "name": r.get("name"),
                    "type": r.get("type", "Default"),
                    "region": r.get("region", "-"),
                    "active": "Yes" if r.get("active", True) else "No"
                })
            st.table(view)

        st.markdown("**Manage rules**")
        rule_ids = [r.get("id") for r in st.session_state.assignment_rules if r.get("id") is not None]
        if rule_ids:
            sel = st.selectbox("Select rule to edit / delete", options=[None] + rule_ids, format_func=lambda x: ("New rule" if x is None else next((rr.get("name") for rr in st.session_state.assignment_rules if rr.get("id")==x), str(x))))
            if sel:
                sel_rule = next((rr for rr in st.session_state.assignment_rules if rr.get("id") == sel), None)
                if sel_rule:
                    if st.button("Delete selected rule"):
                        if st.checkbox("Confirm delete"):
                            st.session_state.assignment_rules = [rr for rr in st.session_state.assignment_rules if rr.get("id") != sel_rule.get("id")]
                            st.success("Rule deleted.")
                            st.rerun()
                    if st.button("Duplicate selected rule"):
                        new = deepcopy(sel_rule)
                        new["id"] = _next_rule_id()
                        new["name"] = sel_rule.get("name","") + " (copy)"
                        st.session_state.assignment_rules.append(new)
                        st.success("Rule duplicated.")
                        st.rerun()

    # ---- Right panel: create/edit form ----
    with right:
        st.subheader("Create / Edit rule")

        editing = False
        edit_buf = None
        edit_choice = st.selectbox("Pick a rule to edit (or choose New)", options=[None] + [r.get("id") for r in st.session_state.assignment_rules], format_func=lambda x: ("New rule" if x is None else next((rr.get("name") for rr in st.session_state.assignment_rules if rr.get("id")==x), str(x))))
        if edit_choice:
            editing = True
            edit_buf = deepcopy(next((rr for rr in st.session_state.assignment_rules if rr.get("id") == edit_choice), {}))

        with st.form(key="rule_form", clear_on_submit=False):
            name = st.text_input("Rule name", value=edit_buf.get("name","") if editing else "")
            rtype = st.selectbox("Rule type", options=["Default", "Region"], index=(0 if not editing else (0 if edit_buf.get("type","Default")=="Default" else 1)))
            region = st.text_input("Region (when Rule type = Region)", value=edit_buf.get("region","") if editing else "")
            active = st.checkbox("Active", value=edit_buf.get("active", True) if editing else True)
            st.markdown("**Per-risk assignment mapping**")
            choices = ["Workload balance", "Fixed doctor", "Round-robin"]
            mapping = {}
            for risk in ["Red", "Amber", "Green"]:
                st.markdown(f"**{risk}**")
                default_mode = edit_buf.get("mapping", {}).get(risk, {}).get("mode", "Workload balance") if editing else "Workload balance"
                mode = st.selectbox(f"Mode_{risk}", options=choices, index=choices.index(default_mode), key=f"mode_{risk}")
                fixed_doc = None
                if mode == "Fixed doctor":
                    doctors_list = ["(none)"] + _doctor_names_in_region(region if rtype=="Region" else None)
                    pre_sel = edit_buf.get("mapping", {}).get(risk, {}).get("doctor") if editing else "(none)"
                    # convert pre_sel to index safely
                    try:
                        idx = doctors_list.index(pre_sel) if pre_sel in doctors_list else 0
                    except Exception:
                        idx = 0
                    fixed_doc = st.selectbox(f"Doctor_{risk}", options=doctors_list, index=idx, key=f"fixed_{risk}")
                else:
                    fixed_doc = None
                mapping[risk] = {"mode": mode, "doctor": (None if fixed_doc in [None,"(none)"] else fixed_doc)}

            st.markdown("**Auto-assign policy / constraints**")
            max_active_cases = st.number_input("Max active cases per doctor (0 = no limit)", min_value=0, value=edit_buf.get("max_active_cases", 0) if editing else 0)
            reassign_after_hours = st.number_input("Reassign if assigned > (hours) (0 = disabled)", min_value=0, value=edit_buf.get("reassign_after_hours", 0) if editing else 0)
            rr_scope = st.selectbox("Round-robin scope", options=["All doctors", "Doctors in region"], index=0 if not editing else (0 if edit_buf.get("rr_scope","All doctors")=="All doctors" else 1))

            saved = st.form_submit_button("Save rule")
            if saved:
                rule_obj = {
                    "id": (edit_choice if editing else _next_rule_id()),
                    "name": name or f"Rule {datetime.now().isoformat()}",
                    "type": rtype,
                    "region": region,
                    "active": bool(active),
                    "mapping": mapping,
                    "max_active_cases": int(max_active_cases),
                    "reassign_after_hours": int(reassign_after_hours),
                    "rr_scope": rr_scope,
                    "created_at": datetime.now().isoformat()
                }
                if editing:
                    for idx, rr in enumerate(st.session_state.assignment_rules):
                        if rr.get("id") == edit_choice:
                            st.session_state.assignment_rules[idx] = rule_obj
                            break
                    st.success("Rule updated.")
                else:
                    st.session_state.assignment_rules.append(rule_obj)
                    st.success("Rule created.")
                st.rerun()

        st.markdown("---")

        # Preview & apply part
        st.subheader("Preview / Apply rule")

        if not st.session_state.assignment_rules:
            st.info("No rules to preview.")
            return

        preview_id = st.selectbox("Select rule to preview", options=[r.get("id") for r in st.session_state.assignment_rules], format_func=lambda x: next((rr.get("name") for rr in st.session_state.assignment_rules if rr.get("id")==x), str(x)))
        rule = next((rr for rr in st.session_state.assignment_rules if rr.get("id") == preview_id), None)
        if not rule:
            st.warning("Pick a valid rule")
            return

        st.markdown(f"**Previewing:** {rule.get('name')} · Type: {rule.get('type','Default')} · Region: {rule.get('region') or '-'} · Active: {'Yes' if rule.get('active') else 'No'}")

        # Matching logic
        def _matches_rule(case, rule):
            if not rule.get("active", True):
                return False
            if rule.get("type") == "Region" and rule.get("region"):
                if rule["region"].strip().lower() not in case.get("village", "").strip().lower():
                    return False
            return True

        matched = [c for c in st.session_state.case_rows if _matches_rule(c, rule)]
        st.write(f"Matched **{len(matched)}** case(s).")
        if matched:
            st.table([{"id": m.get("id"), "name": m.get("name"), "risk": m.get("risk"), "village": m.get("village"), "assigned": m.get("assigned_doctor") or "-", "reported": m.get("reported_time").strftime("%Y-%m-%d %H:%M")} for m in matched])

        st.markdown("**Simulate / Apply**")
        apply_choice = st.selectbox("Assignment target option", options=["Simulate (no change)", "Apply assignments (persist)"])
        if st.button("Run rule now"):
            active_counts = _active_counts()
            def pick_doctor_for_case(case, rule):
                risk = case.get("risk")
                mapping = rule.get("mapping", {})
                m = mapping.get(risk, {"mode": "Workload balance", "doctor": None})
                mode = m.get("mode")
                fixed_doc = m.get("doctor")
                if rule.get("type") == "Region" and rule.get("region"):
                    pool = _doctor_names_in_region(rule.get("region"))
                else:
                    pool = _doctor_names_in_region(None)
                if not pool:
                    pool = [d["name"] for d in st.session_state.doctors]
                if mode == "Workload balance":
                    pool_sorted = sorted(pool, key=lambda dd: active_counts.get(dd, 0))
                    for cand in pool_sorted:
                        if rule.get("max_active_cases", 0) > 0:
                            if active_counts.get(cand, 0) < rule.get("max_active_cases", 0):
                                return cand
                        else:
                            return cand
                    return pool_sorted[0] if pool_sorted else None
                if mode == "Fixed doctor":
                    if fixed_doc and fixed_doc in pool:
                        if rule.get("max_active_cases", 0) > 0 and active_counts.get(fixed_doc, 0) >= rule.get("max_active_cases", 0):
                            return pick_doctor_for_case(case, {**rule, "mapping": {risk: {"mode":"Workload balance"}}})
                        return fixed_doc
                    else:
                        return pick_doctor_for_case(case, {**rule, "mapping": {risk: {"mode":"Workload balance"}}})
                if mode == "Round-robin":
                    key = str(rule.get("id"))
                    pool_rr = pool[:]
                    if not pool_rr:
                        return None
                    idx = st.session_state._rr_counters.get(key, 0) % len(pool_rr)
                    chosen = pool_rr[idx]
                    st.session_state._rr_counters[key] = (st.session_state._rr_counters.get(key, 0) + 1) % max(1, len(pool_rr))
                    return chosen
                return None

            def needs_escalation(case, rule):
                if rule.get("reassign_after_hours", 0) <= 0:
                    return False
                assigned = case.get("assigned_doctor")
                if not assigned:
                    return False
                rt = case.get("reported_time")
                if not rt:
                    return False
                hours = (datetime.now() - rt).total_seconds() / 3600.0
                return hours > rule.get("reassign_after_hours", 0)

            seniors = [d["name"] for d in st.session_state.doctors if d.get("is_senior")]

            changes = []
            for case in matched:
                if needs_escalation(case, rule) and seniors:
                    target = seniors[0]
                else:
                    target = pick_doctor_for_case(case, rule)
                    if not target:
                        if seniors:
                            target = seniors[0]
                        else:
                            all_names = [d["name"] for d in st.session_state.doctors]
                            target = all_names[0] if all_names else None
                if not target:
                    continue
                if apply_choice == "Apply assignments (persist)":
                    for idx, rr in enumerate(st.session_state.case_rows):
                        if rr.get("id") == case.get("id"):
                            prev = st.session_state.case_rows[idx].get("assigned_doctor")
                            st.session_state.case_rows[idx]["assigned_doctor"] = target
                            active_counts[target] = active_counts.get(target, 0) + (0 if prev == target else 1)
                            changes.append((case.get("id"), prev, target))
                            break
                else:
                    changes.append((case.get("id"), case.get("assigned_doctor"), target))

            if not changes:
                st.info("No assignments made/simulated (no matched cases or no eligible doctors).")
            else:
                if apply_choice == "Apply assignments (persist)":
                    st.success(f"Assigned {len(changes)} case(s) according to rule '{rule.get('name')}'")
                else:
                    st.info(f"Simulated {len(changes)} assignments (no changes persisted).")
                summary = []
                for cid, prev, new in changes:
                    summary.append({"case_id": cid, "previous": prev or "-", "assigned_to": new or "-"})
                st.table(summary)
                if apply_choice == "Apply assignments (persist)":
                    st.rerun()

        if st.button("← Back"):
            _set_patient_section("Patient_Dashboard")

# -----------------------------
# Case Allocation (full implementation)
# -----------------------------
def render_case_allocation_screen():
    """
    Interactive Case Allocation screen.
    - Search by patient name / id
    - Filters: Risk (Red/Amber/Green), Village
    - Case queue table with per-row and bulk doctor assignment
    """

    # -- In-memory sample dataset (replace with DB calls) --
    if "case_rows" not in st.session_state:
        now = datetime.now()
        st.session_state.case_rows = [
            {
                "id": "P-1001",
                "name": "Ravi Kumar",
                "age": 56,
                "gender": "M",
                "risk": "Red",
                "village": "Iskapalem",
                "reported_time": now - timedelta(hours=1, minutes=12),
                "rmp_proposed": "Dr. A",
                "assigned_doctor": None,
            },
            {
                "id": "P-1002",
                "name": "Sunita Devi",
                "age": 34,
                "gender": "F",
                "risk": "Amber",
                "village": "Mangalapet",
                "reported_time": now - timedelta(hours=3, minutes=5),
                "rmp_proposed": None,
                "assigned_doctor": None,
            },
            {
                "id": "P-1003",
                "name": "Karan Yadav",
                "age": 42,
                "gender": "M",
                "risk": "Green",
                "village": "Iskapalem",
                "reported_time": now - timedelta(days=1, hours=2),
                "rmp_proposed": "Dr. B",
                "assigned_doctor": "Dr. B",
            },
            {
                "id": "P-1004",
                "name": "Meena Thomas",
                "age": 29,
                "gender": "F",
                "risk": "Red",
                "village": "Padur",
                "reported_time": now - timedelta(minutes=40),
                "rmp_proposed": None,
                "assigned_doctor": None,
            },
        ]

    doctors = ["Dr. A", "Dr. B", "Dr. C", "On-call"]

    st.header("🗂️ Case Allocation")
    st.caption("Search and assign doctors to cases. Use bulk actions for many cases.")

    # Search & filter form
    with st.form(key="case_filters", clear_on_submit=False):
        cols = st.columns([2, 1, 1, 1])
        with cols[0]:
            search_text = st.text_input("Search (Patient Name / ID)", value="")
        with cols[1]:
            risk_filter = st.multiselect("Risk", options=["Red", "Amber", "Green"], default=[])
        with cols[2]:
            village_filter = st.text_input("Village", value="")
        with cols[3]:
            age_gender = st.selectbox("Age/Gender", options=["Any", "Age>50", "Male", "Female"], index=0)

        submitted = st.form_submit_button("Apply")
        if submitted:
            pass

    st.markdown("---")

    # Apply filters
    rows = st.session_state.case_rows.copy()

    def matches_filters(r):
        q = search_text.strip().lower()
        if q:
            if q not in r["name"].lower() and q not in r["id"].lower():
                return False
        if risk_filter:
            if r["risk"] not in risk_filter:
                return False
        if village_filter.strip():
            if village_filter.strip().lower() not in r["village"].lower():
                return False
        if age_gender != "Any":
            if age_gender == "Age>50" and r["age"] <= 50:
                return False
            if age_gender == "Male" and r["gender"] != "M":
                return False
            if age_gender == "Female" and r["gender"] != "F":
                return False
        return True

    filtered = [r for r in rows if matches_filters(r)]

    st.write(f"Showing **{len(filtered)}** case(s).")

    # selection state
    if "case_selected" not in st.session_state:
        st.session_state.case_selected = {r["id"]: False for r in st.session_state.case_rows}

    # select-all toggle (applies to currently visible rows)
    sel_all = st.checkbox("Select all visible", value=all(st.session_state.case_selected.get(r["id"], False) for r in filtered))
    if sel_all:
        for r in filtered:
            st.session_state.case_selected[r["id"]] = True

    # Render rows
    for r in filtered:
        rid = r["id"]
        row_cols = st.columns([0.6, 2.2, 1.0, 1.0, 1.0, 1.4, 1.8])
        with row_cols[0]:
            st.session_state.case_selected[rid] = st.checkbox("", value=st.session_state.case_selected.get(rid, False), key=f"chk_{rid}")
        with row_cols[1]:
            st.markdown(f"**{r['name']}**  \n`{r['id']}`  \nAge: {r['age']} / {r['gender']}")
        with row_cols[2]:
            st.markdown(f"**Risk:**  \n{r['risk']}")
        with row_cols[3]:
            st.markdown(f"**Village:**  \n{r['village']}")
        with row_cols[4]:
            st.markdown(f"**Reported:**  \n{r['reported_time'].strftime('%Y-%m-%d %H:%M')}")
        with row_cols[5]:
            st.markdown(f"**RMP Proposed:**  \n{r['rmp_proposed'] or '-'}")
        with row_cols[6]:
            sel_doc = st.selectbox("Assign", options=["(none)"] + doctors, index=(0 if not r.get("assigned_doctor") else doctors.index(r["assigned_doctor"]) + 1), key=f"sel_{rid}")
            if st.button("Apply", key=f"apply_{rid}"):
                for idx, rr in enumerate(st.session_state.case_rows):
                    if rr["id"] == rid:
                        st.session_state.case_rows[idx]["assigned_doctor"] = None if sel_doc == "(none)" else sel_doc
                        break
                st.success(f"Assigned {sel_doc} to {r['name']}")
                st.rerun()

    st.markdown("---")

    # Bulk actions
    st.subheader("Bulk Actions")
    bcols = st.columns([2, 1, 1, 1])
    with bcols[0]:
        selected_ids = [rid for rid, sel in st.session_state.case_selected.items() if sel]
        st.write(f"Selected: **{len(selected_ids)}**")
    with bcols[1]:
        bulk_doc = st.selectbox("Assign doctor to selected", options=["(none)"] + doctors, index=0, key="bulk_doc_select")
    with bcols[2]:
        if st.button("Assign to selected"):
            if not selected_ids:
                st.warning("No cases selected.")
            else:
                for idx, rr in enumerate(st.session_state.case_rows):
                    if rr["id"] in selected_ids:
                        st.session_state.case_rows[idx]["assigned_doctor"] = None if bulk_doc == "(none)" else bulk_doc
                st.success(f"Assigned {bulk_doc} to {len(selected_ids)} case(s).")
                for sid in selected_ids:
                    st.session_state.case_selected[sid] = False
                st.rerun()
    with bcols[3]:
        if st.button("Clear selections"):
            for k in st.session_state.case_selected.keys():
                st.session_state.case_selected[k] = False
            st.success("Selections cleared.")
            st.rerun()

    st.markdown("---")
    if st.button("← Back"):
        _set_patient_section("Patient_Dashboard")


# -----------------------------
# Main patient dashboard (entry)
# -----------------------------
def render_patient_dashboard(user: dict):
    """
    Patient dashboard entry. Hides the left sidebar and shows:
      - Welcome header (left)
      - Logo (center)
      - Logout (right)
      - KPI cards row (My Appointments, Lab Reports, Prescriptions) matching rmp styles
    """
    _ensure_patient_section_state()

    # add this line (paste it here)
    #maybe_show_sample_loader()
    
    # ----- Hide left sidebar (so the left logout button from root app.py is not visible)
    # This CSS only applies while this function renders (scoped injection).
    # Note: it hides the entire Streamlit sidebar — root app.py still creates it,
    # but this makes it not visible to the user for Patient role (as you requested).
    st.markdown(
        """
        <style>
        /* hide Streamlit sidebar (left) when viewing patient dashboard */
        section[data-testid="stSidebar"] {
            display:none !important;
        }
        /* allow main content to use full width */
        .block-container {
            padding-left: 2rem !important;
            padding-right: 2rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Header: welcome left, logo center, logout right
    col1, col2, col3 = st.columns([1, 2, 1])

    # Left: welcome
    with col1:
        st.markdown(
            f"""
            <div style="height:100%; display:flex; flex-direction:column; justify-content:center;">
                <div style="font-size:20px; font-weight:700;">Welcome, {user.get('name','Patient')}</div>
                <div style="color: #6b7280;">{date.today().strftime('%b %d, %Y')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Center: logo (best-effort)
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
    with col2:
        if found_logo:
            try:
                st.image(found_logo, use_container_width=True, width=160)
            except Exception:
                st.info("Logo found but could not be displayed.")
        else:
            st.markdown(
                "<div style='height:100%;display:flex;align-items:center;justify-content:center;color:#6b7280;'>Logo</div>",
                unsafe_allow_html=True,
            )

    # Right: logout (top)
    with col3:
        st.markdown("<div style='height:100%; display:flex; align-items:center; justify-content:center;'>", unsafe_allow_html=True)
        if st.button("Logout", key="patient_logout_top", use_container_width=True):
            # clear session except theme
            keep = {"theme"}
            for k in list(st.session_state.keys()):
                if k not in keep:
                    del st.session_state[k]
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    # ---- KPI row styled like the third screenshot (uses classes from style.css) ----
    # We render three kpi cards using the existing CSS classes in your static/style.css.
    c1, c2, c3 = st.columns(3, gap="large")
    with c1:
        st.markdown(
            """
            <div class="rmp-card kpi-card" style="height:auto;">
              <div class="kpi-title">My Appointments</div>
              <div class="kpi-value">3</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            """
            <div class="rmp-card kpi-card" style="height:auto;">
              <div class="kpi-title">Lab Reports</div>
              <div class="kpi-value">5</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            """
            <div class="rmp-card kpi-card" style="height:auto;">
              <div class="kpi-title">Prescriptions</div>
              <div class="kpi-value">2</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")  # small gap

    # --- preserve existing routing/tile grid below ---
    section = st.session_state.get("patient_section", "Patient_Dashboard")

    if section == "Patient_Dashboard":
        # Tiles grid (2 columns)
        c1, c2 = st.columns(2)
        with c1:
            _patient_tile_button("🗂️", "Case Allocation", "", "Case_Allocation")
        with c2:
            _patient_tile_button("📊", "Doctor Workload", "", "Doctor_Workload")

        c3, c4 = st.columns(2)
        with c3:
            _patient_tile_button("⚖️", "Assignment Rules", "", "Assignment_Rules")
        with c4:
            _patient_tile_button("🔎", "Patient & Doctor Drilldown", "", "Drilldown")

        st.markdown("")
        # Profile as a full-width tile (remove the small 'Contact' card)
        pcol = st.columns([1])[0]
        with pcol:
            _patient_tile_button("👤", "Profile", "", "Profile")


    elif section == "Case_Allocation":
        render_case_allocation_screen()

    elif section == "Doctor_Workload":
        render_doctor_workload_monitor()

    elif section == "Assignment_Rules":
        render_doctor_assignment_rules()

    elif section == "Drilldown":
        render_patient_doctor_drilldown()

    elif section == "Profile":
        render_patient_profile(user)


# ---------- SAMPLE DATA HELPERS (paste near top of modules/patient/app.py) ----------
from datetime import datetime, timedelta

def load_sample_data(force: bool = False):
    """
    Populate st.session_state with deterministic sample data for testing UI flows.
    Set force=True to overwrite existing sample_data (otherwise the loader will not overwrite).
    """
    if st.session_state.get("sample_data_loaded") and not force:
        return

    now = datetime.now()

    # Sample doctors (name, region, is_senior)
    doctors = [
        {"name": "Dr. A", "region": "North", "is_senior": False},
        {"name": "Dr. B", "region": "North", "is_senior": False},
        {"name": "Dr. C", "region": "South", "is_senior": False},
        {"name": "Dr. D", "region": "South", "is_senior": False},
        {"name": "Dr. Senior", "region": "North", "is_senior": True},
        {"name": "On-call", "region": "", "is_senior": False},
    ]

    # Sample case rows (mix of assigned/unassigned, risk levels, villages, times)
    case_rows = [
        {"id": "P-1001", "name": "Ravi Kumar", "age": 56, "gender": "M", "risk": "Red", "village": "Iskapalem",
         "reported_time": now - timedelta(hours=1, minutes=12), "rmp_proposed": "Dr. A", "assigned_doctor": None},
        {"id": "P-1002", "name": "Sunita Devi", "age": 34, "gender": "F", "risk": "Amber", "village": "Mangalapet",
         "reported_time": now - timedelta(hours=3, minutes=5), "rmp_proposed": None, "assigned_doctor": "Dr. B"},
        {"id": "P-1003", "name": "Karan Yadav", "age": 42, "gender": "M", "risk": "Green", "village": "Iskapalem",
         "reported_time": now - timedelta(days=1, hours=2), "rmp_proposed": "Dr. B", "assigned_doctor": "Dr. B"},
        {"id": "P-1004", "name": "Meena Thomas", "age": 29, "gender": "F", "risk": "Red", "village": "Padur",
         "reported_time": now - timedelta(minutes=40), "rmp_proposed": None, "assigned_doctor": None},
        {"id": "P-1005", "name": "Ajay Singh", "age": 61, "gender": "M", "risk": "Red", "village": "Iskapalem",
         "reported_time": now - timedelta(hours=2, minutes=20), "rmp_proposed": None, "assigned_doctor": "Dr. A"},
        {"id": "P-1006", "name": "Priya Rao", "age": 47, "gender": "F", "risk": "Amber", "village": "Padur",
         "reported_time": now - timedelta(hours=6), "rmp_proposed": None, "assigned_doctor": None},
        {"id": "P-1007", "name": "Mohit Patel", "age": 33, "gender": "M", "risk": "Green", "village": "Mangalapet",
         "reported_time": now - timedelta(days=2), "rmp_proposed": None, "assigned_doctor": "Dr. C"},
        {"id": "P-1008", "name": "Latha Nair", "age": 72, "gender": "F", "risk": "Red", "village": "Iskapalem",
         "reported_time": now - timedelta(hours=8), "rmp_proposed": None, "assigned_doctor": None},
    ]

    # Sample patient profiles (include vitals as floats and rbs as ints)
    patient_profiles = {}
    for c in case_rows:
        pid = c["id"]
        patient_profiles[pid] = {
            "id": pid,
            "name": c["name"],
            "village": c["village"],
            "age": c.get("age", 0),
            "gender": c.get("gender", ""),
            "phone": "",
            "email": "",
            "disability": False,
            "chronic_conditions": [],
            "allergies": "",
            "created_at": (now - timedelta(days=30)).isoformat(),
            "vitals": [
                {"when": (now - timedelta(days=2)).isoformat(), "height_cm": 168.0, "weight_kg": 70.0, "bp": "130/82", "rbs_mgdl": 110},
                {"when": (now - timedelta(days=1)).isoformat(), "height_cm": 168.0, "weight_kg": 69.5, "bp": "128/80", "rbs_mgdl": 105},
            ],
            "visits": [
                {"date": (now - timedelta(days=2)).strftime("%Y-%m-%d"), "reason": "Initial", "notes": "", "reviewed": False}
            ],
            "appointments": []
        }

    # Sample assignment rules (simple examples)
    assignment_rules = [
        {
            "id": 1,
            "name": "Red -> Senior or Least loaded",
            "type": "Default",
            "region": "",
            "active": True,
            "mapping": {
                "Red": {"mode": "Workload balance", "doctor": None},
                "Amber": {"mode": "Workload balance", "doctor": None},
                "Green": {"mode": "Workload balance", "doctor": None},
            },
            "max_active_cases": 5,
            "reassign_after_hours": 24,
            "rr_scope": "All doctors",
            "created_at": now.isoformat()
        },
        {
            "id": 2,
            "name": "Region North: Red fixed Dr. Senior",
            "type": "Region",
            "region": "Iskapalem",
            "active": True,
            "mapping": {
                "Red": {"mode": "Fixed doctor", "doctor": "Dr. Senior"},
                "Amber": {"mode": "Round-robin", "doctor": None},
                "Green": {"mode": "Workload balance", "doctor": None},
            },
            "max_active_cases": 3,
            "reassign_after_hours": 48,
            "rr_scope": "Doctors in region",
            "created_at": now.isoformat()
        }
    ]

    # Put everything into session_state (do not overwrite if user already has data unless force=True)
    if force or "doctors" not in st.session_state:
        st.session_state["doctors"] = doctors
    if force or "case_rows" not in st.session_state:
        st.session_state["case_rows"] = case_rows
    if force or "patient_profiles" not in st.session_state:
        st.session_state["patient_profiles"] = patient_profiles
    if force or "assignment_rules" not in st.session_state:
        st.session_state["assignment_rules"] = assignment_rules
        # set _next_rule_id so future created rules don't clash
        st.session_state["_next_rule_id"] = max(r["id"] for r in assignment_rules) + 1

    # helpers / counters used by other modules
    if "_rr_counters" not in st.session_state:
        st.session_state["_rr_counters"] = {}

    st.session_state["sample_data_loaded"] = True
    st.success("Sample data loaded into session_state (in-memory). You can now verify UI screens.")

def maybe_show_sample_loader():
    """
    Show a small (non-intrusive) button on the patient dashboard to load sample data.
    Call this at the top of render_patient_dashboard() after _ensure_patient_section_state().
    """
    # only show the button if sample data not already loaded
    if not st.session_state.get("sample_data_loaded"):
        st.markdown(
            "<div style='padding:6px; border-radius:8px; background:#f8fafc; margin-bottom:8px;'>"
            "<strong>Test data:</strong> Click to load sample data for UI verification.</div>",
            unsafe_allow_html=True,
        )
        if st.button("Load sample data (for verification)", key="load_sample_data"):
            load_sample_data()
            st.rerun()
