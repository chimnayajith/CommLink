import pandas as pd
import networkx as nx
from pathlib import Path


PROCESSED_FILE = Path("data/processed/college_msg_processed.csv")


def load_data():
    return pd.read_csv(PROCESSED_FILE)


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
    df = load_data()

    print("Loaded interactions:", len(df))

    G = build_graph(df)

    print("Number of nodes:", G.number_of_nodes())
    print("Number of edges:", G.number_of_edges())

    total_weight = sum(
        data["weight"]
        for _, _, data in G.edges(data=True)
    )

    print("Total edge weight:", total_weight)

    print("\nFirst 10 edges:")
    for source, target, data in list(G.edges(data=True))[:10]:
        print(source, target, data["weight"])


if __name__ == "__main__":
    main()
