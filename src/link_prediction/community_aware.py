import networkx as nx


def community_aware_common_neighbors(
    G,
    edges,
    communities
):
    """
    Community-aware Common Neighbors.

    Standard Soundarajan-Hopcroft formulation:

        score(u, v)
        = CN(u, v)
        + number of common neighbors that belong
          to the same community as u and v

    If u and v belong to different communities,
    there is no community bonus.

    communities:
        Dictionary mapping node -> community ID.
    """

    scores = {}

    for u, v in edges:

        common = list(
            nx.common_neighbors(G, u, v)
        )

        score = len(common)

        # Community bonus is only applied when
        # both candidate nodes belong to the same community.
        if communities.get(u) == communities.get(v):

            community = communities[u]

            for w in common:
                if communities.get(w) == community:
                    score += 1

        scores[(u, v)] = score

    return scores