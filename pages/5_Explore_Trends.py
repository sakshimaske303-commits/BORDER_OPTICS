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
across the core statistical sample (Arunachal Pradesh, Sikkim, Uttarakhand), with
Himachal Pradesh reported separately as an illustrative case study, and to explore
whether change tracks allocated VVP-I budget.
""")

st.markdown("---")

# ============================================================
# STATE-WISE COMPARISON (CORE SAMPLE ONLY)
# ============================================================
st.markdown("### Core Sample: State-Wise Mean Change (Summer-Matched)")

core = summer[summer["is_core_sample"] == True] if "is_core_sample" in summer.columns else summer
valid = core.dropna(subset=["ndbi_change"])

state_stats = valid.groupby("state").agg(
    villages=("village_id", "count"),
    mean_ndbi_change=("ndbi_change", "mean"),
    mean_lights_change=("lights_change", "mean"),
).round(4).reset_index().rename(columns={"state": "State"})

metric_choice = st.radio("Metric", ["NDBI Change", "Lights Change"], horizontal=True)
metric_col = "mean_ndbi_change" if metric_choice == "NDBI Change" else "mean_lights_change"
bar_color = PALETTE["border_up"] if metric_choice == "NDBI Change" else PALETTE["lights"]

chart_stats = state_stats.dropna(subset=[metric_col])

fig = go.Figure()
fig.add_trace(go.Bar(
    x=chart_stats["State"], y=chart_stats[metric_col],
    marker_color=bar_color,
    text=chart_stats[metric_col].round(4), textposition="outside",
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

st.dataframe(state_stats, use_container_width=True, hide_index=True)

st.caption(
    "Sikkim may be absent from one or both metrics above — its summer-matched composite "
    "returned zero cloud-free imagery for most villages due to monsoon cloud cover (see "
    "Statistical Validation and Methodology & Limitations)."
)

st.markdown("##### Static exports (used in Research Paper)")
st.image(
    "outputs/figures/04_state_mean_ndbi_change.png",
    caption="Static export: state-wise mean NDBI change",
    use_container_width=True,
)
st.image(
    "outputs/figures/05_state_mean_lights_change.png",
    caption="Static export: state-wise mean night-lights change",
    use_container_width=True,
)

st.markdown("---")

# ============================================================
# THREE-POINT MULTI-YEAR TREND (2021 / 2023 / 2025)
# ============================================================
st.markdown("### Multi-Year Trend — 2021 / 2023 / 2025")
st.markdown(
    "The core comparison above rests on two single years. This extends the same core sample "
    "to a third, independent time point (2023), so a trend line — not a two-point difference — "
    "carries the evidentiary weight. Pick a window and a state to see its own trend line."
)

my_window_choice = st.radio("Compositing window", ["Summer-Matched", "Full-Year"], horizontal=True, key="trend_window")
my_path = (
    "data/processed/border_optics_multiyear_summer.csv"
    if my_window_choice == "Summer-Matched"
    else "data/processed/border_optics_multiyear_fullyear.csv"
)
my_df = pd.read_csv(my_path)
my_core = my_df[my_df["is_core_sample"] == True] if "is_core_sample" in my_df.columns else my_df

my_state_choice = st.selectbox("State (or All)", ["All"] + sorted(my_core["state"].unique().tolist()), key="trend_state")
my_scope = my_core if my_state_choice == "All" else my_core[my_core["state"] == my_state_choice]

years = [2021, 2023, 2025]
trend_col_choice = st.radio("Metric", ["NDBI", "Night-Lights"], horizontal=True, key="trend_metric")
trend_prefix = "ndbi" if trend_col_choice == "NDBI" else "lights"

means = [my_scope[f"{trend_prefix}_{y}"].mean() for y in years]
sems = [my_scope[f"{trend_prefix}_{y}"].std() / (my_scope[f"{trend_prefix}_{y}"].count() ** 0.5) for y in years]

fig_trend = go.Figure()
fig_trend.add_trace(go.Scatter(
    x=years, y=means, mode="lines+markers",
    line=dict(color=PALETTE["border_up"] if trend_prefix == "ndbi" else PALETTE["lights"], width=3),
    marker=dict(size=10),
    error_y=dict(type="data", array=sems, visible=True),
    name=f"Mean {trend_col_choice}",
))
fig_trend.update_layout(
    template="plotly_dark",
    height=380,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color=PALETTE["text_primary"]),
    margin=dict(t=30, b=40, l=40, r=40),
    xaxis=dict(tickmode="array", tickvals=years),
    yaxis_title=f"Mean {trend_col_choice}",
)
st.plotly_chart(fig_trend, use_container_width=True)

st.caption(
    f"{my_state_choice} · {my_window_choice.lower()} window · n = {my_scope[f'{trend_prefix}_2021'].count()} villages with complete 2021/2023/2025 data. "
    "The overall summer-matched NDBI trend across all three years is not itself statistically significant "
    "(Wilcoxon on per-village slopes, p = 0.442) — the reported 2021-vs-2025 increase is concentrated in a "
    "2023-to-2025 recovery following an earlier 2021-to-2023 decline (see Statistical Validation)."
)

st.image(
    "outputs/figures/09_multiyear_trend.png",
    caption="Static export: mean NDBI and night-lights at 2021/2023/2025, core sample, both windows",
    use_container_width=True,
)

st.markdown("---")

# ============================================================
# HIMACHAL PRADESH — ILLUSTRATIVE CASE STUDY (SEPARATE, NOT CORE SAMPLE)
# ============================================================
st.markdown("### Himachal Pradesh — Illustrative Case Study (Not Core Sample)")

hp = summer[summer["state"] == "Himachal Pradesh"].dropna(subset=["ndbi_change"])

if len(hp) > 0:
    h1, h2, h3 = st.columns(3)
    h1.metric("Villages", len(hp))
    h2.metric("Mean NDBI Change", f"{hp['ndbi_change'].mean():.4f}")
    h3.metric("Mean Lights Change", f"{hp['lights_change'].mean():.4f}")

    st.markdown(f"""
    <div class="recon-card" style="border-left: 4px solid {PALETTE['lights']};">
        <p style="color: {PALETTE['lights']}; font-weight: 800; font-size: 0.85rem; text-transform: uppercase; margin-bottom: 10px;">Why This Is Separate</p>
        <p style="color: {PALETTE['text_primary']}; font-size: 0.9rem; margin: 0;">
            Only 7 of Himachal Pradesh's 51 inhabited priority villages could be confidently
            named and geocoded, out of 75 total priority villages under the state's VVP-I
            Action Plan. This is not a random or representative sample of the state, so its
            numbers are shown here for transparency but excluded from the core three-state
            statistical comparison above and from the formal hypothesis tests in Statistical
            Validation.
        </p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.warning("No valid Himachal Pradesh data for this composite window.")

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
        This correlation is <b>exploratory only</b> — with just two core states with
        sufficient valid data, this has very limited statistical power. It is a directional
        signal worth revisiting with a larger multi-state sample, not evidence of a causal
        budget-to-outcome link.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ============================================================
# LIVE STATE DRILL-DOWN (ALL STATES, FOR EXPLORATION)
# ============================================================
st.markdown("### Live State Drill-Down")

all_valid = summer.dropna(subset=["ndbi_change"])
selected_state = st.selectbox("Select a state", sorted(all_valid["state"].unique()))
state_df = all_valid[all_valid["state"] == selected_state]

if selected_state == "Himachal Pradesh":
    st.caption("Illustrative case study only — not part of the core statistical sample.")

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