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
      width: min(100%, 570px);
      aspect-ratio: 1 / 1;
      margin: 0 auto;
      position: relative;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .particle-stage svg { width: 100%; height: 100%; overflow: visible; }
     .particle-cloud { transform-origin: 210px 210px; animation: exclamation-float 7s ease-in-out infinite; will-change: transform; }
    .particle { transform-box: fill-box; transform-origin: center; animation: triangle-twinkle 4.6s ease-in-out infinite; }
    .particle:nth-child(3n) { animation-delay: -1.2s; }
    .particle:nth-child(4n) { animation-delay: -2.1s; }
    .particle:nth-child(5n) { animation-delay: -3.2s; }
    .ambient { animation: ambient-drift 9s ease-in-out infinite alternate; }
    @keyframes exclamation-float {
      0%, 100% { transform: translate3d(0, 0, 0) rotate(-1deg); }
      25% { transform: translate3d(2px, -5px, 0) rotate(.25deg); }
      50% { transform: translate3d(0, -10px, 0) rotate(1deg); }
      75% { transform: translate3d(-2px, -5px, 0) rotate(.25deg); }
    }
    @keyframes triangle-twinkle {
      0%, 100% { opacity: .72; }
      50% { opacity: 1; }
    }
    @keyframes ambient-drift {
      from { transform: translate(0, 0); opacity: .35; }
      to { transform: translate(5px, -8px); opacity: .9; }
    }
    @media (prefers-reduced-motion: reduce) {
      .particle-cloud, .particle, .ambient { animation: none !important; }
    }
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
<svg viewBox="0 0 420 420" xmlns="http://www.w3.org/2000/svg" aria-label="Dense animated triangular particle cloud shaped like a three-dimensional exclamation mark">
 <defs>
  <radialGradient id="particleGlow"><stop offset="0" stop-color="#8052ff" stop-opacity=".18"/><stop offset="1" stop-color="#000000" stop-opacity="0"/></radialGradient>
  <linearGradient id="stemSide" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#241344"/><stop offset=".55" stop-color="#07060d"/><stop offset="1" stop-color="#40205c"/></linearGradient>
  <linearGradient id="stemFront" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#8052ff" stop-opacity=".12"/><stop offset=".48" stop-color="#ffffff" stop-opacity=".02"/><stop offset="1" stop-color="#ffb829" stop-opacity=".14"/></linearGradient>
 </defs>
 <ellipse cx="210" cy="210" rx="180" ry="195" fill="url(#particleGlow)"/>
 <g class="particle-cloud">
  <!-- Soft 3D extruded silhouette behind the particle surface -->
  <path d="M194 31 L250 31 L242 265 L238 285 L255 304 L255 358 L241 382 L184 382 L166 360 L166 315 L184 291 L178 265 Z"
        fill="url(#stemSide)" opacity=".88" transform="translate(12 4)"/>
  <path d="M181 28 Q210 16 239 28 L231 268 Q210 280 189 268 Z"
        fill="url(#stemFront)" stroke="#8052ff" stroke-opacity=".32" stroke-width="1"/>
  <ellipse cx="210" cy="333" rx="43" ry="43" fill="#150d26" stroke="#ffb829" stroke-opacity=".24" stroke-width="1.5" transform="translate(10 3)"/>
  <ellipse cx="210" cy="331" rx="39" ry="39" fill="url(#stemFront)" stroke="#8052ff" stroke-opacity=".28" stroke-width="1"/>
  <g class="ambient">
<circle class="ambient" cx="314.0" cy="248.6" r="1.4" fill="#ff7dcb" opacity="0.67"/>
<circle class="ambient" cx="126.0" cy="28.1" r="1.2" fill="#46a7ff" opacity="0.49"/>
<polygon class="ambient" points="162.1,78.9 159.6,83.1 164.6,83.1" fill="none" stroke="#ffb829" stroke-width=".9" opacity="0.43"/>
<circle class="ambient" cx="360.2" cy="151.4" r="1.5" fill="#ff7dcb" opacity="0.42"/>
<polygon class="ambient" points="88.5,364.2 86.5,367.6 90.5,367.6" fill="none" stroke="#15846e" stroke-width=".9" opacity="0.27"/>
<polygon class="ambient" points="87.5,164.0 84.7,168.7 90.2,168.7" fill="none" stroke="#d04dff" stroke-width=".9" opacity="0.54"/>
<polygon class="ambient" points="147.5,267.3 145.0,271.4 149.9,271.4" fill="none" stroke="#46a7ff" stroke-width=".9" opacity="0.38"/>
<polygon class="ambient" points="155.4,164.5 153.7,167.5 157.1,167.5" fill="none" stroke="#d04dff" stroke-width=".9" opacity="0.24"/>
<circle class="ambient" cx="111.1" cy="231.1" r="1.8" fill="#8052ff" opacity="0.36"/>
<circle class="ambient" cx="337.9" cy="28.0" r="1.8" fill="#8052ff" opacity="0.32"/>
<polygon class="ambient" points="375.2,387.0 372.4,391.7 378.0,391.7" fill="none" stroke="#46a7ff" stroke-width=".9" opacity="0.37"/>
<polygon class="ambient" points="372.6,13.0 370.8,16.0 374.3,16.0" fill="none" stroke="#ffb829" stroke-width=".9" opacity="0.38"/>
<circle class="ambient" cx="333.8" cy="174.6" r="1.7" fill="#ffb829" opacity="0.27"/>
<polygon class="ambient" points="105.4,246.1 103.0,250.2 107.9,250.2" fill="none" stroke="#ff7dcb" stroke-width=".9" opacity="0.26"/>
<circle class="ambient" cx="118.1" cy="35.1" r="1.2" fill="#ffb829" opacity="0.38"/>
<polygon class="ambient" points="267.0,228.6 264.4,233.1 269.7,233.1" fill="none" stroke="#f4f0ff" stroke-width=".9" opacity="0.38"/>
<circle class="ambient" cx="329.7" cy="268.6" r="1.7" fill="#15846e" opacity="0.26"/>
<polygon class="ambient" points="49.0,231.0 45.0,237.8 53.0,237.8" fill="none" stroke="#ff7dcb" stroke-width=".9" opacity="0.23"/>
<circle class="ambient" cx="320.1" cy="208.6" r="1.3" fill="#8052ff" opacity="0.33"/>
<polygon class="ambient" points="58.5,303.4 55.7,308.1 61.2,308.1" fill="none" stroke="#ffb829" stroke-width=".9" opacity="0.43"/>
<polygon class="ambient" points="319.1,74.9 317.1,78.4 321.2,78.4" fill="none" stroke="#15846e" stroke-width=".9" opacity="0.59"/>
<circle class="ambient" cx="336.1" cy="258.0" r="1.3" fill="#8052ff" opacity="0.62"/>
<polygon class="ambient" points="317.2,172.3 311.8,181.5 322.6,181.5" fill="none" stroke="#ffb829" stroke-width=".9" opacity="0.47"/>
<circle class="ambient" cx="184.9" cy="383.6" r="1.2" fill="#8052ff" opacity="0.46"/>
<circle class="ambient" cx="366.8" cy="329.2" r="1.4" fill="#15846e" opacity="0.46"/>
<polygon class="ambient" points="25.7,237.8 23.0,242.5 28.5,242.5" fill="none" stroke="#8052ff" stroke-width=".9" opacity="0.52"/>
<polygon class="ambient" points="170.1,386.2 167.6,390.4 172.5,390.4" fill="none" stroke="#ffb829" stroke-width=".9" opacity="0.53"/>
<polygon class="ambient" points="53.4,173.1 51.7,176.0 55.2,176.0" fill="none" stroke="#f4f0ff" stroke-width=".9" opacity="0.47"/>
<polygon class="ambient" points="293.4,268.1 289.1,275.5 297.8,275.5" fill="none" stroke="#ffb829" stroke-width=".9" opacity="0.67"/>
<polygon class="ambient" points="58.0,386.1 54.6,391.9 61.5,391.9" fill="none" stroke="#46a7ff" stroke-width=".9" opacity="0.22"/>
<circle class="ambient" cx="90.0" cy="52.3" r="1.5" fill="#ff7dcb" opacity="0.64"/>
<circle class="ambient" cx="281.0" cy="366.4" r="1.4" fill="#d04dff" opacity="0.35"/>
<circle class="ambient" cx="380.0" cy="53.4" r="1.6" fill="#ffb829" opacity="0.36"/>
<polygon class="ambient" points="270.1,47.6 266.7,53.4 273.5,53.4" fill="none" stroke="#ffb829" stroke-width=".9" opacity="0.46"/>
<circle class="ambient" cx="372.6" cy="190.3" r="1.5" fill="#46a7ff" opacity="0.65"/>
<polygon class="ambient" points="378.9,278.9 376.9,282.3 380.9,282.3" fill="none" stroke="#46a7ff" stroke-width=".9" opacity="0.56"/>
<polygon class="ambient" points="113.6,15.0 111.7,18.2 115.4,18.2" fill="none" stroke="#46a7ff" stroke-width=".9" opacity="0.33"/>
<circle class="ambient" cx="318.5" cy="44.9" r="1.2" fill="#f4f0ff" opacity="0.27"/>
<polygon class="ambient" points="133.5,92.6 128.8,100.5 138.1,100.5" fill="none" stroke="#15846e" stroke-width=".9" opacity="0.65"/>
<polygon class="ambient" points="41.7,143.3 39.5,147.1 43.9,147.1" fill="none" stroke="#f4f0ff" stroke-width=".9" opacity="0.43"/>
<circle class="ambient" cx="329.7" cy="361.5" r="1.5" fill="#d04dff" opacity="0.29"/>
<polygon class="ambient" points="343.2,303.5 341.7,306.1 344.7,306.1" fill="none" stroke="#d04dff" stroke-width=".9" opacity="0.36"/>
<circle class="ambient" cx="151.7" cy="156.3" r="1.2" fill="#46a7ff" opacity="0.42"/>
<circle class="ambient" cx="38.3" cy="124.9" r="1.5" fill="#8052ff" opacity="0.38"/>
<polygon class="ambient" points="378.0,296.5 373.7,303.7 382.2,303.7" fill="none" stroke="#8052ff" stroke-width=".9" opacity="0.46"/>
<polygon class="ambient" points="232.7,18.5 228.1,26.3 237.3,26.3" fill="none" stroke="#d04dff" stroke-width=".9" opacity="0.67"/>
<polygon class="ambient" points="311.1,11.1 306.5,19.0 315.8,19.0" fill="none" stroke="#ffb829" stroke-width=".9" opacity="0.67"/>
<polygon class="ambient" points="68.1,123.4 64.4,129.7 71.8,129.7" fill="none" stroke="#8052ff" stroke-width=".9" opacity="0.42"/>
<polygon class="ambient" points="99.9,276.3 94.8,285.1 105.0,285.1" fill="none" stroke="#f4f0ff" stroke-width=".9" opacity="0.60"/>
<polygon class="ambient" points="357.5,314.4 354.9,318.8 360.1,318.8" fill="none" stroke="#ffb829" stroke-width=".9" opacity="0.32"/>
<circle class="ambient" cx="159.2" cy="358.2" r="1.4" fill="#8052ff" opacity="0.58"/>
<polygon class="ambient" points="135.2,270.0 131.6,276.2 138.9,276.2" fill="none" stroke="#46a7ff" stroke-width=".9" opacity="0.68"/>
<circle class="ambient" cx="61.7" cy="238.9" r="1.7" fill="#ffb829" opacity="0.46"/>
<polygon class="ambient" points="112.4,321.9 110.0,326.1 114.9,326.1" fill="none" stroke="#f4f0ff" stroke-width=".9" opacity="0.47"/>
<circle class="ambient" cx="157.6" cy="101.0" r="1.5" fill="#46a7ff" opacity="0.59"/>
<polygon class="ambient" points="333.8,342.1 329.9,348.7 337.7,348.7" fill="none" stroke="#46a7ff" stroke-width=".9" opacity="0.61"/>
<polygon class="ambient" points="117.1,196.1 113.9,201.6 120.4,201.6" fill="none" stroke="#ff7dcb" stroke-width=".9" opacity="0.65"/>
<circle class="ambient" cx="294.6" cy="408.0" r="1.5" fill="#46a7ff" opacity="0.40"/>
<polygon class="ambient" points="79.6,394.1 77.1,398.3 82.1,398.3" fill="none" stroke="#8052ff" stroke-width=".9" opacity="0.37"/>
<circle class="ambient" cx="299.5" cy="156.5" r="1.2" fill="#ffb829" opacity="0.41"/>
<circle class="ambient" cx="371.6" cy="393.4" r="1.5" fill="#d04dff" opacity="0.65"/>
<circle class="ambient" cx="97.9" cy="375.5" r="1.5" fill="#46a7ff" opacity="0.66"/>
<circle class="ambient" cx="342.1" cy="281.5" r="1.8" fill="#d04dff" opacity="0.43"/>
<polygon class="ambient" points="62.2,86.6 57.4,94.7 66.9,94.7" fill="none" stroke="#15846e" stroke-width=".9" opacity="0.35"/>
<circle class="ambient" cx="401.2" cy="341.0" r="1.8" fill="#15846e" opacity="0.50"/>
<polygon class="ambient" points="70.3,138.9 64.9,148.0 75.6,148.0" fill="none" stroke="#f4f0ff" stroke-width=".9" opacity="0.65"/>
<polygon class="ambient" points="167.2,114.7 162.3,123.0 172.1,123.0" fill="none" stroke="#d04dff" stroke-width=".9" opacity="0.34"/>
<polygon class="ambient" points="338.4,200.4 336.6,203.3 340.1,203.3" fill="none" stroke="#d04dff" stroke-width=".9" opacity="0.52"/>
<circle class="ambient" cx="328.9" cy="316.2" r="1.1" fill="#ffb829" opacity="0.39"/>
<polygon class="ambient" points="354.5,59.2 351.2,64.6 357.7,64.6" fill="none" stroke="#f4f0ff" stroke-width=".9" opacity="0.33"/>
<circle class="ambient" cx="348.0" cy="69.0" r="1.0" fill="#f4f0ff" opacity="0.22"/>
<polygon class="ambient" points="52.2,256.1 48.4,262.6 55.9,262.6" fill="none" stroke="#ffb829" stroke-width=".9" opacity="0.32"/>
<polygon class="ambient" points="88.5,87.0 84.4,94.0 92.7,94.0" fill="none" stroke="#f4f0ff" stroke-width=".9" opacity="0.59"/>
<polygon class="ambient" points="358.8,277.2 356.9,280.4 360.7,280.4" fill="none" stroke="#8052ff" stroke-width=".9" opacity="0.29"/>
<polygon class="ambient" points="168.5,138.0 165.0,144.0 172.1,144.0" fill="none" stroke="#46a7ff" stroke-width=".9" opacity="0.32"/>
<circle class="ambient" cx="393.9" cy="388.4" r="1.2" fill="#f4f0ff" opacity="0.46"/>
<polygon class="ambient" points="165.8,140.0 161.7,147.0 170.0,147.0" fill="none" stroke="#8052ff" stroke-width=".9" opacity="0.21"/>
<polygon class="ambient" points="347.9,329.1 346.3,331.8 349.4,331.8" fill="none" stroke="#d04dff" stroke-width=".9" opacity="0.38"/>
<polygon class="ambient" points="101.6,138.5 97.3,145.7 105.8,145.7" fill="none" stroke="#8052ff" stroke-width=".9" opacity="0.21"/>
<polygon class="ambient" points="225.3,373.8 223.6,376.6 226.9,376.6" fill="none" stroke="#ffb829" stroke-width=".9" opacity="0.44"/>
<circle class="ambient" cx="311.7" cy="118.0" r="1.4" fill="#f4f0ff" opacity="0.45"/>
<polygon class="ambient" points="333.1,344.5 328.6,352.0 337.5,352.0" fill="none" stroke="#ffb829" stroke-width=".9" opacity="0.21"/>
<polygon class="ambient" points="254.3,190.0 250.1,197.1 258.5,197.1" fill="none" stroke="#ff7dcb" stroke-width=".9" opacity="0.64"/>
<polygon class="ambient" points="27.4,42.0 23.6,48.3 31.2,48.3" fill="none" stroke="#46a7ff" stroke-width=".9" opacity="0.37"/>
<circle class="ambient" cx="102.8" cy="292.5" r="1.2" fill="#ff7dcb" opacity="0.24"/>
<circle class="ambient" cx="168.7" cy="260.3" r="1.7" fill="#d04dff" opacity="0.65"/>
<circle class="ambient" cx="279.6" cy="336.0" r="1.5" fill="#ffb829" opacity="0.51"/>
<circle class="ambient" cx="132.9" cy="103.0" r="1.2" fill="#f4f0ff" opacity="0.27"/>
<polygon class="ambient" points="387.1,168.2 382.4,176.3 391.8,176.3" fill="none" stroke="#f4f0ff" stroke-width=".9" opacity="0.48"/>
<polygon class="ambient" points="355.3,258.7 353.2,262.4 357.5,262.4" fill="none" stroke="#15846e" stroke-width=".9" opacity="0.67"/>
<circle class="ambient" cx="343.3" cy="111.7" r="0.9" fill="#f4f0ff" opacity="0.52"/>
<polygon class="ambient" points="89.1,101.2 83.7,110.6 94.6,110.6" fill="none" stroke="#f4f0ff" stroke-width=".9" opacity="0.48"/>
<circle class="ambient" cx="333.0" cy="177.6" r="1.4" fill="#ffb829" opacity="0.67"/>
<polygon class="ambient" points="389.0,292.6 384.8,299.8 393.3,299.8" fill="none" stroke="#f4f0ff" stroke-width=".9" opacity="0.48"/>
<circle class="ambient" cx="304.8" cy="132.6" r="1.2" fill="#46a7ff" opacity="0.62"/>
<polygon class="ambient" points="101.0,172.7 98.0,177.8 103.9,177.8" fill="none" stroke="#ffb829" stroke-width=".9" opacity="0.35"/>
<polygon class="ambient" points="84.4,175.4 82.8,178.2 86.0,178.2" fill="none" stroke="#f4f0ff" stroke-width=".9" opacity="0.34"/>
<circle class="ambient" cx="281.6" cy="66.5" r="1.5" fill="#ff7dcb" opacity="0.59"/>
<circle class="ambient" cx="317.6" cy="124.2" r="1.6" fill="#ffb829" opacity="0.58"/>
<circle class="ambient" cx="267.0" cy="30.6" r="1.2" fill="#8052ff" opacity="0.37"/>
<polygon class="ambient" points="373.3,281.6 367.9,290.7 378.6,290.7" fill="none" stroke="#f4f0ff" stroke-width=".9" opacity="0.32"/>
<circle class="ambient" cx="279.6" cy="26.6" r="1.1" fill="#15846e" opacity="0.63"/>
<circle class="ambient" cx="341.4" cy="268.5" r="1.3" fill="#ffb829" opacity="0.37"/>
<circle class="ambient" cx="80.3" cy="37.7" r="0.9" fill="#d04dff" opacity="0.30"/>
<polygon class="ambient" points="86.0,150.9 81.6,158.4 90.4,158.4" fill="none" stroke="#46a7ff" stroke-width=".9" opacity="0.35"/>
<circle class="ambient" cx="292.9" cy="282.2" r="1.7" fill="#15846e" opacity="0.46"/>
<polygon class="ambient" points="359.8,268.6 357.5,272.4 362.0,272.4" fill="none" stroke="#f4f0ff" stroke-width=".9" opacity="0.31"/>
<circle class="ambient" cx="41.2" cy="82.1" r="1.8" fill="#15846e" opacity="0.28"/>
<circle class="ambient" cx="310.7" cy="224.8" r="1.7" fill="#f4f0ff" opacity="0.50"/>
<circle class="ambient" cx="70.4" cy="131.1" r="0.9" fill="#8052ff" opacity="0.51"/>
<polygon class="ambient" points="112.9,300.7 109.3,306.9 116.6,306.9" fill="none" stroke="#ff7dcb" stroke-width=".9" opacity="0.30"/>
<polygon class="ambient" points="156.0,403.8 154.0,407.2 158.0,407.2" fill="none" stroke="#8052ff" stroke-width=".9" opacity="0.35"/>
<circle class="ambient" cx="387.0" cy="81.7" r="1.2" fill="#ffb829" opacity="0.44"/>
<polygon class="ambient" points="256.0,165.2 252.2,171.6 259.7,171.6" fill="none" stroke="#15846e" stroke-width=".9" opacity="0.27"/>
<circle class="ambient" cx="79.1" cy="340.5" r="0.8" fill="#8052ff" opacity="0.46"/>
<polygon class="ambient" points="346.8,117.1 343.0,123.5 350.6,123.5" fill="none" stroke="#ffb829" stroke-width=".9" opacity="0.55"/>
<polygon class="ambient" points="368.5,178.1 365.8,182.7 371.2,182.7" fill="none" stroke="#46a7ff" stroke-width=".9" opacity="0.44"/>
<circle class="ambient" cx="23.1" cy="294.5" r="1.8" fill="#ffb829" opacity="0.66"/>
<polygon class="ambient" points="294.5,88.4 290.4,95.4 298.6,95.4" fill="none" stroke="#8052ff" stroke-width=".9" opacity="0.70"/>
<circle class="ambient" cx="359.3" cy="259.0" r="1.8" fill="#ffb829" opacity="0.25"/>
<circle class="ambient" cx="156.3" cy="273.8" r="1.5" fill="#15846e" opacity="0.30"/>
<circle class="ambient" cx="89.8" cy="212.6" r="1.8" fill="#ffb829" opacity="0.37"/>
<circle class="ambient" cx="311.1" cy="309.6" r="1.5" fill="#ff7dcb" opacity="0.20"/>
<circle class="ambient" cx="163.8" cy="356.9" r="0.7" fill="#46a7ff" opacity="0.22"/>
<polygon class="ambient" points="299.7,122.4 297.9,125.5 301.6,125.5" fill="none" stroke="#d04dff" stroke-width=".9" opacity="0.39"/>
<polygon class="ambient" points="333.7,82.4 330.9,87.1 336.4,87.1" fill="none" stroke="#8052ff" stroke-width=".9" opacity="0.48"/>
<polygon class="ambient" points="154.5,314.5 152.2,318.4 156.7,318.4" fill="none" stroke="#46a7ff" stroke-width=".9" opacity="0.50"/>
<polygon class="ambient" points="244.9,166.2 243.1,169.2 246.7,169.2" fill="none" stroke="#f4f0ff" stroke-width=".9" opacity="0.54"/>
<circle class="ambient" cx="21.1" cy="54.7" r="0.8" fill="#46a7ff" opacity="0.50"/>
<polygon class="ambient" points="67.7,197.9 64.4,203.6 71.0,203.6" fill="none" stroke="#15846e" stroke-width=".9" opacity="0.64"/>
<circle class="ambient" cx="143.7" cy="278.1" r="1.0" fill="#8052ff" opacity="0.45"/>
<polygon class="ambient" points="93.1,84.1 88.5,91.9 97.7,91.9" fill="none" stroke="#ff7dcb" stroke-width=".9" opacity="0.25"/>
<circle class="ambient" cx="267.2" cy="364.3" r="1.0" fill="#ffb829" opacity="0.24"/>
<circle class="ambient" cx="395.3" cy="78.5" r="1.4" fill="#46a7ff" opacity="0.39"/>
<circle class="ambient" cx="254.7" cy="316.4" r="0.7" fill="#ffb829" opacity="0.30"/>
<circle class="ambient" cx="315.9" cy="284.9" r="1.5" fill="#d04dff" opacity="0.57"/>
<circle class="ambient" cx="324.5" cy="191.5" r="1.3" fill="#8052ff" opacity="0.57"/>
<polygon class="ambient" points="359.5,300.3 355.7,306.7 363.2,306.7" fill="none" stroke="#d04dff" stroke-width=".9" opacity="0.53"/>
<circle class="ambient" cx="293.3" cy="403.5" r="0.8" fill="#ffb829" opacity="0.21"/>
<polygon class="ambient" points="62.5,171.6 58.3,178.8 66.8,178.8" fill="none" stroke="#ff7dcb" stroke-width=".9" opacity="0.66"/>
<polygon class="ambient" points="341.1,368.3 338.1,373.4 344.1,373.4" fill="none" stroke="#15846e" stroke-width=".9" opacity="0.61"/>
<polygon class="ambient" points="69.2,232.2 65.6,238.2 72.8,238.2" fill="none" stroke="#15846e" stroke-width=".9" opacity="0.20"/>
<circle class="ambient" cx="72.0" cy="254.5" r="0.9" fill="#46a7ff" opacity="0.22"/>
<polygon class="ambient" points="30.8,180.1 26.7,187.0 34.8,187.0" fill="none" stroke="#f4f0ff" stroke-width=".9" opacity="0.31"/>
<circle class="ambient" cx="132.5" cy="18.5" r="1.7" fill="#46a7ff" opacity="0.69"/>
<circle class="ambient" cx="79.6" cy="404.4" r="1.8" fill="#15846e" opacity="0.50"/>
<circle class="ambient" cx="381.7" cy="204.1" r="0.7" fill="#d04dff" opacity="0.68"/>
<circle class="ambient" cx="114.6" cy="234.2" r="1.5" fill="#15846e" opacity="0.53"/>
<polygon class="ambient" points="24.1,145.6 18.9,154.5 29.4,154.5" fill="none" stroke="#ffb829" stroke-width=".9" opacity="0.40"/>
<circle class="ambient" cx="396.8" cy="167.1" r="1.6" fill="#15846e" opacity="0.64"/>
<polygon class="ambient" points="53.8,300.7 49.0,308.9 58.6,308.9" fill="none" stroke="#f4f0ff" stroke-width=".9" opacity="0.36"/>
<polygon class="ambient" points="133.8,294.7 132.0,297.7 135.6,297.7" fill="none" stroke="#f4f0ff" stroke-width=".9" opacity="0.32"/>
<circle class="ambient" cx="160.1" cy="62.5" r="1.7" fill="#ffb829" opacity="0.51"/>
<polygon class="ambient" points="171.8,68.0 167.5,75.3 176.2,75.3" fill="none" stroke="#f4f0ff" stroke-width=".9" opacity="0.41"/>
<circle class="ambient" cx="319.7" cy="351.2" r="1.1" fill="#ffb829" opacity="0.36"/>
  </g>
  <g aria-label="Dense triangular particles forming an exclamation mark">
<polygon class="particle" points="173.7,190.6 170.7,196.8 176.7,196.8" fill="#46a7ff" opacity="0.88" style="animation-delay:-1.94s"/>
<polygon class="particle" points="198.3,180.5 196.9,183.3 199.6,183.3" fill="#d04dff" opacity="0.79" style="animation-delay:-1.60s"/>
<polygon class="particle" points="199.4,96.5 197.3,100.8 201.5,100.8" fill="#f4f0ff" opacity="0.96" style="animation-delay:-0.11s"/>
<polygon class="particle" points="175.1,229.3 173.4,233.0 176.9,233.0" fill="#8052ff" opacity="0.60" style="animation-delay:-1.18s"/>
<polygon class="particle" points="215.4,225.8 213.0,230.8 217.8,230.8" fill="#46a7ff" opacity="0.40" style="animation-delay:-1.89s"/>
<polygon class="particle" points="203.0,79.5 200.4,84.9 205.5,84.9" fill="#8052ff" opacity="0.93" style="animation-delay:-3.73s"/>
<polygon class="particle" points="167.0,168.2 165.5,171.3 168.5,171.3" fill="#ffb829" opacity="0.90" style="animation-delay:-1.09s"/>
<polygon class="particle" points="186.5,242.0 183.8,247.6 189.2,247.6" fill="#f4f0ff" opacity="0.69" style="animation-delay:-0.34s"/>
<polygon class="particle" points="190.5,178.0 188.3,182.5 192.7,182.5" fill="#f4f0ff" opacity="0.51" style="animation-delay:-1.53s"/>
<polygon class="particle" points="206.0,42.1 204.9,44.4 207.2,44.4" fill="#d04dff" opacity="0.77" style="animation-delay:-3.65s"/>
<polygon class="particle" points="195.8,182.4 192.4,189.4 199.1,189.4" fill="#8052ff" opacity="0.42" style="animation-delay:-3.37s"/>
<polygon class="particle" points="186.9,149.6 184.8,154.1 189.1,154.1" fill="#d04dff" opacity="0.73" style="animation-delay:-1.83s"/>
<polygon class="particle" points="184.8,99.4 182.7,103.7 186.9,103.7" fill="#46a7ff" opacity="0.69" style="animation-delay:-0.34s"/>
<polygon class="particle" points="193.1,32.5 191.9,35.0 194.4,35.0" fill="#d04dff" opacity="0.83" style="animation-delay:-2.39s"/>
<polygon class="particle" points="183.1,105.8 181.9,108.3 184.4,108.3" fill="#ff7dcb" opacity="0.87" style="animation-delay:-1.18s"/>
<polygon class="particle" points="226.8,242.7 224.4,247.5 229.1,247.5" fill="#ffb829" opacity="0.93" style="animation-delay:-3.84s"/>
<polygon class="particle" points="224.7,230.2 221.4,237.0 228.0,237.0" fill="#ffb829" opacity="0.56" style="animation-delay:-3.98s"/>
<polygon class="particle" points="211.3,92.6 208.9,97.6 213.8,97.6" fill="#8052ff" opacity="0.65" style="animation-delay:-2.67s"/>
<polygon class="particle" points="220.3,208.0 217.3,214.3 223.4,214.3" fill="#ff7dcb" opacity="0.90" style="animation-delay:-0.27s"/>
<polygon class="particle" points="208.9,231.6 206.7,236.0 211.0,236.0" fill="#8052ff" opacity="0.75" style="animation-delay:-0.12s"/>
<polygon class="particle" points="216.6,184.4 214.1,189.7 219.2,189.7" fill="#8052ff" opacity="0.40" style="animation-delay:-3.43s"/>
<polygon class="particle" points="228.0,39.2 225.6,44.3 230.5,44.3" fill="#f4f0ff" opacity="0.43" style="animation-delay:-1.04s"/>
<polygon class="particle" points="227.5,69.5 224.2,76.1 230.7,76.1" fill="#46a7ff" opacity="0.48" style="animation-delay:-3.07s"/>
<polygon class="particle" points="172.7,104.8 170.2,110.0 175.2,110.0" fill="#f4f0ff" opacity="0.44" style="animation-delay:-2.09s"/>
<polygon class="particle" points="247.1,54.1 246.0,56.4 248.3,56.4" fill="#ffb829" opacity="0.82" style="animation-delay:-2.68s"/>
<polygon class="particle" points="235.3,183.7 232.9,188.5 237.6,188.5" fill="#8052ff" opacity="0.95" style="animation-delay:-3.09s"/>
<polygon class="particle" points="225.0,87.7 222.0,93.8 227.9,93.8" fill="#8052ff" opacity="0.86" style="animation-delay:-0.21s"/>
<polygon class="particle" points="216.9,227.4 214.5,232.2 219.2,232.2" fill="#15846e" opacity="0.76" style="animation-delay:-0.09s"/>
<polygon class="particle" points="209.6,66.2 207.9,69.6 211.2,69.6" fill="#15846e" opacity="0.48" style="animation-delay:-0.87s"/>
<polygon class="particle" points="227.1,168.5 224.9,173.0 229.3,173.0" fill="#ffb829" opacity="0.48" style="animation-delay:-3.39s"/>
<polygon class="particle" points="222.2,61.1 219.8,66.0 224.6,66.0" fill="#f4f0ff" opacity="0.85" style="animation-delay:-3.69s"/>
<polygon class="particle" points="177.4,153.3 175.7,156.7 179.1,156.7" fill="#d04dff" opacity="0.53" style="animation-delay:-0.33s"/>
<polygon class="particle" points="186.8,160.3 185.0,164.0 188.5,164.0" fill="#d04dff" opacity="0.86" style="animation-delay:-2.41s"/>
<polygon class="particle" points="218.0,229.4 215.6,234.5 220.5,234.5" fill="#46a7ff" opacity="0.73" style="animation-delay:-3.75s"/>
<polygon class="particle" points="219.9,217.3 217.6,221.9 222.1,221.9" fill="#ffb829" opacity="0.95" style="animation-delay:-1.39s"/>
<polygon class="particle" points="212.7,160.6 210.5,165.2 215.0,165.2" fill="#8052ff" opacity="0.64" style="animation-delay:-1.43s"/>
<polygon class="particle" points="178.3,116.1 176.7,119.5 180.0,119.5" fill="#f4f0ff" opacity="0.52" style="animation-delay:-2.26s"/>
<polygon class="particle" points="226.3,255.0 225.0,257.7 227.7,257.7" fill="#8052ff" opacity="0.68" style="animation-delay:-3.75s"/>
<polygon class="particle" points="177.0,82.2 173.9,88.6 180.1,88.6" fill="#f4f0ff" opacity="0.90" style="animation-delay:-1.38s"/>
<polygon class="particle" points="192.6,39.9 191.4,42.4 193.8,42.4" fill="#f4f0ff" opacity="0.68" style="animation-delay:-0.81s"/>
<polygon class="particle" points="196.8,89.8 194.2,95.2 199.4,95.2" fill="#46a7ff" opacity="0.47" style="animation-delay:-0.84s"/>
<polygon class="particle" points="183.1,49.8 181.5,53.0 184.6,53.0" fill="#ffb829" opacity="0.65" style="animation-delay:-2.59s"/>
<polygon class="particle" points="237.9,201.0 234.8,207.3 240.9,207.3" fill="#f4f0ff" opacity="0.53" style="animation-delay:-1.37s"/>
<polygon class="particle" points="239.2,215.8 236.1,222.2 242.4,222.2" fill="#15846e" opacity="0.60" style="animation-delay:-0.44s"/>
<polygon class="particle" points="171.2,188.2 168.3,194.1 174.0,194.1" fill="#f4f0ff" opacity="0.71" style="animation-delay:-0.17s"/>
<polygon class="particle" points="235.3,239.4 232.5,245.0 238.0,245.0" fill="#f4f0ff" opacity="0.45" style="animation-delay:-1.65s"/>
<polygon class="particle" points="210.5,30.1 207.8,35.7 213.2,35.7" fill="#8052ff" opacity="0.93" style="animation-delay:-3.18s"/>
<polygon class="particle" points="190.7,162.8 188.5,167.4 192.9,167.4" fill="#ff7dcb" opacity="0.48" style="animation-delay:-1.43s"/>
<polygon class="particle" points="211.6,141.1 210.1,144.2 213.1,144.2" fill="#15846e" opacity="0.45" style="animation-delay:-1.59s"/>
<polygon class="particle" points="200.9,59.1 198.0,65.0 203.7,65.0" fill="#d04dff" opacity="0.47" style="animation-delay:-2.49s"/>
<polygon class="particle" points="188.9,55.5 186.1,61.2 191.6,61.2" fill="#ff7dcb" opacity="0.42" style="animation-delay:-0.07s"/>
<polygon class="particle" points="216.2,109.9 214.6,113.2 217.8,113.2" fill="#f4f0ff" opacity="0.55" style="animation-delay:-2.73s"/>
<polygon class="particle" points="252.4,170.5 249.1,177.3 255.7,177.3" fill="#8052ff" opacity="0.72" style="animation-delay:-2.13s"/>
<polygon class="particle" points="226.9,45.4 223.9,51.6 229.9,51.6" fill="#8052ff" opacity="0.54" style="animation-delay:-0.73s"/>
<polygon class="particle" points="198.5,208.2 196.1,213.1 200.9,213.1" fill="#ffb829" opacity="0.66" style="animation-delay:-2.37s"/>
<polygon class="particle" points="197.2,264.8 194.5,270.6 200.0,270.6" fill="#ffb829" opacity="0.65" style="animation-delay:-2.97s"/>
<polygon class="particle" points="175.5,127.9 172.6,134.0 178.5,134.0" fill="#8052ff" opacity="0.66" style="animation-delay:-2.19s"/>
<polygon class="particle" points="181.4,138.5 180.2,140.9 182.5,140.9" fill="#8052ff" opacity="0.74" style="animation-delay:-2.77s"/>
<polygon class="particle" points="193.9,188.0 190.7,194.6 197.1,194.6" fill="#f4f0ff" opacity="0.60" style="animation-delay:-1.52s"/>
<polygon class="particle" points="218.2,69.1 216.1,73.5 220.3,73.5" fill="#ffb829" opacity="0.87" style="animation-delay:-0.52s"/>
<polygon class="particle" points="226.1,128.5 224.1,132.6 228.0,132.6" fill="#d04dff" opacity="0.43" style="animation-delay:-3.79s"/>
<polygon class="particle" points="203.4,64.8 201.9,68.0 204.9,68.0" fill="#ffb829" opacity="0.56" style="animation-delay:-2.64s"/>
<polygon class="particle" points="236.6,210.1 234.3,215.0 239.0,215.0" fill="#f4f0ff" opacity="0.41" style="animation-delay:-0.69s"/>
<polygon class="particle" points="176.5,216.4 174.4,220.8 178.7,220.8" fill="#ffb829" opacity="0.51" style="animation-delay:-0.02s"/>
<polygon class="particle" points="216.4,179.4 214.4,183.5 218.4,183.5" fill="#ffb829" opacity="0.71" style="animation-delay:-0.91s"/>
<polygon class="particle" points="203.2,110.1 200.9,114.6 205.4,114.6" fill="#ffb829" opacity="0.57" style="animation-delay:-3.03s"/>
<polygon class="particle" points="246.5,161.5 243.3,168.2 249.7,168.2" fill="#ff7dcb" opacity="0.59" style="animation-delay:-0.19s"/>
<polygon class="particle" points="190.6,60.3 188.1,65.5 193.2,65.5" fill="#ffb829" opacity="0.53" style="animation-delay:-2.82s"/>
<polygon class="particle" points="225.8,57.9 223.7,62.3 228.0,62.3" fill="#46a7ff" opacity="0.75" style="animation-delay:-0.52s"/>
<polygon class="particle" points="187.1,256.7 184.6,261.9 189.6,261.9" fill="#f4f0ff" opacity="0.81" style="animation-delay:-3.42s"/>
<polygon class="particle" points="199.6,259.1 197.3,263.8 201.9,263.8" fill="#8052ff" opacity="0.58" style="animation-delay:-1.09s"/>
<polygon class="particle" points="238.8,179.1 235.9,185.1 241.6,185.1" fill="#f4f0ff" opacity="0.60" style="animation-delay:-1.96s"/>
<polygon class="particle" points="228.5,147.5 226.1,152.6 230.9,152.6" fill="#46a7ff" opacity="0.58" style="animation-delay:-2.04s"/>
<polygon class="particle" points="235.9,120.7 233.3,126.1 238.5,126.1" fill="#ff7dcb" opacity="0.59" style="animation-delay:-2.95s"/>
<polygon class="particle" points="246.3,260.5 243.2,266.9 249.4,266.9" fill="#f4f0ff" opacity="0.71" style="animation-delay:-1.03s"/>
<polygon class="particle" points="168.3,147.1 165.0,153.9 171.7,153.9" fill="#d04dff" opacity="0.61" style="animation-delay:-1.30s"/>
<polygon class="particle" points="223.2,58.4 219.9,65.2 226.5,65.2" fill="#15846e" opacity="0.69" style="animation-delay:-1.24s"/>
<polygon class="particle" points="195.8,107.4 193.5,112.0 198.0,112.0" fill="#f4f0ff" opacity="0.75" style="animation-delay:-0.47s"/>
<polygon class="particle" points="198.4,54.3 195.8,59.6 201.0,59.6" fill="#f4f0ff" opacity="0.86" style="animation-delay:-1.50s"/>
<polygon class="particle" points="172.7,202.1 169.9,207.9 175.5,207.9" fill="#8052ff" opacity="0.82" style="animation-delay:-2.76s"/>
<polygon class="particle" points="243.7,137.3 242.0,140.7 245.3,140.7" fill="#f4f0ff" opacity="0.97" style="animation-delay:-0.04s"/>
<polygon class="particle" points="211.7,113.7 209.6,118.0 213.8,118.0" fill="#8052ff" opacity="0.50" style="animation-delay:-2.89s"/>
<polygon class="particle" points="239.5,180.6 236.2,187.5 242.9,187.5" fill="#15846e" opacity="0.44" style="animation-delay:-1.28s"/>
<polygon class="particle" points="179.4,266.7 177.3,271.1 181.6,271.1" fill="#ffb829" opacity="0.53" style="animation-delay:-0.54s"/>
<polygon class="particle" points="165.1,153.2 163.1,157.4 167.2,157.4" fill="#ffb829" opacity="0.76" style="animation-delay:-3.17s"/>
<polygon class="particle" points="202.9,214.4 200.7,218.8 205.0,218.8" fill="#d04dff" opacity="0.94" style="animation-delay:-3.70s"/>
<polygon class="particle" points="239.3,206.6 238.2,209.0 240.5,209.0" fill="#ff7dcb" opacity="0.50" style="animation-delay:-2.59s"/>
<polygon class="particle" points="225.3,234.9 222.7,240.2 227.9,240.2" fill="#d04dff" opacity="0.69" style="animation-delay:-0.48s"/>
<polygon class="particle" points="202.2,141.0 199.5,146.6 204.9,146.6" fill="#8052ff" opacity="0.44" style="animation-delay:-2.12s"/>
<polygon class="particle" points="209.8,52.2 206.8,58.4 212.8,58.4" fill="#46a7ff" opacity="0.73" style="animation-delay:-1.19s"/>
<polygon class="particle" points="200.2,65.6 197.9,70.4 202.5,70.4" fill="#8052ff" opacity="0.60" style="animation-delay:-1.91s"/>
<polygon class="particle" points="246.0,40.3 244.5,43.5 247.6,43.5" fill="#f4f0ff" opacity="0.89" style="animation-delay:-1.69s"/>
<polygon class="particle" points="214.8,196.7 213.4,199.6 216.2,199.6" fill="#ff7dcb" opacity="0.90" style="animation-delay:-1.02s"/>
<polygon class="particle" points="253.8,197.6 252.7,199.9 254.9,199.9" fill="#ff7dcb" opacity="0.53" style="animation-delay:-1.25s"/>
<polygon class="particle" points="216.3,168.8 213.6,174.5 219.1,174.5" fill="#d04dff" opacity="0.45" style="animation-delay:-3.21s"/>
<polygon class="particle" points="209.4,95.5 207.3,99.8 211.5,99.8" fill="#d04dff" opacity="0.59" style="animation-delay:-1.50s"/>
<polygon class="particle" points="186.7,56.0 184.0,61.5 189.4,61.5" fill="#ff7dcb" opacity="0.49" style="animation-delay:-2.37s"/>
<polygon class="particle" points="207.7,99.5 204.8,105.4 210.6,105.4" fill="#f4f0ff" opacity="0.39" style="animation-delay:-1.40s"/>
<polygon class="particle" points="202.8,256.9 201.3,260.0 204.3,260.0" fill="#ffb829" opacity="0.56" style="animation-delay:-0.31s"/>
<polygon class="particle" points="187.7,106.7 184.5,113.2 190.8,113.2" fill="#15846e" opacity="0.39" style="animation-delay:-4.00s"/>
<polygon class="particle" points="168.8,194.2 166.8,198.4 170.9,198.4" fill="#ffb829" opacity="0.65" style="animation-delay:-2.75s"/>
<polygon class="particle" points="191.4,185.6 188.3,192.0 194.5,192.0" fill="#d04dff" opacity="0.83" style="animation-delay:-0.47s"/>
<polygon class="particle" points="202.1,59.6 200.3,63.5 204.0,63.5" fill="#46a7ff" opacity="0.57" style="animation-delay:-3.60s"/>
<polygon class="particle" points="250.0,115.9 248.8,118.5 251.3,118.5" fill="#15846e" opacity="0.59" style="animation-delay:-3.94s"/>
<polygon class="particle" points="183.5,209.9 180.3,216.5 186.8,216.5" fill="#d04dff" opacity="0.67" style="animation-delay:-0.30s"/>
<polygon class="particle" points="180.0,153.6 178.7,156.2 181.2,156.2" fill="#15846e" opacity="0.74" style="animation-delay:-2.43s"/>
<polygon class="particle" points="180.5,163.2 177.5,169.4 183.6,169.4" fill="#ffb829" opacity="0.77" style="animation-delay:-1.30s"/>
<polygon class="particle" points="191.2,101.0 189.9,103.8 192.6,103.8" fill="#15846e" opacity="0.87" style="animation-delay:-3.10s"/>
<polygon class="particle" points="181.2,58.0 179.5,61.5 182.9,61.5" fill="#ffb829" opacity="0.88" style="animation-delay:-1.56s"/>
<polygon class="particle" points="244.8,164.5 243.1,168.1 246.6,168.1" fill="#ffb829" opacity="0.81" style="animation-delay:-1.82s"/>
<polygon class="particle" points="172.3,137.7 169.7,143.1 175.0,143.1" fill="#f4f0ff" opacity="0.55" style="animation-delay:-0.57s"/>
<polygon class="particle" points="184.3,104.9 183.0,107.7 185.6,107.7" fill="#f4f0ff" opacity="0.43" style="animation-delay:-3.16s"/>
<polygon class="particle" points="208.1,147.2 205.1,153.6 211.2,153.6" fill="#f4f0ff" opacity="0.92" style="animation-delay:-2.61s"/>
<polygon class="particle" points="180.2,138.2 178.1,142.4 182.2,142.4" fill="#8052ff" opacity="0.58" style="animation-delay:-3.59s"/>
<polygon class="particle" points="218.3,146.7 216.6,150.0 219.9,150.0" fill="#f4f0ff" opacity="0.93" style="animation-delay:-3.36s"/>
<polygon class="particle" points="180.6,139.9 179.0,143.2 182.2,143.2" fill="#f4f0ff" opacity="0.59" style="animation-delay:-3.66s"/>
<polygon class="particle" points="241.5,237.4 238.8,242.9 244.1,242.9" fill="#ffb829" opacity="0.47" style="animation-delay:-0.26s"/>
<polygon class="particle" points="175.5,172.2 172.5,178.3 178.5,178.3" fill="#ffb829" opacity="0.74" style="animation-delay:-1.55s"/>
<polygon class="particle" points="246.1,74.3 243.1,80.4 249.1,80.4" fill="#ff7dcb" opacity="0.95" style="animation-delay:-3.37s"/>
<polygon class="particle" points="234.4,120.4 231.8,125.8 237.0,125.8" fill="#f4f0ff" opacity="0.98" style="animation-delay:-3.38s"/>
<polygon class="particle" points="224.4,122.7 221.4,128.9 227.4,128.9" fill="#f4f0ff" opacity="0.92" style="animation-delay:-2.61s"/>
<polygon class="particle" points="233.8,247.9 231.3,252.9 236.2,252.9" fill="#f4f0ff" opacity="0.44" style="animation-delay:-0.54s"/>
<polygon class="particle" points="212.9,47.4 210.0,53.4 215.8,53.4" fill="#d04dff" opacity="0.82" style="animation-delay:-0.36s"/>
<polygon class="particle" points="245.1,33.8 243.0,38.1 247.2,38.1" fill="#f4f0ff" opacity="0.49" style="animation-delay:-1.54s"/>
<polygon class="particle" points="211.4,148.4 208.5,154.5 214.3,154.5" fill="#ff7dcb" opacity="0.67" style="animation-delay:-3.57s"/>
<polygon class="particle" points="223.7,203.6 221.0,209.2 226.4,209.2" fill="#ff7dcb" opacity="0.63" style="animation-delay:-1.07s"/>
<polygon class="particle" points="241.5,256.9 239.9,260.1 243.0,260.1" fill="#d04dff" opacity="0.51" style="animation-delay:-3.33s"/>
<polygon class="particle" points="248.4,100.1 247.1,102.8 249.6,102.8" fill="#d04dff" opacity="0.48" style="animation-delay:-1.65s"/>
<polygon class="particle" points="242.6,254.2 240.2,259.1 245.0,259.1" fill="#f4f0ff" opacity="0.51" style="animation-delay:-2.10s"/>
<polygon class="particle" points="189.5,222.9 187.0,227.9 191.9,227.9" fill="#8052ff" opacity="0.51" style="animation-delay:-2.81s"/>
<polygon class="particle" points="186.2,67.3 183.4,73.1 189.0,73.1" fill="#46a7ff" opacity="0.91" style="animation-delay:-3.88s"/>
<polygon class="particle" points="195.4,253.1 193.8,256.4 197.0,256.4" fill="#8052ff" opacity="0.66" style="animation-delay:-1.65s"/>
<polygon class="particle" points="188.6,72.0 185.6,78.2 191.6,78.2" fill="#d04dff" opacity="0.88" style="animation-delay:-3.89s"/>
<polygon class="particle" points="195.8,238.2 193.9,242.2 197.8,242.2" fill="#f4f0ff" opacity="0.49" style="animation-delay:-0.61s"/>
<polygon class="particle" points="243.0,132.9 240.5,138.0 245.4,138.0" fill="#15846e" opacity="0.76" style="animation-delay:-2.45s"/>
<polygon class="particle" points="232.9,100.8 231.2,104.5 234.7,104.5" fill="#46a7ff" opacity="0.44" style="animation-delay:-2.89s"/>
<polygon class="particle" points="210.3,61.1 208.5,64.8 212.1,64.8" fill="#46a7ff" opacity="0.48" style="animation-delay:-0.80s"/>
<polygon class="particle" points="221.8,186.8 220.6,189.2 223.0,189.2" fill="#46a7ff" opacity="0.54" style="animation-delay:-0.60s"/>
<polygon class="particle" points="175.8,121.4 173.6,125.9 177.9,125.9" fill="#ffb829" opacity="0.78" style="animation-delay:-1.80s"/>
<polygon class="particle" points="173.1,90.5 170.4,96.0 175.7,96.0" fill="#8052ff" opacity="0.63" style="animation-delay:-0.74s"/>
<polygon class="particle" points="242.6,228.4 240.7,232.3 244.5,232.3" fill="#46a7ff" opacity="0.66" style="animation-delay:-1.22s"/>
<polygon class="particle" points="205.3,96.0 203.5,99.6 207.1,99.6" fill="#15846e" opacity="0.73" style="animation-delay:-2.10s"/>
<polygon class="particle" points="235.8,258.7 232.8,264.8 238.8,264.8" fill="#ffb829" opacity="0.49" style="animation-delay:-3.38s"/>
<polygon class="particle" points="222.4,86.3 220.3,90.6 224.4,90.6" fill="#f4f0ff" opacity="0.84" style="animation-delay:-0.01s"/>
<polygon class="particle" points="249.6,161.9 246.9,167.4 252.2,167.4" fill="#d04dff" opacity="0.41" style="animation-delay:-3.29s"/>
<polygon class="particle" points="252.3,94.0 249.6,99.6 255.0,99.6" fill="#46a7ff" opacity="0.78" style="animation-delay:-0.82s"/>
<polygon class="particle" points="188.7,159.5 187.2,162.7 190.2,162.7" fill="#8052ff" opacity="0.72" style="animation-delay:-0.01s"/>
<polygon class="particle" points="174.1,195.4 171.9,199.9 176.4,199.9" fill="#f4f0ff" opacity="0.44" style="animation-delay:-0.21s"/>
<polygon class="particle" points="215.5,128.8 213.6,132.8 217.5,132.8" fill="#8052ff" opacity="0.90" style="animation-delay:-0.57s"/>
<polygon class="particle" points="245.6,204.3 242.5,210.6 248.7,210.6" fill="#f4f0ff" opacity="0.44" style="animation-delay:-3.96s"/>
<polygon class="particle" points="186.7,126.7 184.2,131.8 189.2,131.8" fill="#d04dff" opacity="0.50" style="animation-delay:-1.05s"/>
<polygon class="particle" points="165.8,191.7 163.8,195.9 167.9,195.9" fill="#46a7ff" opacity="0.80" style="animation-delay:-0.92s"/>
<polygon class="particle" points="188.6,187.3 187.3,189.9 189.8,189.9" fill="#15846e" opacity="0.98" style="animation-delay:-1.80s"/>
<polygon class="particle" points="189.6,248.4 187.9,252.0 191.3,252.0" fill="#ffb829" opacity="0.85" style="animation-delay:-2.87s"/>
<polygon class="particle" points="179.8,203.7 176.6,210.2 183.0,210.2" fill="#ff7dcb" opacity="0.63" style="animation-delay:-0.99s"/>
<polygon class="particle" points="176.4,130.8 174.3,135.2 178.6,135.2" fill="#46a7ff" opacity="0.66" style="animation-delay:-1.52s"/>
<polygon class="particle" points="204.4,181.9 201.5,187.9 207.3,187.9" fill="#ffb829" opacity="0.40" style="animation-delay:-0.40s"/>
<polygon class="particle" points="231.2,114.3 229.7,117.3 232.6,117.3" fill="#f4f0ff" opacity="0.43" style="animation-delay:-3.66s"/>
<polygon class="particle" points="201.4,150.2 199.0,155.0 203.7,155.0" fill="#ff7dcb" opacity="0.83" style="animation-delay:-0.84s"/>
<polygon class="particle" points="245.5,56.2 242.5,62.4 248.5,62.4" fill="#ff7dcb" opacity="0.74" style="animation-delay:-1.64s"/>
<polygon class="particle" points="201.2,198.7 198.2,204.8 204.1,204.8" fill="#46a7ff" opacity="0.39" style="animation-delay:-1.28s"/>
<polygon class="particle" points="177.8,94.8 175.7,99.2 180.0,99.2" fill="#ff7dcb" opacity="0.52" style="animation-delay:-1.52s"/>
<polygon class="particle" points="223.0,163.3 221.1,167.3 224.9,167.3" fill="#8052ff" opacity="0.96" style="animation-delay:-2.90s"/>
<polygon class="particle" points="244.0,185.2 242.4,188.5 245.6,188.5" fill="#ffb829" opacity="0.65" style="animation-delay:-0.17s"/>
<polygon class="particle" points="217.7,137.0 216.2,140.0 219.1,140.0" fill="#d04dff" opacity="0.63" style="animation-delay:-3.00s"/>
<polygon class="particle" points="237.0,243.3 235.8,245.7 238.2,245.7" fill="#ffb829" opacity="0.45" style="animation-delay:-0.80s"/>
<polygon class="particle" points="225.7,186.8 223.7,190.7 227.6,190.7" fill="#d04dff" opacity="0.48" style="animation-delay:-3.60s"/>
<polygon class="particle" points="194.9,189.6 193.5,192.3 196.2,192.3" fill="#46a7ff" opacity="0.71" style="animation-delay:-1.47s"/>
<polygon class="particle" points="219.7,100.7 217.7,104.8 221.7,104.8" fill="#ffb829" opacity="0.73" style="animation-delay:-0.04s"/>
<polygon class="particle" points="213.8,118.4 210.8,124.5 216.7,124.5" fill="#d04dff" opacity="0.50" style="animation-delay:-2.18s"/>
<polygon class="particle" points="181.8,115.2 179.0,121.0 184.6,121.0" fill="#f4f0ff" opacity="0.80" style="animation-delay:-1.53s"/>
<polygon class="particle" points="226.0,136.4 224.3,139.9 227.8,139.9" fill="#f4f0ff" opacity="0.85" style="animation-delay:-0.25s"/>
<polygon class="particle" points="197.5,97.3 195.8,100.9 199.3,100.9" fill="#15846e" opacity="0.78" style="animation-delay:-0.16s"/>
<polygon class="particle" points="253.7,107.0 251.4,111.8 256.1,111.8" fill="#8052ff" opacity="0.86" style="animation-delay:-3.19s"/>
<polygon class="particle" points="203.0,36.1 200.0,42.1 205.9,42.1" fill="#8052ff" opacity="0.56" style="animation-delay:-1.60s"/>
<polygon class="particle" points="186.2,251.9 184.9,254.8 187.6,254.8" fill="#f4f0ff" opacity="0.92" style="animation-delay:-0.20s"/>
<polygon class="particle" points="227.2,61.0 225.3,65.0 229.2,65.0" fill="#d04dff" opacity="0.56" style="animation-delay:-0.92s"/>
<polygon class="particle" points="190.2,115.3 187.1,121.6 193.3,121.6" fill="#d04dff" opacity="0.64" style="animation-delay:-1.09s"/>
<polygon class="particle" points="194.4,227.8 192.9,230.9 195.9,230.9" fill="#15846e" opacity="0.93" style="animation-delay:-0.27s"/>
<polygon class="particle" points="232.3,34.4 231.0,37.2 233.6,37.2" fill="#8052ff" opacity="0.47" style="animation-delay:-3.73s"/>
<polygon class="particle" points="187.3,261.8 184.8,266.8 189.7,266.8" fill="#ffb829" opacity="0.40" style="animation-delay:-3.89s"/>
<polygon class="particle" points="202.4,97.3 200.3,101.6 204.5,101.6" fill="#f4f0ff" opacity="0.42" style="animation-delay:-1.86s"/>
<polygon class="particle" points="203.0,172.6 200.4,178.0 205.6,178.0" fill="#f4f0ff" opacity="0.86" style="animation-delay:-0.20s"/>
<polygon class="particle" points="247.5,71.9 244.8,77.3 250.1,77.3" fill="#46a7ff" opacity="0.77" style="animation-delay:-3.45s"/>
<polygon class="particle" points="184.0,79.8 181.7,84.6 186.3,84.6" fill="#8052ff" opacity="0.43" style="animation-delay:-3.59s"/>
<polygon class="particle" points="238.7,194.4 236.8,198.4 240.7,198.4" fill="#f4f0ff" opacity="0.47" style="animation-delay:-1.09s"/>
<polygon class="particle" points="190.6,49.5 189.4,51.9 191.8,51.9" fill="#46a7ff" opacity="0.39" style="animation-delay:-3.99s"/>
<polygon class="particle" points="169.0,79.9 167.2,83.7 170.8,83.7" fill="#ffb829" opacity="0.97" style="animation-delay:-2.98s"/>
<polygon class="particle" points="208.0,257.5 205.5,262.8 210.6,262.8" fill="#15846e" opacity="0.41" style="animation-delay:-0.23s"/>
<polygon class="particle" points="237.7,206.3 236.2,209.4 239.2,209.4" fill="#d04dff" opacity="0.75" style="animation-delay:-3.81s"/>
<polygon class="particle" points="253.0,128.9 251.8,131.3 254.2,131.3" fill="#8052ff" opacity="0.78" style="animation-delay:-1.53s"/>
<polygon class="particle" points="244.3,70.7 242.9,73.5 245.6,73.5" fill="#ff7dcb" opacity="0.79" style="animation-delay:-3.23s"/>
<polygon class="particle" points="185.2,205.5 182.0,212.2 188.5,212.2" fill="#ffb829" opacity="0.88" style="animation-delay:-1.16s"/>
<polygon class="particle" points="176.1,140.5 174.7,143.4 177.5,143.4" fill="#d04dff" opacity="0.70" style="animation-delay:-3.19s"/>
<polygon class="particle" points="179.8,43.9 177.7,48.4 182.0,48.4" fill="#8052ff" opacity="0.40" style="animation-delay:-3.11s"/>
<polygon class="particle" points="180.4,61.1 177.1,67.9 183.7,67.9" fill="#8052ff" opacity="0.47" style="animation-delay:-3.22s"/>
<polygon class="particle" points="178.1,229.8 176.6,232.7 179.5,232.7" fill="#d04dff" opacity="0.46" style="animation-delay:-1.19s"/>
<polygon class="particle" points="228.3,135.9 227.0,138.5 229.6,138.5" fill="#f4f0ff" opacity="0.71" style="animation-delay:-2.88s"/>
<polygon class="particle" points="196.1,164.2 194.2,168.2 198.1,168.2" fill="#ffb829" opacity="0.97" style="animation-delay:-3.65s"/>
<polygon class="particle" points="210.6,205.0 209.4,207.3 211.7,207.3" fill="#ffb829" opacity="0.41" style="animation-delay:-1.64s"/>
<polygon class="particle" points="193.9,181.1 191.9,185.2 195.9,185.2" fill="#f4f0ff" opacity="0.87" style="animation-delay:-3.40s"/>
<polygon class="particle" points="216.1,267.9 214.9,270.4 217.4,270.4" fill="#8052ff" opacity="0.72" style="animation-delay:-3.29s"/>
<polygon class="particle" points="242.3,85.3 239.8,90.4 244.8,90.4" fill="#8052ff" opacity="0.44" style="animation-delay:-2.46s"/>
<polygon class="particle" points="211.6,172.3 210.0,175.7 213.3,175.7" fill="#f4f0ff" opacity="0.67" style="animation-delay:-0.28s"/>
<polygon class="particle" points="243.4,215.3 240.7,220.9 246.1,220.9" fill="#46a7ff" opacity="0.56" style="animation-delay:-1.47s"/>
<polygon class="particle" points="221.0,71.2 218.1,77.1 223.8,77.1" fill="#d04dff" opacity="0.81" style="animation-delay:-0.65s"/>
<polygon class="particle" points="249.3,263.9 248.1,266.4 250.5,266.4" fill="#d04dff" opacity="0.39" style="animation-delay:-2.17s"/>
<polygon class="particle" points="231.9,141.0 229.5,145.9 234.3,145.9" fill="#8052ff" opacity="0.87" style="animation-delay:-3.57s"/>
<polygon class="particle" points="228.2,136.4 225.2,142.5 231.1,142.5" fill="#8052ff" opacity="0.65" style="animation-delay:-3.80s"/>
<polygon class="particle" points="177.9,98.7 175.4,103.8 180.4,103.8" fill="#8052ff" opacity="0.78" style="animation-delay:-2.24s"/>
<polygon class="particle" points="181.6,116.7 178.4,123.3 184.8,123.3" fill="#ffb829" opacity="0.72" style="animation-delay:-2.82s"/>
<polygon class="particle" points="210.2,121.6 207.7,126.8 212.7,126.8" fill="#f4f0ff" opacity="0.90" style="animation-delay:-0.46s"/>
<polygon class="particle" points="213.4,217.9 211.8,221.2 214.9,221.2" fill="#46a7ff" opacity="0.85" style="animation-delay:-3.32s"/>
<polygon class="particle" points="182.0,176.9 180.2,180.6 183.7,180.6" fill="#46a7ff" opacity="0.53" style="animation-delay:-1.23s"/>
<polygon class="particle" points="229.7,253.6 227.6,257.8 231.8,257.8" fill="#8052ff" opacity="0.85" style="animation-delay:-0.86s"/>
<polygon class="particle" points="205.5,125.4 202.6,131.3 208.3,131.3" fill="#ffb829" opacity="0.71" style="animation-delay:-2.48s"/>
<polygon class="particle" points="220.2,246.3 218.9,249.2 221.6,249.2" fill="#46a7ff" opacity="0.52" style="animation-delay:-3.83s"/>
<polygon class="particle" points="204.1,97.8 201.6,102.9 206.6,102.9" fill="#d04dff" opacity="0.67" style="animation-delay:-2.97s"/>
<polygon class="particle" points="215.8,144.8 214.0,148.4 217.5,148.4" fill="#ffb829" opacity="0.55" style="animation-delay:-0.81s"/>
<polygon class="particle" points="187.5,176.8 185.6,180.7 189.4,180.7" fill="#ffb829" opacity="0.87" style="animation-delay:-2.55s"/>
<polygon class="particle" points="242.1,60.6 239.4,66.2 244.7,66.2" fill="#46a7ff" opacity="0.62" style="animation-delay:-3.60s"/>
<polygon class="particle" points="210.5,185.2 209.1,188.0 211.9,188.0" fill="#ff7dcb" opacity="0.95" style="animation-delay:-0.83s"/>
<polygon class="particle" points="226.4,190.6 224.0,195.6 228.9,195.6" fill="#f4f0ff" opacity="0.81" style="animation-delay:-3.34s"/>
<polygon class="particle" points="185.7,150.8 183.4,155.5 188.0,155.5" fill="#f4f0ff" opacity="0.47" style="animation-delay:-0.64s"/>
<polygon class="particle" points="247.3,227.5 246.2,229.8 248.5,229.8" fill="#d04dff" opacity="0.47" style="animation-delay:-1.17s"/>
<polygon class="particle" points="225.3,199.5 222.9,204.6 227.8,204.6" fill="#8052ff" opacity="0.98" style="animation-delay:-1.24s"/>
<polygon class="particle" points="178.1,260.8 175.7,265.7 180.5,265.7" fill="#d04dff" opacity="0.70" style="animation-delay:-2.37s"/>
<polygon class="particle" points="212.8,224.0 210.2,229.3 215.4,229.3" fill="#ffb829" opacity="0.45" style="animation-delay:-2.50s"/>
<polygon class="particle" points="167.7,198.3 165.6,202.6 169.8,202.6" fill="#f4f0ff" opacity="0.39" style="animation-delay:-1.39s"/>
<polygon class="particle" points="210.6,127.4 208.0,132.8 213.2,132.8" fill="#8052ff" opacity="0.87" style="animation-delay:-3.21s"/>
<polygon class="particle" points="242.0,87.7 239.2,93.6 244.8,93.6" fill="#f4f0ff" opacity="0.94" style="animation-delay:-2.10s"/>
<polygon class="particle" points="186.5,135.8 185.3,138.3 187.7,138.3" fill="#ffb829" opacity="0.52" style="animation-delay:-2.10s"/>
<polygon class="particle" points="243.0,105.0 241.6,108.0 244.5,108.0" fill="#ffb829" opacity="0.64" style="animation-delay:-0.71s"/>
<polygon class="particle" points="222.4,202.2 219.6,207.9 225.2,207.9" fill="#ffb829" opacity="0.82" style="animation-delay:-0.70s"/>
<polygon class="particle" points="199.3,222.5 196.5,228.1 202.0,228.1" fill="#8052ff" opacity="0.53" style="animation-delay:-2.86s"/>
<polygon class="particle" points="200.3,68.3 199.0,71.0 201.6,71.0" fill="#f4f0ff" opacity="0.55" style="animation-delay:-3.47s"/>
<polygon class="particle" points="210.2,38.9 207.5,44.5 212.9,44.5" fill="#ffb829" opacity="0.57" style="animation-delay:-2.39s"/>
<polygon class="particle" points="215.1,43.8 211.9,50.4 218.3,50.4" fill="#8052ff" opacity="0.83" style="animation-delay:-2.13s"/>
<polygon class="particle" points="247.1,196.7 245.1,200.8 249.1,200.8" fill="#8052ff" opacity="0.58" style="animation-delay:-0.34s"/>
<polygon class="particle" points="214.6,244.3 211.4,250.9 217.8,250.9" fill="#15846e" opacity="0.54" style="animation-delay:-3.86s"/>
<polygon class="particle" points="229.7,265.4 228.0,269.0 231.4,269.0" fill="#ffb829" opacity="0.70" style="animation-delay:-2.73s"/>
<polygon class="particle" points="224.0,108.0 222.6,110.9 225.5,110.9" fill="#ffb829" opacity="0.60" style="animation-delay:-0.94s"/>
<polygon class="particle" points="191.5,89.5 188.9,94.8 194.1,94.8" fill="#ffb829" opacity="0.57" style="animation-delay:-3.67s"/>
<polygon class="particle" points="188.5,153.9 185.9,159.4 191.2,159.4" fill="#15846e" opacity="0.51" style="animation-delay:-3.80s"/>
<polygon class="particle" points="174.3,232.8 171.1,239.4 177.5,239.4" fill="#f4f0ff" opacity="0.67" style="animation-delay:-2.43s"/>
<polygon class="particle" points="224.8,200.3 223.6,202.8 226.1,202.8" fill="#d04dff" opacity="0.61" style="animation-delay:-0.20s"/>
<polygon class="particle" points="179.8,110.9 176.5,117.6 183.1,117.6" fill="#ffb829" opacity="0.81" style="animation-delay:-0.86s"/>
<polygon class="particle" points="246.6,214.7 244.3,219.5 248.9,219.5" fill="#8052ff" opacity="0.73" style="animation-delay:-3.88s"/>
<polygon class="particle" points="236.3,60.5 233.6,66.0 238.9,66.0" fill="#f4f0ff" opacity="0.61" style="animation-delay:-3.51s"/>
<polygon class="particle" points="200.6,206.4 199.5,208.8 201.7,208.8" fill="#ffb829" opacity="0.72" style="animation-delay:-2.53s"/>
<polygon class="particle" points="226.2,91.7 223.8,96.6 228.6,96.6" fill="#f4f0ff" opacity="0.97" style="animation-delay:-1.54s"/>
<polygon class="particle" points="245.4,139.6 243.8,142.8 247.0,142.8" fill="#f4f0ff" opacity="0.40" style="animation-delay:-2.37s"/>
<polygon class="particle" points="211.3,104.4 209.6,108.0 213.1,108.0" fill="#d04dff" opacity="0.53" style="animation-delay:-1.42s"/>
<polygon class="particle" points="216.1,241.3 214.2,245.3 218.1,245.3" fill="#46a7ff" opacity="0.49" style="animation-delay:-1.96s"/>
<polygon class="particle" points="180.2,258.8 178.4,262.6 182.1,262.6" fill="#f4f0ff" opacity="0.84" style="animation-delay:-2.88s"/>
<polygon class="particle" points="215.6,212.4 213.6,216.6 217.6,216.6" fill="#ffb829" opacity="0.44" style="animation-delay:-0.98s"/>
<polygon class="particle" points="195.6,49.0 192.7,55.0 198.5,55.0" fill="#8052ff" opacity="0.77" style="animation-delay:-0.70s"/>
<polygon class="particle" points="172.3,115.5 170.9,118.4 173.7,118.4" fill="#46a7ff" opacity="0.91" style="animation-delay:-0.17s"/>
<polygon class="particle" points="231.2,85.2 228.2,91.3 234.1,91.3" fill="#8052ff" opacity="0.97" style="animation-delay:-2.63s"/>
<polygon class="particle" points="217.8,81.6 215.6,86.0 219.9,86.0" fill="#8052ff" opacity="0.65" style="animation-delay:-1.61s"/>
<polygon class="particle" points="187.3,262.0 185.8,265.0 188.7,265.0" fill="#ff7dcb" opacity="0.84" style="animation-delay:-2.40s"/>
<polygon class="particle" points="185.6,138.6 183.3,143.3 187.9,143.3" fill="#f4f0ff" opacity="0.53" style="animation-delay:-2.91s"/>
<polygon class="particle" points="215.4,188.8 213.1,193.4 217.6,193.4" fill="#8052ff" opacity="0.57" style="animation-delay:-2.93s"/>
<polygon class="particle" points="235.9,152.7 234.1,156.5 237.7,156.5" fill="#ffb829" opacity="0.92" style="animation-delay:-3.67s"/>
<polygon class="particle" points="200.7,225.0 197.3,231.9 204.0,231.9" fill="#8052ff" opacity="0.47" style="animation-delay:-2.37s"/>
<polygon class="particle" points="198.8,132.1 197.3,135.0 200.2,135.0" fill="#46a7ff" opacity="0.79" style="animation-delay:-1.66s"/>
<polygon class="particle" points="252.5,161.3 250.1,166.4 255.0,166.4" fill="#ffb829" opacity="0.69" style="animation-delay:-2.70s"/>
<polygon class="particle" points="191.1,186.3 189.4,189.7 192.8,189.7" fill="#d04dff" opacity="0.80" style="animation-delay:-1.56s"/>
<polygon class="particle" points="199.2,38.0 196.6,43.4 201.9,43.4" fill="#d04dff" opacity="0.79" style="animation-delay:-1.47s"/>
<polygon class="particle" points="188.1,46.6 185.5,52.0 190.7,52.0" fill="#d04dff" opacity="0.91" style="animation-delay:-1.09s"/>
<polygon class="particle" points="183.6,68.8 181.0,74.2 186.2,74.2" fill="#f4f0ff" opacity="0.74" style="animation-delay:-1.42s"/>
<polygon class="particle" points="220.7,77.3 218.5,81.9 222.9,81.9" fill="#46a7ff" opacity="0.95" style="animation-delay:-2.34s"/>
<polygon class="particle" points="203.2,257.9 201.0,262.4 205.4,262.4" fill="#f4f0ff" opacity="0.68" style="animation-delay:-0.59s"/>
<polygon class="particle" points="183.6,48.7 181.7,52.6 185.4,52.6" fill="#46a7ff" opacity="0.75" style="animation-delay:-3.24s"/>
<polygon class="particle" points="220.5,242.6 219.2,245.3 221.8,245.3" fill="#46a7ff" opacity="0.58" style="animation-delay:-1.71s"/>
<polygon class="particle" points="167.4,190.7 165.3,194.9 169.4,194.9" fill="#ffb829" opacity="0.39" style="animation-delay:-3.12s"/>
<polygon class="particle" points="171.7,200.3 170.4,203.0 173.1,203.0" fill="#ffb829" opacity="0.98" style="animation-delay:-2.71s"/>
<polygon class="particle" points="179.9,157.0 177.7,161.5 182.1,161.5" fill="#46a7ff" opacity="0.43" style="animation-delay:-1.65s"/>
<polygon class="particle" points="252.3,99.8 250.0,104.6 254.6,104.6" fill="#8052ff" opacity="0.94" style="animation-delay:-1.99s"/>
<polygon class="particle" points="226.0,54.5 224.8,57.0 227.2,57.0" fill="#ff7dcb" opacity="0.92" style="animation-delay:-1.64s"/>
<polygon class="particle" points="247.2,222.5 244.1,228.9 250.4,228.9" fill="#ff7dcb" opacity="0.94" style="animation-delay:-2.27s"/>
<polygon class="particle" points="247.4,108.9 244.0,115.8 250.7,115.8" fill="#ffb829" opacity="0.93" style="animation-delay:-2.41s"/>
<polygon class="particle" points="246.6,235.0 244.7,238.9 248.5,238.9" fill="#d04dff" opacity="0.80" style="animation-delay:-3.57s"/>
<polygon class="particle" points="217.9,236.4 215.3,241.7 220.4,241.7" fill="#d04dff" opacity="0.63" style="animation-delay:-2.98s"/>
<polygon class="particle" points="186.9,221.5 185.7,224.0 188.0,224.0" fill="#8052ff" opacity="0.62" style="animation-delay:-0.83s"/>
<polygon class="particle" points="216.8,58.3 214.9,62.3 218.8,62.3" fill="#8052ff" opacity="0.43" style="animation-delay:-3.04s"/>
<polygon class="particle" points="225.9,225.5 223.1,231.4 228.8,231.4" fill="#f4f0ff" opacity="0.39" style="animation-delay:-1.81s"/>
<polygon class="particle" points="207.9,130.3 206.1,133.9 209.6,133.9" fill="#d04dff" opacity="0.93" style="animation-delay:-3.78s"/>
<polygon class="particle" points="213.3,193.8 211.2,198.2 215.5,198.2" fill="#15846e" opacity="0.82" style="animation-delay:-1.32s"/>
<polygon class="particle" points="254.8,166.0 253.2,169.3 256.4,169.3" fill="#d04dff" opacity="0.58" style="animation-delay:-0.47s"/>
<polygon class="particle" points="233.3,252.0 230.6,257.6 236.0,257.6" fill="#f4f0ff" opacity="0.43" style="animation-delay:-2.87s"/>
<polygon class="particle" points="193.4,195.5 190.7,201.1 196.1,201.1" fill="#f4f0ff" opacity="0.88" style="animation-delay:-2.62s"/>
<polygon class="particle" points="219.3,174.5 216.1,181.1 222.6,181.1" fill="#ffb829" opacity="0.84" style="animation-delay:-3.35s"/>
<polygon class="particle" points="243.1,204.5 240.4,210.0 245.8,210.0" fill="#8052ff" opacity="0.49" style="animation-delay:-0.81s"/>
<polygon class="particle" points="209.7,230.9 207.4,235.6 212.0,235.6" fill="#d04dff" opacity="0.74" style="animation-delay:-3.33s"/>
<polygon class="particle" points="250.5,147.9 249.0,150.9 251.9,150.9" fill="#15846e" opacity="0.94" style="animation-delay:-0.02s"/>
<polygon class="particle" points="199.1,121.7 196.8,126.5 201.4,126.5" fill="#ffb829" opacity="0.64" style="animation-delay:-0.92s"/>
<polygon class="particle" points="191.7,105.2 188.4,112.0 195.0,112.0" fill="#d04dff" opacity="0.48" style="animation-delay:-1.75s"/>
<polygon class="particle" points="200.5,34.6 198.9,37.7 202.0,37.7" fill="#15846e" opacity="0.46" style="animation-delay:-3.02s"/>
<polygon class="particle" points="236.6,183.6 235.1,186.7 238.1,186.7" fill="#d04dff" opacity="0.45" style="animation-delay:-3.39s"/>
<polygon class="particle" points="182.0,182.8 180.1,186.7 183.9,186.7" fill="#ffb829" opacity="0.61" style="animation-delay:-2.72s"/>
<polygon class="particle" points="198.0,187.6 195.9,191.8 200.0,191.8" fill="#8052ff" opacity="0.45" style="animation-delay:-1.69s"/>
<polygon class="particle" points="202.2,58.2 199.4,64.0 205.0,64.0" fill="#15846e" opacity="0.89" style="animation-delay:-0.55s"/>
<polygon class="particle" points="190.2,256.7 188.8,259.6 191.6,259.6" fill="#ffb829" opacity="0.43" style="animation-delay:-3.31s"/>
<polygon class="particle" points="175.8,87.3 174.4,90.2 177.2,90.2" fill="#f4f0ff" opacity="0.49" style="animation-delay:-2.80s"/>
<polygon class="particle" points="188.7,121.9 185.4,128.8 192.1,128.8" fill="#8052ff" opacity="0.89" style="animation-delay:-0.30s"/>
<polygon class="particle" points="204.0,163.8 202.4,167.1 205.6,167.1" fill="#ffb829" opacity="0.97" style="animation-delay:-1.97s"/>
<polygon class="particle" points="237.0,237.4 235.0,241.5 239.0,241.5" fill="#46a7ff" opacity="0.81" style="animation-delay:-2.99s"/>
<polygon class="particle" points="183.6,205.4 180.8,211.3 186.5,211.3" fill="#15846e" opacity="0.62" style="animation-delay:-2.17s"/>
<polygon class="particle" points="207.6,97.7 206.4,100.3 208.9,100.3" fill="#f4f0ff" opacity="0.45" style="animation-delay:-3.20s"/>
<polygon class="particle" points="220.0,108.4 218.0,112.6 222.1,112.6" fill="#d04dff" opacity="0.91" style="animation-delay:-3.69s"/>
<polygon class="particle" points="237.1,179.8 235.0,184.0 239.1,184.0" fill="#8052ff" opacity="0.66" style="animation-delay:-2.75s"/>
<polygon class="particle" points="252.2,193.6 249.9,198.3 254.4,198.3" fill="#8052ff" opacity="0.76" style="animation-delay:-0.16s"/>
<polygon class="particle" points="197.4,153.7 194.8,159.1 200.0,159.1" fill="#ffb829" opacity="0.66" style="animation-delay:-3.16s"/>
<polygon class="particle" points="194.5,168.3 191.3,174.9 197.7,174.9" fill="#8052ff" opacity="0.49" style="animation-delay:-2.70s"/>
<polygon class="particle" points="206.7,208.1 204.1,213.4 209.2,213.4" fill="#46a7ff" opacity="0.47" style="animation-delay:-3.20s"/>
<polygon class="particle" points="181.0,204.5 179.3,208.0 182.7,208.0" fill="#ffb829" opacity="0.67" style="animation-delay:-2.64s"/>
<polygon class="particle" points="211.1,147.3 209.5,150.7 212.8,150.7" fill="#f4f0ff" opacity="0.49" style="animation-delay:-0.21s"/>
<polygon class="particle" points="213.3,48.4 211.4,52.2 215.1,52.2" fill="#8052ff" opacity="0.51" style="animation-delay:-3.10s"/>
<polygon class="particle" points="177.8,211.5 175.2,216.9 180.4,216.9" fill="#ffb829" opacity="0.53" style="animation-delay:-0.13s"/>
<polygon class="particle" points="232.1,43.6 229.1,49.7 235.0,49.7" fill="#ffb829" opacity="0.74" style="animation-delay:-3.14s"/>
<polygon class="particle" points="185.8,193.8 182.8,200.1 188.9,200.1" fill="#f4f0ff" opacity="0.66" style="animation-delay:-0.91s"/>
<polygon class="particle" points="187.7,234.1 184.8,240.1 190.6,240.1" fill="#d04dff" opacity="0.54" style="animation-delay:-1.05s"/>
<polygon class="particle" points="243.0,174.6 239.7,181.4 246.3,181.4" fill="#8052ff" opacity="0.45" style="animation-delay:-0.66s"/>
<polygon class="particle" points="178.6,59.1 176.6,63.1 180.5,63.1" fill="#f4f0ff" opacity="0.92" style="animation-delay:-2.27s"/>
<polygon class="particle" points="237.2,37.8 235.7,41.0 238.7,41.0" fill="#f4f0ff" opacity="0.76" style="animation-delay:-1.71s"/>
<polygon class="particle" points="180.1,175.2 178.3,178.8 181.8,178.8" fill="#d04dff" opacity="0.61" style="animation-delay:-0.54s"/>
<polygon class="particle" points="232.8,56.8 231.3,59.8 234.3,59.8" fill="#ffb829" opacity="0.46" style="animation-delay:-0.53s"/>
<polygon class="particle" points="187.7,64.4 184.6,70.8 190.7,70.8" fill="#8052ff" opacity="0.77" style="animation-delay:-0.57s"/>
<polygon class="particle" points="244.4,30.4 241.1,37.2 247.7,37.2" fill="#ff7dcb" opacity="0.39" style="animation-delay:-2.68s"/>
<polygon class="particle" points="192.8,241.1 191.7,243.4 193.9,243.4" fill="#f4f0ff" opacity="0.79" style="animation-delay:-2.20s"/>
<polygon class="particle" points="184.8,136.3 181.4,143.2 188.1,143.2" fill="#ff7dcb" opacity="0.50" style="animation-delay:-3.99s"/>
<polygon class="particle" points="184.8,261.7 182.9,265.7 186.7,265.7" fill="#15846e" opacity="0.70" style="animation-delay:-0.88s"/>
<polygon class="particle" points="211.4,201.0 210.3,203.4 212.6,203.4" fill="#f4f0ff" opacity="0.44" style="animation-delay:-2.93s"/>
<polygon class="particle" points="186.9,45.9 185.7,48.3 188.0,48.3" fill="#8052ff" opacity="0.92" style="animation-delay:-2.50s"/>
<polygon class="particle" points="248.9,236.6 246.4,241.9 251.4,241.9" fill="#f4f0ff" opacity="0.87" style="animation-delay:-1.47s"/>
<polygon class="particle" points="201.2,136.9 199.4,140.6 203.0,140.6" fill="#ffb829" opacity="0.46" style="animation-delay:-2.59s"/>
<polygon class="particle" points="235.3,112.6 233.2,117.1 237.5,117.1" fill="#f4f0ff" opacity="0.65" style="animation-delay:-0.37s"/>
<polygon class="particle" points="233.3,28.4 230.3,34.5 236.3,34.5" fill="#8052ff" opacity="0.70" style="animation-delay:-2.16s"/>
<polygon class="particle" points="246.7,78.1 244.3,83.1 249.2,83.1" fill="#8052ff" opacity="0.58" style="animation-delay:-0.24s"/>
<polygon class="particle" points="175.4,236.2 172.2,242.8 178.5,242.8" fill="#ffb829" opacity="0.78" style="animation-delay:-2.31s"/>
<polygon class="particle" points="180.0,90.7 178.4,94.2 181.7,94.2" fill="#d04dff" opacity="0.46" style="animation-delay:-3.82s"/>
<polygon class="particle" points="228.5,167.7 226.6,171.6 230.4,171.6" fill="#8052ff" opacity="0.84" style="animation-delay:-2.99s"/>
<polygon class="particle" points="206.6,39.7 203.3,46.5 209.9,46.5" fill="#ff7dcb" opacity="0.65" style="animation-delay:-0.24s"/>
<polygon class="particle" points="243.6,102.6 241.0,107.9 246.2,107.9" fill="#15846e" opacity="0.80" style="animation-delay:-0.56s"/>
<polygon class="particle" points="241.8,218.4 239.6,222.8 243.9,222.8" fill="#15846e" opacity="0.79" style="animation-delay:-1.27s"/>
<polygon class="particle" points="187.6,158.0 185.4,162.5 189.7,162.5" fill="#f4f0ff" opacity="0.65" style="animation-delay:-0.22s"/>
<polygon class="particle" points="247.6,231.0 244.6,237.3 250.7,237.3" fill="#f4f0ff" opacity="0.72" style="animation-delay:-0.11s"/>
<polygon class="particle" points="196.1,62.4 193.6,67.7 198.6,67.7" fill="#ffb829" opacity="0.67" style="animation-delay:-0.28s"/>
<polygon class="particle" points="236.6,205.2 233.9,210.8 239.3,210.8" fill="#46a7ff" opacity="0.46" style="animation-delay:-0.03s"/>
<polygon class="particle" points="220.3,231.8 219.1,234.2 221.4,234.2" fill="#15846e" opacity="0.71" style="animation-delay:-2.65s"/>
<polygon class="particle" points="244.4,249.0 242.4,253.1 246.4,253.1" fill="#46a7ff" opacity="0.60" style="animation-delay:-3.74s"/>
<polygon class="particle" points="182.9,34.2 181.3,37.5 184.5,37.5" fill="#46a7ff" opacity="0.54" style="animation-delay:-1.72s"/>
<polygon class="particle" points="235.6,112.7 234.3,115.3 236.9,115.3" fill="#8052ff" opacity="0.54" style="animation-delay:-2.56s"/>
<polygon class="particle" points="206.0,48.2 203.6,53.3 208.5,53.3" fill="#f4f0ff" opacity="0.59" style="animation-delay:-2.36s"/>
<polygon class="particle" points="242.4,203.2 239.9,208.4 244.9,208.4" fill="#f4f0ff" opacity="0.75" style="animation-delay:-3.50s"/>
<polygon class="particle" points="202.7,86.9 201.3,89.9 204.2,89.9" fill="#d04dff" opacity="0.89" style="animation-delay:-2.07s"/>
<polygon class="particle" points="196.6,152.8 193.9,158.4 199.3,158.4" fill="#8052ff" opacity="0.73" style="animation-delay:-1.74s"/>
<polygon class="particle" points="175.5,232.8 173.1,237.8 178.0,237.8" fill="#ffb829" opacity="0.85" style="animation-delay:-0.57s"/>
<polygon class="particle" points="254.6,133.5 252.5,137.8 256.6,137.8" fill="#ffb829" opacity="0.93" style="animation-delay:-2.62s"/>
<polygon class="particle" points="207.0,197.7 205.8,200.2 208.2,200.2" fill="#8052ff" opacity="0.60" style="animation-delay:-0.83s"/>
<polygon class="particle" points="219.3,196.1 215.9,203.0 222.6,203.0" fill="#8052ff" opacity="0.45" style="animation-delay:-1.44s"/>
<polygon class="particle" points="226.7,240.7 224.1,246.0 229.3,246.0" fill="#8052ff" opacity="0.55" style="animation-delay:-3.82s"/>
<polygon class="particle" points="203.6,152.6 201.9,156.1 205.3,156.1" fill="#46a7ff" opacity="0.93" style="animation-delay:-3.22s"/>
<polygon class="particle" points="188.3,191.2 186.6,194.8 190.1,194.8" fill="#d04dff" opacity="0.84" style="animation-delay:-1.57s"/>
<polygon class="particle" points="169.2,61.1 166.4,66.9 172.0,66.9" fill="#8052ff" opacity="0.44" style="animation-delay:-2.40s"/>
<polygon class="particle" points="186.8,197.3 184.6,201.9 189.1,201.9" fill="#ff7dcb" opacity="0.61" style="animation-delay:-3.84s"/>
<polygon class="particle" points="177.3,232.6 174.1,239.2 180.5,239.2" fill="#d04dff" opacity="0.44" style="animation-delay:-2.60s"/>
<polygon class="particle" points="252.0,180.2 250.0,184.3 254.0,184.3" fill="#8052ff" opacity="0.86" style="animation-delay:-0.33s"/>
<polygon class="particle" points="240.8,47.3 237.5,54.0 244.1,54.0" fill="#f4f0ff" opacity="0.96" style="animation-delay:-0.07s"/>
<polygon class="particle" points="244.6,179.4 241.8,185.2 247.4,185.2" fill="#d04dff" opacity="0.65" style="animation-delay:-0.79s"/>
<polygon class="particle" points="249.4,73.4 247.4,77.3 251.3,77.3" fill="#f4f0ff" opacity="0.76" style="animation-delay:-0.58s"/>
<polygon class="particle" points="166.0,161.4 162.8,168.2 169.3,168.2" fill="#d04dff" opacity="0.50" style="animation-delay:-0.07s"/>
<polygon class="particle" points="182.8,98.6 180.7,102.9 184.9,102.9" fill="#ffb829" opacity="0.43" style="animation-delay:-2.17s"/>
<polygon class="particle" points="247.3,200.5 244.5,206.3 250.1,206.3" fill="#8052ff" opacity="0.70" style="animation-delay:-1.00s"/>
<polygon class="particle" points="229.6,153.3 228.4,155.9 230.9,155.9" fill="#f4f0ff" opacity="0.42" style="animation-delay:-3.60s"/>
<polygon class="particle" points="206.4,89.8 205.2,92.3 207.7,92.3" fill="#f4f0ff" opacity="0.53" style="animation-delay:-1.29s"/>
<polygon class="particle" points="198.8,117.6 196.9,121.6 200.7,121.6" fill="#ffb829" opacity="0.69" style="animation-delay:-0.03s"/>
<polygon class="particle" points="228.8,147.6 226.8,151.7 230.8,151.7" fill="#8052ff" opacity="0.75" style="animation-delay:-3.60s"/>
<polygon class="particle" points="223.0,125.3 221.1,129.1 224.8,129.1" fill="#ffb829" opacity="0.51" style="animation-delay:-1.07s"/>
<polygon class="particle" points="185.2,217.4 182.3,223.5 188.2,223.5" fill="#8052ff" opacity="0.76" style="animation-delay:-2.94s"/>
<polygon class="particle" points="220.6,98.0 218.2,102.8 222.9,102.8" fill="#8052ff" opacity="0.44" style="animation-delay:-1.90s"/>
<polygon class="particle" points="205.4,252.0 203.5,255.9 207.3,255.9" fill="#46a7ff" opacity="0.56" style="animation-delay:-3.50s"/>
<polygon class="particle" points="217.1,158.8 215.6,161.9 218.6,161.9" fill="#f4f0ff" opacity="0.79" style="animation-delay:-2.49s"/>
<polygon class="particle" points="210.1,177.3 207.0,183.7 213.2,183.7" fill="#f4f0ff" opacity="0.60" style="animation-delay:-2.85s"/>
<polygon class="particle" points="188.1,246.8 186.9,249.3 189.3,249.3" fill="#ffb829" opacity="0.68" style="animation-delay:-1.69s"/>
<polygon class="particle" points="172.6,77.9 171.1,81.0 174.0,81.0" fill="#8052ff" opacity="0.47" style="animation-delay:-1.24s"/>
<polygon class="particle" points="217.3,232.8 214.3,238.9 220.3,238.9" fill="#f4f0ff" opacity="0.56" style="animation-delay:-2.62s"/>
<polygon class="particle" points="202.6,111.7 200.2,116.6 205.0,116.6" fill="#f4f0ff" opacity="0.42" style="animation-delay:-3.80s"/>
<polygon class="particle" points="220.3,54.8 217.1,61.5 223.6,61.5" fill="#f4f0ff" opacity="0.75" style="animation-delay:-0.90s"/>
<polygon class="particle" points="228.6,188.7 225.3,195.4 231.8,195.4" fill="#46a7ff" opacity="0.85" style="animation-delay:-0.50s"/>
<polygon class="particle" points="175.7,102.2 173.0,107.7 178.4,107.7" fill="#46a7ff" opacity="0.42" style="animation-delay:-1.43s"/>
<polygon class="particle" points="172.0,157.2 169.3,162.7 174.7,162.7" fill="#15846e" opacity="0.43" style="animation-delay:-1.93s"/>
<polygon class="particle" points="228.5,124.2 225.4,130.6 231.6,130.6" fill="#f4f0ff" opacity="0.56" style="animation-delay:-2.48s"/>
<polygon class="particle" points="196.0,257.9 193.2,263.6 198.7,263.6" fill="#f4f0ff" opacity="0.85" style="animation-delay:-2.61s"/>
<polygon class="particle" points="249.9,104.8 246.7,111.5 253.1,111.5" fill="#f4f0ff" opacity="0.46" style="animation-delay:-3.41s"/>
<polygon class="particle" points="227.0,235.2 224.0,241.5 230.0,241.5" fill="#d04dff" opacity="0.97" style="animation-delay:-1.94s"/>
<polygon class="particle" points="206.1,230.2 203.8,234.9 208.4,234.9" fill="#ffb829" opacity="0.54" style="animation-delay:-1.39s"/>
<polygon class="particle" points="221.5,123.2 218.5,129.2 224.4,129.2" fill="#f4f0ff" opacity="0.84" style="animation-delay:-1.31s"/>
<polygon class="particle" points="166.3,166.1 163.5,171.8 169.0,171.8" fill="#d04dff" opacity="0.44" style="animation-delay:-2.22s"/>
<polygon class="particle" points="225.2,222.2 223.5,225.7 226.9,225.7" fill="#d04dff" opacity="0.69" style="animation-delay:-3.09s"/>
<polygon class="particle" points="247.4,163.7 244.7,169.3 250.1,169.3" fill="#46a7ff" opacity="0.51" style="animation-delay:-2.60s"/>
<polygon class="particle" points="172.5,144.0 170.8,147.5 174.2,147.5" fill="#d04dff" opacity="0.74" style="animation-delay:-3.00s"/>
<polygon class="particle" points="202.1,252.3 199.6,257.3 204.5,257.3" fill="#8052ff" opacity="0.54" style="animation-delay:-2.74s"/>
<polygon class="particle" points="242.5,223.8 240.5,227.8 244.4,227.8" fill="#ffb829" opacity="0.67" style="animation-delay:-1.51s"/>
<polygon class="particle" points="195.5,156.2 193.9,159.4 197.0,159.4" fill="#f4f0ff" opacity="0.96" style="animation-delay:-3.30s"/>
<polygon class="particle" points="226.1,160.3 223.2,166.1 228.9,166.1" fill="#ffb829" opacity="0.90" style="animation-delay:-1.46s"/>
<polygon class="particle" points="219.8,267.3 218.0,271.0 221.6,271.0" fill="#f4f0ff" opacity="0.42" style="animation-delay:-3.12s"/>
<polygon class="particle" points="238.8,50.1 237.5,52.8 240.1,52.8" fill="#ffb829" opacity="0.92" style="animation-delay:-3.74s"/>
<polygon class="particle" points="244.1,79.1 242.1,83.2 246.1,83.2" fill="#ffb829" opacity="0.50" style="animation-delay:-0.30s"/>
<polygon class="particle" points="208.9,68.6 206.5,73.5 211.3,73.5" fill="#f4f0ff" opacity="0.83" style="animation-delay:-2.34s"/>
<polygon class="particle" points="189.1,197.9 187.5,201.3 190.8,201.3" fill="#ff7dcb" opacity="0.91" style="animation-delay:-1.12s"/>
<polygon class="particle" points="203.9,247.6 201.7,252.0 206.0,252.0" fill="#f4f0ff" opacity="0.41" style="animation-delay:-3.49s"/>
<polygon class="particle" points="245.1,31.1 242.7,36.2 247.5,36.2" fill="#ffb829" opacity="0.89" style="animation-delay:-2.73s"/>
<polygon class="particle" points="209.6,161.5 206.6,167.8 212.7,167.8" fill="#d04dff" opacity="0.86" style="animation-delay:-0.24s"/>
<polygon class="particle" points="186.6,39.6 184.3,44.4 189.0,44.4" fill="#d04dff" opacity="0.54" style="animation-delay:-2.04s"/>
<polygon class="particle" points="169.2,237.0 166.3,243.1 172.2,243.1" fill="#f4f0ff" opacity="0.50" style="animation-delay:-0.96s"/>
<polygon class="particle" points="238.1,183.1 235.4,188.7 240.8,188.7" fill="#f4f0ff" opacity="0.48" style="animation-delay:-1.26s"/>
<polygon class="particle" points="175.9,229.0 173.6,233.7 178.3,233.7" fill="#f4f0ff" opacity="0.79" style="animation-delay:-0.45s"/>
<polygon class="particle" points="238.7,46.2 237.5,48.7 239.9,48.7" fill="#f4f0ff" opacity="0.80" style="animation-delay:-3.54s"/>
<polygon class="particle" points="216.6,72.3 214.6,76.6 218.7,76.6" fill="#ff7dcb" opacity="0.87" style="animation-delay:-2.32s"/>
<polygon class="particle" points="224.4,145.4 222.4,149.6 226.4,149.6" fill="#f4f0ff" opacity="0.39" style="animation-delay:-3.82s"/>
<polygon class="particle" points="215.1,151.8 213.2,155.7 217.1,155.7" fill="#f4f0ff" opacity="0.94" style="animation-delay:-0.26s"/>
<polygon class="particle" points="179.8,193.2 176.8,199.4 182.8,199.4" fill="#46a7ff" opacity="0.69" style="animation-delay:-2.91s"/>
<polygon class="particle" points="185.0,54.4 181.7,61.2 188.3,61.2" fill="#46a7ff" opacity="0.47" style="animation-delay:-3.73s"/>
<polygon class="particle" points="191.2,45.4 189.8,48.4 192.7,48.4" fill="#d04dff" opacity="0.91" style="animation-delay:-3.31s"/>
<polygon class="particle" points="167.9,127.4 165.8,131.8 170.0,131.8" fill="#15846e" opacity="0.64" style="animation-delay:-0.66s"/>
<polygon class="particle" points="180.7,197.2 178.4,201.8 182.9,201.8" fill="#ff7dcb" opacity="0.45" style="animation-delay:-0.14s"/>
<polygon class="particle" points="225.7,189.6 222.8,195.6 228.6,195.6" fill="#d04dff" opacity="0.69" style="animation-delay:-3.69s"/>
<polygon class="particle" points="182.8,228.8 180.2,234.1 185.3,234.1" fill="#46a7ff" opacity="0.97" style="animation-delay:-2.87s"/>
<polygon class="particle" points="198.5,127.3 195.2,134.2 201.8,134.2" fill="#ffb829" opacity="0.87" style="animation-delay:-0.21s"/>
<polygon class="particle" points="178.4,62.7 175.6,68.4 181.1,68.4" fill="#8052ff" opacity="0.86" style="animation-delay:-2.68s"/>
<polygon class="particle" points="181.6,194.8 179.5,199.2 183.7,199.2" fill="#ff7dcb" opacity="0.43" style="animation-delay:-3.56s"/>
<polygon class="particle" points="188.5,267.1 187.3,269.4 189.6,269.4" fill="#8052ff" opacity="0.89" style="animation-delay:-3.36s"/>
<polygon class="particle" points="197.6,245.4 195.6,249.6 199.6,249.6" fill="#15846e" opacity="0.41" style="animation-delay:-2.04s"/>
<polygon class="particle" points="165.3,155.9 163.7,159.2 167.0,159.2" fill="#15846e" opacity="0.70" style="animation-delay:-3.97s"/>
<polygon class="particle" points="167.8,200.3 165.5,205.2 170.2,205.2" fill="#15846e" opacity="0.95" style="animation-delay:-3.50s"/>
<polygon class="particle" points="211.0,241.2 209.5,244.4 212.6,244.4" fill="#8052ff" opacity="0.81" style="animation-delay:-3.46s"/>
<polygon class="particle" points="175.1,121.8 172.5,127.2 177.8,127.2" fill="#46a7ff" opacity="0.90" style="animation-delay:-2.26s"/>
<polygon class="particle" points="185.7,177.8 182.7,184.0 188.7,184.0" fill="#46a7ff" opacity="0.50" style="animation-delay:-1.50s"/>
<polygon class="particle" points="224.4,151.9 221.5,157.8 227.2,157.8" fill="#46a7ff" opacity="0.92" style="animation-delay:-3.00s"/>
<polygon class="particle" points="208.5,141.9 206.5,145.9 210.4,145.9" fill="#ffb829" opacity="0.96" style="animation-delay:-2.07s"/>
<polygon class="particle" points="208.6,248.6 205.9,254.2 211.3,254.2" fill="#f4f0ff" opacity="0.89" style="animation-delay:-3.53s"/>
<polygon class="particle" points="193.7,232.4 192.6,234.7 194.8,234.7" fill="#f4f0ff" opacity="0.92" style="animation-delay:-1.76s"/>
<polygon class="particle" points="233.1,180.3 231.1,184.6 235.2,184.6" fill="#15846e" opacity="0.52" style="animation-delay:-0.12s"/>
<polygon class="particle" points="233.0,54.7 231.0,58.8 235.0,58.8" fill="#15846e" opacity="0.87" style="animation-delay:-0.94s"/>
<polygon class="particle" points="229.5,254.8 227.6,258.9 231.5,258.9" fill="#f4f0ff" opacity="0.96" style="animation-delay:-2.82s"/>
<polygon class="particle" points="176.8,153.6 174.7,158.1 179.0,158.1" fill="#d04dff" opacity="0.55" style="animation-delay:-2.90s"/>
<polygon class="particle" points="213.8,214.7 211.4,219.7 216.2,219.7" fill="#8052ff" opacity="0.87" style="animation-delay:-1.12s"/>
<polygon class="particle" points="227.4,66.4 224.3,72.8 230.5,72.8" fill="#15846e" opacity="0.73" style="animation-delay:-0.45s"/>
<polygon class="particle" points="244.0,231.8 241.5,237.0 246.5,237.0" fill="#ffb829" opacity="0.57" style="animation-delay:-0.84s"/>
<polygon class="particle" points="184.4,91.6 183.2,94.0 185.6,94.0" fill="#8052ff" opacity="0.63" style="animation-delay:-2.79s"/>
<polygon class="particle" points="225.1,226.2 223.1,230.2 227.0,230.2" fill="#f4f0ff" opacity="0.64" style="animation-delay:-1.28s"/>
<polygon class="particle" points="210.9,160.1 208.8,164.6 213.1,164.6" fill="#f4f0ff" opacity="0.42" style="animation-delay:-0.60s"/>
<polygon class="particle" points="193.6,242.5 190.7,248.4 196.4,248.4" fill="#f4f0ff" opacity="0.93" style="animation-delay:-1.32s"/>
<polygon class="particle" points="218.0,211.7 216.7,214.3 219.3,214.3" fill="#8052ff" opacity="0.92" style="animation-delay:-2.35s"/>
<polygon class="particle" points="228.1,142.1 226.2,146.1 230.1,146.1" fill="#ffb829" opacity="0.87" style="animation-delay:-1.84s"/>
<polygon class="particle" points="175.7,80.5 173.9,84.1 177.5,84.1" fill="#f4f0ff" opacity="0.53" style="animation-delay:-1.28s"/>
<polygon class="particle" points="178.2,124.6 176.9,127.1 179.4,127.1" fill="#15846e" opacity="0.80" style="animation-delay:-3.29s"/>
<polygon class="particle" points="209.6,87.4 208.0,90.8 211.3,90.8" fill="#f4f0ff" opacity="0.67" style="animation-delay:-0.85s"/>
<polygon class="particle" points="239.9,213.8 238.3,217.2 241.6,217.2" fill="#ff7dcb" opacity="0.55" style="animation-delay:-0.70s"/>
<polygon class="particle" points="215.4,246.7 213.7,250.0 217.0,250.0" fill="#46a7ff" opacity="0.43" style="animation-delay:-0.33s"/>
<polygon class="particle" points="192.7,143.7 190.3,148.6 195.1,148.6" fill="#8052ff" opacity="0.91" style="animation-delay:-3.95s"/>
<polygon class="particle" points="178.6,136.2 175.9,141.7 181.3,141.7" fill="#15846e" opacity="0.94" style="animation-delay:-0.28s"/>
<polygon class="particle" points="208.1,43.4 204.9,50.0 211.4,50.0" fill="#8052ff" opacity="0.84" style="animation-delay:-2.40s"/>
<polygon class="particle" points="210.3,264.4 209.1,267.0 211.6,267.0" fill="#f4f0ff" opacity="0.73" style="animation-delay:-3.97s"/>
<polygon class="particle" points="193.6,78.4 192.2,81.1 194.9,81.1" fill="#46a7ff" opacity="0.67" style="animation-delay:-1.40s"/>
<polygon class="particle" points="240.0,68.8 238.0,73.0 242.1,73.0" fill="#15846e" opacity="0.70" style="animation-delay:-2.70s"/>
<polygon class="particle" points="189.4,201.2 188.1,203.9 190.7,203.9" fill="#d04dff" opacity="0.70" style="animation-delay:-3.97s"/>
<polygon class="particle" points="207.5,228.8 205.2,233.6 209.8,233.6" fill="#f4f0ff" opacity="0.91" style="animation-delay:-1.35s"/>
<polygon class="particle" points="178.0,211.2 175.1,217.2 180.9,217.2" fill="#15846e" opacity="0.73" style="animation-delay:-0.42s"/>
<polygon class="particle" points="246.8,220.3 243.9,226.2 249.6,226.2" fill="#ffb829" opacity="0.55" style="animation-delay:-0.02s"/>
<polygon class="particle" points="172.1,75.5 170.3,79.3 173.9,79.3" fill="#ffb829" opacity="0.42" style="animation-delay:-3.78s"/>
<polygon class="particle" points="210.0,147.4 207.7,152.4 212.4,152.4" fill="#f4f0ff" opacity="0.78" style="animation-delay:-2.86s"/>
<polygon class="particle" points="251.2,146.0 249.8,148.8 252.5,148.8" fill="#ffb829" opacity="0.79" style="animation-delay:-3.51s"/>
<polygon class="particle" points="174.2,63.6 172.0,68.1 176.4,68.1" fill="#8052ff" opacity="0.41" style="animation-delay:-3.66s"/>
<polygon class="particle" points="167.6,226.1 164.5,232.7 170.8,232.7" fill="#ffb829" opacity="0.62" style="animation-delay:-0.03s"/>
<polygon class="particle" points="249.1,146.8 247.4,150.4 250.9,150.4" fill="#f4f0ff" opacity="0.94" style="animation-delay:-1.15s"/>
<polygon class="particle" points="245.6,80.9 242.7,87.0 248.6,87.0" fill="#8052ff" opacity="0.91" style="animation-delay:-2.31s"/>
<polygon class="particle" points="248.0,168.6 245.4,173.9 250.6,173.9" fill="#ffb829" opacity="0.57" style="animation-delay:-2.11s"/>
<polygon class="particle" points="177.0,159.5 175.6,162.3 178.3,162.3" fill="#46a7ff" opacity="0.67" style="animation-delay:-1.06s"/>
<polygon class="particle" points="195.9,261.3 193.4,266.5 198.4,266.5" fill="#ffb829" opacity="0.56" style="animation-delay:-3.30s"/>
<polygon class="particle" points="248.4,253.3 245.7,258.8 251.0,258.8" fill="#46a7ff" opacity="0.58" style="animation-delay:-3.52s"/>
<polygon class="particle" points="209.8,154.3 208.2,157.7 211.5,157.7" fill="#15846e" opacity="0.75" style="animation-delay:-1.60s"/>
<polygon class="particle" points="182.5,188.6 181.3,191.1 183.6,191.1" fill="#8052ff" opacity="0.70" style="animation-delay:-0.02s"/>
<polygon class="particle" points="207.7,193.6 205.8,197.5 209.5,197.5" fill="#d04dff" opacity="0.47" style="animation-delay:-1.69s"/>
<polygon class="particle" points="181.4,238.5 179.5,242.4 183.4,242.4" fill="#f4f0ff" opacity="0.39" style="animation-delay:-2.16s"/>
<polygon class="particle" points="175.5,112.2 172.3,118.8 178.7,118.8" fill="#f4f0ff" opacity="0.58" style="animation-delay:-1.91s"/>
<polygon class="particle" points="248.2,256.9 245.9,261.5 250.5,261.5" fill="#d04dff" opacity="0.77" style="animation-delay:-0.14s"/>
<polygon class="particle" points="186.2,98.3 184.8,101.1 187.5,101.1" fill="#15846e" opacity="0.60" style="animation-delay:-0.19s"/>
<polygon class="particle" points="211.5,129.2 210.2,131.8 212.7,131.8" fill="#ffb829" opacity="0.72" style="animation-delay:-3.12s"/>
<polygon class="particle" points="208.8,241.8 205.5,248.7 212.1,248.7" fill="#d04dff" opacity="0.49" style="animation-delay:-2.50s"/>
<polygon class="particle" points="224.2,116.1 221.3,122.2 227.2,122.2" fill="#46a7ff" opacity="0.46" style="animation-delay:-2.40s"/>
<polygon class="particle" points="249.0,182.1 247.5,185.1 250.4,185.1" fill="#f4f0ff" opacity="0.67" style="animation-delay:-1.31s"/>
<polygon class="particle" points="208.7,181.1 206.1,186.6 211.4,186.6" fill="#8052ff" opacity="0.95" style="animation-delay:-0.53s"/>
<polygon class="particle" points="188.6,242.6 185.3,249.3 191.8,249.3" fill="#8052ff" opacity="0.41" style="animation-delay:-0.62s"/>
<polygon class="particle" points="245.5,65.4 244.3,67.9 246.8,67.9" fill="#ffb829" opacity="0.78" style="animation-delay:-3.18s"/>
<polygon class="particle" points="165.6,185.7 163.0,191.1 168.2,191.1" fill="#8052ff" opacity="0.92" style="animation-delay:-3.14s"/>
<polygon class="particle" points="252.9,153.4 250.3,158.7 255.4,158.7" fill="#d04dff" opacity="0.64" style="animation-delay:-0.88s"/>
<polygon class="particle" points="231.2,41.8 230.0,44.1 232.3,44.1" fill="#d04dff" opacity="0.51" style="animation-delay:-1.97s"/>
<polygon class="particle" points="238.4,105.7 235.8,111.3 241.1,111.3" fill="#d04dff" opacity="0.43" style="animation-delay:-1.31s"/>
<polygon class="particle" points="175.7,200.5 173.2,205.6 178.2,205.6" fill="#15846e" opacity="0.59" style="animation-delay:-0.69s"/>
<polygon class="particle" points="193.1,173.1 190.9,177.6 195.2,177.6" fill="#f4f0ff" opacity="0.88" style="animation-delay:-3.70s"/>
<polygon class="particle" points="192.1,234.2 189.8,238.9 194.4,238.9" fill="#ffb829" opacity="0.56" style="animation-delay:-0.60s"/>
<polygon class="particle" points="235.0,205.9 232.0,212.2 238.1,212.2" fill="#ffb829" opacity="0.79" style="animation-delay:-1.17s"/>
<polygon class="particle" points="200.2,137.5 198.0,141.9 202.3,141.9" fill="#d04dff" opacity="0.85" style="animation-delay:-2.37s"/>
<polygon class="particle" points="245.1,105.7 242.2,111.8 248.1,111.8" fill="#ffb829" opacity="0.39" style="animation-delay:-3.06s"/>
<polygon class="particle" points="197.9,89.4 194.7,95.9 201.0,95.9" fill="#ffb829" opacity="0.72" style="animation-delay:-2.75s"/>
<polygon class="particle" points="165.6,152.3 162.5,158.7 168.7,158.7" fill="#8052ff" opacity="0.97" style="animation-delay:-3.70s"/>
<polygon class="particle" points="238.1,228.0 235.2,234.0 241.0,234.0" fill="#d04dff" opacity="0.58" style="animation-delay:-1.77s"/>
<polygon class="particle" points="250.2,185.0 247.8,189.9 252.6,189.9" fill="#d04dff" opacity="0.66" style="animation-delay:-2.50s"/>
<polygon class="particle" points="191.1,264.3 188.2,270.2 194.0,270.2" fill="#ff7dcb" opacity="0.58" style="animation-delay:-0.48s"/>
<polygon class="particle" points="249.8,69.7 247.1,75.3 252.5,75.3" fill="#8052ff" opacity="0.77" style="animation-delay:-2.58s"/>
<polygon class="particle" points="247.9,34.3 245.5,39.3 250.3,39.3" fill="#d04dff" opacity="0.90" style="animation-delay:-2.27s"/>
<polygon class="particle" points="209.5,178.1 207.7,182.0 211.4,182.0" fill="#f4f0ff" opacity="0.81" style="animation-delay:-0.44s"/>
<polygon class="particle" points="210.5,220.6 209.0,223.7 212.0,223.7" fill="#ffb829" opacity="0.66" style="animation-delay:-0.55s"/>
<polygon class="particle" points="213.0,63.5 210.2,69.3 215.8,69.3" fill="#f4f0ff" opacity="0.62" style="animation-delay:-2.34s"/>
<polygon class="particle" points="202.5,169.6 200.1,174.7 205.0,174.7" fill="#8052ff" opacity="0.65" style="animation-delay:-0.96s"/>
<polygon class="particle" points="215.1,86.0 212.8,90.8 217.4,90.8" fill="#f4f0ff" opacity="0.74" style="animation-delay:-2.61s"/>
<polygon class="particle" points="240.4,213.7 238.0,218.6 242.8,218.6" fill="#f4f0ff" opacity="0.79" style="animation-delay:-2.40s"/>
<polygon class="particle" points="237.3,244.5 234.8,249.7 239.9,249.7" fill="#8052ff" opacity="0.49" style="animation-delay:-0.57s"/>
<polygon class="particle" points="200.5,218.6 197.8,224.1 203.1,224.1" fill="#f4f0ff" opacity="0.41" style="animation-delay:-1.85s"/>
<polygon class="particle" points="166.3,112.3 163.3,118.5 169.3,118.5" fill="#8052ff" opacity="0.72" style="animation-delay:-3.88s"/>
<polygon class="particle" points="197.8,120.5 196.4,123.2 199.1,123.2" fill="#8052ff" opacity="0.76" style="animation-delay:-1.82s"/>
<polygon class="particle" points="203.6,131.6 201.2,136.5 206.0,136.5" fill="#f4f0ff" opacity="0.63" style="animation-delay:-2.22s"/>
<polygon class="particle" points="254.2,147.9 252.6,151.2 255.8,151.2" fill="#ffb829" opacity="0.40" style="animation-delay:-2.78s"/>
<polygon class="particle" points="240.4,40.5 238.7,44.0 242.1,44.0" fill="#ffb829" opacity="0.91" style="animation-delay:-3.37s"/>
<polygon class="particle" points="173.6,113.3 170.3,120.2 177.0,120.2" fill="#ffb829" opacity="0.94" style="animation-delay:-0.76s"/>
<polygon class="particle" points="171.1,49.0 168.5,54.6 173.8,54.6" fill="#ffb829" opacity="0.70" style="animation-delay:-3.27s"/>
<polygon class="particle" points="252.0,77.6 249.5,82.8 254.5,82.8" fill="#15846e" opacity="0.91" style="animation-delay:-0.51s"/>
<polygon class="particle" points="173.8,166.1 171.6,170.5 175.9,170.5" fill="#ff7dcb" opacity="0.40" style="animation-delay:-0.32s"/>
<polygon class="particle" points="242.8,80.4 240.1,85.9 245.5,85.9" fill="#46a7ff" opacity="0.66" style="animation-delay:-2.23s"/>
<polygon class="particle" points="244.3,31.2 242.1,35.8 246.6,35.8" fill="#8052ff" opacity="0.72" style="animation-delay:-3.32s"/>
<polygon class="particle" points="191.8,109.2 189.1,114.7 194.4,114.7" fill="#ffb829" opacity="0.60" style="animation-delay:-0.22s"/>
<polygon class="particle" points="172.0,122.0 170.0,126.2 174.1,126.2" fill="#d04dff" opacity="0.49" style="animation-delay:-2.85s"/>
<polygon class="particle" points="186.1,129.5 184.4,133.1 187.8,133.1" fill="#15846e" opacity="0.96" style="animation-delay:-3.52s"/>
<polygon class="particle" points="241.9,30.9 240.2,34.3 243.6,34.3" fill="#f4f0ff" opacity="0.44" style="animation-delay:-1.18s"/>
<polygon class="particle" points="179.4,40.3 177.2,44.8 181.6,44.8" fill="#8052ff" opacity="0.45" style="animation-delay:-1.83s"/>
<polygon class="particle" points="224.7,54.7 222.6,59.0 226.8,59.0" fill="#46a7ff" opacity="0.47" style="animation-delay:-2.35s"/>
<polygon class="particle" points="244.5,106.5 242.3,111.1 246.7,111.1" fill="#8052ff" opacity="0.78" style="animation-delay:-1.97s"/>
<polygon class="particle" points="205.2,31.5 203.4,35.3 207.0,35.3" fill="#8052ff" opacity="0.91" style="animation-delay:-0.94s"/>
<polygon class="particle" points="188.0,46.8 185.4,52.0 190.5,52.0" fill="#f4f0ff" opacity="0.63" style="animation-delay:-1.05s"/>
<polygon class="particle" points="173.2,50.4 170.1,56.9 176.4,56.9" fill="#f4f0ff" opacity="0.91" style="animation-delay:-2.56s"/>
<polygon class="particle" points="237.7,186.1 235.5,190.5 239.8,190.5" fill="#46a7ff" opacity="0.68" style="animation-delay:-2.10s"/>
<polygon class="particle" points="191.5,57.2 190.1,60.0 192.9,60.0" fill="#f4f0ff" opacity="0.88" style="animation-delay:-2.77s"/>
<polygon class="particle" points="171.5,265.3 170.1,268.2 172.9,268.2" fill="#15846e" opacity="0.85" style="animation-delay:-2.64s"/>
<polygon class="particle" points="217.0,248.7 213.9,255.0 220.0,255.0" fill="#f4f0ff" opacity="0.60" style="animation-delay:-1.84s"/>
<polygon class="particle" points="237.0,146.7 235.3,150.0 238.6,150.0" fill="#ffb829" opacity="0.80" style="animation-delay:-3.99s"/>
<polygon class="particle" points="197.3,199.1 195.0,203.9 199.6,203.9" fill="#46a7ff" opacity="0.96" style="animation-delay:-0.38s"/>
<polygon class="particle" points="227.3,83.8 224.0,90.7 230.6,90.7" fill="#15846e" opacity="0.47" style="animation-delay:-0.79s"/>
<polygon class="particle" points="200.5,229.3 198.9,232.4 202.0,232.4" fill="#8052ff" opacity="0.87" style="animation-delay:-3.39s"/>
<polygon class="particle" points="238.3,265.7 236.9,268.6 239.7,268.6" fill="#ffb829" opacity="0.39" style="animation-delay:-2.13s"/>
<polygon class="particle" points="175.9,229.3 173.4,234.4 178.4,234.4" fill="#15846e" opacity="0.90" style="animation-delay:-2.10s"/>
<polygon class="particle" points="200.4,114.4 198.5,118.4 202.3,118.4" fill="#8052ff" opacity="0.52" style="animation-delay:-3.41s"/>
<polygon class="particle" points="193.0,178.8 190.4,184.2 195.6,184.2" fill="#46a7ff" opacity="0.97" style="animation-delay:-0.94s"/>
<polygon class="particle" points="203.2,261.3 201.8,264.2 204.5,264.2" fill="#15846e" opacity="0.92" style="animation-delay:-2.23s"/>
<polygon class="particle" points="237.0,49.7 234.0,55.8 240.0,55.8" fill="#d04dff" opacity="0.42" style="animation-delay:-3.10s"/>
<polygon class="particle" points="186.5,111.0 183.5,117.2 189.6,117.2" fill="#f4f0ff" opacity="0.51" style="animation-delay:-3.55s"/>
<polygon class="particle" points="169.5,133.0 168.2,135.7 170.7,135.7" fill="#15846e" opacity="0.96" style="animation-delay:-2.58s"/>
<polygon class="particle" points="240.9,212.9 237.8,219.2 243.9,219.2" fill="#46a7ff" opacity="0.97" style="animation-delay:-3.23s"/>
<polygon class="particle" points="236.7,42.3 234.4,47.0 239.0,47.0" fill="#ffb829" opacity="0.67" style="animation-delay:-1.24s"/>
<polygon class="particle" points="235.6,230.9 233.9,234.4 237.3,234.4" fill="#ffb829" opacity="0.52" style="animation-delay:-0.71s"/>
<polygon class="particle" points="201.7,263.1 199.4,267.8 204.0,267.8" fill="#8052ff" opacity="0.87" style="animation-delay:-3.08s"/>
<polygon class="particle" points="250.8,163.6 248.9,167.7 252.8,167.7" fill="#46a7ff" opacity="0.46" style="animation-delay:-3.20s"/>
<polygon class="particle" points="199.0,36.6 196.3,42.2 201.7,42.2" fill="#ff7dcb" opacity="0.58" style="animation-delay:-0.50s"/>
<polygon class="particle" points="218.7,144.7 216.3,149.7 221.2,149.7" fill="#ffb829" opacity="0.41" style="animation-delay:-3.79s"/>
<polygon class="particle" points="217.7,183.2 215.5,187.8 219.9,187.8" fill="#d04dff" opacity="0.72" style="animation-delay:-1.77s"/>
<polygon class="particle" points="217.9,230.4 216.0,234.2 219.8,234.2" fill="#46a7ff" opacity="0.48" style="animation-delay:-1.81s"/>
<polygon class="particle" points="219.0,177.9 216.7,182.7 221.4,182.7" fill="#ffb829" opacity="0.49" style="animation-delay:-1.32s"/>
<polygon class="particle" points="237.5,167.0 234.2,173.8 240.9,173.8" fill="#ffb829" opacity="0.50" style="animation-delay:-1.83s"/>
<polygon class="particle" points="205.4,240.3 202.9,245.4 207.9,245.4" fill="#ff7dcb" opacity="0.96" style="animation-delay:-1.91s"/>
<polygon class="particle" points="191.7,110.5 189.2,115.7 194.2,115.7" fill="#46a7ff" opacity="0.46" style="animation-delay:-3.16s"/>
<polygon class="particle" points="216.7,257.0 215.0,260.5 218.4,260.5" fill="#8052ff" opacity="0.63" style="animation-delay:-0.43s"/>
<polygon class="particle" points="173.8,171.9 171.1,177.4 176.5,177.4" fill="#f4f0ff" opacity="0.70" style="animation-delay:-1.02s"/>
<polygon class="particle" points="244.7,56.0 241.9,61.9 247.5,61.9" fill="#d04dff" opacity="0.74" style="animation-delay:-0.97s"/>
<polygon class="particle" points="225.7,261.2 222.7,267.5 228.8,267.5" fill="#8052ff" opacity="0.64" style="animation-delay:-1.62s"/>
<polygon class="particle" points="219.7,212.5 216.6,219.0 222.9,219.0" fill="#f4f0ff" opacity="0.39" style="animation-delay:-3.02s"/>
<polygon class="particle" points="198.2,94.1 195.4,99.6 200.9,99.6" fill="#d04dff" opacity="0.77" style="animation-delay:-1.33s"/>
<polygon class="particle" points="184.0,239.2 182.4,242.6 185.7,242.6" fill="#8052ff" opacity="0.62" style="animation-delay:-2.28s"/>
<polygon class="particle" points="191.3,212.6 189.4,216.6 193.2,216.6" fill="#f4f0ff" opacity="0.78" style="animation-delay:-1.18s"/>
<polygon class="particle" points="224.9,224.9 221.9,231.1 227.9,231.1" fill="#8052ff" opacity="0.79" style="animation-delay:-2.80s"/>
<polygon class="particle" points="180.4,156.4 178.2,161.0 182.7,161.0" fill="#f4f0ff" opacity="0.88" style="animation-delay:-3.23s"/>
<polygon class="particle" points="243.2,117.7 241.8,120.5 244.6,120.5" fill="#f4f0ff" opacity="0.96" style="animation-delay:-1.97s"/>
<polygon class="particle" points="178.2,85.0 176.2,89.2 180.2,89.2" fill="#46a7ff" opacity="0.71" style="animation-delay:-1.71s"/>
<polygon class="particle" points="208.9,254.5 207.4,257.7 210.5,257.7" fill="#f4f0ff" opacity="0.59" style="animation-delay:-2.40s"/>
<polygon class="particle" points="213.3,256.2 211.2,260.5 215.3,260.5" fill="#46a7ff" opacity="0.80" style="animation-delay:-2.31s"/>
<polygon class="particle" points="217.8,236.5 214.9,242.5 220.7,242.5" fill="#8052ff" opacity="0.56" style="animation-delay:-3.87s"/>
<polygon class="particle" points="221.2,181.5 219.7,184.6 222.7,184.6" fill="#ffb829" opacity="0.71" style="animation-delay:-0.32s"/>
<polygon class="particle" points="247.3,85.6 244.7,91.1 250.0,91.1" fill="#f4f0ff" opacity="0.43" style="animation-delay:-1.91s"/>
<polygon class="particle" points="226.7,65.3 224.0,70.8 229.4,70.8" fill="#ffb829" opacity="0.81" style="animation-delay:-2.52s"/>
<polygon class="particle" points="240.5,113.0 238.1,118.0 243.0,118.0" fill="#8052ff" opacity="0.83" style="animation-delay:-3.96s"/>
<polygon class="particle" points="199.1,214.7 195.7,221.6 202.4,221.6" fill="#ffb829" opacity="0.80" style="animation-delay:-2.77s"/>
<polygon class="particle" points="188.9,254.9 185.9,261.1 191.9,261.1" fill="#f4f0ff" opacity="0.73" style="animation-delay:-3.85s"/>
<polygon class="particle" points="214.4,85.8 212.4,89.8 216.3,89.8" fill="#8052ff" opacity="0.65" style="animation-delay:-0.38s"/>
<polygon class="particle" points="183.7,29.8 180.5,36.3 186.8,36.3" fill="#ffb829" opacity="0.61" style="animation-delay:-1.30s"/>
<polygon class="particle" points="232.8,238.2 231.2,241.5 234.4,241.5" fill="#15846e" opacity="0.92" style="animation-delay:-1.75s"/>
<polygon class="particle" points="252.0,195.8 250.0,199.8 253.9,199.8" fill="#ffb829" opacity="0.82" style="animation-delay:-2.85s"/>
<polygon class="particle" points="236.7,174.2 234.9,178.0 238.6,178.0" fill="#15846e" opacity="0.44" style="animation-delay:-2.54s"/>
<polygon class="particle" points="236.7,64.7 233.9,70.3 239.4,70.3" fill="#d04dff" opacity="0.74" style="animation-delay:-2.01s"/>
<polygon class="particle" points="247.3,203.4 244.3,209.7 250.4,209.7" fill="#8052ff" opacity="0.96" style="animation-delay:-0.07s"/>
<polygon class="particle" points="221.8,36.2 219.7,40.5 223.9,40.5" fill="#8052ff" opacity="0.60" style="animation-delay:-2.20s"/>
<polygon class="particle" points="207.2,225.8 205.3,229.5 209.0,229.5" fill="#8052ff" opacity="0.75" style="animation-delay:-1.35s"/>
<polygon class="particle" points="227.2,50.3 225.0,54.7 229.3,54.7" fill="#8052ff" opacity="0.87" style="animation-delay:-1.90s"/>
<polygon class="particle" points="199.3,200.5 196.2,206.8 202.4,206.8" fill="#8052ff" opacity="0.43" style="animation-delay:-0.52s"/>
<polygon class="particle" points="233.8,87.6 232.2,91.0 235.5,91.0" fill="#15846e" opacity="0.49" style="animation-delay:-2.76s"/>
<polygon class="particle" points="216.4,181.3 213.8,186.7 219.1,186.7" fill="#f4f0ff" opacity="0.89" style="animation-delay:-2.15s"/>
<polygon class="particle" points="183.5,223.0 182.1,225.9 184.8,225.9" fill="#8052ff" opacity="0.40" style="animation-delay:-1.12s"/>
<polygon class="particle" points="254.4,143.4 251.8,148.9 257.0,148.9" fill="#8052ff" opacity="0.55" style="animation-delay:-3.96s"/>
<polygon class="particle" points="175.1,253.6 172.4,259.0 177.7,259.0" fill="#d04dff" opacity="0.61" style="animation-delay:-2.55s"/>
<polygon class="particle" points="241.6,123.8 239.1,129.0 244.1,129.0" fill="#15846e" opacity="0.58" style="animation-delay:-0.39s"/>
<polygon class="particle" points="201.9,148.4 200.2,152.0 203.6,152.0" fill="#d04dff" opacity="0.47" style="animation-delay:-1.66s"/>
<polygon class="particle" points="217.8,228.6 214.6,235.2 221.0,235.2" fill="#f4f0ff" opacity="0.65" style="animation-delay:-1.81s"/>
<polygon class="particle" points="252.6,189.3 249.8,195.2 255.5,195.2" fill="#d04dff" opacity="0.53" style="animation-delay:-2.43s"/>
<polygon class="particle" points="216.2,209.3 213.7,214.4 218.7,214.4" fill="#ff7dcb" opacity="0.72" style="animation-delay:-3.06s"/>
<polygon class="particle" points="244.1,216.4 242.2,220.5 246.1,220.5" fill="#15846e" opacity="0.83" style="animation-delay:-2.11s"/>
<polygon class="particle" points="217.4,76.0 215.1,80.9 219.7,80.9" fill="#d04dff" opacity="0.56" style="animation-delay:-2.16s"/>
<polygon class="particle" points="230.3,136.7 227.5,142.7 233.2,142.7" fill="#ffb829" opacity="0.63" style="animation-delay:-2.33s"/>
<polygon class="particle" points="207.3,43.8 206.0,46.5 208.6,46.5" fill="#ffb829" opacity="0.74" style="animation-delay:-1.39s"/>
<polygon class="particle" points="221.6,57.8 219.4,62.5 223.9,62.5" fill="#d04dff" opacity="0.72" style="animation-delay:-0.52s"/>
<polygon class="particle" points="252.8,92.0 250.0,97.7 255.6,97.7" fill="#f4f0ff" opacity="0.43" style="animation-delay:-2.99s"/>
<polygon class="particle" points="188.1,258.2 185.9,262.8 190.3,262.8" fill="#d04dff" opacity="0.95" style="animation-delay:-3.21s"/>
<polygon class="particle" points="197.9,180.9 195.2,186.5 200.7,186.5" fill="#15846e" opacity="0.82" style="animation-delay:-1.58s"/>
<polygon class="particle" points="239.2,219.5 237.5,223.0 240.9,223.0" fill="#f4f0ff" opacity="0.76" style="animation-delay:-1.78s"/>
<polygon class="particle" points="249.3,258.7 246.8,263.8 251.7,263.8" fill="#46a7ff" opacity="0.55" style="animation-delay:-2.82s"/>
<polygon class="particle" points="204.6,59.3 203.2,62.3 206.1,62.3" fill="#d04dff" opacity="0.77" style="animation-delay:-1.28s"/>
<polygon class="particle" points="239.9,144.8 236.9,150.9 242.9,150.9" fill="#ffb829" opacity="0.67" style="animation-delay:-0.18s"/>
<polygon class="particle" points="203.4,219.4 200.7,224.9 206.1,224.9" fill="#8052ff" opacity="0.50" style="animation-delay:-2.69s"/>
<polygon class="particle" points="168.3,209.6 166.1,214.3 170.6,214.3" fill="#8052ff" opacity="0.58" style="animation-delay:-1.19s"/>
<polygon class="particle" points="229.9,202.2 227.3,207.6 232.6,207.6" fill="#8052ff" opacity="0.70" style="animation-delay:-3.08s"/>
<polygon class="particle" points="223.8,145.1 221.6,149.6 226.0,149.6" fill="#46a7ff" opacity="0.86" style="animation-delay:-3.30s"/>
<polygon class="particle" points="211.0,155.3 209.7,157.9 212.2,157.9" fill="#d04dff" opacity="0.84" style="animation-delay:-1.01s"/>
<polygon class="particle" points="207.5,176.5 205.2,181.3 209.8,181.3" fill="#46a7ff" opacity="0.47" style="animation-delay:-1.43s"/>
<polygon class="particle" points="167.5,86.1 165.9,89.6 169.2,89.6" fill="#46a7ff" opacity="0.83" style="animation-delay:-3.75s"/>
<polygon class="particle" points="188.4,184.5 187.1,187.2 189.7,187.2" fill="#f4f0ff" opacity="0.67" style="animation-delay:-2.50s"/>
<polygon class="particle" points="242.9,154.3 241.1,157.9 244.6,157.9" fill="#d04dff" opacity="0.80" style="animation-delay:-0.69s"/>
<polygon class="particle" points="168.6,117.1 165.4,123.9 171.9,123.9" fill="#8052ff" opacity="0.44" style="animation-delay:-3.22s"/>
<polygon class="particle" points="227.7,237.9 226.3,240.8 229.1,240.8" fill="#ff7dcb" opacity="0.92" style="animation-delay:-2.33s"/>
<polygon class="particle" points="241.1,255.3 237.8,262.0 244.3,262.0" fill="#ffb829" opacity="0.80" style="animation-delay:-3.74s"/>
<polygon class="particle" points="212.5,234.3 210.3,238.7 214.7,238.7" fill="#ff7dcb" opacity="0.48" style="animation-delay:-2.67s"/>
<polygon class="particle" points="238.4,166.9 236.5,170.6 240.2,170.6" fill="#15846e" opacity="0.40" style="animation-delay:-2.94s"/>
<polygon class="particle" points="175.9,72.4 173.4,77.5 178.3,77.5" fill="#f4f0ff" opacity="0.80" style="animation-delay:-0.92s"/>
<polygon class="particle" points="224.8,259.2 223.3,262.2 226.3,262.2" fill="#ffb829" opacity="0.66" style="animation-delay:-3.35s"/>
<polygon class="particle" points="194.5,42.9 191.4,49.5 197.7,49.5" fill="#46a7ff" opacity="0.67" style="animation-delay:-1.57s"/>
<polygon class="particle" points="238.1,50.8 236.5,54.0 239.6,54.0" fill="#f4f0ff" opacity="0.91" style="animation-delay:-3.39s"/>
<polygon class="particle" points="219.0,106.4 216.6,111.4 221.4,111.4" fill="#ffb829" opacity="0.49" style="animation-delay:-0.04s"/>
<polygon class="particle" points="168.5,131.3 166.3,135.8 170.7,135.8" fill="#15846e" opacity="0.92" style="animation-delay:-2.59s"/>
<polygon class="particle" points="220.4,231.1 219.0,233.9 221.7,233.9" fill="#ffb829" opacity="0.41" style="animation-delay:-2.09s"/>
<polygon class="particle" points="165.8,171.6 162.9,177.7 168.8,177.7" fill="#ffb829" opacity="0.84" style="animation-delay:-2.78s"/>
<polygon class="particle" points="191.8,57.8 189.9,61.7 193.7,61.7" fill="#ffb829" opacity="0.68" style="animation-delay:-0.86s"/>
<polygon class="particle" points="202.8,70.5 199.6,77.1 206.0,77.1" fill="#8052ff" opacity="0.73" style="animation-delay:-2.31s"/>
<polygon class="particle" points="241.5,162.3 238.4,168.9 244.7,168.9" fill="#ffb829" opacity="0.61" style="animation-delay:-2.54s"/>
<polygon class="particle" points="209.3,84.0 207.0,88.7 211.5,88.7" fill="#f4f0ff" opacity="0.64" style="animation-delay:-0.93s"/>
<polygon class="particle" points="205.0,149.3 202.1,155.3 207.9,155.3" fill="#15846e" opacity="0.76" style="animation-delay:-3.33s"/>
<polygon class="particle" points="186.8,143.3 185.3,146.4 188.3,146.4" fill="#8052ff" opacity="0.76" style="animation-delay:-3.44s"/>
<polygon class="particle" points="212.8,224.5 210.0,230.3 215.6,230.3" fill="#d04dff" opacity="0.83" style="animation-delay:-1.49s"/>
<polygon class="particle" points="224.7,131.5 222.8,135.6 226.7,135.6" fill="#f4f0ff" opacity="0.90" style="animation-delay:-0.91s"/>
<polygon class="particle" points="200.2,112.6 197.1,119.1 203.3,119.1" fill="#ff7dcb" opacity="0.50" style="animation-delay:-1.02s"/>
<polygon class="particle" points="252.1,108.7 250.7,111.7 253.6,111.7" fill="#15846e" opacity="0.39" style="animation-delay:-1.38s"/>
<polygon class="particle" points="208.8,144.6 206.0,150.3 211.5,150.3" fill="#8052ff" opacity="0.85" style="animation-delay:-2.82s"/>
<polygon class="particle" points="209.7,79.8 208.2,82.9 211.1,82.9" fill="#ff7dcb" opacity="0.84" style="animation-delay:-0.99s"/>
<polygon class="particle" points="221.8,246.6 219.9,250.5 223.7,250.5" fill="#f4f0ff" opacity="0.60" style="animation-delay:-1.50s"/>
<polygon class="particle" points="188.1,124.3 185.6,129.4 190.6,129.4" fill="#d04dff" opacity="0.72" style="animation-delay:-2.57s"/>
<polygon class="particle" points="235.1,196.9 233.7,199.8 236.5,199.8" fill="#d04dff" opacity="0.71" style="animation-delay:-0.21s"/>
<polygon class="particle" points="176.8,95.6 174.8,99.7 178.8,99.7" fill="#f4f0ff" opacity="0.85" style="animation-delay:-2.92s"/>
<polygon class="particle" points="243.9,87.2 242.5,90.2 245.4,90.2" fill="#f4f0ff" opacity="0.56" style="animation-delay:-2.47s"/>
<polygon class="particle" points="243.3,160.6 241.8,163.7 244.8,163.7" fill="#f4f0ff" opacity="0.39" style="animation-delay:-2.81s"/>
<polygon class="particle" points="206.2,226.5 204.0,231.1 208.4,231.1" fill="#8052ff" opacity="0.44" style="animation-delay:-2.62s"/>
<polygon class="particle" points="236.7,42.4 234.0,48.0 239.4,48.0" fill="#8052ff" opacity="0.68" style="animation-delay:-1.48s"/>
<polygon class="particle" points="217.3,251.8 215.3,255.9 219.3,255.9" fill="#f4f0ff" opacity="0.61" style="animation-delay:-0.83s"/>
<polygon class="particle" points="209.0,79.9 207.7,82.6 210.4,82.6" fill="#46a7ff" opacity="0.64" style="animation-delay:-2.03s"/>
<polygon class="particle" points="202.8,103.0 200.6,107.6 205.1,107.6" fill="#f4f0ff" opacity="0.80" style="animation-delay:-0.19s"/>
<polygon class="particle" points="190.9,150.5 188.0,156.5 193.8,156.5" fill="#46a7ff" opacity="0.66" style="animation-delay:-0.91s"/>
<polygon class="particle" points="176.7,102.9 174.6,107.2 178.8,107.2" fill="#15846e" opacity="0.81" style="animation-delay:-2.56s"/>
<polygon class="particle" points="250.4,98.6 247.8,104.0 253.0,104.0" fill="#d04dff" opacity="0.55" style="animation-delay:-0.27s"/>
<polygon class="particle" points="193.5,113.7 192.3,116.3 194.8,116.3" fill="#8052ff" opacity="0.91" style="animation-delay:-3.85s"/>
<polygon class="particle" points="237.3,95.5 235.7,98.8 238.9,98.8" fill="#ffb829" opacity="0.91" style="animation-delay:-2.25s"/>
<polygon class="particle" points="227.7,233.1 224.4,240.0 231.0,240.0" fill="#d04dff" opacity="0.70" style="animation-delay:-3.39s"/>
<polygon class="particle" points="178.0,91.7 174.7,98.4 181.2,98.4" fill="#f4f0ff" opacity="0.70" style="animation-delay:-1.31s"/>
<polygon class="particle" points="168.6,217.8 167.3,220.6 169.9,220.6" fill="#f4f0ff" opacity="0.79" style="animation-delay:-2.60s"/>
<polygon class="particle" points="197.2,47.8 194.8,52.7 199.6,52.7" fill="#f4f0ff" opacity="0.88" style="animation-delay:-0.65s"/>
<polygon class="particle" points="247.3,88.5 244.5,94.2 250.0,94.2" fill="#8052ff" opacity="0.49" style="animation-delay:-0.35s"/>
<polygon class="particle" points="205.6,238.3 203.3,243.0 207.9,243.0" fill="#f4f0ff" opacity="0.79" style="animation-delay:-2.32s"/>
<polygon class="particle" points="222.5,117.5 220.3,122.1 224.8,122.1" fill="#46a7ff" opacity="0.51" style="animation-delay:-1.54s"/>
<polygon class="particle" points="211.4,111.5 210.3,113.8 212.5,113.8" fill="#ffb829" opacity="0.55" style="animation-delay:-1.13s"/>
<polygon class="particle" points="208.2,46.2 205.5,51.8 210.9,51.8" fill="#46a7ff" opacity="0.60" style="animation-delay:-3.05s"/>
<polygon class="particle" points="236.3,33.8 233.6,39.4 239.1,39.4" fill="#f4f0ff" opacity="0.49" style="animation-delay:-0.99s"/>
<polygon class="particle" points="220.8,254.0 219.1,257.4 222.4,257.4" fill="#f4f0ff" opacity="0.77" style="animation-delay:-3.39s"/>
<polygon class="particle" points="198.5,179.8 197.0,183.0 200.1,183.0" fill="#8052ff" opacity="0.97" style="animation-delay:-2.81s"/>
<polygon class="particle" points="202.6,52.4 199.7,58.3 205.4,58.3" fill="#f4f0ff" opacity="0.55" style="animation-delay:-3.97s"/>
<polygon class="particle" points="204.3,138.8 202.0,143.6 206.7,143.6" fill="#15846e" opacity="0.92" style="animation-delay:-0.79s"/>
<polygon class="particle" points="223.0,107.1 220.1,113.3 226.0,113.3" fill="#ffb829" opacity="0.45" style="animation-delay:-0.20s"/>
<polygon class="particle" points="222.6,219.7 220.8,223.4 224.4,223.4" fill="#46a7ff" opacity="0.61" style="animation-delay:-2.49s"/>
<polygon class="particle" points="231.1,178.0 228.3,183.6 233.8,183.6" fill="#ffb829" opacity="0.53" style="animation-delay:-0.25s"/>
<polygon class="particle" points="242.3,248.2 240.4,252.1 244.2,252.1" fill="#ffb829" opacity="0.56" style="animation-delay:-3.33s"/>
<polygon class="particle" points="205.7,115.7 202.9,121.4 208.4,121.4" fill="#8052ff" opacity="0.89" style="animation-delay:-2.59s"/>
<polygon class="particle" points="174.8,221.3 172.4,226.2 177.2,226.2" fill="#ffb829" opacity="0.54" style="animation-delay:-0.29s"/>
<polygon class="particle" points="201.0,68.8 199.3,72.3 202.7,72.3" fill="#ffb829" opacity="0.73" style="animation-delay:-0.10s"/>
<polygon class="particle" points="229.2,249.1 226.3,255.2 232.2,255.2" fill="#46a7ff" opacity="0.94" style="animation-delay:-2.24s"/>
<polygon class="particle" points="181.4,257.7 179.8,261.0 183.0,261.0" fill="#f4f0ff" opacity="0.61" style="animation-delay:-1.78s"/>
<polygon class="particle" points="222.3,132.4 219.2,138.8 225.4,138.8" fill="#ffb829" opacity="0.95" style="animation-delay:-2.61s"/>
<polygon class="particle" points="195.6,136.8 192.8,142.5 198.4,142.5" fill="#d04dff" opacity="0.66" style="animation-delay:-3.05s"/>
<polygon class="particle" points="195.5,29.7 192.6,35.8 198.4,35.8" fill="#f4f0ff" opacity="0.74" style="animation-delay:-2.71s"/>
<polygon class="particle" points="201.1,49.7 198.8,54.4 203.4,54.4" fill="#8052ff" opacity="0.59" style="animation-delay:-0.97s"/>
<polygon class="particle" points="205.9,167.4 204.7,169.8 207.0,169.8" fill="#f4f0ff" opacity="0.68" style="animation-delay:-2.08s"/>
<polygon class="particle" points="239.1,243.9 236.8,248.7 241.4,248.7" fill="#8052ff" opacity="0.57" style="animation-delay:-2.73s"/>
<polygon class="particle" points="203.9,67.5 200.6,74.3 207.2,74.3" fill="#8052ff" opacity="0.51" style="animation-delay:-0.40s"/>
<polygon class="particle" points="228.9,39.1 226.2,44.7 231.7,44.7" fill="#ff7dcb" opacity="0.91" style="animation-delay:-1.02s"/>
<polygon class="particle" points="228.4,85.6 225.4,91.7 231.4,91.7" fill="#f4f0ff" opacity="0.83" style="animation-delay:-3.17s"/>
<polygon class="particle" points="202.2,169.1 200.5,172.7 204.0,172.7" fill="#f4f0ff" opacity="0.83" style="animation-delay:-3.65s"/>
<polygon class="particle" points="249.7,80.3 247.4,84.9 251.9,84.9" fill="#f4f0ff" opacity="0.97" style="animation-delay:-3.10s"/>
<polygon class="particle" points="225.9,236.1 223.0,242.1 228.8,242.1" fill="#ffb829" opacity="0.90" style="animation-delay:-0.81s"/>
<polygon class="particle" points="254.9,142.4 252.0,148.3 257.7,148.3" fill="#f4f0ff" opacity="0.90" style="animation-delay:-0.31s"/>
<polygon class="particle" points="191.4,98.3 188.2,105.0 194.7,105.0" fill="#15846e" opacity="0.71" style="animation-delay:-0.59s"/>
<polygon class="particle" points="175.2,184.2 173.2,188.3 177.2,188.3" fill="#8052ff" opacity="0.95" style="animation-delay:-1.49s"/>
<polygon class="particle" points="220.5,101.1 217.6,107.0 223.3,107.0" fill="#15846e" opacity="0.97" style="animation-delay:-1.29s"/>
<polygon class="particle" points="183.9,77.0 181.3,82.4 186.6,82.4" fill="#f4f0ff" opacity="0.84" style="animation-delay:-1.47s"/>
<polygon class="particle" points="211.6,118.8 209.3,123.4 213.8,123.4" fill="#f4f0ff" opacity="0.39" style="animation-delay:-3.56s"/>
<polygon class="particle" points="218.4,246.2 216.2,250.9 220.7,250.9" fill="#ffb829" opacity="0.44" style="animation-delay:-1.98s"/>
<polygon class="particle" points="244.7,39.3 241.6,45.5 247.7,45.5" fill="#d04dff" opacity="0.45" style="animation-delay:-1.38s"/>
<polygon class="particle" points="202.2,236.4 201.0,238.7 203.3,238.7" fill="#f4f0ff" opacity="0.42" style="animation-delay:-2.63s"/>
<polygon class="particle" points="205.9,105.1 203.2,110.6 208.5,110.6" fill="#d04dff" opacity="0.71" style="animation-delay:-1.49s"/>
<polygon class="particle" points="189.9,195.4 186.9,201.5 192.9,201.5" fill="#46a7ff" opacity="0.54" style="animation-delay:-0.76s"/>
<polygon class="particle" points="219.7,34.7 218.2,38.0 221.3,38.0" fill="#ff7dcb" opacity="0.69" style="animation-delay:-0.85s"/>
<polygon class="particle" points="223.5,37.7 221.4,42.2 225.7,42.2" fill="#ffb829" opacity="0.50" style="animation-delay:-2.86s"/>
<polygon class="particle" points="187.6,106.5 184.6,112.6 190.5,112.6" fill="#f4f0ff" opacity="0.57" style="animation-delay:-1.69s"/>
<polygon class="particle" points="208.3,36.6 206.5,40.2 210.0,40.2" fill="#8052ff" opacity="0.71" style="animation-delay:-3.06s"/>
<polygon class="particle" points="182.3,185.5 181.1,188.0 183.5,188.0" fill="#8052ff" opacity="0.94" style="animation-delay:-3.68s"/>
<polygon class="particle" points="214.9,140.3 212.7,144.7 217.0,144.7" fill="#8052ff" opacity="0.70" style="animation-delay:-3.19s"/>
<polygon class="particle" points="197.8,155.7 194.7,161.9 200.8,161.9" fill="#ffb829" opacity="0.94" style="animation-delay:-3.91s"/>
<polygon class="particle" points="238.8,135.5 236.5,140.3 241.1,140.3" fill="#f4f0ff" opacity="0.55" style="animation-delay:-1.21s"/>
<polygon class="particle" points="192.9,171.6 190.2,177.3 195.7,177.3" fill="#46a7ff" opacity="0.74" style="animation-delay:-0.29s"/>
<polygon class="particle" points="173.0,154.3 170.1,160.4 175.9,160.4" fill="#f4f0ff" opacity="0.69" style="animation-delay:-3.49s"/>
<polygon class="particle" points="229.1,118.3 226.8,123.0 231.3,123.0" fill="#f4f0ff" opacity="0.83" style="animation-delay:-1.30s"/>
<polygon class="particle" points="216.1,117.8 214.5,121.1 217.7,121.1" fill="#ffb829" opacity="0.50" style="animation-delay:-1.15s"/>
<polygon class="particle" points="186.5,261.0 184.6,264.9 188.4,264.9" fill="#ffb829" opacity="0.78" style="animation-delay:-1.30s"/>
<polygon class="particle" points="213.6,64.5 212.4,67.0 214.9,67.0" fill="#ffb829" opacity="0.52" style="animation-delay:-0.10s"/>
<polygon class="particle" points="173.1,251.6 170.4,257.2 175.8,257.2" fill="#8052ff" opacity="0.92" style="animation-delay:-1.84s"/>
<polygon class="particle" points="222.3,97.8 219.5,103.5 225.1,103.5" fill="#8052ff" opacity="0.91" style="animation-delay:-1.20s"/>
<polygon class="particle" points="180.1,264.3 178.2,268.3 182.0,268.3" fill="#15846e" opacity="0.90" style="animation-delay:-2.40s"/>
<polygon class="particle" points="189.3,98.5 187.5,102.3 191.2,102.3" fill="#ffb829" opacity="0.89" style="animation-delay:-0.31s"/>
<polygon class="particle" points="226.1,93.1 223.5,98.6 228.8,98.6" fill="#f4f0ff" opacity="0.38" style="animation-delay:-0.53s"/>
<polygon class="particle" points="231.4,222.4 229.9,225.5 232.9,225.5" fill="#f4f0ff" opacity="0.89" style="animation-delay:-0.37s"/>
<polygon class="particle" points="173.0,160.6 171.0,164.6 175.0,164.6" fill="#ffb829" opacity="0.56" style="animation-delay:-0.66s"/>
<polygon class="particle" points="175.7,184.5 172.7,190.7 178.7,190.7" fill="#f4f0ff" opacity="0.68" style="animation-delay:-1.55s"/>
<polygon class="particle" points="247.0,263.0 243.8,269.6 250.2,269.6" fill="#ffb829" opacity="0.56" style="animation-delay:-0.47s"/>
<polygon class="particle" points="181.5,138.2 178.6,144.1 184.4,144.1" fill="#15846e" opacity="0.64" style="animation-delay:-0.20s"/>
<polygon class="particle" points="201.8,150.4 200.6,152.9 203.0,152.9" fill="#15846e" opacity="0.88" style="animation-delay:-0.67s"/>
<polygon class="particle" points="212.2,65.0 210.1,69.4 214.4,69.4" fill="#8052ff" opacity="0.59" style="animation-delay:-3.30s"/>
<polygon class="particle" points="240.4,196.6 237.4,202.7 243.4,202.7" fill="#d04dff" opacity="0.44" style="animation-delay:-1.20s"/>
<polygon class="particle" points="235.0,142.9 232.4,148.3 237.7,148.3" fill="#8052ff" opacity="0.76" style="animation-delay:-0.78s"/>
<polygon class="particle" points="239.4,150.7 237.3,155.1 241.6,155.1" fill="#ff7dcb" opacity="0.67" style="animation-delay:-2.56s"/>
<polygon class="particle" points="193.7,222.0 191.5,226.6 195.9,226.6" fill="#46a7ff" opacity="0.82" style="animation-delay:-1.81s"/>
<polygon class="particle" points="235.0,85.4 233.4,88.6 236.5,88.6" fill="#f4f0ff" opacity="0.92" style="animation-delay:-1.44s"/>
<polygon class="particle" points="166.4,151.7 164.7,155.2 168.1,155.2" fill="#d04dff" opacity="0.66" style="animation-delay:-1.48s"/>
<polygon class="particle" points="251.0,202.0 249.3,205.5 252.7,205.5" fill="#ffb829" opacity="0.43" style="animation-delay:-0.24s"/>
<polygon class="particle" points="172.7,213.1 171.4,215.7 174.0,215.7" fill="#f4f0ff" opacity="0.91" style="animation-delay:-3.08s"/>
<polygon class="particle" points="201.0,236.6 198.1,242.7 204.0,242.7" fill="#f4f0ff" opacity="0.45" style="animation-delay:-2.57s"/>
<polygon class="particle" points="238.0,207.3 235.1,213.3 240.9,213.3" fill="#15846e" opacity="0.45" style="animation-delay:-1.54s"/>
<polygon class="particle" points="214.9,100.0 211.9,106.2 217.9,106.2" fill="#ffb829" opacity="0.75" style="animation-delay:-3.57s"/>
<polygon class="particle" points="192.7,187.6 189.3,194.5 196.0,194.5" fill="#ff7dcb" opacity="0.75" style="animation-delay:-3.75s"/>
<polygon class="particle" points="166.3,143.5 164.5,147.2 168.1,147.2" fill="#ffb829" opacity="0.39" style="animation-delay:-2.19s"/>
<polygon class="particle" points="177.8,134.2 176.0,137.8 179.5,137.8" fill="#15846e" opacity="0.54" style="animation-delay:-2.06s"/>
<polygon class="particle" points="251.4,93.0 249.0,97.9 253.8,97.9" fill="#f4f0ff" opacity="0.75" style="animation-delay:-0.72s"/>
<polygon class="particle" points="207.6,50.9 204.9,56.4 210.2,56.4" fill="#46a7ff" opacity="0.88" style="animation-delay:-0.59s"/>
<polygon class="particle" points="203.9,43.9 201.6,48.6 206.1,48.6" fill="#46a7ff" opacity="0.69" style="animation-delay:-0.84s"/>
<polygon class="particle" points="234.0,72.8 231.1,78.9 237.0,78.9" fill="#d04dff" opacity="0.40" style="animation-delay:-2.66s"/>
<polygon class="particle" points="217.7,64.6 216.3,67.4 219.1,67.4" fill="#ff7dcb" opacity="0.96" style="animation-delay:-0.71s"/>
<polygon class="particle" points="249.0,211.2 246.0,217.4 252.0,217.4" fill="#46a7ff" opacity="0.40" style="animation-delay:-0.95s"/>
<polygon class="particle" points="179.6,137.2 176.6,143.3 182.5,143.3" fill="#46a7ff" opacity="0.69" style="animation-delay:-3.55s"/>
<polygon class="particle" points="207.4,106.3 205.6,110.1 209.3,110.1" fill="#f4f0ff" opacity="0.92" style="animation-delay:-2.77s"/>
<polygon class="particle" points="184.7,257.3 182.5,261.8 186.9,261.8" fill="#ff7dcb" opacity="0.55" style="animation-delay:-3.27s"/>
<polygon class="particle" points="230.0,251.4 228.2,255.0 231.7,255.0" fill="#f4f0ff" opacity="0.64" style="animation-delay:-1.56s"/>
<polygon class="particle" points="180.8,191.4 178.4,196.5 183.3,196.5" fill="#d04dff" opacity="0.59" style="animation-delay:-2.65s"/>
<polygon class="particle" points="186.2,73.1 183.8,78.0 188.6,78.0" fill="#f4f0ff" opacity="0.39" style="animation-delay:-2.50s"/>
<polygon class="particle" points="168.4,83.7 167.0,86.6 169.9,86.6" fill="#ffb829" opacity="0.85" style="animation-delay:-2.42s"/>
<polygon class="particle" points="235.5,128.4 234.0,131.6 237.0,131.6" fill="#46a7ff" opacity="0.88" style="animation-delay:-3.75s"/>
<polygon class="particle" points="202.0,201.3 199.0,207.5 205.0,207.5" fill="#f4f0ff" opacity="0.56" style="animation-delay:-1.08s"/>
<polygon class="particle" points="182.2,223.2 179.5,228.8 184.9,228.8" fill="#15846e" opacity="0.46" style="animation-delay:-1.79s"/>
<polygon class="particle" points="190.7,95.9 189.1,99.3 192.4,99.3" fill="#f4f0ff" opacity="0.60" style="animation-delay:-2.63s"/>
<polygon class="particle" points="175.9,62.7 173.5,67.5 178.2,67.5" fill="#f4f0ff" opacity="0.86" style="animation-delay:-2.75s"/>
<polygon class="particle" points="216.7,43.1 215.2,46.2 218.2,46.2" fill="#f4f0ff" opacity="0.56" style="animation-delay:-0.17s"/>
<polygon class="particle" points="215.6,132.1 213.3,136.7 217.8,136.7" fill="#d04dff" opacity="0.56" style="animation-delay:-2.49s"/>
<polygon class="particle" points="210.2,161.7 208.4,165.4 212.0,165.4" fill="#f4f0ff" opacity="0.71" style="animation-delay:-1.04s"/>
<polygon class="particle" points="209.2,161.0 206.1,167.4 212.4,167.4" fill="#ffb829" opacity="0.87" style="animation-delay:-2.70s"/>
<polygon class="particle" points="170.9,77.4 169.6,80.0 172.2,80.0" fill="#f4f0ff" opacity="0.75" style="animation-delay:-3.37s"/>
<polygon class="particle" points="178.2,66.1 175.8,71.1 180.7,71.1" fill="#46a7ff" opacity="0.73" style="animation-delay:-0.65s"/>
<polygon class="particle" points="239.0,190.0 236.0,196.3 242.1,196.3" fill="#8052ff" opacity="0.59" style="animation-delay:-3.56s"/>
<polygon class="particle" points="216.6,165.0 215.0,168.4 218.2,168.4" fill="#ff7dcb" opacity="0.60" style="animation-delay:-1.04s"/>
<polygon class="particle" points="199.2,145.9 197.8,148.7 200.5,148.7" fill="#ff7dcb" opacity="0.61" style="animation-delay:-3.81s"/>
<polygon class="particle" points="207.1,90.0 204.3,95.7 209.8,95.7" fill="#f4f0ff" opacity="0.66" style="animation-delay:-0.81s"/>
<polygon class="particle" points="191.2,241.4 188.0,248.0 194.4,248.0" fill="#f4f0ff" opacity="0.79" style="animation-delay:-0.91s"/>
<polygon class="particle" points="246.6,170.1 244.5,174.5 248.8,174.5" fill="#f4f0ff" opacity="0.94" style="animation-delay:-1.00s"/>
<polygon class="particle" points="219.0,164.2 217.2,167.9 220.8,167.9" fill="#8052ff" opacity="0.59" style="animation-delay:-1.51s"/>
<polygon class="particle" points="183.5,70.6 181.9,73.8 185.0,73.8" fill="#ffb829" opacity="0.92" style="animation-delay:-1.27s"/>
<polygon class="particle" points="184.8,177.1 182.4,182.1 187.3,182.1" fill="#d04dff" opacity="0.38" style="animation-delay:-0.10s"/>
<polygon class="particle" points="197.6,122.1 195.8,125.8 199.4,125.8" fill="#d04dff" opacity="0.71" style="animation-delay:-3.41s"/>
<polygon class="particle" points="211.3,172.2 209.5,175.9 213.0,175.9" fill="#15846e" opacity="0.42" style="animation-delay:-3.85s"/>
<polygon class="particle" points="198.1,41.7 195.7,46.6 200.4,46.6" fill="#46a7ff" opacity="0.63" style="animation-delay:-3.81s"/>
<polygon class="particle" points="217.3,161.5 214.6,167.2 220.1,167.2" fill="#f4f0ff" opacity="0.58" style="animation-delay:-1.36s"/>
<polygon class="particle" points="194.2,161.0 192.0,165.6 196.5,165.6" fill="#ff7dcb" opacity="0.83" style="animation-delay:-3.15s"/>
<polygon class="particle" points="218.5,255.5 216.2,260.1 220.8,260.1" fill="#15846e" opacity="0.91" style="animation-delay:-2.32s"/>
<polygon class="particle" points="204.4,117.2 201.2,123.8 207.5,123.8" fill="#f4f0ff" opacity="0.88" style="animation-delay:-3.61s"/>
<polygon class="particle" points="240.5,66.0 238.4,70.3 242.5,70.3" fill="#46a7ff" opacity="0.84" style="animation-delay:-0.99s"/>
<polygon class="particle" points="216.0,222.1 214.6,225.0 217.4,225.0" fill="#d04dff" opacity="0.42" style="animation-delay:-0.07s"/>
<polygon class="particle" points="196.6,104.4 193.7,110.3 199.4,110.3" fill="#8052ff" opacity="0.85" style="animation-delay:-3.02s"/>
<polygon class="particle" points="220.9,89.1 218.8,93.5 223.1,93.5" fill="#ffb829" opacity="0.53" style="animation-delay:-1.91s"/>
<polygon class="particle" points="213.6,188.7 210.5,195.2 216.7,195.2" fill="#15846e" opacity="0.54" style="animation-delay:-1.82s"/>
<polygon class="particle" points="195.0,81.0 193.1,85.0 197.0,85.0" fill="#46a7ff" opacity="0.39" style="animation-delay:-2.18s"/>
<polygon class="particle" points="235.7,169.0 233.3,173.9 238.1,173.9" fill="#ffb829" opacity="0.46" style="animation-delay:-2.75s"/>
<polygon class="particle" points="173.5,143.9 172.0,147.1 175.1,147.1" fill="#ffb829" opacity="0.73" style="animation-delay:-0.37s"/>
<polygon class="particle" points="217.6,112.8 215.5,117.2 219.7,117.2" fill="#8052ff" opacity="0.39" style="animation-delay:-2.52s"/>
<polygon class="particle" points="238.1,219.8 236.8,222.5 239.4,222.5" fill="#8052ff" opacity="0.46" style="animation-delay:-3.16s"/>
<polygon class="particle" points="234.4,134.4 231.2,140.9 237.5,140.9" fill="#8052ff" opacity="0.52" style="animation-delay:-1.11s"/>
<polygon class="particle" points="225.8,43.6 224.0,47.3 227.6,47.3" fill="#8052ff" opacity="0.51" style="animation-delay:-2.60s"/>
<polygon class="particle" points="241.5,99.3 240.1,102.4 243.0,102.4" fill="#d04dff" opacity="0.77" style="animation-delay:-0.59s"/>
<polygon class="particle" points="242.5,105.7 240.3,110.2 244.8,110.2" fill="#f4f0ff" opacity="0.92" style="animation-delay:-1.42s"/>
<polygon class="particle" points="189.9,192.4 187.0,198.3 192.8,198.3" fill="#15846e" opacity="0.58" style="animation-delay:-0.52s"/>
<polygon class="particle" points="177.1,263.6 175.5,266.8 178.7,266.8" fill="#46a7ff" opacity="0.50" style="animation-delay:-1.69s"/>
<polygon class="particle" points="188.3,167.7 186.0,172.6 190.6,172.6" fill="#d04dff" opacity="0.40" style="animation-delay:-0.43s"/>
<polygon class="particle" points="183.8,132.1 181.0,138.0 186.7,138.0" fill="#ffb829" opacity="0.87" style="animation-delay:-3.16s"/>
<polygon class="particle" points="236.2,127.1 234.2,131.1 238.1,131.1" fill="#ffb829" opacity="0.52" style="animation-delay:-2.10s"/>
<polygon class="particle" points="208.4,163.0 205.9,168.2 211.0,168.2" fill="#46a7ff" opacity="0.86" style="animation-delay:-0.42s"/>
<polygon class="particle" points="203.9,237.2 201.4,242.4 206.4,242.4" fill="#d04dff" opacity="0.51" style="animation-delay:-1.85s"/>
<polygon class="particle" points="189.8,68.3 187.6,72.9 192.1,72.9" fill="#ffb829" opacity="0.69" style="animation-delay:-1.71s"/>
<polygon class="particle" points="172.4,179.9 169.9,185.0 174.9,185.0" fill="#f4f0ff" opacity="0.66" style="animation-delay:-2.22s"/>
<polygon class="particle" points="184.8,251.7 182.7,255.9 186.8,255.9" fill="#ffb829" opacity="0.89" style="animation-delay:-1.26s"/>
<polygon class="particle" points="165.8,172.5 164.0,176.1 167.5,176.1" fill="#ff7dcb" opacity="0.54" style="animation-delay:-1.33s"/>
<polygon class="particle" points="245.6,248.1 242.6,254.2 248.5,254.2" fill="#f4f0ff" opacity="0.54" style="animation-delay:-3.34s"/>
<polygon class="particle" points="187.4,70.9 186.0,73.9 188.9,73.9" fill="#ffb829" opacity="0.67" style="animation-delay:-1.52s"/>
<polygon class="particle" points="209.3,93.4 206.4,99.3 212.1,99.3" fill="#15846e" opacity="0.81" style="animation-delay:-2.65s"/>
<polygon class="particle" points="236.9,35.8 233.8,42.1 239.9,42.1" fill="#d04dff" opacity="0.98" style="animation-delay:-3.26s"/>
<polygon class="particle" points="243.7,44.5 242.2,47.4 245.1,47.4" fill="#ffb829" opacity="0.76" style="animation-delay:-3.16s"/>
<polygon class="particle" points="180.8,47.5 179.4,50.3 182.1,50.3" fill="#8052ff" opacity="0.74" style="animation-delay:-3.59s"/>
<polygon class="particle" points="181.6,245.2 179.5,249.7 183.8,249.7" fill="#ffb829" opacity="0.80" style="animation-delay:-2.02s"/>
<polygon class="particle" points="205.7,93.1 202.8,99.1 208.6,99.1" fill="#8052ff" opacity="0.53" style="animation-delay:-3.44s"/>
<polygon class="particle" points="239.5,133.6 237.7,137.3 241.3,137.3" fill="#8052ff" opacity="0.62" style="animation-delay:-0.89s"/>
<polygon class="particle" points="245.9,186.7 243.9,190.7 247.8,190.7" fill="#f4f0ff" opacity="0.89" style="animation-delay:-2.64s"/>
<polygon class="particle" points="182.9,176.3 179.9,182.6 186.0,182.6" fill="#f4f0ff" opacity="0.60" style="animation-delay:-0.90s"/>
<polygon class="particle" points="174.0,40.9 172.0,45.1 176.1,45.1" fill="#8052ff" opacity="0.87" style="animation-delay:-0.66s"/>
<polygon class="particle" points="252.1,227.4 249.0,233.8 255.1,233.8" fill="#f4f0ff" opacity="0.67" style="animation-delay:-3.71s"/>
<polygon class="particle" points="207.1,130.8 204.8,135.5 209.4,135.5" fill="#8052ff" opacity="0.42" style="animation-delay:-2.33s"/>
<polygon class="particle" points="207.4,233.5 205.3,237.7 209.4,237.7" fill="#15846e" opacity="0.74" style="animation-delay:-1.06s"/>
<polygon class="particle" points="167.4,93.1 165.4,97.1 169.3,97.1" fill="#8052ff" opacity="0.46" style="animation-delay:-2.46s"/>
<polygon class="particle" points="171.0,168.6 169.2,172.4 172.8,172.4" fill="#ff7dcb" opacity="0.95" style="animation-delay:-1.50s"/>
<polygon class="particle" points="224.2,205.1 222.7,208.2 225.7,208.2" fill="#46a7ff" opacity="0.79" style="animation-delay:-1.49s"/>
<polygon class="particle" points="224.3,228.7 221.2,235.2 227.4,235.2" fill="#f4f0ff" opacity="0.90" style="animation-delay:-0.53s"/>
<polygon class="particle" points="198.4,241.6 195.9,246.8 200.9,246.8" fill="#f4f0ff" opacity="0.90" style="animation-delay:-1.51s"/>
<polygon class="particle" points="209.4,33.0 207.5,36.9 211.3,36.9" fill="#46a7ff" opacity="0.98" style="animation-delay:-1.08s"/>
<polygon class="particle" points="191.7,206.1 188.9,212.0 194.5,212.0" fill="#8052ff" opacity="0.61" style="animation-delay:-1.38s"/>
<polygon class="particle" points="239.6,121.0 237.9,124.5 241.3,124.5" fill="#f4f0ff" opacity="0.76" style="animation-delay:-0.26s"/>
<polygon class="particle" points="244.1,184.6 241.8,189.4 246.5,189.4" fill="#46a7ff" opacity="0.96" style="animation-delay:-2.52s"/>
<polygon class="particle" points="182.4,184.4 179.4,190.5 185.4,190.5" fill="#ffb829" opacity="0.91" style="animation-delay:-3.84s"/>
<polygon class="particle" points="173.2,183.4 170.2,189.6 176.2,189.6" fill="#f4f0ff" opacity="0.73" style="animation-delay:-2.75s"/>
<polygon class="particle" points="227.5,96.4 224.2,103.1 230.7,103.1" fill="#f4f0ff" opacity="0.71" style="animation-delay:-3.39s"/>
<polygon class="particle" points="216.9,108.5 214.6,113.3 219.2,113.3" fill="#ffb829" opacity="0.42" style="animation-delay:-1.48s"/>
<polygon class="particle" points="195.9,257.0 194.0,261.0 197.8,261.0" fill="#ffb829" opacity="0.50" style="animation-delay:-2.19s"/>
<polygon class="particle" points="236.1,102.9 233.3,108.6 238.8,108.6" fill="#d04dff" opacity="0.81" style="animation-delay:-0.57s"/>
<polygon class="particle" points="184.5,230.1 183.0,233.2 186.0,233.2" fill="#46a7ff" opacity="0.40" style="animation-delay:-3.58s"/>
<polygon class="particle" points="190.9,51.4 189.7,54.0 192.1,54.0" fill="#46a7ff" opacity="0.59" style="animation-delay:-0.90s"/>
<polygon class="particle" points="214.6,47.2 213.3,50.0 216.0,50.0" fill="#f4f0ff" opacity="0.59" style="animation-delay:-1.30s"/>
<polygon class="particle" points="203.7,209.0 201.7,212.9 205.6,212.9" fill="#ffb829" opacity="0.66" style="animation-delay:-1.93s"/>
<polygon class="particle" points="168.2,111.3 165.0,117.8 171.4,117.8" fill="#15846e" opacity="0.93" style="animation-delay:-3.95s"/>
<polygon class="particle" points="246.4,132.5 243.8,137.8 249.0,137.8" fill="#ffb829" opacity="0.40" style="animation-delay:-0.74s"/>
<polygon class="particle" points="246.7,51.9 244.4,56.7 249.1,56.7" fill="#46a7ff" opacity="0.74" style="animation-delay:-0.98s"/>
<polygon class="particle" points="189.6,238.8 187.8,242.5 191.4,242.5" fill="#8052ff" opacity="0.85" style="animation-delay:-0.41s"/>
<polygon class="particle" points="251.6,174.9 249.9,178.4 253.3,178.4" fill="#8052ff" opacity="0.60" style="animation-delay:-1.47s"/>
<polygon class="particle" points="196.8,206.1 194.4,211.2 199.3,211.2" fill="#f4f0ff" opacity="0.77" style="animation-delay:-2.67s"/>
<polygon class="particle" points="210.3,230.5 207.1,237.1 213.5,237.1" fill="#46a7ff" opacity="0.63" style="animation-delay:-0.18s"/>
<polygon class="particle" points="186.4,89.6 184.0,94.5 188.7,94.5" fill="#ffb829" opacity="0.84" style="animation-delay:-3.30s"/>
<polygon class="particle" points="218.3,115.4 217.0,118.2 219.7,118.2" fill="#8052ff" opacity="0.46" style="animation-delay:-2.94s"/>
<polygon class="particle" points="172.8,71.9 170.2,77.3 175.4,77.3" fill="#8052ff" opacity="0.41" style="animation-delay:-2.63s"/>
<polygon class="particle" points="169.3,139.9 166.7,145.3 171.9,145.3" fill="#15846e" opacity="0.73" style="animation-delay:-2.26s"/>
<polygon class="particle" points="171.8,212.7 170.1,216.2 173.5,216.2" fill="#8052ff" opacity="0.83" style="animation-delay:-1.70s"/>
<polygon class="particle" points="247.4,210.4 245.8,213.7 249.0,213.7" fill="#f4f0ff" opacity="0.63" style="animation-delay:-2.13s"/>
<polygon class="particle" points="248.1,149.9 246.0,154.1 250.1,154.1" fill="#d04dff" opacity="0.93" style="animation-delay:-0.29s"/>
<polygon class="particle" points="182.0,155.4 179.7,160.2 184.4,160.2" fill="#8052ff" opacity="0.52" style="animation-delay:-0.41s"/>
<polygon class="particle" points="187.4,239.8 184.3,246.3 190.5,246.3" fill="#8052ff" opacity="0.75" style="animation-delay:-3.48s"/>
<polygon class="particle" points="185.9,78.0 184.0,82.0 187.9,82.0" fill="#ffb829" opacity="0.45" style="animation-delay:-3.42s"/>
<polygon class="particle" points="222.9,264.7 221.7,267.3 224.2,267.3" fill="#ffb829" opacity="0.40" style="animation-delay:-0.68s"/>
<polygon class="particle" points="178.8,199.3 175.5,206.0 182.0,206.0" fill="#8052ff" opacity="0.83" style="animation-delay:-3.43s"/>
<polygon class="particle" points="178.0,197.0 176.1,201.0 179.9,201.0" fill="#8052ff" opacity="0.91" style="animation-delay:-0.01s"/>
<polygon class="particle" points="199.5,156.4 197.7,160.1 201.3,160.1" fill="#15846e" opacity="0.70" style="animation-delay:-0.96s"/>
<polygon class="particle" points="171.1,168.6 169.9,171.2 172.3,171.2" fill="#15846e" opacity="0.53" style="animation-delay:-3.30s"/>
<polygon class="particle" points="242.0,121.1 239.2,126.9 244.9,126.9" fill="#f4f0ff" opacity="0.68" style="animation-delay:-3.27s"/>
<polygon class="particle" points="173.5,89.1 170.2,96.0 176.9,96.0" fill="#8052ff" opacity="0.54" style="animation-delay:-2.22s"/>
<polygon class="particle" points="188.0,62.2 185.1,68.2 190.9,68.2" fill="#46a7ff" opacity="0.38" style="animation-delay:-2.26s"/>
<polygon class="particle" points="193.3,216.1 190.6,221.6 195.9,221.6" fill="#46a7ff" opacity="0.48" style="animation-delay:-3.55s"/>
<polygon class="particle" points="217.0,186.4 214.1,192.3 219.9,192.3" fill="#8052ff" opacity="0.50" style="animation-delay:-2.55s"/>
<polygon class="particle" points="174.3,152.1 173.1,154.6 175.6,154.6" fill="#d04dff" opacity="0.82" style="animation-delay:-1.44s"/>
<polygon class="particle" points="221.8,251.6 220.3,254.8 223.3,254.8" fill="#d04dff" opacity="0.67" style="animation-delay:-1.85s"/>
<polygon class="particle" points="179.4,177.0 177.1,181.9 181.8,181.9" fill="#d04dff" opacity="0.45" style="animation-delay:-3.53s"/>
<polygon class="particle" points="234.5,151.4 231.3,158.0 237.6,158.0" fill="#46a7ff" opacity="0.83" style="animation-delay:-2.25s"/>
<polygon class="particle" points="171.0,73.7 169.2,77.5 172.9,77.5" fill="#d04dff" opacity="0.68" style="animation-delay:-0.83s"/>
<polygon class="particle" points="184.0,165.0 182.5,168.1 185.5,168.1" fill="#d04dff" opacity="0.64" style="animation-delay:-1.62s"/>
<polygon class="particle" points="228.0,31.1 226.1,35.0 229.9,35.0" fill="#15846e" opacity="0.86" style="animation-delay:-1.70s"/>
<polygon class="particle" points="185.2,30.2 182.1,36.7 188.4,36.7" fill="#f4f0ff" opacity="0.88" style="animation-delay:-2.16s"/>
<polygon class="particle" points="181.2,261.5 177.9,268.3 184.5,268.3" fill="#f4f0ff" opacity="0.87" style="animation-delay:-3.75s"/>
<polygon class="particle" points="187.9,52.0 185.0,58.0 190.9,58.0" fill="#d04dff" opacity="0.69" style="animation-delay:-1.15s"/>
<polygon class="particle" points="217.5,89.3 216.0,92.3 218.9,92.3" fill="#ffb829" opacity="0.78" style="animation-delay:-1.30s"/>
<polygon class="particle" points="247.8,124.1 245.1,129.6 250.4,129.6" fill="#ff7dcb" opacity="0.87" style="animation-delay:-3.77s"/>
<polygon class="particle" points="196.9,42.0 194.2,47.6 199.6,47.6" fill="#f4f0ff" opacity="0.90" style="animation-delay:-2.17s"/>
<polygon class="particle" points="243.1,230.4 241.7,233.3 244.5,233.3" fill="#15846e" opacity="0.40" style="animation-delay:-1.91s"/>
<polygon class="particle" points="187.7,98.6 184.5,105.2 190.9,105.2" fill="#8052ff" opacity="0.82" style="animation-delay:-0.91s"/>
<polygon class="particle" points="229.9,182.8 228.6,185.5 231.2,185.5" fill="#8052ff" opacity="0.73" style="animation-delay:-3.21s"/>
<polygon class="particle" points="230.5,107.1 227.4,113.4 233.5,113.4" fill="#f4f0ff" opacity="0.67" style="animation-delay:-1.35s"/>
<polygon class="particle" points="228.0,154.0 226.5,157.0 229.5,157.0" fill="#ffb829" opacity="0.47" style="animation-delay:-1.19s"/>
<polygon class="particle" points="222.8,147.4 219.5,154.1 226.0,154.1" fill="#46a7ff" opacity="0.46" style="animation-delay:-1.45s"/>
<polygon class="particle" points="239.7,211.4 238.4,214.1 241.0,214.1" fill="#f4f0ff" opacity="0.75" style="animation-delay:-3.41s"/>
<polygon class="particle" points="222.0,183.2 218.8,189.8 225.2,189.8" fill="#ffb829" opacity="0.65" style="animation-delay:-2.09s"/>
<polygon class="particle" points="232.7,168.7 230.8,172.7 234.6,172.7" fill="#8052ff" opacity="0.81" style="animation-delay:-3.39s"/>
<polygon class="particle" points="246.0,121.5 244.6,124.4 247.4,124.4" fill="#f4f0ff" opacity="0.86" style="animation-delay:-0.74s"/>
<polygon class="particle" points="239.6,109.2 236.3,116.1 242.9,116.1" fill="#d04dff" opacity="0.98" style="animation-delay:-0.92s"/>
<polygon class="particle" points="199.2,161.6 197.4,165.3 200.9,165.3" fill="#ffb829" opacity="0.52" style="animation-delay:-0.29s"/>
<polygon class="particle" points="205.1,153.8 202.0,160.3 208.3,160.3" fill="#d04dff" opacity="0.39" style="animation-delay:-0.40s"/>
<polygon class="particle" points="222.5,210.1 220.7,213.8 224.3,213.8" fill="#f4f0ff" opacity="0.51" style="animation-delay:-1.86s"/>
<polygon class="particle" points="187.1,124.6 184.0,130.9 190.1,130.9" fill="#d04dff" opacity="0.70" style="animation-delay:-0.02s"/>
<polygon class="particle" points="178.2,191.2 177.0,193.8 179.5,193.8" fill="#8052ff" opacity="0.47" style="animation-delay:-1.30s"/>
<polygon class="particle" points="203.0,216.0 199.9,222.6 206.2,222.6" fill="#15846e" opacity="0.74" style="animation-delay:-2.74s"/>
<polygon class="particle" points="203.2,133.9 201.2,138.0 205.2,138.0" fill="#f4f0ff" opacity="0.88" style="animation-delay:-0.91s"/>
<polygon class="particle" points="227.3,235.7 224.2,242.0 230.3,242.0" fill="#f4f0ff" opacity="0.55" style="animation-delay:-3.03s"/>
<polygon class="particle" points="234.8,76.2 232.0,82.0 237.6,82.0" fill="#f4f0ff" opacity="0.96" style="animation-delay:-3.09s"/>
<polygon class="particle" points="230.9,150.5 228.1,156.3 233.7,156.3" fill="#f4f0ff" opacity="0.90" style="animation-delay:-1.71s"/>
<polygon class="particle" points="185.2,240.4 183.4,244.2 187.1,244.2" fill="#ff7dcb" opacity="0.95" style="animation-delay:-0.47s"/>
<polygon class="particle" points="176.8,158.8 175.0,162.5 178.5,162.5" fill="#f4f0ff" opacity="0.91" style="animation-delay:-1.39s"/>
<polygon class="particle" points="231.0,236.9 228.7,241.7 233.3,241.7" fill="#f4f0ff" opacity="0.87" style="animation-delay:-0.91s"/>
<polygon class="particle" points="190.1,198.5 188.7,201.4 191.5,201.4" fill="#8052ff" opacity="0.59" style="animation-delay:-1.66s"/>
<polygon class="particle" points="218.7,91.0 215.7,97.2 221.7,97.2" fill="#ffb829" opacity="0.48" style="animation-delay:-2.91s"/>
<polygon class="particle" points="186.7,39.2 183.6,45.6 189.8,45.6" fill="#f4f0ff" opacity="0.63" style="animation-delay:-1.34s"/>
<polygon class="particle" points="170.3,262.1 168.8,265.2 171.8,265.2" fill="#8052ff" opacity="0.50" style="animation-delay:-3.75s"/>
<polygon class="particle" points="250.4,163.1 247.6,169.0 253.3,169.0" fill="#d04dff" opacity="0.86" style="animation-delay:-2.19s"/>
<polygon class="particle" points="249.9,127.8 248.5,130.5 251.2,130.5" fill="#ffb829" opacity="0.81" style="animation-delay:-3.70s"/>
<polygon class="particle" points="250.4,134.1 247.5,139.9 253.2,139.9" fill="#f4f0ff" opacity="0.50" style="animation-delay:-2.97s"/>
<polygon class="particle" points="172.0,220.9 170.2,224.7 173.9,224.7" fill="#ffb829" opacity="0.61" style="animation-delay:-2.85s"/>
<polygon class="particle" points="201.8,223.3 200.1,226.8 203.5,226.8" fill="#15846e" opacity="0.60" style="animation-delay:-1.73s"/>
<polygon class="particle" points="174.1,51.4 170.9,58.2 177.4,58.2" fill="#d04dff" opacity="0.40" style="animation-delay:-3.59s"/>
<polygon class="particle" points="185.2,128.4 183.3,132.3 187.0,132.3" fill="#ffb829" opacity="0.41" style="animation-delay:-1.19s"/>
<polygon class="particle" points="219.5,131.6 218.0,134.6 220.9,134.6" fill="#ffb829" opacity="0.86" style="animation-delay:-0.60s"/>
<polygon class="particle" points="220.2,219.3 217.3,225.3 223.1,225.3" fill="#f4f0ff" opacity="0.67" style="animation-delay:-0.29s"/>
<polygon class="particle" points="232.7,204.5 229.8,210.5 235.7,210.5" fill="#46a7ff" opacity="0.62" style="animation-delay:-2.04s"/>
<polygon class="particle" points="241.8,100.4 240.4,103.5 243.3,103.5" fill="#8052ff" opacity="0.83" style="animation-delay:-3.41s"/>
<polygon class="particle" points="198.4,52.5 196.0,57.3 200.8,57.3" fill="#d04dff" opacity="0.40" style="animation-delay:-3.62s"/>
<polygon class="particle" points="231.6,209.4 230.3,212.1 232.9,212.1" fill="#f4f0ff" opacity="0.59" style="animation-delay:-2.38s"/>
<polygon class="particle" points="195.7,240.8 193.1,246.2 198.3,246.2" fill="#ffb829" opacity="0.60" style="animation-delay:-3.59s"/>
<polygon class="particle" points="195.5,155.1 192.3,161.6 198.6,161.6" fill="#46a7ff" opacity="0.92" style="animation-delay:-0.56s"/>
<polygon class="particle" points="253.3,128.4 250.5,134.2 256.1,134.2" fill="#15846e" opacity="0.78" style="animation-delay:-3.66s"/>
<polygon class="particle" points="217.4,169.3 214.4,175.4 220.3,175.4" fill="#8052ff" opacity="0.44" style="animation-delay:-2.85s"/>
<polygon class="particle" points="191.8,188.7 189.2,194.0 194.4,194.0" fill="#f4f0ff" opacity="0.78" style="animation-delay:-2.07s"/>
<polygon class="particle" points="180.1,241.3 178.5,244.4 181.6,244.4" fill="#15846e" opacity="0.93" style="animation-delay:-0.29s"/>
<polygon class="particle" points="238.8,170.8 237.0,174.6 240.6,174.6" fill="#46a7ff" opacity="0.60" style="animation-delay:-1.99s"/>
<polygon class="particle" points="251.5,183.5 249.5,187.8 253.6,187.8" fill="#ffb829" opacity="0.98" style="animation-delay:-2.01s"/>
<polygon class="particle" points="183.5,140.0 181.9,143.4 185.2,143.4" fill="#ffb829" opacity="0.83" style="animation-delay:-3.04s"/>
<polygon class="particle" points="248.6,238.2 245.7,244.1 251.5,244.1" fill="#f4f0ff" opacity="0.96" style="animation-delay:-0.89s"/>
<polygon class="particle" points="181.9,179.1 179.1,184.9 184.7,184.9" fill="#f4f0ff" opacity="0.47" style="animation-delay:-2.60s"/>
<polygon class="particle" points="197.6,154.5 194.9,160.2 200.4,160.2" fill="#8052ff" opacity="0.80" style="animation-delay:-1.37s"/>
<polygon class="particle" points="197.2,179.9 195.7,182.9 198.6,182.9" fill="#d04dff" opacity="0.81" style="animation-delay:-0.33s"/>
<polygon class="particle" points="215.8,237.5 213.2,243.0 218.5,243.0" fill="#15846e" opacity="0.81" style="animation-delay:-2.88s"/>
<polygon class="particle" points="200.7,196.9 198.0,202.4 203.3,202.4" fill="#8052ff" opacity="0.64" style="animation-delay:-3.72s"/>
<polygon class="particle" points="251.3,242.2 250.1,244.7 252.6,244.7" fill="#8052ff" opacity="0.55" style="animation-delay:-1.54s"/>
<polygon class="particle" points="197.4,95.9 194.5,101.8 200.3,101.8" fill="#ffb829" opacity="0.88" style="animation-delay:-2.49s"/>
<polygon class="particle" points="199.3,221.2 196.0,228.0 202.6,228.0" fill="#8052ff" opacity="0.43" style="animation-delay:-1.59s"/>
<polygon class="particle" points="190.7,210.9 188.7,214.9 192.6,214.9" fill="#ff7dcb" opacity="0.71" style="animation-delay:-1.29s"/>
<polygon class="particle" points="204.4,33.9 202.0,39.0 206.9,39.0" fill="#f4f0ff" opacity="0.90" style="animation-delay:-0.09s"/>
<polygon class="particle" points="206.5,239.2 204.0,244.3 209.0,244.3" fill="#f4f0ff" opacity="0.75" style="animation-delay:-3.48s"/>
<polygon class="particle" points="199.0,81.0 196.6,86.0 201.5,86.0" fill="#ffb829" opacity="0.70" style="animation-delay:-0.45s"/>
<polygon class="particle" points="207.0,37.9 204.0,43.9 209.9,43.9" fill="#f4f0ff" opacity="0.80" style="animation-delay:-3.20s"/>
<polygon class="particle" points="203.9,248.1 200.7,254.8 207.2,254.8" fill="#ffb829" opacity="0.48" style="animation-delay:-1.27s"/>
<polygon class="particle" points="201.9,138.7 198.9,144.9 205.0,144.9" fill="#46a7ff" opacity="0.38" style="animation-delay:-3.01s"/>
<polygon class="particle" points="181.3,222.7 179.9,225.5 182.6,225.5" fill="#ffb829" opacity="0.50" style="animation-delay:-3.35s"/>
<polygon class="particle" points="230.9,148.8 228.7,153.3 233.1,153.3" fill="#f4f0ff" opacity="0.73" style="animation-delay:-0.87s"/>
<polygon class="particle" points="241.9,71.7 240.7,74.3 243.1,74.3" fill="#f4f0ff" opacity="0.55" style="animation-delay:-3.44s"/>
<polygon class="particle" points="210.5,202.9 208.9,206.1 212.1,206.1" fill="#8052ff" opacity="0.64" style="animation-delay:-1.10s"/>
<polygon class="particle" points="168.6,228.7 166.2,233.8 171.1,233.8" fill="#8052ff" opacity="0.86" style="animation-delay:-0.72s"/>
<polygon class="particle" points="252.7,218.2 249.5,224.7 255.8,224.7" fill="#ffb829" opacity="0.66" style="animation-delay:-2.66s"/>
<polygon class="particle" points="173.1,151.2 171.6,154.3 174.6,154.3" fill="#8052ff" opacity="0.54" style="animation-delay:-1.44s"/>
<polygon class="particle" points="240.7,221.7 237.7,227.8 243.7,227.8" fill="#d04dff" opacity="0.71" style="animation-delay:-1.70s"/>
<polygon class="particle" points="196.9,57.7 195.7,60.3 198.2,60.3" fill="#8052ff" opacity="0.80" style="animation-delay:-2.49s"/>
<polygon class="particle" points="214.5,134.4 211.9,139.7 217.1,139.7" fill="#46a7ff" opacity="0.57" style="animation-delay:-1.02s"/>
<polygon class="particle" points="239.8,118.4 236.5,125.2 243.1,125.2" fill="#8052ff" opacity="0.66" style="animation-delay:-1.52s"/>
<polygon class="particle" points="253.4,192.2 251.8,195.4 254.9,195.4" fill="#15846e" opacity="0.84" style="animation-delay:-2.90s"/>
<polygon class="particle" points="219.8,225.3 216.5,232.2 223.2,232.2" fill="#f4f0ff" opacity="0.89" style="animation-delay:-0.47s"/>
<polygon class="particle" points="218.9,212.1 215.7,218.9 222.2,218.9" fill="#ffb829" opacity="0.44" style="animation-delay:-0.62s"/>
<polygon class="particle" points="234.3,132.5 232.1,137.0 236.5,137.0" fill="#8052ff" opacity="0.80" style="animation-delay:-3.25s"/>
<polygon class="particle" points="166.7,210.8 164.7,215.0 168.7,215.0" fill="#d04dff" opacity="0.94" style="animation-delay:-1.07s"/>
<polygon class="particle" points="231.2,205.5 227.9,212.4 234.6,212.4" fill="#f4f0ff" opacity="0.79" style="animation-delay:-3.89s"/>
<polygon class="particle" points="244.3,170.8 241.2,177.3 247.5,177.3" fill="#15846e" opacity="0.98" style="animation-delay:-2.37s"/>
<polygon class="particle" points="184.8,176.7 183.6,179.1 186.0,179.1" fill="#ffb829" opacity="0.72" style="animation-delay:-0.94s"/>
<polygon class="particle" points="209.3,200.8 208.0,203.4 210.6,203.4" fill="#d04dff" opacity="0.93" style="animation-delay:-2.46s"/>
<polygon class="particle" points="202.2,37.4 200.8,40.3 203.6,40.3" fill="#ffb829" opacity="0.67" style="animation-delay:-2.05s"/>
<polygon class="particle" points="243.4,37.2 242.1,40.0 244.8,40.0" fill="#46a7ff" opacity="0.81" style="animation-delay:-3.59s"/>
<polygon class="particle" points="222.6,201.5 220.4,206.1 224.9,206.1" fill="#46a7ff" opacity="0.52" style="animation-delay:-1.28s"/>
<polygon class="particle" points="222.7,32.5 220.5,37.2 225.0,37.2" fill="#f4f0ff" opacity="0.96" style="animation-delay:-0.91s"/>
<polygon class="particle" points="190.4,194.4 188.7,197.7 192.0,197.7" fill="#8052ff" opacity="0.78" style="animation-delay:-2.88s"/>
<polygon class="particle" points="239.2,62.7 237.6,65.9 240.7,65.9" fill="#f4f0ff" opacity="0.56" style="animation-delay:-3.99s"/>
<polygon class="particle" points="207.0,156.5 204.3,161.9 209.6,161.9" fill="#15846e" opacity="0.87" style="animation-delay:-0.09s"/>
<polygon class="particle" points="235.8,46.8 233.3,51.9 238.2,51.9" fill="#f4f0ff" opacity="0.40" style="animation-delay:-1.67s"/>
<polygon class="particle" points="176.9,236.1 175.4,239.3 178.5,239.3" fill="#f4f0ff" opacity="0.97" style="animation-delay:-2.15s"/>
<polygon class="particle" points="187.0,247.6 184.5,252.7 189.4,252.7" fill="#f4f0ff" opacity="0.80" style="animation-delay:-1.70s"/>
<polygon class="particle" points="175.8,99.5 174.7,101.9 177.0,101.9" fill="#46a7ff" opacity="0.79" style="animation-delay:-0.55s"/>
<polygon class="particle" points="234.2,221.6 231.2,227.7 237.2,227.7" fill="#f4f0ff" opacity="0.54" style="animation-delay:-0.46s"/>
<polygon class="particle" points="190.2,64.6 187.4,70.4 193.1,70.4" fill="#f4f0ff" opacity="0.76" style="animation-delay:-1.02s"/>
<polygon class="particle" points="205.2,61.2 203.8,64.2 206.7,64.2" fill="#8052ff" opacity="0.97" style="animation-delay:-3.43s"/>
<polygon class="particle" points="203.5,97.5 201.6,101.4 205.4,101.4" fill="#46a7ff" opacity="0.92" style="animation-delay:-3.94s"/>
<polygon class="particle" points="183.7,120.4 182.5,122.8 184.9,122.8" fill="#f4f0ff" opacity="0.68" style="animation-delay:-2.40s"/>
<polygon class="particle" points="196.6,136.2 193.8,142.0 199.5,142.0" fill="#d04dff" opacity="0.62" style="animation-delay:-1.40s"/>
<polygon class="particle" points="221.0,187.9 217.9,194.2 224.0,194.2" fill="#15846e" opacity="0.91" style="animation-delay:-0.06s"/>
<polygon class="particle" points="211.7,105.5 209.8,109.4 213.6,109.4" fill="#ff7dcb" opacity="0.52" style="animation-delay:-1.43s"/>
<polygon class="particle" points="231.5,119.6 228.4,126.1 234.6,126.1" fill="#46a7ff" opacity="0.72" style="animation-delay:-0.11s"/>
<polygon class="particle" points="232.9,66.3 229.7,72.9 236.1,72.9" fill="#f4f0ff" opacity="0.66" style="animation-delay:-3.93s"/>
<polygon class="particle" points="186.0,95.6 183.9,99.9 188.1,99.9" fill="#d04dff" opacity="0.92" style="animation-delay:-0.65s"/>
<polygon class="particle" points="246.6,260.4 243.3,267.0 249.8,267.0" fill="#d04dff" opacity="0.45" style="animation-delay:-3.49s"/>
<polygon class="particle" points="236.2,187.3 235.0,189.8 237.4,189.8" fill="#f4f0ff" opacity="0.66" style="animation-delay:-0.44s"/>
<polygon class="particle" points="165.8,146.0 163.8,150.1 167.8,150.1" fill="#f4f0ff" opacity="0.53" style="animation-delay:-1.70s"/>
<polygon class="particle" points="210.8,135.4 209.0,139.1 212.5,139.1" fill="#8052ff" opacity="0.46" style="animation-delay:-2.20s"/>
<polygon class="particle" points="187.0,226.2 185.6,229.1 188.4,229.1" fill="#8052ff" opacity="0.86" style="animation-delay:-0.15s"/>
<polygon class="particle" points="229.5,243.2 227.6,247.2 231.4,247.2" fill="#46a7ff" opacity="0.71" style="animation-delay:-2.90s"/>
<polygon class="particle" points="194.4,221.0 191.8,226.4 197.0,226.4" fill="#ffb829" opacity="0.57" style="animation-delay:-0.13s"/>
<polygon class="particle" points="202.6,77.1 199.7,83.1 205.6,83.1" fill="#ffb829" opacity="0.68" style="animation-delay:-3.38s"/>
<polygon class="particle" points="234.6,162.2 232.5,166.6 236.7,166.6" fill="#ff7dcb" opacity="0.51" style="animation-delay:-3.19s"/>
<polygon class="particle" points="177.7,110.2 175.1,115.7 180.4,115.7" fill="#46a7ff" opacity="0.40" style="animation-delay:-3.48s"/>
<polygon class="particle" points="186.1,159.5 183.6,164.6 188.6,164.6" fill="#8052ff" opacity="0.63" style="animation-delay:-3.57s"/>
<polygon class="particle" points="225.9,150.9 223.0,156.9 228.8,156.9" fill="#8052ff" opacity="0.85" style="animation-delay:-0.23s"/>
<polygon class="particle" points="202.7,187.2 201.2,190.3 204.2,190.3" fill="#46a7ff" opacity="0.48" style="animation-delay:-2.93s"/>
<polygon class="particle" points="169.9,198.9 167.5,204.0 172.4,204.0" fill="#f4f0ff" opacity="0.71" style="animation-delay:-3.62s"/>
<polygon class="particle" points="185.8,231.8 183.5,236.5 188.1,236.5" fill="#ffb829" opacity="0.89" style="animation-delay:-1.34s"/>
<polygon class="particle" points="192.5,94.2 189.2,101.1 195.8,101.1" fill="#f4f0ff" opacity="0.93" style="animation-delay:-0.11s"/>
<polygon class="particle" points="214.9,48.1 212.1,54.0 217.7,54.0" fill="#ffb829" opacity="0.73" style="animation-delay:-0.67s"/>
<polygon class="particle" points="207.1,261.8 205.9,264.1 208.2,264.1" fill="#ffb829" opacity="0.81" style="animation-delay:-2.88s"/>
<polygon class="particle" points="179.4,244.2 176.0,251.1 182.7,251.1" fill="#d04dff" opacity="0.77" style="animation-delay:-3.76s"/>
<polygon class="particle" points="187.5,61.7 185.4,66.1 189.7,66.1" fill="#ffb829" opacity="0.44" style="animation-delay:-2.72s"/>
<polygon class="particle" points="237.4,46.8 235.0,51.8 239.8,51.8" fill="#d04dff" opacity="0.53" style="animation-delay:-1.33s"/>
<polygon class="particle" points="254.7,130.2 251.4,136.8 257.9,136.8" fill="#ffb829" opacity="0.92" style="animation-delay:-0.94s"/>
<polygon class="particle" points="175.2,171.1 172.2,177.3 178.2,177.3" fill="#15846e" opacity="0.97" style="animation-delay:-3.10s"/>
<polygon class="particle" points="196.8,249.7 193.6,256.5 200.1,256.5" fill="#f4f0ff" opacity="0.91" style="animation-delay:-1.79s"/>
<polygon class="particle" points="194.4,61.4 191.9,66.7 197.0,66.7" fill="#d04dff" opacity="0.65" style="animation-delay:-1.97s"/>
<polygon class="particle" points="245.4,108.3 242.7,113.8 248.0,113.8" fill="#8052ff" opacity="0.77" style="animation-delay:-2.20s"/>
<polygon class="particle" points="175.6,151.2 172.6,157.4 178.7,157.4" fill="#46a7ff" opacity="0.58" style="animation-delay:-1.40s"/>
<polygon class="particle" points="217.9,222.4 216.0,226.3 219.8,226.3" fill="#d04dff" opacity="0.83" style="animation-delay:-2.72s"/>
<polygon class="particle" points="170.2,93.4 168.1,97.7 172.3,97.7" fill="#8052ff" opacity="0.82" style="animation-delay:-0.15s"/>
<polygon class="particle" points="253.6,156.3 250.6,162.4 256.6,162.4" fill="#ff7dcb" opacity="0.89" style="animation-delay:-3.73s"/>
<polygon class="particle" points="221.7,68.3 219.5,72.8 223.9,72.8" fill="#d04dff" opacity="0.59" style="animation-delay:-3.00s"/>
<polygon class="particle" points="225.3,88.5 224.1,91.1 226.6,91.1" fill="#ff7dcb" opacity="0.94" style="animation-delay:-2.52s"/>
<polygon class="particle" points="197.2,263.4 195.1,267.9 199.4,267.9" fill="#8052ff" opacity="0.46" style="animation-delay:-0.40s"/>
<polygon class="particle" points="241.4,161.5 238.7,167.1 244.1,167.1" fill="#f4f0ff" opacity="0.46" style="animation-delay:-2.92s"/>
<polygon class="particle" points="212.5,59.5 210.9,62.6 214.0,62.6" fill="#f4f0ff" opacity="0.45" style="animation-delay:-1.17s"/>
<polygon class="particle" points="176.7,91.8 175.1,95.1 178.2,95.1" fill="#8052ff" opacity="0.71" style="animation-delay:-2.40s"/>
<polygon class="particle" points="180.8,47.8 178.5,52.4 183.0,52.4" fill="#8052ff" opacity="0.98" style="animation-delay:-0.95s"/>
<polygon class="particle" points="215.7,213.1 212.6,219.6 218.9,219.6" fill="#ff7dcb" opacity="0.98" style="animation-delay:-2.08s"/>
<polygon class="particle" points="215.1,242.5 212.2,248.3 217.9,248.3" fill="#ff7dcb" opacity="0.48" style="animation-delay:-2.82s"/>
<polygon class="particle" points="234.2,198.6 232.8,201.6 235.7,201.6" fill="#f4f0ff" opacity="0.93" style="animation-delay:-0.31s"/>
<polygon class="particle" points="177.9,248.9 175.1,254.7 180.7,254.7" fill="#46a7ff" opacity="0.53" style="animation-delay:-2.27s"/>
<polygon class="particle" points="225.1,120.0 221.8,126.8 228.4,126.8" fill="#46a7ff" opacity="0.82" style="animation-delay:-0.04s"/>
<polygon class="particle" points="197.2,252.9 194.8,257.9 199.6,257.9" fill="#8052ff" opacity="0.73" style="animation-delay:-1.64s"/>
<polygon class="particle" points="194.8,158.7 192.8,162.8 196.8,162.8" fill="#f4f0ff" opacity="0.44" style="animation-delay:-2.03s"/>
<polygon class="particle" points="175.5,69.0 173.4,73.3 177.6,73.3" fill="#ff7dcb" opacity="0.88" style="animation-delay:-3.84s"/>
<polygon class="particle" points="193.7,206.6 191.5,211.2 196.0,211.2" fill="#ffb829" opacity="0.53" style="animation-delay:-2.23s"/>
<polygon class="particle" points="213.9,145.9 211.6,150.6 216.2,150.6" fill="#ffb829" opacity="0.52" style="animation-delay:-2.66s"/>
<polygon class="particle" points="178.9,29.8 177.1,33.7 180.8,33.7" fill="#8052ff" opacity="0.54" style="animation-delay:-1.54s"/>
<polygon class="particle" points="220.6,130.6 218.8,134.3 222.4,134.3" fill="#ffb829" opacity="0.83" style="animation-delay:-0.46s"/>
<polygon class="particle" points="213.1,236.4 211.7,239.4 214.5,239.4" fill="#46a7ff" opacity="0.67" style="animation-delay:-0.41s"/>
<polygon class="particle" points="223.3,97.6 220.2,104.1 226.5,104.1" fill="#8052ff" opacity="0.74" style="animation-delay:-1.58s"/>
<polygon class="particle" points="216.2,147.6 214.6,151.0 217.8,151.0" fill="#ffb829" opacity="0.74" style="animation-delay:-1.66s"/>
<polygon class="particle" points="188.6,116.3 186.7,120.4 190.6,120.4" fill="#d04dff" opacity="0.81" style="animation-delay:-1.76s"/>
<polygon class="particle" points="230.9,257.1 228.9,261.2 232.8,261.2" fill="#d04dff" opacity="0.60" style="animation-delay:-2.07s"/>
<polygon class="particle" points="169.8,210.1 168.0,213.8 171.5,213.8" fill="#46a7ff" opacity="0.79" style="animation-delay:-0.90s"/>
<polygon class="particle" points="242.2,129.4 239.0,136.0 245.4,136.0" fill="#46a7ff" opacity="0.61" style="animation-delay:-3.21s"/>
<polygon class="particle" points="215.8,190.4 212.6,197.2 219.1,197.2" fill="#8052ff" opacity="0.81" style="animation-delay:-1.12s"/>
<polygon class="particle" points="230.1,169.9 227.0,176.4 233.3,176.4" fill="#ffb829" opacity="0.38" style="animation-delay:-2.26s"/>
<polygon class="particle" points="220.9,254.7 219.7,257.2 222.1,257.2" fill="#8052ff" opacity="0.80" style="animation-delay:-0.43s"/>
<polygon class="particle" points="183.3,212.0 181.6,215.6 185.0,215.6" fill="#f4f0ff" opacity="0.39" style="animation-delay:-2.18s"/>
<polygon class="particle" points="180.8,172.8 179.0,176.5 182.6,176.5" fill="#d04dff" opacity="0.93" style="animation-delay:-2.99s"/>
<polygon class="particle" points="225.0,97.5 223.7,100.1 226.3,100.1" fill="#f4f0ff" opacity="0.50" style="animation-delay:-3.87s"/>
<polygon class="particle" points="199.1,67.1 196.4,72.8 201.8,72.8" fill="#46a7ff" opacity="0.48" style="animation-delay:-1.05s"/>
<polygon class="particle" points="192.4,258.1 190.0,263.2 194.9,263.2" fill="#f4f0ff" opacity="0.86" style="animation-delay:-3.27s"/>
<polygon class="particle" points="185.6,222.8 183.0,228.0 188.1,228.0" fill="#46a7ff" opacity="0.66" style="animation-delay:-1.24s"/>
<polygon class="particle" points="237.9,163.6 234.6,170.5 241.3,170.5" fill="#46a7ff" opacity="0.53" style="animation-delay:-0.95s"/>
<polygon class="particle" points="205.5,244.4 202.1,251.4 208.8,251.4" fill="#ffb829" opacity="0.92" style="animation-delay:-2.78s"/>
<polygon class="particle" points="201.8,156.9 198.6,163.5 205.0,163.5" fill="#8052ff" opacity="0.77" style="animation-delay:-1.70s"/>
<polygon class="particle" points="173.9,207.4 172.5,210.4 175.3,210.4" fill="#f4f0ff" opacity="0.57" style="animation-delay:-1.74s"/>
<polygon class="particle" points="167.9,206.8 165.9,211.0 169.9,211.0" fill="#ffb829" opacity="0.57" style="animation-delay:-0.33s"/>
<polygon class="particle" points="218.3,207.5 216.0,212.3 220.7,212.3" fill="#8052ff" opacity="0.58" style="animation-delay:-3.07s"/>
<polygon class="particle" points="193.6,124.1 190.5,130.4 196.6,130.4" fill="#d04dff" opacity="0.44" style="animation-delay:-1.13s"/>
<polygon class="particle" points="203.2,213.1 199.9,219.8 206.4,219.8" fill="#46a7ff" opacity="0.96" style="animation-delay:-2.45s"/>
<polygon class="particle" points="191.1,227.8 189.8,230.5 192.4,230.5" fill="#46a7ff" opacity="0.63" style="animation-delay:-1.32s"/>
<polygon class="particle" points="178.9,238.2 177.1,241.9 180.7,241.9" fill="#15846e" opacity="0.86" style="animation-delay:-2.34s"/>
<polygon class="particle" points="206.8,137.9 204.4,142.9 209.2,142.9" fill="#8052ff" opacity="0.40" style="animation-delay:-1.81s"/>
<polygon class="particle" points="241.2,33.1 239.6,36.4 242.8,36.4" fill="#15846e" opacity="0.74" style="animation-delay:-1.52s"/>
<polygon class="particle" points="172.4,119.6 169.1,126.4 175.7,126.4" fill="#f4f0ff" opacity="0.98" style="animation-delay:-2.40s"/>
<polygon class="particle" points="250.9,151.3 249.3,154.5 252.5,154.5" fill="#f4f0ff" opacity="0.64" style="animation-delay:-2.23s"/>
<polygon class="particle" points="233.6,90.8 231.1,96.1 236.2,96.1" fill="#f4f0ff" opacity="0.69" style="animation-delay:-1.08s"/>
<polygon class="particle" points="212.6,107.6 209.4,114.2 215.7,114.2" fill="#f4f0ff" opacity="0.58" style="animation-delay:-3.62s"/>
<polygon class="particle" points="230.6,177.6 228.9,181.0 232.3,181.0" fill="#f4f0ff" opacity="0.73" style="animation-delay:-1.81s"/>
<polygon class="particle" points="187.5,252.5 186.4,254.9 188.7,254.9" fill="#f4f0ff" opacity="0.73" style="animation-delay:-1.48s"/>
<polygon class="particle" points="225.0,77.4 222.0,83.6 228.0,83.6" fill="#8052ff" opacity="0.72" style="animation-delay:-2.45s"/>
<polygon class="particle" points="248.1,96.0 246.5,99.2 249.6,99.2" fill="#d04dff" opacity="0.92" style="animation-delay:-3.72s"/>
<polygon class="particle" points="187.9,93.6 186.4,96.7 189.4,96.7" fill="#d04dff" opacity="0.65" style="animation-delay:-2.87s"/>
<polygon class="particle" points="238.4,141.2 235.4,147.2 241.3,147.2" fill="#ff7dcb" opacity="0.66" style="animation-delay:-3.06s"/>
<polygon class="particle" points="171.7,103.7 168.6,110.1 174.7,110.1" fill="#ffb829" opacity="0.68" style="animation-delay:-0.43s"/>
<polygon class="particle" points="189.6,52.2 187.5,56.4 191.6,56.4" fill="#ffb829" opacity="0.74" style="animation-delay:-3.81s"/>
<polygon class="particle" points="222.7,229.3 221.4,231.9 224.0,231.9" fill="#46a7ff" opacity="0.81" style="animation-delay:-3.15s"/>
<polygon class="particle" points="172.5,31.5 171.4,33.9 173.7,33.9" fill="#ffb829" opacity="0.83" style="animation-delay:-2.82s"/>
<polygon class="particle" points="227.2,221.8 226.0,224.3 228.4,224.3" fill="#ff7dcb" opacity="0.54" style="animation-delay:-2.43s"/>
<polygon class="particle" points="251.6,155.3 249.2,160.2 254.0,160.2" fill="#8052ff" opacity="0.59" style="animation-delay:-0.38s"/>
<polygon class="particle" points="181.5,193.6 180.3,196.1 182.8,196.1" fill="#ffb829" opacity="0.59" style="animation-delay:-0.33s"/>
<polygon class="particle" points="253.7,160.4 251.5,164.9 255.9,164.9" fill="#8052ff" opacity="0.64" style="animation-delay:-3.17s"/>
<polygon class="particle" points="191.5,157.6 188.4,163.9 194.5,163.9" fill="#15846e" opacity="0.66" style="animation-delay:-0.82s"/>
<polygon class="particle" points="219.0,40.0 217.6,42.8 220.4,42.8" fill="#f4f0ff" opacity="0.81" style="animation-delay:-3.38s"/>
<polygon class="particle" points="204.8,113.7 203.5,116.4 206.2,116.4" fill="#8052ff" opacity="0.79" style="animation-delay:-1.03s"/>
<polygon class="particle" points="233.1,182.6 229.9,189.2 236.3,189.2" fill="#f4f0ff" opacity="0.76" style="animation-delay:-0.08s"/>
<polygon class="particle" points="174.7,61.1 171.4,68.0 178.0,68.0" fill="#ff7dcb" opacity="0.52" style="animation-delay:-0.09s"/>
<polygon class="particle" points="192.5,101.9 190.9,105.3 194.1,105.3" fill="#46a7ff" opacity="0.50" style="animation-delay:-2.57s"/>
<polygon class="particle" points="232.8,203.8 230.5,208.6 235.1,208.6" fill="#46a7ff" opacity="0.61" style="animation-delay:-3.23s"/>
<polygon class="particle" points="202.9,124.0 201.1,127.9 204.8,127.9" fill="#8052ff" opacity="0.78" style="animation-delay:-1.43s"/>
<polygon class="particle" points="229.0,128.2 226.7,133.0 231.4,133.0" fill="#f4f0ff" opacity="0.42" style="animation-delay:-1.60s"/>
<polygon class="particle" points="180.3,176.8 178.3,181.0 182.3,181.0" fill="#d04dff" opacity="0.63" style="animation-delay:-3.22s"/>
<polygon class="particle" points="178.3,73.8 177.0,76.5 179.6,76.5" fill="#8052ff" opacity="0.97" style="animation-delay:-2.76s"/>
<polygon class="particle" points="211.5,191.0 208.5,197.3 214.6,197.3" fill="#d04dff" opacity="0.72" style="animation-delay:-1.99s"/>
<polygon class="particle" points="169.7,139.2 166.9,145.1 172.6,145.1" fill="#f4f0ff" opacity="0.75" style="animation-delay:-0.19s"/>
<polygon class="particle" points="180.7,188.1 179.0,191.6 182.4,191.6" fill="#ffb829" opacity="0.61" style="animation-delay:-1.44s"/>
<polygon class="particle" points="182.3,132.4 180.5,136.2 184.2,136.2" fill="#8052ff" opacity="0.81" style="animation-delay:-1.92s"/>
<polygon class="particle" points="212.2,173.0 209.3,179.1 215.2,179.1" fill="#46a7ff" opacity="0.48" style="animation-delay:-2.06s"/>
<polygon class="particle" points="181.4,31.2 179.9,34.2 182.8,34.2" fill="#8052ff" opacity="0.85" style="animation-delay:-2.82s"/>
<polygon class="particle" points="209.7,53.9 207.6,58.3 211.8,58.3" fill="#d04dff" opacity="0.52" style="animation-delay:-0.50s"/>
<polygon class="particle" points="205.4,78.2 203.0,83.1 207.7,83.1" fill="#f4f0ff" opacity="0.70" style="animation-delay:-3.04s"/>
<polygon class="particle" points="247.6,85.5 244.3,92.4 251.0,92.4" fill="#15846e" opacity="0.67" style="animation-delay:-4.00s"/>
<polygon class="particle" points="247.9,69.6 246.1,73.1 249.6,73.1" fill="#8052ff" opacity="0.64" style="animation-delay:-3.55s"/>
<polygon class="particle" points="175.2,204.4 172.3,210.2 178.0,210.2" fill="#f4f0ff" opacity="0.80" style="animation-delay:-2.22s"/>
<polygon class="particle" points="166.1,192.3 164.3,196.0 167.9,196.0" fill="#ffb829" opacity="0.50" style="animation-delay:-3.51s"/>
<polygon class="particle" points="236.5,122.0 233.1,128.9 239.9,128.9" fill="#ffb829" opacity="0.56" style="animation-delay:-3.61s"/>
<polygon class="particle" points="232.3,193.8 229.6,199.4 235.0,199.4" fill="#f4f0ff" opacity="0.92" style="animation-delay:-0.10s"/>
<polygon class="particle" points="201.8,253.0 199.5,257.8 204.1,257.8" fill="#46a7ff" opacity="0.65" style="animation-delay:-0.21s"/>
<polygon class="particle" points="242.2,54.2 240.6,57.7 243.9,57.7" fill="#15846e" opacity="0.67" style="animation-delay:-0.77s"/>
<polygon class="particle" points="236.3,68.4 234.6,71.9 238.0,71.9" fill="#46a7ff" opacity="0.38" style="animation-delay:-3.51s"/>
<polygon class="particle" points="183.3,219.6 180.7,225.1 186.0,225.1" fill="#8052ff" opacity="0.80" style="animation-delay:-2.25s"/>
<polygon class="particle" points="167.4,164.9 165.3,169.1 169.4,169.1" fill="#15846e" opacity="0.67" style="animation-delay:-2.40s"/>
<polygon class="particle" points="188.8,29.8 186.9,33.8 190.8,33.8" fill="#d04dff" opacity="0.95" style="animation-delay:-0.22s"/>
<polygon class="particle" points="222.1,185.7 221.0,188.1 223.3,188.1" fill="#f4f0ff" opacity="0.43" style="animation-delay:-3.29s"/>
<polygon class="particle" points="242.4,100.9 240.0,106.0 244.9,106.0" fill="#8052ff" opacity="0.91" style="animation-delay:-1.05s"/>
<polygon class="particle" points="198.9,209.8 196.0,215.9 201.9,215.9" fill="#ff7dcb" opacity="0.38" style="animation-delay:-1.84s"/>
<polygon class="particle" points="235.8,235.1 233.6,239.6 237.9,239.6" fill="#15846e" opacity="0.55" style="animation-delay:-0.62s"/>
<polygon class="particle" points="196.2,195.4 194.2,199.6 198.3,199.6" fill="#f4f0ff" opacity="0.60" style="animation-delay:-1.80s"/>
<polygon class="particle" points="189.7,85.5 188.4,88.3 191.1,88.3" fill="#46a7ff" opacity="0.47" style="animation-delay:-2.26s"/>
<polygon class="particle" points="223.0,214.2 220.2,220.1 225.9,220.1" fill="#8052ff" opacity="0.78" style="animation-delay:-2.81s"/>
<polygon class="particle" points="244.3,90.6 242.7,93.7 245.8,93.7" fill="#ffb829" opacity="0.66" style="animation-delay:-1.29s"/>
<polygon class="particle" points="253.8,173.0 251.6,177.3 255.9,177.3" fill="#46a7ff" opacity="0.43" style="animation-delay:-1.64s"/>
<polygon class="particle" points="247.7,239.5 245.6,244.0 249.9,244.0" fill="#f4f0ff" opacity="0.60" style="animation-delay:-3.16s"/>
<polygon class="particle" points="226.2,135.2 224.8,138.0 227.6,138.0" fill="#ffb829" opacity="0.51" style="animation-delay:-0.92s"/>
<polygon class="particle" points="212.8,150.6 211.0,154.3 214.6,154.3" fill="#d04dff" opacity="0.40" style="animation-delay:-0.81s"/>
<polygon class="particle" points="182.8,135.8 181.4,138.7 184.2,138.7" fill="#ffb829" opacity="0.71" style="animation-delay:-2.67s"/>
<polygon class="particle" points="187.3,195.0 185.2,199.3 189.4,199.3" fill="#f4f0ff" opacity="0.44" style="animation-delay:-3.19s"/>
<polygon class="particle" points="210.7,161.7 209.0,165.3 212.5,165.3" fill="#f4f0ff" opacity="0.40" style="animation-delay:-2.72s"/>
<polygon class="particle" points="195.0,29.7 192.5,35.0 197.6,35.0" fill="#f4f0ff" opacity="0.55" style="animation-delay:-0.27s"/>
<polygon class="particle" points="233.1,47.2 231.4,50.9 234.9,50.9" fill="#ffb829" opacity="0.39" style="animation-delay:-1.88s"/>
<polygon class="particle" points="244.4,134.9 241.8,140.1 246.9,140.1" fill="#46a7ff" opacity="0.52" style="animation-delay:-2.25s"/>
<polygon class="particle" points="226.7,31.7 223.9,37.5 229.5,37.5" fill="#f4f0ff" opacity="0.77" style="animation-delay:-3.53s"/>
<polygon class="particle" points="170.1,219.8 167.4,225.3 172.7,225.3" fill="#d04dff" opacity="0.80" style="animation-delay:-0.86s"/>
<polygon class="particle" points="206.5,106.6 204.1,111.5 208.9,111.5" fill="#f4f0ff" opacity="0.80" style="animation-delay:-2.96s"/>
<polygon class="particle" points="190.7,118.5 189.2,121.5 192.2,121.5" fill="#15846e" opacity="0.55" style="animation-delay:-3.91s"/>
<polygon class="particle" points="254.2,154.4 251.6,159.7 256.7,159.7" fill="#ffb829" opacity="0.91" style="animation-delay:-0.87s"/>
<polygon class="particle" points="224.9,256.2 221.6,262.9 228.1,262.9" fill="#15846e" opacity="0.39" style="animation-delay:-0.64s"/>
<polygon class="particle" points="218.1,93.0 215.0,99.5 221.3,99.5" fill="#15846e" opacity="0.41" style="animation-delay:-1.53s"/>
<polygon class="particle" points="242.1,86.8 240.1,91.0 244.2,91.0" fill="#ffb829" opacity="0.94" style="animation-delay:-2.82s"/>
<polygon class="particle" points="225.7,98.7 222.4,105.6 229.0,105.6" fill="#46a7ff" opacity="0.73" style="animation-delay:-2.85s"/>
<polygon class="particle" points="248.1,239.4 246.7,242.3 249.5,242.3" fill="#f4f0ff" opacity="0.52" style="animation-delay:-0.49s"/>
<polygon class="particle" points="174.9,180.2 173.3,183.5 176.5,183.5" fill="#8052ff" opacity="0.80" style="animation-delay:-2.25s"/>
<polygon class="particle" points="176.1,206.2 174.2,210.1 178.0,210.1" fill="#8052ff" opacity="0.67" style="animation-delay:-2.13s"/>
<polygon class="particle" points="231.9,135.2 229.4,140.5 234.5,140.5" fill="#15846e" opacity="0.53" style="animation-delay:-0.47s"/>
<polygon class="particle" points="229.1,238.4 226.4,243.8 231.7,243.8" fill="#46a7ff" opacity="0.71" style="animation-delay:-0.58s"/>
<polygon class="particle" points="231.8,168.0 228.9,174.0 234.7,174.0" fill="#8052ff" opacity="0.45" style="animation-delay:-0.98s"/>
<polygon class="particle" points="185.7,121.7 182.8,127.7 188.6,127.7" fill="#46a7ff" opacity="0.38" style="animation-delay:-1.96s"/>
<polygon class="particle" points="201.8,76.6 199.9,80.4 203.6,80.4" fill="#f4f0ff" opacity="0.87" style="animation-delay:-2.43s"/>
<polygon class="particle" points="188.0,244.0 186.4,247.2 189.6,247.2" fill="#15846e" opacity="0.60" style="animation-delay:-0.15s"/>
<polygon class="particle" points="181.8,145.5 179.2,150.9 184.4,150.9" fill="#ffb829" opacity="0.55" style="animation-delay:-3.76s"/>
<polygon class="particle" points="248.6,241.1 245.7,247.1 251.5,247.1" fill="#46a7ff" opacity="0.89" style="animation-delay:-1.44s"/>
<polygon class="particle" points="248.6,78.6 247.1,81.7 250.0,81.7" fill="#f4f0ff" opacity="0.80" style="animation-delay:-1.61s"/>
<polygon class="particle" points="247.5,182.5 244.7,188.3 250.3,188.3" fill="#15846e" opacity="0.92" style="animation-delay:-0.84s"/>
<polygon class="particle" points="223.7,194.8 220.7,201.0 226.7,201.0" fill="#46a7ff" opacity="0.97" style="animation-delay:-0.63s"/>
<polygon class="particle" points="225.1,135.1 223.1,139.3 227.2,139.3" fill="#ffb829" opacity="0.44" style="animation-delay:-1.23s"/>
<polygon class="particle" points="236.8,163.8 233.9,169.8 239.7,169.8" fill="#46a7ff" opacity="0.47" style="animation-delay:-0.76s"/>
<polygon class="particle" points="242.3,46.0 241.1,48.5 243.5,48.5" fill="#f4f0ff" opacity="0.67" style="animation-delay:-3.37s"/>
<polygon class="particle" points="201.0,174.6 198.4,180.1 203.7,180.1" fill="#15846e" opacity="0.69" style="animation-delay:-1.97s"/>
<polygon class="particle" points="228.2,115.2 225.0,121.8 231.4,121.8" fill="#15846e" opacity="0.95" style="animation-delay:-1.02s"/>
<polygon class="particle" points="213.0,44.2 210.1,50.0 215.8,50.0" fill="#46a7ff" opacity="0.69" style="animation-delay:-2.08s"/>
<polygon class="particle" points="206.9,64.3 203.6,71.1 210.2,71.1" fill="#ffb829" opacity="0.83" style="animation-delay:-2.32s"/>
<polygon class="particle" points="187.0,131.3 184.6,136.4 189.5,136.4" fill="#f4f0ff" opacity="0.71" style="animation-delay:-1.35s"/>
<polygon class="particle" points="235.7,151.4 233.1,156.6 238.2,156.6" fill="#ffb829" opacity="0.87" style="animation-delay:-2.32s"/>
<polygon class="particle" points="188.0,67.2 184.9,73.7 191.2,73.7" fill="#ff7dcb" opacity="0.73" style="animation-delay:-0.15s"/>
<polygon class="particle" points="211.9,255.1 208.7,261.7 215.1,261.7" fill="#46a7ff" opacity="0.77" style="animation-delay:-2.23s"/>
<polygon class="particle" points="225.4,254.8 224.0,257.9 226.9,257.9" fill="#8052ff" opacity="0.50" style="animation-delay:-3.67s"/>
<polygon class="particle" points="177.7,38.3 175.5,42.7 179.9,42.7" fill="#8052ff" opacity="0.43" style="animation-delay:-2.64s"/>
<polygon class="particle" points="194.1,181.0 191.6,186.1 196.6,186.1" fill="#f4f0ff" opacity="0.55" style="animation-delay:-0.62s"/>
<polygon class="particle" points="229.0,192.9 227.4,196.2 230.7,196.2" fill="#8052ff" opacity="0.56" style="animation-delay:-3.07s"/>
<polygon class="particle" points="203.2,169.1 201.3,172.8 205.0,172.8" fill="#15846e" opacity="0.40" style="animation-delay:-0.50s"/>
<polygon class="particle" points="222.7,103.3 221.1,106.4 224.2,106.4" fill="#ff7dcb" opacity="0.96" style="animation-delay:-1.48s"/>
<polygon class="particle" points="182.2,135.5 180.0,140.0 184.4,140.0" fill="#f4f0ff" opacity="0.70" style="animation-delay:-1.68s"/>
<polygon class="particle" points="171.4,250.2 169.9,253.5 173.0,253.5" fill="#ffb829" opacity="0.44" style="animation-delay:-3.40s"/>
<polygon class="particle" points="201.1,192.3 200.0,194.6 202.3,194.6" fill="#f4f0ff" opacity="0.82" style="animation-delay:-3.25s"/>
<polygon class="particle" points="252.4,152.7 249.5,158.7 255.3,158.7" fill="#ffb829" opacity="0.41" style="animation-delay:-3.89s"/>
<polygon class="particle" points="189.8,43.2 187.7,47.5 191.8,47.5" fill="#d04dff" opacity="0.43" style="animation-delay:-2.73s"/>
<polygon class="particle" points="240.2,163.1 238.6,166.4 241.8,166.4" fill="#d04dff" opacity="0.93" style="animation-delay:-1.78s"/>
<polygon class="particle" points="248.1,125.4 244.8,132.1 251.3,132.1" fill="#15846e" opacity="0.46" style="animation-delay:-3.94s"/>
<polygon class="particle" points="221.9,81.5 220.7,84.1 223.1,84.1" fill="#15846e" opacity="0.76" style="animation-delay:-0.51s"/>
<polygon class="particle" points="182.8,62.6 181.1,66.1 184.5,66.1" fill="#ff7dcb" opacity="0.78" style="animation-delay:-0.70s"/>
<polygon class="particle" points="219.4,240.9 218.2,243.3 220.5,243.3" fill="#f4f0ff" opacity="0.74" style="animation-delay:-0.07s"/>
<polygon class="particle" points="183.6,122.7 180.4,129.2 186.7,129.2" fill="#ffb829" opacity="0.66" style="animation-delay:-3.46s"/>
<polygon class="particle" points="228.6,102.1 226.9,105.7 230.4,105.7" fill="#ff7dcb" opacity="0.79" style="animation-delay:-3.86s"/>
<polygon class="particle" points="178.9,203.2 177.5,206.0 180.2,206.0" fill="#f4f0ff" opacity="0.78" style="animation-delay:-3.68s"/>
<polygon class="particle" points="207.1,159.7 205.8,162.5 208.5,162.5" fill="#8052ff" opacity="0.45" style="animation-delay:-1.89s"/>
<polygon class="particle" points="176.7,43.5 174.2,48.5 179.1,48.5" fill="#46a7ff" opacity="0.94" style="animation-delay:-2.42s"/>
<polygon class="particle" points="248.9,50.9 247.1,54.6 250.6,54.6" fill="#f4f0ff" opacity="0.57" style="animation-delay:-2.52s"/>
<polygon class="particle" points="200.8,262.8 199.5,265.5 202.2,265.5" fill="#46a7ff" opacity="0.65" style="animation-delay:-3.45s"/>
<polygon class="particle" points="249.2,135.5 247.1,139.9 251.3,139.9" fill="#d04dff" opacity="0.74" style="animation-delay:-0.69s"/>
<polygon class="particle" points="183.1,242.9 179.9,249.5 186.3,249.5" fill="#ff7dcb" opacity="0.57" style="animation-delay:-2.53s"/>
<polygon class="particle" points="225.2,140.6 222.1,146.9 228.2,146.9" fill="#d04dff" opacity="0.96" style="animation-delay:-1.66s"/>
<polygon class="particle" points="246.2,132.1 243.6,137.6 248.9,137.6" fill="#46a7ff" opacity="0.94" style="animation-delay:-3.29s"/>
<polygon class="particle" points="250.6,217.7 249.3,220.4 251.9,220.4" fill="#46a7ff" opacity="0.50" style="animation-delay:-2.61s"/>
<polygon class="particle" points="231.3,168.7 228.8,173.8 233.7,173.8" fill="#f4f0ff" opacity="0.41" style="animation-delay:-3.47s"/>
<polygon class="particle" points="253.5,163.0 251.5,167.0 255.4,167.0" fill="#15846e" opacity="0.47" style="animation-delay:-1.43s"/>
<polygon class="particle" points="234.2,139.4 231.1,145.7 237.3,145.7" fill="#ffb829" opacity="0.68" style="animation-delay:-2.01s"/>
<polygon class="particle" points="236.6,59.5 234.9,63.1 238.4,63.1" fill="#f4f0ff" opacity="0.45" style="animation-delay:-1.75s"/>
<polygon class="particle" points="230.2,225.7 228.2,229.9 232.3,229.9" fill="#ffb829" opacity="0.58" style="animation-delay:-1.45s"/>
<polygon class="particle" points="191.1,245.2 188.4,250.7 193.8,250.7" fill="#ffb829" opacity="0.87" style="animation-delay:-1.64s"/>
<polygon class="particle" points="211.2,44.8 208.9,49.6 213.5,49.6" fill="#ffb829" opacity="0.90" style="animation-delay:-0.08s"/>
<polygon class="particle" points="199.8,40.4 198.4,43.2 201.1,43.2" fill="#15846e" opacity="0.63" style="animation-delay:-3.61s"/>
<polygon class="particle" points="225.2,153.7 222.9,158.3 227.4,158.3" fill="#8052ff" opacity="0.84" style="animation-delay:-2.54s"/>
<polygon class="particle" points="177.5,256.6 175.4,260.9 179.6,260.9" fill="#f4f0ff" opacity="0.69" style="animation-delay:-1.14s"/>
<polygon class="particle" points="196.8,48.2 193.5,54.8 200.0,54.8" fill="#46a7ff" opacity="0.63" style="animation-delay:-1.73s"/>
<polygon class="particle" points="177.7,207.9 176.1,211.1 179.2,211.1" fill="#46a7ff" opacity="0.49" style="animation-delay:-1.40s"/>
<polygon class="particle" points="241.8,35.8 240.4,38.7 243.2,38.7" fill="#8052ff" opacity="0.81" style="animation-delay:-0.59s"/>
<polygon class="particle" points="241.9,145.8 240.7,148.1 243.0,148.1" fill="#d04dff" opacity="0.70" style="animation-delay:-1.26s"/>
<polygon class="particle" points="193.8,55.3 191.9,59.3 195.8,59.3" fill="#f4f0ff" opacity="0.92" style="animation-delay:-0.92s"/>
<polygon class="particle" points="254.5,185.6 252.2,190.4 256.8,190.4" fill="#15846e" opacity="0.42" style="animation-delay:-2.48s"/>
<polygon class="particle" points="190.5,156.8 188.6,160.8 192.4,160.8" fill="#15846e" opacity="0.54" style="animation-delay:-3.92s"/>
<polygon class="particle" points="215.8,201.2 213.9,205.1 217.7,205.1" fill="#f4f0ff" opacity="0.54" style="animation-delay:-1.21s"/>
<polygon class="particle" points="184.9,146.6 182.9,150.7 186.9,150.7" fill="#8052ff" opacity="0.71" style="animation-delay:-3.24s"/>
<polygon class="particle" points="190.2,67.2 188.4,70.8 192.0,70.8" fill="#8052ff" opacity="0.87" style="animation-delay:-0.09s"/>
<polygon class="particle" points="183.6,93.0 181.4,97.5 185.9,97.5" fill="#ffb829" opacity="0.96" style="animation-delay:-2.31s"/>
<polygon class="particle" points="221.2,76.8 219.9,79.5 222.5,79.5" fill="#f4f0ff" opacity="0.54" style="animation-delay:-2.22s"/>
<polygon class="particle" points="195.9,118.4 193.4,123.5 198.4,123.5" fill="#ffb829" opacity="0.52" style="animation-delay:-3.77s"/>
<polygon class="particle" points="252.2,215.8 249.0,222.5 255.4,222.5" fill="#8052ff" opacity="0.61" style="animation-delay:-3.20s"/>
<polygon class="particle" points="243.0,117.2 241.7,119.9 244.4,119.9" fill="#ff7dcb" opacity="0.92" style="animation-delay:-0.91s"/>
<polygon class="particle" points="239.5,112.2 238.4,114.6 240.7,114.6" fill="#8052ff" opacity="0.87" style="animation-delay:-3.62s"/>
<polygon class="particle" points="179.0,61.1 176.6,66.1 181.4,66.1" fill="#d04dff" opacity="0.64" style="animation-delay:-2.84s"/>
<polygon class="particle" points="204.4,259.2 202.5,263.1 206.3,263.1" fill="#f4f0ff" opacity="0.89" style="animation-delay:-2.51s"/>
<polygon class="particle" points="192.4,238.4 189.6,244.2 195.3,244.2" fill="#d04dff" opacity="0.81" style="animation-delay:-2.99s"/>
<polygon class="particle" points="238.6,221.2 235.2,228.1 241.9,228.1" fill="#f4f0ff" opacity="0.75" style="animation-delay:-2.02s"/>
<polygon class="particle" points="243.0,182.1 241.5,185.2 244.5,185.2" fill="#f4f0ff" opacity="0.57" style="animation-delay:-2.60s"/>
<polygon class="particle" points="190.1,253.6 188.5,256.7 191.6,256.7" fill="#8052ff" opacity="0.69" style="animation-delay:-3.33s"/>
<polygon class="particle" points="183.9,179.0 182.2,182.6 185.7,182.6" fill="#ffb829" opacity="0.61" style="animation-delay:-1.86s"/>
<polygon class="particle" points="246.1,135.6 243.3,141.5 249.0,141.5" fill="#d04dff" opacity="0.55" style="animation-delay:-0.12s"/>
<polygon class="particle" points="174.6,131.2 171.8,136.9 177.3,136.9" fill="#8052ff" opacity="0.94" style="animation-delay:-3.75s"/>
<polygon class="particle" points="228.9,90.6 227.2,94.1 230.7,94.1" fill="#f4f0ff" opacity="0.63" style="animation-delay:-1.79s"/>
<polygon class="particle" points="173.5,141.2 171.5,145.2 175.4,145.2" fill="#ffb829" opacity="0.98" style="animation-delay:-1.29s"/>
<polygon class="particle" points="245.1,64.0 241.8,70.9 248.4,70.9" fill="#f4f0ff" opacity="0.63" style="animation-delay:-1.74s"/>
<polygon class="particle" points="236.9,181.4 234.9,185.6 239.0,185.6" fill="#ffb829" opacity="0.55" style="animation-delay:-0.70s"/>
<polygon class="particle" points="238.2,80.9 235.0,87.4 241.3,87.4" fill="#15846e" opacity="0.52" style="animation-delay:-2.97s"/>
<polygon class="particle" points="214.5,259.6 213.2,262.2 215.7,262.2" fill="#ffb829" opacity="0.92" style="animation-delay:-3.69s"/>
<polygon class="particle" points="196.2,214.2 193.5,219.7 198.8,219.7" fill="#f4f0ff" opacity="0.72" style="animation-delay:-1.51s"/>
<polygon class="particle" points="196.7,200.4 195.1,203.6 198.2,203.6" fill="#46a7ff" opacity="0.54" style="animation-delay:-0.44s"/>
<polygon class="particle" points="204.8,214.6 202.0,220.5 207.7,220.5" fill="#ffb829" opacity="0.62" style="animation-delay:-2.25s"/>
<polygon class="particle" points="243.8,200.9 242.0,204.8 245.7,204.8" fill="#f4f0ff" opacity="0.75" style="animation-delay:-2.14s"/>
<polygon class="particle" points="176.6,210.5 174.4,214.9 178.7,214.9" fill="#d04dff" opacity="0.69" style="animation-delay:-3.58s"/>
<polygon class="particle" points="218.7,259.4 215.6,265.7 221.8,265.7" fill="#15846e" opacity="0.56" style="animation-delay:-3.34s"/>
<polygon class="particle" points="235.2,87.2 232.6,92.5 237.7,92.5" fill="#d04dff" opacity="0.98" style="animation-delay:-0.97s"/>
<polygon class="particle" points="226.0,265.9 224.1,269.8 227.9,269.8" fill="#f4f0ff" opacity="0.64" style="animation-delay:-0.89s"/>
<polygon class="particle" points="226.2,231.9 224.4,235.6 228.0,235.6" fill="#ff7dcb" opacity="0.39" style="animation-delay:-3.50s"/>
<polygon class="particle" points="197.6,146.5 196.0,149.8 199.2,149.8" fill="#f4f0ff" opacity="0.88" style="animation-delay:-2.13s"/>
<polygon class="particle" points="191.1,81.4 189.8,84.0 192.3,84.0" fill="#ffb829" opacity="0.66" style="animation-delay:-2.96s"/>
<polygon class="particle" points="247.5,199.9 245.0,205.0 249.9,205.0" fill="#ffb829" opacity="0.48" style="animation-delay:-0.55s"/>
<polygon class="particle" points="248.3,73.2 246.0,78.1 250.7,78.1" fill="#ffb829" opacity="0.44" style="animation-delay:-0.57s"/>
<polygon class="particle" points="213.6,144.3 212.0,147.6 215.2,147.6" fill="#8052ff" opacity="0.70" style="animation-delay:-3.25s"/>
<polygon class="particle" points="180.6,156.1 178.4,160.5 182.7,160.5" fill="#f4f0ff" opacity="0.56" style="animation-delay:-3.63s"/>
<polygon class="particle" points="247.4,176.0 245.5,179.7 249.2,179.7" fill="#15846e" opacity="0.71" style="animation-delay:-2.41s"/>
<polygon class="particle" points="189.3,234.6 187.3,238.7 191.4,238.7" fill="#f4f0ff" opacity="0.77" style="animation-delay:-2.89s"/>
<polygon class="particle" points="186.6,165.6 183.3,172.6 190.0,172.6" fill="#f4f0ff" opacity="0.57" style="animation-delay:-0.34s"/>
<polygon class="particle" points="221.3,106.9 218.9,111.8 223.6,111.8" fill="#ffb829" opacity="0.55" style="animation-delay:-2.25s"/>
<polygon class="particle" points="237.1,91.6 234.5,96.8 239.7,96.8" fill="#f4f0ff" opacity="0.95" style="animation-delay:-0.47s"/>
<polygon class="particle" points="219.2,51.8 216.8,56.6 221.5,56.6" fill="#8052ff" opacity="0.49" style="animation-delay:-1.15s"/>
<polygon class="particle" points="229.1,253.7 226.5,259.1 231.7,259.1" fill="#ffb829" opacity="0.75" style="animation-delay:-2.77s"/>
<polygon class="particle" points="165.8,140.2 164.5,142.8 167.1,142.8" fill="#ffb829" opacity="0.97" style="animation-delay:-0.13s"/>
<polygon class="particle" points="241.5,145.2 240.0,148.3 242.9,148.3" fill="#f4f0ff" opacity="0.53" style="animation-delay:-1.51s"/>
<polygon class="particle" points="194.3,173.0 192.7,176.3 195.9,176.3" fill="#8052ff" opacity="0.41" style="animation-delay:-0.52s"/>
<polygon class="particle" points="242.5,90.5 240.2,95.2 244.8,95.2" fill="#8052ff" opacity="0.50" style="animation-delay:-1.34s"/>
<polygon class="particle" points="205.1,130.3 202.5,135.7 207.7,135.7" fill="#15846e" opacity="0.48" style="animation-delay:-1.28s"/>
<polygon class="particle" points="236.4,133.2 233.4,139.4 239.4,139.4" fill="#8052ff" opacity="0.47" style="animation-delay:-3.05s"/>
<polygon class="particle" points="186.7,220.8 183.6,227.3 189.9,227.3" fill="#f4f0ff" opacity="0.93" style="animation-delay:-3.77s"/>
<polygon class="particle" points="213.0,65.3 210.7,70.1 215.3,70.1" fill="#8052ff" opacity="0.92" style="animation-delay:-2.61s"/>
<polygon class="particle" points="228.7,238.2 226.9,242.0 230.6,242.0" fill="#d04dff" opacity="0.78" style="animation-delay:-3.22s"/>
<polygon class="particle" points="169.1,191.0 167.8,193.7 170.4,193.7" fill="#8052ff" opacity="0.64" style="animation-delay:-0.11s"/>
<polygon class="particle" points="221.2,165.3 217.9,172.0 224.4,172.0" fill="#ff7dcb" opacity="0.64" style="animation-delay:-2.82s"/>
<polygon class="particle" points="190.8,122.5 189.4,125.4 192.2,125.4" fill="#ffb829" opacity="0.74" style="animation-delay:-2.17s"/>
<polygon class="particle" points="179.0,156.2 177.5,159.3 180.5,159.3" fill="#46a7ff" opacity="0.97" style="animation-delay:-2.14s"/>
<polygon class="particle" points="236.7,216.4 234.4,221.0 238.9,221.0" fill="#8052ff" opacity="0.57" style="animation-delay:-1.51s"/>
<polygon class="particle" points="206.5,211.3 205.1,214.3 208.0,214.3" fill="#46a7ff" opacity="0.59" style="animation-delay:-3.25s"/>
<polygon class="particle" points="188.9,89.5 185.9,95.7 192.0,95.7" fill="#8052ff" opacity="0.48" style="animation-delay:-1.71s"/>
<polygon class="particle" points="241.1,257.8 238.5,263.2 243.7,263.2" fill="#f4f0ff" opacity="0.58" style="animation-delay:-1.63s"/>
<polygon class="particle" points="207.5,254.1 204.6,260.0 210.3,260.0" fill="#f4f0ff" opacity="0.94" style="animation-delay:-1.92s"/>
<polygon class="particle" points="240.8,59.1 238.6,63.7 243.1,63.7" fill="#f4f0ff" opacity="0.93" style="animation-delay:-1.14s"/>
<polygon class="particle" points="213.9,241.2 212.5,243.9 215.2,243.9" fill="#d04dff" opacity="0.81" style="animation-delay:-3.39s"/>
<polygon class="particle" points="209.8,95.4 208.1,98.9 211.5,98.9" fill="#ffb829" opacity="0.69" style="animation-delay:-0.03s"/>
<polygon class="particle" points="216.1,209.3 215.0,211.7 217.3,211.7" fill="#ffb829" opacity="0.45" style="animation-delay:-1.73s"/>
<polygon class="particle" points="246.3,131.9 244.0,136.7 248.7,136.7" fill="#f4f0ff" opacity="0.67" style="animation-delay:-3.61s"/>
<polygon class="particle" points="189.3,69.8 186.2,76.1 192.3,76.1" fill="#d04dff" opacity="0.45" style="animation-delay:-3.38s"/>
<polygon class="particle" points="244.5,140.0 242.4,144.3 246.6,144.3" fill="#46a7ff" opacity="0.53" style="animation-delay:-1.67s"/>
<polygon class="particle" points="174.3,231.7 173.0,234.4 175.6,234.4" fill="#f4f0ff" opacity="0.40" style="animation-delay:-3.46s"/>
<polygon class="particle" points="247.3,139.9 245.0,144.6 249.6,144.6" fill="#46a7ff" opacity="0.97" style="animation-delay:-1.05s"/>
<polygon class="particle" points="176.9,70.7 175.8,73.0 178.1,73.0" fill="#8052ff" opacity="0.98" style="animation-delay:-0.62s"/>
<polygon class="particle" points="242.5,163.8 241.1,166.7 243.9,166.7" fill="#d04dff" opacity="0.75" style="animation-delay:-2.22s"/>
<polygon class="particle" points="241.3,84.8 238.7,90.1 243.9,90.1" fill="#f4f0ff" opacity="0.95" style="animation-delay:-2.61s"/>
<polygon class="particle" points="175.0,98.7 173.1,102.5 176.8,102.5" fill="#d04dff" opacity="0.49" style="animation-delay:-0.60s"/>
<polygon class="particle" points="192.0,66.7 189.3,72.4 194.8,72.4" fill="#8052ff" opacity="0.88" style="animation-delay:-3.80s"/>
<polygon class="particle" points="247.7,30.6 245.4,35.4 250.0,35.4" fill="#d04dff" opacity="0.94" style="animation-delay:-1.11s"/>
<polygon class="particle" points="219.5,104.8 217.5,108.8 221.5,108.8" fill="#8052ff" opacity="0.48" style="animation-delay:-0.86s"/>
<polygon class="particle" points="209.9,240.2 206.9,246.5 213.0,246.5" fill="#15846e" opacity="0.43" style="animation-delay:-0.83s"/>
<polygon class="particle" points="181.4,163.6 180.1,166.3 182.7,166.3" fill="#46a7ff" opacity="0.57" style="animation-delay:-3.59s"/>
<polygon class="particle" points="242.2,197.5 239.0,204.1 245.4,204.1" fill="#8052ff" opacity="0.59" style="animation-delay:-2.54s"/>
<polygon class="particle" points="193.8,83.2 191.7,87.5 195.9,87.5" fill="#f4f0ff" opacity="0.57" style="animation-delay:-2.18s"/>
<polygon class="particle" points="223.0,61.6 220.2,67.4 225.9,67.4" fill="#8052ff" opacity="0.63" style="animation-delay:-0.74s"/>
<polygon class="particle" points="238.4,126.1 235.3,132.4 241.4,132.4" fill="#15846e" opacity="0.50" style="animation-delay:-3.81s"/>
<polygon class="particle" points="236.3,28.5 233.3,34.6 239.3,34.6" fill="#d04dff" opacity="0.84" style="animation-delay:-1.87s"/>
<polygon class="particle" points="229.8,130.0 227.8,134.2 231.8,134.2" fill="#f4f0ff" opacity="0.68" style="animation-delay:-0.12s"/>
<polygon class="particle" points="178.0,81.9 174.8,88.5 181.2,88.5" fill="#d04dff" opacity="0.95" style="animation-delay:-0.31s"/>
<polygon class="particle" points="204.5,198.8 201.6,204.9 207.4,204.9" fill="#46a7ff" opacity="0.56" style="animation-delay:-0.80s"/>
<polygon class="particle" points="220.2,169.6 218.7,172.9 221.8,172.9" fill="#ff7dcb" opacity="0.87" style="animation-delay:-2.85s"/>
<polygon class="particle" points="179.2,186.3 176.7,191.7 181.8,191.7" fill="#f4f0ff" opacity="0.70" style="animation-delay:-3.77s"/>
<polygon class="particle" points="240.9,54.1 239.4,57.1 242.3,57.1" fill="#f4f0ff" opacity="0.94" style="animation-delay:-2.16s"/>
<polygon class="particle" points="196.0,253.7 193.7,258.3 198.2,258.3" fill="#f4f0ff" opacity="0.63" style="animation-delay:-3.17s"/>
<polygon class="particle" points="211.4,99.9 209.0,104.7 213.7,104.7" fill="#ffb829" opacity="0.73" style="animation-delay:-0.70s"/>
<polygon class="particle" points="229.3,242.0 228.1,244.5 230.5,244.5" fill="#ffb829" opacity="0.61" style="animation-delay:-1.78s"/>
<polygon class="particle" points="223.0,147.9 220.4,153.3 225.6,153.3" fill="#46a7ff" opacity="0.42" style="animation-delay:-1.02s"/>
<polygon class="particle" points="236.4,43.0 233.3,49.3 239.4,49.3" fill="#15846e" opacity="0.91" style="animation-delay:-2.31s"/>
<polygon class="particle" points="235.9,94.4 233.6,99.2 238.2,99.2" fill="#f4f0ff" opacity="0.67" style="animation-delay:-3.37s"/>
<polygon class="particle" points="239.2,82.8 236.6,88.2 241.8,88.2" fill="#f4f0ff" opacity="0.94" style="animation-delay:-3.59s"/>
<polygon class="particle" points="219.4,177.7 217.1,182.4 221.7,182.4" fill="#ffb829" opacity="0.73" style="animation-delay:-3.45s"/>
<polygon class="particle" points="209.8,163.2 206.6,170.0 213.1,170.0" fill="#15846e" opacity="0.59" style="animation-delay:-0.68s"/>
<polygon class="particle" points="187.3,219.4 185.6,223.0 189.1,223.0" fill="#15846e" opacity="0.43" style="animation-delay:-0.49s"/>
<polygon class="particle" points="244.0,56.9 241.3,62.5 246.8,62.5" fill="#15846e" opacity="0.77" style="animation-delay:-3.30s"/>
<polygon class="particle" points="184.5,42.0 182.4,46.4 186.6,46.4" fill="#f4f0ff" opacity="0.43" style="animation-delay:-3.93s"/>
<polygon class="particle" points="209.3,233.6 206.3,239.8 212.2,239.8" fill="#f4f0ff" opacity="0.94" style="animation-delay:-3.97s"/>
<polygon class="particle" points="176.7,80.1 173.9,85.8 179.4,85.8" fill="#d04dff" opacity="0.78" style="animation-delay:-2.39s"/>
<polygon class="particle" points="213.7,136.1 212.1,139.4 215.3,139.4" fill="#d04dff" opacity="0.50" style="animation-delay:-2.03s"/>
<polygon class="particle" points="198.0,97.2 195.9,101.5 200.1,101.5" fill="#ffb829" opacity="0.83" style="animation-delay:-3.12s"/>
<polygon class="particle" points="239.8,243.4 238.4,246.3 241.2,246.3" fill="#ff7dcb" opacity="0.48" style="animation-delay:-0.30s"/>
<polygon class="particle" points="206.2,62.7 204.0,67.3 208.4,67.3" fill="#d04dff" opacity="0.86" style="animation-delay:-2.90s"/>
<polygon class="particle" points="169.5,66.5 167.5,70.5 171.4,70.5" fill="#f4f0ff" opacity="0.59" style="animation-delay:-0.60s"/>
<polygon class="particle" points="223.4,89.7 220.3,96.1 226.5,96.1" fill="#15846e" opacity="0.62" style="animation-delay:-0.41s"/>
<polygon class="particle" points="187.2,218.0 186.0,220.3 188.3,220.3" fill="#8052ff" opacity="0.59" style="animation-delay:-2.56s"/>
<polygon class="particle" points="208.0,114.2 205.8,118.7 210.2,118.7" fill="#15846e" opacity="0.88" style="animation-delay:-0.41s"/>
<polygon class="particle" points="204.5,202.9 202.6,206.7 206.4,206.7" fill="#15846e" opacity="0.97" style="animation-delay:-2.04s"/>
<polygon class="particle" points="171.5,266.4 169.1,271.4 174.0,271.4" fill="#46a7ff" opacity="0.86" style="animation-delay:-0.10s"/>
<polygon class="particle" points="246.2,115.4 243.2,121.7 249.2,121.7" fill="#d04dff" opacity="0.59" style="animation-delay:-1.76s"/>
<polygon class="particle" points="205.5,169.9 203.1,175.0 207.9,175.0" fill="#8052ff" opacity="0.83" style="animation-delay:-1.01s"/>
<polygon class="particle" points="199.8,48.0 197.1,53.7 202.6,53.7" fill="#d04dff" opacity="0.83" style="animation-delay:-0.78s"/>
<polygon class="particle" points="249.6,256.5 246.8,262.3 252.5,262.3" fill="#8052ff" opacity="0.61" style="animation-delay:-2.93s"/>
<polygon class="particle" points="179.4,99.8 176.3,106.2 182.5,106.2" fill="#ffb829" opacity="0.64" style="animation-delay:-1.22s"/>
<polygon class="particle" points="189.4,178.0 187.0,182.9 191.7,182.9" fill="#f4f0ff" opacity="0.59" style="animation-delay:-3.11s"/>
<polygon class="particle" points="167.9,78.9 165.1,84.7 170.8,84.7" fill="#46a7ff" opacity="0.42" style="animation-delay:-0.37s"/>
<polygon class="particle" points="244.0,38.8 242.7,41.5 245.4,41.5" fill="#46a7ff" opacity="0.86" style="animation-delay:-0.44s"/>
<polygon class="particle" points="198.8,248.6 196.6,253.1 201.0,253.1" fill="#46a7ff" opacity="0.91" style="animation-delay:-2.53s"/>
<polygon class="particle" points="189.2,153.9 187.7,157.0 190.7,157.0" fill="#ffb829" opacity="0.69" style="animation-delay:-3.64s"/>
<polygon class="particle" points="202.6,107.4 201.0,110.7 204.2,110.7" fill="#f4f0ff" opacity="0.56" style="animation-delay:-0.29s"/>
<polygon class="particle" points="202.1,245.6 200.0,249.9 204.2,249.9" fill="#ff7dcb" opacity="0.40" style="animation-delay:-2.04s"/>
<polygon class="particle" points="185.0,100.1 182.9,104.5 187.2,104.5" fill="#ffb829" opacity="0.50" style="animation-delay:-0.30s"/>
<polygon class="particle" points="223.3,257.9 220.1,264.6 226.5,264.6" fill="#d04dff" opacity="0.94" style="animation-delay:-0.92s"/>
<polygon class="particle" points="191.2,56.0 188.2,62.3 194.2,62.3" fill="#d04dff" opacity="0.47" style="animation-delay:-2.73s"/>
<polygon class="particle" points="211.5,159.9 209.8,163.4 213.2,163.4" fill="#8052ff" opacity="0.72" style="animation-delay:-0.82s"/>
<polygon class="particle" points="175.2,236.6 173.3,240.5 177.1,240.5" fill="#46a7ff" opacity="0.79" style="animation-delay:-0.45s"/>
<polygon class="particle" points="227.1,153.5 224.6,158.7 229.6,158.7" fill="#15846e" opacity="0.87" style="animation-delay:-2.15s"/>
<polygon class="particle" points="192.2,260.7 190.1,265.0 194.2,265.0" fill="#ffb829" opacity="0.80" style="animation-delay:-2.39s"/>
<polygon class="particle" points="234.4,116.6 233.1,119.3 235.7,119.3" fill="#15846e" opacity="0.63" style="animation-delay:-0.74s"/>
<polygon class="particle" points="186.6,67.2 183.5,73.6 189.7,73.6" fill="#d04dff" opacity="0.82" style="animation-delay:-0.43s"/>
<polygon class="particle" points="189.7,226.8 187.8,230.9 191.7,230.9" fill="#d04dff" opacity="0.53" style="animation-delay:-3.30s"/>
<polygon class="particle" points="176.1,208.8 174.8,211.5 177.4,211.5" fill="#d04dff" opacity="0.66" style="animation-delay:-1.42s"/>
<polygon class="particle" points="206.2,130.1 203.3,136.1 209.1,136.1" fill="#ff7dcb" opacity="0.75" style="animation-delay:-1.78s"/>
<polygon class="particle" points="232.0,247.7 229.3,253.2 234.6,253.2" fill="#46a7ff" opacity="0.78" style="animation-delay:-1.53s"/>
<polygon class="particle" points="201.9,52.6 200.3,55.8 203.5,55.8" fill="#f4f0ff" opacity="0.62" style="animation-delay:-4.00s"/>
<polygon class="particle" points="178.5,185.7 176.8,189.2 180.1,189.2" fill="#f4f0ff" opacity="0.88" style="animation-delay:-3.76s"/>
<polygon class="particle" points="233.7,117.0 231.1,122.3 236.2,122.3" fill="#46a7ff" opacity="0.76" style="animation-delay:-0.28s"/>
<polygon class="particle" points="193.9,138.5 191.3,143.8 196.5,143.8" fill="#15846e" opacity="0.75" style="animation-delay:-1.34s"/>
<polygon class="particle" points="223.1,159.2 221.3,162.9 224.9,162.9" fill="#ffb829" opacity="0.77" style="animation-delay:-2.51s"/>
<polygon class="particle" points="246.0,190.8 244.6,193.6 247.3,193.6" fill="#8052ff" opacity="0.77" style="animation-delay:-3.86s"/>
<polygon class="particle" points="241.7,212.7 238.5,219.5 245.0,219.5" fill="#8052ff" opacity="0.64" style="animation-delay:-3.44s"/>
<polygon class="particle" points="242.8,226.0 241.2,229.1 244.3,229.1" fill="#f4f0ff" opacity="0.86" style="animation-delay:-0.96s"/>
<polygon class="particle" points="174.6,184.0 172.2,189.0 177.1,189.0" fill="#15846e" opacity="0.97" style="animation-delay:-3.82s"/>
<polygon class="particle" points="180.8,51.1 177.8,57.3 183.9,57.3" fill="#d04dff" opacity="0.57" style="animation-delay:-2.12s"/>
<polygon class="particle" points="236.7,131.0 235.2,134.2 238.3,134.2" fill="#ffb829" opacity="0.51" style="animation-delay:-1.88s"/>
<polygon class="particle" points="214.7,103.8 212.0,109.3 217.3,109.3" fill="#15846e" opacity="0.40" style="animation-delay:-3.64s"/>
<polygon class="particle" points="205.2,82.5 203.5,85.9 206.8,85.9" fill="#8052ff" opacity="0.82" style="animation-delay:-2.95s"/>
<polygon class="particle" points="239.5,61.0 237.9,64.4 241.1,64.4" fill="#46a7ff" opacity="0.66" style="animation-delay:-3.50s"/>
<polygon class="particle" points="202.2,168.1 200.6,171.4 203.7,171.4" fill="#ffb829" opacity="0.66" style="animation-delay:-1.43s"/>
<polygon class="particle" points="194.0,48.3 191.9,52.7 196.1,52.7" fill="#f4f0ff" opacity="0.62" style="animation-delay:-3.82s"/>
<polygon class="particle" points="194.5,75.7 192.4,80.0 196.6,80.0" fill="#f4f0ff" opacity="0.92" style="animation-delay:-3.66s"/>
<polygon class="particle" points="224.1,76.9 221.6,82.0 226.6,82.0" fill="#ffb829" opacity="0.91" style="animation-delay:-3.04s"/>
<polygon class="particle" points="230.0,31.1 228.1,35.0 231.9,35.0" fill="#d04dff" opacity="0.93" style="animation-delay:-1.35s"/>
<polygon class="particle" points="221.0,205.4 219.9,207.7 222.1,207.7" fill="#ffb829" opacity="0.84" style="animation-delay:-0.50s"/>
<polygon class="particle" points="197.4,148.6 196.0,151.4 198.7,151.4" fill="#d04dff" opacity="0.52" style="animation-delay:-2.57s"/>
<polygon class="particle" points="208.4,205.5 207.2,208.0 209.6,208.0" fill="#15846e" opacity="0.67" style="animation-delay:-3.17s"/>
<polygon class="particle" points="198.2,258.4 196.7,261.5 199.7,261.5" fill="#ffb829" opacity="0.55" style="animation-delay:-2.92s"/>
<polygon class="particle" points="172.6,112.2 169.9,117.6 175.3,117.6" fill="#f4f0ff" opacity="0.92" style="animation-delay:-1.49s"/>
<polygon class="particle" points="250.9,249.6 247.6,256.4 254.2,256.4" fill="#d04dff" opacity="0.40" style="animation-delay:-2.69s"/>
<polygon class="particle" points="208.7,122.8 205.7,128.9 211.7,128.9" fill="#ffb829" opacity="0.77" style="animation-delay:-1.19s"/>
<polygon class="particle" points="187.6,30.4 184.8,36.2 190.4,36.2" fill="#f4f0ff" opacity="0.61" style="animation-delay:-0.89s"/>
<polygon class="particle" points="215.7,229.8 213.2,234.9 218.1,234.9" fill="#8052ff" opacity="0.66" style="animation-delay:-3.21s"/>
<polygon class="particle" points="214.1,189.5 212.2,193.4 215.9,193.4" fill="#f4f0ff" opacity="0.45" style="animation-delay:-0.72s"/>
<polygon class="particle" points="188.7,110.9 185.9,116.8 191.6,116.8" fill="#f4f0ff" opacity="0.69" style="animation-delay:-2.85s"/>
<polygon class="particle" points="200.4,151.0 199.1,153.8 201.8,153.8" fill="#f4f0ff" opacity="0.72" style="animation-delay:-0.19s"/>
<polygon class="particle" points="211.7,34.0 209.3,39.0 214.2,39.0" fill="#46a7ff" opacity="0.93" style="animation-delay:-3.17s"/>
<polygon class="particle" points="249.6,87.6 246.6,93.8 252.6,93.8" fill="#8052ff" opacity="0.81" style="animation-delay:-2.91s"/>
<polygon class="particle" points="183.9,140.3 182.4,143.3 185.3,143.3" fill="#ff7dcb" opacity="0.74" style="animation-delay:-1.59s"/>
<polygon class="particle" points="247.4,80.1 245.6,83.8 249.2,83.8" fill="#46a7ff" opacity="0.59" style="animation-delay:-2.42s"/>
<polygon class="particle" points="237.0,260.4 235.1,264.3 238.9,264.3" fill="#ffb829" opacity="0.90" style="animation-delay:-2.44s"/>
<polygon class="particle" points="190.0,85.0 186.9,91.4 193.2,91.4" fill="#ffb829" opacity="0.79" style="animation-delay:-1.08s"/>
<polygon class="particle" points="251.7,145.2 249.5,149.8 253.9,149.8" fill="#ffb829" opacity="0.93" style="animation-delay:-1.18s"/>
<polygon class="particle" points="245.6,180.1 242.8,185.7 248.3,185.7" fill="#ffb829" opacity="0.86" style="animation-delay:-1.83s"/>
<polygon class="particle" points="189.6,44.9 187.5,49.3 191.8,49.3" fill="#8052ff" opacity="0.88" style="animation-delay:-1.46s"/>
<polygon class="particle" points="209.9,150.7 207.8,155.1 212.1,155.1" fill="#8052ff" opacity="0.78" style="animation-delay:-0.80s"/>
<polygon class="particle" points="230.8,71.3 229.2,74.7 232.5,74.7" fill="#46a7ff" opacity="0.83" style="animation-delay:-2.09s"/>
<polygon class="particle" points="253.7,168.4 251.5,173.0 256.0,173.0" fill="#8052ff" opacity="0.58" style="animation-delay:-0.69s"/>
<polygon class="particle" points="179.5,59.6 178.2,62.2 180.7,62.2" fill="#f4f0ff" opacity="0.69" style="animation-delay:-3.34s"/>
<polygon class="particle" points="184.6,181.6 182.6,185.8 186.7,185.8" fill="#46a7ff" opacity="0.84" style="animation-delay:-3.90s"/>
<polygon class="particle" points="252.4,230.0 249.5,235.9 255.2,235.9" fill="#d04dff" opacity="0.89" style="animation-delay:-3.64s"/>
<polygon class="particle" points="195.4,224.2 192.6,229.9 198.1,229.9" fill="#15846e" opacity="0.43" style="animation-delay:-1.44s"/>
<polygon class="particle" points="195.6,236.3 192.6,242.4 198.5,242.4" fill="#15846e" opacity="0.92" style="animation-delay:-1.95s"/>
<polygon class="particle" points="173.3,262.4 171.6,265.9 175.0,265.9" fill="#15846e" opacity="0.91" style="animation-delay:-2.78s"/>
<polygon class="particle" points="176.3,56.8 175.2,59.2 177.5,59.2" fill="#8052ff" opacity="0.84" style="animation-delay:-3.17s"/>
<polygon class="particle" points="209.6,95.8 207.0,101.3 212.3,101.3" fill="#f4f0ff" opacity="0.89" style="animation-delay:-0.43s"/>
<polygon class="particle" points="219.6,228.7 216.3,235.4 222.8,235.4" fill="#8052ff" opacity="0.48" style="animation-delay:-3.75s"/>
<polygon class="particle" points="177.4,120.3 175.8,123.7 179.0,123.7" fill="#46a7ff" opacity="0.65" style="animation-delay:-2.67s"/>
<polygon class="particle" points="214.2,89.1 213.0,91.6 215.5,91.6" fill="#f4f0ff" opacity="0.48" style="animation-delay:-0.09s"/>
<polygon class="particle" points="246.9,104.4 244.8,108.6 248.9,108.6" fill="#ffb829" opacity="0.46" style="animation-delay:-3.28s"/>
<polygon class="particle" points="186.6,117.1 183.8,122.9 189.4,122.9" fill="#8052ff" opacity="0.42" style="animation-delay:-2.52s"/>
<polygon class="particle" points="230.3,30.8 227.5,36.6 233.1,36.6" fill="#f4f0ff" opacity="0.88" style="animation-delay:-2.87s"/>
<polygon class="particle" points="240.1,93.0 236.8,99.8 243.4,99.8" fill="#d04dff" opacity="0.56" style="animation-delay:-2.79s"/>
<polygon class="particle" points="179.0,202.1 176.3,207.8 181.8,207.8" fill="#f4f0ff" opacity="0.66" style="animation-delay:-1.06s"/>
<polygon class="particle" points="250.0,176.8 248.4,180.1 251.5,180.1" fill="#f4f0ff" opacity="0.41" style="animation-delay:-2.96s"/>
<polygon class="particle" points="200.1,31.3 198.7,34.2 201.6,34.2" fill="#ffb829" opacity="0.68" style="animation-delay:-1.90s"/>
<polygon class="particle" points="240.4,129.5 237.8,134.9 243.0,134.9" fill="#46a7ff" opacity="0.74" style="animation-delay:-3.51s"/>
<polygon class="particle" points="203.8,266.3 201.5,271.0 206.1,271.0" fill="#8052ff" opacity="0.60" style="animation-delay:-2.61s"/>
<polygon class="particle" points="174.6,50.0 172.9,53.6 176.4,53.6" fill="#46a7ff" opacity="0.87" style="animation-delay:-2.45s"/>
<polygon class="particle" points="195.3,139.5 193.4,143.5 197.2,143.5" fill="#d04dff" opacity="0.61" style="animation-delay:-3.26s"/>
<polygon class="particle" points="250.6,218.0 249.1,221.0 252.0,221.0" fill="#ff7dcb" opacity="0.55" style="animation-delay:-1.92s"/>
<polygon class="particle" points="208.0,240.4 206.6,243.1 209.3,243.1" fill="#ffb829" opacity="0.72" style="animation-delay:-0.70s"/>
<polygon class="particle" points="233.0,201.4 231.5,204.5 234.5,204.5" fill="#ffb829" opacity="0.54" style="animation-delay:-3.45s"/>
<polygon class="particle" points="184.8,195.1 182.0,200.9 187.6,200.9" fill="#f4f0ff" opacity="0.42" style="animation-delay:-0.87s"/>
<polygon class="particle" points="235.0,252.4 232.5,257.6 237.5,257.6" fill="#ffb829" opacity="0.48" style="animation-delay:-2.38s"/>
<polygon class="particle" points="243.1,233.5 241.0,237.8 245.1,237.8" fill="#ff7dcb" opacity="0.61" style="animation-delay:-0.42s"/>
<polygon class="particle" points="178.9,222.3 175.7,228.9 182.1,228.9" fill="#8052ff" opacity="0.69" style="animation-delay:-2.96s"/>
<polygon class="particle" points="242.6,219.8 240.8,223.5 244.4,223.5" fill="#f4f0ff" opacity="0.96" style="animation-delay:-1.57s"/>
<polygon class="particle" points="209.9,171.3 208.8,173.6 211.0,173.6" fill="#8052ff" opacity="0.69" style="animation-delay:-2.38s"/>
<polygon class="particle" points="182.2,118.6 180.9,121.4 183.6,121.4" fill="#8052ff" opacity="0.67" style="animation-delay:-0.43s"/>
<polygon class="particle" points="175.9,213.0 172.9,219.1 178.9,219.1" fill="#46a7ff" opacity="0.82" style="animation-delay:-2.13s"/>
<polygon class="particle" points="180.1,336.2 178.4,339.9 181.9,339.9" fill="#15846e" opacity="0.67" style="animation-delay:-2.77s"/>
<polygon class="particle" points="199.4,335.2 196.5,341.1 202.2,341.1" fill="#8052ff" opacity="0.67" style="animation-delay:-3.69s"/>
<polygon class="particle" points="181.0,327.2 177.9,333.6 184.0,333.6" fill="#8052ff" opacity="0.41" style="animation-delay:-2.46s"/>
<polygon class="particle" points="217.9,350.1 215.2,355.6 220.5,355.6" fill="#ffb829" opacity="0.55" style="animation-delay:-1.50s"/>
<polygon class="particle" points="204.3,297.2 201.6,302.7 206.9,302.7" fill="#8052ff" opacity="0.79" style="animation-delay:-0.41s"/>
<polygon class="particle" points="201.2,292.9 198.8,297.8 203.5,297.8" fill="#d04dff" opacity="0.75" style="animation-delay:-2.66s"/>
<polygon class="particle" points="235.2,339.8 232.2,346.0 238.2,346.0" fill="#15846e" opacity="0.82" style="animation-delay:-0.62s"/>
<polygon class="particle" points="235.7,352.3 233.8,356.2 237.5,356.2" fill="#8052ff" opacity="0.64" style="animation-delay:-3.25s"/>
<polygon class="particle" points="233.6,321.6 232.4,324.1 234.9,324.1" fill="#8052ff" opacity="0.49" style="animation-delay:-3.96s"/>
<polygon class="particle" points="193.3,308.3 190.7,313.7 195.9,313.7" fill="#d04dff" opacity="0.40" style="animation-delay:-3.64s"/>
<polygon class="particle" points="232.3,350.3 230.5,353.9 234.0,353.9" fill="#8052ff" opacity="0.49" style="animation-delay:-0.97s"/>
<polygon class="particle" points="186.8,343.5 184.7,347.7 188.8,347.7" fill="#15846e" opacity="0.97" style="animation-delay:-1.61s"/>
<polygon class="particle" points="204.9,338.7 203.3,341.9 206.4,341.9" fill="#ffb829" opacity="0.79" style="animation-delay:-0.86s"/>
<polygon class="particle" points="186.0,308.8 182.8,315.3 189.1,315.3" fill="#f4f0ff" opacity="0.49" style="animation-delay:-1.16s"/>
<polygon class="particle" points="175.0,320.0 173.1,324.1 177.0,324.1" fill="#f4f0ff" opacity="0.88" style="animation-delay:-3.58s"/>
<polygon class="particle" points="199.7,299.1 197.5,303.6 201.9,303.6" fill="#46a7ff" opacity="0.70" style="animation-delay:-3.34s"/>
<polygon class="particle" points="202.3,337.9 199.6,343.4 204.9,343.4" fill="#8052ff" opacity="0.70" style="animation-delay:-3.48s"/>
<polygon class="particle" points="187.9,304.0 185.5,308.9 190.2,308.9" fill="#d04dff" opacity="0.73" style="animation-delay:-0.64s"/>
<polygon class="particle" points="239.4,330.6 236.9,335.8 241.9,335.8" fill="#15846e" opacity="0.47" style="animation-delay:-0.01s"/>
<polygon class="particle" points="223.9,334.0 222.3,337.3 225.5,337.3" fill="#15846e" opacity="0.49" style="animation-delay:-3.86s"/>
<polygon class="particle" points="200.6,346.8 198.6,350.9 202.6,350.9" fill="#ff7dcb" opacity="0.74" style="animation-delay:-0.94s"/>
<polygon class="particle" points="208.6,337.1 206.0,342.5 211.2,342.5" fill="#d04dff" opacity="0.95" style="animation-delay:-3.70s"/>
<polygon class="particle" points="241.4,306.4 238.5,312.4 244.3,312.4" fill="#ffb829" opacity="0.83" style="animation-delay:-0.35s"/>
<polygon class="particle" points="184.6,328.2 182.7,332.0 186.4,332.0" fill="#f4f0ff" opacity="0.81" style="animation-delay:-3.26s"/>
<polygon class="particle" points="183.4,323.9 182.2,326.4 184.6,326.4" fill="#8052ff" opacity="0.42" style="animation-delay:-2.01s"/>
<polygon class="particle" points="213.9,298.9 211.5,304.0 216.4,304.0" fill="#46a7ff" opacity="0.47" style="animation-delay:-2.73s"/>
<polygon class="particle" points="224.9,329.8 221.9,336.1 227.9,336.1" fill="#46a7ff" opacity="0.56" style="animation-delay:-3.61s"/>
<polygon class="particle" points="177.6,325.8 175.6,330.0 179.7,330.0" fill="#46a7ff" opacity="0.85" style="animation-delay:-2.83s"/>
<polygon class="particle" points="223.1,314.9 221.6,317.9 224.6,317.9" fill="#ffb829" opacity="0.50" style="animation-delay:-0.75s"/>
<polygon class="particle" points="197.9,298.3 196.7,300.8 199.1,300.8" fill="#ffb829" opacity="0.72" style="animation-delay:-1.95s"/>
<polygon class="particle" points="186.9,327.3 185.2,330.9 188.7,330.9" fill="#8052ff" opacity="0.73" style="animation-delay:-0.57s"/>
<polygon class="particle" points="224.8,330.2 222.4,335.2 227.2,335.2" fill="#46a7ff" opacity="0.72" style="animation-delay:-3.73s"/>
<polygon class="particle" points="226.1,293.6 223.4,299.0 228.7,299.0" fill="#46a7ff" opacity="0.61" style="animation-delay:-0.00s"/>
<polygon class="particle" points="222.4,320.4 220.7,323.9 224.1,323.9" fill="#ff7dcb" opacity="0.70" style="animation-delay:-3.22s"/>
<polygon class="particle" points="190.2,296.4 188.1,300.8 192.3,300.8" fill="#46a7ff" opacity="0.69" style="animation-delay:-2.86s"/>
<polygon class="particle" points="215.2,328.4 212.4,334.1 218.0,334.1" fill="#15846e" opacity="0.81" style="animation-delay:-3.71s"/>
<polygon class="particle" points="204.2,304.5 201.5,310.0 206.9,310.0" fill="#8052ff" opacity="0.84" style="animation-delay:-2.88s"/>
<polygon class="particle" points="177.5,312.1 174.8,317.6 180.2,317.6" fill="#f4f0ff" opacity="0.48" style="animation-delay:-0.09s"/>
<polygon class="particle" points="219.7,330.8 217.5,335.1 221.8,335.1" fill="#ffb829" opacity="0.56" style="animation-delay:-0.46s"/>
<polygon class="particle" points="180.7,322.1 178.6,326.4 182.8,326.4" fill="#46a7ff" opacity="0.90" style="animation-delay:-0.65s"/>
<polygon class="particle" points="240.1,335.5 237.8,340.3 242.4,340.3" fill="#f4f0ff" opacity="0.67" style="animation-delay:-0.46s"/>
<polygon class="particle" points="199.6,292.9 197.4,297.4 201.8,297.4" fill="#8052ff" opacity="0.66" style="animation-delay:-2.24s"/>
<polygon class="particle" points="231.5,327.4 229.7,331.1 233.3,331.1" fill="#46a7ff" opacity="0.85" style="animation-delay:-3.73s"/>
<polygon class="particle" points="211.5,310.4 208.8,316.0 214.2,316.0" fill="#46a7ff" opacity="0.96" style="animation-delay:-1.31s"/>
<polygon class="particle" points="207.3,336.3 205.8,339.5 208.9,339.5" fill="#ffb829" opacity="0.49" style="animation-delay:-1.46s"/>
<polygon class="particle" points="234.2,321.9 231.5,327.4 236.8,327.4" fill="#15846e" opacity="0.68" style="animation-delay:-2.67s"/>
<polygon class="particle" points="194.2,349.1 192.5,352.8 196.0,352.8" fill="#f4f0ff" opacity="0.85" style="animation-delay:-0.93s"/>
<polygon class="particle" points="213.9,354.7 211.4,359.9 216.5,359.9" fill="#ffb829" opacity="0.92" style="animation-delay:-1.25s"/>
<polygon class="particle" points="242.5,346.8 240.1,351.7 244.9,351.7" fill="#ffb829" opacity="0.51" style="animation-delay:-3.88s"/>
<polygon class="particle" points="242.5,320.1 239.7,325.8 245.2,325.8" fill="#ff7dcb" opacity="0.92" style="animation-delay:-1.96s"/>
<polygon class="particle" points="246.5,330.3 244.1,335.2 248.8,335.2" fill="#8052ff" opacity="0.91" style="animation-delay:-1.42s"/>
<polygon class="particle" points="194.6,338.5 191.8,344.3 197.5,344.3" fill="#ffb829" opacity="0.41" style="animation-delay:-0.70s"/>
<polygon class="particle" points="212.7,312.5 210.4,317.4 215.1,317.4" fill="#ffb829" opacity="0.70" style="animation-delay:-0.89s"/>
<polygon class="particle" points="185.4,312.6 182.6,318.3 188.2,318.3" fill="#15846e" opacity="0.75" style="animation-delay:-0.24s"/>
<polygon class="particle" points="212.3,323.1 209.1,329.5 215.4,329.5" fill="#15846e" opacity="0.94" style="animation-delay:-3.14s"/>
<polygon class="particle" points="234.6,323.9 233.2,326.7 236.0,326.7" fill="#ff7dcb" opacity="0.91" style="animation-delay:-0.51s"/>
<polygon class="particle" points="205.4,321.3 202.6,327.2 208.3,327.2" fill="#f4f0ff" opacity="0.69" style="animation-delay:-1.03s"/>
<polygon class="particle" points="226.3,334.2 224.5,338.0 228.1,338.0" fill="#f4f0ff" opacity="0.53" style="animation-delay:-2.74s"/>
<polygon class="particle" points="178.4,337.4 176.0,342.5 180.9,342.5" fill="#ffb829" opacity="0.66" style="animation-delay:-2.62s"/>
<polygon class="particle" points="223.4,293.0 220.6,298.8 226.2,298.8" fill="#f4f0ff" opacity="0.45" style="animation-delay:-2.61s"/>
<polygon class="particle" points="244.6,323.3 241.9,328.9 247.3,328.9" fill="#8052ff" opacity="0.82" style="animation-delay:-0.91s"/>
<polygon class="particle" points="193.8,323.8 190.9,329.7 196.6,329.7" fill="#8052ff" opacity="0.75" style="animation-delay:-0.18s"/>
<polygon class="particle" points="220.6,344.6 217.6,350.7 223.6,350.7" fill="#ffb829" opacity="0.90" style="animation-delay:-0.71s"/>
<polygon class="particle" points="223.5,309.4 221.9,312.6 225.1,312.6" fill="#f4f0ff" opacity="0.71" style="animation-delay:-1.06s"/>
<polygon class="particle" points="206.3,291.7 204.4,295.7 208.2,295.7" fill="#8052ff" opacity="0.70" style="animation-delay:-3.48s"/>
<polygon class="particle" points="204.9,297.4 203.0,301.3 206.8,301.3" fill="#ffb829" opacity="0.54" style="animation-delay:-3.45s"/>
<polygon class="particle" points="246.3,337.0 244.3,341.1 248.4,341.1" fill="#f4f0ff" opacity="0.59" style="animation-delay:-1.03s"/>
<polygon class="particle" points="219.9,317.4 218.7,320.0 221.2,320.0" fill="#f4f0ff" opacity="0.75" style="animation-delay:-0.38s"/>
<polygon class="particle" points="197.2,296.0 195.0,300.5 199.5,300.5" fill="#46a7ff" opacity="0.54" style="animation-delay:-2.80s"/>
<polygon class="particle" points="186.7,310.8 183.8,316.7 189.6,316.7" fill="#f4f0ff" opacity="0.54" style="animation-delay:-2.44s"/>
<polygon class="particle" points="223.2,354.0 222.0,356.5 224.4,356.5" fill="#d04dff" opacity="0.58" style="animation-delay:-3.18s"/>
<polygon class="particle" points="217.8,301.6 215.2,307.1 220.5,307.1" fill="#f4f0ff" opacity="0.45" style="animation-delay:-2.37s"/>
<polygon class="particle" points="199.8,356.4 198.0,360.3 201.7,360.3" fill="#ff7dcb" opacity="0.66" style="animation-delay:-0.24s"/>
<polygon class="particle" points="214.4,360.0 212.6,363.7 216.2,363.7" fill="#ff7dcb" opacity="0.92" style="animation-delay:-3.78s"/>
<polygon class="particle" points="219.7,291.8 216.6,298.1 222.7,298.1" fill="#8052ff" opacity="0.72" style="animation-delay:-2.54s"/>
<polygon class="particle" points="187.0,333.8 185.4,337.0 188.5,337.0" fill="#f4f0ff" opacity="0.94" style="animation-delay:-2.21s"/>
<polygon class="particle" points="207.3,314.8 204.9,319.8 209.7,319.8" fill="#d04dff" opacity="0.49" style="animation-delay:-0.82s"/>
<polygon class="particle" points="243.4,312.1 241.7,315.7 245.2,315.7" fill="#d04dff" opacity="0.66" style="animation-delay:-2.34s"/>
<polygon class="particle" points="217.3,318.0 215.7,321.2 218.9,321.2" fill="#d04dff" opacity="0.84" style="animation-delay:-2.50s"/>
<polygon class="particle" points="236.3,313.4 234.5,317.2 238.1,317.2" fill="#d04dff" opacity="0.71" style="animation-delay:-2.68s"/>
<polygon class="particle" points="174.3,331.5 171.6,337.2 177.1,337.2" fill="#ff7dcb" opacity="0.46" style="animation-delay:-3.36s"/>
<polygon class="particle" points="243.1,312.9 240.6,318.1 245.6,318.1" fill="#15846e" opacity="0.95" style="animation-delay:-3.09s"/>
<polygon class="particle" points="223.2,322.7 220.9,327.3 225.4,327.3" fill="#f4f0ff" opacity="0.80" style="animation-delay:-2.08s"/>
<polygon class="particle" points="241.9,328.9 240.5,331.7 243.2,331.7" fill="#46a7ff" opacity="0.79" style="animation-delay:-1.52s"/>
<polygon class="particle" points="233.3,349.2 230.4,355.1 236.2,355.1" fill="#46a7ff" opacity="0.95" style="animation-delay:-0.05s"/>
<polygon class="particle" points="219.3,354.1 216.8,359.3 221.8,359.3" fill="#f4f0ff" opacity="0.75" style="animation-delay:-1.94s"/>
<polygon class="particle" points="205.9,303.4 202.9,309.7 209.0,309.7" fill="#15846e" opacity="0.83" style="animation-delay:-1.55s"/>
<polygon class="particle" points="235.2,340.5 233.1,344.9 237.4,344.9" fill="#ff7dcb" opacity="0.50" style="animation-delay:-3.06s"/>
<polygon class="particle" points="187.1,302.1 185.3,305.8 188.9,305.8" fill="#15846e" opacity="0.84" style="animation-delay:-2.85s"/>
<polygon class="particle" points="196.6,342.7 194.1,347.9 199.1,347.9" fill="#46a7ff" opacity="0.68" style="animation-delay:-0.73s"/>
<polygon class="particle" points="236.3,354.1 233.4,360.1 239.1,360.1" fill="#ffb829" opacity="0.43" style="animation-delay:-3.30s"/>
<polygon class="particle" points="199.8,355.2 197.2,360.5 202.4,360.5" fill="#8052ff" opacity="0.50" style="animation-delay:-2.72s"/>
<polygon class="particle" points="198.4,363.5 197.3,365.8 199.6,365.8" fill="#f4f0ff" opacity="0.73" style="animation-delay:-0.47s"/>
<polygon class="particle" points="226.6,295.6 224.1,300.6 229.0,300.6" fill="#46a7ff" opacity="0.83" style="animation-delay:-2.32s"/>
<polygon class="particle" points="203.4,297.2 201.6,300.9 205.2,300.9" fill="#ffb829" opacity="0.67" style="animation-delay:-0.73s"/>
<polygon class="particle" points="190.4,313.1 189.1,315.8 191.7,315.8" fill="#ffb829" opacity="0.44" style="animation-delay:-0.07s"/>
<polygon class="particle" points="233.1,309.3 231.9,311.7 234.3,311.7" fill="#ffb829" opacity="0.96" style="animation-delay:-0.04s"/>
<polygon class="particle" points="200.7,295.5 198.9,299.2 202.5,299.2" fill="#d04dff" opacity="0.53" style="animation-delay:-3.66s"/>
<polygon class="particle" points="237.4,303.4 234.4,309.5 240.3,309.5" fill="#d04dff" opacity="0.65" style="animation-delay:-1.20s"/>
<polygon class="particle" points="246.4,317.5 243.8,323.0 249.1,323.0" fill="#46a7ff" opacity="0.78" style="animation-delay:-3.01s"/>
<polygon class="particle" points="237.5,353.3 236.2,356.0 238.8,356.0" fill="#46a7ff" opacity="0.88" style="animation-delay:-0.92s"/>
<polygon class="particle" points="231.2,343.8 228.9,348.4 233.4,348.4" fill="#f4f0ff" opacity="0.81" style="animation-delay:-3.95s"/>
<polygon class="particle" points="203.8,305.7 201.5,310.5 206.2,310.5" fill="#f4f0ff" opacity="0.77" style="animation-delay:-0.68s"/>
<polygon class="particle" points="204.5,351.5 203.3,353.9 205.7,353.9" fill="#ffb829" opacity="0.63" style="animation-delay:-0.85s"/>
<polygon class="particle" points="209.0,308.7 206.0,314.9 212.0,314.9" fill="#46a7ff" opacity="0.96" style="animation-delay:-3.26s"/>
<polygon class="particle" points="210.5,351.2 207.6,357.1 213.3,357.1" fill="#8052ff" opacity="0.54" style="animation-delay:-3.58s"/>
<polygon class="particle" points="184.4,345.0 182.0,350.0 186.8,350.0" fill="#f4f0ff" opacity="0.48" style="animation-delay:-3.43s"/>
<polygon class="particle" points="231.5,322.5 230.0,325.5 232.9,325.5" fill="#8052ff" opacity="0.75" style="animation-delay:-2.03s"/>
<polygon class="particle" points="195.6,346.2 193.4,350.7 197.8,350.7" fill="#ffb829" opacity="0.53" style="animation-delay:-1.41s"/>
<polygon class="particle" points="184.5,322.4 182.5,326.3 186.4,326.3" fill="#ffb829" opacity="0.77" style="animation-delay:-3.61s"/>
<polygon class="particle" points="199.6,322.8 196.4,329.3 202.8,329.3" fill="#f4f0ff" opacity="0.90" style="animation-delay:-1.80s"/>
<polygon class="particle" points="217.3,318.8 214.6,324.5 220.0,324.5" fill="#f4f0ff" opacity="0.68" style="animation-delay:-0.14s"/>
<polygon class="particle" points="191.4,333.4 189.7,337.0 193.2,337.0" fill="#8052ff" opacity="0.50" style="animation-delay:-3.95s"/>
<polygon class="particle" points="222.2,315.8 219.2,322.1 225.3,322.1" fill="#f4f0ff" opacity="0.41" style="animation-delay:-2.60s"/>
<polygon class="particle" points="219.4,308.9 217.7,312.4 221.1,312.4" fill="#8052ff" opacity="0.91" style="animation-delay:-1.83s"/>
<polygon class="particle" points="190.5,297.7 188.1,302.7 192.9,302.7" fill="#d04dff" opacity="0.94" style="animation-delay:-0.06s"/>
<polygon class="particle" points="214.1,326.8 210.9,333.3 217.2,333.3" fill="#d04dff" opacity="0.76" style="animation-delay:-2.71s"/>
<polygon class="particle" points="193.5,326.5 190.8,331.9 196.1,331.9" fill="#ffb829" opacity="0.51" style="animation-delay:-0.02s"/>
<polygon class="particle" points="237.8,337.2 236.4,340.0 239.1,340.0" fill="#f4f0ff" opacity="0.44" style="animation-delay:-2.42s"/>
<polygon class="particle" points="200.0,343.0 197.2,348.8 202.8,348.8" fill="#f4f0ff" opacity="0.95" style="animation-delay:-2.05s"/>
<polygon class="particle" points="187.1,313.3 184.8,317.9 189.3,317.9" fill="#ffb829" opacity="0.84" style="animation-delay:-3.39s"/>
<polygon class="particle" points="201.7,330.7 200.5,333.2 202.9,333.2" fill="#ffb829" opacity="0.67" style="animation-delay:-1.12s"/>
<polygon class="particle" points="218.4,295.0 215.4,301.3 221.5,301.3" fill="#46a7ff" opacity="0.48" style="animation-delay:-3.19s"/>
<polygon class="particle" points="222.2,331.6 219.7,336.9 224.8,336.9" fill="#d04dff" opacity="0.71" style="animation-delay:-3.26s"/>
<polygon class="particle" points="227.1,307.7 225.1,311.9 229.2,311.9" fill="#46a7ff" opacity="0.56" style="animation-delay:-2.26s"/>
<polygon class="particle" points="214.7,320.0 212.9,323.8 216.6,323.8" fill="#46a7ff" opacity="0.43" style="animation-delay:-1.55s"/>
<polygon class="particle" points="193.0,331.0 191.6,333.9 194.4,333.9" fill="#8052ff" opacity="0.90" style="animation-delay:-3.94s"/>
<polygon class="particle" points="218.9,349.7 216.0,355.6 221.7,355.6" fill="#ffb829" opacity="0.67" style="animation-delay:-2.66s"/>
<polygon class="particle" points="204.4,343.9 201.2,350.5 207.5,350.5" fill="#f4f0ff" opacity="0.52" style="animation-delay:-3.03s"/>
<polygon class="particle" points="174.9,325.9 173.3,329.0 176.4,329.0" fill="#ffb829" opacity="0.48" style="animation-delay:-0.54s"/>
<polygon class="particle" points="188.2,311.4 185.6,316.7 190.8,316.7" fill="#ffb829" opacity="0.45" style="animation-delay:-2.69s"/>
<polygon class="particle" points="232.8,343.4 231.5,346.2 234.1,346.2" fill="#f4f0ff" opacity="0.51" style="animation-delay:-1.85s"/>
<polygon class="particle" points="190.4,322.3 188.9,325.4 192.0,325.4" fill="#8052ff" opacity="0.75" style="animation-delay:-2.81s"/>
<polygon class="particle" points="178.3,314.7 176.9,317.5 179.6,317.5" fill="#15846e" opacity="0.93" style="animation-delay:-0.68s"/>
<polygon class="particle" points="218.6,355.6 215.5,362.0 221.7,362.0" fill="#f4f0ff" opacity="0.46" style="animation-delay:-1.65s"/>
<polygon class="particle" points="203.5,342.0 201.5,346.2 205.5,346.2" fill="#8052ff" opacity="0.75" style="animation-delay:-3.56s"/>
<polygon class="particle" points="242.2,338.2 239.0,344.7 245.3,344.7" fill="#f4f0ff" opacity="0.65" style="animation-delay:-1.00s"/>
<polygon class="particle" points="209.8,362.9 208.0,366.7 211.7,366.7" fill="#46a7ff" opacity="0.94" style="animation-delay:-1.08s"/>
<polygon class="particle" points="220.3,306.8 218.5,310.4 222.0,310.4" fill="#8052ff" opacity="0.54" style="animation-delay:-3.66s"/>
<polygon class="particle" points="206.0,303.9 204.8,306.4 207.2,306.4" fill="#ffb829" opacity="0.78" style="animation-delay:-2.08s"/>
<polygon class="particle" points="190.0,333.0 187.6,338.0 192.4,338.0" fill="#15846e" opacity="0.53" style="animation-delay:-2.50s"/>
<polygon class="particle" points="216.7,335.1 215.3,338.0 218.1,338.0" fill="#d04dff" opacity="0.85" style="animation-delay:-0.68s"/>
<polygon class="particle" points="219.6,347.3 218.0,350.7 221.3,350.7" fill="#f4f0ff" opacity="0.92" style="animation-delay:-2.15s"/>
<polygon class="particle" points="208.6,314.2 205.8,320.0 211.3,320.0" fill="#8052ff" opacity="0.41" style="animation-delay:-1.37s"/>
<polygon class="particle" points="244.0,340.1 241.8,344.5 246.1,344.5" fill="#46a7ff" opacity="0.59" style="animation-delay:-3.92s"/>
<polygon class="particle" points="232.0,330.3 229.9,334.8 234.2,334.8" fill="#46a7ff" opacity="0.64" style="animation-delay:-1.18s"/>
<polygon class="particle" points="222.4,333.1 221.1,335.7 223.6,335.7" fill="#f4f0ff" opacity="0.54" style="animation-delay:-1.81s"/>
<polygon class="particle" points="246.7,336.1 244.8,340.2 248.7,340.2" fill="#f4f0ff" opacity="0.66" style="animation-delay:-3.68s"/>
<polygon class="particle" points="217.3,313.0 215.3,317.2 219.3,317.2" fill="#8052ff" opacity="0.44" style="animation-delay:-3.84s"/>
<polygon class="particle" points="217.0,321.9 215.6,324.8 218.4,324.8" fill="#f4f0ff" opacity="0.91" style="animation-delay:-3.77s"/>
<polygon class="particle" points="195.0,329.4 193.9,331.8 196.2,331.8" fill="#f4f0ff" opacity="0.42" style="animation-delay:-1.07s"/>
<polygon class="particle" points="210.4,335.0 209.3,337.5 211.6,337.5" fill="#d04dff" opacity="0.98" style="animation-delay:-0.30s"/>
<polygon class="particle" points="183.7,324.8 180.6,331.2 186.8,331.2" fill="#46a7ff" opacity="0.88" style="animation-delay:-2.70s"/>
<polygon class="particle" points="215.0,349.0 212.1,354.8 217.8,354.8" fill="#46a7ff" opacity="0.92" style="animation-delay:-3.41s"/>
<polygon class="particle" points="192.3,329.4 190.3,333.5 194.3,333.5" fill="#8052ff" opacity="0.48" style="animation-delay:-0.72s"/>
<polygon class="particle" points="225.8,300.6 224.5,303.3 227.1,303.3" fill="#d04dff" opacity="0.55" style="animation-delay:-2.91s"/>
<polygon class="particle" points="186.7,349.6 184.2,354.8 189.3,354.8" fill="#8052ff" opacity="0.92" style="animation-delay:-0.49s"/>
<polygon class="particle" points="174.6,319.2 171.8,324.9 177.4,324.9" fill="#15846e" opacity="0.89" style="animation-delay:-3.47s"/>
<polygon class="particle" points="191.9,353.0 189.0,358.8 194.7,358.8" fill="#d04dff" opacity="0.77" style="animation-delay:-0.32s"/>
<polygon class="particle" points="205.9,313.4 203.8,317.7 208.0,317.7" fill="#f4f0ff" opacity="0.64" style="animation-delay:-1.41s"/>
<polygon class="particle" points="236.6,348.3 233.9,353.9 239.3,353.9" fill="#ffb829" opacity="0.86" style="animation-delay:-0.08s"/>
<polygon class="particle" points="205.8,301.8 203.3,306.7 208.2,306.7" fill="#f4f0ff" opacity="0.81" style="animation-delay:-0.17s"/>
<polygon class="particle" points="230.3,340.7 227.3,347.0 233.4,347.0" fill="#46a7ff" opacity="0.80" style="animation-delay:-1.50s"/>
<polygon class="particle" points="207.7,308.3 204.6,314.7 210.8,314.7" fill="#8052ff" opacity="0.77" style="animation-delay:-2.45s"/>
<polygon class="particle" points="203.1,330.5 200.3,336.3 205.9,336.3" fill="#f4f0ff" opacity="0.92" style="animation-delay:-3.97s"/>
<polygon class="particle" points="218.3,324.2 216.3,328.3 220.4,328.3" fill="#d04dff" opacity="0.73" style="animation-delay:-2.05s"/>
<polygon class="particle" points="224.6,344.8 223.1,347.7 226.0,347.7" fill="#d04dff" opacity="0.93" style="animation-delay:-3.99s"/>
<polygon class="particle" points="235.0,302.1 232.6,307.2 237.5,307.2" fill="#15846e" opacity="0.51" style="animation-delay:-0.98s"/>
<polygon class="particle" points="246.6,323.4 244.8,327.3 248.5,327.3" fill="#f4f0ff" opacity="0.92" style="animation-delay:-2.36s"/>
<polygon class="particle" points="178.7,331.0 177.1,334.2 180.2,334.2" fill="#d04dff" opacity="0.79" style="animation-delay:-2.72s"/>
<polygon class="particle" points="193.6,327.3 191.2,332.3 196.0,332.3" fill="#d04dff" opacity="0.88" style="animation-delay:-1.72s"/>
<polygon class="particle" points="226.3,346.4 223.4,352.3 229.1,352.3" fill="#8052ff" opacity="0.57" style="animation-delay:-0.01s"/>
<polygon class="particle" points="215.3,296.5 213.5,300.3 217.1,300.3" fill="#ffb829" opacity="0.41" style="animation-delay:-2.01s"/>
<polygon class="particle" points="194.9,346.5 193.4,349.6 196.4,349.6" fill="#f4f0ff" opacity="0.84" style="animation-delay:-3.78s"/>
<polygon class="particle" points="194.1,353.5 193.0,355.9 195.3,355.9" fill="#8052ff" opacity="0.52" style="animation-delay:-3.32s"/>
<polygon class="particle" points="189.7,347.4 186.6,353.7 192.8,353.7" fill="#8052ff" opacity="0.69" style="animation-delay:-1.38s"/>
<polygon class="particle" points="243.8,332.6 242.4,335.5 245.2,335.5" fill="#ffb829" opacity="0.87" style="animation-delay:-3.57s"/>
<polygon class="particle" points="221.8,353.1 220.1,356.7 223.6,356.7" fill="#ff7dcb" opacity="0.56" style="animation-delay:-3.74s"/>
<polygon class="particle" points="232.1,314.7 229.2,320.7 235.1,320.7" fill="#d04dff" opacity="0.85" style="animation-delay:-1.71s"/>
<polygon class="particle" points="214.5,338.4 212.6,342.2 216.3,342.2" fill="#46a7ff" opacity="0.44" style="animation-delay:-2.64s"/>
<polygon class="particle" points="175.8,334.6 173.9,338.5 177.7,338.5" fill="#d04dff" opacity="0.58" style="animation-delay:-0.54s"/>
<polygon class="particle" points="194.3,330.2 192.5,333.9 196.1,333.9" fill="#d04dff" opacity="0.77" style="animation-delay:-1.16s"/>
<polygon class="particle" points="186.0,343.9 183.6,348.9 188.4,348.9" fill="#f4f0ff" opacity="0.53" style="animation-delay:-3.33s"/>
<polygon class="particle" points="203.0,338.1 201.1,342.0 204.8,342.0" fill="#ffb829" opacity="0.86" style="animation-delay:-2.88s"/>
<polygon class="particle" points="241.3,312.7 239.8,315.7 242.7,315.7" fill="#46a7ff" opacity="0.96" style="animation-delay:-2.21s"/>
<polygon class="particle" points="196.0,296.5 193.9,300.8 198.1,300.8" fill="#d04dff" opacity="0.87" style="animation-delay:-1.07s"/>
<polygon class="particle" points="216.3,362.6 213.7,367.8 218.8,367.8" fill="#f4f0ff" opacity="0.70" style="animation-delay:-1.26s"/>
<polygon class="particle" points="184.7,328.1 183.5,330.5 185.9,330.5" fill="#8052ff" opacity="0.45" style="animation-delay:-1.28s"/>
<polygon class="particle" points="221.0,292.1 218.5,297.3 223.5,297.3" fill="#8052ff" opacity="0.90" style="animation-delay:-0.86s"/>
<polygon class="particle" points="199.7,334.5 196.9,340.2 202.5,340.2" fill="#ffb829" opacity="0.46" style="animation-delay:-2.55s"/>
<polygon class="particle" points="219.8,335.4 217.9,339.3 221.7,339.3" fill="#15846e" opacity="0.46" style="animation-delay:-1.93s"/>
<polygon class="particle" points="219.6,353.8 216.7,360.0 222.6,360.0" fill="#ffb829" opacity="0.90" style="animation-delay:-0.96s"/>
<polygon class="particle" points="210.8,294.5 208.1,300.1 213.5,300.1" fill="#8052ff" opacity="0.73" style="animation-delay:-0.90s"/>
<polygon class="particle" points="210.3,310.2 208.5,314.0 212.1,314.0" fill="#f4f0ff" opacity="0.50" style="animation-delay:-2.75s"/>
<polygon class="particle" points="212.2,299.9 209.8,304.9 214.7,304.9" fill="#ff7dcb" opacity="0.46" style="animation-delay:-3.14s"/>
<polygon class="particle" points="234.0,355.3 231.8,359.9 236.2,359.9" fill="#8052ff" opacity="0.82" style="animation-delay:-2.39s"/>
<polygon class="particle" points="230.7,351.0 228.1,356.3 233.3,356.3" fill="#f4f0ff" opacity="0.49" style="animation-delay:-2.00s"/>
<polygon class="particle" points="241.3,343.1 238.2,349.5 244.5,349.5" fill="#f4f0ff" opacity="0.73" style="animation-delay:-3.75s"/>
<polygon class="particle" points="201.0,346.7 198.1,352.8 204.0,352.8" fill="#46a7ff" opacity="0.85" style="animation-delay:-2.51s"/>
<polygon class="particle" points="182.6,302.0 180.4,306.4 184.8,306.4" fill="#8052ff" opacity="0.67" style="animation-delay:-3.39s"/>
<polygon class="particle" points="213.9,343.9 211.8,348.3 216.0,348.3" fill="#d04dff" opacity="0.47" style="animation-delay:-0.53s"/>
<polygon class="particle" points="226.1,305.2 224.8,307.9 227.4,307.9" fill="#8052ff" opacity="0.61" style="animation-delay:-2.23s"/>
<polygon class="particle" points="193.0,328.9 190.5,333.9 195.4,333.9" fill="#8052ff" opacity="0.94" style="animation-delay:-0.94s"/>
<polygon class="particle" points="237.0,311.9 235.5,315.1 238.6,315.1" fill="#f4f0ff" opacity="0.91" style="animation-delay:-0.52s"/>
<polygon class="particle" points="221.5,301.9 219.7,305.6 223.3,305.6" fill="#f4f0ff" opacity="0.65" style="animation-delay:-0.55s"/>
<polygon class="particle" points="200.6,356.1 197.5,362.5 203.7,362.5" fill="#d04dff" opacity="0.69" style="animation-delay:-3.66s"/>
<polygon class="particle" points="234.8,339.7 232.8,343.9 236.8,343.9" fill="#d04dff" opacity="0.74" style="animation-delay:-0.02s"/>
<polygon class="particle" points="189.1,317.7 188.0,320.0 190.2,320.0" fill="#ffb829" opacity="0.42" style="animation-delay:-0.13s"/>
<polygon class="particle" points="216.0,297.2 214.7,299.8 217.2,299.8" fill="#8052ff" opacity="0.93" style="animation-delay:-0.19s"/>
<polygon class="particle" points="247.1,327.6 244.0,334.0 250.2,334.0" fill="#ffb829" opacity="0.43" style="animation-delay:-0.65s"/>
<polygon class="particle" points="207.1,293.7 205.0,297.9 209.1,297.9" fill="#8052ff" opacity="0.93" style="animation-delay:-2.75s"/>
<polygon class="particle" points="206.0,358.0 202.8,364.6 209.2,364.6" fill="#ff7dcb" opacity="0.69" style="animation-delay:-3.72s"/>
<polygon class="particle" points="221.3,304.1 218.3,310.2 224.3,310.2" fill="#8052ff" opacity="0.92" style="animation-delay:-1.78s"/>
<polygon class="particle" points="232.2,337.1 230.5,340.5 233.8,340.5" fill="#d04dff" opacity="0.60" style="animation-delay:-3.23s"/>
<polygon class="particle" points="192.9,317.1 191.0,321.1 194.8,321.1" fill="#8052ff" opacity="0.65" style="animation-delay:-3.20s"/>
<polygon class="particle" points="194.3,312.7 193.0,315.4 195.7,315.4" fill="#f4f0ff" opacity="0.55" style="animation-delay:-1.72s"/>
<polygon class="particle" points="217.1,340.8 214.0,347.3 220.3,347.3" fill="#d04dff" opacity="0.51" style="animation-delay:-3.51s"/>
<polygon class="particle" points="190.7,296.4 188.0,302.0 193.4,302.0" fill="#ffb829" opacity="0.57" style="animation-delay:-3.16s"/>
<polygon class="particle" points="189.3,298.0 187.6,301.5 191.0,301.5" fill="#8052ff" opacity="0.67" style="animation-delay:-0.56s"/>
<polygon class="particle" points="199.5,330.9 198.3,333.4 200.6,333.4" fill="#15846e" opacity="0.52" style="animation-delay:-0.98s"/>
<polygon class="particle" points="226.2,341.0 224.4,344.6 227.9,344.6" fill="#ffb829" opacity="0.50" style="animation-delay:-3.88s"/>
<polygon class="particle" points="189.0,356.4 187.4,359.7 190.6,359.7" fill="#f4f0ff" opacity="0.85" style="animation-delay:-3.10s"/>
<polygon class="particle" points="202.5,313.4 201.0,316.4 203.9,316.4" fill="#8052ff" opacity="0.70" style="animation-delay:-0.65s"/>
<polygon class="particle" points="221.4,347.1 219.8,350.4 223.0,350.4" fill="#f4f0ff" opacity="0.97" style="animation-delay:-1.19s"/>
<polygon class="particle" points="183.7,334.5 182.4,337.3 185.1,337.3" fill="#ffb829" opacity="0.66" style="animation-delay:-3.21s"/>
<polygon class="particle" points="204.1,336.2 202.8,339.0 205.5,339.0" fill="#8052ff" opacity="0.82" style="animation-delay:-3.73s"/>
<polygon class="particle" points="212.9,346.7 210.8,351.0 214.9,351.0" fill="#d04dff" opacity="0.69" style="animation-delay:-3.27s"/>
<polygon class="particle" points="202.2,365.3 200.2,369.3 204.1,369.3" fill="#46a7ff" opacity="0.81" style="animation-delay:-0.99s"/>
<polygon class="particle" points="217.7,290.1 214.8,296.2 220.7,296.2" fill="#ffb829" opacity="0.48" style="animation-delay:-0.58s"/>
<polygon class="particle" points="188.1,342.7 185.0,349.2 191.3,349.2" fill="#ff7dcb" opacity="0.42" style="animation-delay:-0.70s"/>
<polygon class="particle" points="233.5,352.7 230.8,358.2 236.2,358.2" fill="#8052ff" opacity="0.82" style="animation-delay:-3.45s"/>
<polygon class="particle" points="183.7,307.7 181.9,311.4 185.5,311.4" fill="#8052ff" opacity="0.56" style="animation-delay:-2.28s"/>
<polygon class="particle" points="207.1,363.6 204.7,368.6 209.5,368.6" fill="#f4f0ff" opacity="0.58" style="animation-delay:-2.47s"/>
<polygon class="particle" points="185.7,342.6 183.0,348.2 188.3,348.2" fill="#f4f0ff" opacity="0.64" style="animation-delay:-1.78s"/>
<polygon class="particle" points="212.8,365.5 210.2,371.0 215.5,371.0" fill="#46a7ff" opacity="0.51" style="animation-delay:-2.57s"/>
<polygon class="particle" points="188.4,297.0 185.3,303.4 191.5,303.4" fill="#d04dff" opacity="0.90" style="animation-delay:-2.36s"/>
<polygon class="particle" points="179.6,309.3 178.1,312.3 181.0,312.3" fill="#d04dff" opacity="0.81" style="animation-delay:-3.27s"/>
<polygon class="particle" points="218.9,350.3 217.0,354.3 220.8,354.3" fill="#8052ff" opacity="0.91" style="animation-delay:-2.59s"/>
<polygon class="particle" points="186.8,326.9 183.7,333.4 190.0,333.4" fill="#ffb829" opacity="0.74" style="animation-delay:-1.54s"/>
<polygon class="particle" points="205.9,311.4 203.7,315.9 208.1,315.9" fill="#46a7ff" opacity="0.68" style="animation-delay:-2.51s"/>
<polygon class="particle" points="187.8,323.9 185.2,329.3 190.3,329.3" fill="#f4f0ff" opacity="0.67" style="animation-delay:-3.93s"/>
<polygon class="particle" points="185.7,302.3 183.8,306.3 187.6,306.3" fill="#ff7dcb" opacity="0.50" style="animation-delay:-0.60s"/>
<polygon class="particle" points="188.1,300.9 186.2,304.9 190.0,304.9" fill="#f4f0ff" opacity="0.56" style="animation-delay:-2.97s"/>
<polygon class="particle" points="177.2,314.8 176.0,317.2 178.4,317.2" fill="#46a7ff" opacity="0.74" style="animation-delay:-3.80s"/>
<polygon class="particle" points="209.4,320.6 207.1,325.3 211.6,325.3" fill="#f4f0ff" opacity="0.57" style="animation-delay:-0.01s"/>
<polygon class="particle" points="203.7,332.4 200.6,338.9 206.9,338.9" fill="#d04dff" opacity="0.92" style="animation-delay:-0.48s"/>
<polygon class="particle" points="232.8,357.7 231.2,360.8 234.3,360.8" fill="#ffb829" opacity="0.81" style="animation-delay:-0.88s"/>
<polygon class="particle" points="184.7,354.9 183.4,357.5 185.9,357.5" fill="#f4f0ff" opacity="0.96" style="animation-delay:-1.47s"/>
<polygon class="particle" points="187.4,298.5 184.6,304.3 190.2,304.3" fill="#ffb829" opacity="0.82" style="animation-delay:-2.73s"/>
<polygon class="particle" points="191.1,360.5 188.5,365.9 193.7,365.9" fill="#8052ff" opacity="0.60" style="animation-delay:-2.96s"/>
<polygon class="particle" points="187.4,306.1 185.9,309.3 189.0,309.3" fill="#46a7ff" opacity="0.60" style="animation-delay:-0.52s"/>
<polygon class="particle" points="210.2,305.8 208.4,309.5 211.9,309.5" fill="#ff7dcb" opacity="0.63" style="animation-delay:-2.84s"/>
<polygon class="particle" points="181.6,323.6 179.6,327.8 183.6,327.8" fill="#f4f0ff" opacity="0.84" style="animation-delay:-3.76s"/>
<polygon class="particle" points="177.9,320.8 176.4,323.8 179.4,323.8" fill="#ffb829" opacity="0.61" style="animation-delay:-1.93s"/>
<polygon class="particle" points="205.5,350.4 202.3,357.0 208.7,357.0" fill="#8052ff" opacity="0.58" style="animation-delay:-3.17s"/>
<polygon class="particle" points="188.3,306.1 185.4,311.9 191.1,311.9" fill="#8052ff" opacity="0.54" style="animation-delay:-0.53s"/>
<polygon class="particle" points="203.9,299.5 201.6,304.2 206.2,304.2" fill="#f4f0ff" opacity="0.75" style="animation-delay:-1.40s"/>
<polygon class="particle" points="195.3,298.4 193.8,301.6 196.9,301.6" fill="#46a7ff" opacity="0.73" style="animation-delay:-0.03s"/>
<polygon class="particle" points="194.7,299.2 193.3,302.0 196.0,302.0" fill="#f4f0ff" opacity="0.57" style="animation-delay:-2.21s"/>
<polygon class="particle" points="236.9,338.1 234.4,343.3 239.5,343.3" fill="#ffb829" opacity="0.92" style="animation-delay:-1.15s"/>
<polygon class="particle" points="194.9,309.0 191.8,315.5 198.0,315.5" fill="#46a7ff" opacity="0.69" style="animation-delay:-2.28s"/>
<polygon class="particle" points="195.6,298.1 192.9,303.6 198.3,303.6" fill="#f4f0ff" opacity="0.77" style="animation-delay:-0.88s"/>
<polygon class="particle" points="223.1,304.0 221.0,308.3 225.2,308.3" fill="#d04dff" opacity="0.44" style="animation-delay:-1.91s"/>
<polygon class="particle" points="240.9,346.5 238.5,351.5 243.3,351.5" fill="#ffb829" opacity="0.55" style="animation-delay:-3.29s"/>
<polygon class="particle" points="242.0,348.9 240.0,352.9 244.0,352.9" fill="#ffb829" opacity="0.88" style="animation-delay:-2.19s"/>
<polygon class="particle" points="235.8,326.4 234.5,329.3 237.2,329.3" fill="#46a7ff" opacity="0.74" style="animation-delay:-2.53s"/>
<polygon class="particle" points="226.4,310.5 223.6,316.4 229.3,316.4" fill="#d04dff" opacity="0.66" style="animation-delay:-3.93s"/>
<polygon class="particle" points="200.0,308.7 197.8,313.2 202.2,313.2" fill="#ffb829" opacity="0.77" style="animation-delay:-2.45s"/>
<polygon class="particle" points="192.5,312.7 191.2,315.3 193.8,315.3" fill="#8052ff" opacity="0.73" style="animation-delay:-0.87s"/>
<polygon class="particle" points="218.1,329.0 215.3,334.8 220.9,334.8" fill="#15846e" opacity="0.42" style="animation-delay:-3.82s"/>
<polygon class="particle" points="232.4,356.2 229.9,361.3 234.8,361.3" fill="#ffb829" opacity="0.64" style="animation-delay:-0.05s"/>
<polygon class="particle" points="218.7,321.8 215.8,327.9 221.7,327.9" fill="#f4f0ff" opacity="0.65" style="animation-delay:-3.41s"/>
<polygon class="particle" points="185.5,333.8 183.2,338.4 187.7,338.4" fill="#d04dff" opacity="0.52" style="animation-delay:-3.22s"/>
<polygon class="particle" points="191.4,346.4 188.5,352.4 194.4,352.4" fill="#8052ff" opacity="0.73" style="animation-delay:-1.64s"/>
<polygon class="particle" points="217.2,364.0 215.0,368.5 219.3,368.5" fill="#ff7dcb" opacity="0.40" style="animation-delay:-3.08s"/>
<polygon class="particle" points="174.3,339.3 172.3,343.5 176.4,343.5" fill="#46a7ff" opacity="0.55" style="animation-delay:-3.45s"/>
<polygon class="particle" points="242.0,344.2 239.5,349.3 244.4,349.3" fill="#f4f0ff" opacity="0.62" style="animation-delay:-0.44s"/>
<polygon class="particle" points="223.5,356.5 221.1,361.4 225.8,361.4" fill="#46a7ff" opacity="0.77" style="animation-delay:-2.62s"/>
<polygon class="particle" points="184.4,323.9 182.1,328.7 186.7,328.7" fill="#d04dff" opacity="0.81" style="animation-delay:-0.27s"/>
<polygon class="particle" points="195.7,334.1 194.2,337.3 197.3,337.3" fill="#8052ff" opacity="0.76" style="animation-delay:-2.44s"/>
<polygon class="particle" points="191.2,346.9 188.1,353.4 194.3,353.4" fill="#f4f0ff" opacity="0.93" style="animation-delay:-3.73s"/>
<polygon class="particle" points="200.4,328.4 197.5,334.3 203.2,334.3" fill="#ff7dcb" opacity="0.48" style="animation-delay:-2.63s"/>
<polygon class="particle" points="224.0,320.1 221.9,324.4 226.1,324.4" fill="#f4f0ff" opacity="0.53" style="animation-delay:-1.24s"/>
<polygon class="particle" points="215.0,321.2 211.9,327.6 218.1,327.6" fill="#ffb829" opacity="0.89" style="animation-delay:-3.85s"/>
<polygon class="particle" points="204.4,322.0 201.4,328.1 207.4,328.1" fill="#f4f0ff" opacity="0.63" style="animation-delay:-2.92s"/>
<polygon class="particle" points="204.0,361.8 202.8,364.3 205.2,364.3" fill="#f4f0ff" opacity="0.53" style="animation-delay:-3.41s"/>
<polygon class="particle" points="233.7,327.4 230.8,333.4 236.6,333.4" fill="#15846e" opacity="0.63" style="animation-delay:-1.59s"/>
<polygon class="particle" points="183.7,337.1 181.9,340.8 185.5,340.8" fill="#8052ff" opacity="0.89" style="animation-delay:-1.39s"/>
<polygon class="particle" points="214.4,303.6 211.7,309.1 217.0,309.1" fill="#8052ff" opacity="0.65" style="animation-delay:-0.79s"/>
<polygon class="particle" points="206.3,363.2 203.7,368.4 208.8,368.4" fill="#f4f0ff" opacity="0.93" style="animation-delay:-2.21s"/>
<polygon class="particle" points="228.0,297.2 225.7,302.0 230.4,302.0" fill="#ffb829" opacity="0.84" style="animation-delay:-2.37s"/>
<polygon class="particle" points="194.1,335.1 192.8,337.8 195.5,337.8" fill="#8052ff" opacity="0.57" style="animation-delay:-1.15s"/>
<polygon class="particle" points="205.5,354.9 203.5,359.1 207.5,359.1" fill="#15846e" opacity="0.79" style="animation-delay:-2.12s"/>
<polygon class="particle" points="208.0,305.1 205.3,310.5 210.6,310.5" fill="#ff7dcb" opacity="0.86" style="animation-delay:-3.48s"/>
<polygon class="particle" points="194.1,361.8 192.7,364.7 195.5,364.7" fill="#f4f0ff" opacity="0.57" style="animation-delay:-2.02s"/>
<polygon class="particle" points="210.3,298.9 208.3,302.9 212.2,302.9" fill="#8052ff" opacity="0.50" style="animation-delay:-3.56s"/>
<polygon class="particle" points="202.8,357.2 200.1,362.7 205.5,362.7" fill="#f4f0ff" opacity="0.92" style="animation-delay:-0.53s"/>
<polygon class="particle" points="237.5,334.6 236.3,337.1 238.8,337.1" fill="#f4f0ff" opacity="0.42" style="animation-delay:-2.68s"/>
<polygon class="particle" points="214.7,340.3 211.6,346.8 217.8,346.8" fill="#8052ff" opacity="0.65" style="animation-delay:-0.09s"/>
<polygon class="particle" points="224.2,295.5 222.8,298.4 225.6,298.4" fill="#8052ff" opacity="0.84" style="animation-delay:-0.65s"/>
<polygon class="particle" points="238.7,337.2 236.5,341.7 240.9,341.7" fill="#15846e" opacity="0.93" style="animation-delay:-2.77s"/>
<polygon class="particle" points="224.0,312.4 222.1,316.2 225.8,316.2" fill="#8052ff" opacity="0.70" style="animation-delay:-0.29s"/>
<polygon class="particle" points="193.8,332.9 192.6,335.4 195.0,335.4" fill="#8052ff" opacity="0.57" style="animation-delay:-1.84s"/>
<polygon class="particle" points="199.7,326.9 197.5,331.5 201.9,331.5" fill="#d04dff" opacity="0.68" style="animation-delay:-2.80s"/>
<polygon class="particle" points="192.0,324.2 189.3,329.9 194.8,329.9" fill="#46a7ff" opacity="0.78" style="animation-delay:-3.36s"/>
<polygon class="particle" points="220.6,311.3 218.5,315.7 222.8,315.7" fill="#8052ff" opacity="0.69" style="animation-delay:-3.03s"/>
<polygon class="particle" points="197.1,302.9 194.1,309.1 200.0,309.1" fill="#d04dff" opacity="0.97" style="animation-delay:-2.14s"/>
<polygon class="particle" points="217.2,333.2 214.4,338.9 220.0,338.9" fill="#f4f0ff" opacity="0.47" style="animation-delay:-2.08s"/>
<polygon class="particle" points="238.7,353.4 237.5,355.9 239.9,355.9" fill="#ffb829" opacity="0.76" style="animation-delay:-1.25s"/>
<polygon class="particle" points="178.3,338.0 175.5,343.8 181.1,343.8" fill="#ff7dcb" opacity="0.75" style="animation-delay:-1.66s"/>
<polygon class="particle" points="208.7,353.5 206.7,357.7 210.8,357.7" fill="#15846e" opacity="0.76" style="animation-delay:-2.09s"/>
<polygon class="particle" points="228.2,360.8 226.2,364.9 230.2,364.9" fill="#8052ff" opacity="0.97" style="animation-delay:-2.28s"/>
<polygon class="particle" points="240.2,349.8 238.6,353.2 241.9,353.2" fill="#d04dff" opacity="0.71" style="animation-delay:-3.78s"/>
<polygon class="particle" points="183.8,314.4 182.5,317.2 185.2,317.2" fill="#15846e" opacity="0.40" style="animation-delay:-3.11s"/>
<polygon class="particle" points="201.5,345.3 198.5,351.5 204.5,351.5" fill="#f4f0ff" opacity="0.69" style="animation-delay:-3.48s"/>
<polygon class="particle" points="216.3,293.4 213.3,299.7 219.4,299.7" fill="#46a7ff" opacity="0.48" style="animation-delay:-1.62s"/>
<polygon class="particle" points="176.0,321.8 173.8,326.3 178.2,326.3" fill="#15846e" opacity="0.45" style="animation-delay:-0.11s"/>
<polygon class="particle" points="194.5,329.8 192.1,334.7 196.8,334.7" fill="#15846e" opacity="0.53" style="animation-delay:-1.04s"/>
<polygon class="particle" points="193.7,354.4 192.4,357.2 195.0,357.2" fill="#d04dff" opacity="0.96" style="animation-delay:-1.61s"/>
<polygon class="particle" points="216.1,317.4 213.9,322.0 218.3,322.0" fill="#ffb829" opacity="0.77" style="animation-delay:-1.32s"/>
<polygon class="particle" points="219.3,313.4 216.7,318.8 222.0,318.8" fill="#8052ff" opacity="0.78" style="animation-delay:-0.41s"/>
<polygon class="particle" points="216.7,356.0 215.0,359.5 218.4,359.5" fill="#ff7dcb" opacity="0.57" style="animation-delay:-1.41s"/>
<polygon class="particle" points="203.6,325.7 202.0,329.0 205.1,329.0" fill="#8052ff" opacity="0.85" style="animation-delay:-2.49s"/>
<polygon class="particle" points="200.7,328.1 198.9,331.7 202.4,331.7" fill="#ffb829" opacity="0.73" style="animation-delay:-3.37s"/>
<polygon class="particle" points="225.2,360.7 222.8,365.6 227.6,365.6" fill="#d04dff" opacity="0.44" style="animation-delay:-3.81s"/>
<polygon class="particle" points="174.5,331.7 173.1,334.4 175.8,334.4" fill="#15846e" opacity="0.66" style="animation-delay:-1.76s"/>
<polygon class="particle" points="202.7,354.9 201.5,357.3 203.9,357.3" fill="#8052ff" opacity="0.73" style="animation-delay:-0.62s"/>
<polygon class="particle" points="212.7,299.5 210.5,303.9 214.8,303.9" fill="#d04dff" opacity="0.74" style="animation-delay:-2.63s"/>
<polygon class="particle" points="222.5,327.9 221.3,330.3 223.7,330.3" fill="#ffb829" opacity="0.83" style="animation-delay:-1.53s"/>
<polygon class="particle" points="197.4,333.5 194.2,340.0 200.5,340.0" fill="#8052ff" opacity="0.94" style="animation-delay:-1.06s"/>
<polygon class="particle" points="239.6,334.5 236.9,340.0 242.2,340.0" fill="#d04dff" opacity="0.89" style="animation-delay:-1.61s"/>
<polygon class="particle" points="223.0,305.2 220.1,311.2 226.0,311.2" fill="#8052ff" opacity="0.75" style="animation-delay:-0.40s"/>
<polygon class="particle" points="203.1,343.7 201.2,347.7 205.0,347.7" fill="#8052ff" opacity="0.66" style="animation-delay:-1.57s"/>
<polygon class="particle" points="217.6,315.0 216.2,317.8 219.0,317.8" fill="#8052ff" opacity="0.90" style="animation-delay:-2.80s"/>
<polygon class="particle" points="227.7,345.1 225.0,350.6 230.4,350.6" fill="#f4f0ff" opacity="0.88" style="animation-delay:-2.23s"/>
<polygon class="particle" points="204.8,319.9 202.5,324.8 207.2,324.8" fill="#f4f0ff" opacity="0.63" style="animation-delay:-3.79s"/>
<polygon class="particle" points="237.3,353.3 234.8,358.5 239.8,358.5" fill="#ffb829" opacity="0.78" style="animation-delay:-0.72s"/>
<polygon class="particle" points="230.1,302.9 228.4,306.2 231.7,306.2" fill="#d04dff" opacity="0.70" style="animation-delay:-3.07s"/>
<polygon class="particle" points="191.5,301.1 189.6,304.9 193.4,304.9" fill="#f4f0ff" opacity="0.96" style="animation-delay:-3.97s"/>
<polygon class="particle" points="212.0,335.2 210.2,339.0 213.9,339.0" fill="#ffb829" opacity="0.55" style="animation-delay:-3.83s"/>
<polygon class="particle" points="189.4,353.0 186.7,358.6 192.1,358.6" fill="#f4f0ff" opacity="0.88" style="animation-delay:-2.13s"/>
<polygon class="particle" points="204.9,327.3 202.9,331.4 206.9,331.4" fill="#15846e" opacity="0.84" style="animation-delay:-0.91s"/>
<polygon class="particle" points="219.8,299.3 217.0,305.2 222.7,305.2" fill="#ffb829" opacity="0.75" style="animation-delay:-3.16s"/>
<polygon class="particle" points="204.0,320.1 201.5,325.2 206.5,325.2" fill="#46a7ff" opacity="0.43" style="animation-delay:-0.05s"/>
<polygon class="particle" points="233.8,328.6 232.0,332.2 235.5,332.2" fill="#f4f0ff" opacity="0.46" style="animation-delay:-3.45s"/>
<polygon class="particle" points="203.6,316.5 202.3,319.1 204.9,319.1" fill="#ffb829" opacity="0.90" style="animation-delay:-0.88s"/>
<polygon class="particle" points="236.5,331.9 234.1,336.7 238.8,336.7" fill="#15846e" opacity="0.76" style="animation-delay:-3.94s"/>
<polygon class="particle" points="224.6,311.3 222.3,315.8 226.8,315.8" fill="#8052ff" opacity="0.95" style="animation-delay:-3.25s"/>
<polygon class="particle" points="213.2,349.4 210.2,355.5 216.1,355.5" fill="#d04dff" opacity="0.70" style="animation-delay:-3.55s"/>
<polygon class="particle" points="191.2,346.9 188.7,352.1 193.7,352.1" fill="#ffb829" opacity="0.54" style="animation-delay:-1.97s"/>
<polygon class="particle" points="234.4,330.6 231.8,335.9 237.0,335.9" fill="#f4f0ff" opacity="0.70" style="animation-delay:-3.53s"/>
<polygon class="particle" points="223.6,340.9 222.3,343.4 224.8,343.4" fill="#d04dff" opacity="0.50" style="animation-delay:-0.81s"/>
<polygon class="particle" points="204.5,309.2 203.0,312.2 205.9,312.2" fill="#f4f0ff" opacity="0.44" style="animation-delay:-2.48s"/>
<polygon class="particle" points="194.1,340.8 192.0,345.1 196.2,345.1" fill="#ffb829" opacity="0.74" style="animation-delay:-0.18s"/>
<polygon class="particle" points="201.7,316.9 198.7,323.2 204.8,323.2" fill="#f4f0ff" opacity="0.42" style="animation-delay:-3.57s"/>
<polygon class="particle" points="191.2,335.4 189.3,339.4 193.1,339.4" fill="#46a7ff" opacity="0.58" style="animation-delay:-2.03s"/>
<polygon class="particle" points="198.0,334.6 196.8,337.1 199.2,337.1" fill="#15846e" opacity="0.72" style="animation-delay:-2.71s"/>
<polygon class="particle" points="199.7,340.1 198.1,343.4 201.3,343.4" fill="#ffb829" opacity="0.83" style="animation-delay:-3.33s"/>
<polygon class="particle" points="201.8,310.4 199.3,315.6 204.4,315.6" fill="#f4f0ff" opacity="0.72" style="animation-delay:-1.97s"/>
<polygon class="particle" points="205.8,366.7 204.4,369.7 207.3,369.7" fill="#8052ff" opacity="0.88" style="animation-delay:-2.33s"/>
<polygon class="particle" points="207.6,293.4 204.8,299.2 210.4,299.2" fill="#f4f0ff" opacity="0.60" style="animation-delay:-0.55s"/>
<polygon class="particle" points="201.3,302.4 198.9,307.3 203.7,307.3" fill="#46a7ff" opacity="0.89" style="animation-delay:-0.68s"/>
<polygon class="particle" points="202.6,340.2 200.5,344.6 204.8,344.6" fill="#15846e" opacity="0.57" style="animation-delay:-0.66s"/>
<polygon class="particle" points="208.0,313.5 206.2,317.3 209.8,317.3" fill="#15846e" opacity="0.52" style="animation-delay:-3.09s"/>
<polygon class="particle" points="200.0,359.7 198.3,363.3 201.7,363.3" fill="#15846e" opacity="0.71" style="animation-delay:-1.97s"/>
<polygon class="particle" points="227.4,317.8 225.0,322.6 229.7,322.6" fill="#ffb829" opacity="0.86" style="animation-delay:-1.36s"/>
<polygon class="particle" points="199.4,306.5 197.7,310.0 201.1,310.0" fill="#ffb829" opacity="0.46" style="animation-delay:-2.88s"/>
<polygon class="particle" points="241.1,319.7 238.7,324.5 243.4,324.5" fill="#46a7ff" opacity="0.46" style="animation-delay:-1.54s"/>
<polygon class="particle" points="210.8,310.5 208.7,314.9 213.0,314.9" fill="#46a7ff" opacity="0.86" style="animation-delay:-1.01s"/>
<polygon class="particle" points="186.1,316.0 184.8,318.8 187.4,318.8" fill="#ffb829" opacity="0.67" style="animation-delay:-0.06s"/>
<polygon class="particle" points="185.8,299.7 183.8,303.8 187.8,303.8" fill="#15846e" opacity="0.42" style="animation-delay:-3.59s"/>
<polygon class="particle" points="241.1,319.9 238.3,325.7 243.9,325.7" fill="#ffb829" opacity="0.45" style="animation-delay:-3.73s"/>
<polygon class="particle" points="199.0,292.3 197.1,296.3 201.0,296.3" fill="#ffb829" opacity="0.47" style="animation-delay:-0.69s"/>
<polygon class="particle" points="245.1,319.0 243.3,322.8 247.0,322.8" fill="#8052ff" opacity="0.46" style="animation-delay:-2.45s"/>
<polygon class="particle" points="220.4,345.6 218.4,349.9 222.5,349.9" fill="#8052ff" opacity="0.75" style="animation-delay:-1.97s"/>
<polygon class="particle" points="209.6,314.6 207.1,319.7 212.0,319.7" fill="#ffb829" opacity="0.72" style="animation-delay:-1.34s"/>
<polygon class="particle" points="209.7,362.6 206.8,368.7 212.7,368.7" fill="#ffb829" opacity="0.69" style="animation-delay:-3.62s"/>
<polygon class="particle" points="179.5,307.8 177.3,312.4 181.7,312.4" fill="#8052ff" opacity="0.86" style="animation-delay:-1.46s"/>
<polygon class="particle" points="192.7,331.6 190.8,335.6 194.7,335.6" fill="#46a7ff" opacity="0.82" style="animation-delay:-0.88s"/>
<polygon class="particle" points="228.6,327.9 227.1,331.0 230.1,331.0" fill="#46a7ff" opacity="0.48" style="animation-delay:-3.42s"/>
<polygon class="particle" points="246.2,337.9 243.2,344.0 249.1,344.0" fill="#8052ff" opacity="0.56" style="animation-delay:-0.35s"/>
<polygon class="particle" points="229.8,330.0 227.6,334.4 231.9,334.4" fill="#8052ff" opacity="0.54" style="animation-delay:-0.28s"/>
<polygon class="particle" points="208.4,335.8 205.3,342.2 211.6,342.2" fill="#f4f0ff" opacity="0.89" style="animation-delay:-2.54s"/>
<polygon class="particle" points="230.3,350.5 228.1,355.0 232.5,355.0" fill="#8052ff" opacity="0.89" style="animation-delay:-2.10s"/>
<polygon class="particle" points="233.1,334.6 230.6,339.7 235.5,339.7" fill="#f4f0ff" opacity="0.52" style="animation-delay:-0.36s"/>
<polygon class="particle" points="192.2,332.4 189.7,337.6 194.7,337.6" fill="#15846e" opacity="0.69" style="animation-delay:-2.52s"/>
<polygon class="particle" points="202.4,336.0 199.4,342.3 205.5,342.3" fill="#f4f0ff" opacity="0.74" style="animation-delay:-1.48s"/>
<polygon class="particle" points="206.1,364.7 203.9,369.3 208.4,369.3" fill="#f4f0ff" opacity="0.46" style="animation-delay:-2.53s"/>
<polygon class="particle" points="174.7,326.7 172.3,331.6 177.0,331.6" fill="#15846e" opacity="0.84" style="animation-delay:-3.48s"/>
<polygon class="particle" points="225.9,343.1 224.5,345.9 227.3,345.9" fill="#46a7ff" opacity="0.44" style="animation-delay:-2.52s"/>
<polygon class="particle" points="181.7,320.1 180.1,323.4 183.3,323.4" fill="#f4f0ff" opacity="0.71" style="animation-delay:-0.30s"/>
<polygon class="particle" points="193.1,334.8 190.5,340.3 195.8,340.3" fill="#ffb829" opacity="0.47" style="animation-delay:-3.93s"/>
<polygon class="particle" points="205.7,329.4 203.3,334.3 208.0,334.3" fill="#d04dff" opacity="0.67" style="animation-delay:-0.75s"/>
<polygon class="particle" points="188.6,300.0 185.8,305.7 191.4,305.7" fill="#46a7ff" opacity="0.86" style="animation-delay:-1.46s"/>
<polygon class="particle" points="178.6,348.7 176.4,353.1 180.7,353.1" fill="#ffb829" opacity="0.91" style="animation-delay:-3.44s"/>
<polygon class="particle" points="208.8,293.1 207.5,295.7 210.0,295.7" fill="#8052ff" opacity="0.92" style="animation-delay:-2.22s"/>
<polygon class="particle" points="194.8,299.6 192.3,304.6 197.2,304.6" fill="#8052ff" opacity="0.44" style="animation-delay:-2.54s"/>
<polygon class="particle" points="213.8,327.3 211.5,332.0 216.1,332.0" fill="#ffb829" opacity="0.53" style="animation-delay:-3.23s"/>
<polygon class="particle" points="212.4,299.8 210.6,303.5 214.2,303.5" fill="#8052ff" opacity="0.76" style="animation-delay:-0.46s"/>
<polygon class="particle" points="215.2,354.2 213.9,356.9 216.5,356.9" fill="#46a7ff" opacity="0.85" style="animation-delay:-0.55s"/>
<polygon class="particle" points="205.2,364.3 204.0,366.7 206.4,366.7" fill="#46a7ff" opacity="0.81" style="animation-delay:-1.66s"/>
<polygon class="particle" points="233.8,343.1 231.5,347.9 236.1,347.9" fill="#ffb829" opacity="0.84" style="animation-delay:-0.42s"/>
<polygon class="particle" points="210.6,349.9 209.3,352.7 212.0,352.7" fill="#8052ff" opacity="0.43" style="animation-delay:-3.58s"/>
<polygon class="particle" points="243.3,344.4 241.8,347.4 244.8,347.4" fill="#ffb829" opacity="0.93" style="animation-delay:-3.34s"/>
<polygon class="particle" points="194.8,356.5 193.4,359.5 196.3,359.5" fill="#46a7ff" opacity="0.91" style="animation-delay:-1.85s"/>
<polygon class="particle" points="245.9,338.5 243.4,343.6 248.3,343.6" fill="#15846e" opacity="0.92" style="animation-delay:-0.70s"/>
<polygon class="particle" points="193.8,348.5 192.2,351.9 195.5,351.9" fill="#f4f0ff" opacity="0.88" style="animation-delay:-0.00s"/>
<polygon class="particle" points="209.5,340.3 207.0,345.4 211.9,345.4" fill="#ffb829" opacity="0.64" style="animation-delay:-3.42s"/>
<polygon class="particle" points="190.7,325.1 187.6,331.5 193.8,331.5" fill="#ffb829" opacity="0.58" style="animation-delay:-1.74s"/>
<polygon class="particle" points="202.6,345.9 200.7,349.8 204.5,349.8" fill="#8052ff" opacity="0.90" style="animation-delay:-3.04s"/>
<polygon class="particle" points="224.1,301.7 222.7,304.5 225.5,304.5" fill="#8052ff" opacity="0.68" style="animation-delay:-3.10s"/>
<polygon class="particle" points="240.0,338.1 238.0,342.4 242.1,342.4" fill="#8052ff" opacity="0.80" style="animation-delay:-3.11s"/>
<polygon class="particle" points="184.0,309.1 182.1,313.0 185.9,313.0" fill="#8052ff" opacity="0.73" style="animation-delay:-3.75s"/>
<polygon class="particle" points="212.1,298.6 210.1,302.8 214.1,302.8" fill="#46a7ff" opacity="0.75" style="animation-delay:-0.10s"/>
<polygon class="particle" points="191.8,316.0 188.8,322.1 194.8,322.1" fill="#8052ff" opacity="0.44" style="animation-delay:-3.64s"/>
<polygon class="particle" points="225.3,345.5 223.0,350.2 227.5,350.2" fill="#46a7ff" opacity="0.40" style="animation-delay:-2.45s"/>
<polygon class="particle" points="229.6,331.4 226.6,337.7 232.6,337.7" fill="#f4f0ff" opacity="0.48" style="animation-delay:-0.47s"/>
<polygon class="particle" points="202.5,320.6 199.6,326.5 205.4,326.5" fill="#f4f0ff" opacity="0.87" style="animation-delay:-0.16s"/>
<polygon class="particle" points="226.5,321.4 223.4,327.7 229.6,327.7" fill="#f4f0ff" opacity="0.61" style="animation-delay:-3.07s"/>
<polygon class="particle" points="206.3,358.9 203.6,364.5 209.0,364.5" fill="#f4f0ff" opacity="0.98" style="animation-delay:-1.26s"/>
<polygon class="particle" points="217.9,343.4 215.7,347.8 220.0,347.8" fill="#d04dff" opacity="0.85" style="animation-delay:-3.69s"/>
<polygon class="particle" points="208.2,345.3 206.2,349.4 210.1,349.4" fill="#ff7dcb" opacity="0.88" style="animation-delay:-0.85s"/>
<polygon class="particle" points="202.6,298.7 199.6,305.0 205.7,305.0" fill="#f4f0ff" opacity="0.79" style="animation-delay:-1.26s"/>
<polygon class="particle" points="214.6,308.6 212.1,313.8 217.1,313.8" fill="#8052ff" opacity="0.44" style="animation-delay:-3.90s"/>
<polygon class="particle" points="207.8,324.9 206.3,327.9 209.3,327.9" fill="#8052ff" opacity="0.93" style="animation-delay:-1.93s"/>
<polygon class="particle" points="197.3,361.5 195.4,365.5 199.2,365.5" fill="#46a7ff" opacity="0.53" style="animation-delay:-2.86s"/>
<polygon class="particle" points="234.8,353.5 233.4,356.6 236.3,356.6" fill="#8052ff" opacity="0.73" style="animation-delay:-1.99s"/>
<polygon class="particle" points="212.5,341.8 211.0,344.8 213.9,344.8" fill="#d04dff" opacity="0.58" style="animation-delay:-2.29s"/>
<polygon class="particle" points="189.5,319.7 186.7,325.4 192.3,325.4" fill="#8052ff" opacity="0.92" style="animation-delay:-0.27s"/>
<polygon class="particle" points="204.5,298.8 202.0,303.9 207.0,303.9" fill="#ffb829" opacity="0.95" style="animation-delay:-3.75s"/>
<polygon class="particle" points="219.2,294.5 217.7,297.6 220.8,297.6" fill="#d04dff" opacity="0.88" style="animation-delay:-0.81s"/>
<polygon class="particle" points="198.5,337.0 197.0,340.1 200.0,340.1" fill="#46a7ff" opacity="0.60" style="animation-delay:-2.46s"/>
<polygon class="particle" points="205.6,318.6 203.5,322.8 207.6,322.8" fill="#8052ff" opacity="0.48" style="animation-delay:-3.94s"/>
<polygon class="particle" points="223.6,338.3 220.9,343.9 226.3,343.9" fill="#d04dff" opacity="0.76" style="animation-delay:-1.24s"/>
<polygon class="particle" points="177.7,320.7 176.1,324.1 179.4,324.1" fill="#f4f0ff" opacity="0.45" style="animation-delay:-0.38s"/>
<polygon class="particle" points="216.2,348.0 213.4,353.8 219.1,353.8" fill="#f4f0ff" opacity="0.93" style="animation-delay:-2.41s"/>
<polygon class="particle" points="233.6,310.0 231.6,314.0 235.5,314.0" fill="#ffb829" opacity="0.52" style="animation-delay:-3.81s"/>
<polygon class="particle" points="207.4,300.1 206.3,302.5 208.5,302.5" fill="#15846e" opacity="0.57" style="animation-delay:-3.29s"/>
<polygon class="particle" points="241.9,349.3 240.2,352.8 243.6,352.8" fill="#d04dff" opacity="0.75" style="animation-delay:-0.35s"/>
<polygon class="particle" points="197.4,308.8 194.5,314.7 200.2,314.7" fill="#ffb829" opacity="0.79" style="animation-delay:-2.14s"/>
<polygon class="particle" points="194.4,318.2 191.7,323.7 197.0,323.7" fill="#d04dff" opacity="0.77" style="animation-delay:-1.69s"/>
<polygon class="particle" points="180.3,343.8 178.0,348.6 182.6,348.6" fill="#d04dff" opacity="0.93" style="animation-delay:-0.86s"/>
<polygon class="particle" points="211.9,296.2 210.3,299.6 213.6,299.6" fill="#ffb829" opacity="0.48" style="animation-delay:-2.74s"/>
<polygon class="particle" points="196.3,330.8 194.5,334.4 198.1,334.4" fill="#ffb829" opacity="0.78" style="animation-delay:-1.53s"/>
<polygon class="particle" points="219.3,360.6 217.7,363.9 220.9,363.9" fill="#ffb829" opacity="0.88" style="animation-delay:-2.01s"/>
<polygon class="particle" points="201.5,300.7 200.3,303.1 202.6,303.1" fill="#15846e" opacity="0.90" style="animation-delay:-2.61s"/>
<polygon class="particle" points="181.4,351.7 178.5,357.6 184.2,357.6" fill="#f4f0ff" opacity="0.90" style="animation-delay:-3.25s"/>
<polygon class="particle" points="182.2,340.0 180.8,343.0 183.7,343.0" fill="#f4f0ff" opacity="0.85" style="animation-delay:-2.57s"/>
<polygon class="particle" points="230.8,298.1 229.0,301.9 232.7,301.9" fill="#f4f0ff" opacity="0.45" style="animation-delay:-2.32s"/>
<polygon class="particle" points="215.1,295.1 212.2,301.1 218.0,301.1" fill="#8052ff" opacity="0.46" style="animation-delay:-0.15s"/>
<polygon class="particle" points="215.8,318.6 214.0,322.2 217.5,322.2" fill="#f4f0ff" opacity="0.70" style="animation-delay:-0.08s"/>
<polygon class="particle" points="203.8,341.3 201.7,345.6 205.9,345.6" fill="#46a7ff" opacity="0.60" style="animation-delay:-3.89s"/>
<polygon class="particle" points="180.1,336.4 178.5,339.6 181.6,339.6" fill="#8052ff" opacity="0.60" style="animation-delay:-2.19s"/>
<polygon class="particle" points="199.7,314.7 197.4,319.4 201.9,319.4" fill="#f4f0ff" opacity="0.73" style="animation-delay:-2.19s"/>
<polygon class="particle" points="246.6,327.9 244.7,331.9 248.6,331.9" fill="#15846e" opacity="0.54" style="animation-delay:-0.78s"/>
<polygon class="particle" points="200.3,340.8 198.9,343.6 201.7,343.6" fill="#15846e" opacity="0.83" style="animation-delay:-2.90s"/>
<polygon class="particle" points="205.3,350.7 203.7,354.0 206.9,354.0" fill="#8052ff" opacity="0.80" style="animation-delay:-1.71s"/>
<polygon class="particle" points="192.2,344.7 189.3,350.7 195.1,350.7" fill="#15846e" opacity="0.98" style="animation-delay:-0.57s"/>
<polygon class="particle" points="233.7,299.6 230.6,306.0 236.8,306.0" fill="#d04dff" opacity="0.50" style="animation-delay:-1.61s"/>
<polygon class="particle" points="234.1,300.5 231.4,306.0 236.8,306.0" fill="#f4f0ff" opacity="0.93" style="animation-delay:-0.03s"/>
<polygon class="particle" points="188.7,331.3 186.1,336.7 191.4,336.7" fill="#f4f0ff" opacity="0.76" style="animation-delay:-2.95s"/>
<polygon class="particle" points="176.6,322.0 173.6,328.1 179.5,328.1" fill="#8052ff" opacity="0.88" style="animation-delay:-2.07s"/>
<polygon class="particle" points="201.8,347.4 200.6,349.9 203.1,349.9" fill="#ffb829" opacity="0.42" style="animation-delay:-3.33s"/>
<polygon class="particle" points="223.8,362.7 221.5,367.5 226.2,367.5" fill="#f4f0ff" opacity="0.41" style="animation-delay:-1.79s"/>
<polygon class="particle" points="177.2,333.4 175.5,337.0 179.0,337.0" fill="#8052ff" opacity="0.51" style="animation-delay:-0.88s"/>
<polygon class="particle" points="202.4,306.8 201.2,309.4 203.7,309.4" fill="#46a7ff" opacity="0.73" style="animation-delay:-2.97s"/>
<polygon class="particle" points="195.2,328.9 192.2,335.1 198.2,335.1" fill="#8052ff" opacity="0.59" style="animation-delay:-2.78s"/>
<polygon class="particle" points="231.2,354.3 229.3,358.2 233.1,358.2" fill="#ffb829" opacity="0.83" style="animation-delay:-2.71s"/>
<polygon class="particle" points="197.5,363.5 195.2,368.4 199.9,368.4" fill="#ffb829" opacity="0.91" style="animation-delay:-1.12s"/>
<polygon class="particle" points="183.5,326.6 181.5,330.7 185.5,330.7" fill="#8052ff" opacity="0.75" style="animation-delay:-2.44s"/>
<polygon class="particle" points="234.8,353.1 232.4,358.1 237.2,358.1" fill="#8052ff" opacity="0.73" style="animation-delay:-1.71s"/>
<polygon class="particle" points="210.6,326.6 208.3,331.3 212.9,331.3" fill="#15846e" opacity="0.79" style="animation-delay:-1.61s"/>
<polygon class="particle" points="195.0,315.2 192.9,319.6 197.1,319.6" fill="#ffb829" opacity="0.81" style="animation-delay:-3.52s"/>
<polygon class="particle" points="243.7,315.8 242.3,318.6 245.1,318.6" fill="#15846e" opacity="0.75" style="animation-delay:-3.04s"/>
<polygon class="particle" points="226.3,339.8 223.6,345.3 229.0,345.3" fill="#46a7ff" opacity="0.73" style="animation-delay:-2.96s"/>
<polygon class="particle" points="206.2,331.7 203.0,338.3 209.4,338.3" fill="#f4f0ff" opacity="0.51" style="animation-delay:-0.56s"/>
<polygon class="particle" points="195.9,331.4 194.0,335.3 197.7,335.3" fill="#f4f0ff" opacity="0.61" style="animation-delay:-2.46s"/>
<polygon class="particle" points="188.7,322.8 186.7,326.9 190.7,326.9" fill="#ffb829" opacity="0.93" style="animation-delay:-2.82s"/>
<polygon class="particle" points="211.8,296.5 210.4,299.4 213.2,299.4" fill="#46a7ff" opacity="0.75" style="animation-delay:-1.68s"/>
<polygon class="particle" points="210.6,351.8 208.2,356.7 213.0,356.7" fill="#ffb829" opacity="0.68" style="animation-delay:-3.92s"/>
<polygon class="particle" points="204.9,358.6 202.0,364.6 207.8,364.6" fill="#ffb829" opacity="0.50" style="animation-delay:-1.70s"/>
<polygon class="particle" points="190.8,299.6 187.6,306.1 193.9,306.1" fill="#46a7ff" opacity="0.88" style="animation-delay:-1.31s"/>
<polygon class="particle" points="220.4,308.4 219.2,311.0 221.7,311.0" fill="#f4f0ff" opacity="0.69" style="animation-delay:-0.55s"/>
<polygon class="particle" points="184.6,330.5 183.4,333.0 185.8,333.0" fill="#8052ff" opacity="0.77" style="animation-delay:-0.18s"/>
<polygon class="particle" points="214.8,338.4 211.8,344.6 217.8,344.6" fill="#d04dff" opacity="0.56" style="animation-delay:-2.01s"/>
<polygon class="particle" points="225.8,295.0 222.8,301.0 228.7,301.0" fill="#8052ff" opacity="0.88" style="animation-delay:-3.37s"/>
<polygon class="particle" points="216.8,346.8 214.5,351.5 219.1,351.5" fill="#ffb829" opacity="0.60" style="animation-delay:-2.60s"/>
<polygon class="particle" points="197.8,348.7 195.0,354.5 200.6,354.5" fill="#8052ff" opacity="0.44" style="animation-delay:-0.50s"/>
<polygon class="particle" points="230.6,355.5 228.1,360.6 233.0,360.6" fill="#8052ff" opacity="0.82" style="animation-delay:-2.66s"/>
<polygon class="particle" points="217.5,296.2 214.8,301.9 220.3,301.9" fill="#f4f0ff" opacity="0.42" style="animation-delay:-2.45s"/>
<polygon class="particle" points="191.7,315.1 189.1,320.4 194.3,320.4" fill="#15846e" opacity="0.87" style="animation-delay:-0.43s"/>
<polygon class="particle" points="216.7,364.0 215.6,366.3 217.8,366.3" fill="#8052ff" opacity="0.41" style="animation-delay:-0.15s"/>
<polygon class="particle" points="197.2,346.4 196.0,348.8 198.3,348.8" fill="#f4f0ff" opacity="0.63" style="animation-delay:-2.64s"/>
<polygon class="particle" points="224.9,300.4 222.9,304.6 226.9,304.6" fill="#ffb829" opacity="0.42" style="animation-delay:-2.33s"/>
<polygon class="particle" points="184.2,319.3 182.0,323.9 186.5,323.9" fill="#d04dff" opacity="0.42" style="animation-delay:-1.30s"/>
<polygon class="particle" points="234.5,348.2 232.8,351.8 236.3,351.8" fill="#f4f0ff" opacity="0.70" style="animation-delay:-0.27s"/>
<polygon class="particle" points="191.0,345.0 189.6,347.9 192.4,347.9" fill="#d04dff" opacity="0.89" style="animation-delay:-2.20s"/>
<polygon class="particle" points="226.2,346.6 223.8,351.6 228.6,351.6" fill="#f4f0ff" opacity="0.55" style="animation-delay:-0.51s"/>
<polygon class="particle" points="213.7,359.6 211.8,363.7 215.7,363.7" fill="#f4f0ff" opacity="0.95" style="animation-delay:-1.66s"/>
<polygon class="particle" points="203.8,304.4 201.3,309.6 206.4,309.6" fill="#ffb829" opacity="0.61" style="animation-delay:-2.72s"/>
  </g>
  <!-- Bright edge lights add a dimensional, sculptural contour -->
  <path d="M181 31 Q210 18 239 31 L231 263" fill="none" stroke="#ffb829" stroke-opacity=".42" stroke-width="1.2"/>
  <path d="M189 270 Q210 278 231 270" fill="none" stroke="#8052ff" stroke-opacity=".65" stroke-width="1.3"/>
  <ellipse cx="210" cy="331" rx="40" ry="40" fill="none" stroke="#46a7ff" stroke-opacity=".36" stroke-width="1.1"/>
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
        status_slot = st.empty()
        status_slot.info("Analysis submitted preparing your result…")
        try:
            settings = config["prediction_transformer"]
            results = predict_texts(
                [text],
                scorer,
                labels,
                {**config, "prediction": settings},
            )
            result = results[0]

            status_slot.success("Analysis complete your result is shown below.")
            st.markdown("---")
            st.markdown('<div class="section-tag">02 / Result</div>', unsafe_allow_html=True)
            st.markdown("## What the model flagged")
            with st.expander("Text analysed", expanded=True):
                st.markdown(
                    '<div style="color:#9a9a9a;font-size:.75rem;letter-spacing:.1em;text-transform:uppercase;margin-bottom:.5rem">Exact input used for this result</div>',
                    unsafe_allow_html=True,
                )
                st.code(text, language=None)

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
