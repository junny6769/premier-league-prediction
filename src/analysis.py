import pandas as pd

from db import get_engine

engine = get_engine()

query = """
SELECT *
FROM team_matches;
"""

team_matches = pd.read_sql(query, engine)

print(team_matches.head())
print(team_matches.shape)

# Calculate home performance
home_stats = (
    team_matches[team_matches["venue"] == "Home"]
    .groupby(["season", "team"])
    .agg(
        home_matches=("team", "size"),
        home_goals_for=("goals_for", "mean"),
        home_goals_against=("goals_against", "mean"),
        home_shots=("shots_for", "mean"),
        home_shots_on_target=("shots_on_target_for", "mean")
    )
    .reset_index()
)

# Calculate away performance
away_stats = (
    team_matches[team_matches["venue"] == "Away"]
    .groupby(["season", "team"])
    .agg(
        away_matches=("team", "size"),
        away_goals_for=("goals_for", "mean"),
        away_goals_against=("goals_against", "mean"),
        away_shots=("shots_for", "mean"),
        away_shots_on_target=("shots_on_target_for", "mean")
    )
    .reset_index()
)

print(home_stats.head())
print(away_stats.head())

# League average goals by season
league_averages = (
    team_matches
    .groupby(["season", "venue"])
    ["goals_for"]
    .mean()
    .unstack()
    .reset_index()
)

league_averages = league_averages.rename(columns={
    "Home": "league_home_goals",
    "Away": "league_away_goals"
})

print(league_averages)

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

print(
    team_strengths[
        [
            "season",
            "team",
            "home_attack_strength",
            "home_defence_strength",
            "away_attack_strength",
            "away_defence_strength"
        ]
    ].head(20)
)

#example using Tottenham
print(
    team_strengths[
        team_strengths["team"] == "Tottenham"
    ][
        [
            "season",
            "team",
            "home_attack_strength",
            "home_defence_strength",
            "away_attack_strength",
            "away_defence_strength"
        ]
    ]
)

# Give more recent seasons greater importance
season_weights = {
    "2021-22": 1,
    "2022-23": 2,
    "2023-24": 3,
    "2024-25": 4,
    "2025-26": 5
}

team_strengths["weight"] = team_strengths["season"].map(season_weights)


# Create weighted strength columns
team_strengths["home_attack_strength_weighted"] = (
    team_strengths["home_attack_strength"] * team_strengths["weight"]
)

team_strengths["home_defence_strength_weighted"] = (
    team_strengths["home_defence_strength"] * team_strengths["weight"]
)

team_strengths["away_attack_strength_weighted"] = (
    team_strengths["away_attack_strength"] * team_strengths["weight"]
)

team_strengths["away_defence_strength_weighted"] = (
    team_strengths["away_defence_strength"] * team_strengths["weight"]
)

current_strengths = (
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
    current_strengths[
        current_strengths["team"] == "Tottenham"
    ]
)

current_strengths.to_csv(
    "data/processed/current_team_strengths.csv",
    index=False
)

season_weights = {
    "2021-22": 1,
    "2022-23": 2,
    "2023-24": 3,
    "2024-25": 4,
    "2025-26": 5
}

league_averages["weight"] = (
    league_averages["season"].map(season_weights)
)

weighted_league_home_goals = (
    (
        league_averages["league_home_goals"]
        * league_averages["weight"]
    ).sum()
    / league_averages["weight"].sum()
)

weighted_league_away_goals = (
    (
        league_averages["league_away_goals"]
        * league_averages["weight"]
    ).sum()
    / league_averages["weight"].sum()
)

print("Weighted league home goals:",
      weighted_league_home_goals)

print("Weighted league away goals:",
      weighted_league_away_goals)

weighted_league_average = pd.DataFrame({
    "league_home_goals": [weighted_league_home_goals],
    "league_away_goals": [weighted_league_away_goals]
})

weighted_league_average.to_csv(
    "data/processed/weighted_league_average.csv",
    index=False
)