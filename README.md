## Status

Phase 5: baseline model trained and evaluated on the validation split. The test split has not been used. A transformer comparison (Phase 6) is next.

## Baseline model

TF-IDF (50,000 word and word-pair features) with one Logistic Regression per label and balanced class weights, trained on the training split of the Jigsaw Toxic Comment Classification data (127,655 comments). Training takes under a minute on a laptop CPU.

## Setup (Windows, PowerShell)

    python -m venv .venv
    .venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    python -m src.data_preprocessing
    python -m src.train_baseline
    python -m src.evaluate

The Jigsaw files must be placed in data/raw first (train.csv, test.csv, test_labels.csv). The data is not stored in this repository.

## Validation results

Thresholds were tuned per label on the validation split (15,958 comments), so these figures are optimistic. Scores are model scores and are not calibrated probabilities.

| Label | Threshold | Precision | Recall | F1 |
|---|---|---|---|---|
| toxic | 0.69 | 0.784 | 0.770 | 0.777 |
| severe_toxic | 0.96 | 0.459 | 0.608 | 0.523 |
| obscene | 0.73 | 0.803 | 0.817 | 0.810 |
| threat | 0.50 | 0.262 | 0.696 | 0.380 |
| insult | 0.76 | 0.724 | 0.751 | 0.737 |
| identity_hate | 0.96 | 0.573 | 0.481 | 0.523 |
| any label (toxic vs non_toxic) | one per label | 0.810 | 0.758 | 0.784 |

On validation the model flagged 288 of 14,335 clean comments and missed 392 of 1,623 labelled comments.

## Human review rule

A comment is marked for review when its highest score is within 0.15 of that label's threshold, or when it carries a threat flag. On validation this covered about 6% of comments and about half of the model's mistakes. It cannot find confident mistakes.

## Known limitations

- Trained on English Wikipedia talk page comments. Social media text may differ and has not been tested.
- The model reads words, not meaning. In a probe of 24 hand-written sentences, 15 matched expectations. Five of six ambiguous or quoted sentences were wrongly flagged (for example "I hate Mondays."), mostly with confident scores and no review flag.
- Identity terms: in a probe of neutral template sentences, all four sentences containing "gay" were flagged, and sentences with "black", "deaf", "lesbian", "blind", and "Muslim" were flagged in 1 or 2 of 4 cases. None of 16 sentences with control words were flagged. The probe is small, but the model needs a proper bias evaluation before any use on real content.
- English only. One abusive romanised Hindi sentence was not flagged and received no review flag.
- Category tags are less reliable than the overall decision. The obscene and insult tags often appeared together on sentences that contain insults but no profanity.
- Severity (low, moderate, high, critical) is not implemented. severe_toxic is a separate Jigsaw label and is not a severity scale.
- A single comment cannot show repeated cyberbullying, and the model makes no claim about that.
- Output is decision support for human review. It must not be used for automatic action against a person.