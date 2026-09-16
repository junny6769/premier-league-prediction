import pandas as pd
from season_simulation import run_simulation

def apply_hypothetical_result(
    current_table,
    fixtures,
    home_team,
    away_team,
    home_goals,
    away_goals
):

    # Check that fixture exists
    match_exists = fixtures[
        (fixtures["home_team"] == home_team)
        &
        (fixtures["away_team"] == away_team)
    ]

    if match_exists.empty:
        raise ValueError(
            f"{home_team} vs {away_team} "
            "is not in the remaining fixtures."
        )

    # Copies so original data is unchanged
    what_if_table = current_table.copy()
    what_if_fixtures = fixtures.copy()

    # Find teams
    home_idx = what_if_table.index[
        what_if_table["team"] == home_team
    ][0]

    away_idx = what_if_table.index[
        what_if_table["team"] == away_team
    ][0]

    # Matches played
    what_if_table.at[home_idx, "played"] += 1
    what_if_table.at[away_idx, "played"] += 1

    # Goals
    what_if_table.at[
        home_idx, "goals_for"
    ] += home_goals

    what_if_table.at[
        home_idx, "goals_against"
    ] += away_goals

    what_if_table.at[
        away_idx, "goals_for"
    ] += away_goals

    what_if_table.at[
        away_idx, "goals_against"
    ] += home_goals

    # Result
    if home_goals > away_goals:

        what_if_table.at[home_idx, "wins"] += 1
        what_if_table.at[away_idx, "losses"] += 1

        what_if_table.at[home_idx, "points"] += 3

    elif away_goals > home_goals:

        what_if_table.at[away_idx, "wins"] += 1
        what_if_table.at[home_idx, "losses"] += 1

        what_if_table.at[away_idx, "points"] += 3

    else:

        what_if_table.at[home_idx, "draws"] += 1
        what_if_table.at[away_idx, "draws"] += 1

        what_if_table.at[home_idx, "points"] += 1
        what_if_table.at[away_idx, "points"] += 1

    # Goal difference
    what_if_table["goal_difference"] = (
        what_if_table["goals_for"]
        - what_if_table["goals_against"]
    )

    # Remove the fixed fixture
    what_if_fixtures = what_if_fixtures[
        ~(
            (what_if_fixtures["home_team"] == home_team)
            &
            (what_if_fixtures["away_team"] == away_team)
        )
    ].copy()

    return what_if_table, what_if_fixtures

if __name__ == "__main__":

    current_table = pd.read_csv(
        "data/processed/current_2026_27_table.csv"
    )

    fixtures = pd.read_csv(
        "data/processed/remaining_2026_27_fixtures.csv"
    )

    # Example hypothetical result
    home_team = "Tottenham"
    away_team = "Arsenal"

    home_goals = 2
    away_goals = 0

    # Apply hypothetical result
    what_if_table, what_if_fixtures = (
        apply_hypothetical_result(
            current_table,
            fixtures,
            home_team,
            away_team,
            home_goals,
            away_goals
        )
    )

    print(
        "\nWhat-If:",
        f"{home_team} {home_goals}-{away_goals} {away_team}"
    )

    print(
        "Remaining fixtures:",
        len(what_if_fixtures)
    )

    # Run season simulation after hypothetical result
    what_if_prediction = run_simulation(
        what_if_table,
        what_if_fixtures,
        num_simulations=1000
    )

    print("\nWHAT-IF PREDICTED TABLE")
    print("-----------------------")

    print(
        what_if_prediction.to_string(
            index=False
        )
    )

baseline_prediction = run_simulation(
    current_table,
    fixtures,
    num_simulations=1000,
    random_seed=42
)

teams_to_compare = [
    home_team,
    away_team
]

baseline_compare = baseline_prediction[
    baseline_prediction["team"].isin(
        teams_to_compare
    )
][
    [
        "team",
        "average_position",
        "average_points",
        "title_probability",
        "top4_probability",
        "relegation_probability"
    ]
].copy()

what_if_compare = what_if_prediction[
    what_if_prediction["team"].isin(
        teams_to_compare
    )
][
    [
        "team",
        "average_position",
        "average_points",
        "title_probability",
        "top4_probability",
        "relegation_probability"
    ]
].copy()

baseline_compare = baseline_compare.rename(
    columns={
        "average_position":
            "baseline_average_position",
        "average_points":
            "baseline_average_points",
        "title_probability":
            "baseline_title_probability",
        "top4_probability":
            "baseline_top4_probability",
        "relegation_probability":
            "baseline_relegation_probability"
    }
)

what_if_compare = what_if_compare.rename(
    columns={
        "average_position":
            "what_if_average_position",
        "average_points":
            "what_if_average_points",
        "title_probability":
            "what_if_title_probability",
        "top4_probability":
            "what_if_top4_probability",
        "relegation_probability":
            "what_if_relegation_probability"
    }
)

comparison = baseline_compare.merge(
    what_if_compare,
    on="team"
)

comparison["position_change"] = (
    comparison["what_if_average_position"]
    - comparison["baseline_average_position"]
)

comparison["points_change"] = (
    comparison["what_if_average_points"]
    - comparison["baseline_average_points"]
)

comparison["title_change"] = (
    comparison["what_if_title_probability"]
    - comparison["baseline_title_probability"]
)

comparison["top4_change"] = (
    comparison["what_if_top4_probability"]
    - comparison["baseline_top4_probability"]
)

comparison["relegation_change"] = (
    comparison["what_if_relegation_probability"]
    - comparison["baseline_relegation_probability"]
)

print("\nWHAT-IF COMPARISON")
print("------------------")

print(
    comparison[
        [
            "team",
            "baseline_average_position",
            "what_if_average_position",
            "position_change",
            "baseline_title_probability",
            "what_if_title_probability",
            "title_change",
            "baseline_top4_probability",
            "what_if_top4_probability",
            "top4_change"
        ]
    ].to_string(index=False)
)