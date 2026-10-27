
"""Measure how well the human-review rule catches model errors.

Run from the project root:
    python -m src.review_rule_analysis

Evaluates both the baseline and transformer using validation data only.
"""
from pathlib import Path

import numpy as np
import pandas as pd

from src.data_preprocessing import load_config
from src.predict import load_model


MARGINS = [0.02, 0.05, 0.10, 0.15, 0.20, 0.30]


def analyze_review_rule(scores, actual, labels, thresholds, margins, name):
    """Measure review coverage for one model."""
    if scores.shape != actual.shape:
        raise ValueError(
            f"{name}: scores shape {scores.shape} does not match "
            f"actual labels shape {actual.shape}."
        )

    if scores.shape[1] != len(labels):
        raise ValueError(
            f"{name}: got {scores.shape[1]} score columns but "
            f"{len(labels)} labels."
        )

    if "threat" not in labels:
        raise ValueError("The label list must contain 'threat'.")

    # Positive distance means at least one label is flagged.
    # Exclude threat from general uncertainty.
    # Flagged threats are handled separately by the review rule.
    non_threat_indices = [
        i for i, label in enumerate(labels) if label != "threat"
    ]
    distance = (scores[:, non_threat_indices] -
                thresholds[non_threat_indices]).max(axis=1)
    flagged_any = distance >= 0
    actual_any = actual.any(axis=1)
    is_error = flagged_any != actual_any

    threat_index = labels.index("threat")
    threat_flagged = scores[:, threat_index] >= thresholds[threat_index]

    total_errors = int(is_error.sum())

    print(f"\n{'=' * 68}")
    print(f"Model: {name}")
    print(f"{'=' * 68}")
    print(f"Comments: {len(scores)}")
    print(f"Errors (any_label): {total_errors}")
    print(f"Error rate: {is_error.mean():.4f}")
    print(f"Comments with a threat flag: {int(threat_flagged.sum())}")

    rows = []

    for margin in margins:
        # Review if the overall decision is close to any threshold.
        near_threshold = np.abs(distance) <= margin

        # Also review every comment flagged as a threat.
        review = near_threshold | threat_flagged

        errors_near = int((near_threshold & is_error).sum())
        errors_reviewed = int((review & is_error).sum())

        rows.append({
            "margin": margin,
            "reviewed_near_threshold": int(near_threshold.sum()),
            "near_threshold_%": 100 * near_threshold.mean(),
            "errors_caught_near_%": (
                100 * errors_near / total_errors
                if total_errors else np.nan
            ),
            "error_rate_inside_%": (
                100 * is_error[near_threshold].mean()
                if near_threshold.any() else np.nan
            ),
            "error_rate_outside_%": (
                100 * is_error[~near_threshold].mean()
                if (~near_threshold).any() else np.nan
            ),
            "reviewed_with_threat_rule": int(review.sum()),
            "reviewed_with_threat_rule_%": 100 * review.mean(),
            "errors_caught_with_threat_rule_%": (
                100 * errors_reviewed / total_errors
                if total_errors else np.nan
            ),
        })

    result = pd.DataFrame(rows)

    pd.set_option("display.width", 250)
    print("\nReview-rule results:")
    print(result.round(2).to_string(index=False))

    return result


def main():
    config = load_config()
    labels = config["labels"]

    processed_dir = Path(config["paths"]["processed_data"])
    reports_dir = Path(config["paths"].get("reports", "reports"))
    reports_dir.mkdir(parents=True, exist_ok=True)

    val_path = processed_dir / "validation_split.csv"
    val = pd.read_csv(val_path)

    actual = val[labels].to_numpy(dtype=int) == 1

    # 1. Evaluate the baseline.
    pipeline, baseline_labels = load_model(config)

    if list(baseline_labels) != list(labels):
        raise ValueError(
            "Baseline model label order differs from config.json."
        )

    baseline_scores = np.asarray(
        pipeline.predict_proba(val["comment_text"]),
        dtype=float,
    )

    baseline_cfg = config["prediction"]
    baseline_default = baseline_cfg["threshold"]
    baseline_thresholds = np.array([
        baseline_cfg.get("label_thresholds", {}).get(
            label, baseline_default
        )
        for label in labels
    ])

    baseline_result = analyze_review_rule(
        scores=baseline_scores,
        actual=actual,
        labels=labels,
        thresholds=baseline_thresholds,
        margins=MARGINS,
        name="baseline",
    )

    baseline_path = reports_dir / "review_rule_validation.csv"
    baseline_result.round(3).to_csv(baseline_path, index=False)
    print(f"\nSaved baseline results to {baseline_path}")

    # 2. Evaluate the transformer using its saved validation scores.
    transformer_scores_path = (
        processed_dir / "val_scores_transformer.npy"
    )

    transformer_scores = np.load(transformer_scores_path)

    if transformer_scores.shape[0] != len(val):
        raise ValueError(
            "Transformer score count does not match validation rows: "
            f"{transformer_scores.shape[0]} scores vs {len(val)} rows."
        )

    transformer_cfg = config["prediction_transformer"]
    transformer_default = transformer_cfg["threshold"]
    transformer_thresholds = np.array([
        transformer_cfg.get("label_thresholds", {}).get(
            label, transformer_default
        )
        for label in labels
    ])

    transformer_result = analyze_review_rule(
        scores=transformer_scores,
        actual=actual,
        labels=labels,
        thresholds=transformer_thresholds,
        margins=MARGINS,
        name="transformer",
    )

    transformer_path = (
        reports_dir / "review_rule_validation_transformer.csv"
    )
    transformer_result.round(3).to_csv(
        transformer_path, index=False
    )
    print(f"\nSaved transformer results to {transformer_path}")


if __name__ == "__main__":
    main()
