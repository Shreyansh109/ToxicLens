"""ToxicLens: minimal dark-stage UI with dHhi branding."""
from pathlib import Path

import streamlit as st

from src.data_preprocessing import load_config
from src.predict import predict_texts
from src.transformer_scoring import load_transformer


st.set_page_config(
    page_title="dHhi · ToxicLens",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="collapsed",
)

CATEGORY_NAMES = {
    "insult": "Insult",
    "threat": "Threat",
    "identity_hate": "Identity-based hate",
    "obscene": "Obscene language",
}

# Dala-inspired dark canvas. Styling only; model logic remains unchanged.
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@200;300;400;500;600&display=swap');

    :root {
      --void: #000000;
      --white: #ffffff;
      --ash: #9a9a9a;
      --silver: #bdbdbd;
      --iris: #8052ff;
      --amber: #ffb829;
      --teal: #15846e;
    }

    html, body, [class*="css"] {
      font-family: 'Inter', ui-sans-serif, system-ui, sans-serif;
      color: var(--white);
      font-weight: 300;
    }
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
      background: var(--void);
      color: var(--white);
    }
    [data-testid="stHeader"] { background: transparent; }
    .block-container {
      max-width: 1280px;
      padding-top: 1.5rem;
      padding-bottom: 4rem;
    }
    p, li, label, .stCaption {
      color: var(--silver);
      font-weight: 300;
      line-height: 1.55;
    }
    h1, h2, h3 {
      color: var(--white) !important;
      font-weight: 400 !important;
      letter-spacing: -0.045em !important;
    }
    h1 { font-size: clamp(3.2rem, 8vw, 7rem) !important; line-height: .98 !important; }
    h2 { font-size: clamp(2rem, 4vw, 3rem) !important; line-height: 1.08 !important; }
    h3 { font-size: 1.55rem !important; }
    .topline {
      display: flex;
      align-items: center;
      gap: 12px;
      margin: 0 0 4rem 0;
    }
    .brand {
      color: var(--white);
      font-size: 1rem;
      font-weight: 500;
      letter-spacing: -.03em;
    }
    .brand-sub {
      color: var(--ash);
      font-size: .72rem;
      margin-top: 2px;
      letter-spacing: .02em;
    }
    .topright {
      margin-left: auto;
      color: var(--ash);
      font-size: .78rem;
      letter-spacing: .07em;
      text-transform: uppercase;
    }
    .eyebrow {
      color: var(--amber);
      font-size: .78rem;
      font-weight: 600;
      letter-spacing: .13em;
      text-transform: uppercase;
      margin-bottom: 1.2rem;
    }
    .hero-copy {
      color: var(--silver);
      font-size: 1.1rem;
      line-height: 1.65;
      max-width: 520px;
      font-weight: 200;
      margin-top: 1.3rem;
    }
    .particle-stage {
      width: min(100%, 440px);
      aspect-ratio: 1 / 1;
      margin: 0 auto;
      position: relative;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .particle-stage svg { width: 100%; height: 100%; overflow: visible; }
    .stage-label {
      position: absolute;
      bottom: 3%;
      left: 8%;
      color: #777;
      font-size: .68rem;
      letter-spacing: .12em;
      text-transform: uppercase;
    }
    .section-tag {
      color: var(--amber);
      font-size: .75rem;
      font-weight: 600;
      letter-spacing: .13em;
      text-transform: uppercase;
      margin-bottom: .7rem;
    }
    .stTextArea textarea {
      background: #080808 !important;
      color: var(--white) !important;
      border: 1px solid #383838 !important;
      border-radius: 12px !important;
      font-size: 1rem !important;
      line-height: 1.6 !important;
      padding: 1rem !important;
    }
    .stTextArea textarea:focus {
      border-color: var(--iris) !important;
      box-shadow: 0 0 0 1px var(--iris) !important;
    }
    .stTextArea label {
      color: var(--silver) !important;
      font-size: .86rem !important;
    }
    .stButton > button {
      background: var(--iris) !important;
      color: var(--white) !important;
      border: 0 !important;
      border-radius: 999px !important;
      padding: .72rem 1.25rem !important;
      min-height: 2.8rem;
      font-weight: 600 !important;
      letter-spacing: .025em;
      transition: filter .15s ease, transform .15s ease;
    }
    .stButton > button:hover { filter: brightness(1.12); transform: translateY(-1px); }
    [data-testid="stAlert"] {
      background: #0c0c0c;
      border: 1px solid #303030;
      border-radius: 12px;
      color: var(--silver);
    }
    [data-testid="stProgress"] > div {
      background: #242424;
      border-radius: 99px;
    }
    [data-testid="stProgress"] > div > div {
      background: var(--iris);
      border-radius: 99px;
    }
    hr { border-color: #252525 !important; margin: 2.5rem 0 !important; }
    .result-flag {
      color: var(--white);
      font-size: 1.45rem;
      font-weight: 400;
      letter-spacing: -.025em;
      line-height: 1.35;
    }
    .result-detail {
      color: var(--silver);
      font-size: .94rem;
      line-height: 1.6;
      margin-top: .5rem;
    }
    .label-chip {
      display: inline-block;
      border: 1px solid #494949;
      border-radius: 999px;
      padding: 5px 10px;
      margin: 3px 5px 3px 0;
      color: #ddd;
      font-size: .76rem;
    }
    .metric-number {
      color: var(--white);
      font-size: 1.5rem;
      font-weight: 400;
      letter-spacing: -.04em;
    }
    .footer {
      color: #777;
      font-size: .76rem;
      line-height: 1.6;
      margin-top: 3rem;
    }
    @media (max-width: 760px) {
      .block-container { padding-top: 1rem; }
      .topline { margin-bottom: 2.5rem; }
      .topright { display: none; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Minimal dHhi brand lockup; the logo is optional and loaded from assets/dhhi_logo.png.
logo_path = Path("assets") / "dhhi_logo.png"
brand_cols = st.columns([0.7, 7, 3], vertical_alignment="center")
with brand_cols[0]:
    if logo_path.exists():
        st.image(str(logo_path), width=48)
    else:
        st.markdown(
            '<div style="font-size:1.8rem;color:#8052ff;line-height:1">◢</div>',
            unsafe_allow_html=True,
        )
with brand_cols[1]:
    st.markdown(
        '<div class="brand">dHhi<div class="brand-sub">ToxicLens · comment analysis</div></div>',
        unsafe_allow_html=True,
    )
with brand_cols[2]:
    st.markdown('<div class="topright">Research prototype&nbsp;&nbsp; · &nbsp;&nbsp;Human review</div>', unsafe_allow_html=True)

st.markdown("---")

# Abstract triangular particle constellation, inspired by the provided style reference.
# This is decorative only and has no effect on model output.
particle_svg = """
<svg viewBox="0 0 420 420" xmlns="http://www.w3.org/2000/svg" aria-label="Abstract multicolour particle constellation">
 <defs>
  <radialGradient id="glow"><stop offset="0" stop-color="#8052ff" stop-opacity=".18"/><stop offset="1" stop-color="#000000" stop-opacity="0"/></radialGradient>
 </defs>
 <circle cx="210" cy="205" r="190" fill="url(#glow)"/>
 <g stroke-width="1.3" fill="none" opacity=".95">
  <path d="M55 170 L112 94 L156 133 L198 63 L255 95 L303 72 L356 143 L326 205 L362 262 L294 309 L250 354 L196 320 L143 347 L94 286 L61 242 Z" stroke="#8052ff" opacity=".55"/>
  <path d="M112 94 L198 63 L156 133 L255 95 L236 164 L303 72 L326 205 L255 95 L294 309 L236 164 L250 354 L196 320 L236 164 L143 347 L156 133 L94 286 L112 94" stroke="#373044" opacity=".85"/>
 </g>
 <g fill="#8052ff">
  <path d="M198 63 l8 -12 8 14z"/><path d="M236 164 l9 -12 5 15z"/><path d="M326 205 l8 -9 6 12z"/>
  <path d="M143 347 l7 -11 8 13z"/><path d="M55 170 l8 -10 7 13z"/><path d="M294 309 l8 -10 7 12z"/>
 </g>
 <g fill="#ffb829">
  <path d="M112 94 l8 -11 7 13z"/><path d="M303 72 l7 -12 8 14z"/><path d="M94 286 l8 -12 7 13z"/>
  <path d="M250 354 l8 -11 7 13z"/><path d="M362 262 l7 -11 8 13z"/>
 </g>
 <g fill="#15846e">
  <path d="M156 133 l8 -12 7 13z"/><path d="M255 95 l8 -11 7 13z"/><path d="M196 320 l8 -12 7 13z"/>
  <path d="M61 242 l8 -12 7 13z"/><path d="M356 143 l8 -11 7 13z"/>
 </g>
 <g fill="#d04dff">
  <path d="M75 218 l7 -10 7 12z"/><path d="M175 245 l8 -12 7 13z"/><path d="M278 226 l8 -11 7 13z"/>
  <path d="M322 280 l7 -10 7 12z"/><path d="M128 174 l7 -10 7 12z"/>
 </g>
 <g fill="#46a7ff">
  <path d="M146 76 l7 -10 7 12z"/><path d="M278 123 l8 -11 7 13z"/><path d="M216 286 l7 -10 7 12z"/>
  <path d="M108 251 l8 -11 7 13z"/><path d="M338 170 l7 -10 7 12z"/>
 </g>
 <g fill="#ffffff" opacity=".85">
  <circle cx="76" cy="120" r="2"/><circle cx="174" cy="54" r="2"/><circle cx="283" cy="52" r="1.8"/>
  <circle cx="374" cy="189" r="2"/><circle cx="349" cy="321" r="1.8"/><circle cx="198" cy="375" r="2"/>
  <circle cx="52" cy="270" r="1.5"/><circle cx="128" cy="315" r="1.7"/><circle cx="235" cy="37" r="1.5"/>
  <circle cx="320" cy="116" r="1.7"/><circle cx="87" cy="206" r="1.5"/><circle cx="263" cy="340" r="1.6"/>
 </g>
</svg>
"""

hero_left, hero_right = st.columns([1.05, 0.95], gap="large", vertical_alignment="center")
with hero_left:
    st.markdown('<div class="eyebrow">MODEL-ASSISTED REVIEW</div>', unsafe_allow_html=True)
    st.markdown("# Understand the signal.<br>Keep human judgment.", unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-copy">ToxicLens highlights language that may need attention. '
        'Review the labels and raw scores, then use context and human judgment to decide what happens next.</div>',
        unsafe_allow_html=True,
    )
    st.write("")
    st.markdown('<div style="color:#ffb829;font-size:.78rem;letter-spacing:.1em;font-weight:600">SIX LABELS · ONE COMMENT AT A TIME</div>', unsafe_allow_html=True)
with hero_right:
    st.markdown(f'<div class="particle-stage">{particle_svg}<div class="stage-label">Signals · not verdicts</div></div>', unsafe_allow_html=True)

st.markdown("---")
st.markdown('<div class="section-tag">01 / Input</div>', unsafe_allow_html=True)
st.markdown("## Analyse a comment")
st.markdown(
    '<div style="color:#9a9a9a;max-width:700px;margin-bottom:1.2rem">Paste a comment below to inspect the model’s configured label scores. Avoid treating a score as certainty.</div>',
    unsafe_allow_html=True,
)

text = st.text_area(
    "Comment text",
    height=170,
    max_chars=10000,
    placeholder="Paste a comment here…",
)

action_col, hint_col = st.columns([1, 3], vertical_alignment="center")
with action_col:
    analyse = st.button("ANALYSE TEXT", type="primary", use_container_width=True)
with hint_col:
    st.caption("Local transformer · Raw scores · Human review rule")

st.warning(
    "This tool can make mistakes. Scores are raw model scores, not calibrated probabilities. "
    "Use predictions as decision support, not as definitive judgments about a person."
)

try:
    @st.cache_resource
    def get_model():
        config = load_config()
        scorer, labels = load_transformer(config)
        return config, scorer, labels

    config, scorer, labels = get_model()
except Exception as exc:
    st.error(f"Could not load the transformer model: {exc}")
    st.info(
        "Check that the trained model exists in models/transformer "
        "and that your project's virtual environment is active."
    )
    st.stop()

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
            st.markdown('<div class="section-tag">02 / Result</div>', unsafe_allow_html=True)
            st.markdown("## What the model flagged")

            if result["label"] == "toxic":
                st.markdown('<div class="result-flag">Potential toxicity flagged<span style="color:#ffb829">.</span></div>', unsafe_allow_html=True)
                st.markdown('<div class="result-detail">One or more configured labels crossed their thresholds. This is a model signal, not a final decision.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="result-flag">No configured label was flagged<span style="color:#8052ff">.</span></div>', unsafe_allow_html=True)
                st.markdown('<div class="result-detail">This does not guarantee that the comment is harmless or context-free.</div>', unsafe_allow_html=True)

            st.write("")
            review_left, review_right = st.columns([1, 1], gap="large")
            with review_left:
                st.markdown('<div class="section-tag">Flagged labels</div>', unsafe_allow_html=True)
                if result["flagged_labels"]:
                    for label in result["flagged_labels"]:
                        st.markdown(f'<span class="label-chip">{label.replace("_", " ").title()}</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="result-detail">No labels crossed their configured thresholds.</div>', unsafe_allow_html=True)

                st.write("")
                st.markdown('<div class="section-tag">Display categories</div>', unsafe_allow_html=True)
                if result["categories"]:
                    for category in result["categories"]:
                        st.markdown(f'<span class="label-chip">{CATEGORY_NAMES.get(category, category)}</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="result-detail">No display categories were assigned.</div>', unsafe_allow_html=True)

            with review_right:
                st.markdown('<div class="section-tag">Human review</div>', unsafe_allow_html=True)
                if result["needs_human_review"]:
                    st.markdown('<div class="result-flag" style="color:#ffb829">Review recommended<span>.</span></div>', unsafe_allow_html=True)
                    st.markdown('<div class="result-detail">The configured rule detected a near-threshold score or a flagged threat label.</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="result-flag">No review requested<span>.</span></div>', unsafe_allow_html=True)
                    st.markdown('<div class="result-detail">The review rule cannot detect every confidently wrong prediction.</div>', unsafe_allow_html=True)

            st.markdown("---")
            st.markdown('<div class="section-tag">03 / Score details</div>', unsafe_allow_html=True)
            st.markdown("## Raw model scores")
            st.markdown('<div class="result-detail">Scores are not calibrated probabilities and do not measure a person’s intent.</div>', unsafe_allow_html=True)

            score_cols = st.columns(2, gap="large")
            for index, label in enumerate(labels):
                with score_cols[index % 2]:
                    score = result["scores"][label]
                    threshold = settings.get("label_thresholds", {}).get(label, settings["threshold"])
                    label_col, score_col = st.columns([3, 1])
                    with label_col:
                        st.markdown(f"**{label.replace('_', ' ').title()}**")
                    with score_col:
                        st.markdown(f"<div style='text-align:right;color:#bdbdbd'>{score:.4f}</div>", unsafe_allow_html=True)
                    st.progress(min(max(float(score), 0.0), 1.0))
                    st.caption(f"Configured threshold: {threshold:.2f}")

        except Exception as exc:
            st.error(f"Analysis failed: {exc}")

st.markdown("---")
st.markdown(
    '<div class="footer">dHhi · ToxicLens is a research prototype. Do not use predictions as the sole basis for moderation or consequential decisions.</div>',
    unsafe_allow_html=True,
)
