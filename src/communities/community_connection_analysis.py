import pandas as pd
import networkx as nx
from pathlib import Path
from math import comb


PROCESSED_FILE = Path("data/processed/college_msg_processed.csv")
COMMUNITY_FILE = Path("data/processed/louvain_communities.csv")

OUTPUT_FILE = Path(
    "results/tables/community_connection_analysis.csv"
)


def build_graph(df):
    G = nx.Graph()

    for _, row in df.iterrows():
        u = int(row["source"])
        v = int(row["target"])

        if u == v:
            continue

        if G.has_edge(u, v):
            G[u][v]["weight"] += 1
        else:
            G.add_edge(u, v, weight=1)

    return G


def main():

    print("=" * 60)
    print("COMMUNITY-CONNECTION ANALYSIS")
    print("=" * 60)

    df = pd.read_csv(PROCESSED_FILE)
    communities = pd.read_csv(COMMUNITY_FILE)

    G = build_graph(df)

    community_map = dict(
        zip(
            communities["user"],
            communities["community"]
        )
    )

    # Only consider users that have community assignments
    nodes = [
        node for node in G.nodes()
        if node in community_map
    ]

    G = G.subgraph(nodes).copy()

    # --------------------------------------------------
    # Count community sizes
    # --------------------------------------------------

    community_sizes = (
        communities["community"]
        .value_counts()
        .to_dict()
    )

    # --------------------------------------------------
    # Possible pairs
    # --------------------------------------------------

    possible_same = sum(
        comb(size, 2)
        for size in community_sizes.values()
    )

    total_possible = comb(len(nodes), 2)

    possible_different = (
        total_possible - possible_same
    )

    # --------------------------------------------------
    # Observed edges
    # --------------------------------------------------

    same_edges = 0
    different_edges = 0

    same_weight = 0
    different_weight = 0

    for u, v, data in G.edges(data=True):

        if community_map[u] == community_map[v]:

            same_edges += 1
            same_weight += data["weight"]

        else:

            different_edges += 1
            different_weight += data["weight"]

    # --------------------------------------------------
    # Connection probabilities
    # --------------------------------------------------

    p_same = (
        same_edges / possible_same
        if possible_same > 0
        else 0
    )

    p_different = (
        different_edges / possible_different
        if possible_different > 0
        else 0
    )

    if p_different > 0:
        lift = p_same / p_different
    else:
        lift = 0

    # --------------------------------------------------
    # Print results
    # --------------------------------------------------

    print("\n===== COMMUNITY CONNECTION RESULTS =====")

    print(
        "Users with community assignments:",
        len(nodes)
    )

    print(
        "Number of communities:",
        len(community_sizes)
    )

    print("\nSame-community pairs:")
    print("Possible pairs:", possible_same)
    print("Observed edges:", same_edges)
    print(
        "Connection probability:",
        round(p_same, 6)
    )

    print("\nDifferent-community pairs:")
    print("Possible pairs:", possible_different)
    print("Observed edges:", different_edges)
    print(
        "Connection probability:",
        round(p_different, 6)
    )

    print(
        "\nProbability ratio:",
        round(lift, 3)
    )

    print("\nEdge weight comparison:")
    print("Same-community interaction weight:", same_weight)
    print(
        "Different-community interaction weight:",
        different_weight
    )

    # --------------------------------------------------
    # Save results
    # --------------------------------------------------

    result = pd.DataFrame({
        "Category": [
            "Same Community",
            "Different Communities"
        ],
        "Possible Pairs": [
            possible_same,
            possible_different
        ],
        "Observed Edges": [
            same_edges,
            different_edges
        ],
        "Connection Probability": [
            p_same,
            p_different
        ],
        "Total Interaction Weight": [
            same_weight,
            different_weight
        ]
    })

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    result.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        f"\nSaved analysis to: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()
