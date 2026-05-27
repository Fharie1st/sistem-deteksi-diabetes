# =========================
# FILE: dashboard.py
# =========================

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

from utils.database import save_history
from utils.ml_utils import load_model, make_input_df, predict_diabetes


model = load_model()


def show_dashboard():

    if not st.session_state.logged_in:
        st.warning("Silakan login terlebih dahulu")
        st.stop()

    st.title("🩺 Diabetes Detection System")
    st.subheader("Patient Input")

    with st.form("prediction_form"):

        input_col1, input_col2 = st.columns(2)

        with input_col1:

            pregnancies = st.slider(
                "Pregnancies",
                0,
                20,
                1
            )

            glucose = st.slider(
                "Glucose",
                0,
                300,
                120
            )

            bmi = st.slider(
                "BMI",
                0.0,
                70.0,
                25.0
            )

        with input_col2:

            age = st.slider(
                "Age",
                1,
                120,
                25
            )

            insulin = st.slider(
                "Insulin",
                0,
                900,
                80
            )

        submit_prediction = st.form_submit_button("🔍 Prediksi Sekarang")

    if not submit_prediction:
        st.info("Isi data pasien, lalu klik tombol **Prediksi Sekarang** untuk melihat hasil.")
        return

    input_df = make_input_df(
        pregnancies,
        glucose,
        bmi,
        age,
        insulin
    )

    prediction, probability, result = predict_diabetes(
        model,
        input_df
    )

    accuracy = 82.29

    st.markdown("---")
    st.subheader("Hasil Prediksi")

    col1, col2 = st.columns([1, 1])

    with col1:

        st.metric(
            "Model Accuracy",
            f"{accuracy:.2f}%"
        )

        if result == "Diabetes":
            st.error(result)
        else:
            st.success(result)

        st.info(
            f"Probability : {probability * 100:.2f}%"
        )

    with col2:

        fig = go.Figure(go.Pie(

            values=[
                probability,
                1 - probability
            ],

            hole=0.72,

            marker_colors=[
                "#31b7f3",
                "#0d5c78"
            ],

            textinfo="none",
            sort=False
        ))

        fig.update_layout(

            height=400,

            annotations=[dict(
                text=f"{probability * 100:.2f}%",
                x=0.5,
                y=0.5,
                font_size=32,
                showarrow=False
            )],

            showlegend=False
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    current_result = (
        pregnancies,
        glucose,
        bmi,
        age,
        insulin,
        result
    )

    if "last_prediction" not in st.session_state:
        st.session_state.last_prediction = None

    if st.session_state.last_prediction != current_result:

        save_history(
            st.session_state.username,
            pregnancies,
            glucose,
            bmi,
            age,
            insulin,
            result,
            probability,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        st.session_state.last_prediction = current_result
        st.success("Hasil prediksi berhasil disimpan ke history.")
