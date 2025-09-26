import pandas as pd
import sqlite3
from pathlib import Path

def load_csv(path:str | Path) -> pd.DataFrame:
    """Load a CSV file into a pandas DataFrame."""
    path = Path(path)
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"The file {path} does not exist.")
    df = pd.read_csv(path)
    print(f"Loaded CSV: {path} | shape={df.shape}")
    return df

def load_json(path:str | Path) -> pd.DataFrame:
    """Load a JSON file into a pandas DataFrame."""
    path = Path(path)
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"The file {path} does not exist.")
    df = pd.read_json(path)
    print(f"Loaded JSON: {path} | shape={df.shape}")
    return df

def load_sqlite(db_path:str | Path, query:str) -> pd.DataFrame:
    """Load data from a SQLite database into a pandas DataFrame."""
    db_path = Path(db_path)
    if not db_path.exists() or not db_path.is_file():
        raise FileNotFoundError(f"The database file {db_path} does not exist.")
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(query, conn)
    conn.close()
    print(f"Loaded SQLite DB: {db_path} | shape={df.shape}")
    return df


def save_csv(df:pd.DataFrame, path:str | Path) -> None:
    """Save a pandas DataFrame to a CSV file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    print(f"Saved CSV: {path} | shape={df.shape}")