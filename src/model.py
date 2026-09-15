import pandas as pd
from scipy.stats import poisson


# Load team strengths
current_strengths = pd.read_csv(
    "data/processed/current_team_strengths.csv"
)

# Load league scoring averages
league_average = pd.read_csv(
    "data/processed/weighted_league_average.csv"
)

league_home_goals = league_average["league_home_goals"].iloc[0]
league_away_goals = league_average["league_away_goals"].iloc[0]

def get_team_strength(team):

    team_row = current_strengths[
        current_strengths["team"] == team
    ]

    if not team_row.empty:
        return team_row.iloc[0]

    # Team with no historical EPL data
    return pd.Series({
        "home_attack_strength": 1.0,
        "home_defence_strength": 1.0,
        "away_attack_strength": 1.0,
        "away_defence_strength": 1.0
    })

def calculate_expected_goals(
    home_team,
    away_team
):

    home = get_team_strength(home_team)
    away = get_team_strength(away_team)

    expected_home_goals = (
        league_home_goals
        * home["home_attack_strength"]
        * away["away_defence_strength"]
    )

    expected_away_goals = (
        league_away_goals
        * away["away_attack_strength"]
        * home["home_defence_strength"]
    )

    return (
        expected_home_goals,
        expected_away_goals
    )

def predict_match(home_team, away_team):

    home = current_strengths[
        current_strengths["team"] == home_team
    ].iloc[0]

    away = current_strengths[
        current_strengths["team"] == away_team
    ].iloc[0]

    # Expected goals
    expected_home_goals = (
        league_home_goals
        * home["home_attack_strength"]
        * away["away_defence_strength"]
    )

    expected_away_goals = (
        league_away_goals
        * away["away_attack_strength"]
        * home["home_defence_strength"]
    )

    home_win_probability = 0
    draw_probability = 0
    away_win_probability = 0

    most_likely_score = None
    highest_probability = 0

    # Calculate score probabilities from 0-0 to 10-10
    for home_goals in range(11):
        for away_goals in range(11):

            probability = (
                poisson.pmf(home_goals, expected_home_goals)
                * poisson.pmf(away_goals, expected_away_goals)
            )

            if probability > highest_probability:
                highest_probability = probability
                most_likely_score = (
                    home_goals,
                    away_goals
                )

            if home_goals > away_goals:
                home_win_probability += probability

            elif home_goals == away_goals:
                draw_probability += probability

            else:
                away_win_probability += probability

        total_probability = (
            home_win_probability
            + draw_probability
            + away_win_probability
        )
        
        print(f"Probability captured: {total_probability * 100:.6f}%")

    print(f"\n{home_team} vs {away_team}")

    print("\nExpected goals:")
    print(f"{home_team}: {expected_home_goals:.2f}")
    print(f"{away_team}: {expected_away_goals:.2f}")

    print("\nResult probabilities:")
    print(
        f"{home_team} win: "
        f"{home_win_probability * 100:.1f}%"
    )
    print(
        f"Draw: "
        f"{draw_probability * 100:.1f}%"
    )
    print(
        f"{away_team} win: "
        f"{away_win_probability * 100:.1f}%"
    )

    print(
        f"\nMost likely score: "
        f"{home_team} {most_likely_score[0]}-"
        f"{most_likely_score[1]} {away_team}"
    )

    return {
    "home_team": home_team,
    "away_team": away_team,
    "expected_home_goals": expected_home_goals,
    "expected_away_goals": expected_away_goals,
    "home_win_probability": home_win_probability,
    "draw_probability": draw_probability,
    "away_win_probability": away_win_probability,
    "most_likely_home_goals": most_likely_score[0],
    "most_likely_away_goals": most_likely_score[1]
}

predict_match("Man City", "Man United")