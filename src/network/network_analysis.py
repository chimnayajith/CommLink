import pandas as pd
import networkx as nx


PROCESSED_FILE = "data/processed/college_msg_processed.csv"


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


def analyze_network(G):
    print("===== NETWORK ANALYSIS =====")

    print("Nodes:", G.number_of_nodes())
    print("Edges:", G.number_of_edges())

    print("Density:", nx.density(G))

    print("Average degree:", sum(dict(G.degree()).values()) / G.number_of_nodes())

    components = list(nx.connected_components(G))

    print("Connected components:", len(components))

    largest_component = max(components, key=len)

    print("Largest component size:", len(largest_component))

    print("Smallest component size:", min(len(c) for c in components))

    degrees = [degree for _, degree in G.degree()]

    print("Minimum degree:", min(degrees))
    print("Maximum degree:", max(degrees))


def main():
    df = pd.read_csv(PROCESSED_FILE)

    G = build_graph(df)

    analyze_network(G)


if __name__ == "__main__":
    main()
