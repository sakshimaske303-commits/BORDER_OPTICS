import streamlit as st

# ============================================================
# BORDER OPTICS — Watermelon & Mint Theme
# (styling pattern matched to GREEN_ALIBI's utils/style.py —
#  same palette as before, just restyled: flat cards instead of
#  glass/blur, centered solid-color headers instead of gradient
#  text, simpler buttons/hr/alerts. See Devlopment_Log.md.)
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
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Poppins', sans-serif;
        }}

        .stApp {{
            background: {p['bg_main']};
            color: {p['text_primary']};
            font-family: 'Poppins', sans-serif;
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

        /* ---- Sidebar — translucent mint glass ---- */
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, rgba(167,225,193,0.62) 0%, rgba(143,212,174,0.62) 100%);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border-right: 3px solid {p['accent_vintage']};
        }}
        section[data-testid="stSidebar"] * {{
            color: #1C1C1C !important;
        }}
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span {{
            font-weight: 700;
        }}

        /* ---- Sidebar page nav list — all-caps, bolder + bigger,
        packed tight so every page fits without scrolling ---- */
        section[data-testid="stSidebar"] [data-testid="stSidebarNavItems"] {{
            padding-top: 4px !important;
            padding-bottom: 4px !important;
        }}
        section[data-testid="stSidebar"] [data-testid="stSidebarNavItems"] li,
        section[data-testid="stSidebar"] nav ul li,
        section[data-testid="stSidebar"] ul li {{
            margin-bottom: 3px !important;
        }}
        section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"],
        section[data-testid="stSidebar"] [data-testid="stSidebarNavItems"] a,
        section[data-testid="stSidebar"] nav a,
        section[data-testid="stSidebar"] ul li a {{
            font-weight: 900 !important;
            font-size: 1.3rem !important;
            line-height: 1.15 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.4px !important;
            color: #5C1030 !important;
            -webkit-text-stroke: 0.5px #5C1030;
            padding: 7px 14px !important;
            border-radius: 10px !important;
            transition: background-color 0.15s ease, transform 0.15s ease;
        }}
        section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"]:hover,
        section[data-testid="stSidebar"] nav a:hover,
        section[data-testid="stSidebar"] ul li a:hover {{
            background-color: rgba(255, 124, 172, 0.4) !important;
            transform: translateX(3px);
        }}
        section[data-testid="stSidebar"] [aria-selected="true"],
        section[data-testid="stSidebar"] [aria-current="page"] {{
            background-color: rgba(255, 124, 172, 0.55) !important;
            color: #3A0A1D !important;
            -webkit-text-stroke: 0.5px #3A0A1D;
            border-left: 5px solid {p['accent_vintage']};
            font-weight: 900 !important;
        }}

        /* ---- Headers ---- */
        h1 {{
            color: {p['accent_vintage']} !important;
            font-weight: 800 !important;
            font-size: 2.9rem !important;
            border-bottom: 3px solid {p['accent']};
            text-align: center !important;
            padding-bottom: 0.4rem;
        }}

        h2 {{
            color: {p['accent']} !important;
            font-weight: 700 !important;
            text-align: center !important;
            margin-top: 1.5rem !important;
        }}

        h3 {{
            color: {p['accent_vintage']} !important;
            text-align: center !important;
            font-weight: 600 !important;
        }}

        p, li {{
            color: {p['text_primary']};
            font-weight: 500;
        }}

        strong, b {{
            color: {p['accent']};
            font-weight: 700;
        }}

        /* ---- Metric cards ---- */
        div[data-testid="stMetric"] {{
            background-color: {p['bg_card']};
            border: 1px solid {p['accent']};
            border-left: 5px solid {p['accent_vintage']};
            border-radius: 8px;
            padding: 16px 18px;
        }}
        div[data-testid="stMetricValue"] {{
            color: {p['text_primary']} !important;
            font-weight: 800 !important;
            font-size: 1.6rem !important;
        }}
        div[data-testid="stMetricLabel"] {{
            color: {p['accent']} !important;
            text-transform: uppercase;
            font-size: 0.75rem !important;
            font-weight: 700 !important;
            letter-spacing: 1.5px;
        }}

        /* ---- Buttons ---- */
        .stButton>button {{
            background-color: {p['accent']};
            color: #1C1C1C;
            border-radius: 6px;
            border: none;
            font-weight: 700;
        }}
        .stButton>button:hover {{
            background-color: {p['accent_vintage']};
            color: #1C1C1C;
        }}

        div[data-testid="stDownloadButton"] > button {{
            background-color: {p['accent']};
            color: #1C1C1C;
            border-radius: 6px;
            border: none;
            font-weight: 700;
        }}
        div[data-testid="stDownloadButton"] > button:hover {{
            background-color: {p['accent_vintage']};
            color: #1C1C1C;
        }}
        div[data-testid="stDownloadButton"] > button p {{
            color: #1C1C1C !important;
        }}

        /* ---- Info / warning / success callouts ---- */
        div[data-testid="stAlert"] {{
            background-color: {p['bg_card']} !important;
            border-radius: 8px;
            border-left: 5px solid {p['accent']};
            color: {p['text_primary']} !important;
            font-weight: 600;
        }}

        hr {{
            border: none;
            border-top: 2px solid {p['accent']};
            margin: 1.8rem 0;
        }}

        .caption-text {{
            color: {p['text_secondary']};
            font-size: 0.88rem;
            font-weight: 600;
        }}

        /* ---- Tables / dataframes ---- */
        div[data-testid="stDataFrame"] {{
            border: 1px solid {p['accent']};
            border-radius: 6px;
        }}

        /* ---- Tabs ---- */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
        }}
        .stTabs [data-baseweb="tab"] {{
            color: {p['text_secondary']};
            font-weight: 700;
        }}
        .stTabs [aria-selected="true"] {{
            color: {p['accent_vintage']} !important;
            font-weight: 800;
            border-bottom: 3px solid {p['accent']} !important;
        }}

        /* ---- Custom content cards (used throughout app.py/pages) ---- */
        .recon-card {{
            background-color: {p['bg_card']};
            border: 1px solid {p['accent']};
            border-left: 5px solid {p['accent_vintage']};
            border-radius: 10px;
            padding: 22px;
        }}

        [data-testid="stExpander"] {{
            background-color: {p['bg_card']} !important;
            border: 1px solid {p['accent']} !important;
            border-radius: 8px !important;
        }}
        [data-testid="stExpander"] summary {{
            background-color: {p['bg_card']} !important;
        }}
        [data-testid="stExpander"] summary p {{
            font-size: 1.05rem !important;
            font-weight: 700 !important;
            color: {p['accent_vintage']} !important;
        }}
        [data-testid="stExpanderDetails"] {{
            background-color: {p['bg_card']} !important;
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
