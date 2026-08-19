#!/usr/bin/env bash
# Create the wujia_tea_19 database and install initial Wujia modules.
# Run once when bootstrapping a fresh environment.
set -euo pipefail

PROJECT_DIR="/home/huyban/odoo-dev/WujiaTea"
ODOO_DIR="${PROJECT_DIR}/odoo19"
CONFIG="${PROJECT_DIR}/config/odoo.conf"
PYTHON="/home/huyban/miniconda3/envs/odoo/bin/python"
DB_NAME="wujia_tea_19"
MODULES="wujia_core,wujia_franchise"

cd "${ODOO_DIR}"
exec "${PYTHON}" odoo-bin -c "${CONFIG}" -d "${DB_NAME}" -i "${MODULES}" --stop-after-init --without-demo=True
