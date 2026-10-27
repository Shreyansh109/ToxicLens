
"""ToxicLens: local toxicity analysis app."""
import streamlit as st

from src.data_preprocessing import load_config
from src.predict import predict_texts
from src.transformer_scoring import load_transformer


st.set_page_config(
    page_title="ToxicLens",
    page_icon="🔎",
    layout="centered",
)

CATEGORY_NAMES = {
    "insult": "Insult",
    "threat": "Threat",
    "identity_hate": "Identity-based hate",
    "obscene": "Obscene language",
}

st.title("ToxicLens")
st.caption("AI-assisted toxicity detection with human review.")

st.warning(
    "This tool can make mistakes. Scores are raw model scores, not "
    "calibrated probabilities. Use predictions as decision support, "
    "not as definitive judgments about a person."
)


@st.cache_resource
def get_model():
    config = load_config()
    scorer, labels = load_transformer(config)
    return config, scorer, labels


try:
    config, scorer, labels = get_model()
except Exception as exc:
    st.error(f"Could not load the transformer model: {exc}")
    st.info(
        "Check that the trained model exists in models/transformer "
        "and that your project's virtual environment is active."
    )
    st.stop()


st.subheader("Analyse a comment")

text = st.text_area(
    "Enter text to analyse",
    height=150,
    max_chars=10000,
    placeholder="Paste a comment here...",
)

if st.button("Analyse text", type="primary"):
    if not text.strip():
        st.warning("Enter some text before analysing.")
    else:
        try:
            settings = config["prediction_transformer"]
            results = predict_texts(
                [text],
                scorer,
                labels,
                {
                    **config,
                    "prediction": settings,
                },
            )
            result = results[0]

            st.divider()
            st.subheader("Result")

            if result["label"] == "toxic":
                st.error("Toxicity detected by the model")
            else:
                st.success("No configured toxicity label was flagged")

            if result["flagged_labels"]:
                st.write("**Flagged labels**")
                for label in result["flagged_labels"]:
                    st.write(
                        f"- {label.replace('_', ' ').title()}"
                    )
            else:
                st.write("No labels crossed their configured thresholds.")

            if result["categories"]:
                st.write("**Categories**")
                for category in result["categories"]:
                    st.write(
                        f"- {CATEGORY_NAMES.get(category, category)}"
                    )

            if result["needs_human_review"]:
                st.warning(
                    "Human review recommended. The result is near a "
                    "decision boundary or a threat label was flagged."
                )
            else:
                st.info("The configured review rule did not request review.")

            st.subheader("Raw model scores")
            st.caption(
                "These are raw model scores, not calibrated probabilities "
                "or measures of a person's intent."
            )

            for label in labels:
                score = result["scores"][label]
                threshold = settings.get(
                    "label_thresholds",
                    {},
                ).get(label, settings["threshold"])

                st.write(
                    f"**{label.replace('_', ' ').title()}**: "
                    f"{score:.4f}  | Threshold: {threshold:.2f}"
                )
                st.progress(min(max(score, 0.0), 1.0))

        except Exception as exc:
            st.error(f"Analysis failed: {exc}")


st.divider()
st.caption(
    "ToxicLens is a research project. Do not use its predictions "
    "as the sole basis for moderation or consequential decisions."
)
