#!/usr/bin/env bash
# Regenerates BO_Executive_Summary.pdf, BO_Research_Paper.pdf, and
# BO_Development_Log.pdf from their source .md files, and copies all three
# into static/ — this is where the dashboard's "Full Project Documentation"
# viewer on the Home page reads them from (see app.py / utils/doc_viewer.py).
#
# Requires pandoc + wkhtmltopdf (both open-source, freely installable).
# Run from the repository root:
#   bash build_docs_pdfs.sh

set -euo pipefail
export LANG=C.utf8 LC_ALL=C.utf8

mkdir -p static

for doc in "BO_Executive_Summary:BORDER OPTICS — Executive Summary" \
           "BO_Research_Paper:BORDER OPTICS — Research Paper" \
           "BO_Development_Log:BORDER OPTICS — Development Log"; do
    name="${doc%%:*}"
    title="${doc#*:}"
    echo "Building ${name}.pdf..."
    pandoc "${name}.md" -o "${name}.pdf" \
        --pdf-engine=wkhtmltopdf \
        -V margin-top=20mm -V margin-bottom=20mm -V margin-left=20mm -V margin-right=20mm \
        --metadata title="${title}" \
        --toc
    cp "${name}.pdf" "static/${name}.pdf"
done

echo "Done. BO_Executive_Summary.pdf, BO_Research_Paper.pdf, and BO_Development_Log.pdf are up to date (root + static/)."
