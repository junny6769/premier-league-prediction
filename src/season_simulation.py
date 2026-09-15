from model import calculate_expected_goals
import pandas as pd
import numpy as np

current_table = pd.read_csv(
    "data/processed/current_2026_27_table.csv"
)

fixtures = pd.read_csv(
    "data/processed/remaining_2026_27_fixtures.csv"
)

print("Current teams:", len(current_table))
print("Remaining fixtures:", len(fixtures))

home_counts = fixtures["home_team"].value_counts()
away_counts = fixtures["away_team"].value_counts()

remaining_counts = home_counts.add(
    away_counts,
    fill_value=0
)

fixture_check = current_table[
    ["team", "played"]
].copy()

fixture_check["remaining"] = (
    fixture_check["team"]
    .map(remaining_counts)
    .fillna(0)
    .astype(int)
)

fixture_check["final_total"] = (
    fixture_check["played"]
    + fixture_check["remaining"]
)

print("\nFIXTURE CHECK")
print(fixture_check.to_string(index=False))

fixture_predictions = []

for _, fixture in fixtures.iterrows():

    home_team = fixture["home_team"]
    away_team = fixture["away_team"]

    expected_home_goals, expected_away_goals = (
        calculate_expected_goals(
            home_team,
            away_team
        )
    )

    fixture_predictions.append({
        "home_team": home_team,
        "away_team": away_team,
        "expected_home_goals":
            expected_home_goals,
        "expected_away_goals":
            expected_away_goals
    })

fixture_predictions = pd.DataFrame(
    fixture_predictions
)

print(
    "\nFixtures prepared:",
    len(fixture_predictions)
)

#Monte carlo simulation
NUM_SIMULATIONS = 1000

rng = np.random.default_rng(42)

teams = current_table["team"].tolist()

team_index = {
    team: i
    for i, team in enumerate(teams)
}

position_totals = np.zeros(len(teams))
points_totals = np.zeros(len(teams))

for simulation in range(NUM_SIMULATIONS):

    sim_table = current_table.copy()

    for _, fixture in fixture_predictions.iterrows():

        home = fixture["home_team"]
        away = fixture["away_team"]

        home_goals = rng.poisson(
            fixture["expected_home_goals"]
        )

        away_goals = rng.poisson(
            fixture["expected_away_goals"]
        )

        home_idx = sim_table.index[
            sim_table["team"] == home
        ][0]

        away_idx = sim_table.index[
            sim_table["team"] == away
        ][0]

        # Played
        sim_table.loc[home_idx, "played"] += 1
        sim_table.loc[away_idx, "played"] += 1

        # Goals
        sim_table.loc[
            home_idx,
            "goals_for"
        ] += home_goals

        sim_table.loc[
            home_idx,
            "goals_against"
        ] += away_goals

        sim_table.loc[
            away_idx,
            "goals_for"
        ] += away_goals

        sim_table.loc[
            away_idx,
            "goals_against"
        ] += home_goals

        # Points
        if home_goals > away_goals:

            sim_table.loc[
                home_idx,
                "wins"
            ] += 1

            sim_table.loc[
                away_idx,
                "losses"
            ] += 1

            sim_table.loc[
                home_idx,
                "points"
            ] += 3

        elif away_goals > home_goals:

            sim_table.loc[
                away_idx,
                "wins"
            ] += 1

            sim_table.loc[
                home_idx,
                "losses"
            ] += 1

            sim_table.loc[
                away_idx,
                "points"
            ] += 3

        else:

            sim_table.loc[
                home_idx,
                "draws"
            ] += 1

            sim_table.loc[
                away_idx,
                "draws"
            ] += 1

            sim_table.loc[
                home_idx,
                "points"
            ] += 1

            sim_table.loc[
                away_idx,
                "points"
            ] += 1

        sim_table["goal_difference"] = (
        sim_table["goals_for"]
        - sim_table["goals_against"]
    )

    sim_table = sim_table.sort_values(
        by=[
            "points",
            "goal_difference",
            "goals_for"
        ],
        ascending=False
    ).reset_index(drop=True)

    sim_table["position"] = (
        range(1, 21)
    )

    for _, row in sim_table.iterrows():

        idx = team_index[row["team"]]

        position_totals[idx] += (
            row["position"]
        )

        points_totals[idx] += (
            row["points"]
        )


#Predicted table produced 

predicted_table = pd.DataFrame({
    "team": teams,
    "average_position":
        position_totals / NUM_SIMULATIONS,
    "average_points":
        points_totals / NUM_SIMULATIONS
})
predicted_table = (
    predicted_table
    .sort_values(
        "average_position"
    )
    .reset_index(drop=True)
)

predicted_table.insert(
    0,
    "predicted_position",
    range(1, 21)
)

predicted_table[
    "average_position"
] = predicted_table[
    "average_position"
].round(2)

predicted_table[
    "average_points"
] = predicted_table[
    "average_points"
].round(1)

print("\nPREDICTED FINAL 2026/27 TABLE")
print("-----------------------------")

print(
    predicted_table.to_string(
        index=False
    )
)

predicted_table.to_csv(
    "data/processed/predicted_2026_27_table.csv",
    index=False
)
