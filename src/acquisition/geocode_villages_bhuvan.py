"""
BORDER OPTICS — Village Geocoding Pipeline, Phase 2 (Bhuvan fallback)
Retries villages still unmatched after the OSM/Nominatim pass, using
Bhuvan's (ISRO) Village Geocoding API. Since this API does NOT filter
by state/district (a same-named village in another state can be
returned instead), every result is validated against the expected
district before being accepted — this avoids silently contaminating
the dataset with a wrong-state match.

NOTE: Bhuvan tokens expire in ~1 day. If you see repeated failures,
regenerate a token from https://bhuvan-app1.nrsc.gov.in/api/ and
set it as the BHUVAN_TOKEN environment variable (see .env.example).
"""

import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

BHUVAN_TOKEN = os.environ.get("BHUVAN_TOKEN")
if not BHUVAN_TOKEN:
    raise RuntimeError(
        "BHUVAN_TOKEN environment variable is not set. Create a .env file "
        "(see .env.example) with BHUVAN_TOKEN=<your token>, or export it "
        "in your shell before running this script."
    )

STATE_FILES = {
    "Arunachal Pradesh": "data/processed/arunachal_pradesh_geocoded.csv",
    "Sikkim": "data/processed/sikkim_geocoded.csv",
    "Uttarakhand": "data/processed/uttarakhand_geocoded.csv",
    "Himachal Pradesh": "data/processed/himachal_pradesh_geocoded.csv",
}

BHUVAN_URL = "https://bhuvan-app1.nrsc.gov.in/api/api_proximity/curl_village_geocode.php"
REQUEST_TIMEOUT = 20
MAX_RETRIES = 3
RETRY_WAIT_SECONDS = 5
MIN_DELAY_SECONDS = 1.0

STATUS_MATCHED_BHUVAN = "matched via Bhuvan (district-verified)"
STATUS_BHUVAN_NO_MATCH = "NO MATCH — Bhuvan also failed or district mismatch"

RETRY_STATUSES = {
    "NO MATCH — not in OSM (tried full + simplified query)",
    "NO MATCH — Bhuvan also failed or district mismatch",
}


def district_matches(returned_dist, expected_dist):
    if not returned_dist or not expected_dist:
        return False
    r = str(returned_dist).strip().lower()
    e = str(expected_dist).strip().lower()
    return r in e or e in r


def bhuvan_lookup(village_name):
    params = {"village": village_name, "token": BHUVAN_TOKEN}
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(BHUVAN_URL, params=params, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, list) and data:
                return data
            return []  # false / no result
        except requests.exceptions.RequestException as e:
            print(f"    attempt {attempt}/{MAX_RETRIES} failed for '{village_name}': {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_WAIT_SECONDS)
    return None  # network failure after retries


def process_state(state, filepath):
    print(f"\n--- Bhuvan fallback pass: {state} ---")
    df = pd.read_csv(filepath)

    if "bhuvan_vid" not in df.columns:
     df["bhuvan_vid"] = pd.Series([None] * len(df), dtype="object")
    else:
     df["bhuvan_vid"] = df["bhuvan_vid"].astype(object)

    if "bhuvan_population" not in df.columns:
     df["bhuvan_population"] = pd.Series([None] * len(df), dtype="object")
    else:
     df["bhuvan_population"] = df["bhuvan_population"].astype(object)

    retried, newly_matched = 0, 0

    for i, row in df.iterrows():
        status = row.get("geocode_status")
        if status not in RETRY_STATUSES:
            continue

        retried += 1
        habitation = str(row.get("Habitation", "")).strip()
        expected_district = row.get("District", "")

        results = bhuvan_lookup(habitation)
        time.sleep(MIN_DELAY_SECONDS)

        if results is None:
            # network failure — leave status as-is, retryable on a future run
            continue

        accepted = None
        for candidate in results:
            if district_matches(candidate.get("dist_name"), expected_district):
                accepted = candidate
                break

        if accepted:
            df.at[i, "latitude"] = float(accepted["latitude"])
            df.at[i, "longitude"] = float(accepted["longitude"])
            df.at[i, "geocode_status"] = STATUS_MATCHED_BHUVAN
            df.at[i, "bhuvan_vid"] = accepted.get("vid")
            df.at[i, "bhuvan_population"] = accepted.get("tot_p")
            newly_matched += 1
            print(f"    MATCHED: {habitation} -> {accepted['dist_name']}, {accepted['state_name']}")
        else:
            df.at[i, "geocode_status"] = STATUS_BHUVAN_NO_MATCH
            if results:
                found_in = ", ".join(f"{c.get('dist_name')}/{c.get('state_name')}" for c in results)
                print(f"    DISTRICT MISMATCH (discarded): {habitation} — Bhuvan only found it in: {found_in}")
            else:
                print(f"    NOT FOUND: {habitation}")

    df.to_csv(filepath, index=False)
    print(f"  Retried {retried} villages, newly matched {newly_matched}. Updated {filepath}")


if __name__ == "__main__":
    for state, path in STATE_FILES.items():
        process_state(state, path)

    print("\n=== FINAL SUMMARY (after Bhuvan fallback) ===")
    matched_statuses = {"matched", "matched (fallback query, no block)", STATUS_MATCHED_BHUVAN}
    for state, path in STATE_FILES.items():
        df = pd.read_csv(path)
        matched = df["geocode_status"].isin(matched_statuses).sum()
        print(f"{state}: {matched}/{len(df)} geocoded")