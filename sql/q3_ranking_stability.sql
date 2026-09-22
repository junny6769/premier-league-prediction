-- Q3: How well does early-season league position explain final league position?

-- 1. CREATE REUSABLE RANKING PROGRESSION VIEW

CREATE OR REPLACE VIEW q3_rank_progression AS

WITH ordered_matches AS (
    SELECT
        season,
        team,
        date,
        points,
        goals_for,
        goals_against,

        ROW_NUMBER() OVER (
            PARTITION BY season, team
            ORDER BY date
        ) AS matches_played

    FROM team_matches
),


cumulative_performance AS (
    SELECT
        season,
        team,
        date,
        matches_played,

        SUM(points) OVER (
            PARTITION BY season, team
            ORDER BY matches_played
            ROWS BETWEEN UNBOUNDED PRECEDING
                     AND CURRENT ROW
        ) AS cumulative_points,

        SUM(goals_for) OVER (
            PARTITION BY season, team
            ORDER BY matches_played
            ROWS BETWEEN UNBOUNDED PRECEDING
                     AND CURRENT ROW
        ) AS cumulative_goals_for,

        SUM(goals_against) OVER (
            PARTITION BY season, team
            ORDER BY matches_played
            ROWS BETWEEN UNBOUNDED PRECEDING
                     AND CURRENT ROW
        ) AS cumulative_goals_against

    FROM ordered_matches
),


league_positions AS (
    SELECT
        season,
        team,
        matches_played,

        cumulative_points,
        cumulative_goals_for,
        cumulative_goals_against,

        cumulative_goals_for
            - cumulative_goals_against
            AS cumulative_goal_difference,

        ROW_NUMBER() OVER (
            PARTITION BY season, matches_played

            ORDER BY
                cumulative_points DESC,
                (
                    cumulative_goals_for
                    - cumulative_goals_against
                ) DESC,
                cumulative_goals_for DESC,
                team
        ) AS current_position

    FROM cumulative_performance
),


final_positions AS (
    SELECT
        season,
        team,
        current_position AS final_position

    FROM league_positions

    WHERE matches_played = 38
)

SELECT
    lp.season,
    lp.team,
    lp.matches_played,

    lp.cumulative_points,
    lp.cumulative_goals_for,
    lp.cumulative_goals_against,
    lp.cumulative_goal_difference,

    lp.current_position,
    fp.final_position,

    ABS(
        lp.current_position
        - fp.final_position
    ) AS position_error

FROM league_positions lp

JOIN final_positions fp
    ON lp.season = fp.season
   AND lp.team = fp.team;

-- 2. CHECK THE VIEW

SELECT
    COUNT(*) AS total_rows
FROM q3_rank_progression;

-- 3. DETAILED RANKING PROGRESSION

SELECT
    season,
    team,
    matches_played,

    cumulative_points,
    cumulative_goal_difference,

    current_position,
    final_position,
    position_error

FROM q3_rank_progression

ORDER BY
    season,
    matches_played,
    current_position;

-- 4. RANKING STABILITY BY SEASON

SELECT
    season,
    matches_played,

    ROUND(
        CORR(
            current_position,
            final_position
        )::numeric,
        3
    ) AS spearman_correlation,

    ROUND(
        AVG(position_error)::numeric,
        3
    ) AS mean_position_error

FROM q3_rank_progression

GROUP BY
    season,
    matches_played

ORDER BY
    season,
    matches_played;

-- 5. AVERAGE RANKING STABILITY ACROSS ALL 10 SEASONS

WITH season_results AS (

    SELECT
        season,
        matches_played,

        CORR(
            current_position,
            final_position
        ) AS spearman_correlation,

        AVG(position_error)
            AS mean_position_error

    FROM q3_rank_progression

    GROUP BY
        season,
        matches_played
)

SELECT
    matches_played,

    ROUND(
        AVG(spearman_correlation)::numeric,
        3
    ) AS avg_spearman_correlation,

    ROUND(
        AVG(mean_position_error)::numeric,
        3
    ) AS mean_position_error

FROM season_results

GROUP BY matches_played

ORDER BY matches_played;

-- 6. USEFUL CHECKPOINTS

WITH season_results AS (

    SELECT
        season,
        matches_played,

        CORR(
            current_position,
            final_position
        ) AS spearman_correlation,

        AVG(position_error)
            AS mean_position_error

    FROM q3_rank_progression

    GROUP BY
        season,
        matches_played
),

overall_results AS (

    SELECT
        matches_played,

        AVG(spearman_correlation)
            AS avg_spearman_correlation,

        AVG(mean_position_error)
            AS mean_position_error

    FROM season_results

    GROUP BY matches_played
)

SELECT
    matches_played,

    ROUND(
        avg_spearman_correlation::numeric,
        3
    ) AS avg_spearman_correlation,

    ROUND(
        mean_position_error::numeric,
        3
    ) AS mean_position_error

FROM overall_results

WHERE matches_played IN (
    1,
    5,
    10,
    15,
    20,
    25,
    30,
    35,
    38
)

ORDER BY matches_played;