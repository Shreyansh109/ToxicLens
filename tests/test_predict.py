
import pytest

from src.predict import predict_texts


LABELS = [
    "toxic",
    "severe_toxic",
    "obscene",
    "threat",
    "insult",
    "identity_hate",
]


class MockModel:
    """Returns predefined scores without loading a real model."""

    def __init__(self, scores):
        self.scores = scores

    def predict_proba(self, texts):
        assert len(texts) == len(self.scores)
        return self.scores


@pytest.fixture
def config():
    return {
        "prediction": {
            "threshold": 0.5,
            "label_thresholds": {
                "toxic": 0.7,
                "severe_toxic": 0.8,
                "obscene": 0.7,
                "threat": 0.5,
                "insult": 0.7,
                "identity_hate": 0.8,
            },
            "review_margin": 0.15,
            "review_all_threats": True,
        }
    }


def test_non_toxic_text(config):
    model = MockModel([[0.1, 0.1, 0.1, 0.1, 0.1, 0.1]])

    result = predict_texts(
        ["Thank you for your help."], model, LABELS, config
    )[0]

    assert result["label"] == "non_toxic"
    assert result["flagged_labels"] == []


def test_toxic_label_uses_configured_threshold(config):
    model = MockModel([[0.75, 0.1, 0.1, 0.1, 0.1, 0.1]])

    result = predict_texts(
        ["An insulting comment"], model, LABELS, config
    )[0]

    assert result["label"] == "toxic"
    assert "toxic" in result["flagged_labels"]


def test_threat_flag_requests_human_review(config):
    model = MockModel([[0.1, 0.1, 0.1, 0.6, 0.1, 0.1]])

    result = predict_texts(
        ["A threatening comment"], model, LABELS, config
    )[0]

    assert "threat" in result["flagged_labels"]
    assert result["needs_human_review"] is True


def test_near_threshold_requests_review(config):
    # Toxic threshold is 0.70; score 0.60 is within the 0.15 margin.
    model = MockModel([[0.60, 0.1, 0.1, 0.1, 0.1, 0.1]])

    result = predict_texts(
        ["A borderline comment"], model, LABELS, config
    )[0]

    assert result["needs_human_review"] is True


@pytest.mark.parametrize(
    "texts",
    [
        [],
        [""],
        ["   "],
        [None],
        [123],
    ],
)
def test_invalid_input_is_rejected(texts, config):
    model = MockModel([])

    with pytest.raises(ValueError):
        predict_texts(texts, model, LABELS, config)
