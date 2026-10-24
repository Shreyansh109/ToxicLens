"""Shows how precision and recall change with the threshold, per label.

Run from the project root:
    python -m src.threshold_analysis
"""
from pathlib import Path

import numpy as np
import pandas as pd

from src.data_preprocessing import load_config
from src.predict import load_model

SHOW_THRESHOLDS = [0.05, 0.1, 0.2, 0.3, 0.4, 0.5]


def metrics_from(pred, actual):
    """pred and actual are boolean arrays of the same length."""
    tp = int((pred & actual).sum())
    fp = int((pred & ~actual).sum())
    fn = int((~pred & actual).sum())
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "flagged": tp + fp,
        "false_alarms": fp,
        "missed": fn,
    }


def main():
    config = load_config()
    pipeline, labels = load_model(config)
    recall_target = config["prediction"].get("recall_target", 0.8)

    val_path = Path(config["paths"]["processed_data"]) / "validation_split.csv"
    val = pd.read_csv(val_path)
    scores = pipeline.predict_proba(val["comment_text"])
    y_true = val[labels].values == 1

    grid = [i / 100 for i in range(2, 99)]
    pd.set_option("display.width", 200)

    sweeps = []
    best_rows, target_rows = [], []
    best_thresholds, target_thresholds = {}, {}

    for i, label in enumerate(labels):
        actual = y_true[:, i]
        table = pd.DataFrame(
            [{"threshold": t, **metrics_from(scores[:, i] >= t, actual)} for t in grid]
        )
        table.insert(0, "label", label)
        sweeps.append(table)

        print(f"=== {label} ({int(actual.sum())} real examples in validation) ===")
        print(table[table["threshold"].isin(SHOW_THRESHOLDS)].drop(columns="label").round(3).to_string(index=False))
        print()

        best = table.loc[table["f1"].idxmax()]
        best_thresholds[label] = best["threshold"]
        best_rows.append({"label": label, **best.drop("label").to_dict()})

        reachable = table[table["recall"] >= recall_target]
        if len(reachable):
            chosen = reachable.loc[reachable["threshold"].idxmax()]
            target_thresholds[label] = chosen["threshold"]
            target_rows.append({"label": label, **chosen.drop("label").to_dict()})
        else:
            target_rows.append({"label": label, "threshold": "not reached"})

    best_df = pd.DataFrame(best_rows).set_index("label")
    target_df = pd.DataFrame(target_rows).set_index("label")

    print("Rule 1: threshold with the best F1")
    print(best_df.round(3))
    print()
    print(f"Rule 2: highest threshold with recall >= {recall_target}")
    print(target_df.round(3))
    print()

    # Overall result when each label uses its own threshold
    actual_any = y_true.any(axis=1)
    overall = {"current (0.5 for all labels)": (scores >= 0.5).any(axis=1)}
    overall["rule 1 (best F1)"] = (scores >= np.array([best_thresholds[l] for l in labels])).any(axis=1)
    if len(target_thresholds) == len(labels):
        overall["rule 2 (recall target)"] = (
            scores >= np.array([target_thresholds[l] for l in labels])
        ).any(axis=1)
    else:
        print("Rule 2 could not be applied to every label, so it is left out of the overall comparison.")
    overall_df = pd.DataFrame(
        {name: metrics_from(pred, actual_any) for name, pred in overall.items()}
    ).T
    print("Overall toxic vs non_toxic on validation:")
    print(overall_df.round(3))

    reports_dir = Path(config["paths"].get("reports", "reports"))
    reports_dir.mkdir(parents=True, exist_ok=True)
    pd.concat(sweeps).round(4).to_csv(reports_dir / "threshold_sweep_validation.csv", index=False)
    print()
    print("Saved sweep to", reports_dir / "threshold_sweep_validation.csv")


if __name__ == "__main__":
    main()