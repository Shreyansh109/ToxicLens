
"""Evaluate baseline and transformer once on the held-out test split.

Uses thresholds already fixed in config.json. Does not tune thresholds.
Run from the project root:
    python -m src.evaluate_test
"""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support

from src.data_preprocessing import load_config
from src.predict import load_model
from src.transformer_scoring import load_transformer


def score_one_label(y_true, y_pred):
    tn, fp, fn, tp = confusion_matrix(
        y_true, y_pred, labels=[0, 1]
    ).ravel()

    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="binary", pos_label=1, zero_division=0
    )

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "TP": tp,
        "FP": fp,
        "FN": fn,
        "TN": tn,
    }


def evaluate_model(name, scores, actual, labels, settings):
    default_threshold = settings["threshold"]
    label_settings = settings.get("label_thresholds", {})
    thresholds = np.array([
        label_settings.get(label, default_threshold)
        for label in labels
    ])

    predicted = scores >= thresholds
    rows = {}

    for i, label in enumerate(labels):
        rows[label] = score_one_label(actual[:, i], predicted[:, i])
        rows[label]["threshold"] = thresholds[i]

    any_actual = actual.any(axis=1)
    any_predicted = predicted.any(axis=1)

    rows["any_label"] = score_one_label(any_actual, any_predicted)
    rows["any_label"]["threshold"] = np.nan

    report = pd.DataFrame.from_dict(rows, orient="index")
    report.insert(0, "model", name)

    macro_f1 = np.mean([rows[label]["f1"] for label in labels])
    overall_accuracy = (any_actual == any_predicted).mean()
    always_negative_accuracy = (~any_actual).mean()

    print(f"\n{'=' * 65}")
    print(f"{name.upper()} TEST RESULTS")
    print(f"{'=' * 65}")
    print(f"Test comments: {len(actual)}")
    print(f"Macro F1 across six labels: {macro_f1:.4f}")
    print(f"Any-label accuracy: {overall_accuracy:.4f}")
    print(f"Always-non-toxic accuracy: {always_negative_accuracy:.4f}")
    print("\nPer-label and overall metrics:")
    print(report.drop(columns=["model"]).round(4).to_string())

    return report


def main():
    config = load_config()
    processed_dir = Path(config["paths"]["processed_data"])
    test_path = processed_dir / "test_split.csv"

    if not test_path.exists():
        raise FileNotFoundError(
            f"Test split not found: {test_path}\n"
            "Check that data preprocessing has created the split."
        )

    test = pd.read_csv(test_path)
    labels = config["labels"]

    required_columns = ["comment_text", *labels]
    missing = [column for column in required_columns
               if column not in test.columns]
    if missing:
        raise ValueError(f"Missing required test columns: {missing}")

    actual = test[labels].to_numpy(dtype=int) == 1
    texts = test["comment_text"].tolist()

    print("Held-out test evaluation")
    print(f"Test file: {test_path}")
    print(f"Comments: {len(test)}")
    print("Thresholds will be read from config.json.")
    print("No threshold search or model training will be performed.")

    # Evaluate the baseline using its existing fixed thresholds.
    baseline, baseline_labels = load_model(config)
    if baseline_labels != labels:
        raise ValueError(
            f"Baseline label order differs from config: {baseline_labels}"
        )

    baseline_scores = baseline.predict_proba(texts)
    baseline_report = evaluate_model(
        "baseline",
        baseline_scores,
        actual,
        labels,
        config["prediction"],
    )

    # Evaluate the transformer using its separate fixed thresholds.
    transformer, transformer_labels = load_transformer(config)
    if transformer_labels != labels:
        raise ValueError(
            f"Transformer label order differs from config: {transformer_labels}"
        )

    transformer_scores = transformer.predict_proba(texts)
    transformer_report = evaluate_model(
        "transformer",
        transformer_scores,
        actual,
        labels,
        config["prediction_transformer"],
    )

    reports_dir = Path(config["paths"].get("reports", "reports"))
    reports_dir.mkdir(parents=True, exist_ok=True)

    output = pd.concat(
        [baseline_report, transformer_report],
        axis=0,
        names=["model", "label"],
    )
    output_path = reports_dir / "test_metrics.csv"
    output.to_csv(output_path, index_label="label")

    print(f"\nSaved combined test report to: {output_path}")
    print("Keep these test results for final model comparison.")


if __name__ == "__main__":
    main()
