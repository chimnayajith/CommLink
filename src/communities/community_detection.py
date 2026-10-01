import pandas as pd
import networkx as nx
import community.community_louvain as community_louvain
from networkx.algorithms.community import girvan_newman
from pathlib import Path
import random


PROCESSED_FILE = Path("data/processed/college_msg_processed.csv")
OUTPUT_FILE = Path("data/processed/louvain_communities.csv")


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


def detect_louvain(G):
    partition = community_louvain.best_partition(
        G,
        weight="weight",
        random_state=42
    )

    return partition


def detect_girvan_newman(G, target_communities):
    # Find the largest connected component
    largest_component = max(
        nx.connected_components(G),
        key=len
    )

    G_largest = G.subgraph(largest_component).copy()

    # Randomly sample 300 nodes for computational feasibility
    random.seed(42)

    sample_size = min(300, G_largest.number_of_nodes())

    nodes = random.sample(
        list(G_largest.nodes()),
        sample_size
    )

    G_sample = G_largest.subgraph(nodes).copy()

    print("Girvan-Newman sample:")
    print("Nodes:", G_sample.number_of_nodes())
    print("Edges:", G_sample.number_of_edges())

    generator = girvan_newman(G_sample)

    for partition in generator:
        communities = tuple(partition)

        if len(communities) >= target_communities:
            return G_sample, communities

    return G_sample, communities


def main():

    # ==========================================
    # LOAD DATA
    # ==========================================

    df = pd.read_csv(PROCESSED_FILE)

    # ==========================================
    # BUILD NETWORK
    # ==========================================

    G = build_graph(df)

    print("Nodes:", G.number_of_nodes())
    print("Edges:", G.number_of_edges())

    # ==========================================
    # LOUVAIN
    # ==========================================

    print("\n===== LOUVAIN =====")

    partition = detect_louvain(G)

    number_of_communities = len(
        set(partition.values())
    )

    modularity = community_louvain.modularity(
        partition,
        G,
        weight="weight"
    )

    print(
        "Number of communities:",
        number_of_communities
    )

    print("Modularity:", modularity)

    # Community sizes

    community_sizes = {}

    for community_id in partition.values():

        community_sizes[community_id] = (
            community_sizes.get(community_id, 0) + 1
        )

    print("\nCommunity sizes:")

    for community_id, size in sorted(
        community_sizes.items(),
        key=lambda x: x[1],
        reverse=True
    ):
        print(
            f"Community {community_id}: {size} nodes"
        )

    # Save Louvain assignments

    result = pd.DataFrame(
        partition.items(),
        columns=["user", "community"]
    )

    result = result.sort_values("user")

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    result.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        f"\nSaved community assignments to: "
        f"{OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()
