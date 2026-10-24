"""Trains the TF-IDF + Logistic Regression baseline.

Run from the project root:
    python -m src.train_baseline
"""
import json
import time
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import Pipeline

from src.data_preprocessing import load_config


def build_pipeline(config):
    tfidf_cfg = config["tfidf"]
    lr_cfg = config["logistic_regression"]
    return Pipeline([
        ("tfidf", TfidfVectorizer(
            max_features=tfidf_cfg["max_features"],
            ngram_range=tuple(tfidf_cfg["ngram_range"]),
            min_df=tfidf_cfg["min_df"],
        )),
        ("classifier", OneVsRestClassifier(LogisticRegression(
            C=lr_cfg["C"],
            max_iter=lr_cfg["max_iter"],
            class_weight=lr_cfg["class_weight"],
        ))),
    ])


def main():
    config = load_config()
    labels = config["labels"]

    train_path = Path(config["paths"]["processed_data"]) / "train_split.csv"
    if not train_path.exists():
        raise FileNotFoundError(
            f"{train_path} not found. Run: python -m src.data_preprocessing"
        )

    train = pd.read_csv(train_path)
    X_train = train["comment_text"]
    y_train = train[labels].values
    print(f"Loaded {len(train)} training comments")

    pipeline = build_pipeline(config)
    print("Training started. This can take a few minutes...")
    start = time.time()
    pipeline.fit(X_train, y_train)
    print(f"Training finished in {time.time() - start:.0f} seconds")

    vocab_size = len(pipeline.named_steps["tfidf"].vocabulary_)
    print("TF-IDF vocabulary size:", vocab_size)

    models_dir = Path(config["paths"]["models"])
    models_dir.mkdir(parents=True, exist_ok=True)
    model_path = models_dir / "baseline_pipeline.joblib"
    labels_path = models_dir / "baseline_labels.json"

    joblib.dump(pipeline, model_path)
    with open(labels_path, "w") as f:
        json.dump(labels, f)

    print("Saved model to", model_path)
    print("Saved label order to", labels_path)


if __name__ == "__main__":
    main()