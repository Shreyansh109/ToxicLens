"""ToxicLens: local toxicity analysis app with dHhi branding."""
from pathlib import Path

import streamlit as st

from src.data_preprocessing import load_config
from src.predict import predict_texts
from src.transformer_scoring import load_transformer


st.set_page_config(
    page_title="dHhi | ToxicLens",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# dHhi / ToxicLens sticker-book palette
INK = "#111111"
PAPER = "#FFFFFF"
SKY = "#DCEEFF"
BLUE = "#4DA2FF"
MINT = "#55DB9C"
LAVENDER = "#E9CCFF"
ORANGE = "#FB4903"
YELLOW = "#FFD731"
VIOLET = "#5C4ADE"

CATEGORY_NAMES = {
    "insult": "Insult",
    "threat": "Threat",
    "identity_hate": "Identity-based hate",
    "obscene": "Obscene language",
}

# CSS affects presentation only; prediction code and thresholds are unchanged.
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    :root {{
        --ink: {INK};
        --paper: {PAPER};
        --sky: {SKY};
        --blue: {BLUE};
        --mint: {MINT};
        --lavender: {LAVENDER};
        --orange: {ORANGE};
        --yellow: {YELLOW};
        --violet: {VIOLET};
    }}

    html, body, [class*="css"] {{
        font-family: 'Inter', ui-sans-serif, system-ui, sans-serif;
        color: var(--ink);
    }}
    .stApp {{
        background: var(--sky);
    }}
    [data-testid="stHeader"] {{
        background: transparent;
    }}
    .block-container {{
        max-width: 1440px;
        padding-top: 1.3rem;
        padding-bottom: 3rem;
    }}
    .brandbar {{
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 12px 18px;
        background: var(--paper);
        border: 2px solid var(--ink);
        border-radius: 999px;
        margin-bottom: 26px;
    }}
    .brandword {{
        font-size: 1.25rem;
        font-weight: 900;
        letter-spacing: -0.06em;
        line-height: 1;
    }}
    .brandproduct {{
        font-size: .78rem;
        font-weight: 700;
        color: #555;
        margin-top: 4px;
    }}
    .brandchip {{
        margin-left: auto;
        background: var(--yellow);
        border: 2px solid var(--ink);
        border-radius: 999px;
        padding: 8px 14px;
        font-size: .75rem;
        font-weight: 800;
        letter-spacing: .02em;
    }}
    .hero {{
        background: var(--blue);
        border: 2px solid var(--ink);
        border-radius: 30px;
        padding: clamp(22px, 4vw, 54px);
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
    }}
    .eyebrow {{
        display: inline-block;
        background: var(--paper);
        border: 2px solid var(--ink);
        border-radius: 999px;
        padding: 7px 12px;
        font-size: .75rem;
        font-weight: 800;
        letter-spacing: .04em;
        text-transform: uppercase;
    }}
    .hero h1 {{
        font-size: clamp(3.2rem, 9vw, 7.5rem);
        line-height: .84;
        letter-spacing: -.085em;
        font-weight: 900;
        margin: 22px 0 14px;
        color: var(--ink);
    }}
    .hero p {{
        font-size: clamp(1rem, 2vw, 1.25rem);
        line-height: 1.45;
        font-weight: 600;
        max-width: 670px;
        margin-bottom: 0;
    }}
    .sticker {{
        display: inline-block;
        border: 2px solid var(--ink);
        border-radius: 18px;
        padding: 10px 14px;
        font-weight: 900;
        transform: rotate(5deg);
        background: var(--yellow);
        margin-top: 20px;
    }}
    .section-label {{
        font-size: .8rem;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: .08em;
        margin: 0 0 10px;
    }}
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: var(--paper);
        border: 2px solid var(--ink);
        border-radius: 24px;
        padding: 20px;
    }}
    .stTextArea textarea {{
        background: #FBFDFF;
        border: 2px solid var(--ink);
        border-radius: 18px;
        color: var(--ink);
        font-size: 1rem;
    }}
    .stTextArea label, .stCheckbox label {{
        font-weight: 700;
    }}
    .stButton > button {{
        background: var(--ink);
        color: var(--paper);
        border: 2px solid var(--ink);
        border-radius: 999px;
        padding: .72rem 1.3rem;
        font-weight: 800;
        min-height: 3rem;
        transition: transform .15s ease, background .15s ease;
    }}
    .stButton > button:hover {{
        background: var(--violet);
        color: var(--paper);
        border-color: var(--ink);
        transform: translateY(-2px);
    }}
    .result-toxic {{
        background: #FFE0D5;
        border: 2px solid var(--ink);
        border-radius: 20px;
        padding: 18px;
        font-size: 1.2rem;
        font-weight: 900;
    }}
    .result-clean {{
        background: var(--mint);
        border: 2px solid var(--ink);
        border-radius: 20px;
        padding: 18px;
        font-size: 1.2rem;
        font-weight: 900;
    }}
    .mini-note {{
        font-size: .84rem;
        line-height: 1.5;
        color: #333;
    }}
    .pill {{
        display: inline-block;
        border: 2px solid var(--ink);
        border-radius: 999px;
        padding: 7px 11px;
        margin: 4px 5px 4px 0;
        background: var(--lavender);
        font-size: .8rem;
        font-weight: 800;
    }}
    .footer {{
        text-align: center;
        padding: 20px 12px 0;
        color: #333;
        font-size: .78rem;
        font-weight: 600;
    }}
    [data-testid="stProgress"] > div > div {{
        background-color: var(--violet);
    }}
    [data-testid="stAlert"] {{
        border: 2px solid var(--ink);
        border-radius: 18px;
    }}
    @media (max-width: 700px) {{
        .brandbar {{ border-radius: 24px; }}
        .brandchip {{ display: none; }}
        .hero {{ border-radius: 24px; }}
        .block-container {{ padding-left: 1rem; padding-right: 1rem; }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# Load model using the same cached loader as the original app.
@st.cache_resource
def get_model():
    config = load_config()
    scorer, labels = load_transformer(config)
    return config, scorer, labels


# Header: use the user's supplied logo if it is saved at assets/dhhi_logo.png.
logo_path = Path("assets") / "dhhi_logo.png"
header_cols = st.columns([1, 8, 2], vertical_alignment="center")
with header_cols[0]:
    if logo_path.exists():
        st.image(str(logo_path), width=74)
    else:
        st.markdown(
            "<div style='font-size:2.4rem;line-height:1'>🌈</div>",
            unsafe_allow_html=True,
        )
with header_cols[1]:
    st.markdown(
        """
        <div>
          <div class="brandword">dHhi</div>
          <div class="brandproduct">ToxicLens · AI-assisted comment analysis</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with header_cols[2]:
    st.markdown('<div class="brandchip">HUMAN REVIEW FIRST</div>', unsafe_allow_html=True)

st.markdown(
    """
    <section class="hero">
      <span class="eyebrow">A research prototype · Built for review</span>
      <h1>Words have<br>impact.</h1>
      <p>Explore potentially toxic language with model-assisted signals, clear thresholds, and human judgment in the loop.</p>
      <span class="sticker">PAUSE · CHECK · REVIEW</span>
    </section>
    """,
    unsafe_allow_html=True,
)

st.warning(
    "ToxicLens can make mistakes. Scores are raw model scores, not calibrated "
    "probabilities. Use predictions as decision support—not as definitive judgments "
    "about a person or comment."
)

try:
    config, scorer, labels = get_model()
except Exception as exc:
    st.error(f"Could not load the transformer model: {exc}")
    st.info(
        "Check that the trained model exists in models/transformer "
        "and that your project's virtual environment is active."
    )
    st.stop()

left, right = st.columns([1.05, 0.95], gap="large")

with left:
    with st.container(border=True):
        st.markdown('<div class="section-label">01 / Analyse</div>', unsafe_allow_html=True)
        st.subheader("Paste a comment")
        text = st.text_area(
            "Text to analyse",
            height=220,
            max_chars=10000,
            placeholder="Paste a comment here. The model will return label scores for review.",
            label_visibility="visible",
        )
        st.caption("English Wikipedia comments were used for training. Other languages and contexts may behave differently.")
        analyse = st.button("Analyse comment  →", type="primary", use_container_width=True)

with right:
    with st.container(border=True):
        st.markdown('<div class="section-label">02 / Before you begin</div>', unsafe_allow_html=True)
        st.subheader("A signal, not a verdict")
        st.markdown(
            """
            **What ToxicLens can do**
            - Flag text that crosses configured label thresholds.
            - Show which labels contributed to the decision.
            - Recommend human review under the configured rule.

            **What it cannot do**
            - Reliably determine intent or context.
            - Prove that a person is abusive.
            - Guarantee a comment is safe when no label is flagged.
            """
        )
        st.markdown(
            '<span class="pill">6 labels</span><span class="pill">Local model</span><span class="pill">Human in the loop</span>',
            unsafe_allow_html=True,
        )

if analyse:
    if not text.strip():
        st.warning("Enter some text before analysing.")
    else:
        try:
            settings = config["prediction_transformer"]
            results = predict_texts(
                [text],
                scorer,
                labels,
                {**config, "prediction": settings},
            )
            result = results[0]
            st.markdown("---")
            st.markdown('<div class="section-label">03 / Analysis result</div>', unsafe_allow_html=True)
            st.header("Your results")

            result_col, review_col = st.columns([1.1, 0.9], gap="large")
            with result_col:
                if result["label"] == "toxic":
                    st.markdown(
                        '<div class="result-toxic">⚠ Potential toxicity flagged</div>',
                        unsafe_allow_html=True,
                    )
                    st.caption("One or more configured toxicity labels crossed their thresholds.")
                else:
                    st.markdown(
                        '<div class="result-clean">✓ No configured label was flagged</div>',
                        unsafe_allow_html=True,
                    )
                    st.caption("This does not guarantee that the comment is harmless.")
            with review_col:
                with st.container(border=True):
                    st.markdown('<div class="section-label">Human review</div>', unsafe_allow_html=True)
                    if result["needs_human_review"]:
                        st.warning("Review recommended")
                        st.write("The configured rule detected a near-threshold score or a flagged threat label.")
                    else:
                        st.info("No review requested by the configured rule.")
                        st.write("A confidently wrong prediction may still occur.")

            detail_col, score_col = st.columns([0.9, 1.1], gap="large")
            with detail_col:
                with st.container(border=True):
                    st.markdown('<div class="section-label">Flagged labels</div>', unsafe_allow_html=True)
                    if result["flagged_labels"]:
                        for label in result["flagged_labels"]:
                            st.markdown(
                                f'<span class="pill">{label.replace("_", " ").title()}</span>',
                                unsafe_allow_html=True,
                            )
                    else:
                        st.write("No labels crossed their configured thresholds.")

                    st.markdown('<div class="section-label" style="margin-top:18px">Categories</div>', unsafe_allow_html=True)
                    if result["categories"]:
                        for category in result["categories"]:
                            st.markdown(
                                f'<span class="pill">{CATEGORY_NAMES.get(category, category)}</span>',
                                unsafe_allow_html=True,
                            )
                    else:
                        st.write("No display categories were assigned.")

            with score_col:
                with st.container(border=True):
                    st.markdown('<div class="section-label">Label scorecard</div>', unsafe_allow_html=True)
                    st.caption("Raw model scores, not calibrated probabilities.")
                    for label in labels:
                        score = result["scores"][label]
                        threshold = settings.get("label_thresholds", {}).get(
                            label, settings["threshold"]
                        )
                        label_col, value_col = st.columns([3, 1])
                        with label_col:
                            st.markdown(f"**{label.replace('_', ' ').title()}**")
                        with value_col:
                            st.markdown(f"**{score:.4f}**")
                        st.progress(min(max(float(score), 0.0), 1.0))
                        st.caption(f"Configured threshold: {threshold:.2f}")

        except Exception as exc:
            st.error(f"Analysis failed: {exc}")

st.markdown(
    """
    <div class="footer">
      dHhi · ToxicLens is a research prototype. Do not use its predictions as the sole
      basis for moderation or consequential decisions.
    </div>
    """,
    unsafe_allow_html=True,
)
