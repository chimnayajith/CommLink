import networkx as nx


def common_neighbors(G, edges):
    """
    Common Neighbors:
        CN(u, v) = |N(u) ∩ N(v)|
    """

    scores = {}

    for u, v in edges:
        scores[(u, v)] = len(
            list(nx.common_neighbors(G, u, v))
        )

    return scores


def jaccard_similarity(G, edges):
    """
    Jaccard Similarity:

        |N(u) ∩ N(v)|
        ----------------
        |N(u) ∪ N(v)|
    """

    scores = {}

    for u, v, score in nx.jaccard_coefficient(G, edges):
        scores[(u, v)] = score

    return scores


def adamic_adar(G, edges):
    """
    Adamic-Adar:

        sum(1 / log(degree(w)))

    over common neighbors w.
    """

    scores = {}

    for u, v, score in nx.adamic_adar_index(G, edges):
        scores[(u, v)] = score

    return scores


def preferential_attachment(G, edges):
    """
    Preferential Attachment:

        degree(u) * degree(v)
    """

    scores = {}

    for u, v, score in nx.preferential_attachment(
        G,
        edges
    ):
        scores[(u, v)] = score

    return scores


def run_baselines(G, edges):
    """
    Run all four baseline methods on exactly the same
    candidate edge set.
    """

    return {
        "Common Neighbors": common_neighbors(G, edges),
        "Jaccard": jaccard_similarity(G, edges),
        "Adamic-Adar": adamic_adar(G, edges),
        "Preferential Attachment": preferential_attachment(
            G,
            edges
        ),
    }