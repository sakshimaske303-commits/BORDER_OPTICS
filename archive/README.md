# Archive

Files moved here are deliberately kept, not deleted. This project's own practice (see `BO_Development_Log.md`) is to keep pre-fix data alongside post-fix data as an audit trail rather than overwrite history — this folder is that same practice applied to repo housekeeping, so a repo browser doesn't mistake an intentional audit trail for clutter, and so the numbered production outputs in `outputs/figures/` and `data/processed/` aren't sitting next to superseded or unused files.

Nothing in `src/`, `pages/`, or `app.py` reads from this folder. Every file here was confirmed unreferenced by any current script before being moved (checked by grep across `src/`, `pages/`, `app.py`, `tests/` on 2026-09-17).

## `data_processed/`

| File | Original path | Why it's here |
|---|---|---|
| `border_optics_control_villages_PRE_ENTRY24_FIX.csv` | `data/processed/` | The 735-village control list before the coordinate-proximity + official-name-list dedup fix (Development Log Entry 24). Superseded first by the 732-village list that fix produced (Entry 25), and later by the current 721-village `border_optics_control_villages.csv` (Entry 37 district-verification fix). Kept because it's the source used to independently reproduce the "20 duplicates / 21 treated villages" count in `BO_Research_Paper.md` §4.6 and §6.10 — see `BO_Development_Log.md` Entries 22-25 for the full account. |
| `border_optics_control_results_summer.OLD_PRE_ENTRY22.csv` | `data/processed/` | The control-group summer extraction before the Entry 22 same-day, complete re-pull. Deliberately renamed rather than overwritten at the time (Entry 22) so the pre/post comparison stayed inspectable. |
| `border_optics_buffer250_summer_PRE_SAMEDAY_BUFFER_CHECK.csv` | `data/processed/` | Buffer-sensitivity sweep (250m radius) before the same-day-extraction re-pull. |
| `border_optics_buffer1000_summer_PRE_SAMEDAY_BUFFER_CHECK.csv` | `data/processed/` | Buffer-sensitivity sweep (1km radius) before the same-day-extraction re-pull. |
| `border_optics_village_results_summer_PRE_SAMEDAY_BUFFER_CHECK.csv` | `data/processed/` | Treated-village summer results before the same-day-extraction re-pull. |

Note: `border_optics_village_results_summer_sclmask_strict.csv` and `..._sclmask_corrected.csv` are **not** archived here — they are live outputs of `src/acquisition/extract_scl_cloud_mask_ndbi.py` and `scl_vs_qa60_comparison.py` still reads them; see `DATA_DICTIONARY.md`.

## `figures/`

| File | Original path | Why it's here |
|---|---|---|
| `img1.png` | `outputs/figures/` | Unreferenced duplicate/earlier draft of the same diagram as `outputs/figures/imgg1.png` (same 1672×941 dimensions). Confirmed no `.py` file loads it. |
| `photo1.png` | `outputs/figures/` | Unreferenced image, confirmed no `.py` file loads it. |

Note: `outputs/figures/imgg1.png` is **not** archived — despite the similar filename, it's the live diagram loaded by `pages/2_Theoretical_Foundations.py`. Don't move or rename it without updating that page's `IMG_PATH`.

## `root/`

| File | Original path | Why it's here |
|---|---|---|
| `border optics maps.pdf` | repo root | An earlier, 6-page draft of what `BORDER_OPTICS_Maps_and_Plots.pdf` (16 pages, current) superseded. Confirmed no `.py` or `.md` file references it by name. The filename's space was also flagged as a hygiene issue independently of its staleness. |

## `superseded_scripts/`

| File | Original path | Why it's here |
|---|---|---|
| `analyze_results_fullyear.py` | `src/analysis/` | Near-duplicate of `analyze_results.py`, differing only in which window's file paths it read/wrote and its print labels — the same window-consistency risk this project has been bitten by before. Consolidated into `src/analysis/analyze_results.py --window {summer,full_year}`, following the same path-dictionary pattern `did_model.py` already used. Verified byte-for-byte identical output (printed stats and saved CSV, `md5sum`-checked) before archiving. |
