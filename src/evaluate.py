"""Evaluates the baseline model on the validation split.

Run from the project root:
    python -m src.evaluate
"""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support

from src.data_preprocessing import load_config
from src.predict import load_model


def score_one_label(y_true, y_pred):
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="binary", pos_label=1, zero_division=0
    )
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "false_positive_rate": fp / (fp + tn),
        "TP": tp,
        "FP": fp,
        "FN": fn,
        "TN": tn,
    }


def main():
    config = load_config()
    pipeline, labels = load_model(config)
    default_threshold = config["prediction"]["threshold"]
    label_thresholds = config["prediction"].get("label_thresholds", {})
    thresholds = np.array([label_thresholds.get(l, default_threshold) for l in labels])

    val_path = Path(config["paths"]["processed_data"]) / "validation_split.csv"
    val = pd.read_csv(val_path)

    scores = pipeline.predict_proba(val["comment_text"])
    y_true = val[labels].values
    y_pred = (scores >= thresholds).astype(int)

    rows = {}
    for i, label in enumerate(labels):
        rows[label] = score_one_label(y_true[:, i], y_pred[:, i])

    # Overall result: toxic means at least one of the six labels
    any_true = y_true.max(axis=1)
    any_pred = y_pred.max(axis=1)
    rows["any_label"] = score_one_label(any_true, any_pred)

    report = pd.DataFrame.from_dict(rows, orient="index")
    report.insert(0, "threshold", list(thresholds) + [np.nan])

    pd.set_option("display.width", 200)
    print(f"Validation comments: {len(val)}")
    print()
    print(report.round(3))
    print()
    print(f"Accuracy if the model always said non_toxic: {(any_true == 0).mean():.3f}")
    print(f"Accuracy of the model (toxic vs non_toxic):  {(any_true == any_pred).mean():.3f}")

    reports_dir = Path(config["paths"].get("reports", "reports"))
    reports_dir.mkdir(parents=True, exist_ok=True)
    out_path = reports_dir / "baseline_validation_metrics_tuned.csv"
    report.round(4).to_csv(out_path)
    print()
    print("Saved report to", out_path)


if __name__ == "__main__":
    main()