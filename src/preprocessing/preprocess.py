import pandas as pd
from pathlib import Path


RAW_FILE = Path("data/raw/CollegeMsg.txt")
PROCESSED_FILE = Path("data/processed/college_msg_processed.csv")


def load_data():
    columns = ["source", "target", "timestamp"]

    df = pd.read_csv(
        RAW_FILE,
        sep=r"\s+",
        names=columns
    )

    return df


def preprocess_data(df):
    # Remove rows with missing values
    df = df.dropna()

    # Convert IDs and timestamp to integers
    df["source"] = df["source"].astype(int)
    df["target"] = df["target"].astype(int)
    df["timestamp"] = df["timestamp"].astype(int)

    # Convert Unix timestamp to datetime
    df["datetime"] = pd.to_datetime(df["timestamp"], unit="s")

    # Sort interactions chronologically
    df = df.sort_values("timestamp").reset_index(drop=True)

    return df


def main():
    df = load_data()

    print("Original interactions:", len(df))

    df = preprocess_data(df)

    print("Processed interactions:", len(df))
    print("Unique users:", len(set(df["source"]) | set(df["target"])))
    print("Time range:", df["datetime"].min(), "to", df["datetime"].max())

    PROCESSED_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_FILE, index=False)

    print(f"Saved processed data to: {PROCESSED_FILE}")


if __name__ == "__main__":
    main()
