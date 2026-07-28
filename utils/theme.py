import streamlit as st

# ============================================================
# BORDER OPTICS — Smoky Vintage / Tech-Noir Theme
# ============================================================
PALETTE = {
    "bg_main": "#100E0C",
    "bg_card": "#1B1713",
    "bg_sidebar": "#0A0908",
    "border_up": "#3FB78C",      # tech-teal — growth / increase
    "border_down": "#B23A48",    # muted vintage crimson — decrease
    "lights": "#D9A441",         # antique brass — night-lights theme
    "warning": "#C97A3D",        # burnt copper — warnings
    "text_primary": "#EDE6DA",   # warm parchment off-white
    "text_secondary": "#9C9184", # smoky taupe
    "accent": "#2FD1C5",         # neon-tech teal glow — primary highlight
    "accent_vintage": "#B9863F", # antique brass — secondary highlight
}

# Backward-compatible aliases (used by some pages)
GOLD = PALETTE["accent_vintage"]
CYAN = PALETTE["accent"]
AMBER = PALETTE["lights"]


def inject_theme():
    p = PALETTE
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@500;600;700;800;900&family=JetBrains+Mono:wght@600;700&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
        }}

        .stApp {{
            background: {p['bg_main']};
            color: {p['text_primary']};
        }}

        .block-container {{
            padding-top: 1.5rem !important;
            padding-bottom: 2rem !important;
        }}

        header[data-testid="stHeader"] {{
            background: transparent;
            height: 0px;
        }}

        section[data-testid="stSidebar"] {{
            background: {p['bg_sidebar']};
            border-right: 1px solid rgba(47, 209, 197, 0.15);
        }}
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span {{
            color: {p['text_primary']} !important;
            font-weight: 600;
        }}

        h1 {{
            color: {p['text_primary']} !important;
            font-weight: 900 !important;
            font-size: 2.9rem !important;
            letter-spacing: -0.5px;
            text-align: center;
            text-shadow: 0 0 30px rgba(47, 209, 197, 0.28);
        }}

        h2 {{
            color: {p['text_primary']} !important;
            font-weight: 800 !important;
            border-left: 4px solid {p['accent']};
            padding-left: 14px;
            font-size: 1.6rem !important;
        }}

        h3 {{
            color: {p['text_secondary']} !important;
            font-weight: 700 !important;
        }}

        p, li {{
            color: {p['text_primary']};
            font-weight: 500;
        }}

        strong, b {{
            color: {p['accent']};
            font-weight: 700;
        }}

        div[data-testid="stMetric"] {{
            background: rgba(27, 23, 19, 0.7);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid rgba(47, 209, 197, 0.25);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.45);
        }}
        div[data-testid="stMetricValue"] {{
            color: {p['text_primary']} !important;
            font-weight: 800 !important;
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.7rem !important;
        }}
        div[data-testid="stMetricLabel"] {{
            color: {p['accent']} !important;
            text-transform: uppercase;
            font-size: 0.75rem !important;
            font-weight: 700 !important;
            letter-spacing: 1.5px;
        }}

        .stButton>button {{
            background: linear-gradient(90deg, {p['accent']}, {p['accent_vintage']});
            color: #0A0908;
            border-radius: 8px;
            border: none;
            font-weight: 700;
        }}

        div[data-testid="stAlert"] {{
            border-radius: 10px;
            font-weight: 600;
            background: rgba(27, 23, 19, 0.7);
            backdrop-filter: blur(10px);
        }}

        hr {{
            border: none;
            height: 1px;
            background: linear-gradient(90deg, transparent, {p['accent']}, transparent);
            margin: 1.8rem 0;
        }}

        .caption-text {{
            color: {p['text_secondary']};
            font-size: 0.88rem;
            font-weight: 600;
        }}

        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
        }}
        .stTabs [data-baseweb="tab"] {{
            background: rgba(27, 23, 19, 0.7);
            border-radius: 8px 8px 0 0;
            color: {p['text_secondary']};
            font-weight: 700;
        }}
        .stTabs [aria-selected="true"] {{
            background: rgba(47, 209, 197, 0.2) !important;
            color: {p['accent']} !important;
            font-weight: 800;
        }}

        .recon-card {{
            background: rgba(27, 23, 19, 0.7);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-radius: 14px;
            padding: 22px;
            border: 1px solid rgba(47, 209, 197, 0.25);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.45);
        }}

        [data-testid="stExpander"] {{
            background-color: rgba(27, 23, 19, 0.7) !important;
            border: 1px solid rgba(47, 209, 197, 0.25) !important;
            border-radius: 10px !important;
        }}
        [data-testid="stExpander"] summary {{
            background-color: rgba(27, 23, 19, 0.9) !important;
        }}
        [data-testid="stExpander"] summary p {{
            font-size: 1.05rem !important;
            font-weight: 700 !important;
            color: {p['text_primary']} !important;
        }}
        [data-testid="stExpanderDetails"] {{
            background-color: rgba(27, 23, 19, 0.5) !important;
        }}
        [data-testid="stExpanderDetails"] p, [data-testid="stExpanderDetails"] li {{
            color: {p['text_primary']} !important;
        }}
        [data-testid="stExpander"] summary svg,
        [data-testid="stExpander"] svg {{
            fill: {p['accent']} !important;
            stroke: {p['accent']} !important;
            color: {p['accent']} !important;
        }}
    </style>
    """, unsafe_allow_html=True)