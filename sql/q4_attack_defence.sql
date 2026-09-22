-- Q4: Is attacking strength or defensive strength more strongly associated with points per game?

-- 1. CREATE TEAM-SEASON PERFORMANCE VIEW

CREATE OR REPLACE VIEW q4_team_season_performance AS

SELECT
    season,
    team,

    COUNT(*) AS matches_played,

    SUM(goals_for) AS goals_for,
    SUM(goals_against) AS goals_against,

    SUM(goals_for) - SUM(goals_against)
        AS goal_difference,

    SUM(points) AS total_points,

    ROUND(
        AVG(goals_for)::numeric,
        3
    ) AS goals_for_per_game,

    ROUND(
        AVG(goals_against)::numeric,
        3
    ) AS goals_against_per_game,

    ROUND(
        (
            AVG(goals_for)
            - AVG(goals_against)
        )::numeric,
        3
    ) AS goal_difference_per_game,

    ROUND(
        AVG(points)::numeric,
        3
    ) AS points_per_game

FROM team_matches

GROUP BY
    season,
    team;


SELECT
    season,
    team,
    matches_played,

    goals_for_per_game,
    goals_against_per_game,
    goal_difference_per_game,
    points_per_game

FROM q4_team_season_performance

ORDER BY
    season,
    points_per_game DESC;

-- 2. CORRELATION WITH POINTS PER GAME

SELECT
    'Goals For per Game' AS metric,

    ROUND(
        CORR(
            goals_for_per_game,
            points_per_game
        )::numeric,
        3
    ) AS correlation_with_ppg

FROM q4_team_season_performance

UNION ALL

SELECT
    'Goals Against per Game' AS metric,

    ROUND(
        CORR(
            goals_against_per_game,
            points_per_game
        )::numeric,
        3
    ) AS correlation_with_ppg

FROM q4_team_season_performance

UNION ALL

SELECT
    'Goal Difference per Game' AS metric,

    ROUND(
        CORR(
            goal_difference_per_game,
            points_per_game
        )::numeric,
        3
    ) AS correlation_with_ppg

FROM q4_team_season_performance;

-- 3. CORRELATION MATRIX

WITH metric_values AS (

    SELECT
        season,
        team,
        metric,
        value

    FROM q4_team_season_performance

    CROSS JOIN LATERAL (

        VALUES
            (
                'Goals For',
                goals_for_per_game::double precision
            ),
            (
                'Goals Against',
                goals_against_per_game::double precision
            ),
            (
                'Goal Difference',
                goal_difference_per_game::double precision
            ),
            (
                'Points per Game',
                points_per_game::double precision
            )

    ) AS metrics(metric, value)
),

correlation_matrix AS (

    SELECT
        a.metric AS metric_1,
        b.metric AS metric_2,

        CORR(
            a.value,
            b.value
        ) AS correlation

    FROM metric_values a

    JOIN metric_values b
        ON a.season = b.season
       AND a.team = b.team

    GROUP BY
        a.metric,
        b.metric
)

SELECT
    metric_1,
    metric_2,

    ROUND(
        correlation::numeric,
        3
    ) AS correlation

FROM correlation_matrix

ORDER BY
    metric_1,
    metric_2;