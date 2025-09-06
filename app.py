# app.py (root)
import streamlit as st

# Import dashboards
from modules.patient.app import render_patient_dashboard
from modules.health_agent.app import render_health_agent_dashboard
from modules.doctor.app import render_doctor_dashboard
from modules.management.app import render_management_dashboard

from db import get_user_by_username, verify_password, init_db

st.set_page_config(page_title="Hospital App", layout="wide")

import streamlit as st
from pathlib import Path

# def local_css(file_name):
    # with open(file_name) as f:
        # st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# # Load once at the start of app
# local_css("static/style.css")


   
# Ensure DB exists
init_db()  # creates users.db if missing

# -----------------------------
# Login Form
# -----------------------------






# =========================
# 3️⃣ Login Page
# =========================
def render_login():
    import base64
    import streamlit as st

    # Load DPS banner
    banner_b64 = ""
    try:
        with open("Logo_upscaled.png", "rb") as f:
            banner_b64 = base64.b64encode(f.read()).decode("utf-8")
    except Exception:
        pass

    # CSS
    st.markdown(f"""
    <style>
    /* Background */
    html, body, [data-testid="stAppViewContainer"], .main, .block-container {{
        background: #165B33 !important;
    }}
    header, footer {{display: none !important;}}

    /* Banner */
    .login-header img {{
        width: 100%;
        max-width: 600px;
        height: auto;
        display: block;
        margin: 1rem auto;
    }}

    /* Login form container (no ghost box!) */
    .stForm {{
        background: #fff;
        padding: 1.2rem;
        border-radius: 8px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
        width: 100%;
        max-width: 320px;
        margin: 0 auto; /* Center */
    }}

    /* Force visible labels */
    label, .stTextInput label, .stPasswordInput label, .stSelectbox label {{
        color: #000 !important;
        font-weight: 600 !important;
        opacity: 1 !important;
    }}

    /* Slimmer input fields */
    input, select, textarea {{
        height: 1.6rem !important;   /* ⬅️ reduced */
        font-size: 0.85rem !important;
        border-radius: 5px !important;
        padding: 0 0.4rem !important;
    }}

    /* Slimmer button */
    button[kind="secondary"] {{
        width: 100%;
        height: 1.9rem !important;   /* ⬅️ reduced */
        border-radius: 5px;
        font-weight: 600;
        font-size: 0.85rem !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    # Banner
    if banner_b64:
        st.markdown(f"<div class='login-header'><img src='data:image/png;base64,{banner_b64}'/></div>", unsafe_allow_html=True)
    else:
        st.markdown("<h2 style='color:white;text-align:center;'>Mother Teresa Hospital</h2>", unsafe_allow_html=True)

    # Login Form (direct, no extra wrapper divs)
    with st.form("login_form_modern", clear_on_submit=False):
        login_input = st.text_input("Login ID (Email / User ID)")
        password = st.text_input("Password", type="password")
        role_choice = st.selectbox("Role", ["Patient", "Health Agent", "Doctor", "Management"])
        login_btn = st.form_submit_button("Log In")

    if login_btn:
        user_row = get_user_by_username(login_input.strip())
        if not user_row:
            st.error("User not found. (Ask admin to create your account.)")
        elif not verify_password(user_row["salt"], user_row["password_hash"], password):
            st.error("Incorrect password.")
        else:
            st.session_state.user = {
                "id": user_row["id"],
                "username": user_row["username"],
                "name": user_row["name"],
                "role": user_row["role"]
            }
            st.success(f"Logged in as {user_row['name']} ({user_row['role']})")
            st.rerun()


# =========================
# 4️⃣ Role-based Dashboards
# =========================
if "user" not in st.session_state:
    render_login()
else:
    role = st.session_state["user"]["role"]
    user = st.session_state["user"]

    if user["role"] == "Patient":
        render_patient_dashboard(user)
    elif user["role"] == "Health Agent":
        render_health_agent_dashboard(user)
    elif user["role"] == "Doctor":
        render_doctor_dashboard(user)
    elif user["role"] == "Management":
        render_management_dashboard(user)
    else:
        st.error("Unknown role")

