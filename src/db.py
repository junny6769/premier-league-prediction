import os
from pathlib import Path

from sqlalchemy import create_engine


def get_engine():
    url = os.environ.get("DATABASE_URL")
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not url and env_path.is_file():
        url = next(
            (line.partition("=")[2].strip().strip("\"'")
             for line in env_path.read_text().splitlines()
             if line.startswith("DATABASE_URL=")),
            None,
        )
    if not url:
        raise RuntimeError("Set DATABASE_URL or add it to .env")
    return create_engine(url.replace("postgresql://", "postgresql+psycopg://", 1))
