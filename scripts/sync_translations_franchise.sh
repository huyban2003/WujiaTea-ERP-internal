#!/usr/bin/env bash
set -euo pipefail

PYTHON="/home/dev/miniconda3/envs/odoo19/bin/python3.10"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

"${PYTHON}" "${SCRIPT_DIR}/sync_franchise_translations.py" "$@"
