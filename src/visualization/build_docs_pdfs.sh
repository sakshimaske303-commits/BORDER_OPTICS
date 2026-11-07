#!/usr/bin/env bash
# Regenerates docs/BO_Executive_Summary.pdf, docs/BO_Research_Paper.pdf and
# docs/BO_Development_Log.pdf from their Markdown sources in docs/, and copies
# all three into static/, where the dashboard's "Full Project Documentation"
# viewer reads them (see app.py / utils/doc_viewer.py).
#
# Requires pandoc + wkhtmltopdf (both open-source, freely installable).
# Run from the repository root:
#   bash src/visualization/build_docs_pdfs.sh

set -euo pipefail
export LANG=C.utf8 LC_ALL=C.utf8

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
mkdir -p "$ROOT/static"
cd "$ROOT/docs"   # image links in the .md files are relative to docs/ (../outputs/...)

for doc in "BO_Executive_Summary:BORDER OPTICS — Executive Summary" \
           "BO_Research_Paper:BORDER OPTICS — Research Paper" \
           "BO_Development_Log:BORDER OPTICS — Development Log"; do
    name="${doc%%:*}"
    title="${doc#*:}"
    echo "Building docs/${name}.pdf..."
    pandoc "${name}.md" -f markdown-implicit_figures -o "${name}.pdf" \
        --pdf-engine=wkhtmltopdf --pdf-engine-opt=--enable-local-file-access \
        -V margin-top=20mm -V margin-bottom=20mm -V margin-left=20mm -V margin-right=20mm \
        --metadata title="${title}" \
        --toc
    cp "${name}.pdf" "$ROOT/static/${name}.pdf"
done

# the Declarations PDF is built separately; keep the dashboard's copy in step with docs/
cp BO_Declarations.pdf "$ROOT/static/BO_Declarations.pdf"

echo "Done. The three PDFs are up to date in docs/ and static/; BO_Declarations.pdf copied to static/."
