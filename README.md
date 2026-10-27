
# ToxicLens

ToxicLens is a machine-learning prototype that detects potentially toxic comments using six independent labels from the Jigsaw Toxic Comment Classification dataset. It includes a TF-IDF baseline, a fine-tuned DistilBERT transformer, and a local Streamlit interface.

**Important:** ToxicLens is a decision-support prototype. Its predictions can be wrong and should not be used as the sole basis for moderation or consequential decisions.

## Status

- Data preprocessing and train/validation/test splitting completed.
- Baseline model trained and evaluated.
- DistilBERT transformer trained and evaluated.
- Held-out test evaluation completed.
- Local Streamlit app implemented for single-comment analysis.
- Automated tests, CSV batch analysis, and more extensive bias evaluation remain future work.

## Models

### Baseline

TF-IDF with up to 50,000 word and word-pair features, using one Logistic Regression classifier per label with balanced class weights.

### Transformer

Fine-tuned `distilbert-base-uncased` with six independent output labels. Training used two epochs and a maximum sequence length of 128 tokens.

The transformer is the stronger model on the current held-out test evaluation.

## Labels

The six Jigsaw labels are:

- `toxic`
- `severe_toxic`
- `obscene`
- `threat`
- `insult`
- `identity_hate`

The app also maps selected labels to display categories. These categories are model outputs, not definitive judgments about a person or comment.

The `severe_toxic` label is not a severity scale. Low, moderate, high, and critical severity classification has not been implemented.

## Setup (Windows, PowerShell)

Use Python and create a virtual environment from the project root.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

The project uses PyTorch and Hugging Face Transformers for the transformer model. Install a PyTorch build appropriate for your hardware and CUDA setup, following the official PyTorch installation selector:
https://pytorch.org/get-started/locally/

If the project dependencies are not yet fully listed in `requirements.txt`, install the missing packages in the activated environment before continuing.

Place the required Jigsaw training data in `data/raw/`. The preprocessing script expects the dataset files described by the project code.

Prepare the splits and train the baseline:

```powershell
python -m src.data_preprocessing
python -m src.train_baseline
```

Train the transformer when needed:

```powershell
python -m src.train_transformer
```

Training the transformer is resource-intensive and can take considerably longer than training the baseline. Trained models are saved locally and are not stored in this repository.

## Run the app

Activate the project's virtual environment and run:

```powershell
python -m streamlit run app.py
```

Open the local URL printed in the terminal, usually `http://localhost:8501`.

The current interface supports single-comment analysis. It displays the overall decision, flagged labels, raw model scores, configured thresholds, and the human-review recommendation.

## Evaluation methodology

The dataset was split into training, validation, and test partitions. The held-out test split contains 15,958 comments.

Thresholds were selected using validation data and then held fixed for the final test evaluation. The test results below are for those configured thresholds; the test split was not used to tune them.

Model scores are raw scores and are not calibrated probabilities.

## Held-out test results

### Overall decision: toxic vs non-toxic

| Metric | Baseline | Transformer |
|---|---:|---:|
| Precision | 0.8044 | 0.8736 |
| Recall | 0.7425 | 0.7917 |
| F1 | 0.7722 | 0.8306 |
| False positives | 293 | 186 |
| False negatives | 418 | 338 |

Transformer accuracy for the overall decision was 0.9672 (96.72%). Accuracy alone can be misleading because most comments in this dataset are non-toxic.

### Transformer per-label results

| Label | Threshold | Precision | Recall | F1 |
|---|---:|---:|---:|---:|
| toxic | 0.81 | 0.8353 | 0.8046 | 0.8196 |
| severe_toxic | 0.81 | 0.4335 | 0.6154 | 0.5087 |
| obscene | 0.83 | 0.8265 | 0.8305 | 0.8285 |
| threat | 0.10 | 0.3125 | 0.7143 | 0.4348 |
| insult | 0.72 | 0.7202 | 0.8008 | 0.7584 |
| identity_hate | 0.86 | 0.5969 | 0.5833 | 0.5900 |

The transformer's macro F1 across the six individual labels was 0.6567. Threat and severe-toxicity classification remain challenging.

### Baseline per-label results

| Label | Threshold | Precision | Recall | F1 |
|---|---:|---:|---:|---:|
| toxic | 0.69 | 0.7785 | 0.7561 | 0.7671 |
| severe_toxic | 0.96 | 0.4463 | 0.5524 | 0.4938 |
| obscene | 0.73 | 0.7947 | 0.7966 | 0.7956 |
| threat | 0.50 | 0.2692 | 0.6667 | 0.3836 |
| insult | 0.76 | 0.6902 | 0.7416 | 0.7150 |
| identity_hate | 0.96 | 0.4588 | 0.2955 | 0.3594 |

## Human review rule

The current prediction rule recommends review when a score is near a configured decision boundary or when the threat label is flagged. The review margin is configurable.

This rule cannot detect every confidently wrong prediction. A review recommendation is not proof that a comment is harmful, and the absence of a recommendation does not guarantee correctness.

## Known limitations

- Training data consists of English Wikipedia talk-page comments. Performance on social media and other domains may differ.
- The model can misclassify ambiguous wording, quotations, slang, and context-dependent language.
- Romanised Hindi and other non-English content have not been adequately evaluated.
- Small exploratory identity-term probes showed possible bias signals, including false flags on some neutral identity-related sentences. A proper bias evaluation remains necessary.
- Threat and severe-toxicity labels have relatively low precision.
- Category tags are imperfect and can overlap.
- The model does not determine intent, establish that a person is abusive, detect repeated cyberbullying across conversations, or predict severity.
- Scores are not calibrated probabilities.
- The current Streamlit app is a local prototype, not a production moderation service.

## Hardware and performance

The transformer was trained and evaluated locally using a CUDA-capable GPU. Training takes substantially longer than baseline training, and CPU inference may be slower.

Exact training time and memory use depend on hardware, batch size, and software versions.

## Repository contents

- `src/data_preprocessing.py`: prepares dataset splits.
- `src/train_baseline.py`: trains the TF-IDF baseline.
- `src/train_transformer.py`: fine-tunes the transformer.
- `src/predict.py`: shared prediction functions and baseline CLI.
- `src/transformer_scoring.py`: loads and scores the transformer.
- `src/evaluate.py`: baseline validation evaluation.
- `src/evaluate_transformer.py`: transformer validation evaluation and threshold analysis.
- `src/evaluate_test.py`: held-out test evaluation.
- `app.py`: local Streamlit interface.
- `config.json`: project configuration and prediction thresholds.

Datasets and trained model weights are kept locally and should not be committed to Git.