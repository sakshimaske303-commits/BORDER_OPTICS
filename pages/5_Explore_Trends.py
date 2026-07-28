import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.theme import inject_theme, PALETTE
from utils.data import load_data

st.set_page_config(page_title="Explore Trends — BORDER OPTICS", page_icon="📈", layout="wide")
inject_theme()

villages, full_year, summer = load_data()

st.markdown("<h1>📈 EXPLORE TRENDS</h1>", unsafe_allow_html=True)
st.markdown(
    "<h3 style='text-align: center; font-weight: 700;'>Cross-State Comparison</h3>",
    unsafe_allow_html=True,
)
st.markdown("---")

st.markdown("""
Aggregating village-level results up to the state level to compare the pace of change
across Arunachal Pradesh, Sikkim, Uttarakhand, and Himachal Pradesh, and to explore
whether it tracks allocated VVP-I budget.
""")

st.markdown("---")

# ============================================================
# STATE-WISE COMPARISON (PLOTLY)
# ============================================================
st.markdown("### State-Wise Mean Change (Summer-Matched)")

valid = summer.dropna(subset=["ndbi_change"])
state_stats = valid.groupby("state").agg(
    villages=("village_id", "count"),
    mean_ndbi_change=("ndbi_change", "mean"),
    mean_lights_change=("lights_change", "mean"),
).round(4).reset_index().rename(columns={"state": "State"})

metric_choice = st.radio("Metric", ["NDBI Change", "Lights Change"], horizontal=True)
metric_col = "mean_ndbi_change" if metric_choice == "NDBI Change" else "mean_lights_change"
bar_color = PALETTE["border_up"] if metric_choice == "NDBI Change" else PALETTE["lights"]

fig = go.Figure()
fig.add_trace(go.Bar(
    x=state_stats["State"], y=state_stats[metric_col],
    marker_color=bar_color,
    text=state_stats[metric_col].round(4), textposition="outside",
))
fig.update_layout(
    template="plotly_dark",
    height=420,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color=PALETTE["text_primary"]),
    margin=dict(t=30, b=40, l=40, r=40),
    yaxis_title=metric_choice,
)
st.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns([1.2, 1])
with col1:
    st.dataframe(state_stats, use_container_width=True, hide_index=True)

st.markdown("---")

# ============================================================
# BUDGET CORRELATION (RQ2)
# ============================================================
st.markdown("### RQ2 — Change vs. Budget Allocation")

st.image(
    "outputs/figures/02_state_change_vs_budget.png",
    caption="State-level built-up change vs. VVP-I budget allocation",
    use_container_width=True,
)

st.markdown(f"""
<div class="recon-card" style="border-left: 4px solid {PALETTE['warning']};">
    <p style="color: {PALETTE['warning']}; font-weight: 800; font-size: 0.85rem; text-transform: uppercase; margin-bottom: 10px;">Interpretation Caveat</p>
    <p style="color: {PALETTE['text_primary']}; font-size: 0.9rem; margin: 0;">
        This correlation is <b>exploratory only</b> — with just four states in the sample, a
        Spearman correlation at the state level has very limited statistical power. It is a
        directional signal worth revisiting with a larger multi-state sample, not evidence of
        a causal budget-to-outcome link.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ============================================================
# LIVE STATE DRILL-DOWN
# ============================================================
st.markdown("### 🎛️ Live State Drill-Down")

selected_state = st.selectbox("Select a state", sorted(valid["state"].unique()))
state_df = valid[valid["state"] == selected_state]

d1, d2, d3 = st.columns(3)
d1.metric("Villages", len(state_df))
d2.metric("Mean NDBI Change", f"{state_df['ndbi_change'].mean():.4f}")
d3.metric("Mean Lights Change", f"{state_df['lights_change'].mean():.4f}")

display_cols = [c for c in ["village", "district", "block", "ndbi_change", "lights_change", "distance_to_border_km"] if c in state_df.columns]
st.dataframe(
    state_df[display_cols].sort_values("ndbi_change", ascending=False),
    use_container_width=True, hide_index=True, height=350,
)

st.markdown("---")
st.markdown(
    "<p class='caption-text' style='text-align:center;'>BORDER OPTICS — Cross-state comparison, village-level granularity</p>",
    unsafe_allow_html=True,
)