import pandas as pd
import glob

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

def clean_season(path):
    df = pd.read_csv(path, header=1)
    df = df[match_columns].copy()
    df = df.rename(columns=rename_map)
    df["date"] = pd.to_datetime(df["date"], dayfirst=True)
    return df

# Grab all raw season files and clean each one
season_files = sorted(glob.glob("data/raw/premier_league_*.csv"))
clean_df = pd.concat([clean_season(f) for f in season_files], ignore_index=True)

# Data-quality checks
print("Shape:", clean_df.shape)
print("Duplicates:", clean_df.duplicated().sum())
print("Number of teams:", clean_df["home_team"].nunique())
print("\nMissing values:")
print(clean_df.isnull().sum())

# Save processed dataset
clean_df.to_csv("data/processed/premier_league_2021_26_clean.csv", index=False)
print("Saved cleaned 5-season dataset.")