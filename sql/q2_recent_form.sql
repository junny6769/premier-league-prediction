-- Q2: Does recent 5-match form relate to the next match result?

WITH rolling_form AS (

    SELECT
        season,
        team,
        date,
        venue,
        points,

        SUM(points) OVER (
            PARTITION BY season, team
            ORDER BY date
            ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING
        ) AS recent_5_points,

        COUNT(points) OVER (
            PARTITION BY season, team
            ORDER BY date
            ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING
        ) AS previous_matches

    FROM team_matches
)

SELECT
    season,
    team,
    date,
    venue,

    recent_5_points,

    ROUND(
        recent_5_points / 5.0,
        3
    ) AS recent_5_ppg,

    points AS next_match_points,

    CASE
        WHEN points = 3 THEN 1
        ELSE 0
    END AS next_match_win,

    CASE
        WHEN points = 3 THEN 'Win'
        WHEN points = 1 THEN 'Draw'
        ELSE 'Loss'
    END AS next_match_result

FROM rolling_form

WHERE previous_matches = 5

ORDER BY
    season,
    team,
    date;





WITH rolling_form AS (

    SELECT
        season,
        team,
        date,
        venue,
        points,

        SUM(points) OVER (
            PARTITION BY season, team
            ORDER BY date
            ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING
        ) AS recent_5_points,

        COUNT(points) OVER (
            PARTITION BY season, team
            ORDER BY date
            ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING
        ) AS previous_matches

    FROM team_matches
),

form_data AS (

    SELECT
        *,

        CASE
            WHEN recent_5_points <= 4 THEN 'Poor'
            WHEN recent_5_points <= 7 THEN 'Average'
            WHEN recent_5_points <= 10 THEN 'Good'
            ELSE 'Excellent'
        END AS form_group

    FROM rolling_form

    WHERE previous_matches = 5
)

SELECT
    form_group,

    COUNT(*) AS matches,

    ROUND(
        AVG(recent_5_points / 5.0)::numeric,
        3
    ) AS avg_recent_5_ppg,

    ROUND(
        (
            100.0 *
            SUM(CASE WHEN points = 3 THEN 1 ELSE 0 END)
            / COUNT(*)
        )::numeric,
        2
    ) AS next_match_win_rate,

    ROUND(
        AVG(points)::numeric,
        3
    ) AS next_match_ppg

FROM form_data

GROUP BY form_group

ORDER BY
    MIN(recent_5_points);