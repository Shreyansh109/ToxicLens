"""Shows comments the baseline model gets wrong on the validation split.

Run from the project root:
    python -m src.error_analysis
    python -m src.error_analysis --n 25
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from src.data_preprocessing import load_config
from src.predict import load_model


def short(text, width=220):
    return " ".join(text.split())[:width]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=15, help="examples to show per error type")
    args = parser.parse_args()

    config = load_config()
    pipeline, labels = load_model(config)
    seed = config["random_seed"]
    default_threshold = config["prediction"]["threshold"]
    label_thresholds = config["prediction"].get("label_thresholds", {})
    thresholds = np.array([label_thresholds.get(l, default_threshold) for l in labels])

    val_path = Path(config["paths"]["processed_data"]) / "validation_split.csv"
    val = pd.read_csv(val_path)
    scores = pipeline.predict_proba(val["comment_text"])
    flagged = scores >= thresholds
    y = val[labels].values

    actual_any = y.max(axis=1) == 1
    flagged_any = flagged.any(axis=1)

    val["actual_labels"] = [", ".join(l for l, v in zip(labels, r) if v == 1) or "none" for r in y]
    val["flagged_labels"] = [", ".join(l for l, v in zip(labels, r) if v) or "none" for r in flagged]
    val["top_score"] = scores.max(axis=1).round(3)
    val["n_chars"] = val["comment_text"].str.len()

    missed = val[actual_any & ~flagged_any]
    false_alarms = val[~actual_any & flagged_any]

    def show(title, frame):
        count = min(args.n, len(frame))
        print("=" * 70)
        print(f"{title}: {len(frame)} comments (showing {count})")
        print("=" * 70)
        for _, row in frame.sample(n=count, random_state=seed).iterrows():
            print(f"[actual: {row['actual_labels']} | flagged: {row['flagged_labels']} | top score: {row['top_score']}]")
            print(short(row["comment_text"]))
            print()

    show("MISSED: labelled comments with no flag", missed)
    show("FALSE ALARMS: clean comments that were flagged", false_alarms)

    # Does comment length change how well the model does?
    buckets = pd.cut(
        val["n_chars"],
        bins=[0, 50, 150, 400, 1000, float("inf")],
        labels=["1-50", "51-150", "151-400", "401-1000", "over 1000"],
    )
    rows = []
    for name in buckets.cat.categories:
        in_bucket = (buckets == name).values
        pos = in_bucket & actual_any
        neg = in_bucket & ~actual_any
        rows.append({
            "length (chars)": name,
            "comments": int(in_bucket.sum()),
            "labelled": int(pos.sum()),
            "recall": (flagged_any & pos).sum() / pos.sum() if pos.sum() else np.nan,
            "false_alarm_rate": (flagged_any & neg).sum() / neg.sum() if neg.sum() else np.nan,
        })
    print("=" * 70)
    print("Performance by comment length (any_label)")
    print("=" * 70)
    print(pd.DataFrame(rows).round(3).to_string(index=False))

    # Full lists go to a file that Git ignores, because they contain comment text
    errors = pd.concat([missed.assign(error_type="missed"), false_alarms.assign(error_type="false_alarm")])
    out_path = Path(config["paths"]["processed_data"]) / "validation_errors.csv"
    errors[["id", "error_type", "actual_labels", "flagged_labels", "top_score", "comment_text"]].to_csv(
        out_path, index=False
    )
    print()
    print("Saved all errors to", out_path)


if __name__ == "__main__":
    main()