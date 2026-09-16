"""
One-command runner for all the pretreatment/footprint combos, so I don't
have to type each one out. If one combo fails it just moves to the next --
each script checkpoints on its own so nothing already done gets redone.

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
