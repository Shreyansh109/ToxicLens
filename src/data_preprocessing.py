"""Loads the Jigsaw training data and creates reproducible train/validation/test splits.

Run from the project root:
    python -m src.data_preprocessing
"""
import json
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


def load_config(path="config.json"):
    with open(path) as f:
        return json.load(f)


def load_raw_train(config):
    csv_path = Path(config["paths"]["raw_data"]) / "train.csv"
    return pd.read_csv(csv_path)


def make_splits(df, config):
    labels = config["labels"]
    seed = config["random_seed"]
    sizes = config["data_split"]

    total = sizes["train_size"] + sizes["validation_size"] + sizes["test_size"]
    if abs(total - 1.0) > 1e-9:
        raise ValueError("Split sizes in config.json must add up to 1.0")

    # Used only to keep the share of labelled comments similar in every split
    has_label = (df[labels].sum(axis=1) > 0).astype(int)

    # Step 1: set the test set aside
    train_val, test = train_test_split(
        df, test_size=sizes["test_size"], random_state=seed, stratify=has_label
    )

    # Step 2: split the remainder into train and validation
    val_share = sizes["validation_size"] / (sizes["train_size"] + sizes["validation_size"])
    train, val = train_test_split(
        train_val,
        test_size=val_share,
        random_state=seed,
        stratify=has_label.loc[train_val.index],
    )

    return (
        train.reset_index(drop=True),
        val.reset_index(drop=True),
        test.reset_index(drop=True),
    )


def check_no_overlap(splits):
    names = list(splits)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            shared = set(splits[names[i]]["id"]) & set(splits[names[j]]["id"])
            if shared:
                raise ValueError(f"{names[i]} and {names[j]} share {len(shared)} comments")


def print_summary(splits, labels):
    print("Rows per split:")
    for name, part in splits.items():
        print(f"  {name}: {len(part)}")
    print()

    counts = pd.DataFrame({name: part[labels].sum() for name, part in splits.items()})
    percent = pd.DataFrame(
        {name: (part[labels].mean() * 100).round(2) for name, part in splits.items()}
    )
    print("Comments with each label:")
    print(counts)
    print()
    print("Percent of comments with each label:")
    print(percent)


def save_splits(splits, config):
    out_dir = Path(config["paths"]["processed_data"])
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, part in splits.items():
        part.to_csv(out_dir / f"{name}_split.csv", index=False)


def main():
    config = load_config()
    df = load_raw_train(config)
    train, val, test = make_splits(df, config)
    splits = {"train": train, "validation": val, "test": test}

    check_no_overlap(splits)
    print_summary(splits, config["labels"])
    save_splits(splits, config)
    print()
    print("Saved splits to", config["paths"]["processed_data"])


if __name__ == "__main__":
    main()