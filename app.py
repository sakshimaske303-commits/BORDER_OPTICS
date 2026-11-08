import json
import os

import pandas as pd
import streamlit as st
from scipy.stats import t as t_dist
from utils.theme import inject_theme, PALETTE
from utils.data import load_data
from utils.doc_viewer import render_doc_viewer

st.set_page_config(page_title="BORDER OPTICS", layout="wide", initial_sidebar_state="expanded")
inject_theme()

villages, full_year, summer = load_data()


st.markdown("<h1>BORDER OPTICS</h1>", unsafe_allow_html=True)
st.markdown(
    "<h3 style='text-align: center; font-weight: 700; margin-top: -10px;'>"
    "Evaluating a Place-Based Border Programme from Space: Evidence and Indicator Limits from India's Vibrant Villages Programme</h3>",
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <style>
        .doi-badge-link {{ text-decoration:none; }}
        .doi-badge-card {{ transition: transform 0.18s ease, box-shadow 0.18s ease, filter 0.18s ease; cursor: pointer; }}
        .doi-badge-link:hover .doi-badge-card {{ transform: translateY(-3px) scale(1.02); box-shadow: 0 10px 32px rgba(255, 124, 172, 0.6); filter: brightness(1.08); }}
    </style>
    <div style="display:flex; flex-wrap:wrap; justify-content:center; gap:16px; margin: 10px 0 18px 0;">
        <a href="https://eartharxiv.org/repository/view/14830/" target="_blank" class="doi-badge-link" style="text-decoration:none;">
            <div class="doi-badge-card" style="
                display:flex; align-items:center; gap:18px;
                background: linear-gradient(145deg, {PALETTE['bg_card']}, {PALETTE['bg_main']});
                border: 2px solid {PALETTE['accent_vintage']};
                border-radius: 14px;
                padding: 16px 32px;
                box-shadow: 0 4px 20px rgba(255, 124, 172, 0.35);
            ">
                <div style="text-align:left;">
                    <div style="color:{PALETTE['accent']}; font-family:'Inter',sans-serif; font-weight:800; font-size:1.05rem; letter-spacing:0.4px; display:flex; align-items:center; gap:8px;">
                        <span>PREPRINT ON EARTHARXIV</span>
                        <span style="opacity:0.8; font-size:0.95rem;">↗</span>
                    </div>
                    <div style="color:{PALETTE['text_primary']}; font-family:'Inter',sans-serif; font-weight:900; font-size:1.35rem; margin-top:2px;">
                        Read the preprint
                    </div>
                </div>
            </div>
        </a>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")

core_n = int((villages["is_core_sample"] == True).sum())
illus_n = int(len(villages) - core_n)
core_states = villages.loc[villages["is_core_sample"] == True, "state"].nunique()
n_control = len(pd.read_csv("data/processed/border_optics_control_villages.csv"))
did_ps = []
for _path in ["data/processed/border_optics_did_summary_fullyear.json", "data/processed/border_optics_did_summary_summer.json"]:
    with open(_path) as _f:
        # t with 12 df (13 district clusters from v2.1), matching the paper's Table 2
        did_ps += [2 * t_dist.sf(abs(r["did_coef"] / r["did_se"]), 12) for r in json.load(_f)["did"]]
with open("outputs/dynamic_world_robustness_results.json") as _f:
    _dw = json.load(_f)["summer_main"]

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("CORE SAMPLE", f"{core_n} villages", f"{core_states} states (+{illus_n} outside core)")
with col2:
    st.metric("COMPARISON GROUP", f"{n_control} villages", "same 13 districts")
with col3:
    st.metric("NDBI & NIGHT-LIGHT DiD", "no difference", f"p = {min(did_ps):.2f}–{max(did_ps):.2f}", delta_color="off")
with col4:
    st.metric("DYNAMIC WORLD DiD (SUMMER)", f"+{_dw['coef']:.4f}", f"bootstrap p = {_dw['wild_cluster_bootstrap_p']:.3f}",
              delta_color="off")

st.markdown("---")

st.markdown(
    f"""
    <div style="padding: 20px 26px; margin: 4px 0 20px 0; background: rgba(255, 124, 172, 0.06);
                border: 1px solid rgba(255, 124, 172, 0.3); border-left: 4px solid {PALETTE['accent_vintage']};
                border-radius: 10px;">
        <p style="color:{PALETTE['accent_vintage']}; text-transform:uppercase; letter-spacing:1.5px;
                  font-weight:800; font-size:0.85rem; margin-bottom:8px;">Research Question</p>
        <p style="color:{PALETTE['text_primary']}; font-size:1.05rem; line-height:1.6; margin:0 0 10px 0; font-weight:700;">
            Did India's Vibrant Villages Programme priority villages show more satellite-observed built-up
            and night-light change between 2021 and 2025 than non-priority villages in the same districts?
        </p>
        <p style="color:{PALETTE['text_primary']}; font-size:0.95rem; line-height:1.6; margin:0;">
            Asked in Parliament whether the programme's impact had been assessed, the Ministry of Home Affairs
            replied that "no impact assessment has been carried out" (Lok Sabha Unstarred Question No. 508,
            3 February 2026). This project tests the ₹4,800 crore programme against independent satellite
            evidence, and asks how much change each satellite measure could actually detect.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

col_left, col_right = st.columns([1.1, 1])

with col_left:
    st.markdown("""
    ### What Is BORDER OPTICS?

    The **Vibrant Villages Programme (VVP-I)**, approved in February 2023, funds roads, power,
    communications and livelihood works in 2,967 border villages, 662 of them priority villages.
    Official reports describe sanctioned works but do not independently verify change on the ground.

    BORDER OPTICS compares **220 geocoded priority villages** in Arunachal Pradesh and
    Uttarakhand with **628 non-priority villages in the same 13 districts**, using four satellite
    measures (Sentinel-2 NDBI, VIIRS night lights, Sentinel-1 radar, Dynamic World built-up
    probability) in a difference-in-differences design, and checks every measure against Google
    Open Buildings footprints to estimate what it can and cannot detect. Sikkim is left out from
    version 2.1, because none of its comparison villages could be verified inside its district.
    """)

with col_right:
    st.markdown(f"""
    <div class="recon-card">
        <p style="color:{PALETTE['accent']}; text-transform:uppercase; font-size:0.78rem;
                  letter-spacing:1.5px; font-weight:800; margin-bottom:12px;">Core Findings (v2.1)</p>
        <p style="color:{PALETTE['text_primary']}; font-size:0.93rem; line-height:1.65; margin:0; font-weight:500;">
            <b>1.</b> NDBI, night lights and radar show no difference between priority and comparison villages.<br>
            <b>2.</b> That null cannot rule out construction: buildings cover a median 0.32% of a 500 m buffer,
            so doubling a village's buildings would move the NDBI average by only ~0.002, far below what the
            design can detect.<br>
            <b>3.</b> Dynamic World, the measure most sensitive to buildings, shows a small positive difference
            in the summer window (≈1,900 m² of built-up surface per village); the full-year estimate is not significant.<br>
            <b>4.</b> No consistent border-proximity pattern: pooled correlations disappear or reverse within
            districts.<br>
            See Statistical Validation and Methodology &amp; Limitations for details.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

st.markdown("### Methodology at a Glance")

m1, m2, m3 = st.columns(3)

with m1:
    st.markdown(f"""
    <div class="recon-card" style="min-height: 190px;">
        <p style="color: {PALETTE['border_up']}; font-weight: 800; font-size: 0.85rem; text-transform: uppercase; margin-bottom: 10px;">Satellite Measures</p>
        <p style="color: {PALETTE['text_primary']}; font-size: 0.88rem; margin: 0;">
            Sentinel-2 NDBI, VIIRS night lights, Sentinel-1 radar and Dynamic World built-up
            probability in a 500 m buffer around 220 priority and 628 comparison villages,
            2021 and 2025 (plus a 2019 placebo year), full-year and June–September composites.
            Google Open Buildings footprints size what each measure can detect.
        </p>
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown(f"""
    <div class="recon-card" style="min-height: 190px;">
        <p style="color: {PALETTE['lights']}; font-weight: 800; font-size: 0.85rem; text-transform: uppercase; margin-bottom: 10px;">Primary Analysis</p>
        <p style="color: {PALETTE['text_primary']}; font-size: 0.88rem; margin: 0;">
            Within-district difference-in-differences of priority vs. comparison villages,
            with t (12 df) and an exact wild cluster bootstrap for 13 district clusters, checked
            by a 2019–2021 placebo, leave-one-district-out and randomization inference. Border
            distance is analysed pooled and within districts.
        </p>
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown(f"""
    <div class="recon-card" style="min-height: 190px;">
        <p style="color: {PALETTE['border_down']}; font-weight: 800; font-size: 0.85rem; text-transform: uppercase; margin-bottom: 10px;">Honest Validation</p>
        <p style="color: {PALETTE['text_primary']}; font-size: 0.88rem; margin: 0;">
            Every data gap — Ladakh's unresolved villages, Himachal Pradesh's partial
            sample, Uttarakhand's block ambiguity — is disclosed transparently, not
            papered over.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

st.markdown("### Explore the Evidence")

nav_items = [
    ("Study Design", "Research question, design, sample overview"),
    ("Theoretical Foundations", "Why Himalayan terrain and altitude drive measurement uncertainty"),
    ("Built-Up Change", "NDBI findings across all villages"),
    ("Night-Lights", "VIIRS radiance change findings"),
    ("Statistical Validation", "Difference-in-differences, detectability, robustness"),
    ("Explore Trends", "Cross-state comparison and multi-year trend"),
    ("Interactive Maps & Plots", "Live village-level geospatial exploration plus the three headline charts"),
    ("Methodology & Limitations", "Full transparency on data and methods"),
]

cols = st.columns(3)
for i, (title, desc) in enumerate(nav_items):
    with cols[i % 3]:
        st.markdown(f"""
        <div class="recon-card" style="margin-bottom: 14px; min-height: 110px;">
            <p style="color: {PALETTE['text_primary']}; font-weight: 800; font-size: 0.95rem; margin: 0 0 4px 0;">{title}</p>
            <p style="color: {PALETTE['text_secondary']}; font-size: 0.8rem; margin: 0; font-weight: 600;">{desc}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ============================================================
# FULL PROJECT DOCUMENTATION
# ============================================================
st.markdown("### Full Project Documentation")
st.markdown(
    f"<p style='color:{PALETTE['text_secondary']}; font-weight:600;'>"
    "The executive summary, research paper, development log and declarations open directly below, no download needed.</p>",
    unsafe_allow_html=True,
)

_all_docs = [
    {"label": "Executive Summary", "filename": "BO_Executive_Summary.pdf"},
    {"label": "Research Paper", "filename": "BO_Research_Paper.pdf"},
    {"label": "Development Log", "filename": "BO_Development_Log.pdf"},
    {"label": "Declarations", "filename": "BO_Declarations.pdf"},
]
_docs = [d for d in _all_docs if os.path.exists(os.path.join("static", d["filename"]))]
_missing = [d for d in _all_docs if d not in _docs]

if _docs:
    render_doc_viewer(
        docs=_docs,
        colors={
            "navy_dark": PALETTE["bg_main"],
            "navy_med": PALETTE["bg_card"],
            "magenta": PALETTE["accent_vintage"],
            "teal": PALETTE["accent"],
            "text_light": PALETTE["text_primary"],
        },
    )
for d in _missing:
    st.warning(f"{d['filename']} not found.")

st.markdown(
    f"""
    <div style="text-align:center; margin: 22px 0 6px 0;">
        <a href="https://github.com/sakshimaske303-commits/BORDER_OPTICS" target="_blank" style="text-decoration:none;">
            <span style="display:inline-block; background: linear-gradient(90deg, {PALETTE['accent']}, {PALETTE['accent_vintage']}); color:#1C1C1C; font-weight:800; font-size:0.95rem; padding:12px 28px; border-radius:8px;">
                View Full Project on GitHub
            </span>
        </a>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")

# ============================================================
# FOOTER
# ============================================================
st.markdown(
    f"""
    <div style="text-align: center; padding: 25px;" class="recon-card">
        <p style="color: {PALETTE['text_secondary']}; text-transform: uppercase; letter-spacing: 2px; font-size: 0.8rem; font-weight: 700;">Developed by</p>
        <h2 style="color: {PALETTE['accent_vintage']}; margin: 5px 0; border: none; padding: 0;">SAKSHI D. MASKE</h2>
        <p style="color: {PALETTE['accent']}; font-weight: 700;">Satellite data and policy, self-directed research</p>
    </div>
    """,
    unsafe_allow_html=True,
)