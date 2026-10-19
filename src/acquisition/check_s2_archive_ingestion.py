"""
Tests the "Sentinel-2 archive backfill" explanation for the Sikkim summer
dropout (Development Log Entries 21-22; forensic review item B2). NOT YET RUN.

The original summer extraction reported 0 Sentinel-2 scenes (counted BEFORE
cloud masking) for all 31 Sikkim villages in both Jun-Sep 2021 and Jun-Sep
2025; a later Python extraction found ~24-31 scenes per village. If the
backfill explanation is right, most of those scenes should carry an Earth
Engine ingestion time ("system:version", microseconds since epoch) AFTER the
date of the original extraction (late July 2026). If they were ingested
long before, the original zero was a code/asset problem in the earlier
(Code Editor) pipeline, and the paper should say "cause undetermined"
rather than "archive backfill".

run:  python src/acquisition/check_s2_archive_ingestion.py
out:  printed summary + outputs/s2_archive_ingestion_check.csv
"""

import datetime as dt
import os

import ee
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
ORIGINAL_EXTRACTION_DATE = dt.datetime(2026, 7, 28)  # Development Log Entry 5 / file date of the first summer pull
WINDOWS = {"2021": ("2021-06-01", "2021-10-01"), "2025": ("2025-06-01", "2025-10-01")}


def main():
    ee.Initialize(project=os.environ.get("EE_PROJECT"))
    v = pd.read_csv("data/processed/border_optics_master_villages.csv")
    v = v[v.state == "Sikkim"]
    rows = []
    for _, r in v.iterrows():
        buf = ee.Geometry.Point([r.longitude, r.latitude]).buffer(500)
        for label, (s, e) in WINDOWS.items():
            col = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED").filterBounds(buf).filterDate(s, e)
            versions = col.aggregate_array("system:version").getInfo()
            ingested = [dt.datetime(1970, 1, 1) + dt.timedelta(microseconds=int(x)) for x in versions]
            after = sum(d > ORIGINAL_EXTRACTION_DATE for d in ingested)
            rows.append({"village": r.village, "window": label, "n_scenes": len(ingested),
                         "n_ingested_after_original_pull": after,
                         "earliest_ingestion": min(ingested).date() if ingested else None,
                         "latest_ingestion": max(ingested).date() if ingested else None})
    out = pd.DataFrame(rows)
    os.makedirs("outputs", exist_ok=True)
    out.to_csv("outputs/s2_archive_ingestion_check.csv", index=False)
    tot = out.n_scenes.sum()
    late = out.n_ingested_after_original_pull.sum()
    print(out.groupby("window")[["n_scenes", "n_ingested_after_original_pull"]].sum())
    print(f"\n{late}/{tot} scenes ({100 * late / max(tot, 1):.0f}%) were ingested after {ORIGINAL_EXTRACTION_DATE.date()}.")
    print("Mostly after -> backfill explanation supported. Mostly before -> original zero was a pipeline problem.")


if __name__ == "__main__":
    main()
