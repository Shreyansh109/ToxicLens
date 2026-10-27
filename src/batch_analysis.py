"""Batch analysis helpers for CSV files. They do not depend on Streamlit, so they can be tested.

Used by app.py.
"""
import pandas as pd

from src.predict import predict_texts

MAX_ROWS = 20000
CHUNK_SIZE = 128
RESULT_PREFIX = "toxiclens_"
SPREADSHEET_TRIGGERS = ("=", "+", "-", "@", "\t", "\r")


def read_uploaded_csv(uploaded_file):
    try:
        return pd.read_csv(uploaded_file)
    except UnicodeDecodeError:
        uploaded_file.seek(0)
        return pd.read_csv(uploaded_file, encoding="latin-1")


def guess_text_column(df):
    preferred = ["comment_text", "text", "comment", "content", "body", "message"]
    lowered = {str(column).lower(): column for column in df.columns}
    for name in preferred:
        if name in lowered:
            return lowered[name]
    best, best_length = df.columns[0], -1.0
    for column in df.columns:
        if pd.api.types.is_string_dtype(df[column]) or pd.api.types.is_object_dtype(df[column]):
            length = df[column].astype(str).str.len().mean()
            if length > best_length:
                best, best_length = column, length
    return best


def truncated_flags(texts, scorer):
    """True for each text that is longer than the model's token limit."""
    tokenizer = getattr(scorer, "tokenizer", None)
    limit = getattr(scorer, "max_length", None)
    if tokenizer is None or limit is None or not texts:
        return [False] * len(texts)
    encoded = tokenizer(list(texts), truncation=True, max_length=limit + 1)["input_ids"]
    return [len(ids) > limit for ids in encoded]


def analyse_dataframe(df, text_column, scorer, labels, config, progress_callback=None):
    """Scores every non-empty text. Returns a DataFrame in the same row order as df."""
    df = df.reset_index(drop=True)
    texts = df[text_column]
    valid = [i for i, value in enumerate(texts) if isinstance(value, str) and value.strip()]
    valid_texts = [texts[i] for i in valid]
    truncated = dict(zip(valid, truncated_flags(valid_texts, scorer)))

    results = {}
    for start in range(0, len(valid_texts), CHUNK_SIZE):
        chunk = valid_texts[start:start + CHUNK_SIZE]
        positions = valid[start:start + CHUNK_SIZE]
        for position, result in zip(positions, predict_texts(chunk, scorer, labels, config)):
            results[position] = result
        if progress_callback:
            progress_callback(min(start + CHUNK_SIZE, len(valid_texts)), len(valid_texts))

    records = []
    for i in range(len(df)):
        result = results.get(i)
        if result is None:
            record = {
                f"{RESULT_PREFIX}result": "skipped",
                f"{RESULT_PREFIX}flagged_labels": "",
                f"{RESULT_PREFIX}categories": "",
                f"{RESULT_PREFIX}needs_review": False,
                f"{RESULT_PREFIX}truncated": False,
            }
            record.update({f"{RESULT_PREFIX}score_{label}": None for label in labels})
        else:
            record = {
                f"{RESULT_PREFIX}result": result["label"],
                f"{RESULT_PREFIX}flagged_labels": ", ".join(result["flagged_labels"]),
                f"{RESULT_PREFIX}categories": ", ".join(result["categories"]),
                f"{RESULT_PREFIX}needs_review": result["needs_human_review"],
                f"{RESULT_PREFIX}truncated": truncated[i],
            }
            record.update({f"{RESULT_PREFIX}score_{label}": result["scores"][label] for label in labels})
        records.append(record)
    return pd.DataFrame(records)


def _protect(value):
    if isinstance(value, str) and value.startswith(SPREADSHEET_TRIGGERS):
        return "'" + value
    return value


def to_safe_csv_bytes(df):
    """CSV bytes for download. Text that starts with = + - or @ gets a leading apostrophe,
    so a spreadsheet program does not run it as a formula."""
    safe = df.copy()
    for column in safe.columns:
        if pd.api.types.is_string_dtype(safe[column]) or pd.api.types.is_object_dtype(safe[column]):
            safe[column] = safe[column].map(_protect)
    return safe.to_csv(index=False).encode("utf-8-sig")