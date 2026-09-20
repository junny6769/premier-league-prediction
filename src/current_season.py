import pandas as pd

current_results = pd.read_csv(
    "data/raw/premier_league_2026_27.csv"
)

print("Completed matches:", len(current_results))

print(
    current_results[
        [
            "Date",
            "HomeTeam",
            "AwayTeam",
            "FTHG",
            "FTAG",
            "FTR"
        ]
    ].head()
)

current_results = current_results[
    [
        "Date",
        "Time",
        "HomeTeam",
        "AwayTeam",
        "FTHG",
        "FTAG",
        "FTR"
    ]
].copy()

current_results = current_results.rename(
    columns={
        "Date": "date",
        "Time": "time",
        "HomeTeam": "home_team",
        "AwayTeam": "away_team",
        "FTHG": "home_goals",
        "FTAG": "away_goals",
        "FTR": "full_time_result"
    }
)

current_results["date"] = pd.to_datetime(
    current_results["date"],
    dayfirst=True
)

current_results["season"] = "2026-27"

current_results = current_results.drop_duplicates(
    subset=[
        "date",
        "home_team",
        "away_team"
    ]
)

current_results = current_results.sort_values(
    by=["date", "time"]
).reset_index(drop=True)

current_results.to_csv(
    "data/processed/current_2026_27_results.csv",
    index=False
)

# Build current Premier League table

teams = sorted(
    set(current_results["home_team"])
    | set(current_results["away_team"])
)

table = pd.DataFrame({
    "team": teams,
    "played": 0,
    "wins": 0,
    "draws": 0,
    "losses": 0,
    "goals_for": 0,
    "goals_against": 0,
    "points": 0
})

table = table.set_index("team")


for _, match in current_results.iterrows():

    home = match["home_team"]
    away = match["away_team"]

    home_goals = match["home_goals"]
    away_goals = match["away_goals"]

    # Games played
    table.loc[home, "played"] += 1
    table.loc[away, "played"] += 1

    # Goals
    table.loc[home, "goals_for"] += home_goals
    table.loc[home, "goals_against"] += away_goals

    table.loc[away, "goals_for"] += away_goals
    table.loc[away, "goals_against"] += home_goals

    # Result
    if home_goals > away_goals:

        table.loc[home, "wins"] += 1
        table.loc[away, "losses"] += 1

        table.loc[home, "points"] += 3

    elif home_goals < away_goals:

        table.loc[away, "wins"] += 1
        table.loc[home, "losses"] += 1

        table.loc[away, "points"] += 3

    else:

        table.loc[home, "draws"] += 1
        table.loc[away, "draws"] += 1

        table.loc[home, "points"] += 1
        table.loc[away, "points"] += 1

table["goal_difference"] = (
    table["goals_for"]
    - table["goals_against"]
)

table = table.sort_values(
    by=[
        "points",
        "goal_difference",
        "goals_for"
    ],
    ascending=False
)

table = table.reset_index()

table.insert(
    0,
    "position",
    range(1, len(table) + 1)
)

print("\nCURRENT 2026/27 TABLE")
print("---------------------")

print(
    table[
        [
            "position",
            "team",
            "played",
            "wins",
            "draws",
            "losses",
            "goals_for",
            "goals_against",
            "goal_difference",
            "points"
        ]
    ].to_string(index=False)
)

table.to_csv(
    "data/processed/current_2026_27_table.csv",
    index=False
)
