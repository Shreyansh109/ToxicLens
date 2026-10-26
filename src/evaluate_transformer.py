"""Evaluates the fine-tuned transformer on the validation split and picks thresholds.

Run from the project root:
    python -m src.evaluate_transformer
"""
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

from src.data_preprocessing import load_config
from src.transformer_scoring import load_transformer

GRID = [round(i / 100, 2) for i in range(2, 99)]
THREAT_CLOSE_UP = [0.05, 0.1, 0.2, 0.3, 0.4, 0.5]


def counts(pred, actual):
    tp = int((pred & actual).sum())
    fp = int((pred & ~actual).sum())
    fn = int((~pred & actual).sum())
    tn = int((~pred & ~actual).sum())
    return tp, fp, fn, tn


def f1_value(tp, fp, fn):
    denominator = 2 * tp + fp + fn
    return 2 * tp / denominator if denominator else 0.0


def summary(pred, actual):
    tp, fp, fn, tn = counts(pred, actual)
    return {
        "precision": tp / (tp + fp) if (tp + fp) else 0.0,
        "recall": tp / (tp + fn) if (tp + fn) else 0.0,
        "f1": f1_value(tp, fp, fn),
        "TP": tp, "FP": fp, "FN": fn, "TN": tn,
    }


def best_threshold(scores, actual):
    best_t, best_f1 = 0.5, -1.0
    for t in GRID:
        tp, fp, fn, _ = counts(scores >= t, actual)
        f1 = f1_value(tp, fp, fn)
        if f1 > best_f1:
            best_t, best_f1 = t, f1
    return best_t


def f1_at(scores, actual, t):
    tp, fp, fn, _ = counts(scores >= t, actual)
    return f1_value(tp, fp, fn)


def main():
    config = load_config()
    scorer, labels = load_transformer(config)
    folder = Path(config["paths"]["processed_data"])
    val = pd.read_csv(folder / "validation_split.csv")
    actual = val[labels].values == 1

    print(f"Scoring {len(val)} validation comments on the GPU. This takes a few minutes...")
    start = time.time()
    scores = scorer.predict_proba(val["comment_text"].tolist())
    print(f"Scoring finished in {(time.time() - start) / 60:.1f} minutes")
    np.save(folder / "val_scores_transformer.npy", scores)

    thresholds, rows = {}, {}
    for i, label in enumerate(labels):
        t = best_threshold(scores[:, i], actual[:, i])
        thresholds[label] = t
        row = summary(scores[:, i] >= t, actual[:, i])
        row["threshold"] = t
        row["f1_at_t_minus_0.05"] = f1_at(scores[:, i], actual[:, i], round(t - 0.05, 2))
        row["f1_at_t_plus_0.05"] = f1_at(scores[:, i], actual[:, i], round(t + 0.05, 2))
        rows[label] = row

    pred = scores >= np.array([thresholds[l] for l in labels])
    any_true = actual.any(axis=1)
    rows["any_label"] = summary(pred.any(axis=1), any_true)

    columns = ["threshold", "precision", "recall", "f1", "FP", "FN", "TP", "TN",
               "f1_at_t_minus_0.05", "f1_at_t_plus_0.05"]
    report = pd.DataFrame.from_dict(rows, orient="index")[columns]

    pd.set_option("display.width", 220)
    print()
    print("Validation results with the best-F1 threshold for each label")
    print(report.round(3).to_string())
    print()
    print(f"Macro F1: {np.mean([rows[l]['f1'] for l in labels]):.3f}")
    print(f"Accuracy if the model always said non_toxic: {(~any_true).mean():.3f}")
    print(f"Accuracy of the model (toxic vs non_toxic):  {(pred.any(axis=1) == any_true).mean():.3f}")

    t_idx = labels.index("threat")
    close = []
    for t in THREAT_CLOSE_UP:
        s = summary(scores[:, t_idx] >= t, actual[:, t_idx])
        close.append({
            "threshold": t, "flagged": s["TP"] + s["FP"], "caught": s["TP"],
            "missed": s["FN"], "false_tags": s["FP"],
            "precision": s["precision"], "recall": s["recall"],
        })
    print()
    print("Threat close-up: what each threshold would catch")
    print(pd.DataFrame(close).round(3).to_string(index=False))

    reports_dir = Path(config["paths"].get("reports", "reports"))
    reports_dir.mkdir(parents=True, exist_ok=True)
    report.round(4).to_csv(reports_dir / "transformer_validation_metrics.csv")

    suggestion = {
        "prediction_transformer": {
            "threshold": 0.5,
            "label_thresholds": thresholds,
            "review_margin": 0.15,
            "review_all_threats": True,
        }
    }
    print()
    print("Best-F1 thresholds (do not paste these into config.json yet):")
    print(json.dumps(suggestion, indent=2))


if __name__ == "__main__":
    main()