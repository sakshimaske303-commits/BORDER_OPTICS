"""One-command runner for every combination the two new Section 7.2/7.5
extraction scripts need, so this doesn't have to be typed out combination by
combination.

This does NOT change how extract_pretreatment_baseline.py or
extract_building_footprints.py work -- they still checkpoint per file and
resume on their own (same as every other extraction script in this study).
This script just calls each of the group/window combinations they need, one
after another, in a single process, so one `python` invocation does
everything instead of six.

If one combination fails partway (a network blip, a Earth Engine rate
limit), this prints the error clearly and moves on to the next combination
rather than stopping the whole run -- because each script's own checkpoint
file means a failed combination can always be re-run on its own afterward
without losing the ones that already succeeded (this is the same
resume-safety property extract_sar_backscatter.py and
extract_dynamicworld_built.py already have; nothing new).

Usage:
    python3 src/acquisition/run_all_new_extractions.py
    python3 src/acquisition/run_all_new_extractions.py --only pretreatment
    python3 src/acquisition/run_all_new_extractions.py --only footprints
"""
import argparse
import sys
import time
import traceback

sys.path.insert(0, "src/acquisition")

PRETREATMENT_COMBOS = [
    ("treated", "full_year"),
    ("treated", "summer"),
    ("control", "full_year"),
    ("control", "summer"),
]
FOOTPRINT_GROUPS = ["treated", "control"]


def run_pretreatment():
    import extract_pretreatment_baseline as mod

    mod.init_ee()
    results = []
    for group, window in PRETREATMENT_COMBOS:
        print("\n" + "=" * 78)
        print(f"PRE-TREATMENT BASELINE: group={group}  window={window}")
        print("=" * 78)
        try:
            mod.extract(group, window)
            results.append((group, window, "OK"))
        except Exception as e:
            print(f"!! FAILED: group={group} window={window}: {e}")
            traceback.print_exc()
            results.append((group, window, f"FAILED: {e}"))
        time.sleep(1)
    return results


def run_footprints():
    import extract_building_footprints as mod

    mod.init_ee()
    results = []
    for group in FOOTPRINT_GROUPS:
        print("\n" + "=" * 78)
        print(f"BUILDING FOOTPRINTS: group={group}")
        print("=" * 78)
        try:
            mod.extract(group)
            results.append((group, "OK"))
        except Exception as e:
            print(f"!! FAILED: group={group}: {e}")
            traceback.print_exc()
            results.append((group, f"FAILED: {e}"))
        time.sleep(1)
    return results


def main():
    parser = argparse.ArgumentParser(description="Run every combination for the new §7.2/§7.5 extractions in one go.")
    parser.add_argument("--only", choices=["pretreatment", "footprints"], default=None,
                         help="Run only one of the two extraction sets. Default: both.")
    args = parser.parse_args()

    all_results = {}
    if args.only in (None, "pretreatment"):
        all_results["pretreatment"] = run_pretreatment()
    if args.only in (None, "footprints"):
        all_results["footprints"] = run_footprints()

    print("\n" + "#" * 78)
    print("SUMMARY")
    print("#" * 78)
    any_failed = False
    for key, results in all_results.items():
        for r in results:
            status = r[-1]
            print(f"  [{key}] {r[:-1]}: {status}")
            if status != "OK":
                any_failed = True

    if any_failed:
        print("\nOne or more combinations failed -- re-run just those specific "
              "group/window combinations directly with extract_pretreatment_baseline.py "
              "or extract_building_footprints.py once you've looked at the error above; "
              "everything that already succeeded is checkpointed and won't be redone.")
    else:
        print("\nAll combinations completed. Next: "
              "python3 src/analysis/pretreatment_placebo_test.py --window full_year (and --window summer), "
              "then python3 src/analysis/building_footprint_validation.py")


if __name__ == "__main__":
    main()
