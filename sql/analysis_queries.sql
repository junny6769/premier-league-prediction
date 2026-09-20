CREATE OR REPLACE VIEW team_matches AS

SELECT
    season,
    date,
    home.name AS team,
    away.name AS opponent,
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

FROM matches AS m
JOIN teams AS home ON home.team_id = m.home_team_id
JOIN teams AS away ON away.team_id = m.away_team_id

UNION ALL

SELECT
    season,
    date,
    away.name AS team,
    home.name AS opponent,
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

FROM matches AS m
JOIN teams AS home ON home.team_id = m.home_team_id
JOIN teams AS away ON away.team_id = m.away_team_id;

CREATE OR REPLACE VIEW team_season_summary AS

SELECT
    season,
    team,

    COUNT(*) AS matches_played,

    SUM(
        CASE
            WHEN points = 3 THEN 1
            ELSE 0
        END
    ) AS wins,

    SUM(
        CASE
            WHEN points = 1 THEN 1
            ELSE 0
        END
    ) AS draws,

    SUM(
        CASE
            WHEN points = 0 THEN 1
            ELSE 0
        END
    ) AS losses,

    SUM(goals_for) AS goals_for,
    SUM(goals_against) AS goals_against,

    SUM(goals_for) - SUM(goals_against)
        AS goal_difference,

    SUM(points) AS points,

    ROUND(AVG(goals_for), 2)
        AS goals_per_game,

    ROUND(AVG(goals_against), 2)
        AS goals_conceded_per_game,

    ROUND(AVG(shots_for), 2)
        AS shots_per_game,

    ROUND(AVG(shots_on_target_for), 2)
        AS shots_on_target_per_game

FROM team_matches

GROUP BY season, team;

CREATE OR REPLACE VIEW team_venue_summary AS

SELECT
    season,
    team,
    venue,

    COUNT(*) AS matches_played,

    ROUND(AVG(goals_for), 3)
        AS goals_for_per_game,

    ROUND(AVG(goals_against), 3)
        AS goals_against_per_game,

    ROUND(AVG(shots_for), 3)
        AS shots_per_game,

    ROUND(AVG(shots_on_target_for), 3)
        AS shots_on_target_per_game

FROM team_matches

GROUP BY season, team, venue;
