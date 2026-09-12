import json

import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    villages = pd.read_csv("data/processed/border_optics_master_villages_with_distance.csv")
    full_year = pd.read_csv("data/processed/border_optics_village_results_analyzed.csv")
    summer = pd.read_csv("data/processed/border_optics_village_results_summer_analyzed.csv")

    # full_year's own extraction doesn't carry lat/lon, so it needs the full merge.
    # summer's fresh extraction (post Development Log Entry 22) already carries its
    # own latitude/longitude columns -- merging those in again from villages would
    # collide and get silently renamed to latitude_x/latitude_y by pandas, dropping
    # the plain column names. summer only needs distance_to_border_km from villages.
    merge_cols = ["village_id", "latitude", "longitude", "distance_to_border_km"]
    full_year = full_year.merge(villages[merge_cols], on="village_id", how="left")
    summer = summer.merge(villages[["village_id", "distance_to_border_km"]], on="village_id", how="left")

    return villages, full_year, summer


@st.cache_data
def load_expanded_results():
    """Control-group DiD, multi-year trend, and buffer-sensitivity summaries -
    the three robustness checks that stress-test the summer-matched NDBI
    result against a district-restricted control group, a three-point trend, and a
    buffer-radius sweep (Research Paper Sections 3.7-3.9 / 4.6-4.8)."""
    with open("data/processed/border_optics_did_summary_fullyear.json") as f:
        did_fullyear = json.load(f)
    with open("data/processed/border_optics_did_summary_summer.json") as f:
        did_summer = json.load(f)
    with open("data/processed/border_optics_multiyear_summary_fullyear.json") as f:
        multiyear_fullyear = json.load(f)
    with open("data/processed/border_optics_multiyear_summary_summer.json") as f:
        multiyear_summer = json.load(f)
    with open("data/processed/border_optics_buffer_sensitivity_summary.json") as f:
        buffer_sensitivity = json.load(f)
    with open("outputs/robustness_extended_results.json") as f:
        robustness_extended = json.load(f)

    return {
        "did_fullyear": did_fullyear,
        "did_summer": did_summer,
        "multiyear_fullyear": multiyear_fullyear,
        "multiyear_summer": multiyear_summer,
        "buffer_sensitivity": buffer_sensitivity,
        "robustness_extended": robustness_extended,
    }