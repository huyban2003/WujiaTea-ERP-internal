#!/usr/bin/env bash
# Cài/gỡ cron 22h cho nightly agent (idempotent). Chạy SAU khi cổng ghi + auth đã sẵn.
#   ./install-cron.sh install     # cài
#   ./install-cron.sh uninstall   # gỡ
set -uo pipefail
LINE="0 22 * * * /home/huyban/odoo-dev/WujiaTea/scripts/ba_spec/qa_nightly/cron-tmux-launch.sh"
TAG="# wujia-nightly-agent"

# crontab hiện tại, bỏ dòng cũ của mình (|| true để không chết khi crontab rỗng)
current="$(crontab -l 2>/dev/null | grep -vF "$TAG" || true)"

case "${1:-install}" in
  install)
    { [ -n "$current" ] && printf '%s\n' "$current"; printf '%s %s\n' "$LINE" "$TAG"; } | crontab -
    echo "Đã cài cron 22h (interactive trong tmux — attach: tmux attach -t wujia-nightly):"
    crontab -l | grep -F "$TAG" ;;
  uninstall)
    if [ -n "$current" ]; then printf '%s\n' "$current" | crontab -; else crontab -r 2>/dev/null || true; fi
    echo "Đã gỡ cron nightly." ;;
  *) echo "usage: $0 [install|uninstall]"; exit 1 ;;
esac
