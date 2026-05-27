# =========================
# FILE: risk_tracker.py
# =========================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils.database import get_connection


def safe_float(value):
    try:
        if value is None or value == "":
            return 0.0
        return float(value)
    except Exception:
        return 0.0


def get_risk_level(probability):
    if probability >= 0.70:
        return "Tinggi", "🔴"
    elif probability >= 0.40:
        return "Sedang", "🟡"
    else:
        return "Rendah", "🟢"


def show_risk_tracker():

    if not st.session_state.logged_in:
        st.warning("Silakan login terlebih dahulu")
        st.stop()

    st.title("📈 Pemantauan Risiko")

    st.write(
        "Pantau perkembangan risiko diabetes berdasarkan hasil prediksi yang tersimpan di history."
    )

    # =========================
    # GET HISTORY
    # =========================

    conn = get_connection()

    history_df = pd.read_sql_query(
        """
        SELECT *
        FROM history
        WHERE username=?
        ORDER BY id ASC
        """,
        conn,
        params=(st.session_state.username,)
    )

    conn.close()

    if history_df.empty:
        st.info(
            "Belum ada data prediksi. Silakan lakukan prediksi di Dashboard terlebih dahulu."
        )
        return

    # =========================
    # CLEAN DATA
    # =========================

    history_df["probability"] = history_df["probability"].apply(
        safe_float
    )

    history_df["Probability (%)"] = (
        history_df["probability"] * 100
    )

    history_df["created_at"] = pd.to_datetime(
        history_df["created_at"],
        errors="coerce"
    )

    history_df = history_df.dropna(
        subset=["created_at"]
    )

    if history_df.empty:
        st.warning("Data history belum memiliki tanggal yang valid.")
        return

    # =========================
    # SUMMARY
    # =========================

    total_data = len(history_df)

    diabetes_count = len(
        history_df[
            history_df["prediction"] == "Diabetes"
        ]
    )

    no_diabetes_count = len(
        history_df[
            history_df["prediction"] == "No Diabetes"
        ]
    )

    last_row = history_df.iloc[-1]

    last_probability = safe_float(
        last_row["probability"]
    )

    last_probability_percent = (
        last_probability * 100
    )

    risk_level, risk_icon = get_risk_level(
        last_probability
    )

    first_probability = safe_float(
        history_df.iloc[0]["probability"]
    )

    difference = (
        last_probability - first_probability
    ) * 100

    # =========================
    # METRIC
    # =========================

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total History",
            total_data
        )

    with col2:
        st.metric(
            "Risiko Terakhir",
            f"{last_probability_percent:.2f}%"
        )

    with col3:
        st.metric(
            "Risk Level",
            f"{risk_icon} {risk_level}"
        )

    # =========================
    # MONTHLY RISK DATA
    # =========================

    history_df["Month"] = (
        history_df["created_at"]
        .dt.to_period("M")
        .astype(str)
    )

    monthly_df = history_df.groupby(
        "Month",
        as_index=False
    )["Probability (%)"].mean()

    # =========================
    # CHART SECTION
    # =========================

    st.markdown("---")

    chart_col1, chart_col2 = st.columns([1.4, 1])

    with chart_col1:

        st.subheader("Perkembangan Risiko per Bulan")

        line_fig = go.Figure()

        line_fig.add_trace(
            go.Scatter(
                x=monthly_df["Month"],
                y=monthly_df["Probability (%)"],
                mode="lines+markers",
                name="Risiko",
                line=dict(
                    color="#e74c3c",
                    width=3
                ),
                marker=dict(
                    color="#e74c3c",
                    size=8
                )
            )
        )

        line_fig.update_layout(
            height=350,
            margin=dict(
                l=20,
                r=20,
                t=20,
                b=20
            ),
            plot_bgcolor="white",
            paper_bgcolor="white",
            xaxis=dict(
                title="Bulan",
                showgrid=True,
                gridcolor="#eeeeee"
            ),
            yaxis=dict(
                title="Probability (%)",
                range=[0, 100],
                showgrid=True,
                gridcolor="#eeeeee"
            ),
            showlegend=False
        )

        st.plotly_chart(
            line_fig,
            use_container_width=True
        )

    with chart_col2:

        st.subheader("Diabetes vs No Diabetes")

        pie_fig = go.Figure(
            data=[
                go.Pie(
                    labels=[
                        "Diabetes",
                        "No Diabetes"
                    ],
                    values=[
                        diabetes_count,
                        no_diabetes_count
                    ],
                    hole=0.35,
                    textinfo="label+percent",
                    pull=[
                        0.03,
                        0.03
                    ]
                )
            ]
        )

        pie_fig.update_layout(
            height=350,
            margin=dict(
                l=10,
                r=10,
                t=20,
                b=10
            ),
            showlegend=True,
            paper_bgcolor="white",
            plot_bgcolor="white"
        )

        st.plotly_chart(
            pie_fig,
            use_container_width=True
        )

    # =========================
    # INSIGHT
    # =========================

    st.markdown("---")

    st.subheader("Insight")

    if difference > 0:
        st.warning(
            f"Risiko terakhir naik {difference:.2f}% dibanding prediksi pertama."
        )

    elif difference < 0:
        st.success(
            f"Risiko terakhir turun {abs(difference):.2f}% dibanding prediksi pertama."
        )

    else:
        st.info(
            "Risiko terakhir masih sama dengan prediksi pertama."
        )

    if last_probability >= 0.70:
        st.error(
            "Kategori risiko terakhir tinggi. Sebaiknya lakukan pemeriksaan lebih lanjut."
        )

    elif last_probability >= 0.40:
        st.warning(
            "Kategori risiko terakhir sedang. Tetap lakukan monitoring dan jaga pola hidup."
        )

    else:
        st.success(
            "Kategori risiko terakhir rendah berdasarkan data prediksi."
        )