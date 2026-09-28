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
2. For a new Neon database, run `sql/migrations/001_create_core_tables.up.sql`, then `sql/analysis_queries.sql` in the Neon SQL Editor. If `teams` and `matches` already exist, no table migration is needed.
3. With the virtual environment active, load the historical match data from the repository root:

```sh
python src/data_cleaning.py
```

Query `matches` or the `team_matches`, `team_season_summary`, and `team_venue_summary` views directly in Neon. The rest of the prediction pipeline has not yet been converted to direct database queries.

The matching `001_create_core_tables.down.sql` drops the views and both tables, including their data.

## Project Analysis

The Tableau analysis investigates five questions about Premier League performance and prediction.

### 1. How large is home advantage?

Across the 2016/17–2025/26 seasons:

- Home teams averaged **1.571 points per game**
- Away teams averaged **1.196 points per game**
- Home teams scored **0.275 more goals per game**
- Home win rate was **12.5 percentage points higher**

Home advantage was positive in almost every season analysed, with 2020/21 being a notable exception.

### 2. Does recent five-match form relate to the next match result?

Teams with stronger recent form recorded higher next-match win rates:

| Recent Form | Next-Match Win Rate |
|---|---:|
| Poor | 29.23% |
| Average | 35.41% |
| Good | 42.81% |
| Excellent | 54.05% |

The positive relationship was visible for both home and away fixtures.

### 3. How early does the Premier League table become reliable?

After **10 matches**, the average Spearman rank correlation between the current table and final standings was **0.809**, while teams were an average of **2.59 positions** from their eventual finishing position.

After **20 matches**, the correlation increased to **0.912** and the average position error decreased to **1.71 places**.

### 4. Is attacking or defensive performance more strongly related to points?

Both attacking and defensive performance showed strong relationships with points per game:

- Goals scored vs points per game: **r = 0.907**
- Goals conceded vs points per game: **r = -0.844**
- Multiple regression R²: **0.941**
- Standardised attacking coefficient: **+0.621**
- Standardised defensive coefficient: **-0.448**

Attacking performance showed the stronger association with points per game when both variables were considered together.

### 5. Is recent form more useful than season performance for predicting the next match?

Three models were compared using unseen-season backtesting:

| Model | Accuracy |
|---|---:|
| Season PPG | **65.33%** |
| Recent 5 PPG | 64.12% |
| Combined | 65.24% |

Season-to-date performance slightly outperformed recent five-match form. Adding recent form to the season model produced almost no improvement in predictive accuracy.

## 2026/27 Season Prediction

The prediction model estimates team attacking and defensive strength, calculates expected goals using Poisson distributions, and simulates the remainder of the season **10,000 times** using Monte Carlo simulation.

The current top five prediction is:

| Position | Team | Avg Points | Title Probability |
|---:|---|---:|---:|
| 1 | Man City | 79.2 | 47.3% |
| 2 | Arsenal | 78.4 | 41.2% |
| 3 | Liverpool | 70.5 | 10.0% |
| 4 | Chelsea | 58.2 | 0.4% |
| 5 | Newcastle | 58.1 | 0.5% |

The full prediction also includes average finishing position, Top 4 probability and relegation probability.

## Tableau Dashboard

The interactive Tableau dashboard presents the five analytical questions and the 2026/27 season prediction.

**Dashboard:** [View on Tableau Public](https://public.tableau.com/views/EPLanalyticspredictionproject/Overview?:language=en-GB&:sid=&:redirect=auth&:display_count=n&:origin=viz_share_link)

## Tech Stack

- **Python** — data cleaning, statistical analysis and predictive modelling
- **pandas / NumPy / SciPy** — data manipulation and modelling
- **PostgreSQL / Neon** — relational data storage and SQL analysis
- **Tableau** — interactive data visualisation
- **Poisson distributions** — match score modelling
- **Monte Carlo simulation** — season outcome simulation
- **Git / GitHub** — version control

## Limitations

Premier League match outcomes contain substantial randomness, so the results should be interpreted as probabilistic forecasts rather than deterministic predictions.

Promoted teams without sufficient recent Premier League history are assigned league-average attacking and defensive strengths.

The current model primarily uses historical team-level match performance and does not directly account for factors such as injuries, transfers, expected line-ups or player-level performance.

## Author

**Jun Han**  
BSc Mathematics and Statistics  
University of Manchester