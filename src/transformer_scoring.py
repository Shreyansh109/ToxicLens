"""Loads the fine-tuned transformer and turns text into six label scores.

The scorer has the same predict_proba(texts) method as the baseline pipeline,
so the functions in src/predict.py can work with either model.
"""
import json
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer


class TransformerScorer:
    def __init__(self, model_dir, max_length=128, batch_size=64):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.max_length = max_length
        self.batch_size = batch_size
        self.tokenizer = AutoTokenizer.from_pretrained(str(model_dir))
        self.model = AutoModelForSequenceClassification.from_pretrained(str(model_dir))
        self.model.to(self.device)
        self.model.eval()

    def predict_proba(self, texts):
        texts = list(texts)
        batches = []
        with torch.no_grad():
            for start in range(0, len(texts), self.batch_size):
                chunk = texts[start:start + self.batch_size]
                encoded = self.tokenizer(
                    chunk, truncation=True, max_length=self.max_length,
                    padding=True, return_tensors="pt",
                )
                encoded = {k: v.to(self.device) for k, v in encoded.items()}
                logits = self.model(**encoded).logits
                batches.append(torch.sigmoid(logits.float()).cpu().numpy())
        return np.concatenate(batches)


def load_transformer(config):
    model_dir = Path(config["paths"]["models"]) / "transformer"
    labels_path = model_dir / "labels.json"
    if not model_dir.exists() or not labels_path.exists():
        raise FileNotFoundError("Fine-tuned model not found. Run: python -m src.train_transformer")
    with open(labels_path) as f:
        labels = json.load(f)
    scorer = TransformerScorer(model_dir, max_length=config["transformer"]["max_length"])
    return scorer, labels