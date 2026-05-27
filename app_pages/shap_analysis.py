# =========================
# FILE: shap_analysis.py
# =========================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils.database import get_connection
from utils.ml_utils import load_model, make_input_df, predict_diabetes


model = load_model()


# =========================
# SAFE CONVERT
# =========================

def safe_float(value):
    try:
        if value is None:
            return 0.0

        if value == "":
            return 0.0

        return float(value)

    except:
        return 0.0


# =========================
# RISK LEVEL
# =========================

def risk_level(probability):
    if probability >= 0.70:
        return "Tinggi", "🔴"

    elif probability >= 0.40:
        return "Sedang", "🟡"

    else:
        return "Rendah", "🟢"


# =========================
# RISK CHART
# =========================

def risk_chart(probability):
    probability_percent = probability * 100

    fig = go.Figure()

    zones = [
        (0, 40, "#bff2b2", "Rendah / Normal"),
        (40, 70, "#fff3a3", "Sedang"),
        (70, 100, "#ffb3b3", "Tinggi")
    ]

    for y0, y1, color, label in zones:

        fig.add_shape(
            type="rect",
            x0=0,
            x1=100,
            y0=y0,
            y1=y1,
            fillcolor=color,
            opacity=0.85,
            line_width=0,
            layer="below"
        )

        fig.add_annotation(
            x=5,
            y=(y0 + y1) / 2,
            text=label,
            showarrow=False,
            font=dict(size=13)
        )

    fig.add_hline(
        y=40,
        line_dash="dot",
        line_color="gray"
    )

    fig.add_hline(
        y=70,
        line_dash="dot",
        line_color="gray"
    )

    x_values = [0, 25, 50, 75, 100]

    y_values = [
        max(probability_percent - 8, 0),
        max(probability_percent - 3, 0),
        probability_percent,
        max(probability_percent - 4, 0),
        probability_percent
    ]

    fig.add_trace(
        go.Scatter(
            x=x_values,
            y=y_values,
            mode="lines+markers",
            line=dict(
                color="black",
                width=3
            ),
            marker=dict(
                size=8,
                color="black"
            )
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[100],
            y=[probability_percent],
            mode="markers+text",
            marker=dict(
                size=18,
                color="white",
                line=dict(
                    color="black",
                    width=3
                )
            ),
            text=[f"{probability_percent:.2f}%"],
            textposition="middle right"
        )
    )

    fig.update_layout(
        height=360,
        showlegend=False,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(
            l=35,
            r=35,
            t=20,
            b=25
        ),
        xaxis=dict(
            showticklabels=False,
            range=[0, 105]
        ),
        yaxis=dict(
            title="Probability (%)",
            range=[0, 100],
            tickvals=[0, 40, 70, 100],
            ticktext=[
                "0%",
                "40%",
                "70%",
                "100%"
            ]
        )
    )

    return fig


# =========================
# AUTO INSIGHT
# =========================

def auto_insight(
    probability,
    glucose,
    bmi,
    insulin,
    age
):
    if probability >= 0.70:
        st.error(
            "Risiko berada pada zona tinggi. Sebaiknya lakukan pemeriksaan lebih lanjut."
        )

    elif probability >= 0.40:
        st.warning(
            "Risiko berada pada zona sedang. Perhatikan pola hidup dan lakukan monitoring."
        )

    else:
        st.success(
            "Risiko berada pada zona rendah berdasarkan data yang dipilih."
        )

    if glucose >= 140:
        st.warning(
            "Glucose tinggi dan dapat meningkatkan risiko diabetes."
        )

    if bmi >= 30:
        st.warning(
            "BMI tinggi dan dapat berpengaruh terhadap risiko diabetes."
        )

    if insulin >= 150:
        st.info(
            "Insulin cukup tinggi, sebaiknya diperhatikan bersama parameter lain."
        )

    if age >= 45:
        st.info(
            "Usia termasuk faktor yang perlu diperhatikan dalam risiko diabetes."
        )


# =========================
# MAIN PAGE
# =========================

def show_shap_analysis():

    if not st.session_state.logged_in:
        st.warning("Silakan login terlebih dahulu")
        st.stop()

    st.title("📊 Feature Impact Analysis")

    st.caption(
        "Analisis ini mengambil data dari History dan menampilkan zona risiko agar lebih mudah dipahami."
    )

    # =========================
    # GET HISTORY DATA
    # =========================

    conn = get_connection()

    history_df = pd.read_sql_query(
        """
        SELECT *
        FROM history
        WHERE username=?
        ORDER BY id DESC
        """,
        conn,
        params=(
            st.session_state.username,
        )
    )

    conn.close()

    if history_df.empty:
        st.info(
            "Belum ada data prediksi. Silakan prediksi di Dashboard terlebih dahulu."
        )
        return

    # =========================
    # CLEAN DATA
    # =========================

    history_df["probability"] = history_df["probability"].apply(
        safe_float
    )

    history_df["pregnancies"] = history_df["pregnancies"].apply(
        safe_float
    )

    history_df["glucose"] = history_df["glucose"].apply(
        safe_float
    )

    history_df["bmi"] = history_df["bmi"].apply(
        safe_float
    )

    history_df["age"] = history_df["age"].apply(
        safe_float
    )

    history_df["insulin"] = history_df["insulin"].apply(
        safe_float
    )

    # =========================
    # HISTORY LABEL
    # =========================

    history_df["label"] = history_df.apply(
        lambda row: (
            f"ID {row['id']} | "
            f"{row['prediction']} | "
            f"{row['probability'] * 100:.2f}% | "
            f"{row['created_at']}"
        ),
        axis=1
    )

    selected_label = st.selectbox(
        "Pilih data dari history",
        history_df["label"]
    )

    selected_row = history_df[
        history_df["label"] == selected_label
    ].iloc[0]

    pregnancies = safe_float(selected_row["pregnancies"])
    glucose = safe_float(selected_row["glucose"])
    bmi = safe_float(selected_row["bmi"])
    age = safe_float(selected_row["age"])
    insulin = safe_float(selected_row["insulin"])

    # =========================
    # INPUT DATA PREVIEW
    # =========================

    st.markdown("---")

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Pregnancies", pregnancies)
    col2.metric("Glucose", glucose)
    col3.metric("BMI", bmi)
    col4.metric("Age", age)
    col5.metric("Insulin", insulin)

    # =========================
    # BUTTON ANALYSIS
    # =========================

    if st.button("📊 Tampilkan Analisis"):

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

        probability = safe_float(probability)

        level, icon = risk_level(probability)

        # =========================
        # SUMMARY
        # =========================

        st.markdown("---")

        m1, m2, m3 = st.columns(3)

        m1.metric(
            "Prediction",
            result
        )

        m2.metric(
            "Probability",
            f"{probability * 100:.2f}%"
        )

        m3.metric(
            "Risk Level",
            f"{icon} {level}"
        )

        # =========================
        # CHART
        # =========================

        st.subheader("📈 Grafik Zona Risiko")

        st.plotly_chart(
            risk_chart(probability),
            use_container_width=True
        )

        # =========================
        # AUTO INSIGHT
        # =========================

        st.subheader("📝 Penjelasan Otomatis")

        auto_insight(
            probability,
            glucose,
            bmi,
            insulin,
            age
        )

        # =========================
        # SHORT EXPLANATION
        # =========================

        st.markdown("---")

        st.info("""
        Zona hijau menunjukkan risiko rendah, kuning menunjukkan risiko sedang,
        dan merah menunjukkan risiko tinggi.

        Titik terakhir pada grafik adalah probability dari hasil prediksi
        yang dipilih dari history.
        """)