
import os
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "processed")

MASTER_PATH = os.path.join(DATA, "border_optics_master_villages_with_distance.csv")
CONTROL_PATH = os.path.join(DATA, "border_optics_control_villages.csv")
SUMMER_ANALYZED_PATH = os.path.join(DATA, "border_optics_village_results_summer_analyzed.csv")
FULLYEAR_ANALYZED_PATH = os.path.join(DATA, "border_optics_village_results_analyzed.csv")
CONTROL_RESULTS_SUMMER_PATH = os.path.join(DATA, "border_optics_control_results_summer.csv")
CONTROL_RESULTS_FULLYEAR_PATH = os.path.join(DATA, "border_optics_control_results.csv")
DID_PANEL_SUMMER_PATH = os.path.join(DATA, "border_optics_did_panel_summer.csv")
DID_PANEL_FULLYEAR_PATH = os.path.join(DATA, "border_optics_did_panel_fullyear.csv")

EXPECTED_CORE_TREATED = 251
EXPECTED_TOTAL_TREATED = 258
EXPECTED_CONTROL = 732  # was 735 pre-Entry-24-fix; dropped to 732 once the 50m coordinate-proximity dedup + full official-name exclusion removed the contaminated rows (Entry 25)
EXPECTED_DISTRICTS = 14
EXPECTED_STATE_COUNTS = {
    "Arunachal Pradesh": 186,
    "Sikkim": 31,
    "Uttarakhand": 34,
    "Himachal Pradesh": 0,  # illustrative only, not core sample
}


def _round_coords(df, ndigits=6):
    return list(zip(df["latitude"].round(ndigits), df["longitude"].round(ndigits)))


def test_core_sample_size():
    df = pd.read_csv(MASTER_PATH)
    core = df[df["is_core_sample"] == True]
    assert len(core) == EXPECTED_CORE_TREATED, (
        f"Expected {EXPECTED_CORE_TREATED} core-sample treated villages, found {len(core)}. "
        f"If this changed on purpose (a re-extraction, a new state added), update this "
        f"constant AND note the change in the Development Log — do not just silently pass."
    )
    assert len(df) == EXPECTED_TOTAL_TREATED, (
        f"Expected {EXPECTED_TOTAL_TREATED} total geocoded treated villages, found {len(df)}."
    )


def test_state_composition():
    df = pd.read_csv(MASTER_PATH)
    core = df[df["is_core_sample"] == True]
    counts = core.groupby("state").size().to_dict()
    for state, expected in EXPECTED_STATE_COUNTS.items():
        actual = counts.get(state, 0)
        assert actual == expected, (
            f"{state}: expected {expected} core-sample villages, found {actual}."
        )


def test_control_group_size():
    df = pd.read_csv(CONTROL_PATH)
    assert len(df) == EXPECTED_CONTROL, (
        f"Expected {EXPECTED_CONTROL} control villages, found {len(df)}. A count drift here "
        f"usually means select_control_villages.py was rerun against a changed treated list "
        f"or boundary source without regenerating every downstream file."
    )


def test_control_group_no_duplicate_coordinates():
    df = pd.read_csv(CONTROL_PATH)
    coords = _round_coords(df)
    n_unique = len(set(coords))
    assert n_unique == len(coords), (
        f"Found {len(coords) - n_unique} duplicate coordinate(s) in the control-village list "
        f"— this is exactly the cross-district matching bug Development Log Entry 22 found and "
        f"fixed (106 duplicate-coordinate rows in an earlier version). Re-run "
        f"select_control_villages.py's dedup logic rather than hand-editing the CSV."
    )


def test_no_treated_control_coordinate_overlap():
    """RESOLVED as of Development Log Entry 25. Originally found in Entry 23: 20 control
    villages sat at the exact same coordinates as 21 treated villages -- the same physical
    settlement entered twice under a different name spelling or OSM-tag script (e.g.
    Sibia/Sebia, Gunji/गूंजी, Chate/赛探). That was a direct consequence of the exclusion
    filter relying on exact ASCII name matching rather than coordinate proximity. Entry 24
    fixed select_control_villages.py to add a 50m coordinate-proximity dedup on top of the
    name-based exclusion; Entry 25 confirms that on the regenerated 732-village control
    list, the overlap count is genuinely 0 -- ceiling tightened from 20 to 0. If this ever
    fails again, something new broke; do not loosen this back up without a Development Log
    entry explaining why.
    """
    KNOWN_OVERLAP_CEILING = 0

    treated = pd.read_csv(MASTER_PATH)
    control = pd.read_csv(CONTROL_PATH)
    treated_coords = set(_round_coords(treated))
    control_coords = set(_round_coords(control))
    overlap = treated_coords & control_coords
    assert len(overlap) <= KNOWN_OVERLAP_CEILING, (
        f"{len(overlap)} coordinate(s) appear in BOTH the treated and control village lists: "
        f"{sorted(overlap)[:5]}{'...' if len(overlap) > 5 else ''} -- more than the "
        f"{KNOWN_OVERLAP_CEILING} known and documented in Development Log Entry 23. A village "
        f"cannot be its own counterfactual — investigate before trusting any DiD result built "
        f"on this data."
    )


def test_village_ids_unique():
    for path, label in [(MASTER_PATH, "treated master"), (CONTROL_PATH, "control")]:
        df = pd.read_csv(path)
        n_unique = df["village_id"].nunique()
        assert n_unique == len(df), (
            f"{label} village_id column has {len(df) - n_unique} duplicate value(s). "
            f"village_id is the join key used throughout this pipeline — a duplicate here "
            f"silently corrupts any merge on it."
        )


def test_control_name_not_official_priority_village():
    """RESOLVED as of Development Log Entry 25. Originally found in Entry 23: the
    control-list exclusion filter only checked candidate names against the 251
    SUCCESSFULLY GEOCODED treated village names, not the full official priority-village
    universe recorded in data/raw/*_vvp_villages.csv -- letting 3 ungeocoded-but-official
    VVP priority villages (all Arunachal Pradesh) leak into the control group. Entry 24
    fixed select_control_villages.py to exclude against the full official name list, not
    just the geocoded subset; Entry 25 confirms that on the regenerated 732-village
    control list, this match count is genuinely 0 -- ceiling tightened from 3 to 0. If
    this ever fails again, something new broke; do not loosen this back up without a
    Development Log entry explaining why.
    """
    KNOWN_CONTAMINATION_CEILING = 0

    raw_files = {
        "Arunachal Pradesh": os.path.join(ROOT, "data", "raw", "arunachal_pradesh_vvp_villages.csv"),
        "Sikkim": os.path.join(ROOT, "data", "raw", "sikkim_vvp_villages.csv"),
        "Uttarakhand": os.path.join(ROOT, "data", "raw", "uttarakhand_vvp_villages.csv"),
    }
    if not all(os.path.exists(p) for p in raw_files.values()):
        print("  SKIPPED test_control_name_not_official_priority_village: raw village-list files not found")
        return

    import unicodedata

    def normalize(name):
        name = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode()
        return " ".join(name.lower().split())

    master = pd.read_csv(MASTER_PATH)
    master_core = master[master["is_core_sample"] == True]
    geocoded_by_state = master_core.groupby("state")["village"].apply(lambda s: set(normalize(n) for n in s))

    control = pd.read_csv(CONTROL_PATH)
    control["_norm"] = control["village"].apply(normalize)

    total_matches = 0
    for state, path in raw_files.items():
        official = set(normalize(n) for n in pd.read_csv(path)["Habitation"])
        ungeocoded_official = official - geocoded_by_state.get(state, set())
        matches = control[(control["state"] == state) & (control["_norm"].isin(ungeocoded_official))]
        total_matches += len(matches)

    assert total_matches <= KNOWN_CONTAMINATION_CEILING, (
        f"Found {total_matches} control villages matching an official-but-ungeocoded VVP "
        f"priority-village name — more than the {KNOWN_CONTAMINATION_CEILING} known and "
        f"documented in Development Log Entry 23. Investigate before trusting the H4 DiD result."
    )


def test_ndbi_values_in_valid_range():
    for path, label in [(SUMMER_ANALYZED_PATH, "treated summer"), (FULLYEAR_ANALYZED_PATH, "treated full-year")]:
        df = pd.read_csv(path)
        for col in ["ndbi_before", "ndbi_after"]:
            valid = df[col].dropna()
            out_of_range = valid[(valid < -1) | (valid > 1)]
            assert out_of_range.empty, (
                f"{label} {col}: {len(out_of_range)} value(s) outside NDBI's valid [-1, 1] range."
            )


def test_image_counts_non_negative():
    for path, label in [
        (SUMMER_ANALYZED_PATH, "treated summer"),
        (CONTROL_RESULTS_SUMMER_PATH, "control summer"),
        (CONTROL_RESULTS_FULLYEAR_PATH, "control full-year"),
    ]:
        if not os.path.exists(path):
            print(f"  SKIPPED test_image_counts_non_negative for {label}: file not found")
            continue
        df = pd.read_csv(path)
        count_cols = [c for c in df.columns if c.endswith("_image_count")]
        for col in count_cols:
            valid = df[col].dropna()
            negative = valid[valid < 0]
            assert negative.empty, f"{label} {col}: {len(negative)} negative image count(s)."


def test_did_panel_row_count():
    for path, label, n_treated, n_control in [
        (DID_PANEL_SUMMER_PATH, "summer", EXPECTED_CORE_TREATED, EXPECTED_CONTROL),
        (DID_PANEL_FULLYEAR_PATH, "full-year", EXPECTED_CORE_TREATED, EXPECTED_CONTROL),
    ]:
        df = pd.read_csv(path)
        expected_rows = (n_treated + n_control) * 2  # one row per village per period (before/after)
        assert len(df) == expected_rows, (
            f"{label} DiD panel: expected {expected_rows} rows ({n_treated} treated + "
            f"{n_control} control, x2 periods), found {len(df)}."
        )


def test_did_panel_no_duplicate_village_period_rows():
    for path, label in [(DID_PANEL_SUMMER_PATH, "summer"), (DID_PANEL_FULLYEAR_PATH, "full-year")]:
        df = pd.read_csv(path)
        dupes = df.duplicated(subset=["village_id", "treatment", "post"], keep=False)
        # village_id is only unique WITHIN treated or WITHIN control (both start at 1), so
        # also key on treatment to avoid a false positive between e.g. treated village_id=1
        # and control village_id=1.
        assert dupes.sum() == 0, (
            f"{label} DiD panel has {dupes.sum()} duplicated (village_id, treatment, post) row(s)."
        )


def test_district_cluster_count():
    treated = pd.read_csv(MASTER_PATH)
    core = treated[treated["is_core_sample"] == True]
    n_districts = core["district"].nunique()
    assert n_districts == EXPECTED_DISTRICTS, (
        f"Expected {EXPECTED_DISTRICTS} treated-village districts (the cluster count every "
        f"cluster-robust SE and leave-one-district-out check in this study assumes), found "
        f"{n_districts}."
    )


if __name__ == "__main__":
    tests = [
        test_core_sample_size,
        test_state_composition,
        test_control_group_size,
        test_control_group_no_duplicate_coordinates,
        test_no_treated_control_coordinate_overlap,
        test_village_ids_unique,
        test_control_name_not_official_priority_village,
        test_ndbi_values_in_valid_range,
        test_image_counts_non_negative,
        test_did_panel_row_count,
        test_did_panel_no_duplicate_village_period_rows,
        test_district_cluster_count,
    ]
    n_pass, n_fail = 0, 0
    for t in tests:
        try:
            t()
            print(f"PASS: {t.__name__}")
            n_pass += 1
        except AssertionError as e:
            print(f"FAIL: {t.__name__}\n      {e}")
            n_fail += 1
        except FileNotFoundError as e:
            print(f"SKIP: {t.__name__} (file not found: {e})")

    print(f"\n{n_pass} passed, {n_fail} failed")
    sys.exit(1 if n_fail else 0)
