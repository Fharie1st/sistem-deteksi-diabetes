# =========================
# FILE: main.py
# =========================

import streamlit as st

from utils.database import init_db, register_user, login_user
from app_pages.dashboard import show_dashboard
from app_pages.history import show_history
from app_pages.shap_analysis import show_shap_analysis
from app_pages.risk_tracker import show_risk_tracker
from app_pages.profile import show_profile


# =========================
# CONFIG
# =========================

st.set_page_config(
    page_title="Diabetes Detection System",
    layout="wide",
    page_icon="🩺"
)


# =========================
# INIT DATABASE
# =========================

init_db()


# =========================
# SESSION
# =========================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""


# =========================
# SIDEBAR
# =========================

st.sidebar.title("🩺 Diabetes Detection")

if st.session_state.logged_in:

    menu = st.sidebar.radio(
        "Menu",
        [
            "Dashboard",
            "History",
            "Feature Impact Analysis",
            "Pemantauan Risiko",
            "Profile"
        ]
    )

else:

    menu = st.sidebar.radio(
        "Menu",
        [
            "Login",
            "Register"
        ]
    )


# =========================
# REGISTER
# =========================

if menu == "Register":

    st.title("Register")

    username = st.text_input("Username")

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Register"):

        if username.strip() == "" or password.strip() == "":
            st.warning("Username dan password wajib diisi")

        elif register_user(username, password):
            st.success("Register berhasil, silakan login")

        else:
            st.error("Username sudah digunakan")


# =========================
# LOGIN
# =========================

elif menu == "Login":

    st.title("Login")

    username = st.text_input("Username")

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login"):

        if username.strip() == "" or password.strip() == "":
            st.warning("Username dan password wajib diisi")

        elif login_user(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username

            st.success("Login berhasil")
            st.rerun()

        else:
            st.error("Username / password salah")


# =========================
# DASHBOARD
# =========================

elif menu == "Dashboard":

    show_dashboard()


# =========================
# HISTORY
# =========================

elif menu == "History":

    show_history()


# =========================
# FEATURE IMPACT ANALYSIS
# =========================

elif menu == "Feature Impact Analysis":

    show_shap_analysis()


# =========================
# PEMANTAUAN RISIKO
# =========================

elif menu == "Pemantauan Risiko":

    show_risk_tracker()


# =========================
# PROFILE
# =========================

elif menu == "Profile":

    show_profile()


# =========================
# FOOTER / LOGOUT
# =========================

st.sidebar.markdown("---")

if st.session_state.logged_in:

    st.sidebar.success(
        f"Login sebagai : {st.session_state.username}"
    )

    if st.sidebar.button("Logout"):

        st.session_state.logged_in = False
        st.session_state.username = ""

        if "last_prediction" in st.session_state:
            del st.session_state.last_prediction

        st.rerun()

else:

    st.sidebar.info("Belum login")