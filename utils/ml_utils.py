# =========================
# FILE: ml_utils.py
# =========================

import pandas as pd
import joblib
from pathlib import Path

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "model.pkl"

FEATURE_COLUMNS = [
    "Pregnancies",
    "Glucose",
    "BMI",
    "Age",
    "Insulin",
    "PregnancyRatio",
    "RiskScore",
    "InsulinEfficiency",
    "Glucose_BMI",
    "BMI_Age"
]


def load_model():
    return joblib.load(MODEL_PATH)


def create_features(df):

    df["PregnancyRatio"] = (
        df["Pregnancies"] / (df["Age"] + 1)
    )

    df["RiskScore"] = (
        df["Glucose"] * 0.4 +
        df["BMI"] * 0.3 +
        df["Age"] * 0.2 +
        df["Insulin"] * 0.1
    )

    df["InsulinEfficiency"] = (
        df["Glucose"] / (df["Insulin"] + 1)
    )

    df["Glucose_BMI"] = (
        df["Glucose"] * df["BMI"]
    )

    df["BMI_Age"] = (
        df["BMI"] * df["Age"]
    )

    return df


def make_input_df(
    pregnancies,
    glucose,
    bmi,
    age,
    insulin
):
    input_df = pd.DataFrame([{
        "Pregnancies": pregnancies,
        "Glucose": glucose,
        "BMI": bmi,
        "Age": age,
        "Insulin": insulin
    }])

    input_df = create_features(input_df)

    return input_df[FEATURE_COLUMNS]


def predict_diabetes(model, input_df):
    prediction = model.predict(input_df)[0]
    probability = model.predict_proba(input_df)[0][1]

    result = (
        "Diabetes"
        if prediction == 1
        else "No Diabetes"
    )

    return prediction, probability, result
