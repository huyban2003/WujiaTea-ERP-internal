#!/usr/bin/env bash
# Build doc PDF từ LaTeX source.
# Pipeline mặc định: pandoc + wkhtmltopdf (đã có sẵn, không cần install thêm).
# Pipeline preferred (nếu cài texlive-luatex): lualatex compile trực tiếp,
# giữ nguyên longtable/lstlisting style đẹp hơn.
set -euo pipefail

DOCS_DIR="/home/huyban/odoo-dev/WujiaTea/docs"
TEX_FILE="wujia-tea-doc.tex"
PDF_FILE="${TEX_FILE%.tex}.pdf"

cd "${DOCS_DIR}"

# Ưu tiên lualatex nếu có luaotfload (texlive-luatex package)
if command -v lualatex >/dev/null 2>&1 && \
   kpsewhich luaotfload-main.lua >/dev/null 2>&1; then
    echo "==> Using lualatex (direct .tex -> .pdf)"
    lualatex -interaction=nonstopmode -halt-on-error "${TEX_FILE}" >/dev/null
    lualatex -interaction=nonstopmode -halt-on-error "${TEX_FILE}" >/dev/null
elif command -v pandoc >/dev/null 2>&1 && \
     command -v wkhtmltopdf >/dev/null 2>&1; then
    echo "==> Using pandoc + wkhtmltopdf (fallback — cài texlive-luatex để có quality cao hơn)"
    pandoc "${TEX_FILE}" -o "${PDF_FILE}" \
        --pdf-engine=wkhtmltopdf \
        --toc --toc-depth=2 \
        --metadata title="WujiaTea Odoo 19 — Documentation" \
        --metadata date="$(date +%Y-%m-%d)" \
        -V margin-top=20 -V margin-bottom=20 \
        -V margin-left=20 -V margin-right=20 \
        2>&1 | grep -v "^\[" | grep -v "Loading page\|Printing pages\|inotify_" || true
else
    echo "ERROR: cần một trong:"
    echo "  - sudo apt install texlive-luatex texlive-fonts-extra (preferred)"
    echo "  - hoặc pandoc + wkhtmltopdf (đã có sẵn)"
    exit 1
fi

echo ""
echo "==> Done"
ls -lh "${DOCS_DIR}/${PDF_FILE}"
echo "    Open: xdg-open ${DOCS_DIR}/${PDF_FILE}"
