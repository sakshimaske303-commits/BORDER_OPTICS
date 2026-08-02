#!/usr/bin/env bash
# Regenerates Research_Paper.pdf, Project_Journal.pdf, and Development_Log.pdf
# from their source .md files — these three PDFs are what the dashboard's
# "Full Project Documentation" download buttons on the Home page serve.
#
# Requires pandoc + wkhtmltopdf (both open-source, freely installable).
# Run from the repository root:
#   bash build_docs_pdfs.sh

set -euo pipefail
export LANG=C.utf8 LC_ALL=C.utf8

for doc in "Research_Paper:BORDER OPTICS — Research Paper" \
           "Project_Journal:BORDER OPTICS — Project Journal" \
           "Development_Log:BORDER OPTICS — Development Log"; do
    name="${doc%%:*}"
    title="${doc#*:}"
    echo "Building ${name}.pdf..."
    pandoc "${name}.md" -o "${name}.pdf" \
        --pdf-engine=wkhtmltopdf \
        -V margin-top=20mm -V margin-bottom=20mm -V margin-left=20mm -V margin-right=20mm \
        --metadata title="${title}" \
        --toc
done

echo "Done. Research_Paper.pdf, Project_Journal.pdf, and Development_Log.pdf are up to date."
