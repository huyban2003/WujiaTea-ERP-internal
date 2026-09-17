# css_move — bộ dời CSS màn khỏi portal_layout (dựng ở F2, dùng lại F3)

1. `plan.py <dir> <css_owner --layout-domain report>` → `moves.json` + cảnh báo CASCADE? (sửa TARGET/KEEP trong file).
2. `apply.py <dir>` — cắt rule khỏi layout, dán lên ĐẦU file CSS module (sửa MODCSS). Loại rule lật cascade khỏi moves.json trước.
3. `semdiff.py <dir>` — tập (media, selector, prop, value) mất ở layout = thêm ở module (so HEAD ↔ worktree).
4. `cstyle.py out.json` (TRƯỚC khi sửa + SAU) rồi `cdiff.py before.json after.json` — full computed style + ép :hover/:active/:focus,
   cần server 8099. Sửa ACC/PREF theo màn. **Xoá `ir_attachment` url `/web/assets/%` + restart** trước lượt SAU (bundle cache cũ).
Chạy `cstyle.py` 2 lần trước khi sửa để chắc đo ổn định (0 khác).
