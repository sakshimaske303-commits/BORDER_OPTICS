import streamlit as st
from utils.theme import inject_theme, PALETTE
from utils.data import load_data

st.set_page_config(page_title="BORDER OPTICS", page_icon="🛰️", layout="wide", initial_sidebar_state="expanded")
inject_theme()

villages, full_year, summer = load_data()

from scipy import stats

st.markdown("<h1>🛰️ BORDER OPTICS</h1>", unsafe_allow_html=True)
st.markdown(
    "<h3 style='text-align: center; font-weight: 700; margin-top: -10px;'>"
    "A Satellite-Based Verification Framework for India's Vibrant Villages Programme (VVP-I)</h3>",
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <style>
        .doi-badge-link {{ text-decoration:none; }}
        .doi-badge-card {{ transition: transform 0.18s ease, box-shadow 0.18s ease, filter 0.18s ease; cursor: pointer; }}
        .doi-badge-link:hover .doi-badge-card {{ transform: translateY(-3px) scale(1.02); box-shadow: 0 10px 32px rgba(255, 124, 172, 0.6); filter: brightness(1.08); }}
    </style>
    <div style="display:flex; justify-content:center; margin: 10px 0 18px 0;">
        <a href="https://doi.org/10.5281/zenodo.21759970" target="_blank" class="doi-badge-link" style="text-decoration:none;">
            <div class="doi-badge-card" style="
                display:flex; align-items:center; gap:18px;
                background: linear-gradient(145deg, {PALETTE['bg_card']}, {PALETTE['bg_main']});
                border: 2px solid {PALETTE['accent_vintage']};
                border-radius: 14px;
                padding: 16px 32px;
                box-shadow: 0 4px 20px rgba(255, 124, 172, 0.35);
            ">
                <span style="font-size:2.1rem; line-height:1;">📦</span>
                <div style="text-align:left;">
                    <div style="color:{PALETTE['accent']}; font-family:'Inter',sans-serif; font-weight:800; font-size:1.05rem; letter-spacing:0.4px; display:flex; align-items:center; gap:8px;">
                        <span>ARCHIVED &amp; CITABLE ON ZENODO</span>
                        <span style="opacity:0.8; font-size:0.95rem;">↗</span>
                    </div>
                    <div style="color:{PALETTE['text_primary']}; font-family:'Inter',sans-serif; font-weight:900; font-size:1.35rem; margin-top:2px;">
                        DOI: 10.5281/zenodo.21759970
                    </div>
                </div>
            </div>
        </a>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")

valid_ndbi = summer.dropna(subset=["ndbi_change"])
peak_row = valid_ndbi.loc[valid_ndbi["ndbi_change"].idxmax()] if len(valid_ndbi) else None
paired = summer.dropna(subset=["ndbi_before", "ndbi_after"])
if len(paired) >= 2:
    _, p_val = stats.wilcoxon(paired["ndbi_before"], paired["ndbi_after"])
else:
    p_val = float("nan")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("STUDY REGION", f"{villages['state'].nunique()} States", "Himalayan Border Belt")
with col2:
    st.metric("PEAK NDBI CHANGE", f"{peak_row['ndbi_change']:.3f}" if peak_row is not None else "—",
               peak_row["village"] if peak_row is not None else None)
with col3:
    st.metric("STATISTICAL SIGNIFICANCE", f"p = {p_val:.4f}" if p_val == p_val else "—")
with col4:
    st.metric("VILLAGES VERIFIED", f"{len(villages)}", "Multi-Source Geocoded")

st.markdown("---")

st.markdown(
    f"""
    <div style="padding: 20px 26px; margin: 4px 0 20px 0; background: rgba(255, 124, 172, 0.06);
                border: 1px solid rgba(255, 124, 172, 0.3); border-left: 4px solid {PALETTE['accent_vintage']};
                border-radius: 10px;">
        <p style="color:{PALETTE['accent_vintage']}; text-transform:uppercase; letter-spacing:1.5px;
                  font-weight:800; font-size:0.85rem; margin-bottom:8px;">⚡ Why This Matters</p>
        <p style="color:{PALETTE['text_primary']}; font-size:1rem; line-height:1.6; margin:0;">
            Asked directly in Parliament whether the Vibrant Villages Programme's impact had ever been
            assessed, the Ministry of Home Affairs answered without qualification: "No impact assessment
            has been carried out" (Lok Sabha Unstarred Question No. 508, 3 February 2026). This project
            is that missing independent assessment — testing ₹4,800 crore of sanctioned border-development
            spending against satellite-observed physical change, rather than trusting official progress
            reports alone. And when the two most defensible measurement choices produce opposite
            conclusions, that instability is reported as the finding, not resolved by picking whichever
            version looks better.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

col_left, col_right = st.columns([1.1, 1])

with col_left:
    st.markdown("""
    ### What Is BORDER OPTICS?

    Under the **Vibrant Villages Programme (VVP-I)**, the Government of India sanctioned
    infrastructure and development spending across border villages in Arunachal Pradesh,
    Sikkim, Uttarakhand, Himachal Pradesh, and Ladakh. Official progress reports describe
    spending and sanctioned works, but do not independently verify physical, observable
    change on the ground.

    This project fills that gap: applying **Sentinel-2 built-up-area indices (NDBI)** and
    **VIIRS night-lights** data to 258 individually geocoded villages, testing whether
    measurable change occurred between 2021 and 2025, whether it correlates with state-wise
    budget allocation, and whether proximity to the border/LAC itself predicts the pace
    of development — with every data gap and methodological trade-off disclosed transparently.
    """)

with col_right:
    st.markdown(f"""
    <div class="recon-card">
        <p style="color:{PALETTE['accent']}; text-transform:uppercase; font-size:0.78rem;
                  letter-spacing:1.5px; font-weight:800; margin-bottom:12px;">Core Finding</p>
        <p style="color:{PALETTE['text_primary']}; font-size:0.95rem; line-height:1.7; margin:0; font-weight:500;">
            Built-up area change across the sample was tested under two independent
            compositing windows — full-year and summer-matched — to guard against
            seasonal artifacts. Where the two windows agree, the result is reported with
            confidence; where they diverge, that instability is disclosed as a genuine
            finding rather than resolved by discarding one window. See Statistical
            Validation for the full breakdown.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

st.markdown("### Methodology at a Glance")

m1, m2, m3 = st.columns(3)

with m1:
    st.markdown(f"""
    <div class="recon-card" style="min-height: 190px;">
        <p style="color: {PALETTE['border_up']}; font-weight: 800; font-size: 0.85rem; text-transform: uppercase; margin-bottom: 10px;">🛰️ Satellite Verification</p>
        <p style="color: {PALETTE['text_primary']}; font-size: 0.88rem; margin: 0;">
            Sentinel-2 NDBI and VIIRS night-lights extracted at 258 village points (500m
            buffer), across paired 2021/2025 composites, under both full-year and
            season-matched windows.
        </p>
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown(f"""
    <div class="recon-card" style="min-height: 190px;">
        <p style="color: {PALETTE['lights']}; font-weight: 800; font-size: 0.85rem; text-transform: uppercase; margin-bottom: 10px;">📊 Statistical Testing</p>
        <p style="color: {PALETTE['text_primary']}; font-size: 0.88rem; margin: 0;">
            Wilcoxon signed-rank tests for before/after change, and Spearman correlations
            for budget (RQ2) and border-proximity (H3), with sample-size caveats disclosed
            wherever a test is exploratory.
        </p>
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown(f"""
    <div class="recon-card" style="min-height: 190px;">
        <p style="color: {PALETTE['border_down']}; font-weight: 800; font-size: 0.85rem; text-transform: uppercase; margin-bottom: 10px;">🔥 Honest Validation</p>
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
    ("🏛️", "Study Design", "Research questions, hypotheses, sample overview"),
    ("🏔️", "Theoretical Foundations", "Why Himalayan terrain and altitude drive measurement uncertainty"),
    ("🏗️", "Built-Up Change", "NDBI findings across all villages"),
    ("💡", "Night-Lights", "VIIRS radiance change findings"),
    ("📊", "Statistical Validation", "Wilcoxon tests, Spearman correlations, robustness"),
    ("📈", "Explore Trends", "Cross-state comparison, budget correlation"),
    ("🗺️", "Interactive Maps", "Live village-level geospatial exploration"),
    ("📖", "Methodology & Limitations", "Full transparency on data and methods"),
]

cols = st.columns(3)
for i, (icon, title, desc) in enumerate(nav_items):
    with cols[i % 3]:
        st.markdown(f"""
        <div class="recon-card" style="margin-bottom: 14px; min-height: 110px;">
            <p style="font-size: 1.6rem; margin: 0 0 6px 0;">{icon}</p>
            <p style="color: {PALETTE['text_primary']}; font-weight: 800; font-size: 0.95rem; margin: 0 0 4px 0;">{title}</p>
            <p style="color: {PALETTE['text_secondary']}; font-size: 0.8rem; margin: 0; font-weight: 600;">{desc}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ============================================================
# FULL PROJECT DOCUMENTATION
# ============================================================
st.markdown("### 📄 Full Project Documentation")
st.markdown(
    f"<p style='color:{PALETTE['text_secondary']}; font-weight:600;'>"
    "Download the complete research paper, project journal, and development log.</p>",
    unsafe_allow_html=True,
)

doc0, doc1, doc2, doc3 = st.columns(4)

with doc0:
    try:
        with open("BO_Executive_Summary.pdf", "rb") as f:
            st.download_button(
                label="⚡ Executive Summary (PDF)",
                data=f,
                file_name="BORDER_OPTICS_Executive_Summary.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
    except FileNotFoundError:
        st.warning("BO_Executive_Summary.pdf not found.")

with doc1:
    try:
        with open("BO_Research_Paper.pdf", "rb") as f:
            st.download_button(
                label="📘 Research Paper (PDF)",
                data=f,
                file_name="BORDER_OPTICS_Research_Paper.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
    except FileNotFoundError:
        st.warning("BO_Research_Paper.pdf not found.")

with doc2:
    try:
        with open("BO_Project_Report.pdf", "rb") as f:
            st.download_button(
                label="📗 Project Report (PDF)",
                data=f,
                file_name="BORDER_OPTICS_Project_Report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
    except FileNotFoundError:
        st.warning("BO_Project_Report.pdf not found.")

with doc3:
    try:
        with open("BO_Development_Log.pdf", "rb") as f:
            st.download_button(
                label="📙 Development Log (PDF)",
                data=f,
                file_name="BORDER_OPTICS_Development_Log.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
    except FileNotFoundError:
        st.warning("BO_Development_Log.pdf not found.")

st.markdown(
    f"""
    <div style="text-align:center; margin: 22px 0 6px 0;">
        <a href="https://github.com/sakshimaske303-commits/BORDER_OPTICS" target="_blank" style="text-decoration:none;">
            <span style="display:inline-block; background: linear-gradient(90deg, {PALETTE['accent']}, {PALETTE['accent_vintage']}); color:#1C1C1C; font-weight:800; font-size:0.95rem; padding:12px 28px; border-radius:8px;">
                🔗 View Full Project on GitHub
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
        <p style="color: {PALETTE['accent']}; font-weight: 700;">Independent Geospatial Researcher</p>
    </div>
    """,
    unsafe_allow_html=True,
)