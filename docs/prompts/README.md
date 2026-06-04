# WujiaTea prompts — paste-ready cho mỗi session

Folder này chứa các prompt sẵn-paste cho từng sprint con. Mục đích: anh không phải nhớ workflow, không phải bịa spec — chỉ cần `/wujia-start` → mở file `.md` → copy → paste.

## Cấu trúc

- `sprint9/` — 16 prompt cho 16 sprint con còn lại của Sprint 9 (UI-01 đã DONE).
  - `09.02-ui-02-sidebar-remove-user-info.md` → `09.13-empty-state.md` — 1 file / issue UI.
  - `09.14-cleanup.md` — 301 redirect legacy slug + xóa stub `wujia_account`.
  - `09.15-verify.md` — `reseed_full.sh` + `test_sprint9.py` + 8 screenshot.
  - `09.16-doc.md` — `chapters/18-sprint9-*.tex` + `19-roadmap-v14-gaps.tex` + PDF + update summary.
  - `09.17-push.md` — commit Conventional EN + push + deploy command Windows.

## Cách dùng (mỗi session)

1. Gõ `/wujia-start` — agent load operating rules.
2. Mở file `sprint9/09.XX-*.md` tương ứng issue sắp làm.
3. Copy full content → paste vào chat.
4. Agent sẽ:
   - Mở xlsm verify spec cột G/H khớp với prompt (nếu BA edit sheet, agent dừng lại hỏi).
   - Grep v19 hiện trạng → plan ngắn → đợi anh approve.
   - Edit → upgrade → restart → screenshot.
   - Loop fix đến khi 100% khớp BA mockup col F.
   - Anh OK → cập nhật §9 bảng trong `wujia-compact-summary.md` (⬜ → ✅ + ngày + Files đã chạm).
5. Đóng session. Session sau lại lặp lại bước 1-5 với issue kế tiếp.

## Quy tắc tuyệt đối (lặp lại trong mọi prompt)

- **KHÔNG BỊA SPEC.** Spec gốc luôn ở `WujiaTea/docs/Wujia_Internal ERP Master Plan.xlsm` sheet "5. Issue List" cột G/H. Prompt chỉ là copy verbatim từ xlsm tại thời điểm 2026-05-23; nếu BA edit sau ngày này, agent phải đọc lại xlsm.
- **Code English-only.** Không tạo `.po` Sprint 9 — BA tự lo Sprint 10.
- **CSS dùng `var(--wujia-*)` trong `_variables.css`** + class share trong `_components.css`. Không hex/px cứng trong template.
- **1 sprint con = 1 session.** Không gộp nhiều issue.
- **Không push `main` đến hết Sprint 9.17.** Local-first, screenshot-first.
- **`bash scripts/upgrade.sh "<modules csv>"` RC=0** là điều kiện cần (không đủ — phải screenshot khớp).

## Thứ tự BA order (KHÔNG đảo)

`UI-01` ✅ → `UI-02` → `UI-03` → `UI-04` → `UI-05` → `UI-06` → `UI-07` → `UI-09` → `UI-11` → `UI-12` → `UI-14` → `UI-15` → `Empty` → `cleanup` → `verify` → `doc` → `push`.

(BA bỏ số UI-08, UI-10, UI-13 — không phải lỗi của em.)
