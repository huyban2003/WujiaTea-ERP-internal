# Prompt phiên E4b — FilterBar `CMP-FB-001`, phủ hết call site

> **⚠️ ĐÃ TÁCH ĐÔI 19/09/2026** — chủ dự án chốt cắt E4b thành **E4b1 (PC, đã xong:
> `docs/e4b1-acceptance-matrix.md`)** và **E4b2 (mobile, prompt: `docs/prompt-e4b2.md`)**.
> File này giữ lại làm hồ sơ phạm vi gốc; **đừng dán nguyên nó cho phiên mới**.

> Dán khối dưới đây sau `/wujia-start`. **Điều kiện tiên quyết: E4a đã xong** (component
> `wj_filter_bar` + sub-component đã dựng, 2 route mẫu đã migrate, kiểm kê FB-10 đã chụp ở
> `docs/e4-filter-inventory.md`). Chưa có E4a thì dừng, làm E4a trước.

---

Làm **cụm E4b** — lượt giữa của `UI-FILTER-001` (STT 139, dòng 132 sheet, `Ready for Dev`,
Owner Dev). Phạm vi: **nhân component của E4a ra hết call site còn lại**, PC lẫn mobile.
**KHÔNG đóng issue ở lượt này** — đóng ở E4c sau khi vá wiring ngày.

## Phạm vi chính xác (đã đếm 16/09, đếm lại trước khi sửa)

**PC — 4 màn Bootstrap `row g-2` → về component** (control BA đo 28–32px, phải lên **42**):

| Màn | File:dòng |
|---|---|
| Hỗ trợ | `wujia_portal_support/views/portal_support.xml:24` |
| Kiến thức | `wujia_portal_knowledge/views/portal_knowledge.xml:36` |
| Đổi trả | `wujia_portal_return/views/portal_return_list.xml:38` |
| Yêu cầu cập nhật | `wujia_portal_info_request/views/portal_info_request_list.xml:34` |

⚠️ `grep 'row g-2'` bắt **10 chỗ**, nhưng chỉ 4 chỗ trên là thanh lọc — 6 chỗ còn lại là lưới
trong form tạo/chi tiết (`portal_return_form:28/98`, `portal_return_detail:210`,
`portal_info_request_form:31`, `portal_info_request_detail:34`, `portal_support:221`).
**Đụng vào là hỏng màn khác** — đây đúng họ bẫy D4e (grep thô đếm nhầm 36 thay vì 7, đính chính 3 lần).

**PC — căn lề, KHÔNG đổi cấu trúc:**
- `wj-pc-filterbar` 3 màn còn lại (delivery · exam · notification) — mẫu BA là history, E4a đã làm.
- `wj-debt-pc-filter` `portal_debt.xml:293` + `:580` — **GIỮ NGUYÊN week selector**, chỉ căn lề/nhãn.

**Mobile — 6 `wj-filter-card` còn lại** (mẫu BA là delivery `:313`, E4a đã làm):
`portal_history.xml:253` · `portal_notification.xml:276` · `portal_support.xml:141` ·
`portal_knowledge.xml:156` · `portal_return_list.xml:165` · `portal_exam.xml:148` (qua `sc_class`).

**Mobile lẻ — chỉ đồng bộ token, không dựng lại:** `wujia-morder-search` (Đặt hàng — **không đụng
ProductCard**) · `wj-rep-mfilter` (Báo cáo) · `wj-debt-filter` `portal_debt.xml:17`.

## Luật bắt buộc của lượt này

1. **Không thêm/bớt điều kiện lọc nào** giữa PC và mobile — bảng kiểm kê FB-10 của E4a là chân lý,
   đo lại sau khi sửa phải ra **đúng bộ tham số cũ** cho từng màn. Đây là acceptance chính.
2. **Không thêm reset vào màn chưa có**; màn đang có nút reset thì nhãn về "Xóa lọc".
   Không thêm header/bottom-sheet cho mobile.
3. Mobile giữ dáng card delivery: **r14 · padding 12 · gap 8**, thứ tự search → ngày → chip/select.
   Ô lọc: **visual 38, vùng chạm 44** (Q1 chủ dự án đã chốt 12/09, không hỏi lại).
4. **Xoá họ class cũ — nhưng chỗ nào nhóm Khảo sát còn dùng thì THU HẸP selector vào
   `.wj-inspection-pc`, TUYỆT ĐỐI không xoá.** Bẫy E3c: xoá thẳng là gãy ngầm màn Khảo sát,
   mà Khảo sát thuộc diện defer nên không được sửa để chữa.
5. **Không đụng** `wujia_portal_inspection` / `wujia_franchise_inspection` (luật 08/09).
6. Comment **tối đa 1 dòng**, chỉ ở chỗ người sau chắc chắn đoán sai (chủ dự án nhắc lần 2, 04/09).
7. Không hex cứng — dùng `var(--wujia-*)`; không đẻ modifier mới khi cái sẵn có đủ.

## Nghiệm thu (đo bằng máy, không nhìn ảnh)

- DB **copy cô lập**, cổng riêng, **có cài 2 module Khảo sát giống UAT** (luật 11/09 — 4 test D3
  từng đỏ chỉ vì DB dev không cài khảo sát). Không đụng `wujia_tea_19`/8019.
- `-u <mod> --stop-after-init` RC=0, 0 ERROR. Nhớ truyền `--http-port` riêng (bẫy E3: `--no-http`
  vẫn bind cổng).
- **FB-10**: kiểm kê điều kiện lọc **trước = sau** cho 12 màn — đây là dòng Pass/Fail quan trọng nhất.
- Control PC **42px** cùng baseline, wrap theo nhóm; mobile card r14/p12/g8, ô lọc 38 visual / 44 chạm.
- Guard: mở rộng `scripts/qa/wj_formcontrol.py` (D6c). **Mẫu đo phải khác 0** — nếu ra 0 control thì
  là `--scope` sai chứ không phải Pass (bẫy D6d: `--scope .wujia-mpage` bỏ sót đúng form thứ ba,
  luôn dùng `--scope body`).
- Hồi quy `wj_measure --diff` ≥13 route × 5 khổ: 0 tràn ngang · 0 lỗi JS · 0 màn mất record;
  mọi ô đổi chiều cao phải giải trình được bằng đúng thay đổi của lượt.
- **Run đối chứng** trên cây mã trước lượt (worktree + DB riêng) để phân biệt lỗi có sẵn với lỗi mới —
  bắt buộc, bài học S57.
- Bộ test: giữ 0 đỏ; test mới phải **mutation-proof** (phá từng guard, mỗi mũi đỏ đúng test của nó;
  `assert s != before` trong harness mutation — bẫy D6c M5).

## Kết thúc lượt

- Bump version **mọi module bị đụng** (bẫy D4: 13/14 module quên bump ⇒ restart không nạp lại XML)
  + bump `?v=` của **mọi file CSS nạp bằng `<link>` tay**.
- Ghi `docs/e4b-acceptance-matrix.md` + cập nhật `docs/e4-filter-inventory.md`.
- **KHÔNG chạy `qa_sync.py`**, không đổi trạng thái sheet — issue đóng ở E4c.
- Commit + push `main`, ghi rõ lệnh `-u` gộp cho lượt deploy.
