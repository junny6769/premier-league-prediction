CREATE OR REPLACE VIEW team_matches AS

SELECT
    season,
    date,
    home_team AS team,
    away_team AS opponent,
    'Home' AS venue,
    home_goals AS goals_for,
    away_goals AS goals_against,
    home_shots AS shots_for,
    away_shots AS shots_against,
    home_shots_on_target AS shots_on_target_for,
    away_shots_on_target AS shots_on_target_against,

    CASE
        WHEN full_time_result = 'H' THEN 3
        WHEN full_time_result = 'D' THEN 1
        ELSE 0
    END AS points

FROM matches

UNION ALL

SELECT
    season,
    date,
    away_team AS team,
    home_team AS opponent,
    'Away' AS venue,
    away_goals AS goals_for,
    home_goals AS goals_against,
    away_shots AS shots_for,
    home_shots AS shots_against,
    away_shots_on_target AS shots_on_target_for,
    home_shots_on_target AS shots_on_target_against,

    CASE
        WHEN full_time_result = 'A' THEN 3
        WHEN full_time_result = 'D' THEN 1
        ELSE 0
    END AS points

FROM matches;