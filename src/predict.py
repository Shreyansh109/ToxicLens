"""Prediction functions for the baseline toxicity model.

Command line, from the project root:
    python -m src.predict                         (runs built-in examples)
    python -m src.predict "your text here"        (analyses your own text)
    python -m src.predict --validation-sample 5   (random validation comments)
"""
import argparse
import json
from pathlib import Path

import joblib
import pandas as pd

from src.data_preprocessing import load_config

# Jigsaw label name -> project category name
CATEGORY_NAMES = {
    "insult": "insult",
    "threat": "threat",
    "identity_hate": "identity_based_hate",
    "obscene": "obscene_language",
}

DEFAULT_EXAMPLES = [
    "Thanks for the helpful edit, I appreciate it.",
    "I hate Mondays.",
    "That movie was killer, I loved every minute.",
    "You are an idiot and nobody wants you here.",
    "I will find you and hurt you.",
    "The article needs better sources for the second paragraph.",
]


def load_model(config=None):
    config = config or load_config()
    models_dir = Path(config["paths"]["models"])
    model_path = models_dir / "baseline_pipeline.joblib"
    labels_path = models_dir / "baseline_labels.json"
    if not model_path.exists() or not labels_path.exists():
        raise FileNotFoundError(
            "Trained model not found. Run: python -m src.train_baseline"
        )
    pipeline = joblib.load(model_path)
    with open(labels_path) as f:
        labels = json.load(f)
    return pipeline, labels


def predict_texts(texts, pipeline, labels, config):
    """Takes a list of strings and returns one result dictionary per string."""
    if not texts:
        raise ValueError("No text supplied.")
    for i, text in enumerate(texts):
        if not isinstance(text, str) or not text.strip():
            raise ValueError(f"Item {i} is empty or not text.")

    settings = config["prediction"]
    default_threshold = settings["threshold"]
    thresholds = settings.get("label_thresholds", {})
    margin = settings.get("review_margin", 0.15)
    review_all_threats = settings.get("review_all_threats", True)

    # Each row holds six independent scores, in the saved label order
    all_scores = pipeline.predict_proba(texts)

    results = []
    for text, row in zip(texts, all_scores):
        scores = {label: round(float(s), 4) for label, s in zip(labels, row)}
        flagged = [
            label for label, s in scores.items()
            if s >= thresholds.get(label, default_threshold)
        ]

        # Distance to the flag/no-flag boundary: positive means flagged
        distance = max(
            s - thresholds.get(label, default_threshold) for label, s in scores.items()
        )
        near_boundary = abs(distance) <= margin
        threat_flagged = review_all_threats and "threat" in flagged

        results.append({
            "text": text,
            "label": "toxic" if flagged else "non_toxic",
            "flagged_labels": flagged,
            "categories": [CATEGORY_NAMES[l] for l in flagged if l in CATEGORY_NAMES],
            "scores": scores,
            "needs_human_review": bool(near_boundary or threat_flagged),
        })
    return results


def print_result(result, actual_labels=None):
    print("-" * 60)
    print("Text:", result["text"][:150])
    print("Result:", result["label"])
    print("Flagged labels:", result["flagged_labels"] or "none")
    print("Categories:", result["categories"] or "none")
    print("Scores:", result["scores"])
    print("Human review suggested:", result["needs_human_review"])
    if actual_labels is not None:
        print("Actual labels:", actual_labels or "none")


def main():
    parser = argparse.ArgumentParser(description="Analyse text with the baseline model.")
    parser.add_argument("texts", nargs="*", help="Text to analyse")
    parser.add_argument(
        "--validation-sample", type=int, default=0,
        help="Predict N random comments from the validation split",
    )
    args = parser.parse_args()

    config = load_config()
    pipeline, labels = load_model(config)

    if args.validation_sample > 0:
        path = Path(config["paths"]["processed_data"]) / "validation_split.csv"
        sample = pd.read_csv(path).sample(
            n=args.validation_sample, random_state=config["random_seed"]
        )
        results = predict_texts(sample["comment_text"].tolist(), pipeline, labels, config)
        for result, (_, row) in zip(results, sample.iterrows()):
            actual = [label for label in labels if row[label] == 1]
            print_result(result, actual)
        return

    texts = args.texts or DEFAULT_EXAMPLES
    for result in predict_texts(texts, pipeline, labels, config):
        print_result(result)


if __name__ == "__main__":
    main()