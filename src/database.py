import pandas as pd
from sqlalchemy import create_engine, text
from getpass import getpass
from urllib.parse import quote_plus


# Load cleaned Premier League data
df = pd.read_csv(
    "data/processed/premier_league_2021_26_clean.csv"
)
# Convert date and time strings to proper Python date/time types
df["date"] = pd.to_datetime(df["date"]).dt.date

df["time"] = pd.to_datetime(
    df["time"],
    format="%H:%M"
).dt.time

print("Rows to load:", len(df))


# Ask for PostgreSQL password
password = getpass("PostgreSQL password: ")
password = quote_plus(password)


# Connect to PostgreSQL
engine = create_engine(
    f"postgresql+psycopg://postgres:{password}@localhost:5432/premier_league"
)


# Check whether data already exists
with engine.connect() as connection:
    existing_rows = connection.execute(
        text("SELECT COUNT(*) FROM matches")
    ).scalar()


if existing_rows > 0:
    print(f"Database already contains {existing_rows} matches.")
    print("Data was not inserted again.")

else:
    df.to_sql(
        "matches",
        engine,
        if_exists="append",
        index=False
    )

    print(f"Successfully loaded {len(df)} matches into PostgreSQL.")