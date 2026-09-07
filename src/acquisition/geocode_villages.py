"""Village geocoding pipeline v4: skips Forest Block entries, falls back to
a simplified query if the full query finds nothing, and distinguishes
real not-in-OSM misses from network failures so re-runs only retry the
failures.
"""

import os
import time
import requests
import pandas as pd

STATE_FILES = {
    "Arunachal Pradesh": "data/raw/arunachal_pradesh_vvp_villages.csv",
    "Sikkim": "data/raw/sikkim_vvp_villages.csv",
    "Uttarakhand": "data/raw/uttarakhand_vvp_villages.csv",
    "Himachal Pradesh": "data/raw/himachal_pradesh_vvp_villages.csv",
}

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
HEADERS = {"User-Agent": "border_optics_research_sakshi_maske (contact: sakshimaske303@gmail.com)"}

REQUEST_TIMEOUT = 20
MAX_RETRIES = 5
RETRY_WAIT_SECONDS = 8
MIN_DELAY_SECONDS = 1.5

STATUS_MATCHED = "matched"
STATUS_MATCHED_FALLBACK = "matched (fallback query, no block)"
STATUS_MATCHED_UNVERIFIED_STATE = "matched — WARNING: Nominatim result's state doesn't match expected state, verify manually"
STATUS_EXCLUDED_FOREST = "EXCLUDED — forest block, not an inhabited settlement"
STATUS_NO_MATCH_FINAL = "NO MATCH — not in OSM (tried full + simplified query)"
STATUS_FAILED_NETWORK = "FAILED AFTER RETRIES — network/timeout issue, retry later"


def is_forest_block(habitation):
    return "forest block" in str(habitation).lower()


def _normalize_state(name):
    return " ".join(str(name).lower().split())


def geocode_query(query, expected_state):
    """Returns (lat, lon, ok, network_failed, state_verified).

    Used to blindly accept whatever Nominatim's top hit (limit=1) was, with
    no check that it was even in the right state — a village name that
    exists in more than one state (not rare among small habitations) could
    silently geocode to the wrong one with nothing to catch it. This pulls a
    few candidates with addressdetails and prefers the first whose returned
    address.state matches expected_state; if none match, it still returns
    the top hit (better than nothing) but flags state_verified=False so the
    caller can mark the row for manual review instead of treating it as a
    clean match.
    """
    params = {"q": query, "format": "json", "limit": 5, "addressdetails": 1}
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(NOMINATIM_URL, params=params, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            if not data:
                return None, None, False, False, False  # genuinely no result, not a network issue

            expected_norm = _normalize_state(expected_state)
            for candidate in data:
                candidate_state = candidate.get("address", {}).get("state", "")
                if _normalize_state(candidate_state) == expected_norm:
                    return float(candidate["lat"]), float(candidate["lon"]), True, False, True

            # No candidate's state matched — fall back to the top hit but flag it unverified
            top = data[0]
            return float(top["lat"]), float(top["lon"]), True, False, False
        except requests.exceptions.RequestException as e:
            print(f"    attempt {attempt}/{MAX_RETRIES} failed for '{query}': {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_WAIT_SECONDS)
    return None, None, False, True, False  # exhausted retries due to network/timeout


def build_query(row, state, use_block=True):
    parts = [str(row.get("Habitation", "")).strip()]
    if use_block and "Block" in row and pd.notna(row["Block"]) and "unresolved" not in str(row["Block"]).lower():
        parts.append(str(row["Block"]).strip())
    if "District" in row and pd.notna(row["District"]):
        parts.append(str(row["District"]).strip())
    parts.append(state)
    parts.append("India")
    return ", ".join([p for p in parts if p])


def process_row(row, state):
    habitation = row.get("Habitation", "")

    if is_forest_block(habitation):
        return None, None, STATUS_EXCLUDED_FOREST, build_query(row, state)

    query_full = build_query(row, state, use_block=True)
    lat, lon, ok, net_failed, state_verified = geocode_query(query_full, state)
    if ok:
        return lat, lon, (STATUS_MATCHED if state_verified else STATUS_MATCHED_UNVERIFIED_STATE), query_full
    if net_failed:
        return None, None, STATUS_FAILED_NETWORK, query_full

    time.sleep(MIN_DELAY_SECONDS)

    query_simple = build_query(row, state, use_block=False)
    if query_simple != query_full:
        lat, lon, ok, net_failed, state_verified = geocode_query(query_simple, state)
        if ok:
            return lat, lon, (STATUS_MATCHED_FALLBACK if state_verified else STATUS_MATCHED_UNVERIFIED_STATE), query_simple
        if net_failed:
            return None, None, STATUS_FAILED_NETWORK, query_simple

    return None, None, STATUS_NO_MATCH_FINAL, query_simple


def geocode_state(state, filepath):
    print(f"\n--- Geocoding {state} ---")
    df = pd.read_csv(filepath)

    out_path = f"data/processed/{state.lower().replace(' ', '_')}_geocoded.csv"
    os.makedirs("data/processed", exist_ok=True)

    terminal_statuses = {
    STATUS_MATCHED, STATUS_MATCHED_FALLBACK, STATUS_MATCHED_UNVERIFIED_STATE,
    STATUS_EXCLUDED_FOREST, STATUS_NO_MATCH_FINAL,
    "matched via Bhuvan (district-verified)",
    "NO MATCH — Bhuvan also failed or district mismatch",
}

    if os.path.exists(out_path):
        existing = pd.read_csv(out_path)
        if len(existing) == len(df) and "geocode_status" in existing.columns:
            done_mask = existing["geocode_status"].isin(terminal_statuses)
            print(f"  Found existing progress file: {done_mask.sum()}/{len(df)} rows already finalized.")
            df = existing
        else:
            df["geocode_query_used"] = None
            df["latitude"] = None
            df["longitude"] = None
            df["geocode_status"] = None
    else:
        df["geocode_query_used"] = None
        df["latitude"] = None
        df["longitude"] = None
        df["geocode_status"] = None

    for i, row in df.iterrows():
        status = row.get("geocode_status")
        if pd.notna(status) and status in terminal_statuses:
            continue

        lat, lon, new_status, query_used = process_row(row, state)

        df.at[i, "geocode_query_used"] = query_used
        df.at[i, "latitude"] = lat
        df.at[i, "longitude"] = lon
        df.at[i, "geocode_status"] = new_status

        time.sleep(MIN_DELAY_SECONDS)

        if (i + 1) % 10 == 0:
            df.to_csv(out_path, index=False)
            matched_so_far = df["geocode_status"].isin([STATUS_MATCHED, STATUS_MATCHED_FALLBACK]).sum()
            print(f"  {i + 1}/{len(df)} processed... ({matched_so_far} matched so far)")

    df.to_csv(out_path, index=False)
    matched = df["geocode_status"].isin([STATUS_MATCHED, STATUS_MATCHED_FALLBACK]).sum()
    unverified = (df["geocode_status"] == STATUS_MATCHED_UNVERIFIED_STATE).sum()
    excluded = (df["geocode_status"] == STATUS_EXCLUDED_FOREST).sum()
    no_match = (df["geocode_status"] == STATUS_NO_MATCH_FINAL).sum()
    failed = (df["geocode_status"] == STATUS_FAILED_NETWORK).sum()
    print(f"  Done: {matched} matched, {unverified} matched but state-unverified (check these), "
          f"{excluded} excluded (forest block), {no_match} not in OSM, {failed} network-failed (retry next run). "
          f"Saved to {out_path}")
    return df


if __name__ == "__main__":
    all_results = {}
    for state, path in STATE_FILES.items():
        all_results[state] = geocode_state(state, path)

    print("\n=== SUMMARY ===")
    for state, df in all_results.items():
        matched = df["geocode_status"].isin([STATUS_MATCHED, STATUS_MATCHED_FALLBACK]).sum()
        unverified = (df["geocode_status"] == STATUS_MATCHED_UNVERIFIED_STATE).sum()
        print(f"{state}: {matched}/{len(df)} geocoded, {unverified} state-unverified (manual check recommended)")
    print("\nRun the script again to retry any 'FAILED AFTER RETRIES' rows (network issues).")
    print("Rows marked 'NO MATCH — not in OSM' or 'EXCLUDED — forest block' are final and won't be retried.")
    print("Rows marked state-unverified matched SOMETHING in Nominatim, but no candidate's returned "
          "state matched the expected state — worth a manual look before trusting the coordinates.")