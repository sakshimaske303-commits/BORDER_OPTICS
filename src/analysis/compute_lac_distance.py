"""
Distance from every treated and control village to the China boundary only
(the LAC sector of Natural Earth's India boundary lines), alongside the
existing all-borders distance. Added Development Log Entry 49.

Why: H3 is a securitization hypothesis about the China frontier, but
distance_to_border_km is measured to the nearest India boundary of any kind,
so 31 core villages were scored by their distance to Bhutan, Nepal or
Myanmar instead (e.g. Khellong, West Kameng: 34 km from Bhutan).

Integrity check built in: the all-borders distance is recomputed here with
the same nearest-point + geodesic rule as compute_border_distance.py and
must reproduce the committed distance_to_border_km for every village (to
within 1 m) before the China-only column is written.

run:  python src/analysis/compute_lac_distance.py
out:  data/processed/border_optics_lac_distance.csv
"""

import pandas as pd

from border_geometry import distance_to_border_km, load_india_segments, segment_arrays

TREATED_PATH = "data/processed/border_optics_master_villages_with_distance.csv"
CONTROL_PATH = "data/processed/border_optics_control_villages.csv"
OUT_PATH = "data/processed/border_optics_lac_distance.csv"
TOLERANCE_KM = 0.001


def main():
    segments = load_india_segments()
    A_all, B_all, own_all = segment_arrays(segments)
    A_cn, B_cn, own_cn = segment_arrays(segments, country="China")
    print(f"{len(segments)} India boundary segments; "
          f"{sum(s['other_country'] == 'China' for s in segments)} with China")

    rows = []
    for group, path in [("treated", TREATED_PATH), ("control", CONTROL_PATH)]:
        df = pd.read_csv(path)
        worst = 0.0
        for _, r in df.iterrows():
            d_all, country = distance_to_border_km(r.longitude, r.latitude, A_all, B_all, own_all, segments)
            d_cn, _ = distance_to_border_km(r.longitude, r.latitude, A_cn, B_cn, own_cn, segments)
            worst = max(worst, abs(d_all - r.distance_to_border_km))
            rows.append({
                "group": group, "village_id": int(r.village_id), "village": r.village,
                "district": r.district, "state": r.state,
                "distance_to_border_km": r.distance_to_border_km,
                "distance_to_border_km_recomputed": d_all,
                "nearest_border_country_recomputed": country,
                "distance_to_china_km": d_cn,
            })
        print(f"{group}: {len(df)} villages, max |recomputed - committed| = {worst * 1000:.3f} m")
        if worst > TOLERANCE_KM:
            raise SystemExit(f"{group}: recomputed all-borders distance does not reproduce the committed "
                             f"column (max diff {worst:.4f} km) -- not writing China distances.")

    out = pd.DataFrame(rows)
    out.to_csv(OUT_PATH, index=False)
    t = out[out.group == "treated"]
    print(f"\nSaved {OUT_PATH}")
    print("Treated villages whose nearest border is not China:",
          int((t.nearest_border_country_recomputed != "China").sum()))
    print(t.distance_to_china_km.describe().round(1).to_string())


if __name__ == "__main__":
    main()
