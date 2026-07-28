#!/usr/bin/env bash
# Start Odoo 19 in dev mode for the WujiaTea project.
set -euo pipefail

PROJECT_DIR="/home/dev/WujiaTea-ERP-internal"
ODOO_DIR="${PROJECT_DIR}/odoo19"
CONFIG="${PROJECT_DIR}/config/odoo.conf"
PYTHON="/home/dev/miniconda3/envs/odoo19/bin/python"

cd "${ODOO_DIR}"
exec "${PYTHON}" odoo-bin -c "${CONFIG}" --dev=xml,qweb,reload "$@"
