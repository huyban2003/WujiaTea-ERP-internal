#!/usr/bin/env bash
# WujiaTea — phiên Dev Agent INTERACTIVE (CÓ NGƯỜI TRỰC).
# Khác run.sh (headless cron): mở Claude Code interactive để agent HỎI THẲNG bạn khi
# gặp fork và CHỜ trả lời (như Claude Code thường ngày). Bạn ngồi canh + trả lời.
# KHÔNG chạy qua cron (cron không có TTY) — chạy tay trong terminal khi bạn ngồi vào máy.
#
#   ./run-interactive.sh
#
set -uo pipefail

PROJECT="/home/huyban/odoo-dev/WujiaTea"
BA="$PROJECT/scripts/ba_spec"
NIGHTLY="$BA/qa_nightly"
PY="/home/huyban/miniconda3/envs/odoo/bin/python3"
CLAUDE="/home/huyban/.local/bin/claude"
UAT="http://113.161.187.126:8019"

if [ ! -t 0 ]; then
  echo "⚠  Cần chạy trong terminal (TTY) để agent hỏi/chờ bạn. Đang không có TTY -> thoát."
  echo "   (Muốn chạy không người trực thì dùng run.sh headless qua cron.)"
  exit 1
fi

cd "$BA" || exit 1
echo "========== WUJIA INTERACTIVE DEV SESSION $(date '+%F %T') =========="

# 1) UAT health-check (thông tin — không chặn)
UAT_CODE=$(curl -sL --max-time 15 -o /dev/null -w '%{http_code}' "$UAT/web/login" 2>/dev/null || echo 000)
echo "[health] UAT $UAT/web/login -> $UAT_CODE"

# 2) Bức tranh hôm nay: trạng thái Issue List + hàng đợi Dev + task tab Tasks
echo
echo "----- Issue List theo trạng thái (nhìn để biết cần làm gì) -----"
"$PY" issue_queue.py --status 2>/dev/null || echo "(issue_queue lỗi — kiểm mạng/sheet)"
echo
echo "----- Task tab Tasks sẵn sàng cho AI -----"
"$PY" task_sync.py --list 2>/dev/null || echo "(task_sync lỗi)"
echo
echo "==============================================================="
echo "Mở Claude Code interactive. Agent sẽ đề xuất việc rồi HỎI bạn ở mỗi fork."
echo "Ctrl-C / /exit để dừng. Git branch riêng mỗi việc, push main chỉ khi bạn đồng ý."
echo

# 3) Mở phiên interactive, seed bằng prompt interactive.
#    (Mặc định permission = hỏi trước như Claude Code thường. Muốn ít prompt hơn:
#     thêm  --permission-mode acceptEdits  để tự nhận sửa file, vẫn hỏi khi chạy git/-u.)
exec "$CLAUDE" --model opus --effort xhigh --permission-mode acceptEdits \
     "$(cat "$NIGHTLY/agent_prompt_interactive.md")"
