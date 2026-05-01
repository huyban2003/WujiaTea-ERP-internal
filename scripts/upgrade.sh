#!/usr/bin/env bash
# Upgrade Wujia modules without dropping the DB.
# Usage: ./scripts/upgrade.sh                # upgrade all wujia_* modules
#        ./scripts/upgrade.sh wujia_franchise  # upgrade specific module(s)
set -euo pipefail

PROJECT_DIR="/home/huyban/odoo-dev/WujiaTea"
ODOO_DIR="${PROJECT_DIR}/odoo19"
CONFIG="${PROJECT_DIR}/config/odoo.conf"
PYTHON="/home/huyban/miniconda3/envs/odoo/bin/python"
DB_NAME="wujia_tea_19"

MODULES="${1:-wujia_core,wujia_franchise}"

cd "${ODOO_DIR}"
exec "${PYTHON}" odoo-bin -c "${CONFIG}" -d "${DB_NAME}" -u "${MODULES}" --stop-after-init
