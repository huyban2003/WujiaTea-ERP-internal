# Prompt phiên E4a — FilterBar `CMP-FB-001`, kiểm kê + nền + 2 route mẫu

> Dán khối dưới đây sau `/wujia-start`. Đây là **lượt mở màn** của cụm E4; E4b (`docs/prompt-e4b.md`)
> và E4c chạy sau. Không có tiền đề nào ngoài E3 đã xong.

---

Làm **cụm E4a** — lượt đầu của `UI-FILTER-001` (STT 139, dòng 132 sheet, `Ready for Dev`, Owner Dev,
Need BA Confirm = No). Ba việc, **đúng thứ tự**: kiểm kê → dựng nền → migrate 2 route mẫu.
**KHÔNG đóng issue, KHÔNG chạy `qa_sync.py`** — issue đóng ở E4c.

## Việc 1 — Kiểm kê FB-10 (làm TRƯỚC khi sửa một byte nào)

Đây không phải thủ tục giấy tờ: acceptance chính của cả cụm E4 là **"điều kiện lọc trước = sau"**.
Không chụp trước thì sau này không có gì để đối chiếu, và bảng Pass sẽ vô nghĩa.

Với **từng màn × từng viewport** (PC ≥992 và mobile <992), ghi: tên `name=` của mọi input/select,
kiểu control (text · date · select · chip), nhãn, có nút reset không, nhãn nút submit.

- Đếm **theo cấu trúc bằng `lxml`**, không grep thô. Bài học D4e: grep bắt cả tên con BEM nên đếm
  ra 36 trong khi sự thật là 7, phải đính chính **ba lần**; E3 đếm bằng `t-foreach` + lxml nên không
  đính chính lần nào.
- ⚠️ `grep 'row g-2'` ra **10 chỗ** nhưng chỉ **4** là thanh lọc (support:24 · knowledge:36 ·
  return_list:38 · info_request_list:34). 6 chỗ còn lại là lưới trong form tạo/chi tiết — đụng vào
  là hỏng màn khác.
- Sản phẩm: **`docs/e4-filter-inventory.md`** — bảng 12 màn, kèm lệnh đếm lại được để E4b/E4c dùng
  chính nó làm mốc.

## Việc 2 — Dựng nền, KHÔNG dựng lại từ đầu

Hai seam đã có sẵn và gần đúng spec BA rồi; việc của lượt này là **gom về một component**, không phải
viết CSS mới:

| Tầng | Hiện trạng đã soi | Việc |
|---|---|---|
| PC | `.wj-pc-filterbar` r16 · padding `22px 20px` · control **42** qua `--wj-pc-input-h` (`_pc_components.css:89-123`) — **đã khớp BA** | Bọc thành template `wujia_portal_layout.wj_filter_bar`, tham số hoá: search · dates · selects · chips · actions |
| Mobile | `.wj-filter-card` trên nền `wj-surface-card` · search field **38** · nút `38×38` · radius 10 · gap 10 (`_components.css:261-300`) | Về **r14 · padding 12 · gap 8**; ô lọc **visual 38 + vùng chạm 44** |

- **Vùng chạm 44 mà không nở visual**: dùng đúng kỹ thuật đã nghiệm thu ở E3 — `::before`
  `position:absolute` phủ 44×44, hộp nhìn thấy giữ 38. Đã có guard đo được (`wj_pagination.py` PG-2).
- Sub-component **đã có, phải tái dùng chứ không đẻ mới**: `wj-filter-chip` (+`chips`/`--soft`/
  `--wrap`/`--clear`, 30 chỗ) · `wj-pc-filter-control` (25) · `wj-filter-search[-field/-btn]` ·
  `wj-filter-date[s/-sep]` (8) · `wj-filter-error` (2 — cảnh báo ngày ngược, hiện chỉ history + return).
- **Gỡ inline style khi tham số hoá**: mẫu PC đang có `style="max-width:180px"` ×2 và
  `max-width:200px` (`portal_history.xml:196-203`) — component nhận gợi ý bề rộng, không để inline.
- Nhãn theo BA: submit **"Tìm kiếm"** (hiện đang "Tìm"), reset **"Xóa lọc"** (hiện "Reset").
  **Không thêm reset vào màn chưa có.**
- `wj-pc-filterbar` còn 1 call site ở gallery `pc_preview.xml:92` — migrate luôn để gallery không
  thành nguồn dáng thứ hai (bài học E3: `pc_preview.py` phải `import` **tại chỗ** vì
  `wujia_portal_base` phụ thuộc `wujia_portal_layout`, import đầu file là vòng tròn).

## Việc 3 — Migrate đúng 2 route mẫu BA

| Mẫu | Call site | Ghi chú |
|---|---|---|
| PC | `wujia_portal_purchase_history/views/portal_history.xml:187` | mẫu BA chọn; giữ `<input type="hidden" name="page_size">` (WJ-PH-008 — mất là người dùng phải chọn lại số dòng) |
| Mobile | `wujia_portal_delivery/views/portal_delivery.xml:313` | mẫu BA chọn; giữ `<input type="hidden" name="bs">` luôn render kể cả rỗng (JS chip AJAX đồng bộ qua nó) |

Hai màn này đo xong, khớp bảng, **mới** được nhân ra ở E4b. Không tiện tay migrate thêm màn thứ ba.

## Luật bắt buộc

1. **Không thêm/bớt điều kiện lọc** giữa PC và mobile — kiểm kê Việc 1 là chân lý.
2. **Không đụng** `wujia_portal_inspection` / `wujia_franchise_inspection` (luật 08/09). Họ class cũ
   nào Khảo sát còn dùng thì **thu hẹp selector vào `.wj-inspection-pc`, KHÔNG xoá** (bẫy E3c).
3. Không đụng ProductCard của màn Đặt hàng.
4. Comment **tối đa 1 dòng**, chỉ ở chỗ người sau chắc chắn đoán sai (chủ dự án nhắc lần 2, 04/09).
5. Không hex cứng — `var(--wujia-*)`; không đẻ modifier mới khi cái sẵn có đủ.
6. **Ask-don't-assume**: gặp fork ngoài 5 điểm đã chốt 12/09 thì hỏi, đừng tự code.

## Nghiệm thu (đo bằng máy, không nhìn ảnh)

- DB **copy cô lập**, cổng riêng, **có cài 2 module Khảo sát giống UAT** (luật 11/09). Không đụng
  `wujia_tea_19`/8019. Truyền `--http-port` riêng (bẫy E3: `--no-http` vẫn bind cổng).
- `-u <mod> --stop-after-init` RC=0, 0 ERROR.
- Đo bằng `em.hcm` / `wujia@test123`, **không dùng `admin`** (bẫy Pass rỗng).
- **FB-10 trên 2 màn mẫu**: bộ tham số sau = trước, từng cái một.
- PC control **42** cùng baseline, wrap theo nhóm; mobile card **r14/p12/g8**, ô lọc **38 visual /
  44 chạm** (đo hộp `::before`, không đo hộp nhìn thấy).
- **Mẫu đo phải khác 0** — ra 0 control là `--scope` sai chứ không phải Pass; luôn `--scope body`
  (bẫy D6d: `--scope .wujia-mpage` bỏ sót đúng form thứ ba).
- Hồi quy `wj_measure --diff` ≥13 route × 5 khổ: 0 tràn ngang · 0 lỗi JS · 0 màn mất record; mọi ô
  đổi chiều cao phải giải trình được.
- **Run đối chứng** trên cây mã trước lượt (worktree + DB riêng) — bắt buộc, bài học S57.
- Test mới **mutation-proof**: phá từng guard, mỗi mũi đỏ đúng test của nó; harness mutation phải
  `assert s != before` (bẫy D6c M5) và tránh assert lỏng kiểu chuỗi cũ là tiền tố chuỗi mới (M9).

## Kết thúc lượt

- Bump version **mọi module bị đụng** + bump `?v=` của **mọi file CSS nạp bằng `<link>` tay**
  (bẫy D4: quên bump ⇒ restart không nạp lại XML, BA retest trên cache cũ).
- Ghi `docs/e4a-acceptance-matrix.md` + `docs/e4-filter-inventory.md`.
- **KHÔNG** `qa_sync.py`, không đổi trạng thái sheet.
- Commit + push `main`; ghi rõ lệnh `-u` để gộp vào lượt deploy của E4c.
