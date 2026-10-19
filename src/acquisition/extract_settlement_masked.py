"""
Settlement-targeted outcomes (Development Log Entry 49 -- fix A1 of the
forensic review). NOT YET RUN: needs a live Earth Engine session.

Why: the original outcome is the mean NDBI over a 500 m circle (78.5 ha),
while the median village's buildings cover ~0.33% of that circle. Doubling a
village's buildings would move that mean by only ~0.002 NDBI -- about a
seventh of the DiD's minimum detectable effect
(outputs/measurement_sensitivity_results.json). This script measures where
the buildings actually are.

For each village (treated core + control, same 500 m buffer centre) and
period it records:

  zone_area_m2      area of the "settlement zone": Google Open Buildings v3
                    footprints (confidence >= 0.70) inside the 500 m buffer,
                    each dilated by ZONE_DILATION_M and dissolved. Null if the
                    buffer contains no footprint (flag for geocode QA).
  ndbi_zone         mean NDBI inside the settlement zone, Sentinel-2 SR
                    Harmonized median composite masked with Cloud Score+
                    (cs_cdf >= 0.60, consistent across all years incl. the
                    2022-24 QA60 gap) and with SCL snow/ice (class 11) removed.
  dw_built_zone     mean Dynamic World "built" probability inside the zone.
  dw_built_area_m2  area of the whole 500 m buffer whose Dynamic World modal
                    label for the period is "built" (class 6) -- counts NEW
                    built pixels outside today's footprints too.
  viirs_cf          VIIRS DNB monthly avg_rad, months with cf_cvg = 0 (no
                    cloud-free observation) masked out before averaging,
                    mean over the 500 m buffer.
  *_n               image counts (after masking for S2; months for VIIRS)

Periods: 2019 (placebo), 2021 (baseline), 2025, and for the summer window
2026 (Jun-Sep 2026, complete as of October 2026) to lengthen exposure.

Caveat to state in the paper: Open Buildings v3 is a single recent snapshot,
so the zone is defined by today's footprints for every year. Buildings that
existed in 2021 but were demolished are outside its scope, and new
construction more than ZONE_DILATION_M from an existing footprint is only
captured by dw_built_area_m2.

run (each ~1-2 h; resumable; one call per group x window):
  python src/acquisition/extract_settlement_masked.py --group treated --window summer
  python src/acquisition/extract_settlement_masked.py --group control --window summer
  python src/acquisition/extract_settlement_masked.py --group treated --window full_year
  python src/acquisition/extract_settlement_masked.py --group control --window full_year
then:
  python src/analysis/settlement_masked_did.py
"""

import argparse
import os
import time

import ee
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

BUFFER_RADIUS_M = 500
ZONE_DILATION_M = 25
OB_MIN_CONFIDENCE = 0.70
CS_THRESHOLD = 0.60

S2 = "COPERNICUS/S2_SR_HARMONIZED"
CSPLUS = "GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED"
DW = "GOOGLE/DYNAMICWORLD/V1"
VIIRS = "NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG"
OPEN_BUILDINGS = "GOOGLE/Research/open-buildings/v3/polygons"

VILLAGE_PATHS = {
    "treated": "data/processed/border_optics_master_villages.csv",
    "control": "data/processed/border_optics_control_villages.csv",
}
PERIODS = {
    "full_year": {y: (f"{y}-01-01", f"{y + 1}-01-01") for y in (2019, 2021, 2025)},
    "summer": {y: (f"{y}-06-01", f"{y}-10-01") for y in (2019, 2021, 2025, 2026)},
}
METRICS = ["ndbi_zone", "ndbi_n", "dw_built_zone", "dw_built_area_m2", "dw_n", "viirs_cf", "viirs_n"]


def out_path(group, window):
    return f"data/processed/border_optics_{group}_settlement_masked_{window}.csv"


def init_ee():
    project = os.environ.get("EE_PROJECT")
    try:
        ee.Initialize(project=project)
    except Exception:
        ee.Authenticate()
        ee.Initialize(project=project)


def settlement_zone(buffer_geom):
    fp = (ee.FeatureCollection(OPEN_BUILDINGS)
          .filterBounds(buffer_geom)
          .filter(ee.Filter.gte("confidence", OB_MIN_CONFIDENCE)))
    n = fp.size().getInfo()
    if n == 0:
        return None, 0
    zone = (fp.map(lambda f: f.buffer(ZONE_DILATION_M, 1))
            .union(1)
            .geometry()
            .intersection(buffer_geom, 1))
    return zone, n


def s2_ndbi(zone, start, end):
    s2 = ee.ImageCollection(S2).filterBounds(zone).filterDate(start, end)
    cs = ee.ImageCollection(CSPLUS).filterBounds(zone).filterDate(start, end)
    linked = s2.linkCollection(cs, ["cs_cdf"])

    def mask(img):
        clear = img.select("cs_cdf").gte(CS_THRESHOLD)
        not_snow = img.select("SCL").neq(11)
        return img.updateMask(clear.And(not_snow))

    col = linked.map(mask)
    n = col.size().getInfo()
    if n == 0:
        return None, 0
    ndbi = col.median().normalizedDifference(["B11", "B8"])
    val = ndbi.reduceRegion(ee.Reducer.mean(), zone, 10, maxPixels=1e9).getInfo()
    return list(val.values())[0] if val else None, n


def dynamic_world(zone, buffer_geom, start, end):
    col = ee.ImageCollection(DW).filterBounds(buffer_geom).filterDate(start, end)
    n = col.size().getInfo()
    if n == 0:
        return None, None, 0
    built_prob = col.select("built").median()
    built_label = col.select("label").mode().eq(6)
    prob = (built_prob.reduceRegion(ee.Reducer.mean(), zone, 10, maxPixels=1e9).get("built").getInfo()
            if zone is not None else None)
    area = (built_label.multiply(ee.Image.pixelArea())
            .reduceRegion(ee.Reducer.sum(), buffer_geom, 10, maxPixels=1e9)
            .get("label").getInfo())
    return prob, area, n


def viirs_cloud_filtered(buffer_geom, start, end):
    col = ee.ImageCollection(VIIRS).filterBounds(buffer_geom).filterDate(start, end)
    n = col.size().getInfo()
    if n == 0:
        return None, 0
    masked = col.map(lambda img: img.select("avg_rad").updateMask(img.select("cf_cvg").gt(0)))
    val = masked.mean().reduceRegion(ee.Reducer.mean(), buffer_geom, 500, maxPixels=1e9).get("avg_rad").getInfo()
    return val, n


def extract(group, window, checkpoint_every=10):
    path = out_path(group, window)
    villages = pd.read_csv(VILLAGE_PATHS[group])
    if group == "treated":
        villages = villages[villages["is_core_sample"] == True].reset_index(drop=True)
    cols = ["zone_area_m2", "n_footprints"] + [f"{m}_{y}" for y in PERIODS[window] for m in METRICS]
    for c in cols:
        villages[c] = None
    if os.path.exists(path):
        done = pd.read_csv(path)
        key = lambda df: list(zip(df["latitude"].round(6), df["longitude"].round(6)))
        if set(key(done)) == set(key(villages)):
            villages = done
            print(f"Resuming from {path}")
        else:
            print(f"{path} does not match the current village list -- starting fresh.")

    for i, row in villages.iterrows():
        if pd.notna(row.get(f"dw_n_{max(PERIODS[window])}")):
            continue
        pt = ee.Geometry.Point([row["longitude"], row["latitude"]])
        buf = pt.buffer(BUFFER_RADIUS_M)
        zone, n_fp = settlement_zone(buf)
        villages.at[i, "n_footprints"] = n_fp
        villages.at[i, "zone_area_m2"] = zone.area(1).getInfo() if zone is not None else None
        for year, (start, end) in PERIODS[window].items():
            ndbi, n_s2 = s2_ndbi(zone, start, end) if zone is not None else (None, 0)
            prob, area, n_dw = dynamic_world(zone, buf, start, end)
            lights, n_v = viirs_cloud_filtered(buf, start, end)
            for m, v in zip(METRICS, [ndbi, n_s2, prob, area, n_dw, lights, n_v]):
                villages.at[i, f"{m}_{year}"] = v
        if (i + 1) % checkpoint_every == 0:
            villages.to_csv(path, index=False)
            print(f"  {i + 1}/{len(villages)} villages")
        time.sleep(0.2)

    villages.to_csv(path, index=False)
    print(f"Done: {path}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Settlement-masked NDBI / Dynamic World / cloud-filtered VIIRS (Entry 49).")
    p.add_argument("--group", choices=["treated", "control"], required=True)
    p.add_argument("--window", choices=["full_year", "summer"], required=True)
    a = p.parse_args()
    init_ee()
    extract(a.group, a.window)
