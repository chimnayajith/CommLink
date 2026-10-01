import pandas as pd
from pathlib import Path


COMMUNITY_FILE = Path(
    "data/processed/louvain_communities.csv"
)

OUTPUT_FILE = Path(
    "results/tables/community_summary.csv"
)


def main():
    df = pd.read_csv(COMMUNITY_FILE)

    total_users = len(df)

    summary = (
        df["community"]
        .value_counts()
        .reset_index()
    )

    summary.columns = ["community", "number_of_users"]

    summary["percentage"] = (
        summary["number_of_users"] / total_users * 100
    ).round(2)

    summary = summary.sort_values(
        "number_of_users",
        ascending=False
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    summary.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("===== COMMUNITY SUMMARY =====")
    print(summary.to_string(index=False))

    print(
        f"\nSaved summary to: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()
