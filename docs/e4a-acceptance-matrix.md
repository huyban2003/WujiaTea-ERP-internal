# E4a — Nghiệm thu FilterBar `CMP-FB-001` (`UI-FILTER-001`, STT 139)

Lượt **E4a** = kiểm kê FB-10 + dựng component `wj_filter_bar` + migrate **đúng 2 route mẫu BA**.
Issue **CHƯA đóng** (đóng ở E4c), **không** chạy `qa_sync.py`, **không** đổi trạng thái sheet.

- Cây mã trước lượt: `018cf6c` · đo ngày 17/09/2026.
- DB copy cô lập **`wujia_tea_e4a`** (clone `wujia_tea_mt4`, **có** 2 module Khảo sát như UAT, chép cả
  `data/filestore/`), cổng **8096/8097**; test chạy cổng **8102/8103**. Không đụng `wujia_tea_19`/8019.
- **Run đối chứng**: worktree `scratchpad/e4/base_e4a` @ `018cf6c` + DB `wujia_tea_e4abase`, cổng
  **8098/8101** — mọi số "trước" trong bảng lấy từ đây, không suy đoán.
- Đo bằng **`em.hcm` / `wujia@test123`** (không dùng `admin`), `--scope body`.
- Khổ đo: PC **1440×900 · 1024×768 · 992 · 991** · mobile **430 · 391×844 · 360×800**.

## 1. Bảng nghiệm thu

| # | Yêu cầu (nguồn) | Đo được | Kết luận |
|---|---|---|---|
| 1 | Kiểm kê FB-10 **trước khi sửa byte nào**, đếm theo cấu trúc `lxml` | `scratchpad/e4/e4_inventory.py` → **24 form GET / 21 thanh lọc thật** / 12 màn, ghi `docs/e4-filter-inventory.md` (bảng từng `name`·kiểu·nhãn·chip·submit·reset) | **Pass** |
| 2 | Có **một** component chung, gom 2 seam (PC `.wj-pc-filterbar` + mobile `.wj-filter-card`) | `custom/wujia_portal_layout/views/wj_filter_bar.xml` — 1 template, `fb_platform='pc'|'m'`, 3 call site dùng nó (history PC, delivery mobile, gallery) | **Pass** |
| 3 | FB-02 PC: control **42** đồng cao, cùng baseline | history 1440: `q`/`date_from`/`date_to`/`state` = **42/42/42/42**, `top` = 183 cả 4 → 1 baseline; card **88** r16 pad 22/20 (đúng mẫu BA) | **Pass** |
| 4 | FB-02 PC: wrap **theo nhóm**, không tràn ngang | ≥1200 phải 1 hàng — harness assert cứng; 1440 = 1 hàng (88). 1024/992 = 142 (2 hàng) **y như trước lượt** (run đối chứng: before cũng 142) | **Pass** |
| 5 | FB-02 nhãn: submit **“Tìm kiếm”**, reset hiện có → **“Xóa lọc”** | history: `Tìm` → **`Tìm kiếm`** (w 64→123), `Reset` → **`Xóa lọc`** | **Pass** |
| 6 | FB-02/FB-03: **không thêm reset** vào màn chưa có | delivery mobile: `reset = None` trước và sau; component chỉ render reset khi `fb_reset_url` **và** platform `pc` (test `test_mobile_khong_co_reset_du_truyen_reset_url`) | **Pass** |
| 7 | FB-03 mobile: card **r14 / p12 / g8** | delivery 360/391/430/991: `r=14 pad=12/12 gap=8` — **không đổi** trước/sau (token `<992` sẵn có, không sửa) | **Pass** |
| 8 | FB-03 mobile: ô lọc **visual 38** | delivery 391: `q` 44 → **38**; `date_from`/`date_to` 18 (input trần, không có hộp) → **38** (nay có hộp `__box`) | **Pass** |
| 9 | FB-04: vùng chạm **≥44×44** (đo hộp chạm, không đo hộp nhìn thấy) | 3 ô đo `hit.h = 44` (wrapper `<label>` `--hit`); nút tìm icon-only: hộp nhìn **38×38**, `::before` **44×44** | **Pass** |
| 10 | FB-04: nút icon-only có **accessible name** | delivery mobile: `aria-label` `None` → **“Tìm kiếm”** ở cả 4 khổ; `scripts/qa/wj_formcontrol.py` @391: **2 finding → 1** (cái còn lại là history mobile — chưa migrate, E4b) | **Pass** |
| 11 | FB-04: Enter ≡ bấm nút | `<button type="submit">` trong `<form method="get">` (không JS chặn) — Enter trong input submit đúng form đó; test `test_form_luon_la_get_va_giu_action_cua_man` | **Pass** |
| 12 | FB-05: nhãn ngày **phân biệt được kể cả khi đã chọn** | nhãn chữ **trong** pill: `Từ` / `Đến` (`.wj-filter-date__label`) + `aria-label` “Từ ngày” / “Đến ngày” — không biến mất khi có giá trị | **Pass** |
| 13 | FB-06: chip **32**, không đổi | delivery mobile: **4 chip**, cao **32** trước và sau; markup chip vẫn do part `mchips` render (slot thô) | **Pass** |
| 14 | FB-07: giữ **URL / query / AJAX** — FB-10 “không thêm/bớt điều kiện PC↔mobile” | so **từng param một** trên 14 ô route×khổ: **14/14 giống hệt**. history PC `page_size,q,date_from,date_to,state`; delivery m `bs,q,date_from,date_to` | **Pass** |
| 15 | WJ-PH-008: hidden `page_size` còn trong form | history PC: `page_size` có trong `params` ở cả 4 khổ PC; test `test_pc_lich_su_dat_hang_goi_component_va_giu_page_size` | **Pass** |
| 16 | Delivery: `id="wj-dlv-mform"` + hidden `bs` **luôn render kể cả rỗng** | `bs` xuất hiện trong `params` ở cả 4 khổ mobile dù đang rỗng; test chặn cả việc thêm `t-if` vào input đó | **Pass** |
| 17 | Gỡ hết **inline style** ở thanh lọc | 0 `@style` trong 3 call site (history / delivery / `pc_preview`) — test `test_khong_con_inline_style_o_thanh_loc_hai_man_mau`; bề rộng nay bằng lớp (`flex 200/158/190`) | **Pass** |
| 18 | Gallery `pc_preview` không là **nguồn dáng thứ hai** | `pc_preview.xml` gọi chính component; 0 node `wj-pc-filter-control` tự dựng. Đo @1440/1024: 0 tràn, 0 lỗi JS | **Pass** |
| 19 | Không hex cứng, dùng token | khối CSS mới chỉ dùng `var(--wujia-*)` / `var(--wj-pc-*)`; test `test_control_pc_cao_42_bang_token_chung` assert `height: var(--wj-pc-input-h)` **và** `assertNotIn('#')` | **Pass** |
| 20 | Màn **chưa** migrate không đổi một pixel | history **mobile** và delivery **PC** ở mọi khổ: shell/h, control, chip, submit, reset **giống hệt** run đối chứng | **Pass** |
| 21 | `-u` sạch | `-u wujia_portal_layout,wujia_portal_purchase_history,wujia_portal_delivery --stop-after-init` RC=0, 0 ERROR mới (xem LIMIT-2) | **Pass** |
| 22 | Hồi quy `wj_measure --diff` ≥13 route × 5 khổ | 13 route × 5 khổ: **0 tràn ngang · 0 lỗi JS · 0 HIERARCHY · “ô mất record: 0”**; 5 redirect im lặng **có sẵn** ở cả run đối chứng | **Pass** |
| 23 | Mẫu đo khác 0 | 7 ô (bar×khổ) **đã migrate** đo được, 0 vi phạm; 0 control = coi là sai `--scope`, không phải Pass (assert trong harness) | **Pass** |
| 24 | Test mới **mutation-proof** | `custom/wujia_portal_layout/tests/test_e4_filter_bar.py` — **27 test**, suite tổng `0 failed / 520`; sweep `scratchpad/e4/e4a_mutations.py` **21 mũi**, mỗi mũi `assert s != before`, mỗi mũi đỏ **đúng test của nó** (§2; 2 guard chứng-minh-rỗng lộ ra đã vá bằng test mới) | **Pass** |
| 25 | Không đụng module Khảo sát | 0 byte thay đổi trong `wujia_portal_inspection` / `wujia_franchise_inspection`; không xoá họ class nào của chúng (lượt này không xoá CSS cũ — E4b/E4c mới gom) | **defer đúng luật** |
| 26 | Bump version + `?v=` | `wujia_portal_layout` 19.0.50.0.0→**51.0.0**, `..._purchase_history` 3.11.0→**3.12.0**, `..._delivery` 3.13.0→**3.14.0**; `_components.css` + `_pc_components.css` `?v=1292`→**1293** | **Pass** |

**26/26 tiêu chí đạt** (1 dòng là `defer` theo luật 08/09) → **100%**, trên ngưỡng ≥90%.

## 2. Mutation sweep — 21 mũi

| Mũi | Phá gì | Tệp | Test đỏ | Kết quả |
|---|---|---|---|---|
| M1 | vỏ PC thành vỏ mobile | `template` | `test_pc_dung_vo_filterbar_va_mobile_dung_vo_surface_card` | ✅ đỏ đúng 1 test |
| M2 | form POST | `template` | `test_form_luon_la_get_va_giu_action_cua_man` | ✅ đỏ đúng 1 test |
| M3 | nhãn submit về "Tìm" | `template` | `test_pc_nhan_submit_la_tim_kiem_va_reset_la_xoa_loc` | ✅ đỏ đúng 1 test |
| M4 | reset lọt xuống mobile | `template` | `test_mobile_khong_co_reset_ca_khi_man_khong_co_o_tim` | ✅ đỏ đúng 1 test |
| M4b | hàng hành động lọt xuống mobile có ô tìm | `template` | `test_mobile_co_o_tim_thi_khong_them_hang_hanh_dong` | ✅ đỏ đúng 1 test |
| M5 | bỏ wrapper chạm của ô search | `template` | `test_o_tim_boc_trong_label_de_vung_cham_44_khong_no_hop_38` | ✅ đỏ đúng 1 test |
| M6 | nút tìm mobile mất accessible name | `template` | `test_nut_tim_icon_only_cua_mobile_co_ten_doc_duoc` | ✅ đỏ đúng 1 test |
| M7 | nhãn ngày chỉ còn aria (ẩn chữ trong ô) | `template` | `test_o_ngay_co_nhan_chu_doc_duoc_ca_khi_da_chon_gia_tri` | ✅ đỏ đúng 1 test |
| M8 | aria ngày mất phân biệt | `template` | `test_o_ngay_co_aria_label_phan_biet` | ✅ đỏ đúng 1 test |
| M9 | kẹp min/max luôn bật | `template` | `test_chi_kep_min_max_khi_man_yeu_cau` | ✅ đỏ đúng 1 test |
| M10 | select mất giá trị đang chọn | `template` | `test_select_giu_gia_tri_dang_chon_va_dong_tat_ca` | ✅ đỏ đúng 1 test |
| M11 | select tự submit mọi nơi | `template` | `test_select_chi_tu_submit_khi_man_yeu_cau` | ✅ đỏ đúng 1 test |
| M12 | slot thô bị chặn | `template` | `test_slot_tho_hidden_chips_error_giu_nguyen_markup_cua_man` | ✅ đỏ đúng 1 test |
| M13 | lịch sử rơi hidden page_size | `history` | `test_pc_lich_su_dat_hang_goi_component_va_giu_page_size` | ✅ đỏ đúng 1 test |
| M14 | giao hàng chỉ render bs khi có giá trị | `delivery` | `test_mobile_giao_hang_goi_component_giu_id_va_hidden_bs` | ✅ đỏ đúng 1 test |
| M15 | gallery dựng lại thanh lọc tay | `pc_preview` | `test_gallery_pc_preview_khong_la_nguon_dang_thu_hai` | ✅ đỏ đúng 1 test |
| M16 | inline style quay lại call site | `history` | `test_khong_con_inline_style_o_thanh_loc_hai_man_mau` | ✅ đỏ đúng 1 test |
| M17 | hộp nhìn thấy phình 44 | `_components.css` | `test_hop_nhin_thay_38_va_vung_cham_44` | ✅ đỏ đúng 1 test |
| M18 | vùng chạm nút tìm co về 38 | `_components.css` | `test_nut_tim_38_co_vung_cham_44_bang_pseudo` | ✅ đỏ đúng 1 test |
| M19 | gap hàng lọc mobile về 10 | `_components.css` | `test_gap_hang_loc_mobile_la_8` | ✅ đỏ đúng 1 test |
| M20 | control PC hard-code hex thay token | `_pc_components.css` | `test_control_pc_cao_42_bang_token_chung` | ✅ đỏ đúng 1 test |

**21/21 mũi đỏ đúng một test của nó.** Harness `scratchpad/e4/e4a_mutations.py`: mỗi mũi
`assert s != before` trước khi chạy (bẫy D6c M5 — mũi rỗng thì "pass" là giả).

Hai mũi lộ ra **guard chứng-minh-rỗng**, đã vá bằng test mới thay vì hạ chuẩn:
- **M4** (bỏ `and _fb_pc` ở link reset) ban đầu **không đỏ test nào**: ở mobile *có* ô tìm, hàng hành
  động vốn đã không render nên test cũ không cảm nhận được. Thêm
  `test_mobile_khong_co_reset_ca_khi_man_khong_co_o_tim` (mobile **không** ô tìm) mới khoá được.
- **M4b** (bỏ điều kiện của cả hàng hành động) cũng im: thêm
  `test_mobile_co_o_tim_thi_khong_them_hang_hanh_dong` — mobile đã có nút kính lúp thì **không** được
  mọc hàng nút thứ hai (FB-03).

Suite sau khi hoàn nguyên: **`0 failed, 0 error(s) of 520 tests`** (E3 để lại 493 + **27** test mới).

## 3. LIMIT / ghi chú bàn giao

- **LIMIT-1** — lượt này chỉ **2 route mẫu + gallery**. 19 thanh lọc còn lại vẫn dùng markup cũ và
  **vẫn giữ hình học 44 của D6c**; CSS mới chỉ chạm markup của component (`__box`, `--hit`,
  `label.wj-filter-search-field`, `selectwrap`) nên màn cũ không đổi pixel nào. E4b phủ hết.
- **LIMIT-2** — để `-u` chạy được trên DB test phải thêm **`wujia_sale`** vào danh sách
  (`wujia_tea_mt4` còn `wujia_sale` 19.0.4.4.0, repo 19.0.4.6.0 → `column sl.is_export does not exist`).
  Đây là **lệch template sẵn có, không do E4a** — **không** thuộc danh sách deploy.
- **LIMIT-3** — 10 dòng `ERROR ... Model wujia.franchise.revenue.compute.wizard has no table` và 5
  redirect im lặng khi đo: **có sẵn** trên run đối chứng `018cf6c`.
- **LIMIT-4** — wiring ngày (`date_from > date_to` → báo lỗi cạnh ô), `type="text"` của màn Thi, và
  guard chống thêm/bớt điều kiện là **E4c** theo phân lượt chốt 16/09.
- Ảnh trước/sau 2 màn mẫu: `scratchpad/e4/shots-before/` · `scratchpad/e4/shots-after/` (cùng
  viewport/role/URL) — E4c bàn giao BA.
- Sửa kèm hạ tầng đo: `scripts/qa/wj_formcontrol.py` trước đây tự điền form `/web/login` (theme Vuexy
  ẩn form đó ⇒ treo 30s rồi báo sai); nay dùng `login()` của `wj_measure.py`.
- **Lệnh deploy để E4c gộp**:
  `-u wujia_portal_layout,wujia_portal_purchase_history,wujia_portal_delivery`
