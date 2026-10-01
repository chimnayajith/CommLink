import numpy as np

from sklearn.metrics import (
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


def evaluate_predictions(
    positive_edges,
    negative_edges,
    scores
):
    """
    Evaluate a link prediction method.

    Precision, Recall and F1:
        calculated using the top-k predictions,
        where k = number of positive test links.

    ROC-AUC and Average Precision:
        calculated using the raw prediction scores.
    """

    positive_set = set(positive_edges)

    all_edges = positive_edges + negative_edges

    y_true = np.array([
        1 if edge in positive_set else 0
        for edge in all_edges
    ])

    y_scores = np.array([
        scores.get(edge, 0.0)
        for edge in all_edges
    ])

    # ------------------------------------------
    # Top-k evaluation
    # ------------------------------------------

    k = len(positive_edges)

    ranked_indices = np.argsort(
        -y_scores,
        kind="stable"
    )

    predicted_indices = ranked_indices[:k]

    y_pred = np.zeros(len(y_true), dtype=int)

    y_pred[predicted_indices] = 1

    precision = precision_score(
        y_true,
        y_pred,
        zero_division=0
    )

    recall = recall_score(
        y_true,
        y_pred,
        zero_division=0
    )

    f1 = f1_score(
        y_true,
        y_pred,
        zero_division=0
    )

    # ------------------------------------------
    # Ranking metrics
    # ------------------------------------------

    if len(np.unique(y_true)) > 1:
        roc_auc = roc_auc_score(
            y_true,
            y_scores
        )

        average_precision = average_precision_score(
            y_true,
            y_scores
        )
    else:
        roc_auc = 0.0
        average_precision = 0.0

    return {
        "Precision": precision,
        "Recall": recall,
        "F1": f1,
        "ROC-AUC": roc_auc,
        "Average Precision": average_precision,
    }