#!/usr/bin/env bash
# WujiaTea — CRON ENTRYPOINT (22h): mở phiên nightly agent dạng INTERACTIVE trong tmux.
# Vì cron KHÔNG có TTY nên không chạy interactive trực tiếp được; ta mở 1 tmux session
# detached (có pty) chạy run-interactive.sh, rồi user attach vào xem + trả lời khi agent hỏi:
#
#     tmux attach -t wujia-nightly
#
# (Ctrl-b d để detach lại mà không tắt phiên.) Cần: tmux đã cài + run-interactive.sh opus xhigh.
set -uo pipefail

export PATH="/home/huyban/.local/bin:/home/huyban/miniconda3/envs/odoo/bin:/usr/local/bin:/usr/bin:/bin"
export HOME="/home/huyban"
SESSION="wujia-nightly"
NIGHTLY="/home/huyban/odoo-dev/WujiaTea/scripts/ba_spec/qa_nightly"
LOG="/home/huyban/odoo-dev/WujiaTea/logs/qa-nightly-tmux-$(date +%F).log"
mkdir -p "$(dirname "$LOG")"

# Skip 1 đêm cụ thể: tạo file $NIGHTLY/.skip-YYYY-MM-DD (user tự trigger tay đêm đó).
# Tự hết hạn: hôm sau ngày đổi -> không còn khớp -> chạy bình thường.
if [ -f "$NIGHTLY/.skip-$(date +%F)" ]; then
  echo "$(date '+%F %T') có .skip-$(date +%F) — bỏ qua nightly tối nay." >>"$LOG"
  exit 0
fi

if ! command -v tmux >/dev/null 2>&1; then
  echo "$(date '+%F %T') [LỖI] chưa cài tmux — chạy: sudo apt-get install -y tmux" >>"$LOG"
  exit 1
fi

# Đã có phiên thì không mở đè (tránh 2 agent chạy song song đụng git)
if tmux has-session -t "$SESSION" 2>/dev/null; then
  echo "$(date '+%F %T') phiên '$SESSION' đã chạy — bỏ qua." >>"$LOG"
  exit 0
fi

# Session dùng shell BỀN (không exec agent trực tiếp): tạo shell rồi GÕ lệnh agent vào.
# Agent thoát/crash → về lại shell, session VẪN sống (không biến mất cả server như trước).
tmux new-session -d -s "$SESSION"
tmux send-keys -t "$SESSION" "$NIGHTLY/run-interactive.sh" Enter
echo "$(date '+%F %T') đã mở phiên '$SESSION' (shell bền) + gõ agent. Xem: tmux attach -t $SESSION" >>"$LOG"
