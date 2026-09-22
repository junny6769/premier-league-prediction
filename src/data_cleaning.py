import pandas as pd
from sqlalchemy import text
from sqlalchemy.types import Time

from db import get_engine

match_columns = [
    "Date", "Time", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR",
    "HTHG", "HTAG", "HTR", "HS", "AS", "HST", "AST", "HF", "AF",
    "HC", "AC", "HY", "AY", "HR", "AR"
]

rename_map = {
    "Date": "date", "Time": "time", "HomeTeam": "home_team", "AwayTeam": "away_team",
    "FTHG": "home_goals", "FTAG": "away_goals", "FTR": "full_time_result",
    "HTHG": "half_time_home_goals", "HTAG": "half_time_away_goals", "HTR": "half_time_result",
    "HS": "home_shots", "AS": "away_shots", "HST": "home_shots_on_target",
    "AST": "away_shots_on_target", "HF": "home_fouls", "AF": "away_fouls",
    "HC": "home_corners", "AC": "away_corners", "HY": "home_yellow_cards",
    "AY": "away_yellow_cards", "HR": "home_red_cards", "AR": "away_red_cards"
}

def clean_season(path, season):
    print(f"Cleaning {season}: {path}")

    # Find which row contains the actual CSV header
    header_row = None

    with open(path, "r", encoding="utf-8-sig") as file:
        for i in range(5):
            line = file.readline()

            if "Date" in line and "HomeTeam" in line and "AwayTeam" in line:
                header_row = i
                break

    if header_row is None:
        raise ValueError(
            f"Could not find CSV header for {season}: {path}"
        )

    df = pd.read_csv(path, header=header_row)

    # Columns that every season must contain
    required_columns = [
        "Date",
        "HomeTeam",
        "AwayTeam",
        "FTHG",
        "FTAG",
        "FTR"
    ]

    missing_required = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_required:
        raise ValueError(
            f"{season} is missing required columns: {missing_required}"
        )

    # Older seasons may not contain some columns such as Time
    for column in match_columns:
        if column not in df.columns:
            df[column] = pd.NA

    df = df[match_columns].copy()

    df = df.rename(columns=rename_map)

    df["date"] = pd.to_datetime(
        df["date"],
        dayfirst=True
    ).dt.date

    # Some historical seasons do not include kick-off time
    df["time"] = pd.to_datetime(
        df["time"],
        format="%H:%M",
        errors="coerce"
    ).dt.time

    df["season"] = season

    return df

# Grab all raw season files and clean each one
season_files = {
    "2016-17": "data/raw/premier_league_2016_17.csv",
    "2017-18": "data/raw/premier_league_2017_18.csv",
    "2018-19": "data/raw/premier_league_2018_19.csv",
    "2019-20": "data/raw/premier_league_2019_20.csv",
    "2020-21": "data/raw/premier_league_2020_21.csv",
    "2021-22": "data/raw/premier_league_2021_22.csv",
    "2022-23": "data/raw/premier_league_2022_23.csv",
    "2023-24": "data/raw/premier_league_2023_24.csv",
    "2024-25": "data/raw/premier_league_2024_25.csv",
    "2025-26": "data/raw/premier_league_2025_26.csv",
}

clean_df = pd.concat(
    [clean_season(path,season)
     for season, path in season_files.items()],
     ignore_index=True
)


# Data-quality checks
print("Shape:", clean_df.shape)
print("Duplicates:", clean_df.duplicated().sum())
print("\nMatches per season:")
print(clean_df["season"].value_counts().sort_index())
print("\nTeams per season:")
print(
    clean_df.groupby("season")["home_team"].nunique()
)
print("\nMissing values:")
print(clean_df.isnull().sum())

if (
    clean_df.groupby("season").size().to_dict() != dict.fromkeys(season_files, 380)
    or clean_df.duplicated(["season", "date", "home_team", "away_team"]).any()
    or clean_df[["home_goals", "away_goals", "full_time_result"]].isna().any().any()
):
    raise ValueError("Historical match data is incomplete or duplicated; database was not changed")

engine = get_engine()
with engine.begin() as connection:
    team_names = sorted(set(clean_df["home_team"]) | set(clean_df["away_team"]))
    connection.execute(
        text("INSERT INTO teams (name) VALUES (:name) ON CONFLICT (name) DO NOTHING"),
        [{"name": name} for name in team_names],
    )
    team_ids = pd.read_sql("SELECT team_id, name FROM teams", connection).set_index("name")["team_id"]
    clean_df["home_team_id"] = clean_df.pop("home_team").map(team_ids)
    clean_df["away_team_id"] = clean_df.pop("away_team").map(team_ids)
    for season in season_files:
        connection.execute(text("DELETE FROM matches WHERE season = :season"), {"season": season})
    clean_df.to_sql("matches", connection, if_exists="append", index=False,  dtype={"time": Time()
    })

print(f"Loaded {len(clean_df)} matches and updated teams in PostgreSQL.")
