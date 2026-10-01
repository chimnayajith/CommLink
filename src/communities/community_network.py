import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path


PROCESSED_FILE = Path(
    "data/processed/college_msg_processed.csv"
)

COMMUNITY_FILE = Path(
    "data/processed/louvain_communities.csv"
)

OUTPUT_DIR = Path("results/figures")


def build_graph(df):
    G = nx.Graph()

    for _, row in df.iterrows():
        source = int(row["source"])
        target = int(row["target"])

        if G.has_edge(source, target):
            G[source][target]["weight"] += 1
        else:
            G.add_edge(source, target, weight=1)

    return G


def main():

    # Load data
    df = pd.read_csv(PROCESSED_FILE)

    communities = pd.read_csv(COMMUNITY_FILE)

    # Build graph
    G = build_graph(df)

    # Create user -> community mapping
    community_map = dict(
        zip(
            communities["user"],
            communities["community"]
        )
    )

    # Use spring layout
    print("Calculating network layout...")

    pos = nx.spring_layout(
        G,
        seed=42,
        k=0.15,
        iterations=50
    )

    # Assign community to each node
    node_communities = [
        community_map[node]
        for node in G.nodes()
    ]

    # Plot
    plt.figure(figsize=(14, 10))

    nx.draw_networkx_edges(
        G,
        pos,
        alpha=0.08,
        width=0.5
    )

    nx.draw_networkx_nodes(
        G,
        pos,
        node_color=node_communities,
        node_size=18,
        cmap="tab20",
        alpha=0.9
    )

    plt.title(
        "CollegeMsg Network - Louvain Communities"
    )

    plt.axis("off")

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        OUTPUT_DIR /
        "louvain_community_network.png"
    )

    plt.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()

    print(
        f"Saved figure to: {output_file}"
    )


if __name__ == "__main__":
    main()

