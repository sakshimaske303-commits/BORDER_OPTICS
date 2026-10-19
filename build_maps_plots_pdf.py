"""
puts all the figures + static map renders into one PDF, with a cover page.
dashboard maps stay interactive, this is just the print copy.
"""

import os
from PIL import Image
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

OUT_PATH = "BORDER_OPTICS_Maps_and_Plots.pdf"
BG = (10, 10, 10)
ACCENT = (215, 165, 60)
TEXT = (240, 240, 235)

# Figure numbers follow BO_Research_Paper.md v2.0 (Development Log Entry 49), NOT the PNG
# filename numbers (those are just generation order). Items not in the paper are "Supplementary".
ITEMS = [
    ("outputs/figures/static_map_renders/map_state_overview.png",
     "Figure 1 — Study Area",
     "251 core priority villages, 7 illustrative Himachal Pradesh villages and 721 comparison villages."),
    ("outputs/figures/01_ndbi_change_distribution.png",
     "Figure 2 — NDBI Change per Priority Village",
     "Both compositing windows; labelled outliers start from snow/water values."),
    ("outputs/figures/static_map_renders/map_ndbi_summer.png",
     "Figure 3 — Summer NDBI Change by Village",
     "Interactive version: dashboard → Interactive Maps."),
    ("outputs/figures/08_control_group_did_effect.png",
     "Figure 4 — Priority vs Comparison DiD (NDBI, Night Lights)",
     "95% CI with t (13 df); green band = change from doubling a typical village's buildings."),
    ("outputs/figures/11_triangulation_did.png",
     "Figure 5 — DiD Across Four Satellite Measures",
     "NDBI, Sentinel-1 VV/VH, Dynamic World built probability."),
    ("outputs/figures/12_footprint_validation.png",
     "Figure 6 — Footprint Correlation and Anjaw Case Villages",
     "Case villages shown as percentiles of all villages' change."),
    ("outputs/figures/03_h3_border_distance_vs_lights.png",
     "Figure 7 — Border Distance vs Change, by District",
     "Pooled and within-district Spearman correlations."),
    ("outputs/figures/07_robustness_summary.png",
     "Figure 8 — Treated-Only and Border-Distance Tests",
     "Two-sided tests; within-district H3 shown as hollow markers."),
    ("outputs/figures/09_multiyear_trend.png",
     "Figure 9 — Three-Point Trend (2021 / 2023 / 2025)",
     "2023 composites may be cloud-unmasked (QA60 gap)."),
    ("outputs/figures/02_state_change_vs_budget.png",
     "Figure A1 — State Budget vs Mean NDBI Change",
     "Descriptive only, n = 3 states."),
    ("outputs/figures/04_state_mean_ndbi_change.png",
     "Figure A2 — NDBI Change by State",
     "Medians with 95% bootstrap intervals, and means."),
    ("outputs/figures/05_state_mean_lights_change.png",
     "Figure A3 — Night-Light Change by State",
     "Medians with 95% bootstrap intervals, and means."),
    ("outputs/figures/10_buffer_sensitivity.png",
     "Figure A4 — Buffer Radius Sensitivity",
     "Mean NDBI change with 95% CI at 250 m, 500 m and 1 km (summer)."),
    ("outputs/figures/static_map_renders/map_border_distance.png",
     "Figure A5 — Distance to the Nearest Boundary",
     "Comparative only; Natural Earth cartographic lines."),
    ("outputs/figures/06_lights_change_distribution.png",
     "Supplementary — Night-Light Change Distribution",
     "Summer window."),
    ("outputs/figures/static_map_renders/map_ndbi_fullyear.png",
     "Supplementary — Full-Year NDBI Change by Village",
     "Interactive version: dashboard → Interactive Maps."),
    ("outputs/figures/static_map_renders/map_lights_change.png",
     "Supplementary — Night-Light Change by Village",
     "Interactive version: dashboard → Interactive Maps."),
]

PAGE_W, PAGE_H = letter


def draw_cover(c):
    c.setFillColorRGB(*[v / 255 for v in BG])
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    c.setFillColorRGB(*[v / 255 for v in ACCENT])
    c.setFont("Helvetica-Bold", 26)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 140, "BORDER OPTICS")

    c.setFillColorRGB(*[v / 255 for v in TEXT])
    c.setFont("Helvetica", 15)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 170, "Maps & Plots")
    c.setFont("Helvetica", 10)
    c.drawCentredString(PAGE_W / 2, PAGE_H - 190, "Satellite-Based Verification Framework for India's Vibrant Villages Programme (VVP-I)")

    y = PAGE_H - 250
    c.setFont("Helvetica-Bold", 11)
    c.drawString(72, y, "Contents")
    y -= 22
    c.setFont("Helvetica", 10)
    for i, (_, title, _) in enumerate(ITEMS, start=1):
        c.drawString(84, y, f"{i}.  {title}")
        y -= 17

    c.setFont("Helvetica-Oblique", 8)
    c.setFillColorRGB(*[v / 255 for v in (150, 150, 150)])
    c.drawCentredString(PAGE_W / 2, 50,
        "The five Map pages are static renders for print/offline reference. "
        "Live versions on the dashboard are interactive (pan, zoom, click-to-inspect).")
    c.showPage()


def draw_image_page(c, path, title, caption):
    img = Image.open(path)
    w, h = img.size
    landscape_page = w > h

    page_size = landscape(letter) if landscape_page else letter
    c.setPageSize(page_size)
    pw, ph = page_size

    c.setFillColorRGB(*[v / 255 for v in BG])
    c.rect(0, 0, pw, ph, fill=1, stroke=0)

    margin = 40
    title_h = 50
    caption_h = 40
    avail_w = pw - 2 * margin
    avail_h = ph - title_h - caption_h - 2 * margin

    scale = min(avail_w / w, avail_h / h)
    draw_w, draw_h = w * scale, h * scale
    x = (pw - draw_w) / 2
    y = margin + caption_h

    c.drawImage(path, x, y, width=draw_w, height=draw_h)

    c.setFillColorRGB(*[v / 255 for v in ACCENT])
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(pw / 2, ph - margin - 20, title)

    c.setFillColorRGB(*[v / 255 for v in TEXT])
    c.setFont("Helvetica", 9)
    c.drawCentredString(pw / 2, margin + 18, caption)

    c.showPage()


def main():
    c = canvas.Canvas(OUT_PATH, pagesize=letter)
    draw_cover(c)
    for path, title, caption in ITEMS:
        if not os.path.exists(path):
            print(f"WARNING: missing {path}, skipping")
            continue
        draw_image_page(c, path, title, caption)
    c.save()
    print(f"Saved {OUT_PATH}")


if __name__ == "__main__":
    main()
