import sys
from pathlib import Path

import pandas as pd
import streamlit as st


# Allow app.py to import files from src/
project_root = Path(__file__).resolve().parents[1]
src_path = project_root / "src"

sys.path.append(str(src_path))

from model import predict_match

# Page configuration

st.set_page_config(
    page_title="Premier League Predictor",
    page_icon="⚽",
    layout="wide"
)

# Title

st.title("⚽ Premier League 2026/27 Predictor")

st.write(
    "Premier League standings and match predictions "
    "using historical team strengths, Poisson modelling "
    "and Monte Carlo simulation."
)

# Load data

@st.cache_data
def load_predicted_table():

    path = (
        project_root
        / "data"
        / "processed"
        / "predicted_2026_27_table.csv"
    )

    return pd.read_csv(path)


predicted_table = load_predicted_table()

# Predicted league table

st.header("Predicted Final Table")

display_table = predicted_table[
    [
        "predicted_position",
        "team",
        "average_position",
        "average_points",
        "title_probability",
        "top4_probability",
        "relegation_probability"
    ]
].copy()

display_table = display_table.rename(
    columns={
        "predicted_position": "Position",
        "team": "Team",
        "average_position": "Avg Position",
        "average_points": "Avg Points",
        "title_probability": "Title %",
        "top4_probability": "Top 4 %",
        "relegation_probability": "Relegation %"
    }
)

st.dataframe(
    display_table,
    hide_index=True,
    use_container_width=True
)

# Match predictor

st.header("Match Predictor")

teams = sorted(
    predicted_table["team"].unique()
)

col1, col2 = st.columns(2)

with col1:

    home_team = st.selectbox(
        "Home Team",
        teams,
        index=teams.index("Man City")
        if "Man City" in teams
        else 0
    )

with col2:

    away_team = st.selectbox(
        "Away Team",
        teams,
        index=teams.index("Man United")
        if "Man United" in teams
        else 1
    )

if st.button("Predict Match"):

    if home_team == away_team:

        st.error(
            "Please select two different teams."
        )

    else:

        prediction = predict_match(
            home_team,
            away_team
        )

        st.subheader(
            f"{home_team} vs {away_team}"
        )

        # Expected goals
        col1, col2 = st.columns(2)

        col1.metric(
            f"{home_team} Expected Goals",
            f"{prediction['expected_home_goals']:.2f}"
        )

        col2.metric(
            f"{away_team} Expected Goals",
            f"{prediction['expected_away_goals']:.2f}"
        )

        # Most likely score
        st.subheader("Most Likely Score")

        st.markdown(
            f"### {home_team} "
            f"{prediction['most_likely_home_goals']} "
            f"- "
            f"{prediction['most_likely_away_goals']} "
            f"{away_team}"
        )

        # Result probabilities
        st.subheader("Result Probabilities")

        home_probability = (
            prediction[
                "home_win_probability"
            ] * 100
        )

        draw_probability = (
            prediction[
                "draw_probability"
            ] * 100
        )

        away_probability = (
            prediction[
                "away_win_probability"
            ] * 100
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            f"{home_team} Win",
            f"{home_probability:.1f}%"
        )

        col2.metric(
            "Draw",
            f"{draw_probability:.1f}%"
        )

        col3.metric(
            f"{away_team} Win",
            f"{away_probability:.1f}%"
        )