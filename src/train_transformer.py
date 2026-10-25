"""Fine-tunes DistilBERT for multi-label toxicity classification.

Quick speed and memory test (trains on 2,000 comments, saves nothing):
    python -m src.train_transformer --sample 2000 --epochs 1
    python -m src.train_transformer --sample 2000 --epochs 1 --fp16

Full training (saves the model to models/transformer):
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", type=int, default=0,
                        help="train on N random comments only (test run, nothing is saved)")
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

    train_path = Path(config["paths"]["processed_data"]) / "train_split.csv"
    train = pd.read_csv(train_path)
    full_size = len(train)
    if args.sample:
        train = train.sample(n=args.sample, random_state=seed)
    texts = train["comment_text"].tolist()
    y = train[labels].values.astype(np.float32)

    print(f"Model: {cfg['model_name']}")
    print(f"Training comments: {len(y)}   Epochs: {epochs}   Batch size: {batch_size}   "
          f"Max length: {cfg['max_length']}")
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

    loader = DataLoader(
        CommentDataset(texts, y),
        batch_size=batch_size,
        shuffle=True,
        collate_fn=make_collate(tokenizer, cfg["max_length"]),
        generator=torch.Generator().manual_seed(seed),
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

    torch.cuda.reset_peak_memory_stats()
    torch.cuda.synchronize()
    start = time.time()
    model.train()
    step = 0
    running_loss = 0.0

    for epoch in range(1, epochs + 1):
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
            if step % 25 == 0:
                print(f"epoch {epoch}  step {step}/{total_steps}  "
                      f"average loss over last 25 steps: {running_loss / 25:.4f}  "
                      f"elapsed: {time.time() - start:.0f}s")
                running_loss = 0.0

    torch.cuda.synchronize()
    elapsed = time.time() - start
    rate = len(y) * epochs / elapsed
    print()
    print(f"Training time: {elapsed:.0f} seconds")
    print(f"Speed: {rate:.1f} comments per second")
    print(f"Estimated time for one full epoch over {full_size} comments: "
          f"{full_size / rate / 60:.0f} minutes")
    print(f"Peak GPU memory used by tensors: {torch.cuda.max_memory_allocated() / 1024**3:.2f} GB")
    print(f"Peak GPU memory reserved: {torch.cuda.max_memory_reserved() / 1024**3:.2f} GB")

    if args.sample:
        print("Test run: nothing was saved.")
        return

    out_dir = Path(config["paths"]["models"]) / "transformer"
    out_dir.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(out_dir)
    tokenizer.save_pretrained(out_dir)
    with open(out_dir / "labels.json", "w") as f:
        json.dump(labels, f)
    print("Saved model to", out_dir)


if __name__ == "__main__":
    main()