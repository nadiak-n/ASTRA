
import pandas as pd
from pathlib import Path


# Get the project folder
BASE_DIR = Path(__file__).resolve().parent.parent

# Dataset path
DATA_PATH = BASE_DIR / "data" / "sample_health_data.csv"


def load_health_data():

    # Read CSV file
    df = pd.read_csv(DATA_PATH)

    # Convert timestamp to datetime
    df["timestamp"] = pd.to_datetime(
    df["timestamp"],
    format="mixed"
)

    return df
