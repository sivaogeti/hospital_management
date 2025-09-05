import streamlit as st
from datetime import date

# -----------------------------
# Doctor Dashboard
# -----------------------------

def render_doctor_dashboard(user: dict):
    """Front page for Doctor login."""

    st.markdown("### 👨‍⚕️ Doctor Dashboard")
    st.caption(f"Welcome, Dr. {user.get('name','Doctor')} · {date.today().strftime('%b %d, %Y')}")

    # KPI cards (placeholders for now)
    c1, c2, c3 = st.columns(3)
    with c1:
        _kpi_card("Today's Patients", "8")
    with c2:
        _kpi_card("Pending Reports", "4")
    with c3:
        _kpi_card("Prescriptions Issued", "12")

    st.write("")

    # Tabs
    tab_patients, tab_reports, tab_presc = st.tabs([
        "Patients",
        "Lab Reports",
        "Prescriptions",
    ])

    with tab_patients:
        st.subheader("Patients")
        st.info("List of patients assigned to you will appear here.")

    with tab_reports:
        st.subheader("Lab Reports")
        st.info("View and approve patients' lab reports here.")

    with tab_presc:
        st.subheader("Prescriptions")
        st.info("Create and manage prescriptions for your patients.")


# -----------------------------
# Utilities (shared-style)
# -----------------------------

def _kpi_card(title: str, value: str):
    st.markdown(
        f"""
        <div style="background:#fff;border:1px solid #e5e7eb;border-radius:14px;padding:14px;box-shadow:0 4px 12px rgba(0,0,0,.06);">
            <div style="font-size:.85rem;color:#6b7280;font-weight:600;">{title}</div>
            <div style="font-size:1.6rem;font-weight:800;line-height:2.2rem;">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
