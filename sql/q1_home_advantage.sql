-- Q1: How large is home advantage in the Premier League?

-- 1. Overall home vs away performance

SELECT
    venue,
    COUNT(*) AS matches_played,

    ROUND(
        AVG(goals_for)::numeric,
        3
    ) AS avg_goals_for,

    ROUND(
        AVG(goals_against)::numeric,
        3
    ) AS avg_goals_against,

    ROUND(
        AVG(points)::numeric,
        3
    ) AS points_per_game,

    ROUND(
        100.0
        * SUM(CASE WHEN points = 3 THEN 1 ELSE 0 END)
        / COUNT(*),
        2
    ) AS win_rate

FROM team_matches

GROUP BY venue
ORDER BY venue;

-- 2. Home advantage by season

SELECT
    season,
    venue,

    COUNT(*) AS matches_played,

    ROUND(
        AVG(goals_for)::numeric,
        3
    ) AS avg_goals_for,

    ROUND(
        AVG(points)::numeric,
        3
    ) AS points_per_game,

    ROUND(
        100.0
        * SUM(CASE WHEN points = 3 THEN 1 ELSE 0 END)
        / COUNT(*),
        2
    ) AS win_rate

FROM team_matches

GROUP BY
    season,
    venue

ORDER BY
    season,
    venue;

-- 3. Home advantage gap by season

WITH venue_performance AS (

    SELECT
        season,
        venue,

        AVG(goals_for) AS avg_goals_for,
        AVG(points) AS points_per_game,

        100.0
        * SUM(CASE WHEN points = 3 THEN 1 ELSE 0 END)
        / COUNT(*) AS win_rate

    FROM team_matches

    GROUP BY
        season,
        venue
)

SELECT
    season,

    ROUND(
        MAX(
            CASE
                WHEN venue = 'Home'
                THEN avg_goals_for
            END
        )::numeric,
        3
    ) AS home_goals_per_game,

    ROUND(
        MAX(
            CASE
                WHEN venue = 'Away'
                THEN avg_goals_for
            END
        )::numeric,
        3
    ) AS away_goals_per_game,

    ROUND(
        (
            MAX(
                CASE
                    WHEN venue = 'Home'
                    THEN avg_goals_for
                END
            )
            -
            MAX(
                CASE
                    WHEN venue = 'Away'
                    THEN avg_goals_for
                END
            )
        )::numeric,
        3
    ) AS goal_advantage,

    ROUND(
        (
            MAX(
                CASE
                    WHEN venue = 'Home'
                    THEN points_per_game
                END
            )
            -
            MAX(
                CASE
                    WHEN venue = 'Away'
                    THEN points_per_game
                END
            )
        )::numeric,
        3
    ) AS ppg_advantage,

    ROUND(
        (
            MAX(
                CASE
                    WHEN venue = 'Home'
                    THEN win_rate
                END
            )
            -
            MAX(
                CASE
                    WHEN venue = 'Away'
                    THEN win_rate
                END
            )
        )::numeric,
        2
    ) AS win_rate_advantage

FROM venue_performance

GROUP BY season
ORDER BY season;

-- 4. Home advantage by team
-- Only teams with enough matches at both venues

WITH team_venue AS (

    SELECT
        team,
        venue,

        COUNT(*) AS matches_played,
        AVG(goals_for) AS goals_per_game,
        AVG(points) AS points_per_game

    FROM team_matches

    GROUP BY
        team,
        venue
),

team_comparison AS (

    SELECT
        team,

        MAX(
            CASE
                WHEN venue = 'Home'
                THEN matches_played
            END
        ) AS home_matches,

        MAX(
            CASE
                WHEN venue = 'Away'
                THEN matches_played
            END
        ) AS away_matches,

        MAX(
            CASE
                WHEN venue = 'Home'
                THEN goals_per_game
            END
        ) AS home_goals_per_game,

        MAX(
            CASE
                WHEN venue = 'Away'
                THEN goals_per_game
            END
        ) AS away_goals_per_game,

        MAX(
            CASE
                WHEN venue = 'Home'
                THEN points_per_game
            END
        ) AS home_ppg,

        MAX(
            CASE
                WHEN venue = 'Away'
                THEN points_per_game
            END
        ) AS away_ppg

    FROM team_venue

    GROUP BY team
)

SELECT
    team,

    ROUND(home_goals_per_game::numeric, 3)
        AS home_goals_per_game,

    ROUND(away_goals_per_game::numeric, 3)
        AS away_goals_per_game,

    ROUND(
        (home_goals_per_game - away_goals_per_game)::numeric,
        3
    ) AS home_goal_advantage,

    ROUND(home_ppg::numeric, 3)
        AS home_ppg,

    ROUND(away_ppg::numeric, 3)
        AS away_ppg,

    ROUND(
        (home_ppg - away_ppg)::numeric,
        3
    ) AS home_ppg_advantage

FROM team_comparison

WHERE home_matches >= 19
  AND away_matches >= 19

ORDER BY home_ppg_advantage DESC;