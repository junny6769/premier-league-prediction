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