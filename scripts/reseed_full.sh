#!/usr/bin/env bash
# Drop + recreate the WujiaTea DB, install the full module chain,
# and re-run every seed script in the correct order.
#
# Use when:
#   - dev DB is broken (e.g. after destructive schema change),
#   - bootstrapping a fresh prod / staging server.
#
# Does NOT touch git or push anything.
set -euo pipefail

PROJECT_DIR="/home/huyban/odoo-dev/WujiaTea"
ODOO_DIR="${PROJECT_DIR}/odoo19"
CONFIG="${PROJECT_DIR}/config/odoo.conf"
PYTHON="/home/huyban/miniconda3/envs/odoo/bin/python"
SCRIPTS="${PROJECT_DIR}/scripts"
DB_NAME="${DB_NAME:-wujia_tea_19}"
PG_HOST="${PG_HOST:-127.0.0.1}"
PG_USER="${PG_USER:-odoo19}"
PG_PASS="${PG_PASS:-1}"

MODULES="wujia_core,wujia_franchise,wujia_sale,wujia_fleet,wujia_delivery,wujia_portal_base,wujia_portal_layout,wujia_portal_sale,wujia_portal_purchase_history,wujia_portal_delivery,wujia_portal_return,wujia_portal_notification,wujia_portal_exam,wujia_portal_knowledge,wujia_portal_report,wujia_portal_support"

echo "==> Drop DB ${DB_NAME}"
PGPASSWORD="${PG_PASS}" dropdb -h "${PG_HOST}" -U "${PG_USER}" --if-exists "${DB_NAME}"

echo "==> Create DB ${DB_NAME}"
PGPASSWORD="${PG_PASS}" createdb -h "${PG_HOST}" -U "${PG_USER}" "${DB_NAME}"

echo "==> Install Odoo + modules (no demo data per WujiaTea convention)"
cd "${ODOO_DIR}"
"${PYTHON}" odoo-bin -c "${CONFIG}" -d "${DB_NAME}" \
    -i "${MODULES}" --without-demo=True --stop-after-init

echo "==> Seed admin + franchise"
"${PYTHON}" odoo-bin shell -c "${CONFIG}" -d "${DB_NAME}" --no-http \
    < "${SCRIPTS}/seed_admin_franchise.py"

echo "==> Seed fleet demo"
"${PYTHON}" odoo-bin shell -c "${CONFIG}" -d "${DB_NAME}" --no-http \
    < "${SCRIPTS}/seed_fleet_demo.py"

echo "==> Seed portal demo (sale orders, picking, batches)"
"${PYTHON}" odoo-bin shell -c "${CONFIG}" -d "${DB_NAME}" --no-http \
    < "${SCRIPTS}/seed_portal_demo.py"

echo "==> Seed knowledge demo"
"${PYTHON}" odoo-bin shell -c "${CONFIG}" -d "${DB_NAME}" --no-http \
    < "${SCRIPTS}/seed_knowledge_demo.py"

echo "==> Seed support demo"
"${PYTHON}" odoo-bin shell -c "${CONFIG}" -d "${DB_NAME}" --no-http \
    < "${SCRIPTS}/seed_support_demo.py"

echo "==> DONE. To verify, run:"
echo "    ${PYTHON} odoo-bin shell -c ${CONFIG} -d ${DB_NAME} --no-http < ${SCRIPTS}/test_sprint5.py"
