"""Fine-tunes DistilBERT for multi-label toxicity classification.

Quick test of the whole pipeline (small sample, saves to models/transformer_test):
    python -m src.train_transformer --sample 500 --epochs 1

Full training (validates after every epoch, keeps the best model in models/transformer):
    python -m src.train_transformer
"""
import argparse
import json
import random
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch.optim.lr_scheduler import LambdaLR
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from src.data_preprocessing import load_config

THRESHOLD_GRID = [i / 100 for i in range(2, 99)]


class CommentDataset(Dataset):
    def __init__(self, texts, labels):
        self.texts = list(texts)
        self.labels = labels

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, i):
        return self.texts[i], self.labels[i]


def make_collate(tokenizer, max_length):
    def collate(batch):
        texts = [text for text, _ in batch]
        labels = torch.tensor(np.array([label for _, label in batch]), dtype=torch.float32)
        encoded = tokenizer(
            texts, truncation=True, max_length=max_length, padding=True, return_tensors="pt"
        )
        return encoded, labels

    return collate


def best_f1(scores, actual):
    """Returns the best F1 over a grid of thresholds, and the threshold that gave it."""
    best_value, best_threshold = 0.0, 0.5
    for t in THRESHOLD_GRID:
        pred = scores >= t
        tp = int((pred & actual).sum())
        fp = int((pred & ~actual).sum())
        fn = int((~pred & actual).sum())
        denominator = 2 * tp + fp + fn
        f1 = 2 * tp / denominator if denominator else 0.0
        if f1 > best_value:
            best_value, best_threshold = f1, t
    return best_value, best_threshold


def predict_scores(model, loader, device):
    model.eval()
    all_scores = []
    with torch.no_grad():
        for encoded, _ in loader:
            encoded = {k: v.to(device) for k, v in encoded.items()}
            logits = model(**encoded).logits
            all_scores.append(torch.sigmoid(logits.float()).cpu().numpy())
    model.train()
    return np.concatenate(all_scores)


def save_model(model, tokenizer, labels, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(out_dir)
    tokenizer.save_pretrained(out_dir)
    with open(out_dir / "labels.json", "w") as f:
        json.dump(labels, f)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", type=int, default=0,
                        help="test run: train on N random comments, validate on 1,000")
    parser.add_argument("--epochs", type=int, default=None)
    parser.add_argument("--batch-size", type=int, default=None)
    parser.add_argument("--fp16", action="store_true", help="use half precision")
    args = parser.parse_args()

    config = load_config()
    cfg = config["transformer"]
    labels = config["labels"]
    seed = config["random_seed"]
    epochs = args.epochs or cfg["epochs"]
    batch_size = args.batch_size or cfg["batch_size"]
    use_fp16 = args.fp16 or cfg["use_fp16"]

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

    if not torch.cuda.is_available():
        raise RuntimeError("No GPU found. Run: python -m src.check_gpu")
    device = torch.device("cuda")

    folder = Path(config["paths"]["processed_data"])
    train = pd.read_csv(folder / "train_split.csv")
    val = pd.read_csv(folder / "validation_split.csv")
    full_size = len(train)
    if args.sample:
        train = train.sample(n=args.sample, random_state=seed)
        val = val.head(1000)
    texts = train["comment_text"].tolist()
    y = train[labels].values.astype(np.float32)
    y_val = val[labels].values == 1

    print(f"Model: {cfg['model_name']}")
    print(f"Training comments: {len(y)}   Validation comments: {len(val)}   Epochs: {epochs}   "
          f"Batch size: {batch_size}   Max length: {cfg['max_length']}")
    print(f"Precision: {'half (fp16)' if use_fp16 else 'full (fp32)'}")

    positives = y.sum(axis=0)
    negatives = len(y) - positives
    pos_weight = (negatives / np.maximum(positives, 1)) ** cfg["pos_weight_power"]
    print("Weights for rare labels:", {l: round(float(w), 1) for l, w in zip(labels, pos_weight)})
    loss_fn = torch.nn.BCEWithLogitsLoss(
        pos_weight=torch.tensor(pos_weight, dtype=torch.float32, device=device)
    )

    tokenizer = AutoTokenizer.from_pretrained(cfg["model_name"])
    model = AutoModelForSequenceClassification.from_pretrained(
        cfg["model_name"], num_labels=len(labels), problem_type="multi_label_classification"
    ).to(device)

    collate = make_collate(tokenizer, cfg["max_length"])
    loader = DataLoader(
        CommentDataset(texts, y),
        batch_size=batch_size,
        shuffle=True,
        collate_fn=collate,
        generator=torch.Generator().manual_seed(seed),
    )
    val_loader = DataLoader(
        CommentDataset(val["comment_text"].tolist(), val[labels].values.astype(np.float32)),
        batch_size=32,
        shuffle=False,
        collate_fn=collate,
    )

    optimizer = torch.optim.AdamW(model.parameters(), lr=cfg["learning_rate"], weight_decay=0.01)
    total_steps = epochs * len(loader)
    warmup_steps = max(1, int(0.06 * total_steps))

    def lr_factor(step):
        if step < warmup_steps:
            return (step + 1) / warmup_steps
        return max(0.0, (total_steps - step) / max(1, total_steps - warmup_steps))

    scheduler = LambdaLR(optimizer, lr_factor)
    scaler = torch.amp.GradScaler("cuda", enabled=use_fp16)

    models_dir = Path(config["paths"]["models"])
    out_dir = models_dir / ("transformer_test" if args.sample else "transformer")
    reports_dir = Path(config["paths"].get("reports", "reports"))
    reports_dir.mkdir(parents=True, exist_ok=True)

    log_every = max(25, total_steps // 40)
    history = []
    best_macro = -1.0

    torch.cuda.reset_peak_memory_stats()
    torch.cuda.synchronize()
    start = time.time()
    model.train()
    step = 0
    running_loss = 0.0

    for epoch in range(1, epochs + 1):
        epoch_start = time.time()
        for encoded, batch_labels in loader:
            encoded = {k: v.to(device) for k, v in encoded.items()}
            batch_labels = batch_labels.to(device)

            optimizer.zero_grad(set_to_none=True)
            with torch.autocast(device_type="cuda", dtype=torch.float16, enabled=use_fp16):
                logits = model(**encoded).logits
            loss = loss_fn(logits.float(), batch_labels)

            if not torch.isfinite(loss):
                raise RuntimeError(
                    "The loss became NaN or infinite. If you used --fp16, try without it "
                    "and tell me what happened."
                )

            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            scaler.step(optimizer)
            scaler.update()
            scheduler.step()

            step += 1
            running_loss += loss.item()
            if step % log_every == 0:
                print(f"epoch {epoch}  step {step}/{total_steps}  "
                      f"average loss: {running_loss / log_every:.4f}  "
                      f"elapsed: {(time.time() - start) / 60:.1f} min")
                running_loss = 0.0

        torch.cuda.synchronize()
        train_seconds = time.time() - epoch_start

        # Check progress on the validation comments after every epoch
        scores = predict_scores(model, val_loader, device)
        f1s, thresholds = {}, {}
        for i, label in enumerate(labels):
            f1s[label], thresholds[label] = best_f1(scores[:, i], y_val[:, i])
        macro = float(np.mean(list(f1s.values())))

        print()
        print(f"=== Epoch {epoch} finished. Training took {train_seconds / 60:.1f} min ===")
        print("Validation, best F1 per label (threshold tuned on validation):")
        for label in labels:
            print(f"  {label:14s} F1 {f1s[label]:.3f}   at threshold {thresholds[label]:.2f}")
        print(f"  macro F1: {macro:.3f}")

        row = {"epoch": epoch, "train_minutes": round(train_seconds / 60, 1), "macro_f1": round(macro, 4)}
        row.update({f"{l}_f1": round(f1s[l], 4) for l in labels})
        row.update({f"{l}_threshold": thresholds[l] for l in labels})
        history.append(row)
        if not args.sample:
            pd.DataFrame(history).to_csv(reports_dir / "transformer_epoch_metrics.csv", index=False)

        if macro > best_macro:
            best_macro = macro
            save_model(model, tokenizer, labels, out_dir)
            print(f"Saved as the best model so far to {out_dir}")
        print()

    total_seconds = time.time() - start
    print(f"Total time: {total_seconds / 60:.1f} minutes")
    print(f"Peak GPU memory used by tensors: {torch.cuda.max_memory_allocated() / 1024**3:.2f} GB")
    print(f"Peak GPU memory reserved: {torch.cuda.max_memory_reserved() / 1024**3:.2f} GB")
    if args.sample:
        rate = len(y) * epochs / (total_seconds)
        print(f"(Test run only. Rough speed incl. validation: {rate:.1f} comments per second "
              f"for {full_size} full-size training comments.)")


if __name__ == "__main__":
    main()