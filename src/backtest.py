import pandas as pd
from scipy.stats import poisson
from db import get_engine
import math

# Connect to PostgreSQL
engine = get_engine()

# Load team-level match data
team_matches = pd.read_sql(
    "SELECT * FROM team_matches;",
    engine
)

matches = pd.read_sql(
    """
    SELECT
        m.*,
        home.name AS home_team,
        away.name AS away_team
    FROM matches AS m
    JOIN teams AS home
        ON home.team_id = m.home_team_id
    JOIN teams AS away
        ON away.team_id = m.away_team_id
    ORDER BY date;
    """,
    engine
)


# Training windows to compare

TEST_SEASON = "2025-26"

training_windows = {
    "5 seasons": [
        "2020-21",
        "2021-22",
        "2022-23",
        "2023-24",
        "2024-25",
    ],

    "9 seasons": [
        "2016-17",
        "2017-18",
        "2018-19",
        "2019-20",
        "2020-21",
        "2021-22",
        "2022-23",
        "2023-24",
        "2024-25",
    ]
}

def get_team_strength(team, strength_lookup):

    if team in strength_lookup.index:
        return strength_lookup.loc[team]

    # Fallback for team with no EPL history
    return pd.Series({
        "home_attack_strength": 1.0,
        "home_defence_strength": 1.0,
        "away_attack_strength": 1.0,
        "away_defence_strength": 1.0
    })

# Backtest function

def run_backtest(training_seasons, test_season):

    train = team_matches[
        team_matches["season"].isin(training_seasons)
    ].copy()

    test_matches = matches[
        matches["season"] == test_season
    ].copy()

    print("\n--------------------------------")
    print("Training seasons:")
    print(training_seasons)
    print("Test season:", test_season)
    print("--------------------------------")

    # Recency weights
    # Oldest = 1, newest = N

    season_weights = {
        season: weight
        for weight, season
        in enumerate(training_seasons, start=1)
    }

    # League scoring averages by season

    league_averages = (
        train
        .groupby(["season", "venue"])["goals_for"]
        .mean()
        .unstack()
        .reset_index()
    )

    league_averages = league_averages.rename(columns={
        "Home": "league_home_goals",
        "Away": "league_away_goals"
    })

    # Team home statistics

    home_stats = (
        train[train["venue"] == "Home"]
        .groupby(["season", "team"])
        .agg(
            home_goals_for=("goals_for", "mean"),
            home_goals_against=("goals_against", "mean")
        )
        .reset_index()
    )

    # Team away statistics

    away_stats = (
        train[train["venue"] == "Away"]
        .groupby(["season", "team"])
        .agg(
            away_goals_for=("goals_for", "mean"),
            away_goals_against=("goals_against", "mean")
        )
        .reset_index()
    )

    # Combine stats

    team_strengths = home_stats.merge(
        away_stats,
        on=["season", "team"]
    )

    team_strengths = team_strengths.merge(
        league_averages,
        on="season"
    )

    # Attack / defence strengths

    team_strengths["home_attack_strength"] = (
        team_strengths["home_goals_for"]
        / team_strengths["league_home_goals"]
    )

    team_strengths["home_defence_strength"] = (
        team_strengths["home_goals_against"]
        / team_strengths["league_away_goals"]
    )

    team_strengths["away_attack_strength"] = (
        team_strengths["away_goals_for"]
        / team_strengths["league_away_goals"]
    )

    team_strengths["away_defence_strength"] = (
        team_strengths["away_goals_against"]
        / team_strengths["league_home_goals"]
    )

    # Add recency weights

    team_strengths["weight"] = (
        team_strengths["season"]
        .map(season_weights)
    )

    strength_columns = [
        "home_attack_strength",
        "home_defence_strength",
        "away_attack_strength",
        "away_defence_strength"
    ]

    for column in strength_columns:

        team_strengths[column + "_weighted"] = (
            team_strengths[column]
            * team_strengths["weight"]
        )

    # Weighted team strengths

    backtest_strengths = (
        team_strengths
        .groupby("team")
        .apply(
            lambda x: pd.Series({

                "home_attack_strength":
                    x["home_attack_strength_weighted"].sum()
                    / x["weight"].sum(),

                "home_defence_strength":
                    x["home_defence_strength_weighted"].sum()
                    / x["weight"].sum(),

                "away_attack_strength":
                    x["away_attack_strength_weighted"].sum()
                    / x["weight"].sum(),

                "away_defence_strength":
                    x["away_defence_strength_weighted"].sum()
                    / x["weight"].sum()
            }),
            include_groups=False
        )
        .reset_index()
    )

    # Weighted league scoring averages

    league_averages["weight"] = (
        league_averages["season"]
        .map(season_weights)
    )

    league_home_goals = (
        (
            league_averages["league_home_goals"]
            * league_averages["weight"]
        ).sum()
        / league_averages["weight"].sum()
    )

    league_away_goals = (
        (
            league_averages["league_away_goals"]
            * league_averages["weight"]
        ).sum()
        / league_averages["weight"].sum()
    )

    # Predict test season matches
    # --------------------------------------------------------

    strength_lookup = (
        backtest_strengths
        .set_index("team")
    )

    results = []

    max_goals = 10

    for _, match in test_matches.iterrows():

        home_team = match["home_team"]
        away_team = match["away_team"]

        home = get_team_strength(
            home_team,
            strength_lookup
        )

        away = get_team_strength(
            away_team,
            strength_lookup
        )


        # Expected goals
        expected_home_goals = (
            league_home_goals
            * home["home_attack_strength"]
            * away["away_defence_strength"]
        )

        expected_away_goals = (
            league_away_goals
            * away["away_attack_strength"]
            * home["home_defence_strength"]
        )

        # Poisson match probabilities
        # ----------------------------------------------------

        home_win_probability = 0
        draw_probability = 0
        away_win_probability = 0

        for home_goals in range(max_goals + 1):

            for away_goals in range(max_goals + 1):

                probability = (
                    poisson.pmf(
                        home_goals,
                        expected_home_goals
                    )
                    *
                    poisson.pmf(
                        away_goals,
                        expected_away_goals
                    )
                )

                if home_goals > away_goals:
                    home_win_probability += probability

                elif home_goals == away_goals:
                    draw_probability += probability

                else:
                    away_win_probability += probability


        probabilities = {
            "H": home_win_probability,
            "D": draw_probability,
            "A": away_win_probability
        }

        predicted_result = max(
            probabilities,
            key=probabilities.get
        )

        actual_result = match["full_time_result"]


        results.append({
            "date": match["date"],
            "home_team": home_team,
            "away_team": away_team,

            "expected_home_goals":
                expected_home_goals,

            "expected_away_goals":
                expected_away_goals,

            "home_win_probability":
                home_win_probability,

            "draw_probability":
                draw_probability,

            "away_win_probability":
                away_win_probability,

            "actual_home_goals":
                match["home_goals"],

            "actual_away_goals":
                match["away_goals"],

            "predicted_result":
                predicted_result,

            "actual_result":
                actual_result,

            "correct":
                predicted_result == actual_result
        })

    results_df = pd.DataFrame(results)

    # Calculate match-result log loss
    log_losses = []

    for _, row in results_df.iterrows():

        total = (
            row["home_win_probability"]
            + row["draw_probability"]
            + row["away_win_probability"]
        )

        if row["actual_result"] == "H":
            actual_probability = (
                row["home_win_probability"] / total
            )

        elif row["actual_result"] == "D":
            actual_probability = (
                row["draw_probability"] / total
            )

        else:
            actual_probability = (
                row["away_win_probability"] / total
            )

        actual_probability = max(
            actual_probability,
            1e-15
        )

        log_losses.append(
            -math.log(actual_probability)
        )

    match_log_loss = (
        sum(log_losses) / len(log_losses)
    )

    # Calculate accuracy
    accuracy = results_df["correct"].mean()

    # Calculate goal MAE
    home_goal_mae = (
        results_df["actual_home_goals"]
        - results_df["expected_home_goals"]
    ).abs().mean()

    away_goal_mae = (
        results_df["actual_away_goals"]
        - results_df["expected_away_goals"]
    ).abs().mean()

    overall_goal_mae = (
        home_goal_mae + away_goal_mae
    ) / 2

    # Return all evaluation metrics
    return {
        "accuracy": accuracy,
        "home_goal_mae": home_goal_mae,
        "away_goal_mae": away_goal_mae,
        "overall_goal_mae": overall_goal_mae,
        "log_loss": match_log_loss
    }

# Run both models

comparison_results = []

for model_name, seasons in training_windows.items():

    metrics = run_backtest(
        seasons,
        TEST_SEASON
    )

    comparison_results.append({
        "model": model_name,

        "accuracy":
            metrics["accuracy"],

        "accuracy_pct":
            metrics["accuracy"] * 100,

        "home_goal_mae":
            metrics["home_goal_mae"],

        "away_goal_mae":
            metrics["away_goal_mae"],

        "overall_goal_mae":
            metrics["overall_goal_mae"],

        "log_loss":
            metrics["log_loss"]
    })


# Final comparison

comparison_df = pd.DataFrame(
    comparison_results
)

print("\n===================================")
print("5-SEASON VS 9-SEASON BACKTEST")
print("===================================")

print(
    comparison_df.to_string(
        index=False
    )
)

comparison_df.to_csv(
    "data/processed/"
    "training_window_comparison.csv",
    index=False
)