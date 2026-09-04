# D3 — Kiểm kê & phân loại heading TRONG CARD (`UI-CARDHEADER-001`, STT 125)

**Ngày:** 2026-08-27 · **Branch:** `dev/2026-08-27-d3a` · **Cơ sở:** `9fd35de`

Bước 1 của cụm D3 theo spec `CMP-CH-001` (tab `UI Component` gid 488333015, dòng 34). Chân lý
phân loại vẫn là **ngữ cảnh DOM (tổ tiên)**, không phải tên class — y hệt C8, kiểm kê bằng lxml
đi ngược cây tìm ancestor là **card thật**.

**"Là card"** = có class nào đó khai trong CSS đủ cả ba: `background` + `border*` + `padding`.
Đây đúng phép thử C8 đã dùng để hạ `portal_home.xml:292` xuống CardHeader và giữ
`.wujia-mdash-sec` là SectionHeader.

**Khác C8 một điểm quan trọng:** C8 chỉ quét `h1..h6` (+5 chỗ `div>span` giả heading). D3 phải
quét **cả `<p>/<span>/<div>` đang đóng vai tiêu đề card** — chính là ca BA nêu đích danh trong
issue (*"Form bù hàng mobile dùng `wujia-mdash-title` 18px nhưng markup là thẻ P"*).

---

## 1. Phạm vi

`custom/wujia_portal_*/views/*.xml` + `templates/*.xml`. Loại trừ trước khi phân loại:

| Loại trừ | Lý do |
|---|---|
| `*_backend_views.xml` | Backend Odoo, không phải portal |
| `wujia_portal_layout/views/pc_preview.xml` | Trang demo nội bộ |
| `login_page` · `forgot_pass` · `change_password_page` · `profile_page` | Auth, S39 dựng riêng (giữ ranh giới C8) |
| `wj_ks_dashboard_ninja` · `wj_ks_dn_advance` | Workstream Dashboard riêng (`dashboard-migration-plan.md`) |
| `wujia_portal_remediation` | Code đã xoá (`f789a56`), UAT `uninstalled` |

**Loại trừ theo VAI TRÒ** (91 chỗ) — không phải tiêu đề của card mà là nội dung/nhãn trong thân
card, hoặc thuộc component khác: `*__label` / `form-label` / `*-kv-*` (cặp nhãn–giá trị) ·
`*empty*` / `*modal*` (thuộc `CMP-ES-001` và spec modal, BA chưa viết) · `*-row` / `*-item` /
`*-line` (tiêu đề MỘT bản ghi trong danh sách ⇒ việc của `CMP-DL-001`, cụm D5) · `*chip` /
`*badge` / `*nav-*` · `wj-page-header*` / `wj-section-header*` (**component đã chuẩn hoá xong**
ở B3a/B3b và C8a/C8b — không đụng lại) · `*-link` / `*__actions` (slot phải, không phải title).

## 2. Kết quả

| | Số |
|---|---:|
| Ứng viên tiêu đề nằm trong card | 218 |
| − loại theo vai trò (§1) | 91 |
| **= CardHeader (máy)** | **127** |
| − loại bằng soi tay (§3) | 23 |
| **= call site trong scope D3** | **104** |
| ↳ gộp 1 chỗ subtitle vào header cùng card (§4) | **103 call site thật** |

Trong 127 chỗ máy nhận: **96 là heading thật**, **31 là giả heading** (`<p>` / `<span>` /
`<div>` có chữ trực tiếp) — con số 31 này chính là triệu chứng BA mô tả.

Chia theo vị trí trong card:

| | Số | Nghĩa |
|---|---:|---|
| **A. Đầu card** | 112 | Là header của chính card đó |
| **B. Giữa card** | 15 | Tiêu đề khối con nằm sâu trong card |

> ⚠️ **Không lấy "phải ở đầu card" làm điều kiện loại.** Ranh giới spec chỉ có hai vế: trong
> card ⇒ CardHeader, ngoài card ⇒ SectionHeader. Bản kiểm kê đầu tiên của phiên này đã lỡ dùng
> "phải là con đầu tiên" và **rơi mất 31 chỗ hợp lệ**, trong đó có
> `wj-pc-acct-headcard__title` (nằm trong wrapper `__main`, sau `__icon`). Vị trí A/B chỉ dùng
> để **xếp thứ tự migrate**, không dùng để loại.

## 3. Loại bằng soi tay (23 chỗ)

| File · dòng | Hiện trạng | Vì sao KHÔNG phải CardHeader |
|---|---|---|
| `portal_franchises_in_layout.xml:106` · `portal_templates.xml:108` | `h4/h5.card-title` | Route legacy `/my/franchises` — ADR-004 đã thay bằng portal Vuexy (C8 cũng loại) |
| `layouts.xml:187` | `span.menu-title` | Nhãn sidebar — thuộc `UI-SIDEBAR-001` (lứa D7) |
| `mobile_bottomnav.xml:58` | `div.wujia-msheet-title` | Bottom sheet là overlay, không phải SurfaceCard |
| `header_bell_inherit.xml:22` | `h4.wj-pc-noti-popup__title` | Popup chuông là dropdown, không phải card trong trang |
| `portal_delivery.xml:118, 126` | `h3.wj-pc-dlv-inner__title` | Empty / error state ⇒ `CMP-ES-001` |
| `portal_franchise_information.xml:267` | `h4` trong `.card-body` | Trạng thái khoá cửa hàng ⇒ `CMP-ES-001` |
| `portal_inspection_success_templates.xml:13` | `h2` | Màn kết quả gửi — hero của trang, không phải header card |
| `portal_order_cart.xml:196` | `p.wujia-msubmit-title` | Overlay "Đang tạo đơn…" (S40), không phải card |
| `portal_order_catalog.xml:350` | `span.wujia-morder-floatbar-title` | Thanh giỏ nổi, không phải card |
| `portal_exam.xml:279` | `div.wj-exam-pc-cal__head` | Chỉ có nút `‹ ›`, **không có title** ⇒ không có gì để chuẩn hoá |
| `portal_exam.xml:378` · `portal_history.xml:395` | `__side` / `__right` | Là **slot phải** của header, không phải title |
| `portal_exam.xml:521, 527` | `__title` / `__droptitle` | Chữ trạng thái của vùng kéo-thả ảnh |
| `portal_franchise_information.xml:49` | `div.wj-pc-acct-headcard__box` | Là slot phải — xem **§6 Fork** |
| `portal_knowledge.xml:287, 337` | `h1` tiêu đề bài viết | **Nội dung**, không phải header card — cùng luật BA cấm dùng CardHeader cho tên sản phẩm |
| `portal_notification.xml:364, 448` | `h2` tiêu đề thông báo | ″ |
| `portal_order_product_detail.xml:34` | `h3` tên sản phẩm | ″ — BA ghi thẳng: *"Không dùng CardHeader cho tên sản phẩm"* |
| `portal_order_result.xml:25` | `h2.wujia-mres-title` | *(thêm ở D3b)* Màn kết quả gửi đơn — **hero của trang**, không phải header card; đúng tiền lệ `portal_inspection_success_templates.xml:13` ngay trên |

## 4. Map về 7 nhóm MAPPING của BA

| Nhóm BA | Call site | Nơi tiêu biểu |
|---|---:|---|
| **List/content card** | 38 | `wj-pc-card__title` (23) — danh sách thông báo/đơn/hoá đơn/chuyến · `wujia-content-card-header-title` (8) |
| **FormCard** | 27 | `card-title mb-0` + `h5/h6.mb-0` trong `.card-header` (support, return detail, franchise profile) · `wujia-mdash-title` dạng `<p>` (return form, support) |
| **Dashboard card** | 14 | `wujia-content-card-header-title` ở Home · `wujia-mhist-card-head` |
| **Summary/StatCard** | 12 | `wj-debt-summary__head` · `wj-pc-order-head__code` · `wujia-mexam-rsum-title` · report orders |
| **Cart** | 1 | `wj-pc-cart-title` "Giỏ hàng" (`pc_cart_panel.xml:12`) |
| **FilterCard** | 0 | ⚠️ **Chưa có chỗ nào** — đúng như BA viết: *"FilterCard PC/mobile hiện đưa control trực tiếp vào card, không có header"*. Đây là việc **THÊM MỚI**, không phải migrate |
| **Card nhỏ — không bắt buộc** | 12 | `wj-debt-hint__title` · `wj-exam-pc-slots__title` · `wujia-mexam-person-head`… |

**Chỗ subtitle đã gộp:** `portal_franchise_information.xml:187` (`h3.wujia-maccount-store-name`)
nằm cùng card với `:181` ⇒ là **subtitle của header đó**, không phải call site riêng ⇒ 104 → 103.

## 5. Phân bố theo file — kế hoạch chia D3b…D3n

| File | Call site | Dự kiến |
|---|---:|---|
| `wujia_portal_exam/views/portal_exam.xml` | 21 | **D3d ✅** — 14 chỗ; 3 defer chờ BA (§6), 4 đã loại §3 |
| `wujia_portal_return/views/portal_return_detail.xml` | 15 | **D3e ✅** — 15 chỗ |
| `wujia_portal_purchase_history/views/portal_history.xml` | 10 | **D3e ✅** — 9 chỗ; `:395` đã loại §3 |
| `wujia_portal_base/views/portal_franchise_information.xml` | 10 | **D3a + D3c ✅** — 2 + 4; còn `:40`/`:49` chờ BA (§6), `:290` đã loại §3 |
| `wujia_portal_delivery/views/portal_delivery.xml` | 8 | **D3a + D3c ✅** — 3 + 1; `:118`/`:126` đã loại §3 |
| `wujia_portal_notification/views/portal_notification.xml` | 7 | **D3b ✅** (5 chỗ; 2 chỗ còn lại là §3 tiêu đề thông báo) |
| `wujia_portal_support/views/portal_support.xml` | 7 | **D3a + D3c ✅** — 1 + 6 |
| `wujia_portal_knowledge/views/portal_knowledge.xml` | 7 | **D3b ✅** (5 chỗ; 2 chỗ còn lại là §3 tiêu đề bài viết) |
| `wujia_portal_base/views/portal_home.xml` | 5 | **D3b ✅** |
| `wujia_portal_debt/views/portal_debt.xml` | 5 | **D3f ✅** — 4 chỗ; `:40` actionrow đã loại §3 |
| `wujia_portal_base/views/portal_franchise_profile.xml` | 4 | **D3b ✅** |
| `wujia_portal_inspection/*` (4 file) | 9 | **D3f ✅** — 6 chỗ; `list:34` chờ BA (§6), `detail:176`→D5, `success:13/78` §3 |
| `wujia_portal_return/views/portal_return_form.xml` | 4 | **D3a (mẫu 4)** — 4 xong ✅ |
| `wujia_portal_report/views/portal_report_orders.xml` | 3 | **D3b ✅** |
| `wujia_portal_sale/*` (3 file) | 3 | **D3b ✅** (2 chỗ; `portal_order_result.xml` đã loại → §3) |
| Còn lại (`info_request`, `return_list`) | 2 | **D3b ✅** |

**D3a phủ 4 file / 29 call site** — nhưng cố ý **không migrate hết 4 file**, chỉ lấy đủ mẫu mỗi
họ markup (xem `docs/d3-acceptance-matrix.md`); phần còn lại của chính 4 file đó rơi vào **D3c**.

**Tiến độ (2026-09-04, sau D3f): 95/105.** D3a 10 · D3b 26 · D3c 11 · D3d 14 · D3e 24 · D3f 10.
**Danh sách actionable đã HẾT.** Còn lại đúng 4 chỗ defer chờ BA ở §6 + các chỗ §3.

> ⚠️ **Đính chính D3f — bug ĐẾM của chính harness, không phải của doc.**
> `d3_inventory.py` chỉ bỏ qua wrapper `t-call` tới `wj_section_header`, **thiếu
> `wj_card_header`** ⇒ mọi call site ĐÃ migrate mà giữ `div.card-header` bọc ngoài vẫn bị đếm
> lại. Chạy thô ra **53**; vá xong còn **40**. Đây là lần đầu con số sai đến từ harness chứ
> không phải doc bàn giao — **đã vá trong `scratchpad/d3_inventory.py`**, phiên sau không gặp lại.
>
> Mẫu số cũng lệch: 85 + 12 actionable + 4 defer = **101**, không phải 103. Con số 105 ở trên là
> **101 + 4 chỗ D3f phát sinh** (xem dưới).

> ⚠️ **D3f phát sinh 4 chỗ kiểm kê KHÔNG bắt được.** Head khối `t-foreach sections` của
> `portal_inspection_detail_templates.xml` có **bản mobile song sinh** (`:450`) mà phép thử
> "tổ tiên là card" của harness trượt. Lòi ra nhờ guard `_sec_sev` đếm được 4 thay vì 2. Để
> nguyên thì PC và mobile lệch nhau — đúng cái cụm D3 đang chống ⇒ đã migrate luôn.
> ⇒ **Bài học: kiểm kê là sàn, không phải trần.** Migrate xong một head thì grep tìm bản song
> sinh của nền tảng còn lại trước khi đóng.

📌 **Chủ dự án chốt (2026-09-04): hết cụm D3 sẽ có một phiên review lại toàn cụm để soát vỡ giao
diện** — chạy bằng **ảnh chụp**, không chỉ bảng số. Ba phiên liên tiếp (D3c badge trôi · D3d mất
nhịp dọc · D3e thẻ tóm tắt vỡ) đều là lỗi mà **mọi số đo vẫn Pass**.

> ⚠️ **Đính chính D3e.** Bảng trên ghi `15 / 10`; `portal_history.xml:395` là `__right` — slot
> phải, đã bị §3 loại ⇒ còn **9**. D3e làm thật **24**. Đây là **lần thứ ba liên tiếp** con số bàn
> giao bị cộng dư.

**Quyết định D3e — 4 nhãn phụ giữa thân `portal_return_detail.xml`** (`Ghi chú từ cửa hàng`,
`Lý do từ chối`, `Phản hồi từ Ngô Gia`, `Đơn bù hàng`): **migrate hết** để sửa một chỗ là sửa hết,
nhưng **trả dáng `h6` cũ bằng rule scope** trong `wujia_portal_return/.../portal_return.css` — chúng
không mở đầu card nên phải nhỏ hơn tiêu đề card, để cỡ component thì mất phân cấp. Đo được
trước = sau từng pixel. **Đừng "dọn dẹp" rule này ở phiên sau.**

**Quyết định D3e — rule vá tràn `flex`:** gom về gốc
`.wj-pc-order-head .wj-card-header__lead { flex: 0 1 auto; }` trong `_pc_components.css`; đã **xoá**
bản trùng `.wj-pc-dlv-head ...` ở `portal_delivery.css`.

> ⚠️ **Đính chính D3d.** Bàn giao D3c ghi "D3d = 21 chỗ" — cộng cả 4 dòng đã bị §3 loại
> (`:279` cal-head không title · `:378` slot phải · `:521`/`:527` chữ vùng kéo-thả). Số thật
> **17**, chủ dự án chốt defer 3 ⇒ **14 làm ở D3d**. Lỗi cộng nhầm này lặp lại **hai phiên liên
> tiếp** ⇒ quy tắc: **luôn chạy lại `d3_inventory.py`, đừng tin con số ở doc bàn giao.**

> ⚠️ **Đính chính.** Bàn giao D3b ghi "D3c = 15 chỗ (support 6 · delivery 3 ·
> franchise-information 6)". Chạy lại `d3_inventory.py` cho thấy con số đó **cộng cả dòng đã bị
> loại ở §3** (`delivery:118/126`, `franchise_information:290`) và **cả 2 chỗ đang chờ BA ở §6**
> (`franchise_information:40/49`). Số làm thật của D3c là **11**: support 6 · delivery 1 ·
> franchise-information 4. Đừng cộng cột "Call site" của bảng trên để suy ra việc còn lại —
> luôn chạy lại `scratchpad/d3_inventory.py`.

> ⚠️ Con số cột "Call site" là **tổng theo file**, gồm cả chỗ đã bị loại ở §3, nên cộng dồn
> ra 113 chứ không phải 103 — bám `scratchpad/d3_inventory.py` mới ra danh sách đúng.

## 6. Chỗ KHÔNG đụng — chờ BA (kế thừa LIMIT của C8, đừng quyết lại)

1. **`portal_delivery.xml:15` + `portal_order_catalog.xml:17`** — nằm trong `.wj-pc-card` ⇒ theo
   `CMP-CH-001` phải là CardHeader, **nhưng BA tự chỉ đích danh là SectionHeader** và C8a đã
   migrate sang `wj_section_header`. Đây là **LIMIT-2 đang treo**. Script đã tự bỏ qua wrapper
   nào chứa `t-call` tới `wj_section_header`.
2. **`portal_debt.xml:688`** "THÔNG TIN CHUYỂN KHOẢN" — nhãn 11px trong `.wj-debt-bank`
   (`height:150px` cố định). C8b dung hoà bằng `wj_section_header` + `--flush` + dáng nhãn scope
   trong `portal_debt.css`. BA **nêu lại đúng chỗ này** trong `CMP-CH-001` (*"Debt summary dùng
   label 11px viết hoa"*) ⇒ đây là **ứng viên số 1 để reclassify sang CardHeader**, nhưng phải
   chờ BA trả lời câu hỏi C8 rồi mới đổi.
3. **`portal_inspection_list_templates.xml:34`** "Danh sách phiếu khảo sát" — cùng họ với (1),
   C8b đã ghi `Need Clarification`.

**Fork mới của D3a — `wj-pc-acct-headcard` có HAI vùng phải.** `__chips` (trạng thái cửa hàng)
và `__box` (Quyền xem hiện tại), trong khi spec ghi **tối đa MỘT trailing**. D3a làm theo hướng
an toàn: **chips + box đứng ngoài CardHeader**, là nội dung card ⇒ giữ nguyên hiển thị, đúng
chữ spec, 0 rủi ro hồi quy. Đã ghi LIMIT; BA trả lời thì D3b chỉnh.
**Vẫn treo sau D3c** (`:40` + `:49`) — chờ BA, đừng tự quyết lại.

**2 fork mới của D3d (2026-09-04) — CÙNG HỌ với `wj-pc-acct-headcard`, gộp chung 1 lượt hỏi BA.**
Cả hai đều có **HAI vùng trailing** trong khi spec cho tối đa MỘT ⇒ **defer, không đụng file**:

| Chỗ | Hai trailing | Vì sao không tự quyết |
|---|---|---|
| `portal_exam.xml:375` `wj-exam-pc-parthead` | ô nhập "Ghi chú" + nút "Thêm người" | Cả hai đều là **control tương tác**, không cái nào rõ ràng là "nội dung card" như lối xử `__chips/__box` của D3a |
| `portal_exam.xml:769` `wujia-mexam-person-head` | badge "Bắt buộc" + nút xóa người | Ngoài 2-trailing, node này còn bị `portal_exam_wizard.js` `cloneNode` làm **template dựng người mới** ⇒ đổi cấu trúc = rủi ro chết im lặng cao nhất cụm D3 |

`portal_exam.xml:858` `wujia-mexam-sheet-title` **loại hẳn** theo tiền lệ §3
(`mobile_bottomnav.xml:58`): bottom-sheet overlay, không phải tiêu đề card trong trang.

### Quyết định D3f (2026-09-04) — đã làm, đừng mở lại

Chủ dự án chốt: **đang đồng bộ mọi màn về một component ⇒ migrate hết chỗ là CardHeader thật,
chấp nhận vỡ rồi vá dần**; và **khác biệt nào là DRIFT thì cho hội tụ về chuẩn chung, chỉ khác
biệt nào là THIẾT KẾ mới giữ bằng rule scope**. Áp dụng cho 10 chỗ D3f:

| Giữ bằng rule scope (THIẾT KẾ) | Cho hội tụ (DRIFT) |
|---|---|
| nhãn 11px card tổng S43 (khung 142px khoá cứng) | tiêu đề card 22/24px → **18px** chuẩn |
| nhãn hint 11.5px amber (hộp 52px) | màu `text-dark` bootstrap → token portal |
| tiêu đề tiêu chí 14px (chữ chính của hộp) | subtitle 13.125px → **14px** chuẩn |
| head section 15px PC / .95rem xanh mobile | nhịp header→body 18/21px → **12px** |

**3 chỗ loại — vì SAI COMPONENT, không phải vì sợ vỡ:** `debt:40` (hàng điều hướng có chevron
⇒ `CMP-DL-001`) · `detail:176` (tiêu đề một dòng trong `t-foreach lines` ⇒ **D5**; thêm chặn kỹ
thuật: title có `<span>` lồng mà `ch_title` là `t-out`) · `success:78` (modal overlay, mở ra thì
phải mở lại cả `mobile_bottomnav:58` + `header_bell:22` đã chốt loại từ D3a).

🔴 **Bẫy đặc hiệu tái xuất lần 2 (D3e §7).** Rule severe bản mobile viết ngắn (0,3,0) **thua**
rule màu xanh mobile (0,4,0)`!important` ngay trên nó ⇒ tiêu đề nhánh nghiêm trọng ra **màu xanh
trên nền đỏ**. Quy tắc: rule scope mới phải **đếm đặc hiệu so với chính các rule scope cùng file**,
không chỉ so với component.

### Quyết định D3 REVIEW (2026-09-04) — đã làm, đừng mở lại

Chi tiết + bằng chứng ảnh/số: `docs/d3-review-matrix.md`.

| Chỗ | Phán quyết | Lý do |
|---|---|---|
| Nhãn khối con trong card màn thi (`wj-exam-pc-sechead--sm` · `--2` · `wj-exam-pc-slots__head`) | **DRIFT → hội tụ 18px → 16px** | D3d hạ tiêu đề card 22→18 nhưng không hạ khối con theo ⇒ ba bậc sập thành một. 16px là cỡ chuẩn sẵn có của component, không đẻ số mới |
| Head danh mục khảo sát bản mobile `#0284c7` | **Lỗi a11y có sẵn → sửa `#0369a1`** | tương phản 3.74 < AA 4.5; đậm một bậc cùng hệ xanh ⇒ 5.42, giữ nguyên vai trò "xanh danh mục" |
| Nhãn phụ giữa thân card (`wj-return-sublabel`, `wj-insp-sublabel`) | **THIẾT KẾ, nhưng gom về modifier chung `wj-card-header--sublabel`** | hai bản CSS trùng tuyệt đối cho cùng một vai trò ⇒ đồng bộ ở tầng code; màu riêng vẫn ở module |
| Badge `ch_meta` 3 nhánh của khảo sát (PC + mobile) | **KHÔNG gom template con** | hai bản khác thật 4 điểm (13/12px, bo góc, padding, lớp nhánh `else`) ⇒ tham số hoá lãi không bù rủi ro; để D4 |
| Nhịp header→body 18/12/24/**36**px ở `/portal/exam/register` | **TREO — hỏi chủ dự án** | chênh lệch nằm ở `margin-top` của THÂN card, không thuộc hợp đồng `CMP-CH-001` |

🔴 **Whitelist THIẾT KẾ chỉ được chứa thứ chủ dự án đã chốt.** Trong phiên này tôi từng tự thêm một
dòng không có nguồn (`wj-exam-pc-sechead`) và nó **che mất đúng phát hiện chính**. Đã bỏ.

### 3 fork chủ dự án chốt ở D3c (2026-09-02) — đã làm, đừng mở lại

| # | Chỗ | Fork | Phán quyết |
|---|---|---|---|
| 1 | `portal_franchise_information.xml:157` `h3.wj-pc-acct-staff__title` | CardHeader hay đẩy sang `CMP-ES-001` (khối "Chế độ xem cơ bản" chỉ hiện với role staff)? | **Migrate — coi là CardHeader.** Icon + 2 dòng `__line` + tag `__tag` **ở lại ngoài header** (đúng lối xử `__chips/__box` của D3a). Dùng biến thể flush vì `__line` đã tự khai `margin-top:8px` |
| 2 | `portal_franchise_information.xml:179` + `:185` (mobile) | Giữ thứ tự cũ `h2 → badgerow → h3 tên cửa hàng`, hay đưa tên cửa hàng lên làm `ch_subtitle`? | **ĐỔI thứ tự DOM**: `[h2 + tên cửa hàng làm dòng phụ] → badgerow → p khu vực`. Lý do quyết: **bản PC của chính card đó** (`wj-pc-acct-headcard`, dòng 40–47) vốn đã xếp `title → sub → chips` ⇒ mobile khớp PC |
| 3 | `portal_delivery.xml:377–384` (PC summary head) | Badge trạng thái + 3 cặp KV bên phải — cái nào là trailing (spec cho **tối đa 1**)? | **title = mã chuyến · subtitle = "Chuyến giao cho …" · trailing = badge**; khối 3 cặp KV **ở lại là nội dung card**. Kèm 1 rule CSS scope delivery cho badge bám sát mã (`d3c-acceptance-matrix.md` §9) |

## 7. CSS chờ xoá (sau khi migrate đủ 100%)

**KHÔNG xoá ở D3a** — ràng buộc thứ tự y hệt C8a→C8b (`.wujia-mhist-listhead` dùng ở 2 file,
xoá sớm là vỡ). Danh sách phải grep ra 0 hit rồi mới xoá:

`.wujia-content-card-header*` · `.wj-pc-card__title` (+ `--sm`) · `.wujia-mdash-title` ·
`.wujia-mhist-card-head` · `.wujia-maccount-cardtitle` · `.wj-pc-acct-panel-title` ·
`.wj-pc-acct-staff__title` · `.wujia-mexam-*title` · `.wj-exam-pc-sectitle` ·
`.wj-pc-cart-title` · `.wujia-mknow-h` · `.wujia-mnoti-detail-sectitle` · `.wj-debt-summary__head`

*Thêm sau D3c:* `.wujia-maccount-store-name` · `.wj-pc-dlv-head-meta` (đã 0 hit trong view).

*Thêm sau D3e (0 hit trong view, **vẫn chưa xoá** — khoá tới 100%):* `.wujia-mhist-card-head`
(2 file cuối cùng dùng nó đều đã migrate) · `.wj-pc-order-head__code` (+ `__code-row`).

Chống tái phát bằng unit test quét `arch_db` mọi view qweb — đúng khuôn
`test_retired_heading_classes_are_gone` của C8b.

### ĐÃ XOÁ ở phiên D3 REVIEW (2026-09-04) — 17 lớp / 21 selector

Mỗi lớp đều grep ra **0 call site** trong view + template + JS (biên
`\.CLASS([^-_a-zA-Z0-9]|$)`) trước khi cắt; xoá xong chạy **semantic diff CSS**
(`scratchpad/css_semdiff.py`): **MẤT = đúng 21 selector chủ đích · THÊM = 0 · ĐỔI = 0**.

`.wujia-content-card-header` (+ `-icon`, `-title`, `-link`, `-link:hover`, `-link i`, và
`.wujia-content-card--flush > .wujia-content-card-header`) · `.wujia-mhome .wujia-mhome-section-title`
+ `.wujia-mhome .wujia-mdash-title` · `.wujia-mdash-title` · `.wujia-mhist-card-head` ·
`.wujia-mknow-h` · `.wujia-maccount-store-name` · `.wj-pc-acct-staff__title` ·
`.wj-pc-order-head__code` (+ `__code-row`) · `.wj-pc-cart-title` · `.wj-pc-dlv-head-meta` ·
`.wujia-mexam-rsum-title` · `.wujia-mnoti-detail-sectitle` · `.wj-exam-pc-sectitle--2`.

**CÒN GIỮ, đừng xoá ở phiên sau:**

| Lớp | Vì sao còn |
|---|---|
| `.wj-exam-pc-sectitle` (+ `--sm`) | còn **1 call site sống** ở `portal_exam.xml:398` ("Người tham gia" — chỗ defer chờ BA §6) |
| `.wj-pc-card__title` · `.wujia-maccount-cardtitle` · `.wj-pc-acct-panel-title` | còn call site ở các chỗ §3/§6 |
| `.wj-debt-summary__head` | 2 rule hình học Figma S43 bám vào, có test `test_debt_summary_keeps_its_head_wrapper` |

Token CSS của họ `content-card` (`--wujia-content-card-header-icon-size/-bg` ở `_variables.css`)
**vẫn dùng** cho `.wj-card-header__icon` ⇒ giữ. Riêng `--wujia-content-card-link-color` nay không còn
rule nào tham chiếu — để lại trong bảng token, không xoá kèm (ngoài phạm vi cụm D3).

Guard: `TestCardHeaderD3Review.test_dead_card_header_classes_stay_deleted`.

## 8. Cách tái lập

Script: `scratchpad/d3_inventory.py` (harness, **không** commit vào repo theo §13).
`python3 scratchpad/d3_inventory.py [--out]` — `--out` in thêm 91 chỗ bị loại theo vai trò để
kiểm chứng bộ lọc không cắt nhầm.
