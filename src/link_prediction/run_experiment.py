from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

import community.community_louvain as community_louvain

from src.evaluation.metrics import evaluate_predictions
from src.evaluation.temporal_split import (
    create_evaluation_edges,
    temporal_train_test_split,
)
from src.link_prediction.baselines import run_baselines
from src.link_prediction.community_aware import (
    community_aware_common_neighbors,
)


PROCESSED_FILE = Path(
    "data/processed/college_msg_processed.csv"
)

RESULTS_TABLE = Path(
    "results/tables/link_prediction_results.csv"
)

RESULTS_FIGURE = Path(
    "results/figures/link_prediction_comparison.png"
)

COMMUNITY_FILE = Path(
    "results/tables/training_louvain_communities.csv"
)


def load_data():
    return pd.read_csv(PROCESSED_FILE)


def build_training_graph(train_df):
    G = nx.Graph()

    for _, row in train_df.iterrows():

        u = int(row["source"])
        v = int(row["target"])

        if u == v:
            continue

        if G.has_edge(u, v):
            G[u][v]["weight"] += 1
        else:
            G.add_edge(
                u,
                v,
                weight=1
            )

    return G


def detect_training_communities(G):
    """
    Run Louvain ONLY on the training graph.

    This prevents future information from leaking into
    the community-aware predictor.
    """

    partition = community_louvain.best_partition(
        G,
        weight="weight",
        random_state=42
    )

    return partition


def save_communities(partition):
    COMMUNITY_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df = pd.DataFrame(
        partition.items(),
        columns=[
            "user",
            "community"
        ]
    )

    df = df.sort_values("user")

    df.to_csv(
        COMMUNITY_FILE,
        index=False
    )


def save_results(results):
    RESULTS_TABLE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df = pd.DataFrame(results)

    df.to_csv(
        RESULTS_TABLE,
        index=False
    )

    return df


def plot_results(results_df):
    RESULTS_FIGURE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    metrics = [
        "Precision",
        "Recall",
        "F1",
        "ROC-AUC",
        "Average Precision",
    ]

    methods = results_df["Method"]

    x = range(len(methods))

    width = 0.15

    fig, ax = plt.subplots(
        figsize=(14, 7)
    )

    for i, metric in enumerate(metrics):

        values = results_df[metric]

        positions = [
            value + (i - 2) * width
            for value in x
        ]

        ax.bar(
            positions,
            values,
            width,
            label=metric
        )

    ax.set_xlabel("Method")
    ax.set_ylabel("Score")
    ax.set_title(
        "Link Prediction Method Comparison"
    )

    ax.set_xticks(list(x))
    ax.set_xticklabels(
        methods,
        rotation=20,
        ha="right"
    )

    ax.set_ylim(0, 1)

    ax.legend()

    fig.tight_layout()

    fig.savefig(
        RESULTS_FIGURE,
        dpi=300
    )

    plt.close(fig)


def main():

    print("=" * 60)
    print("COMMUNITY-AWARE TEMPORAL LINK PREDICTION")
    print("=" * 60)

    # ------------------------------------------
    # Load data
    # ------------------------------------------

    df = load_data()

    print("\nTotal interactions:", len(df))

    # ------------------------------------------
    # Temporal split
    # ------------------------------------------

    train_df, test_df, _ = temporal_train_test_split(
        df,
        test_ratio=0.20
    )

    print(
        "Training interactions:",
        len(train_df)
    )

    print(
        "Future interactions:",
        len(test_df)
    )

    print(
        "Training period:",
        pd.to_datetime(
            train_df["timestamp"],
            unit="s"
        ).min(),
        "to",
        pd.to_datetime(
            train_df["timestamp"],
            unit="s"
        ).max()
    )

    print(
        "Test period:",
        pd.to_datetime(
            test_df["timestamp"],
            unit="s"
        ).min(),
        "to",
        pd.to_datetime(
            test_df["timestamp"],
            unit="s"
        ).max()
    )

    # ------------------------------------------
    # Training graph
    # ------------------------------------------

    G = build_training_graph(train_df)

    print("\nTraining graph")
    print("Nodes:", G.number_of_nodes())
    print("Edges:", G.number_of_edges())

    # ------------------------------------------
    # Future positive links + negatives
    # ------------------------------------------

    positive_edges, negative_edges = (
        create_evaluation_edges(
            G,
            test_df,
            seed=42
        )
    )

    print(
        "\nFuture new links:",
        len(positive_edges)
    )

    print(
        "Negative links:",
        len(negative_edges)
    )

    # ------------------------------------------
    # Candidate edges
    # ------------------------------------------

    candidate_edges = (
        positive_edges +
        negative_edges
    )

    # ------------------------------------------
    # Louvain on TRAINING graph
    # ------------------------------------------

    print("\nRunning Louvain on training graph...")

    communities = detect_training_communities(G)

    print(
        "Number of training communities:",
        len(set(communities.values()))
    )

    modularity = community_louvain.modularity(
        communities,
        G,
        weight="weight"
    )

    print(
        "Training modularity:",
        modularity
    )

    save_communities(communities)

    # ------------------------------------------
    # Classical baselines
    # ------------------------------------------

    print("\nRunning classical baselines...")

    baseline_scores = run_baselines(
        G,
        candidate_edges
    )

    # ------------------------------------------
    # Community-aware method
    # ------------------------------------------

    print(
        "Running community-aware prediction..."
    )

    community_scores = (
        community_aware_common_neighbors(
            G,
            candidate_edges,
            communities
        )
    )

    all_scores = {
        **baseline_scores,
        "Community-Aware": community_scores,
    }

    # ------------------------------------------
    # Evaluation
    # ------------------------------------------

    print("\nEvaluating methods...")

    results = []

    for method, scores in all_scores.items():

        print(
            f"  Evaluating {method}..."
        )

        metrics = evaluate_predictions(
            positive_edges,
            negative_edges,
            scores
        )

        row = {
            "Method": method,
            **metrics,
        }

        results.append(row)

    # ------------------------------------------
    # Save results
    # ------------------------------------------

    results_df = save_results(
        results
    )

    print("\n===== RESULTS =====")
    print(
        results_df.to_string(
            index=False
        )
    )

    # ------------------------------------------
    # Plot
    # ------------------------------------------

    plot_results(
        results_df
    )

    print(
        "\nSaved results to:",
        RESULTS_TABLE
    )

    print(
        "Saved plot to:",
        RESULTS_FIGURE
    )

    print(
        "Saved communities to:",
        COMMUNITY_FILE
    )


if __name__ == "__main__":
    main()