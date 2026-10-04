# Cụm I (Issue List) → Cụm H (chuẩn hoá component lượt 2) — lập 02/10/2026

> Chốt chủ dự án 02/10: **Issue trước, H sau**. 4 nhóm component chưa có spec ⇒ **Dev soạn đề xuất, BA duyệt**
> (đã soạn trong phiên 02/10: `docs/ba-component-spec-proposal.{xlsx,pdf}`).
> Tài liệu chuẩn component gửi dev khác: `docs/portal-component-standard.pdf` (v1.0, 20 trang).
> HEAD lúc lập: `394c241` (main, **ahead origin 3** — gồm `bea5fa8` top bar 992 chưa push/deploy).

## 0. Phạm vi — chỉ code của mình

**KHÔNG đụng** (code anh Thái): `wujia_franchise*`, `wujia_portal_inspection`, `wujia_franchise_inspection`,
`wujia_mobile_core`, `wujia_mobile_*`. Chỗ thay đổi helper dùng chung làm đổi hành vi màn của nhóm đó
(vd `get_active_franchise_ids_filter`) ⇒ **dừng hỏi chủ dự án + ghi bàn giao, không sửa code của họ**.

Luật kế thừa: §12 compact summary (UAT chỉ-đọc, Dev không tự `Done`, không ghi thêm vào tài liệu BA),
luật refactor `docs/refactor-plan.md` §"LUẬT BẤT DI BẤT DỊCH" (đo trước–sau bằng máy), test luôn kèm `-u`.

---

## 1. Kết quả review 02/10 (đo tĩnh template + Playwright build hiện hành)

### A. Phần đã chuẩn — giữ, không tách thêm module

| Component | Dùng | Ghi chú |
|---|---|---|
| PageHeader / BackPageHeader | 63 call | `_wj_back_url` một nguồn |
| SurfaceCard · CardHeader | 94 · 93 | |
| DataList · ListCard · Pagination | 36 · 13 (+24 row) · 23 | Bootstrap `pagination` = 0 |
| FilterBar · SectionHeader | 19 · 18 | |
| StatusBadge | 76 class | còn sót, xem B2 |
| Button / IconButton | 83 + 18 class | template `wj_button` 0 call — hợp đồng ở class |
| Bootstrap `card` / `btn` thô | 1 / 1 | |

Kết luận: lõi đủ; **không** tách `wujia_ui_core` (ADR-027: chỉ khi ≥2 kênh cần), không gộp markup PC/mobile.

### B. Còn hở

| # | Vấn đề | Số đo | Xử lý |
|---|---|---|---|
| B1 | Code chết | template `wj_button`/`wj_icon_button` 0 call · CSS `.wujia-btn` 0 dùng · khối Legacy `wujia-content-card-table:not(.wj-data-table)` (mọi call site đã qua `wj_data_list`) | H1 |
| B2 | StatusBadge sót | `wujia-badge` cho trạng thái bù hàng (Đổi trả), trạng thái + ưu tiên (Yêu cầu cập nhật, có Bootstrap `badge`) · guard `test_scan_e2_status_badge.py` chỉ quét 3 file | H2 |
| B3 | CSS trang trong `_components.css` | 2.606 dòng, ~800 dòng (988–1798) là Home, header mobile, bottom nav, kết quả gửi đơn | H3 |
| B4 | EmptyState chưa chuẩn | 7 họ, 198 class | H4 (sau BA) |
| B5 | Nhãn–giá trị | 8 họ, 170 class | H5 |
| B6 | InfoBanner | Bootstrap `alert` 50 + 10 họ 53 | H6 |
| B7 | StatCard | 7 họ | H7 |
| B8 | Badge ngoài trạng thái | `wujia-badge` 38 · `wj-pc-badge` 16 · Bootstrap `badge` 35 | H4b |
| B9 | Modal | 4 JS đóng/mở riêng, 4 bề rộng · 3 hộp `confirm()` trình duyệt | H8 |
| B10 | FormField | 6 họ + `form-control` 31 / `form-select` 13 · chữ trong ô mobile 12.25px (iPhone tự zoom) | H9 |
| B11 | Outlier Đăng ký thi PC | `portal_exam.css` 1.561 dòng, 111 `font-size` px, 24 `!important` | H10a/b |

Số liệu B4–B10 chi tiết: `docs/ba-component-spec-proposal.pdf` (cột Hiện trạng từng dòng).

### C. Issue List (5 Ready for Dev — `issue_queue.py --dev` 02/10)

| STT | ID | Sev | Gốc kỹ thuật (đọc source 02/10) | Dấu vết git |
|---|---|---|---|---|
| 155 | WJ-ORD-031 | Medium | SP công khai Portal thiếu danh mục Portal → mất khi lọc | chưa có |
| 62 | WJ-PH-003 | Medium | BA đổi yêu cầu 01/10: Lịch sử phải gồm đơn **Đã hủy**; `SALE_STATE_META` (`portal_base/controllers/utils.py`) đang loại `cancel`. ⚠ Owner trên sheet = BA/Tester | commit cũ theo yêu cầu cũ |
| 154 | WJ-ORD-030 | High | `wujia.order.window.area_id` M2O → cần M2M + migration; điểm vào `wujia_order_window/models/{wujia_order_window,res_config_settings,sale_order}.py` | chưa có |
| 152 | WJ-PORTAL-SCOPE-001 | High | `get_active_franchise_ids_filter()` `portal_base/controllers/portal.py:78` trả MỌI cửa hàng khi chưa chọn; gọi từ 9 module (có inspection) | chưa có |
| 153 | WJ-PORTAL-ROLE-001 | High | `get_max_role_in_franchises()` `:89` lấy role cao nhất trên mọi cửa hàng, không theo cửa hàng đang chọn | chưa có |

Luật BA 01/10: dữ liệu chỉ theo **một** cửa hàng đang chọn; quyền theo **role tại cửa hàng đó**.

---

## 2. Lộ trình

```
I0 push+deploy top bar (tay) ─► I1 #155 ─► I2 #62 ─► I3 #154 ─► I4a #152 ─► I4b #152 ─► I5 #153 ─► ★IR
                                                                                              │
H-A (không cần BA): H0 công cụ ─► H1 code chết ─► H2 StatusBadge sót ─► H3 CSS trang ─► ★HR-1 ◄┘
                                                                                     │ (+ BA trả kết quả duyệt spec)
H-B (sau BA duyệt):  H4 EmptyState ─► H4b Badge ─► H5 DetailSummary ─► H6 InfoBanner ─► H7 StatCard
                     ─► H8 Modal ─► H9 FormField ─► H10a/b Đăng ký thi PC ─► ★HR-2
```

H-A có thể xen giữa các phiên I nếu đang chờ BA trả lời một fork của issue. Issue mới BA thêm vào sheet
luôn chen trước H (Step 2b `/wujia-start`).

| Phiên | Nội dung | Module `-u` | Rủi ro | Trạng thái |
|---|---|---|---|---|
| I0 | Push `bea5fa8` + deploy top bar 992 + đo chỉ-đọc UAT (chủ dự án làm tay) | layout, base | Thấp | ☐ |
| I1 | #155 WJ-ORD-031 danh mục Portal bắt buộc khi công khai | wujia_sale, portal_sale | Thấp | ☐ |
| I2 | #62 WJ-PH-003 Lịch sử gồm đơn Đã hủy (xác nhận Owner trước) | portal_purchase_history, portal_base | Thấp | ☐ |
| I3 | #154 WJ-ORD-030 khung giờ nhiều khu vực (M2M + migration) | order_window, portal_sale, portal_base | Cao (schema) | ☐ |
| I4a | #152 helper scope một nguồn + Home · Giao hàng · Báo cáo (+ export) | base, delivery, report | Cao | ☐ |
| I4b | #152 Đổi trả · Yêu cầu cập nhật · Hỗ trợ · Thông báo · Công nợ + bàn giao màn Khảo sát | return, info_request, support, notification, debt | Cao | ☐ |
| I5 | #153 role theo cửa hàng đang chọn, chặn backend + ẩn menu/nút | base, report, debt, info_request, layout (nav) | Cao | ☐ |
| **★IR** | **Review cụm I: ma trận role × store × route bằng máy + ảnh** | 0 / vá nhỏ | — | ☐ |
| H0 | `scripts/qa/wj_cmp_audit.py` + test bánh cóc (họ legacy không tăng) | layout (test) | Thấp | ☐ |
| H1 | Dọn code chết B1 | layout | Thấp | ☐ |
| H2 | StatusBadge sót B2 + mở guard ra mọi module portal | return, info_request, base (test) | Thấp | ☐ |
| H3 | Dời ~800 dòng CSS trang khỏi `_components.css` | layout, base, sale | TB | ☐ |
| H-SPEC | Đề xuất spec 7 dòng gửi BA | 0 | — | ✅ 02/10 — `docs/ba-component-spec-proposal.pdf` (chờ BA) |
| **★HR-1** | **Review H0–H3 + nhận kết quả BA duyệt** | 0 / vá nhỏ | — | ☐ |
| H4 | EmptyState `CMP-ES-001` | layout + 11 module màn | TB | ☐ |
| H4b | Badge `CMP-TAG-001` | layout, notification, knowledge, support, base | Thấp | ☐ |
| H5 | DetailSummary + KeyValue `CMP-DS-001` | layout + 8 module màn | TB | ☐ |
| H6 | InfoBanner `CMP-IB-001` | layout, sale, return, base, debt, exam, info_request | TB | ☐ |
| H7 | StatCard `CMP-KPI-001` | layout, base, report, debt | TB | ☐ |
| H8 | Modal `CMP-MD-001` (nếu BA đưa vào danh mục) | layout, sale, debt, exam, info_request | TB | ☐ |
| H9 | FormField `CMP-FF-001` (nếu BA đưa vào) | layout, support, return, info_request, exam | TB | ☐ |
| H10a/b | Đăng ký thi PC hội tụ về component (giảm `portal_exam.css`) | exam | TB | ☐ |
| **★HR-2** | **Review cuối cụm H + chapter `.tex` + PDF chuẩn component v1.1** | 0 / vá nhỏ | — | ☐ |

**Không làm** (ghi lý do để phiên sau không mở lại):
- Tách `wujia_ui_core` — ADR-027: chỉ tách khi ≥2 kênh cần; hiện chỉ portal dùng.
- Gộp markup PC/mobile vào một khối — khác cấu trúc thật (table vs ListCard), BA đã chốt hai khối.
- Tự ghi spec lên Google Sheet — luật §12; BA dán từ `ba-component-spec-proposal.xlsx`.
- Sửa màn Khảo sát cho khớp chuẩn — gửi `portal-component-standard.pdf`, nhóm đó tự chỉnh.

---

## 3. Prompt từng phiên

Dán **sau `/wujia-start`**. Áp cho MỌI phiên (prompt không nhắc lại):
- Đầu phiên: `git pull` · `issue_queue.py --dev` (issue mới chen trước) · reconcile `git log --all -S"<ID>"`.
- Test luôn kèm `-u`; `wj_measure.py` trước/sau (5 khổ) + ảnh; `check_layers.py` 0 vi phạm mới; test đột biến
  (mutation) cho luật mới; sửa asset ⇒ bump version + `?v=`.
- Phiên issue: đối chiếu cột "Kết quả mong muốn" ≥90% ⇒ `docs/qa-issue-ledger.yaml` + `qa_sync.py --dry-run`
  → `--apply`; tối đa `Ready for Retest`.
- Chưa được yêu cầu thì không commit/push/deploy. Kết thúc: mục `docs/f-progress.md` + ✅ bảng §2 + §5 compact summary.

### Prompt I0 — (tay chủ dự án) push + deploy top bar

```text
Không cần phiên Claude. Chủ dự án: git push (3 commit, gồm bea5fa8) → deploy UAT
-u wujia_portal_layout,wujia_portal_base → mở /portal ở 992, 1024, 1199 xem top bar không vỡ.
Xong báo phiên I1 "I0 đã deploy" để ghi ✅.
```

### Prompt I1 — #155 WJ-ORD-031

```text
Làm phiên I1 (docs/next-session-clusters-H.md §1.C). Issue STT 155 WJ-ORD-031.
Đọc nguyên dòng issue trên sheet (Kết quả mong muốn, Acceptance) trước khi code.
1. wujia_sale: chặn bật "công khai Portal" khi sản phẩm chưa có danh mục Portal (constraint ở model,
   thông báo tiếng Việt rõ); không tự gán danh mục cho dữ liệu cũ.
2. wujia_portal_sale: domain list/chi tiết/tìm/giỏ chỉ lấy SP công khai CÓ danh mục — một nguồn domain.
3. Báo cáo dữ liệu UAT chỉ-đọc: danh sách SP đang công khai mà thiếu danh mục (gửi BA xử lý dữ liệu).
Dừng hỏi nếu: SP thiếu danh mục đang nằm trong giỏ/đơn nháp của cửa hàng (xử lý ra sao).
Nghiệm thu: test model + controller, đo /portal/order "Tất cả" = tổng các danh mục.
```

### Prompt I2 — #62 WJ-PH-003

```text
Làm phiên I2. Issue STT 62 WJ-PH-003 — BA đổi yêu cầu 01/10 (Lịch sử phải gồm đơn Đã hủy).
TRƯỚC KHI CODE: sheet ghi Owner=BA/Tester ⇒ hỏi chủ dự án xác nhận Dev nhận issue này.
1. Đọc commit cũ của WJ-PH-003 (git log --all -S"WJ-PH-003") — đang làm theo yêu cầu cũ, đối chiếu lại.
2. SALE_STATE_META (portal_base/controllers/utils.py) + domain Lịch sử: thêm trạng thái Đã hủy
   (StatusBadge neutral/danger theo bảng BA), filter chip/select "Đã hủy", mở được chi tiết đơn hủy.
3. Giữ kiểm current store; Home dùng chung SALE_STATE_META ⇒ kiểm Home không hiện đơn hủy nếu BA không yêu cầu.
Nghiệm thu: test đếm theo trạng thái, đơn hủy store khác → 404/redirect.
```

### Prompt I3 — #154 WJ-ORD-030

```text
Làm phiên I3. Issue STT 154 WJ-ORD-030 (schema — rủi ro cao).
1. wujia_order_window: area_id (M2O) → area_ids (M2M res.area). Migration pre/post trong module:
   mỗi bản ghi cũ giữ đúng khu vực; KHÔNG gộp tự động các bản ghi trùng giờ (hỏi BA nếu muốn gộp).
2. _is_within_order_window / _next_order_window (res_config_settings.py) + sale_order.py: lọc theo
   area_ids; nhiều window khớp ⇒ OR (mở nếu bất kỳ window nào mở) — xác nhận luật này với dòng issue.
3. Form/list backend + mọi chỗ portal đọc area_id (portal_sale cart/controller, Home banner).
4. Banner khung giờ (Home/Đặt hàng/Giỏ) và chặn submit dùng CÙNG một kết quả.
Ghi chú đo 02/10: cùng thời điểm, PC /portal/order báo "Chưa có cấu hình thời gian đặt hàng" còn
mobile báo "Đang trong khung giờ" (hai phiên đăng nhập riêng) — tái hiện, xác định do store context hay lệch nguồn.
Dừng hỏi nếu: migration gặp area_id rỗng (window chung) — giữ là window chung hay đổi nghĩa.
Nghiệm thu: test migration trên DB copy (đếm trước/sau), test OR, đo banner = submit.
```

### Prompt I4a — #152 scope (helper + 3 màn)

```text
Làm phiên I4a. Issue STT 152 WJ-PORTAL-SCOPE-001.
Gốc: get_active_franchise_ids_filter() (portal_base/controllers/portal.py:78) trả MỌI cửa hàng truy cập
được khi chưa chọn ⇒ Home/Giao hàng/Báo cáo cộng dữ liệu nhiều cửa hàng.
1. Liệt kê toàn bộ lời gọi (9 module) thành bảng route → helper → hành vi hiện tại.
2. Luật một nguồn: chưa chọn cửa hàng ⇒ không truy vấn dữ liệu, chuyển tới chọn cửa hàng (hoặc tự chọn
   khi user chỉ có 1 cửa hàng) — xác nhận với Kết quả mong muốn của issue.
3. Áp Home, Giao hàng, Báo cáo + export.
FORK BẮT BUỘC HỎI: wujia_portal_inspection gọi cùng helper ⇒ đổi helper đổi luôn màn Khảo sát.
Phương án: (a) helper mới, màn mình chuyển dần, helper cũ giữ nguyên cho nhóm kia; (b) sửa helper cũ
+ ghi bàn giao. KHÔNG sửa code inspection.
Nghiệm thu: test user 2 cửa hàng — số liệu chỉ của store đang chọn; ID record store khác → chặn.
```

### Prompt I4b — #152 scope (màn còn lại)

```text
Làm phiên I4b (tiếp I4a, cùng luật). Đổi trả · Yêu cầu cập nhật · Hỗ trợ · Thông báo · Công nợ:
list / detail / create / cancel / tải tệp đính kèm — mỗi route kiểm ID thuộc store đang chọn.
Ghi bàn giao cho nhóm Khảo sát (route nào đổi hành vi theo helper) vào docs/, không sửa code của họ.
Nghiệm thu: ma trận route × (store đúng / store khác / chưa chọn) bằng test HTTP.
```

### Prompt I5 — #153 role theo cửa hàng đang chọn

```text
Làm phiên I5. Issue STT 153 WJ-PORTAL-ROLE-001.
Gốc: get_max_role_in_franchises() (portal_base/controllers/portal.py:89) lấy role cao nhất trên mọi cửa hàng.
1. Helper mới: role tại cửa hàng đang chọn (một nguồn, ormcache theo user+store nếu cần cho 1500 user).
2. Nhân viên bị chặn: Báo cáo + export, Công nợ / Lịch sử thanh toán (+ KPI tiền ở Home), Yêu cầu cập nhật,
   danh sách thành viên / SĐT — chặn ở backend (403/redirect) VÀ ẩn menu/nút (sidebar, bottom nav, sheet "Thêm").
3. Đối chiếu bảng quyền trong issue (CT-050–060, POR-061) từng dòng.
Fork hỏi: inspection gọi helper cũ — như I4a.
Nghiệm thu: ma trận role (owner/manager/staff) × store × route; menu khớp quyền backend.
```

### Prompt ★IR — Review cụm I

```text
Review cụm I (I1–I5). KHÔNG làm tính năng mới.
1. Ma trận role × store × route bằng test HTTP + ảnh 2 khổ trên DB copy giống UAT; đo UAT chỉ-đọc sau deploy.
2. Rà diff toàn cụm: code thừa, comment sử ký, bump version/?v= sót, chạm nhầm module anh Thái.
3. Lỗi nhỏ <30 dòng ⇒ sửa; lớn hơn ⇒ ghi nợ. Ghi docs/i-review.md + ledger đủ 5 issue ở Ready for Retest.
```

### Prompt H0 — Công cụ kiểm kê + bánh cóc

```text
Làm phiên H0 (docs/next-session-clusters-H.md §1.B).
1. scripts/qa/wj_cmp_audit.py: đếm t-call component + họ class legacy (B4–B10) theo module, bằng lxml
   trên views/*.xml (không grep trần), bỏ module anh Thái. Số ra khớp §1.B (±5%, lệch thì sửa doc).
2. Test bánh cóc ở wujia_portal_layout: bảng mức trần từng họ legacy = số hiện tại; vượt ⇒ fail
   (chặn thêm chỗ mới trong lúc chờ H4–H9). Mỗi phiên H hạ trần họ vừa dọn.
Nghiệm thu: test xanh; thêm 1 class legacy giả ⇒ đỏ (mutation).
```

### Prompt H1 — Code chết

```text
Làm phiên H1. Xoá: CSS .wujia-btn (0 dùng), khối Legacy wujia-content-card-table:not(.wj-data-table),
rule UI-13 nếu 0 dùng (đếm bằng wj_cmp_audit + grep JS). Template wj_button/wj_icon_button 0 call:
HỎI chủ dự án giữ (tài liệu chuẩn đang ghi "hợp đồng ở class") hay xoá.
Nghiệm thu: wj_measure --diff 0 lệch pixel 5 khổ; css_owner không còn nhóm mồ côi.
```

### Prompt H2 — StatusBadge sót

```text
Làm phiên H2. Trạng thái bù hàng (Đổi trả list+detail), trạng thái + ưu tiên Yêu cầu cập nhật
(list+detail, có Bootstrap badge) → .wj-status-badge qua status_badge/status_badge_for; nhãn mới thêm
vào bảng map một nguồn. Mở test_audited_screens_have_no_legacy_status_badge_left ra mọi module portal
của mình, giữ loại trừ BA: Role/Area/Code/loại thông báo/nhãn bài Kiến thức (chờ CMP-TAG-001).
Ưu tiên "Khẩn": giữ nguyên tới khi BA trả Q-TAG-1.
```

### Prompt H3 — CSS trang ra khỏi `_components.css`

```text
Làm phiên H3. _components.css dòng ~988–1798: Home → wujia_portal_base, kết quả gửi đơn → wujia_portal_sale,
header mobile + bottom nav → file shell riêng trong layout. Dùng scripts/qa/css_move (apply.py/cdiff.py)
như F2/F3; giữ thứ tự nạp asset; css_owner --layout-domain 0 nhóm màn ở layout.
Nghiệm thu: wj_measure --diff 0 lệch 5 khổ + ảnh từng route.
```

### Prompt ★HR-1 — Review H-A + kết quả BA

```text
Review H0–H3 (máy + ảnh, như ★ cụm F). Thu kết quả BA duyệt 7 dòng ba-component-spec-proposal:
dòng nào BA Confirmed, câu hỏi CẦN BA CHỐT nào đã có trả lời ⇒ cập nhật bảng §2 (H4–H9 mở được chưa).
Dòng BA chưa duyệt ⇒ phiên tương ứng chờ; không làm theo đề xuất Dev khi BA chưa chốt.
```

### Prompt H4–H9 — Component theo spec BA (dùng chung, thay `<CMP>`)

```text
Làm phiên <Hx> — <CMP> theo spec BA đã Confirmed trên tab UI Component (đọc bản trên sheet, KHÔNG
dùng bản đề xuất Dev nếu BA đã sửa).
1. Template/class ở wujia_portal_layout (doc-comment đầu file như wj_*.xml hiện có) + test hợp đồng dáng.
2. Inventory trước (wj_cmp_audit) → chuyển call site từng module theo mục "Màn hình áp dụng" → inventory sau = 0 họ cũ.
3. Hạ trần bánh cóc; mỗi Acceptance trong spec ↔ một số đo máy hoặc test.
4. Cập nhật docs/portal-component-standard.tex (mục "Chưa có chuẩn" → mục component mới), build lại PDF.
Dừng hỏi nếu: spec BA mâu thuẫn spec đã chốt (SB/PC/FB/LC) hoặc màn trong mapping là của nhóm Khảo sát.
```

### Prompt H10a/b — Đăng ký thi PC

```text
Làm phiên H10a (H10b tiếp). portal_exam.css 1.561 dòng: thay khối tự dựng bằng component đã chuẩn
(SurfaceCard, CardHeader, DataList, FilterBar, FormField, Modal, InfoBanner, DetailSummary);
mục tiêu bỏ ≥50% font-size px và mọi !important không cần. Không đổi luồng đăng ký, giới hạn, phiếu.
Nghiệm thu: test luồng đăng ký xanh; wj_measure + ảnh 5 khổ, lệch có chủ đích ghi trong ma trận.
```

### Prompt ★HR-2 — Review cuối cụm H

```text
Review toàn cụm H (máy + ảnh mọi route 2 khổ). wj_cmp_audit: họ legacy = 0 (trừ loại trừ BA).
Viết chapter docs/chapters/<số>-sprint<n>-cluster-h-components.tex + build-doc.sh; cập nhật
portal-component-standard.tex lên v1.1 (bỏ mục "Chưa có chuẩn"), build PDF gửi lại nhóm dev khác.
```
