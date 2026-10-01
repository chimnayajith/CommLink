import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


COMMUNITY_FILE = Path(
    "data/processed/louvain_communities.csv"
)

OUTPUT_DIR = Path("results/figures")


def plot_community_sizes():

    df = pd.read_csv(COMMUNITY_FILE)

    community_sizes = (
        df["community"]
        .value_counts()
        .sort_values(ascending=False)
    )

    plt.figure(figsize=(10, 6))

    community_sizes.plot(kind="bar")

    plt.xlabel("Community")
    plt.ylabel("Number of Users")
    plt.title("Louvain Community Size Distribution")

    plt.tight_layout()

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        OUTPUT_DIR /
        "community_size_distribution.png"
    )

    plt.savefig(
        output_file,
        dpi=300
    )

    plt.show()

    print(
        f"Saved figure to: {output_file}"
    )


if __name__ == "__main__":
    plot_community_sizes()

