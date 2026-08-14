"""Interactive Plotly versions of the three headline BORDER OPTICS statistical
figures. Same underlying processed CSVs/JSON as the static figures (08/09/10) -
just Plotly instead of matplotlib, so every point gets a hover tooltip."""

import json
import os

import numpy as np
import pandas as pd
import plotly.graph_objects as go

DATA = "data/processed"
OUT = "outputs/interactive_maps/plots"
os.makedirs(OUT, exist_ok=True)

BLUE = "#4C72B0"
ORANGE = "#DD8452"
RED = "#C44E52"
GREEN = "#55A868"

DARK_LAYOUT = dict(
    template="plotly_dark",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="#0b0f1a",
    font=dict(family="Inter, sans-serif", color="#F5F7FA"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
    margin=dict(t=70, b=50, l=220, r=60),
)


# ============================================================
# FIGURE 8 — Control-group DiD: treated-vs-control effect, both windows
# ============================================================
def build_did_effect():
    with open(f"{DATA}/border_optics_did_summary_fullyear.json") as f:
        did_fy = json.load(f)
    with open(f"{DATA}/border_optics_did_summary_summer.json") as f:
        did_sm = json.load(f)

    rows = []
    for window_label, data in [("Full-Year", did_fy), ("Summer-Matched", did_sm)]:
        for r in data["did"]:
            rows.append({
                "outcome": "NDBI" if r["outcome"] == "ndbi" else "Night-Lights",
                "window": window_label,
                "coef": r["did_coef"], "ci_lo": r["did_ci_lo"], "ci_hi": r["did_ci_hi"],
                "p": r["did_p"],
            })
    df = pd.DataFrame(rows)
    labels = [f"{r.outcome} ({r.window})" for r in df.itertuples()]

    fig = go.Figure()
    for window, color in [("Full-Year", BLUE), ("Summer-Matched", ORANGE)]:
        sub = df[df["window"] == window]
        sub_labels = [f"{o} ({window})" for o in sub["outcome"]]
        fig.add_trace(go.Scatter(
            x=sub["coef"], y=sub_labels, mode="markers", name=window,
            marker=dict(size=14, color=color, line=dict(color="white", width=1)),
            error_x=dict(type="data", symmetric=False,
                         array=sub["ci_hi"] - sub["coef"], arrayminus=sub["coef"] - sub["ci_lo"],
                         color="rgba(255,255,255,0.5)", thickness=1.5, width=6),
            customdata=sub["p"],
            hovertemplate="%{y}<br>DiD coef: %{x:+.5f}<br>p = %{customdata:.5f}<extra></extra>",
        ))

    fig.add_vline(x=0, line_dash="dash", line_color="rgba(255,255,255,0.5)")
    fig.update_layout(
        title="Control-Group DiD: Treated-vs-Control Effect, Both Windows",
        xaxis_title="DiD coefficient (treated-vs-control gap in change, district FE, cluster-robust SE)",
        yaxis=dict(autorange="reversed"),
        height=480, hovermode="closest", **DARK_LAYOUT,
    )
    fig.write_html(f"{OUT}/control_group_did_effect.html", include_plotlyjs="cdn")
    print("Saved:", f"{OUT}/control_group_did_effect.html")


# ============================================================
# FIGURE 9 — Multi-year trend (2021/2023/2025), both windows, NDBI + Lights
# ============================================================
def build_multiyear_trend():
    my_fy = pd.read_csv(f"{DATA}/border_optics_multiyear_fullyear.csv")
    my_sm = pd.read_csv(f"{DATA}/border_optics_multiyear_summer.csv")
    my_fy_core = my_fy[my_fy["is_core_sample"] == True]
    my_sm_core = my_sm[my_sm["is_core_sample"] == True]
    YEARS = [2021, 2023, 2025]

    fig = go.Figure()
    for outcome, dash, symbol in [("ndbi", "solid", "circle"), ("lights", "dot", "square")]:
        for label, df, color in [("Full-Year", my_fy_core, BLUE), ("Summer-Matched", my_sm_core, ORANGE)]:
            means = [df[f"{outcome}_{yr}"].mean() for yr in YEARS]
            sems = [df[f"{outcome}_{yr}"].std() / np.sqrt(df[f"{outcome}_{yr}"].count()) for yr in YEARS]
            oname = "NDBI" if outcome == "ndbi" else "Night-Lights"
            fig.add_trace(go.Scatter(
                x=YEARS, y=means, mode="lines+markers", name=f"{oname} — {label}",
                line=dict(color=color, width=2.5, dash=dash), marker=dict(size=10, symbol=symbol),
                error_y=dict(type="data", array=sems, color=color, thickness=1.5, width=5),
                hovertemplate=f"{oname} — {label}<br>Year: %{{x}}<br>Mean: %{{y:.4f}}<extra></extra>",
            ))

    fig.update_layout(
        title="Three-Point Trend (2021 / 2023 / 2025), Both Compositing Windows — mean ± SE, core sample (n=251)",
        xaxis=dict(title="Year", tickvals=YEARS),
        yaxis_title="Mean value",
        height=560, hovermode="closest", **{**DARK_LAYOUT, "margin": dict(t=70, b=50, l=70, r=30)},
    )
    fig.write_html(f"{OUT}/multiyear_trend.html", include_plotlyjs="cdn")
    print("Saved:", f"{OUT}/multiyear_trend.html")


# ============================================================
# FIGURE 10 — Buffer-radius sensitivity (250m / 500m / 1km), summer window
# ============================================================
def build_buffer_sensitivity():
    with open(f"{DATA}/border_optics_buffer_sensitivity_summary.json") as f:
        buf = json.load(f)

    as_extracted = {r["buffer_m"]: r["ndbi_wilcoxon_p"] for r in buf["as_extracted"]}
    matched = {r["buffer_m"]: r["wilcoxon_p"] for r in buf["matched_subsample"]}
    buffers = [250, 500, 1000]
    labels = [f"{b}m" for b in buffers]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=labels, y=[max(as_extracted[b], 1e-7) for b in buffers],
        name="As extracted (varying n, archive-timing confounded)", marker_color="#B0B0B0",
        marker_line=dict(color="black", width=1),
        hovertemplate="%{x}<br>p = %{y:.5g}<extra>As extracted</extra>",
    ))
    fig.add_trace(go.Bar(
        x=labels, y=[max(matched[b], 1e-7) for b in buffers],
        name="Matched subsample (n=154, buffer radius isolated)", marker_color=GREEN,
        marker_line=dict(color="black", width=1),
        hovertemplate="%{x}<br>p = %{y:.5g}<extra>Matched subsample</extra>",
    ))
    fig.add_hline(y=0.05, line_color=RED, annotation_text="p = 0.05", annotation_position="top right")
    fig.update_layout(
        title="Buffer-Radius Sensitivity: NDBI Significance, Summer Window",
        xaxis_title="Buffer radius", yaxis_title="NDBI Wilcoxon p-value (log scale)",
        yaxis_type="log", barmode="group",
        height=480, hovermode="x unified", **{**DARK_LAYOUT, "margin": dict(t=70, b=50, l=70, r=30)},
    )
    fig.write_html(f"{OUT}/buffer_sensitivity.html", include_plotlyjs="cdn")
    print("Saved:", f"{OUT}/buffer_sensitivity.html")


if __name__ == "__main__":
    build_did_effect()
    build_multiyear_trend()
    build_buffer_sensitivity()
