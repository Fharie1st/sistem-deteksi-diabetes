# =========================
# FILE: history.py
# =========================

import streamlit as st
import pandas as pd

from utils.database import (
    get_connection,
    delete_all_history,
    delete_history_by_id
)


def safe_float(value):
    try:
        if value is None or value == "":
            return 0.0
        return float(value)
    except:
        return 0.0


def get_risk_level(probability):
    if probability >= 0.70:
        return "High"
    elif probability >= 0.40:
        return "Medium"
    else:
        return "Low"


def prediction_style(val):
    if val == "Diabetes":
        return "background-color: #fdeaea; color: #c0392b; border-radius: 6px; font-weight: 600;"
    return "background-color: #eaf7ee; color: #1e8449; border-radius: 6px; font-weight: 600;"


def risk_style(val):
    if val == "High":
        return "background-color: #fdeaea; color: #c0392b; border-radius: 6px; font-weight: 600;"
    elif val == "Medium":
        return "background-color: #fff8e6; color: #b9770e; border-radius: 6px; font-weight: 600;"
    return "background-color: #eaf7ee; color: #1e8449; border-radius: 6px; font-weight: 600;"


def show_history():

    if not st.session_state.logged_in:
        st.warning("Silakan login terlebih dahulu")
        st.stop()

    st.title("📜 Prediction History")
    st.caption("Riwayat hasil prediksi yang tersimpan.")

    if "confirm_delete_all_history" not in st.session_state:
        st.session_state.confirm_delete_all_history = False

    if "confirm_delete_id" not in st.session_state:
        st.session_state.confirm_delete_id = None

    conn = get_connection()

    history_df = pd.read_sql_query(
        """
        SELECT *
        FROM history
        WHERE username=?
        ORDER BY id DESC
        """,
        conn,
        params=(st.session_state.username,)
    )

    conn.close()

    if history_df.empty:
        st.info("Belum ada history prediksi.")
        return

    # =========================
    # CLEAN DATA
    # =========================

    history_df["probability"] = history_df["probability"].apply(safe_float)
    history_df["Probability"] = history_df["probability"].apply(
        lambda x: f"{x * 100:.2f}%"
    )
    history_df["Risk Level"] = history_df["probability"].apply(get_risk_level)

    # =========================
    # TABLE DISPLAY
    # =========================

    display_df = history_df[
        [
            "id",
            "pregnancies",
            "glucose",
            "bmi",
            "age",
            "insulin",
            "prediction",
            "Probability",
            "Risk Level",
            "created_at"
        ]
    ].copy()

    display_df = display_df.rename(
        columns={
            "id": "ID",
            "pregnancies": "Pregnancies",
            "glucose": "Glucose",
            "bmi": "BMI",
            "age": "Age",
            "insulin": "Insulin",
            "prediction": "Prediction",
            "created_at": "Date"
        }
    )

    styled_df = display_df.style.map(
        prediction_style,
        subset=["Prediction"]
    ).map(
        risk_style,
        subset=["Risk Level"]
    )

    # =========================
    # ACTION BUTTONS
    # =========================

    top_col1, top_col2 = st.columns([1, 3])

    with top_col1:
        if not st.session_state.confirm_delete_all_history:
            if st.button("🗑 Hapus Semua"):
                st.session_state.confirm_delete_all_history = True
                st.rerun()
        else:
            st.warning("Hapus semua history?")

            if st.button("Iya, Hapus Semua"):
                delete_all_history(st.session_state.username)
                st.session_state.confirm_delete_all_history = False
                st.session_state.confirm_delete_id = None
                st.success("Semua history berhasil dihapus.")
                st.rerun()

            if st.button("Tidak"):
                st.session_state.confirm_delete_all_history = False
                st.rerun()

    st.markdown("---")

    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True,
        height=380
    )

    st.markdown("---")

    # =========================
    # DELETE SINGLE DATA
    # =========================

    st.subheader("Hapus Data Tertentu")

    history_options = history_df.apply(
        lambda row: (
            f"ID {row['id']} | "
            f"{row['prediction']} | "
            f"{row['probability'] * 100:.2f}% | "
            f"{row['created_at']}"
        ),
        axis=1
    ).tolist()

    selected_history = st.selectbox(
        "Pilih data yang ingin dihapus",
        history_options
    )

    selected_index = history_options.index(selected_history)
    selected_row = history_df.iloc[selected_index]
    delete_id = int(selected_row["id"])

    if st.session_state.confirm_delete_id == delete_id:

        st.warning("Anda ingin menghapus data ini?")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Iya"):
                delete_history_by_id(delete_id)
                st.session_state.confirm_delete_id = None
                st.success("Data berhasil dihapus.")
                st.rerun()

        with col2:
            if st.button("Tidak"):
                st.session_state.confirm_delete_id = None
                st.rerun()

    else:
        if st.button("❌ Hapus Data Ini"):
            st.session_state.confirm_delete_id = delete_id
            st.rerun()