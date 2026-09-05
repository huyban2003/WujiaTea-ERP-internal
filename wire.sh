#!/usr/bin/env bash
# Nối devkit vào đúng chỗ Claude Code + repo WujiaTea mong đợi.
# Chạy 1 lần trên mỗi máy. Idempotent.
set -euo pipefail
DK="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WUJIA="${WUJIA_REPO:-$HOME/odoo-dev/WujiaTea}"

# ba_spec: repo chính gitignore thư mục này -> symlink vào không ảnh hưởng server
if [ -e "$WUJIA/scripts/ba_spec" ] && [ ! -L "$WUJIA/scripts/ba_spec" ]; then
  mv "$WUJIA/scripts/ba_spec" "$WUJIA/scripts/ba_spec.bak.$(date +%s)"
  echo "  ! ba_spec cũ đã đổi tên thành .bak — nhớ bê 3 file secret sang"
fi
ln -sfn "$DK/ba_spec" "$WUJIA/scripts/ba_spec"
echo "  ✅ $WUJIA/scripts/ba_spec -> $DK/ba_spec"

# skill/command của Claude Code
mkdir -p "$HOME/.claude/commands"
for f in "$DK"/commands/*.md; do
  ln -sfn "$f" "$HOME/.claude/commands/$(basename "$f")"
done
echo "  ✅ $HOME/.claude/commands/*.md -> $DK/commands/"

# nhắc secret
for s in sheet_endpoint.json client_secret.json token.json; do
  [ -f "$DK/ba_spec/$s" ] || echo "  ⚠ thiếu $DK/ba_spec/$s (chuyển tay, không qua git)"
done
