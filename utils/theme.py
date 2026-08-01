import streamlit as st

# ============================================================
# BORDER OPTICS — Watermelon & Mint Theme
# ============================================================
PALETTE = {
    "bg_main": "#1C1C1C",
    "bg_card": "#262626",
    "bg_sidebar": "#141414",
    "border_up": "#A7E1C1",      # mint — growth / increase
    "border_down": "#FF7CAC",    # watermelon — decrease
    "lights": "#FF7CAC",         # watermelon — night-lights theme
    "warning": "#E8709D",        # deeper watermelon — warnings
    "text_primary": "#F2F2F0",   # warm off-white
    "text_secondary": "#9A9A98", # muted gray
    "accent": "#A7E1C1",         # mint — primary highlight
    "accent_vintage": "#FF7CAC", # watermelon — secondary highlight
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
            padding-top: 1rem !important;
            padding-bottom: 2rem !important;
        }}

        /* ---- Keep header visible (needed for the sidebar
        open/close button) but hide only the Deploy button ---- */
        [data-testid="stHeader"] {{
            background-color: {p['bg_main']} !important;
            height: 3rem !important;
        }}
        [data-testid="stAppDeployButton"] {{
            display: none !important;
        }}
        [data-testid="stDecoration"] {{
            display: none !important;
        }}
        #MainMenu {{
            visibility: hidden !important;
        }}

        /* ---- Sidebar collapse/expand button — safety net
        covering every naming variant Streamlit has used
        across versions, since it's invisible-by-default on
        a dark theme and hard to see on mobile otherwise ---- */
        [data-testid="collapsedControl"],
        [data-testid="stSidebarCollapsedControl"],
        [data-testid="stSidebarCollapseButton"],
        [data-testid="baseButton-header"],
        [data-testid="stHeader"] button,
        [data-testid*="ollapse" i],
        button[kind="header"] {{
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            z-index: 999999 !important;
        }}
        [data-testid="collapsedControl"],
        [data-testid="stSidebarCollapsedControl"] {{
            position: fixed !important;
            top: 12px !important;
            left: 12px !important;
            background: {p['bg_sidebar']} !important;
            border: 1.5px solid {p['accent_vintage']} !important;
            border-radius: 8px !important;
            padding: 4px !important;
        }}
        [data-testid="collapsedControl"] svg,
        [data-testid="stSidebarCollapsedControl"] svg,
        [data-testid="stSidebarCollapseButton"] svg,
        [data-testid="baseButton-header"] svg,
        [data-testid="stHeader"] button svg,
        button[kind="header"] svg {{
            fill: {p['accent']} !important;
            stroke: {p['accent']} !important;
            opacity: 1 !important;
        }}

        section[data-testid="stSidebar"] {{
            background: {p['bg_sidebar']};
            border-right: 1px solid rgba(167, 225, 193, 0.2);
        }}
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span {{
            color: {p['text_primary']} !important;
            font-weight: 600;
        }}

        h1 {{
            background: linear-gradient(90deg, {p['accent']}, {p['accent_vintage']});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 900 !important;
            font-size: 2.9rem !important;
            letter-spacing: -0.5px;
            text-align: center;
            filter: drop-shadow(0 0 22px rgba(167, 225, 193, 0.35));
        }}

        h2 {{
            color: {p['accent_vintage']} !important;
            font-weight: 800 !important;
            border-left: 4px solid {p['accent']};
            padding-left: 14px;
            font-size: 1.6rem !important;
        }}

        h3 {{
            color: {p['accent']} !important;
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
            background: rgba(38, 38, 38, 0.7);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid rgba(167, 225, 193, 0.25);
            border-top: 3px solid {p['accent_vintage']};
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
            color: #141414;
            border-radius: 8px;
            border: none;
            font-weight: 700;
        }}

        div[data-testid="stDownloadButton"] > button {{
            background: linear-gradient(90deg, {p['accent']}, {p['accent_vintage']});
            color: #141414;
            border-radius: 8px;
            border: none;
            font-weight: 700;
        }}
        div[data-testid="stDownloadButton"] > button:hover {{
            background: linear-gradient(90deg, {p['accent_vintage']}, {p['accent']});
            color: #141414;
        }}
        div[data-testid="stDownloadButton"] > button p {{
            color: #141414 !important;
        }}

        div[data-testid="stAlert"] {{
            border-radius: 10px;
            font-weight: 600;
            background: rgba(38, 38, 38, 0.7);
            backdrop-filter: blur(10px);
            border-left: 3px solid {p['accent_vintage']};
        }}

        hr {{
            border: none;
            height: 2px;
            background: linear-gradient(90deg, transparent, {p['accent']}, {p['accent_vintage']}, transparent);
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
            background: rgba(38, 38, 38, 0.7);
            border-radius: 8px 8px 0 0;
            color: {p['text_secondary']};
            font-weight: 700;
        }}
        .stTabs [aria-selected="true"] {{
            background: rgba(167, 225, 193, 0.2) !important;
            color: {p['accent']} !important;
            font-weight: 800;
            border-bottom: 2px solid {p['accent_vintage']} !important;
        }}

        .recon-card {{
            background: rgba(38, 38, 38, 0.7);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-radius: 14px;
            padding: 22px;
            border: 1px solid rgba(167, 225, 193, 0.25);
            border-top: 3px solid {p['accent']};
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.45);
        }}

        [data-testid="stExpander"] {{
            background-color: rgba(38, 38, 38, 0.7) !important;
            border: 1px solid rgba(167, 225, 193, 0.25) !important;
            border-radius: 10px !important;
        }}
        [data-testid="stExpander"] summary {{
            background-color: rgba(38, 38, 38, 0.9) !important;
        }}
        [data-testid="stExpander"] summary p {{
            font-size: 1.05rem !important;
            font-weight: 700 !important;
            color: {p['accent_vintage']} !important;
        }}
        [data-testid="stExpanderDetails"] {{
            background-color: rgba(38, 38, 38, 0.5) !important;
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