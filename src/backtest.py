import pandas as pd
from scipy.stats import poisson

from db import get_engine

training_seasons = [
    "2021-22",
    "2022-23",
    "2023-24",
    "2024-25",
]

test_season = "2026-27"

season_weights = {
    "2021-22": 1,
    "2022-23": 2,
    "2023-24": 3,
    "2024-25": 4,
}

# Connect to PostgreSQL
engine = get_engine()

# Load team-level match data
team_matches = pd.read_sql(
    "SELECT * FROM team_matches;",
    engine
)

print("Total team-match rows:", len(team_matches))

# Training data
train = team_matches[
    team_matches["season"].isin(training_seasons)
].copy()

# Test data
test = team_matches[
    team_matches["season"] == test_season
].copy()

print("Training rows:", len(train))
print("Test rows:", len(test))

# League scoring averages from training data only
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

home_stats = (
    train[train["venue"] == "Home"]
    .groupby(["season", "team"])
    .agg(
        home_goals_for=("goals_for", "mean"),
        home_goals_against=("goals_against", "mean")
    )
    .reset_index()
)

away_stats = (
    train[train["venue"] == "Away"]
    .groupby(["season", "team"])
    .agg(
        away_goals_for=("goals_for", "mean"),
        away_goals_against=("goals_against", "mean")
    )
    .reset_index()
)

team_strengths = home_stats.merge(
    away_stats,
    on=["season", "team"]
)

team_strengths = team_strengths.merge(
    league_averages,
    on="season"
)

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
        })
    )
    .reset_index()
)

print(
    backtest_strengths[
        backtest_strengths["team"] == "Tottenham"
    ]
)

# Weighted league scoring averages using training seasons only
league_averages["weight"] = (
    league_averages["season"].map(season_weights)
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

print("\nLeague scoring baseline:")
print("Home goals:", round(league_home_goals, 3))
print("Away goals:", round(league_away_goals, 3))

test_matches = pd.read_sql(
    """
    SELECT m.*, home.name AS home_team, away.name AS away_team
    FROM matches AS m
    JOIN teams AS home ON home.team_id = m.home_team_id
    JOIN teams AS away ON away.team_id = m.away_team_id
    WHERE season = '2025-26'
    ORDER BY date;
    """,
    engine
)

print("\nActual test matches:", len(test_matches))

strength_lookup = backtest_strengths.set_index("team")

results = []

max_goals = 10

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

accuracy = results_df["correct"].mean()

print("\nBACKTEST RESULTS")
print("----------------")
print("Total test matches:", len(test_matches))
print("Predicted matches:", len(results_df))
print(
    "Skipped matches:",
    len(test_matches) - len(results_df)
)

print(
    f"Result accuracy: "
    f"{accuracy * 100:.2f}%"
)

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

print(
    f"Home goal MAE: {home_goal_mae:.3f}"
)

print(
    f"Away goal MAE: {away_goal_mae:.3f}"
)

print(
    f"Overall goal MAE: {overall_goal_mae:.3f}"
)
