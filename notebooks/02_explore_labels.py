import json
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # draws into a file, so no window is needed
import matplotlib.pyplot as plt

with open("config.json") as f:
    config = json.load(f)

labels = config["labels"]
df = pd.read_csv(config["paths"]["raw_data"] + "/train.csv")

# 1. Missing values
print("Missing values per column:")
print(df.isna().sum())
print()
print("Empty or whitespace-only comments:", (df["comment_text"].str.strip() == "").sum())
print()

# 2. Duplicates
print("Duplicate ids:", df["id"].duplicated().sum())
print("Duplicate comment texts:", df["comment_text"].duplicated().sum())
print()

# 3. Label counts and percentages
counts = df[labels].sum()
percent = (counts / len(df) * 100).round(2)
summary = pd.DataFrame({"count": counts, "percent_of_comments": percent})
print("Label counts:")
print(summary)
print()

# 4. How many labels each comment has
labels_per_comment = df[labels].sum(axis=1)
print("Comments grouped by number of labels:")
print(labels_per_comment.value_counts().sort_index())
print()
print("Comments with at least one label:", (labels_per_comment > 0).sum())

# 5. Bar chart of label counts
fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(list(summary.index), summary["count"])
ax.bar_label(bars)
ax.set_title("Number of comments per label (train.csv)")
ax.set_ylabel("Comments")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
output_path = config["paths"]["processed_data"] + "/label_counts.png"
fig.savefig(output_path, dpi=120)
print()
print("Saved plot to", output_path)