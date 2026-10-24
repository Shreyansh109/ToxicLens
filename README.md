# Multi-Platform Cyberbullying and Toxic Content Severity Classifier

A local project that detects toxic content in text and, later, estimates severity. Predictions are decision support for human reviewers, not definitive judgments.

## Status

Phase 2: project structure created. No model trained yet.

## Setup (Windows, PowerShell)

```
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Project layout

- data/raw: original datasets (not committed to Git)
- data/processed: cleaned data and splits
- models: trained models
- notebooks: exploration
- src: preprocessing, training, evaluation, prediction code
- tests: automated tests

## Known limitations

To be filled in as we measure the model.