"""Compares model variants on the validation split.

Each variant is trained on the training split. Every variant gets its own
best-F1 threshold per label, so the comparison is fair.

Run from the project root:
    python -m src.experiments
"""
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import Pipeline

from src.data_preprocessing import load_config

THRESHOLD_GRID = [i / 100 for i in range(2, 99)]


def build(config, class_weight=None, lowercase=True):
    tfidf = config["tfidf"]
    lr = config["logistic_regression"]
    return Pipeline([
        ("tfidf", TfidfVectorizer(
            max_features=tfidf["max_features"],
            ngram_range=tuple(tfidf["ngram_range"]),
            min_df=tfidf["min_df"],
            lowercase=lowercase,
        )),
        ("classifier", OneVsRestClassifier(LogisticRegression(
            C=lr["C"], max_iter=lr["max_iter"], class_weight=class_weight,
        ))),
    ])


def best_f1_threshold(scores, actual):
    best_t, best_f1 = 0.5, -1.0
    for t in THRESHOLD_GRID:
        pred = scores >= t
        tp = (pred & actual).sum()
        fp = (pred & ~actual).sum()
        fn = (~pred & actual).sum()
        f1 = 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) else 0.0
        if f1 > best_f1:
            best_t, best_f1 = t, f1
    return best_t, best_f1


def main():
    config = load_config()
    labels = config["labels"]
    folder = Path(config["paths"]["processed_data"])
    train = pd.read_csv(folder / "train_split.csv")
    val = pd.read_csv(folder / "validation_split.csv")
    y_train = train[labels].values
    y_val = val[labels].values == 1
    actual_any = y_val.any(axis=1)

    variants = {
        "A: current setup": {},
        "B: balanced weights": {"class_weight": "balanced"},
        "C: keep capitals": {"lowercase": False},
        "D: balanced + capitals": {"class_weight": "balanced", "lowercase": False},
    }

    rows = []
    for name, options in variants.items():
        start = time.time()
        model = build(config, **options)
        model.fit(train["comment_text"], y_train)
        scores = model.predict_proba(val["comment_text"])

        row = {"variant": name}
        thresholds, f1s = [], []
        for i, label in enumerate(labels):
            t, f1 = best_f1_threshold(scores[:, i], y_val[:, i])
            thresholds.append(t)
            f1s.append(f1)
            row[f"{label}_f1"] = f1
        row["macro_f1"] = float(np.mean(f1s))

        flagged = (scores >= np.array(thresholds)).any(axis=1)
        row["any_recall"] = (flagged & actual_any).sum() / actual_any.sum()
        row["any_false_alarms"] = int((flagged & ~actual_any).sum())
        row["seconds"] = round(time.time() - start)
        rows.append(row)
        print("Finished", name)

    result = pd.DataFrame(rows).set_index("variant")
    pd.set_option("display.width", 220)
    print()
    print(result.round(3).T)

    reports_dir = Path(config["paths"].get("reports", "reports"))
    reports_dir.mkdir(parents=True, exist_ok=True)
    out_path = reports_dir / "experiments_validation.csv"
    result.round(4).to_csv(out_path)
    print()
    print("Saved results to", out_path)


if __name__ == "__main__":
    main()