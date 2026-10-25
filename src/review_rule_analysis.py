"""Measures how well a "distance to the threshold" rule finds the model's mistakes.

Run from the project root:
    python -m src.review_rule_analysis
"""
from pathlib import Path

import numpy as np
import pandas as pd

from src.data_preprocessing import load_config
from src.predict import load_model

MARGINS = [0.02, 0.05, 0.1, 0.15, 0.2, 0.3]


def main():
    config = load_config()
    pipeline, labels = load_model(config)
    default_threshold = config["prediction"]["threshold"]
    label_thresholds = config["prediction"].get("label_thresholds", {})
    thresholds = np.array([label_thresholds.get(l, default_threshold) for l in labels])

    val_path = Path(config["paths"]["processed_data"]) / "validation_split.csv"
    val = pd.read_csv(val_path)
    scores = pipeline.predict_proba(val["comment_text"])
    actual_any = (val[labels].values == 1).any(axis=1)

    # Positive distance means flagged, negative means not flagged
    distance = (scores - thresholds).max(axis=1)
    flagged_any = distance >= 0
    is_error = flagged_any != actual_any

    t = labels.index("threat")
    threat_flagged = scores[:, t] >= thresholds[t]

    total_errors = int(is_error.sum())
    print(f"Comments: {len(val)}   Errors (any_label): {total_errors}   Error rate: {is_error.mean():.3f}")
    print(f"Comments with a threat flag: {int(threat_flagged.sum())}")
    print()

    rows = []
    for m in MARGINS:
        band = np.abs(distance) <= m
        both = band | threat_flagged
        rows.append({
            "margin": m,
            "reviewed": int(band.sum()),
            "reviewed_%": 100 * band.mean(),
            "errors_caught_%": 100 * (band & is_error).sum() / total_errors,
            "error_rate_inside_%": 100 * is_error[band].mean() if band.any() else np.nan,
            "error_rate_outside_%": 100 * is_error[~band].mean(),
            "reviewed_with_threat_rule": int(both.sum()),
            "errors_caught_with_threat_rule_%": 100 * (both & is_error).sum() / total_errors,
        })

    result = pd.DataFrame(rows)
    pd.set_option("display.width", 250)
    print(result.round(1).to_string(index=False))

    reports_dir = Path(config["paths"].get("reports", "reports"))
    reports_dir.mkdir(parents=True, exist_ok=True)
    out_path = reports_dir / "review_rule_validation.csv"
    result.round(3).to_csv(out_path, index=False)
    print()
    print("Saved results to", out_path)


if __name__ == "__main__":
    main()