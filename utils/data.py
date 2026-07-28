import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    villages = pd.read_csv("data/processed/border_optics_master_villages_with_distance.csv")
    full_year = pd.read_csv("data/processed/border_optics_village_results_analyzed.csv")
    summer = pd.read_csv("data/processed/border_optics_village_results_summer_analyzed.csv")

    merge_cols = ["village_id", "latitude", "longitude", "distance_to_border_km"]
    full_year = full_year.merge(villages[merge_cols], on="village_id", how="left")
    summer = summer.merge(villages[merge_cols], on="village_id", how="left")

    return villages, full_year, summer