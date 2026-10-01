import random
from itertools import combinations

import networkx as nx
import pandas as pd


def build_graph(df):
    """
    Build an undirected interaction graph from the given interactions.
    Repeated interactions between the same users become one edge.
    """
    G = nx.Graph()

    for _, row in df.iterrows():
        u = int(row["source"])
        v = int(row["target"])

        if u == v:
            continue

        G.add_edge(u, v)

    return G


def temporal_train_test_split(df, test_ratio=0.2):
    """
    Split interactions chronologically.

    Earlier interactions -> training/observed network
    Later interactions   -> future interactions
    """

    df = df.sort_values("timestamp").reset_index(drop=True)

    split_index = int(len(df) * (1 - test_ratio))

    train_df = df.iloc[:split_index].copy()
    test_df = df.iloc[split_index:].copy()

    train_graph = build_graph(train_df)

    return train_df, test_df, train_graph


def get_future_positive_edges(train_graph, test_df):
    """
    Return unique future edges where both users were already
    observed in the training graph.

    This is necessary because the structural link prediction
    methods require both nodes to exist in the observed graph.
    """

    positive_edges = set()

    for _, row in test_df.iterrows():
        u = int(row["source"])
        v = int(row["target"])

        if u == v:
            continue

        # Both nodes must be known from the training period.
        if u not in train_graph or v not in train_graph:
            continue

        edge = tuple(sorted((u, v)))

        # Only genuinely new links count as positives.
        if not train_graph.has_edge(u, v):
            positive_edges.add(edge)

    return sorted(positive_edges)


def sample_negative_edges(
    train_graph,
    positive_edges,
    num_samples=None,
    seed=42
):
    """
    Generate negative examples.

    Negative examples are node pairs that:
      1. do not exist in the training graph
      2. do not appear as future positive links

    The number of negatives defaults to the number of positives.
    """

    if num_samples is None:
        num_samples = len(positive_edges)

    positive_set = set(positive_edges)

    nodes = list(train_graph.nodes())

    negatives = set()

    random.seed(seed)

    while len(negatives) < num_samples:
        u, v = random.sample(nodes, 2)

        edge = tuple(sorted((u, v)))

        if edge in positive_set:
            continue

        if train_graph.has_edge(u, v):
            continue

        negatives.add(edge)

    return sorted(negatives)


def create_evaluation_edges(
    train_graph,
    test_df,
    seed=42
):
    """
    Create balanced positive/negative evaluation edges.
    """

    positive_edges = get_future_positive_edges(
        train_graph,
        test_df
    )

    negative_edges = sample_negative_edges(
        train_graph,
        positive_edges,
        seed=seed
    )

    return positive_edges, negative_edges