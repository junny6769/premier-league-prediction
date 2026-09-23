-- Q5: Is recent form more useful than season performance for predicting the next match?

CREATE OR REPLACE VIEW q5_prediction_features AS

WITH match_history AS (

    SELECT
        season,
        team,
        date,
        venue,
        points,

        -- Number of previous matches
        COUNT(points) OVER (
            PARTITION BY season, team
            ORDER BY date
            ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
        ) AS previous_matches,

        -- Points from previous 5 matches
        SUM(points) OVER (
            PARTITION BY season, team
            ORDER BY date
            ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING
        ) AS recent_5_points,

        -- Total points earned before current match
        SUM(points) OVER (
            PARTITION BY season, team
            ORDER BY date
            ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
        ) AS season_points_before_match

    FROM team_matches

    -- Keep current 2026-27 results out of historical analysis/training
    WHERE season <> '2026-27'
)

SELECT
    season,
    team,
    date,
    venue,

    ROUND(
        recent_5_points / 5.0,
        3
    ) AS recent_5_ppg,

    ROUND(
        season_points_before_match / previous_matches::numeric,
        3
    ) AS season_ppg,

    points AS match_points,

    CASE
        WHEN points = 3 THEN 1
        ELSE 0
    END AS match_win

FROM match_history

WHERE previous_matches >= 5

ORDER BY
    season,
    team,
    date;

SELECT COUNT(*)
FROM q5_prediction_features;

SELECT *
FROM q5_prediction_features;