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

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load once at the start of app
local_css("static/style.css")


# -----------------------------
# Session State
# -----------------------------
if "user" not in st.session_state:
    st.session_state.user = None
    
# Ensure DB exists
init_db()  # creates users.db if missing

# -----------------------------
# Login Form
# -----------------------------
def login_screen():
    st.markdown("## 🏥 Hospital App Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        role_guess = st.selectbox("Role (select for new users or troubleshooting)", ["Patient", "Health Agent", "Doctor", "Management"])
        submitted = st.form_submit_button("Login")
        if submitted:
            user_row = get_user_by_username(username)
            if not user_row:
                st.error("User not found. (If you are a new user, ask admin to create your account.)")
                return
            if not verify_password(user_row["salt"], user_row["password_hash"], password):
                st.error("Incorrect password.")
                return
            # successful login
            st.session_state.user = {
                "id": user_row["id"],
                "username": user_row["username"],
                "name": user_row["name"],
                "role": user_row["role"]
            }
            st.success(f"Logged in as {user_row['name']} ({user_row['role']})")
            st.rerun()


# -----------------------------
# Main App
# -----------------------------
def main():
    user = st.session_state.user
    if not user:
        login_screen()
        return

    # Sidebar & logout (Health Agent can handle its own header)
    if user["role"] != "Health Agent":
        st.sidebar.success(f"Logged in as {user['name']} ({user['role']})")
        if st.sidebar.button("Logout"):
            st.session_state.user = None
            st.rerun()

    # Route
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

if __name__ == "__main__":
    main()
