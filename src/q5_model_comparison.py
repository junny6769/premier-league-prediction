import pandas as pd
import numpy as np
import statsmodels.api as sm

# Load Q5 prediction features

df = pd.read_csv(
    "data/processed/q5_prediction_features.csv"
)

# Convert venue into numeric form ; Home = 1, Away = 0
df["venue_home"] = (
    df["venue"].str.lower() == "home"
).astype(int)

# Models to compare

models = {
    "Season PPG": [
        "season_ppg"
    ],

    "Recent 5 PPG": [
        "recent_5_ppg"
    ],

    "Combined": [
        "season_ppg",
        "recent_5_ppg"
    ]
}

# Seasons

seasons = sorted(
    df["season"].unique()
)

# First 5 seasons create the initial training period. Then each later season is tested using only previous seasons
test_seasons = seasons[5:]

# Storage

results = []
coefficient_results = []

# Helper: manual log loss

def calculate_log_loss(y_true, probabilities):

    eps = 1e-15

    probabilities = np.clip(
        probabilities,
        eps,
        1 - eps
    )

    return -np.mean(
        y_true * np.log(probabilities)
        + (1 - y_true)
        * np.log(1 - probabilities)
    )

# Time-based backtesting

for test_season in test_seasons:

    test_index = seasons.index(
        test_season
    )

    train_seasons = seasons[
        :test_index
    ]

    train = df[
        df["season"].isin(
            train_seasons
        )
    ].copy()

    test = df[
        df["season"] == test_season
    ].copy()

    y_train = train["match_win"]
    y_test = test["match_win"]


    print(
        f"\nTraining on {train_seasons}"
    )

    print(
        f"Testing on {test_season}"
    )

    # Run each model

    for model_name, form_features in models.items():

        train_model = train.copy()
        test_model = test.copy()

        # Standardise PPG variables using TRAINING data only
        for feature in form_features:

            mean = train_model[
                feature
            ].mean()

            std = train_model[
                feature
            ].std()

            train_model[
                feature
            ] = (
                train_model[feature]
                - mean
            ) / std

            test_model[
                feature
            ] = (
                test_model[feature]
                - mean
            ) / std

        # Venue is included in every model
        features = (
            form_features
            + ["venue_home"]
        )

        # Prepare regression matrices

        X_train = sm.add_constant(
            train_model[features],
            has_constant="add"
        )

        X_test = sm.add_constant(
            test_model[features],
            has_constant="add"
        )

        # Logistic regression

        model = sm.GLM(
            y_train,
            X_train,
            family=sm.families.Binomial()
        ).fit()

        # Predict win probabilities

        win_probability = model.predict(
            X_test
        )

        # Win if probability >= 50%
        predictions = (
            win_probability >= 0.5
        ).astype(int)

        # Accuracy

        accuracy = (
            predictions.values
            == y_test.values
        ).mean()

        # Log loss

        loss = calculate_log_loss(
            y_test.values,
            win_probability.values
        )

        # Store model performance

        results.append({
            "test_season": test_season,
            "model": model_name,
            "accuracy": accuracy,
            "accuracy_pct": accuracy * 100,
            "log_loss": loss
        })

        print(
            f"{model_name}: "
            f"Accuracy = {accuracy:.3f}, "
            f"Log Loss = {loss:.3f}"
        )

        # Save coefficients from Combined model

        if model_name == "Combined":

            for feature in [
                "season_ppg",
                "recent_5_ppg"
            ]:

                coefficient_results.append({
                    "test_season": test_season,
                    "feature": feature,
                    "standardised_beta":
                        model.params[feature]
                })

# Backtest results by season

results_df = pd.DataFrame(
    results
)

results_df.to_csv(
    "data/processed/"
    "q5_backtest_by_season.csv",
    index=False
)

# Average performance across test seasons

summary = (
    results_df
    .groupby(
        "model",
        as_index=False
    )
    .agg(
        accuracy=(
            "accuracy",
            "mean"
        ),

        accuracy_pct=(
            "accuracy_pct",
            "mean"
        ),

        log_loss=(
            "log_loss",
            "mean"
        )
    )
)

summary = summary.sort_values(
    "log_loss"
)

summary.to_csv(
    "data/processed/"
    "q5_model_comparison.csv",
    index=False
)

# Combined-model coefficient comparison

coefficients_df = pd.DataFrame(
    coefficient_results
)

coefficients_df.to_csv(
    "data/processed/"
    "q5_coefficients_by_season.csv",
    index=False
)

coefficient_summary = (
    coefficients_df
    .groupby(
        "feature",
        as_index=False
    )
    .agg(
        standardised_beta=(
            "standardised_beta",
            "mean"
        )
    )
)

coefficient_summary[
    "absolute_beta"
] = (
    coefficient_summary[
        "standardised_beta"
    ].abs()
)

coefficient_summary.to_csv(
    "data/processed/"
    "q5_coefficient_comparison.csv",
    index=False
)

# Print final results

print("\n==============================")
print("AVERAGE MODEL PERFORMANCE")
print("==============================")

print(
    summary.to_string(
        index=False
    )
)

print("\n==============================")
print("COMBINED MODEL COEFFICIENTS")
print("==============================")

print(
    coefficient_summary.to_string(
        index=False
    )
)