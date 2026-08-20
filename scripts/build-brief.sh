#!/usr/bin/env bash
# Build BA Figma Brief PDF từ wujia-figma-brief.tex (standalone, KHÔNG đụng wujia-tea-doc).
# Engine: lualatex preferred (fontspec + Lato hỗ trợ tiếng Việt), fallback xelatex.
set -euo pipefail

DOCS_DIR="/home/huyban/odoo-dev/WujiaTea/docs"
TEX_FILE="wujia-figma-brief.tex"
PDF_FILE="${TEX_FILE%.tex}.pdf"

cd "${DOCS_DIR}"

if command -v lualatex >/dev/null 2>&1 && \
   kpsewhich luaotfload-main.lua >/dev/null 2>&1; then
    echo "==> Using lualatex (direct .tex -> .pdf)"
    lualatex -interaction=nonstopmode -halt-on-error "${TEX_FILE}" >/dev/null
    lualatex -interaction=nonstopmode -halt-on-error "${TEX_FILE}" >/dev/null
elif command -v xelatex >/dev/null 2>&1; then
    echo "==> Using xelatex (direct .tex -> .pdf)"
    xelatex -interaction=nonstopmode -halt-on-error "${TEX_FILE}" >/dev/null
    xelatex -interaction=nonstopmode -halt-on-error "${TEX_FILE}" >/dev/null
else
    echo "ERROR: cần lualatex (texlive-luatex) hoặc xelatex (texlive-xetex)."
    exit 1
fi

echo ""
echo "==> Done"
ls -lh "${DOCS_DIR}/${PDF_FILE}"
echo "    Open: xdg-open ${DOCS_DIR}/${PDF_FILE}"
