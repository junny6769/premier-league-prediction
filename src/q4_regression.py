import pandas as pd
import statsmodels.api as sm

# Load Q4 team-season data
df = pd.read_csv("data/processed/q4_team_season_performance.csv")

# Variables
X = df[[
    "goals_for_per_game",
    "goals_against_per_game"
]]

y = df["points_per_game"]

# Standardise variables so attack and defence can be compared fairly
X_standardised = (X - X.mean()) / X.std()
y_standardised = (y - y.mean()) / y.std()

# Add intercept
X_standardised = sm.add_constant(X_standardised)

# Multiple linear regression
model = sm.OLS(y_standardised, X_standardised).fit()

print(model.summary())

# Save key results
results = pd.DataFrame({
    "metric": [
        "Goals For per Game",
        "Goals Against per Game"
    ],
    "standardised_beta": [
        model.params["goals_for_per_game"],
        model.params["goals_against_per_game"]
    ],
    "p_value": [
        model.pvalues["goals_for_per_game"],
        model.pvalues["goals_against_per_game"]
    ]
})

print("\nStandardised coefficients:")
print(results)
print(f"\nR-squared: {model.rsquared:.3f}")

results.to_csv(
    "data/processed/q4_regression_results.csv",
    index=False
)