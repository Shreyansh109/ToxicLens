import json
import pandas as pd

# Read the settings from config.json (it must be run from the project root)
with open("config.json") as f:
    config = json.load(f)

labels = config["labels"]
train_path = config["paths"]["raw_data"] + "/train.csv"

# Load the CSV file into a table called a DataFrame
df = pd.read_csv(train_path)

print("Shape (rows, columns):", df.shape)
print()
print("Column names:", list(df.columns))
print()
print("Data types:")
print(df.dtypes)
print()
print("First 3 rows, labels only:")
print(df[labels].head(3))
print()

# Show one comment that has no toxic labels, cut to 200 characters
clean_rows = df[df[labels].sum(axis=1) == 0]
print("One example comment with no toxic labels:")
print(clean_rows.iloc[0]["comment_text"][:200])