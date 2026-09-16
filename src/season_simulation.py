import pandas as pd
import numpy as np
from model import calculate_expected_goals

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
NUM_SIMULATIONS = 10000

rng = np.random.default_rng(42)

teams = current_table["team"].tolist()

team_index = {
    team: i
    for i, team in enumerate(teams)
}

num_teams = len(teams)
num_fixtures = len(fixture_predictions)

# Convert fixture teams into numeric indexes 
home_indices = (
    fixture_predictions["home_team"]
    .map(team_index)
    .to_numpy()
)

away_indices = (
    fixture_predictions["away_team"]
    .map(team_index)
    .to_numpy()
)

# Expected goals for every remaining fixtures
home_lambdas = (
    fixture_predictions["expected_home_goals"]
    .to_numpy()
)

away_lambdas = (
    fixture_predictions["expected_away_goals"]
    .to_numpy()
)


# Generate ALL simulated scores at once
home_goals = rng.poisson(
    lam=home_lambdas,
    size=(NUM_SIMULATIONS, num_fixtures)
)

away_goals = rng.poisson(
    lam=away_lambdas,
    size=(NUM_SIMULATIONS, num_fixtures)
)

base_points = current_table["points"].to_numpy()
base_goals_for = current_table["goals_for"].to_numpy()
base_goals_against = current_table["goals_against"].to_numpy()


points = np.tile(
    base_points,
    (NUM_SIMULATIONS, 1)
)

goals_for = np.tile(
    base_goals_for,
    (NUM_SIMULATIONS, 1)
)

goals_against = np.tile(
    base_goals_against,
    (NUM_SIMULATIONS, 1)
)

for fixture in range(num_fixtures):

    home_idx = home_indices[fixture]
    away_idx = away_indices[fixture]

    hg = home_goals[:, fixture]
    ag = away_goals[:, fixture]

    # Goals
    goals_for[:, home_idx] += hg
    goals_against[:, home_idx] += ag

    goals_for[:, away_idx] += ag
    goals_against[:, away_idx] += hg

    # Results
    home_wins = hg > ag
    away_wins = hg < ag
    draws = hg == ag

    points[:, home_idx] += (
        home_wins * 3
        + draws
    )

    points[:, away_idx] += (
        away_wins * 3
        + draws
    )

position_totals = np.zeros(num_teams)

title_counts = np.zeros(num_teams)
top4_counts = np.zeros(num_teams)
relegation_counts = np.zeros(num_teams)


for simulation in range(NUM_SIMULATIONS):

    goal_difference = (
        goals_for[simulation]
        - goals_against[simulation]
    )

    order = np.lexsort((
        -goals_for[simulation],
        -goal_difference,
        -points[simulation]
    ))

    positions = np.empty(num_teams, dtype=int)

    positions[order] = np.arange(
        1,
        num_teams + 1
    )

    position_totals += positions

    title_counts[order[0]] += 1

    top4_counts[
        order[:4]
    ] += 1

    relegation_counts[
        order[-3:]
    ] += 1

#Predicted table produced 

predicted_table = pd.DataFrame({
    "team": teams,
    "average_position":
        position_totals / NUM_SIMULATIONS,
    "average_points":
        points.mean(axis=0),
    "title_probability":
        title_counts
        / NUM_SIMULATIONS
        * 100,
    "top4_probability":
        top4_counts
        / NUM_SIMULATIONS
        * 100,
    "relegation_probability":
        relegation_counts
        / NUM_SIMULATIONS
        * 100
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

predicted_table[
    "title_probability"
] = predicted_table[
    "title_probability"
].round(1)

predicted_table[
    "top4_probability"
] = predicted_table[
    "top4_probability"
].round(1)

predicted_table[
    "relegation_probability"
] = predicted_table[
    "relegation_probability"
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
