#!/usr/bin/env bash
# WujiaTea — nightly autonomous QA/dev agent (chạy 22h local qua crontab).
# Reconcile Issue List (deterministic) + nếu có task Ready-for-AI thì launch claude
# headless để tự code/test/push. Deploy prod = user tay. Dev-only, gitignored.
set -uo pipefail

PROJECT="/home/huyban/odoo-dev/WujiaTea"
BA="$PROJECT/scripts/ba_spec"
NIGHTLY="$BA/qa_nightly"
PY="/home/huyban/miniconda3/envs/odoo/bin/python3"
CLAUDE="/home/huyban/.local/bin/claude"
UAT="http://113.161.187.126:8019"
LOG="$PROJECT/logs/qa-nightly-$(date +%F).log"
BUDGET_USD="${WUJIA_NIGHTLY_BUDGET:-8}"
MAX_HOURS="${WUJIA_NIGHTLY_MAX_HOURS:-3}"   # trần thời gian mỗi đêm (user: 2-3h)

mkdir -p "$PROJECT/logs"
# PATH tối thiểu cho môi trường cron
export PATH="/home/huyban/.local/bin:/home/huyban/miniconda3/envs/odoo/bin:/usr/local/bin:/usr/bin:/bin"

exec >>"$LOG" 2>&1
echo ""
echo "========== WUJIA NIGHTLY $(date '+%F %T') =========="

# 1) UAT health-check
UAT_CODE=$(curl -sL --max-time 15 -o /dev/null -w '%{http_code}' "$UAT/web/login" 2>/dev/null || echo 000)
echo "[health] UAT $UAT/web/login -> $UAT_CODE"

# 2) Reconcile Issue List — deterministic, không cần LLM (chỉ khi UAT ổn định)
cd "$BA" || exit 1
if [ "$UAT_CODE" = "200" ]; then
    echo "[qa_sync] apply..."
    "$PY" qa_sync.py --apply || echo "[qa_sync] lỗi (xem log trên)"
else
    echo "[qa_sync] BỎ QUA — UAT != 200 (đang deploy/down), không handoff retest."
fi

# 3) Có task Ready-for-AI không? (không có -> khỏi tốn LLM)
READY_COUNT=$("$PY" task_sync.py --list 2>/dev/null | grep -c '^\[row ' || true)
echo "[tasks] Ready-for-AI: ${READY_COUNT:-0}"
if [ "${READY_COUNT:-0}" -eq 0 ]; then
    echo "[done] Không có task cho AI — chỉ reconcile. Kết thúc."
    exit 0
fi

# 4) Launch autonomous agent — trần thời gian ${MAX_HOURS}h VÀ trần tiền $BUDGET_USD (cái nào tới trước)
echo "[agent] launch claude headless (max ${MAX_HOURS}h, budget \$$BUDGET_USD)..."
cd "$PROJECT" || exit 1
# Agent chính: opus + effort xhigh. Sub-agent: sonnet low (chỉ thị trong agent_prompt.md).
timeout --signal=INT "${MAX_HOURS}h" \
    "$CLAUDE" -p "$(cat "$NIGHTLY/agent_prompt.md")" \
        --permission-mode bypassPermissions \
        --model opus \
        --effort xhigh \
        --max-budget-usd "$BUDGET_USD" \
        --output-format text
rc=$?
if [ "$rc" = "124" ]; then
    echo "[agent] CHẠM TRẦN ${MAX_HOURS}h -> dừng (INT). Task dở nằm ở branch riêng, main không bẩn."
elif [ "$rc" != "0" ]; then
    echo "[agent] claude thoát mã $rc."
fi

echo "[done] nightly $(date '+%T')."
