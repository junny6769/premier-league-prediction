CREATE TABLE IF NOT EXISTS teams (
    team_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS matches (
    match_id SERIAL PRIMARY KEY,
    season VARCHAR(7) NOT NULL,
    date DATE NOT NULL,
    time TIME,

    home_team_id INTEGER NOT NULL REFERENCES teams(team_id),
    away_team_id INTEGER NOT NULL REFERENCES teams(team_id),

    home_goals INTEGER,
    away_goals INTEGER,
    full_time_result CHAR(1),

    half_time_home_goals INTEGER,
    half_time_away_goals INTEGER,
    half_time_result CHAR(1),

    home_shots INTEGER,
    away_shots INTEGER,
    home_shots_on_target INTEGER,
    away_shots_on_target INTEGER,

    home_fouls INTEGER,
    away_fouls INTEGER,

    home_corners INTEGER,
    away_corners INTEGER,

    home_yellow_cards INTEGER,
    away_yellow_cards INTEGER,

    home_red_cards INTEGER,
    away_red_cards INTEGER,

    UNIQUE (season, home_team_id, away_team_id)
);
