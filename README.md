# premier-league-prediction
An end-to-end data analytics project using Python and SQL to predict final Premier League standings.

Newly promoted teams without recent Premier League history are initialized at league-average attack and defence strength.

I compared multiple temporal weighting strategies through historical backtesting and selected the best-performing configuration, which is linear weighting. 

## Local development

Tested with Python 3.14. From the repository root:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Set up Neon

1. Copy `.env.example` to `.env` and set `DATABASE_URL` to your Neon direct PostgreSQL connection string. `DATABASE_URL_POOLED` is optional and not used by these scripts. `.env` is ignored by Git.
2. For a new Neon database, run `sql/create_tables.sql`, then `sql/analysis_queries.sql` in the Neon SQL Editor.
3. With the virtual environment active, load the historical match data from the repository root:

```sh
python src/data_cleaning.py
```

Query `matches` or the `team_matches`, `team_season_summary`, and `team_venue_summary` views directly in Neon. The rest of the prediction pipeline has not yet been converted to direct database queries.
