import pandas as pd

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
    df = pd.read_csv(path, header=1)
    df = df[match_columns].copy()
    df = df.rename(columns=rename_map)
    df["date"] = pd.to_datetime(df["date"], dayfirst=True)
    df["season"] = season 
    return df

# Grab all raw season files and clean each one
season_files = {
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

# Save processed dataset
clean_df.to_csv("data/processed/premier_league_2021_26_clean.csv", index=False)
print("Saved cleaned 5-season dataset.")