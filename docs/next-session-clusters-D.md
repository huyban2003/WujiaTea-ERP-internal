# Cụm D1–D6 + R1–R5 — prompt cho từng session

**Nguồn:** phiên phân cụm 2026-08-25 (11 issue `Ready for Dev` BA đổ lên `5. Issue List`
sau ngày 24/8 — 7 issue bù hàng audit UAT 23/08 + 3 issue chuẩn hoá component + 1 issue font).
Kế hoạch đầy đủ: `~/.claude/plans/bright-conjuring-sutherland.md`; chuẩn nghiệm thu §13
`wujia-compact-summary.md`.

**Cách dùng:** `/wujia-start` → nói "làm cụm D&lt;n&gt;" → Claude đọc file này, lấy đúng khối
prompt của cụm đó rồi bắt tay.

---

## 📌 BÀN GIAO cho phiên sau (chốt 04/09/2026 — sau D3d)

**Prompt gõ vào phiên sau:**

> `/wujia-start`
> làm cụm D3e = `portal_return_detail.xml` + `portal_history.xml`. **Chạy lại
> `scratchpad/d3_inventory.py` trước khi lập kế hoạch** — con số 15/10 trong bảng §5 inventory là
> tổng theo file (gồm cả dòng đã bị §3 loại); hai phiên liên tiếp (D3c, D3d) đều cộng nhầm vì tin
> doc bàn giao. Đọc `docs/d3d-acceptance-matrix.md` §5 (bẫy specificity, đã trả giá **hai lần**)
> và §6 (JS đọc thẳng tên class tiêu đề — grep `querySelector` trong JS của module trước khi migrate).

### ✅ D3d XONG + ĐÃ DEPLOY UAT + ĐO LẠI (04/09)

Nhánh `dev/2026-09-04-d3d`. **14 call site / 1 file** (`wujia_portal_exam/views/portal_exam.xml`).
Tổng phủ **61/103**. Nghiệm thu local **21✅ + 2 phần = 95,7%** → `docs/d3d-acceptance-matrix.md`.

Đã deploy **2 lượt**: lượt 1 `-u wujia_portal_layout,wujia_portal_exam` (**19.0.5.8.0**), lượt 2
`-u wujia_portal_exam` (**19.0.5.9.0**, vá bố cục <1600px phát hiện khi đo UAT). Không module mới,
không migration, không cần bump `?v=`.

**Đo lại chỉ-đọc trên UAT sau deploy: `128/128` header đạt số BA, `0 VẤN ĐỀ`** (22 route ×
3 breakpoint). Sheet đã `qa_deploy_mark` với cảnh báo phạm vi 61/103 dẫn đầu cột P; issue **vẫn
`Ready for Dev`**, **KHÔNG** chạy `qa_sync.py`.

🔴 **Bài học lớn nhất phiên này: SỐ ĐO SẠCH VẪN CÓ THỂ ĐANG GIẤU LỖI VỠ BỐ CỤC.** Nghiệm thu local
ra 95,7% và ghi cột PC bị bóp ở ≤1440 thành "lỗi có sẵn, không phải hồi quy" — **đúng nhưng chưa
đủ**: chỉ khi đo trên UAT mới lộ tiêu đề ra **3 dòng** (spec cho tối đa 2), vì D3d nâng cỡ chữ
16→18px theo chuẩn BA đã đẩy nó qua ngưỡng. ⇒ "lỗi có sẵn" **không tự động** nghĩa là "không phải
việc của mình": phải kiểm xem thay đổi của mình có đẩy nó **qua ngưỡng spec** hay không.

**Số đáng nhớ của D3d:** giả-heading **21 → 1** (1 còn lại là chỗ defer chờ BA) · **32/32** ô số đo
đạt chuẩn BA · mọi thẻ PC **thấp hơn** sau migrate · `textDigest` **giống hệt 18/18 ô** · **316 test**
0 fail trên 10 module · mutation **đỏ đúng 1 test** · wizard chạy tay **6/6**.

**Câu hỏi BA đã soạn sẵn** cho 3 chỗ defer → `docs/ba-question-cardheader-trailing.md` (gộp 1 lượt:
`wj-pc-acct-headcard` treo từ D3a + 2 chỗ exam). Gửi được ngay, không cần soạn lại.

**3 chỗ defer chờ BA** (ghi §6 inventory): `:375` parthead + `:769` person-head (đều **2 trailing**,
spec cho 1 — gộp chung lượt hỏi với `wj-pc-acct-headcard` treo từ D3a) · `:858` sheet-title (loại
hẳn, bottom-sheet overlay theo tiền lệ §3).

### 🔴 Bài học D3d — đừng lặp lại ở D3e

1. **Bẫy specificity lặp lần THỨ HAI** (D3b `--flush` → D3d `--sechead`). Rule nhịp dọc cũ một lớp
   đơn là (0,1,0), **thua** `.wj-card-header--pc.wj-card-header--compact` (0,2,0) của component ⇒
   nhịp dọc biến mất mà **mọi số đo font/màu/gap vẫn Pass**. Chỉ **ảnh chụp** bắt được. Quy tắc:
   mọi hook spacing scope module phải viết `.wj-card-header.<lớp-của-mình>`.
2. **JS đọc thẳng tên class tiêu đề = chết im lặng.** `portal_exam_wizard.js` chép tên khóa thi
   sang thẻ "đã chọn" qua `.wujia-mexam-course-title`. Migrate quên sửa ⇒ tên biến mất ở bước 2/3,
   **console sạch bong, 0 lỗi**. Trước mỗi file: `grep -n "querySelector" static/src/js/*.js`.
3. **Dữ liệu quá khứ làm wizard bất động.** Mọi ca thi đều đã qua ⇒ khóa render `is-closed`, không
   có link "Chọn". Phải seed session tương lai **giống hệt trên cả hai DB**, và nhớ `_selectable()`
   đọc field **stored** (`available_participant_count` > 0), không compute on-the-fly.
4. **Đừng tin con số ở doc bàn giao** (lặp lại từ D3c) — chạy lại `d3_inventory.py`.

### ✅ D3c ĐÃ MERGE + PUSH + DEPLOY + ĐO LẠI TRÊN UAT (03/09)

Nhánh `dev/2026-09-02-d3c`. **11 call site / 3 file / 3 module** — nốt phần còn lại của 4 file
D3a. Tổng phủ **47/103**. Nghiệm thu local **20✅ + 1 phần = 97,6%** → `docs/d3c-acceptance-matrix.md`.

🔴 **Bài học 03/09 — đừng lặp lại:** phiên D3c (02/09) code xong nhưng **quên merge+push**
— commit `b6cfcbe` nằm một mình trên nhánh, `origin/main` vẫn dừng ở D3b (`aef14e1`) suốt
1 ngày dù ai cũng tưởng đã deploy. Phát hiện bằng kiểm phiên bản module qua XML-RPC (đọc-
chỉ) đối chiếu với version trên đĩa — **luôn làm bước này đầu mỗi phiên review/deploy**,
đừng chỉ tin lời kể. **Cuối MỖI phiên D3x: merge `dev/...` → `main` → `push origin` NGAY,
đừng để dồn.**

```
-u wujia_portal_layout,wujia_portal_base,wujia_portal_support,wujia_portal_delivery
```

Không module mới · không migration · không cập nhật dữ liệu · **không** cần kèm `wujia_sale`
(không đụng `wujia_portal_return`) · **không** cần bump `?v=` (rule CSS mới nằm trong asset
bundle của `wujia_portal_delivery`, không phải `<link>` tay).
Version: base `19.0.7.7.0` · support `19.0.3.14.0` · delivery `19.0.3.8.1` · layout
`19.0.32.7.0` (không đổi — chỉ thêm test).

✅ **Đã deploy UAT 03/09 + đo lại chỉ-đọc ngay trên UAT** bằng `scratchpad/d3c_uat_verify.py`
(gộp 13 route D3a+D3b regression + 6 route mới D3c, 3 breakpoint): **74/74 header đạt toàn
bộ số BA**, 0 tràn ngang, 0 JS error. Kèm audit hợp nhất 47/103 call site (2 kiểu lỗi đã
từng dính — tràn `__lead` flex, màu bị theme đè — quét lại KHÔNG thấy tái diễn chỗ nào
khác) + 183 test 0 failed/0 error trên 10 module bị đụng. Chi tiết đầy đủ →
`docs/d3-consolidated-audit-2026-09-03.md`. `UI-CARDHEADER-001` **vẫn `Ready for Dev`**
(47/103, đúng tiền lệ C8a→C8b) ⇒ **KHÔNG** chạy `qa_sync.py`; entry ledger giữ dạng comment.

**Số đáng nhớ của D3c:** tổng `scrollHeight` **−19px** · giả-heading **0** trên cả 4 route ·
lưới B4 **286/286** · tab-walk **250 stop, 12/12 route giữ nguyên số/thứ tự/ring** · chạy lại
bảng D3b **0 lệch**, bảng D3a **0 lệch ngoài ý muốn** · unit test **32, 0 failed/0 error**,
mutation **đúng 1 đỏ** · màu **`rgb(17,24,39)` ở 11/11 call site**.

⚠️ **2 chỗ ĐỔI THỨ TỰ DOM** (chủ dự án duyệt trước khi code, BA cần xác nhận lúc retest):
tên cửa hàng ở `/portal/franchise-information` mobile lên làm **dòng phụ** của tiêu đề (badge
xuống dưới, khớp bản PC cùng card), và badge trạng thái ở `/portal/delivery/<id>` PC thành
**slot trailing** của header. Ảnh trước/sau: `scratchpad/d3c-shots/`.

### 🔴 Bài học D3c — đừng lặp lại ở D3d

- **Đừng tin con số ở doc bàn giao — chạy lại `d3_inventory.py`.** Bàn giao D3b ghi "15 chỗ";
  số làm thật là **11** vì con số cũ cộng cả dòng đã loại ở §3 và 2 chỗ đang chờ BA ở §6.
- **Số đo đạt hết vẫn có thể vỡ bố cục — phải CHỤP ẢNH.** Badge trạng thái delivery trôi ra
  mép phải cột trái vì `.wj-card-header__lead` là `flex: 1 1 auto` nở hết bề rộng. Mọi
  `fontSize/lineHeight/color/gap` đều Pass; chỉ ảnh mới lộ. Sửa bằng **1 rule scope module**
  (`.wj-pc-dlv-head .wj-card-header__lead { flex: 0 1 auto; }`), **không** đụng component chung.
- **Comment XML không được chứa `--`.** Viết `--flush` trong `<!-- -->` là
  `XMLSyntaxError: Comment must not contain '--'` — đổi chữ thành "biến thể flush".
- **Test `post_install` nằm ở module khác** ⇒ `-u wujia_portal_support --test-tags …` ra
  **"0 tests"** mà RC vẫn 0. Mutation check phải `-u wujia_portal_layout` (nơi chứa test).
- **Id trong URL phải scrape từ chính trang danh sách.** `/portal/support/1` và `/2` **âm thầm
  redirect** về trang list vì thuộc cửa hàng khác cookie đang ghim ⇒ đo nhầm trang (bẫy D3b lặp).
- **M2M cần chèn bảng nối.** Bơm attachment cho ticket: đặt `res_id` là **không đủ**, phải
  insert vào `wujia_support_ticket_attachment_rel`. Và `mail_message_subtype.name` là **jsonb**
  trong Odoo 19 ⇒ `WHERE name->>'en_US' = 'Discussions'`.
- **Thẻ có đồng hồ làm harness báo động giả.** `/portal` 360px báo `cardH` 97→122,4; đo lại
  thì **cả hai server** đều 122,4 — chiều cao đổi theo phút xuống dòng, không phải hồi quy.
  Bài học "harness đo sai còn nguy hơn không đo" lặp y hệt D3b.

### ✅ D3b XONG + ĐÃ ĐO LẠI TRÊN UAT (28/08) — còn **1 lượt deploy nhỏ** *(lịch sử)*

Nhánh `dev/2026-08-28-d3b` → `main`. **26 call site / 7 file / 7 module**, tổng phủ **36/103**.
Nghiệm thu **21✅/1⏳ = 95,5%** → `docs/d3b-acceptance-matrix.md`.

Chủ dự án đã deploy lượt 1; đo lại chỉ-đọc trên UAT (13 route × 3 breakpoint) bắt được
**1 lỗi thật**: title trong `.card > .card-body` sai màu (`#212529` thay vì `#111827`) vì
theme Vuexy có `:where(.card…) .card-body:not(…) h4 { color: inherit }` **(0,4,1)** đè
`.wj-card-header__title` (0,1,0). Đã vá bằng `!important` + test khoá (mutation check đỏ
đúng 1 test). Sau vá: **46/46 header, 0 vấn đề** trên chính UAT. Chi tiết → §12 bảng nghiệm thu.

⚠️ **Deploy lượt 2 (nhỏ):** `-u wujia_portal_layout` — layout `19.0.32.7.0`, `?v=1180`.
Xong thì chạy `python3 scratchpad/d3b_uat_verify.py` (không `WJ_PATCH`) để xác nhận trên
bundle thật, rồi `scripts/ba_spec/qa_deploy_mark.py`.

Lệnh deploy (**bắt buộc kèm `wujia_sale`**, thiếu là RC=255 tại `backend_product_views.xml:5`):

```
-u wujia_portal_layout,wujia_portal_base,wujia_portal_knowledge,wujia_portal_notification,\
   wujia_portal_report,wujia_portal_sale,wujia_portal_info_request,wujia_portal_return,wujia_sale
```

Không module mới · không migration · không cập nhật dữ liệu · `?v=1180` đã bump.
Sau deploy: **đo lại chỉ-đọc trên UAT** (L14/L10) → `scripts/ba_spec/qa_deploy_mark.py`.
`UI-CARDHEADER-001` **vẫn `Ready for Dev`** (36/103) ⇒ **KHÔNG** chạy `qa_sync.py`.

**Số đáng nhớ của D3b:** tổng `scrollHeight` **−24px** · giả-heading **0/44 ô** · lưới B4
**286/286** · chạy lại bảng D3a **356 phép so, 0 lệch** · tab-walk **433 stop, ring 16/16** ·
font **66 tiêu đề, 0 lệch** · unit test **0 failed/0 error/170** · UAT sau vá **46/46 header, 0 vấn đề**.

**✅ D3a ĐÃ DEPLOY VÀ ĐÃ ĐO LẠI TRÊN UAT (28/08).** Nhánh `dev/2026-08-27-d3a` merge `main`,
chủ dự án đã deploy — 6 module `installed`, `wujia_portal_layout 19.0.32.5.0`. Đo lại chỉ-đọc
trên chính UAT × 3 breakpoint: **14 header · 0 lỗi**, khớp 100% số BA, 0 giả-heading, 0 tràn
ngang, 0 JS error. Nhãn lọc bù hàng PC = mobile = `— Tất cả trạng thái —`; `?state=cancelled`
ra meta `0 ticket` (count 0 vẫn hiện). Chi tiết ở `docs/d3-acceptance-matrix.md` §LIMIT 5.
`UI-CARDHEADER-001` **vẫn `Ready for Dev`** (mới 4/103 call site) ⇒ **chưa** có gì cho
`qa_sync.py` handoff; entry ledger soạn sẵn **dạng comment** trong `docs/qa-issue-ledger.yaml`,
D3n bỏ `#` là chạy được (tiền lệ C8a).

**Việc tồn 27/08 — ✅ XONG.** Nhãn option "tất cả" của bộ lọc bù hàng nay gom về **một hằng**
`FILTER_ALL_LABEL` cạnh `FILTER_OPTIONS` (`wujia_portal_return/controllers/portal.py`), cả PC
lẫn mobile đều `t-out="filter_all_label"`. Đo trên browser: PC `— Tất cả —` → **`— Tất cả trạng
thái —`**, khớp mobile. `value=""` không đổi ⇒ kết quả lọc bất biến.

### 🔴 Bài học D3b — đừng lặp lại ở D3c

- **`ch_platform` KHÔNG mặc định là `'pc'`.** `/portal/info-request` **mất hẳn tiêu đề ở
  mobile** vì `.wujia-content-card` của màn đó **không nằm trong khối `d-none d-lg-block`** —
  một markup phục vụ cả hai nền tảng. Trước khi đặt `ch_platform`, phải
  `grep "d-none\|d-lg-"` **trong chính view**; không có ⇒ để trống (biến thể `--any`).
  Đã chốt bằng test `test_shared_markup_views_do_not_bake_platform`.
- **Đo rồi mới thêm rule — và đo xong có thể là "không thêm gì".** 6 lớp body "ứng viên"
  trong kế hoạch (`.card-body`, `.list-group`, `.wujia-mknow-body`, `.wj-rep-pccard__body`,
  `.wj-pc-kv-grid`, `.wj-pc-noti-detail-body`) **không lớp nào cộng chồng**: mọi `gapToBody`
  đều giảm (18→12, 14→12, 10→8). Thêm rule mù ở đây là **bóp nhịp xuống dưới chuẩn BA**.
- **`--flush` trần thua specificity.** `.wj-card-header--flush` là (0,1,0), thua rule nhịp
  `.wj-card-header--m.wj-card-header--compact` (0,2,0) ⇒ phải khai kèm `--m`/`--any`.
  Bên `--pc` may mà đã có cặp nên D3a không lộ.
- **`--any` = một markup cho cả hai nền tảng** (họ Bootstrap `.card-header`) ⇒ phải có khối
  `@media (min-width: 992px)` riêng, nếu không nó dùng **số mobile ở mọi bề rộng**.
- **Component chỉ có `h2/h3/h4`.** Gặp `h5`/`h6` cũ thì buộc phải đổi cấp — kiểm tra outline
  trước/sau, đừng để tụt cấp (D3b: 3 chỗ đổi, cả 3 đều **bớt** nhảy cấp).
- **Thẻ cao lên chưa chắc là lỗi.** 4 thẻ của D3b cao thêm 2–10px vì tiêu đề cũ **nhỏ hơn
  chuẩn** (`h6` 12.3px, `h5` 15.3px, `h3` 14px). Phải truy nguồn tăng là *chữ* hay *margin*
  trước khi kết luận — margin mới là lỗi.
- **`wujia_core` dời logfile giữa chừng** sang `<thư-mục-logfile>/<năm>/<tháng>/<ngày>.log`
  ⇒ file `--logfile` chỉ có ~49 dòng đầu, **không** có `odoo.tests.result`. Đọc file đã dời.
  Traceback `py.warnings` của `wj_ks_dashboard_ninja/controllers/ks_domain_fix.py:8`
  (`@route(type='json')` deprecated) là **cảnh báo**, không phải lỗi.
- **`var()` không phải nghi phạm mặc định khi màu sai.** Giả thuyết "thiếu token ⇒ `var()`
  invalid ⇒ inherit" **sai** — token có ở cả `:root` lẫn element. Thủ phạm là rule theme
  `:where(.card…) .card-body:not(…) h4 { color: inherit }`: `:not()` **mang độ đặc hiệu của
  tham số** nên nó là **(0,4,1)**, không phải (0,1,1). Truy bằng CDP
  `CSS.getMatchedStylesForNode` + `matchingSelectors` (đọc đúng selector nào trong danh sách
  khớp), đừng đoán. Không nâng specificity nào hợp lý thắng nổi ⇒ `!important`.
- **Harness đo sai còn nguy hơn không đo.** Lượt UAT đầu báo 6 lỗi thì **3 là slug không tồn
  tại** (Odoo trả trang danh sách, đo nhầm trang — phải kiểm `href` thật từ trang list) và
  **3 là kỳ vọng quá rộng** (`padding: 0` áp cho cả header cố ý giữ class container cũ).
  Chỉ 3/9 cảnh báo là lỗi thật.
- **Dữ liệu rỗng làm call site "tàng hình".** `related` luôn rỗng (0 sản phẩm có
  `public_categ_id`) ⇒ header `--any` duy nhất không đo được. Phải bơm dữ liệu **giống hệt
  nhau trên CẢ HAI DB copy**, không thì cứ tưởng đã đo đủ.

### Còn treo sau D3a — vẫn treo sau D3c, đọc trước khi làm D3d

1. **Fork `wj-pc-acct-headcard` (19 hit) chưa trả lời.** Markup có **HAI** vùng phải
   (`__chips` + `__box`) mà spec cho **tối đa MỘT** trailing. D3a **không đụng file**, lấy
   `wj-pc-acct-panel-title` cùng route làm mẫu thay thế. Cần BA chốt: chips/box ra **ngoài**
   CardHeader (Dev nghiêng về cái này) / gộp thành **một** control / cho `regular` + miễn trừ.
2. **Title dài vượt 2 dòng.** Spec tự chỏi: *"wrap tối đa 2 dòng"* + *"không ellipsis"*. Dev
   chọn hiện đủ chữ. Đo thật: 2 dòng chứa ~64 ký tự @360 và ~96 @1440, tiêu đề dài nhất trong
   mã nguồn là **22 ký tự** ⇒ mọi call site thực tế đều 1 dòng. Cần BA chốt ưu tiên.
3. **3 chỗ SectionHeader/CardHeader vẫn treo từ C8** (`portal_delivery.xml:15`,
   `portal_order_catalog.xml:17`, `portal_debt.xml:688` "THÔNG TIN CHUYỂN KHOẢN",
   `portal_inspection_list_templates.xml:34`) — **KHÔNG tự quyết lại**.
4. **FilterCard = 0 call site** ⇒ theo MAPPING của BA đây là **dựng MỚI**, không phải migrate.
5. **🆕 Nhãn option rỗng của bộ lọc lệch GIỮA CÁC MÀN** (phát hiện khi đo lại UAT 28/08, cùng
   họ với việc tồn 27/08 nhưng **rộng hơn**, chưa sửa vì ngoài phạm vi D3a). Quét mọi `<select>`
   đang hiện trên UAT: `/portal/return` → `— Tất cả trạng thái —` ✅ (vừa sửa) · `/portal/support`
   → `— Tất cả —` · `/portal/delivery` và `/portal/purchase-history` → `Tất cả trạng thái`
   (**không có gạch em**) · `/portal/notification` → dùng chính tên trường (`Loại thông báo`,
   `Trạng thái`). **4 kiểu chữ cho cùng một ý.** Cả 4 màn đều gõ tay trong `.xml`, không màn nào
   lệch PC↔mobile (3 màn kia mobile không có select nhìn thấy được) ⇒ **không phải bug hiển thị,
   là nợ nhất quán**. Cách sửa giống hệt D3a: một hằng dùng chung. Ghép vào **D7+** cùng lứa
   component-hoá. **D3b có động vào `portal_notification.xml` nhưng CỐ Ý không sửa kèm** — đổi
   chữ hiển thị là hỏng chính phép kiểm "chữ hiển thị không đổi" của bảng hồi quy.
6. **🆕 `/portal/notification/41` có `H3` đứng TRƯỚC `H2`** (outline `H1 H3 H2 H3 H3`) — lỗi thứ
   tự **có sẵn**, không do D3b (đo trước/sau y hệt nhau). Không sửa ở cụm D3 vì đổi `ch_level`
   là đổi outline ngoài phạm vi issue. Đề xuất gộp **R2**.

### 🔴 Bài học D3a — đừng lặp lại ở D3b

- **Gỡ `mb-*` ở call site là CHƯA đủ.** `/portal/support` vẫn cách 28px vì lớp **body** tự khai
  `margin-top` (`.wujia-content-card-table { margin: 16px … }`). Phải **đo `gapToBody` bằng
  `getBoundingClientRect()`**, rồi trung hoà đúng lớp body đó:
  `.wj-card-header + <lớp-body> { margin-top: 0 }`. Danh sách này nằm cuối khối CardHeader
  trong `_components.css`, rút dần mỗi session.
- **Vị trí trong card KHÔNG phải tiêu chí phân loại.** Bộ lọc "phải là con đầu của card" từng
  loại nhầm **31** CardHeader hợp lệ (vd `wj-pc-acct-headcard__title` nằm trong `__main` sau
  `__icon`). Ranh giới của BA thuần tuý là **"nằm trong card ⇒ CardHeader"**.
- **`--log-level=warn` nuốt dòng `odoo.tests.result` khi test PASS** (nó là INFO; chỉ khi FAIL
  mới là ERROR) ⇒ tưởng "test không chạy". Dùng `--log-level=test`.
- **A/B bằng 2 DB rẻ và sạch hơn A/B bằng CSS interception** khi thay đổi nằm ở `arch_db`:
  clone DB, `-u` một bên, dựng 2 server 2 port. Harness: `scratchpad/d3_measure.py` ·
  `d3_probe_ch.py` · `d3_edge.py` · `d3_tabwalk.py`.

### 🆕 6 issue BA vừa đổ lên — lứa **D7+**, CHƯA phân cụm

BA thêm STT **128–133** sau khi lứa D được chốt: **StatusBadge · PageContainer · Pagination ·
Sidebar · Button · UI-MOB-HOME-004**. Chủ dự án chốt 27/08: **chỉ ghi nhận, không đụng** cho
tới khi xong D3–D6. Phân cụm chúng thành D7… sau khi D6 đóng.

**Việc sheet (đợt 27/08) — ✅ ĐÃ XONG, không còn tồn.** Cả 5 issue đã deploy nay ghi
**`ĐÃ DEPLOY UAT 27/08/2026 — sẵn sàng retest`** ở cột `Build / Deploy` + ngày cập nhật 27/08
+ 5 dòng `7. ISSUE HISTORY`, verify lại bằng CSV công khai (`WJ-PORTAL-UI-002` dòng 108 ·
`UAT-BH-001` 111 · `UAT-BH-003` 112 · `UAT-BH-005` 113 · `UAT-BH-006` 114). BA retest được ngay.

⚠️ **Bài học công cụ, ghi để phiên sau khỏi chẩn đoán sai như phiên này:**

1. **`qa_sync.py` cố ý idempotent** — issue đã `Ready for Retest` thì không ghi đè nữa, nên cột
   Build/Deploy **mắc kẹt ở "Chờ deploy UAT" sau mỗi lần cài đặt** và BA tưởng chưa deploy được.
   Đã viết `scripts/ba_spec/qa_deploy_mark.py` cho đúng việc này: chỉ đổi phần đầu cột P + cột
   Ngày cập nhật + thêm dòng History, **không** đụng trạng thái/owner. **Sau mỗi lần chủ dự án
   deploy UAT, chạy nó:**
   ```
   cd scripts/ba_spec
   python3 qa_deploy_mark.py <ID> <ID> …                     # dry-run
   python3 qa_deploy_mark.py --apply --date dd/mm/yyyy <ID> … --note "<số đo sau deploy>"
   ```
2. 🔴 **Bridge Apps Script trả 404 KHÔNG có nghĩa là nó chết.** Phiên này `sheet_io.ping()` lỗi
   404 vài lần liên tiếp, GET thẳng `webapp_url` ra trang "Không tìm thấy trang — Drive", đã kết
   luận nhầm là deployment bị xoá/đổi quyền. Vài phút sau **ping lại 4/4 OK, không sửa gì cả** —
   là **lỗi tạm của phía Google**. ⇒ Gặp 404 thì **thử lại sau vài phút** trước khi bảo chủ dự
   án deploy lại bridge.
3. 🔴 **404 không có nghĩa là chưa ghi.** Lần `--apply` bị 404 đó **thực ra đã ghi xong ô** trên
   sheet, chỉ là response không về nên Python raise **trước khi** kịp thêm dòng History ⇒ dữ
   liệu ghi một nửa mà log báo "fail". ⇒ Bridge lỗi thì **đọc lại sheet để kiểm**, đừng cho là
   chưa ghi rồi chạy lại mù.
4. ⚠️ **Tra dòng phải dùng đúng tên tab `"Issue List"`** (có trong `KNOWN_GID` ⇒ đi
   `export?format=csv`, số dòng tuyệt đối). Gọi `read_values("5. Issue List")` sẽ rơi xuống
   đường `gviz` và **ăn theo filter đang bật của tab** ⇒ chỉ ra 25 dòng, issue nằm ở dòng 7 thay
   vì 108 — ghi theo số đó là **đè nhầm sang issue khác**. Tab History cũng vậy: đọc phải là
   `"7. ISSUE HISTORY"`, còn ghi thì `append_row("ISSUE HISTORY", …)` (bridge tự khớp gần đúng).

⚠️ **Bẫy đã trả giá khi tra dòng**: `sheet_io.read_values("5. Issue List")` đi đường `gviz`
nên **ăn theo filter đang bật của tab** ⇒ chỉ ra 25 dòng và số dòng LỆCH HẲN (issue nằm ở dòng
7 thay vì 108). Ghi theo số dòng đó là **ghi đè nhầm issue khác**. Muốn số dòng tuyệt đối phải
gọi đúng tên `"Issue List"` (có trong `KNOWN_GID` ⇒ đi `export?format=csv`, bỏ qua filter) —
đúng như `qa_sync.py` đang làm.

**Trạng thái khác:** hàng đợi deploy có **D3a chờ lên UAT** · Issue List: ngoài lứa D đang chạy
còn **6 issue mới STT 128–133** đã ghi nhận thành lứa **D7+** (chưa đụng) · nhánh
`dev/2026-08-27-d3a` đã merge `main`.

**Thứ tự chạy:** D1 → D2 → D3 (nhiều session D3a…) → D4 (D4a…) → D5 (D5a…) → D6 → **R1–R5**.
Lý do: D1 là 2 High chức năng, độc lập. D2 rẻ và là **tiền đề** của spec CardHeader/SurfaceCard
("Inter + fallback Unicode") và của BH-007 (tên song ngữ CJK). D3 → D4 → D5 theo đúng quan hệ
spec BA (CardHeader nằm **trong** SurfaceCard; DataList nằm **trong** SurfaceCard và giao header
cho CardHeader). D6 để cuối vì BH-008 đòi card bù hàng "nhất quán hệ thống Portal" — sau D4 thì
đạt bằng cách **dùng component**, không chép token tay. R1–R5 sau cùng vì D3/D4/D5 hút bớt việc
của R1 (hex cứng → token).

**3 quyết định chủ dự án đã chốt 25/08 — đừng hỏi lại:**
1. Chuẩn hoá component **làm kỹ nhất có thể, chấp nhận nhiều session** (D3/D4/D5 chia nhỏ).
2. **Áp đúng con số mật độ BA**, mỗi màn phải có bảng đo **trước–sau** (chiều cao trang, số
   record thấy trong viewport); chỗ nào mâu thuẫn issue đã Pass thì ghi LIMIT, đừng lặng lẽ đổi.
3. `issue_queue.py` đã **nới**: `Ready for Dev` = việc của Dev bất kể cột Owner (BA điền
   `BA/Tester` cho cả 11 issue ⇒ hàng đợi từng báo 0 việc).

> 🔴 **Backend phải làm kĩ (chốt 25/08):** "đừng để lỗi lặt vặt". Cụ thể: server **không tin
> dữ liệu client gửi lên** — tính lại từ recordset sống; test phải mô phỏng **đúng đường web
> client** (`default_get` → lọc field readonly không `force_save` → `create` → gọi nút), và
> phải chứng minh test có ý nghĩa bằng cách stash bản vá cho nó fail.

> 🔴 **Luật không phá hồi quy (kế thừa cụm R, 23/08):** trước khi đụng file, tra
> `docs/qa-issue-ledger.yaml` + các `docs/c*-acceptance-matrix.md` xem file đó đang gánh issue
> nào; đo trước–sau bằng lưới B4 (**chuẩn 286/286**), tab-walk a11y, 2 viewport 391×844 +
> 1920×1080. Dev **không tự đóng `Done`**, chỉ tới `Ready for Retest`.

⚠️ **Bẫy môi trường phải nhớ (đã trả giá):**
- `-u` chạm `wujia_portal_return` **bắt buộc kèm `wujia_sale`** (rename `description_ecommerce`
  S52) — thiếu là RC=255 tại `backend_product_views.xml:5`.
- Chạy test trên DB copy phải thêm **`--db-filter='^wujia_tea_d1$'`** (đổi theo tên DB):
  `config/odoo.conf` ghi cứng `dbfilter = ^wujia_tea_19$`, thiếu cờ thì `HttpCase` bị đăng
  xuất giữa chừng và test controller fail **vì môi trường**, không phải vì code.
- Đăng nhập Playwright: **`POST /web/session/authenticate` + bơm cookie `session_id`**
  (trang login S39 ẩn form mặc định ⇒ `page.fill` luôn timeout). Mật khẩu trên DB copy thường
  khác UAT — đặt lại bằng XML-RPC/`odoo-bin shell` trước khi đo.
- Đo TRƯỚC–SAU trên backend web client: **mỗi lần một context trình duyệt mới** (client cache
  action/view trong session) và chờ đủ ~8s nếu vừa xoá attachment asset.
- DB copy không kèm filestore ⇒ 404 asset (`web_tour…min.js`) + `ir_attachment os.stat` lỗi:
  xoá attachment asset cho tự sinh lại, đừng truy như lỗi sản phẩm.
- `freezegun` phải là **1.1.0**.

**Tiến độ cụm:** D3b ✅ 28/08 (36/103 call site, đã đo lại UAT) · D1 ✅ 25/08/2026 (4 issue → Ready for Retest; `-u wujia_portal_return,wujia_sale,wujia_portal_layout`
trên DB copy `wujia_tea_d1` port 8065 → RC=0; **26/26 đo đạt (100%)**, 6 test mới + 33 hồi quy
= 39 test xanh, lưới B4 286/286, tab-walk 2 viewport sạch; bảng đối chiếu
`docs/d1-acceptance-matrix.md`) · **D2 ✅ 26/08/2026** (`b70d26a`, WJ-PORTAL-UI-002 →
Ready for Retest; `-u wujia_portal_layout` trên DB copy `wujia_tea_d2` port 8066 → RC=0;
**14/14 acceptance**, chỗ ≠ Inter **145 → 0** trên 80 ô đo **ngay trên UAT**, B4 286/286,
tab-walk 331 stop giữ nguyên thứ tự + ring; `docs/d2-acceptance-matrix.md` +
`docs/d2-font-inventory.md`) · **D3a ✅ 27/08/2026** (dựng `wj_card_header` + kiểm kê
`docs/d3-cardheader-inventory.md` **103 call site** trong đó **31 giả-heading** — đúng bệnh BA
nêu; migrate **4 họ markup** mẫu = 10 header; `-u` 6 module trên DB copy `wujia_tea_d3` port
8067 → RC=0, `Registry loaded in 6.302s`; **105 test xanh** + 26 test mới có **mutation check**;
acceptance **19✅/1⚠️/1⏳ = 95%**, mật độ **16/16 ô không cao lên**, 3/4 route thẻ thấp đi
20.6/22.0/**104.0**px, giả-heading **8 → 0**, B4 **286/286**, tab-walk 175 stop giữ nguyên,
font Inter 514/514 y hệt; `docs/d3-acceptance-matrix.md`) · **D3b ✅ 28/08/2026** (migrate
**26 call site / 7 file / 7 module** ⇒ phủ **36/103**; vá 2 lỗ hổng component `--flush`
specificity + `--any` thiếu số desktop; `-u` 9 module trên DB copy `wujia_tea_d3b` port 8068
→ RC=0; **169 test xanh** + 4 test mới có **mutation check**; acceptance **20✅/1⏳ = 95%**,
tổng `scrollHeight` **−24px** trên 44 ô, giả-heading **0/44**, outline 8 giữ/3 tốt lên, chữ
hiển thị 43/44 giống hệt (1 ô mọc đúng "0 kết quả" theo yêu cầu BA), B4 **286/286**, bảng D3a
chạy lại **356 phép so 0 lệch**, tab-walk 433 stop ring 16/16, font 66 tiêu đề 0 lệch;
bắt được **1 lỗi thật**: `/portal/info-request` mất tiêu đề ở mobile do bake `ch_platform`;
`docs/d3b-acceptance-matrix.md`) · D3c ✅ · D3d ✅ · D3e…D3n ⬜ · D4 ⬜ · D5 ⬜ · D6 ⬜ · R1–R5 ⬜

🚚 **D1 + D2 ĐÃ DEPLOY UAT 27/08** (`wujia_portal_layout 19.0.32.4.0` · `wujia_portal_return
19.0.2.7.0` · `wujia_sale 19.0.4.3.0`, xác nhận XML-RPC) **+ đo lại chỉ-đọc ngay trên UAT**:
D2 **14/14** (chỗ ≠ Inter 145→0, `scrollHeight`/số dòng/`font-weight`/icon **0 lệch trên 80 ô**,
B4 286/286, tab-walk 346 stop) · D1 **27/28**.
🚚 **D3b chờ deploy UAT** — xem lệnh + version ở đầu §Bàn giao. (D3a đã deploy + đo lại 28/08.)

---

## D1 — Bù hàng: chức năng + filter ✅ (UAT-BH-001, 003, 005, 006)

Đã xong 25/08. Kết luận để phiên sau khỏi đào lại:

- **BH-001** không phải race condition: field wizard khai `readonly=True` ở **tầng Python** ⇒
  web client bỏ khỏi vals khi `create` ⇒ nhóm rỗng ⇒ luôn `UserError("Dữ liệu đã thay đổi")`.
  Sửa: readonly về **view + `force_save="1"`**, và `action_confirm` **tự dựng lại nhóm + rải
  FIFO từ recordset sống** (`_live_buckets()`), không tin client.
- **BH-003** không phải lỗi domain/dữ liệu: `REF0001…REF0010` là **sample data của Odoo**
  (list view `sale` khai `sample="1"`, tập rỗng thì `SampleServer` dựng bản ghi giả cạnh empty
  state). Sửa bằng view list riêng `sample="0"` gắn vào action qua `view_ids`.
- **BH-005/006**: controller vốn đã nhận đủ `q`/`state`/`date_from`/`date_to`; chỉ template
  thiếu control. Nhãn trạng thái gom về **một nguồn duy nhất** `FILTER_OPTIONS` +
  `state_filter_domain()`.
- **Sai lệch cần BA xác nhận khi retest:** đã **thêm nhãn `Nháp`** ngoài 7 nhãn BA liệt kê —
  portal thật có liệt kê yêu cầu nháp, thiếu nhãn này thì bộ lọc không phủ hết dữ liệu.
- **Còn nợ sang D6:** control lọc mobile cao **38px**, chưa đạt touch target 44–48px của
  **UAT-BH-009**.

## D2 — Font Inter + fallback CJK (WJ-PORTAL-UI-002) ✅ — `-u wujia_portal_layout`

Đã xong 26/08 (`b70d26a`). Kết luận để D3/D4/D6 khỏi đào lại:

- **Gốc rễ không phải "component tự override font"** như đề xuất BA đoán: không module nào
  khai Inter Tight cả. Rule ép Inter (`_wujia_theme.css`, UI-06/S39) neo `.content-wrapper`,
  còn rule `h1..h6{font-family:"Inter Tight"…}` đến từ bundle `website` ⇒ mọi heading ngoài
  neo đó thua, vì **rule khớp element luôn thắng kế thừa, bất kể specificity**. Đổi neo sang
  `html body` là hết, một luật cho toàn portal.
- `wj_section_header` (component chung C8) cũng nằm trong số dính ⇒ đừng vá theo màn.
- **`--wujia-font-family` nay đã có fallback Thái/CJK** → dùng thẳng cho spec `CMP-CH-001`/
  `CMP-SC-001` (D3/D4) và cho BH-007 (D6), **không khai lại stack font ở chỗ khác**.
  Bẫy đã trả giá: phải khai **cả `'Noto Sans SC'` lẫn `'Noto Sans CJK SC'`**, thiếu cái sau
  thì chữ Hán rơi sang biến thể **JP**.
- 🔴 **Rule `font-weight:700 !important` ở `_wujia_theme.css:35-40` VẪN neo `.content-wrapper`**
  — cố ý để nguyên (nới sẽ phá weight 800 của `CMP-SH-001`). D3 đụng weight thì nhớ điều này.
- Harness còn dùng lại được: `scratchpad/d2_font_audit.py` (quét font 16 route × 5 bp trên UAT,
  có `--patch`/`--control`), `d2_compare.py`, `d2_tabwalk.py` (tab-walk A/B bằng
  `ctx.route()` trả file CSS bản HEAD — **cách A/B CSS trên cùng một server**).
- ⚠️ Bẫy đo đã trả giá 2 lần: (1) không set cookie `wujia_active_franchise_id` ⇒ portal ra
  "Chưa chọn cửa hàng", đo trang rỗng; (2) chỉ quét leaf node ⇒ bỏ sót heading có `<span>` con.

### Prompt gốc (giữ để tham chiếu)

> Prompt: "làm cụm D2". Rule hiện có chỉ phủ `.content-wrapper h1..h6` +
> `.wj-page-header__title` (`_wujia_theme.css:41-50`, ghi chú UI-06 S39); các màn BA nêu
> (inspection PC; debt/exam/profile mobile) nằm **ngoài** selector đó.

1. **Đo trước:** liệt kê computed `font-family` của mọi text node trên 12 màn × 2 viewport
   (`qa_visual_check.py`) → danh sách chỗ còn Inter Tight. Đừng grep CSS mà đoán — nguồn là
   asset Odoo, không phải CSS mình.
2. Sửa ở **tầng token/layer chung**, không rải override từng module; giữ nguyên font icon.
3. Thêm **fallback Unicode/CJK thống nhất** vào `--wujia-font-family` (nền cho BH-007 và cho
   spec CMP-CH-001/CMP-SC-001).
4. Acceptance BA đòi **0 thay đổi** xuống dòng/chiều cao/tràn ngang ở 360/390/430/500 +
   desktop ⇒ **bắt buộc đo chiều cao trang trước–sau**, đổi fallback là đổi metrics.

## D3 — CardHeader `CMP-CH-001` (UI-CARDHEADER-001) — nhiều session D3a…D3n

> Prompt: "làm cụm D3a" (rồi D3b, D3c…). Mô hình đã chạy trơn ở C8: **kiểm kê trước, code sau,
> phân loại theo TỔ TIÊN DOM chứ không theo tên class**.

- **D3a ✅ 27/08.** Kiểm kê `docs/d3-cardheader-inventory.md`: 218 ứng viên trong card → 91 bị
  loại theo vai trò → **127 CardHeader** (96 heading thật + **31 giả-heading** = đúng bệnh BA
  nêu) → loại tay 23 → **104** ⇒ **103 chỗ gọi thật**. Con số thật **nhỏ hơn hẳn** ước lượng
  của kế hoạch: `wj-pc-card__title` **23–25** chứ không phải 154, `wj-pc-acct-headcard` **19**
  chứ không phải 33 ⇒ D3 nhẹ hơn dự kiến. Component `wj_card_header` + CSS đã xong; migrate
  **4 họ markup** mẫu (10 header). Đo: `docs/d3-acceptance-matrix.md` — **95%**.
- **D3b ✅ 28/08.** 26 call site / 7 file (home · franchise_profile · knowledge · notification ·
  report_orders · pc_cart_panel + product_detail · info_request · return_list) ⇒ **36/103**.
  Vá 2 lỗ hổng component (`--flush` thua specificity ở mobile/`--any`; `--any` thiếu khối
  `@media ≥992px`). Đo: `docs/d3b-acceptance-matrix.md` — **95%**.
- **D3d ✅ 04/09.** 14 call site / 1 file (`portal_exam.xml`) — phủ **61/103**;
  3 chỗ defer chờ BA. `docs/d3d-acceptance-matrix.md`.
- **D3c ✅ 02/09.** 11 call site / 3 file — nốt phần còn lại của 4 file D3a (support 6 ·
  delivery 1 · franchise-information 4) ⇒ **47/103**. Kèm 1 rule CSS scope delivery cho slot
  trailing và **2 chỗ đổi thứ tự DOM** đã được chủ dự án duyệt. Đo:
  `docs/d3c-acceptance-matrix.md` — **97,6%**.
- **D3e…D3n:** migrate hết call site theo **bảng-theo-file** ở §kế hoạch của inventory, mỗi
  session một nhóm màn, mỗi session một lần `-u`, mỗi session đo lại B4 286/286 + tab-walk.
  **D3e = `portal_return_detail.xml` + `portal_history.xml`** (chạy lại `d3_inventory.py`).
  Issue **giữ `Ready for Dev`** cho tới khi đủ 100% (tiền lệ C8a→C8b); entry ledger đã soạn
  sẵn **dạng comment** ở cuối `docs/qa-issue-ledger.yaml`, D3n bỏ `#` là dùng được.
- 🔴 **Bẫy D3a đã trả giá, đừng lặp:** (1) gỡ `mb-*` ở call site **chưa đủ** — lớp body tự khai
  `margin-top`, phải đo `gapToBody` bằng `getBoundingClientRect()` rồi trung hoà bằng
  `.wj-card-header + <lớp-body> { margin-top: 0 }`; (2) **vị trí trong card không phải tiêu
  chí** — lọc "phải là con đầu của card" từng loại nhầm 31 header hợp lệ; (3)
  `--log-level=warn` **nuốt dòng kết quả test khi PASS**, dùng `--log-level=test`.
- Con số bắt buộc: desktop compact 18/24/600–700, regular 20/28/700; mobile compact 16/22/600–700,
  regular 18/24/700; header→body 12/8. **CardHeader không tự thêm padding, không đặt chiều cao.**
- ⚠️ `_wujia_theme.css:35` ép `.content-wrapper h1..h6{font-weight:700!important}` (UI-06/S35)
  ⇒ weight khác **không ăn**; C8 đã chốt giữ 700 + ghi LIMIT. Cần 600 thì xử ở scope, **không**
  gỡ rule global.
- ⚠️ Odoo 19 QWeb không có directive đặt tên thẻ động (`ir_qweb.py:1705`) ⇒ heading level phải
  rẽ `t-if/t-elif/t-else` như `wj_section_header`.
- ⚠️ Trailing slot render **markup thô không bọc element** để `wj_ajax_list` swap được.

## D4 — SurfaceCard `CMP-SC-001` (UI-SURFACECARD-001) — D4a…D4f

> **D4a XONG 04/09/2026** — kiểm kê + kế hoạch chia lượt, **0 dòng code**.
> Bảng đầy đủ: **`docs/d4-surfacecard-inventory.md`**. Đọc nó TRƯỚC khi làm bất kỳ lượt nào.

**Quy mô:** 442 lượt / 67 họ thô → **384 lượt / 65 họ trong phạm vi**; trong đó **27 họ /
246 lượt là SHELL thật**. Gấp hơn bốn lần D3.

**Điều làm D4 nguy hiểm hơn D3:** D3 đổi cỡ chữ *bên trong* thẻ; D4 đổi **chính cái khung**
⇒ mọi trang đổi chiều cao thật, và **nhịp header→body 12px mà D3 vừa hội tụ cũng đổi theo**.

### 🔴 Ràng buộc ĐO ĐƯỢC — quyết định thứ tự lượt nhiều hơn cả kích cỡ

Ba route **không đo được trên máy local**, phát hiện khi đo D4a:

| Route | Vì sao | Kéo theo họ nào |
|---|---|---|
| `/portal/reports/orders` | **500 có sẵn** — tz `Asia/Saigon`, cụm **R3** | `wj-rep-mcard` (16) + `wj-pc-metric-card` phần báo cáo (20) |
| `/portal/inspection*` | `wujia_portal_inspection` **`uninstalled`** trên DB dev | toàn bộ nhóm Khảo sát (21) + `wj-pc-metric-card` phần khảo sát (24) |

⇒ **`wj-pc-metric-card` (44 lượt — họ to thứ nhì) nằm TRỌN trong hai route không đo được.**
Đó là lý do nó **không** được chọn làm lượt hiệu chỉnh, dù nó gọn nhất về file. Không có bảng
đo trước–sau thì không được migrate — đúng luật số 2 dưới đây.

### Luật chung cho MỌI lượt D4b…D4f

1. **Đúng một lần `-u`** mỗi lượt.
2. **Một bảng đo trước–sau** ở đủ 5 khổ BA chỉ định (**1440 · 1024 · 992/991 · 390 · 360**),
   gồm chiều cao trang **và số record thấy trong viewport** (acceptance #11 của BA: số record
   thấy được **không được giảm** nếu BA/UI chưa duyệt).
3. 🔴 **Chạy lại RULE 1 + RULE 2 của `d3-review-matrix.md`** (`scratchpad/d3_review.py`) sau
   mỗi lượt — đổi padding khung là đổi nhịp header→body mà D3 vừa hội tụ. **Không được coi
   D3 là đã xong.** ⚠️ **D4b chứng minh: RULE 1/2 là điều kiện CẦN, KHÔNG ĐỦ** — chúng đo
   *sự không đều giữa các card*, nên một sai số **đều tay trên mọi card** lọt qua sạch sẽ.
   Phải kèm **một phép đo TUYỆT ĐỐI** nhịp header→body (`scratchpad/d4b_rhythm.py`).
   `--portal-login anh.owner` là **bắt buộc**: mặc định của script là `None` ⇒ rơi về `admin`
   ⇒ 0 bề mặt mà vẫn báo chạy xong (bẫy "Pass rỗng").
4. Chỗ nào **lồng ≥2** hoặc đổi padding khung ⇒ **bắt buộc chụp ảnh**, đừng tin bảng số
   (bài học D3e: badge trôi 966px mà mọi số vẫn Pass).
5. Đo rồi mới thêm rule; đặc hiệu của rule scope mới phải đếm **so với chính các rule cùng
   file**, không chỉ so với component (bẫy `:not()` đã tái xuất **2 lần**).
6. Guard phải chứng minh bằng **mutation** (tạm gỡ ra, thấy đúng test tương ứng đỏ) —
   `assertIn` là guard giả. ⚠️ Test dùng `subTest` in ra `FAIL: Subtest Lop.test (params)` —
   bộ dò mutation thiếu chữ `Subtest` sẽ **báo guard rỗng oan** (dính ở D4b).
7. 🆕 **Chủ sở hữu DUY NHẤT dáng khung.** Khi migrate một họ sang `wj-surface-card`, **rút hẳn**
   `background`/`border`/`border-radius`/`padding`/`box-shadow`/`gap` khỏi rule cũ, đừng để hai
   rule cùng đặc hiệu `(0,1,0)` cùng khai rồi phân xử bằng thứ tự nguồn. Lớp cũ **giữ nguyên ở
   call site** (qua `sc_class`) để CSS con và 3 danh sách `:is()` của `_interaction.css` không đứt.
8. 🆕 **`gap` chỉ đặt ở biến thể xếp ngang (`--summary`), CẤM đặt ở rule gốc** — cộng chồng với
   `margin` của `wj_card_header` thành 24px (xem bài học D4b).
9. 🆕 **Không khoá chiều cao** (BA cấm) — nhưng `min-height` cũng **chưa bao giờ** làm các thẻ
   cao bằng nhau. Cách đúng: `height: 100%` trên **cả** `<a>` bọc ngoài lẫn card.

### Thứ tự lượt — chia theo HỌ, không theo màn (BA cấm variant theo route)

| Lượt | Họ | Lượt / file | `-u` | Rủi ro chính | Vì sao xếp ở đây |
|---|---|---:|---|---|---|
| ✅ **D4b XONG (04/09)** | `wujia-kpi-card` + `wujia-content-card` — **nhóm "bỏ shadow, thêm viền"** | 12 / 6 | `wujia_portal_layout`, `wujia_portal_base` | Thấp — cả hai chỉ lệch **đúng một luật**: có `--wujia-card-shadow` (BA: không shadow) và **thiếu viền**; `wujia-kpi-card` là `wholeCard` ⇒ kiểm luôn focus/hover sau khi bỏ shadow | Gọn, **và quan trọng hơn: 5/5 route dùng nó đều ĐO ĐƯỢC trên máy local** (`/portal` 8 bề mặt · `/knowledge` 2 · `/support` 1 · `/return` 1 · `/info-request` 1) ⇒ dùng để **hiệu chỉnh chính bảng đo trước–sau**. Sai ở đây thì rẻ |
| ✅ **D4c XONG (05/09)** | `wj-pc-card` (34) + `wj-pc-acct-headcard` (2) + **8 modifier** (không phải 9 — `wj-dlv-pc-card` là `id=`, không tồn tại) | **36 call site / 20 file** | 10 module portal | 🔴 Cao nhất cụm — đã đi qua: radius **18→16** (6 rule tiêu thụ token, 4 nằm NGOÀI họ), padding **24→16**, 5 call site không thể thành `<div>` | Số đo đầy đủ: **`docs/d4c-acceptance-matrix.md`**. 185 bề mặt · 0 ô mất record · 26/95 ô thấp xuống · **lồng thẻ trắng 6→0** · 33 test / 10 đột biến đỏ đúng chỗ |
| ✅ **D4d XONG (05/09)** | Mobile: `wujia-mdash-card` + `mhist`/`mknow`/`mnoti`/`mres`/`mexam`/`mdelivery-prodcard` + `wj-filter-card` — **50 lượt, không phải 51** (51 là lỗi cộng của chính bảng này) | **50 / 18** | 10 module portal | Đã đi qua: padding 16→12, viền `#EEF2F5`→`#E5E7EB` (4 họ), gap 10/14/12→8 (3 họ) | Số đo đầy đủ: **`docs/d4d-acceptance-matrix.md`**. 225 bề mặt · **0 ô mất record** · 14/95 ô thấp xuống · touch target **109px** · ảnh @1440 khác **0 pixel** · 45 test / **11 đột biến đỏ đúng chỗ** |
| ✅ **D4e1 XONG (05/09)** | `wj-pc-metric-card` — **toàn họ** (báo cáo 4 · gallery `pc_preview` 4 · khảo sát 4) | **12 / 3** | `wujia_portal_layout`, `wujia_portal_report`, `wujia_portal_inspection` | Đã đi qua: min-height là SÀN thiết kế (đệm dọc 0) nên GIỮ; gỡ override liên module SỐNG (0,2,0) | Số đo: **`docs/d4e1-acceptance-matrix.md`**. Hai chữ ký dáng khung → MỘT · 0 ô mất record · ảnh ngoài phạm vi khác 0 pixel · 52 test / 7 đột biến đỏ đúng chỗ |
| **D4e2** | `wj-rep-mcard` (3) + 2 món nợ D4d: nhịp header→body `18/23/25` · 2 inline `padding:14px 14px 0` | 3 + nợ / 5 | `wujia_portal_layout`, `_report`, `_base`, `_support`, `_exam`, `_notification` | 🔴 `wj-rep-mcard` **không có viền hẳn** ⇒ thêm viền là đổi hình học 3 khối báo cáo; card `--chart` căn cho ra đúng 258 → 260 | Chặn tz đã gỡ bằng DB copy (cách D4e1). BẮT BUỘC ảnh trước/sau @390 |
| **D4f** | Bootstrap thô `card`/`card-header`/`card-footer`/`card-body` (trừ 2 file legacy) | 75 / 13 | `wujia_portal_base`, `_return`, `_sale`, `_support`, `_knowledge`, `_info_request` | 🔴 **Blast radius lớn nhất** — `.card` là lớp dùng chung của Bootstrap, đụng vào là dễ lan ra ngoài phạm vi portal | **CUỐI**, đúng chỉ đạo. Sau D4b–D4e đã có component chuẩn thì đây chỉ còn là việc thay lớp, không phải việc quyết số |
| — | `wj-auth-card` (15) | 15 / 1 | — | — | 🔒 **THIẾT KẾ S39 — giữ dáng.** Dev tự quyết theo luật D3f |
| — | **24 lượt `wj-pc-metric-card` của màn Khảo sát** | 24 / 1 | — | — | Đi theo nhóm Khảo sát: BA ghi provisional, **và** `wujia_portal_inspection` đang `uninstalled` trên DB dev ⇒ **không đo được trên local** |
| — | Nhóm Khảo sát (11 họ / 21 lượt) | 21 / 5 | — | — | BA ghi *"provisional, chưa có seed data"* + acceptance #12. Lệch nặng nhất portal nhưng **chưa khoá field mapping**; DB dev còn `uninstalled` ⇒ chưa đo được |

### 🔴 Bài học D4b — đọc trước khi làm D4c

Số đo trước–sau đầy đủ: **`docs/d4b-acceptance-matrix.md`**. Ba điều chỉ phép đo mới thấy:

1. **Bẫy #4 của inventory §7 CÓ THẬT, và RULE 1/2 mù trước nó.** `gap` ở rule gốc SurfaceCard
   cộng chồng margin `wj_card_header` ⇒ nhịp header→body **24px** trong khi D3 vừa hội tụ 12px.
   RULE 1 + RULE 2 vẫn **sạch tuyệt đối** vì lỗi đều tay mọi card. ⇒ luật chung #3 và #8.
2. **4 thẻ KPI vốn ĐANG SO LE** dù có `min-height: 100px` — đo được `[140,140,105,105]` @1440.
   Bỏ `min-height` theo lệnh BA **đồng thời sửa lỗi có sẵn**: `height:100%` cho `[142×4]`. ⇒ #9.
3. **Baseline dễ nhiễm.** Odoo 19 **tự regenerate asset bundle theo checksum** kể cả khi không
   bật `--dev` ⇒ sửa CSS là ăn ngay. Muốn chụp baseline sau khi đã lỡ sửa thì phải
   `git stash push` đúng file CSS, đo, rồi `stash pop`.

Ngoài ra: `_render()` của `ir_qweb.py:712` **cố ý pop `values['0']`** ⇒ test slot `0` phải tạo
`ir.ui.view` chứa `t-call` thật, không bơm `0` vào `_render` được.

**Còn lại của cụm: 234 lượt / 25 họ** (D4c 87 · D4d 51 · D4e 36 · D4f 75, cộng phần treo).
`--wujia-surface-tonal` **chưa đẻ** — cố ý hoãn sang D4c, nơi nó thực sự có người dùng.

### 🔴 Bài học D4c — đọc trước khi làm D4d

Số đo đầy đủ: **`docs/d4c-acceptance-matrix.md`**. Bốn điều đáng mang sang lượt sau:

1. **Kiểm kê là SÀN.** Bảng §4 của D4a nói `--wj-pc-card-radius` có 4 rule tiêu thụ — thật ra
   **6**, vì 4 bề mặt trắng PC (`wj-pc-acct-nav`, `wj-pc-empty`, `wj-pc-order-head`, `wj-pc-cart`)
   **không có chữ "card" trong tên** nên quét tĩnh không ra. Trước mỗi lượt phải grep lại
   **từng token**, đừng tin bảng họ.
2. **QWeb Odoo 19 không đổi được tên thẻ** ⇒ call site là `<form>`/`<aside>`/`<section>` thì
   `t-call` sẽ nuốt mất thẻ (mất route POST, mất landmark). Cách đúng: **thêm thẳng class
   `.wj-surface-card`** vào thẻ gốc. D4d/D4f chắc chắn gặp lại — mobile có nhiều `<a>`/`<li>`.
3. **Guard so chuỗi con là bẫy.** `test_..._no_longer_declares_padding` đỏ oan vì
   `top: var(--wj-pc-content-padding)` **chứa** chữ "padding". Phải khớp *khai báo thuộc tính*:
   `(?:^|;)\s*padding\s*:`. Test sai → sửa test, đừng sửa code cho vừa test.
4. **Đo tuyệt đối trả lời được câu hỏi mà RULE 1/2 không trả lời nổi.** Histogram nhịp
   header→body của toàn portal PC: `12×32 · 18×14 · 23×2 · 25×2 · 0×2`, **giống hệt trước và sau**
   ⇒ D4c không xê dịch nhịp. Nguồn từng con số đã truy nguyên đến đúng dòng CSS (matrix §4) —
   phần lớn độ lệch là do **`.wj-pc-card__head` chưa migrate CardHeader**, không phải do khung.

**Còn lại của cụm: 198 lượt / 22 họ** (D4d 51 · D4e 36 · D4f 75, cộng phần treo). Tiến độ
**48/384 ≈ 12%** ⇒ `UI-SURFACECARD-001` **vẫn `Ready for Dev`**, chưa đủ để handoff.

### ✅ Việc phải làm TRƯỚC lượt D4b — dựng nền *(D4b đã làm xong)*

- Thêm token vào `_variables.css`: **`--wujia-surface-tonal` (`#F8FAFC`)** +
  `--wujia-surface-tonal-radius: 12px` + 4 token density (16/20/12/14) + 2 token gap (12/8).
  **2 trong 3 hex BA chốt đã có tên sẵn** (`--wujia-border-soft`, `--wujia-border`) — dùng
  lại, đừng đẻ token trùng hex.
- Dựng component `wj_surface_card` (khuôn `wj_card_header` của D3a): 4 biến thể
  `section`/`record`/`summary`/`transactional` × props `density`/`bodyMode`/`interactive`.
- Cột `interactive` **đọc từ CSS, không đoán**: danh sách `:is(...)` ở `_interaction.css`
  chính là bản kiểm kê "thẻ bấm được cả khối" có sẵn.

### 🟢 KHÔNG có câu hỏi nào chặn D4 — cả bốn chỗ Dev tự quyết

Bốn chỗ ban đầu tưởng phải hỏi BA, rà kỹ thì quyết được hết (inventory §6). Văn bản **thông
báo** (không phải câu hỏi) gửi BA: `docs/ba-notice-d4-surfacecard.md`.

1. **`wj-filter-card` (7) + `wj-pc-acct-headcard` (20)** — câu (a)/(d)/(e) đang treo ở
   `UI-CARDHEADER-001` chỉ hỏi về **tiêu đề và khối bên phải**, không đụng gì tới **khung**
   ⇒ tách đôi: khung làm ngay ở D4c/D4d, slot vẫn chờ. **Gỡ 27 lượt khỏi hàng chờ.**
2. **`height: 142px` card tổng Công nợ (S43)** chỏi *"không đặt fixed height"* ⇒ **giữ 142**,
   cùng luật với `wj-auth-card`: bản vẽ Figma cụ thể BA đã duyệt thắng quy tắc chung. Ghi LIMIT.
3. **Nhóm Khảo sát** — **chính BA đã viết** *"provisional, chưa khoá field mapping"* +
   acceptance #12 ⇒ để nguyên, hỏi lại là thừa.
4. **`wj-auth-card`** — THIẾT KẾ S39, giữ dáng.

*(gap card 12/8 vs nhịp SectionHeader 16/8 của C8b: **không chỏi thật** — một cái là khoảng
cách ngoài card, một cái là giữa hai card. Ghi ở inventory §7 để phiên sau khỏi nhầm.)*

## D5 — DataList `CMP-DL-001` (UI-DATALIST-001) — D5a…D5n

> Prompt: "làm cụm D5a".

- `>= 992px` DataTable semantic; `< 992px` chỉ **hai** layout: `compact-row` (mặc định) và
  `detail-card` (ngoại lệ: bù hàng, giao hàng). Cấu trúc `DataList [DataViewport + DataItem(s)
  + DataState + Pagination]`; CardHeader và Filter nằm **ngoài** DataList.
- **Tái dùng `wj_ajax_list`** (`wujia_portal_base`, S49 — 11 màn đang dùng, 136ms→32ms) làm tầng
  state/fetch; DataList là tầng render bên trên. Pagination tái dùng helper
  `page_numbers`/`group_counts` (§11), không viết mới.
- Con số: desktop header 44, single-line row min 52, multi-line 64–72, cell padding 10/16;
  mobile compact-row 64–76, detail-card 96–120, gap 8. **Không** hiện pager khi 0 hoặc 1 trang.
- Không dùng cho product grid đặt hàng, cart có stepper, featured/editorial card.
- Đo ở **1440, 1024, 992/991, 390, 360** (BA chỉ định, rộng hơn lưới cũ).

## D6 — Bù hàng UI trên component mới (BH-007, 008, 009) — `-u wujia_portal_return,wujia_sale`

> Prompt: "làm cụm D6". Chạy **sau** D2 (fallback CJK) và D4 (SurfaceCard).

- **BH-007:** card `/portal/return` cho tên sản phẩm **2 dòng**, ellipsis chỉ ở cuối dòng 2;
  dropdown `/portal/return/new` phải xem được option đầy đủ + có vùng hiện tên đầy đủ sau khi
  chọn. **Không đổi tên sản phẩm trong Odoo.**
- **BH-008:** tách 2 badge đang cùng hàng — giữ **trạng thái phê duyệt** ở dòng đầu, đưa **tiến
  độ bù** xuống dòng riêng nhãn "Tiến độ bù" (nguồn `COMPENSATION_STATUS_LABELS`). Card về
  `CMP-SC-001` variant `record`.
- **BH-009:** control mobile về touch target **44–48px** + radius token (D1 đang để 38px, đã ghi
  LIMIT); ở 360px các trường chật (SL yêu cầu, Ngày sản xuất) xuống 1 cột; thêm `id/for` hoặc
  `aria-labelledby` cho mọi label (`views/portal_return_form.xml`). Đo bằng harness a11y đã có
  (tab-walk + `forcePseudoState` cho `input[type=date]` — bẫy C8a).

### ✅ D4e1 XONG (05/09) — toàn bộ họ `wj-pc-metric-card`, 12 shell / 3 file / 3 module

Số đo đầy đủ: **`docs/d4e1-acceptance-matrix.md`**. Tiến độ cụm **110/384 ≈ 29%**.
`wujia_portal_layout` → **19.0.36.0.0**, `?v=1190 → 1200`;
`-u wujia_portal_layout,wujia_portal_report,wujia_portal_inspection` **một lần**, RC=0.
**CHỜ DEPLOY UAT.**

Kết quả cốt lõi: **hai chữ ký dáng khung về MỘT** — trước là báo cáo `pad 0/16 · gap 14 ·
minH 100` vs gallery+khảo sát `pad 0/22 · gap 16 · minH 96`; sau là cả ba
`pad 0/16 · gap 12 · minH 96`. Variant-theo-route bị xoá.

### 🔴 Bài học D4e1 — đọc trước khi làm D4e2

1. 🔴 **Con số "bỏ min-height thì thẻ thấp đi" của prompt là SAI — vì nó đoán nội dung.**
   Prompt tính 84/92 từ giả định nội dung = icon 52px; đo thật nội dung là khối 3 dòng cao
   **52–98px**, nên lấy `compact p16` thì thẻ **CAO LÊN 121–130**, tức *thưa hơn* — chỏi
   thẳng câu BA viết. **Đừng nhận một phép tính hình học trong prompt mà không đo lại.**
2. 🔴 **Bảy guard cùng "KHÔNG ĐỎ" một lượt = bộ dò hỏng, không phải guard yếu.** Bộ dò
   mutation viết `FAIL: (Subtest )?[A-Za-z]+\.[a-z_]+` nên **không khớp tên lớp có chữ số**
   (`TestSurfaceCardD4e1`). Cùng họ bẫy D4d #2 (sed trượt thụt lề), chỉ đổi chỗ trượt.
   Xác minh TAY một đột biến trước khi kết luận.
3. 🔴 **Đột biến làm XML sai cú pháp thì `-u` abort, view không đổi, test XANH OAN.** Đổi
   `<t t-call>` thành `<div>` để lại `</t>` lệch ⇒ `ExpatError`. Đột biến phải **giữ XML
   hợp lệ** (đổi sang một template khác là cách sạch).
4. **"Rule chết hay sống" phải đếm lúc chạy.** `.wj-rep-pcmetrics .wj-pc-metric-card` khớp
   **đúng 4 phần tử ở cả 5 khổ** ⇒ SỐNG, khác hẳn bẫy #4 của D4d (0 phần tử).
5. **Không phải "đo được" là "hết chặn nghiệp vụ".** Màn Khảo sát nay đo được, nhưng cờ
   *provisional* của BA gắn vào **field mapping**, không gắn vào khung ⇒ migrate khung là
   tự quyết được, và phải ghi rõ là không chốt hộ field mapping.
6. **Kiểm kê sai lần thứ 4.** `wj-pc-metric-card` 44→**12**, `wj-rep-mcard` 16→**3**. Và
   `scripts/qa/wj_inventory.py` mà prompt nhắc **không tồn tại**.
7. **Chia lượt theo HỌ, không theo file.** Chẻ một họ giữa hai lượt = tự tạo cửa sổ
   variant-theo-route trong lúc chờ lượt sau.

### 🔴 Bài học D4d — đọc trước khi làm D4e

Số đo trước–sau đầy đủ: **`docs/d4d-acceptance-matrix.md`**. Tiến độ cụm **98/384 ≈ 26%**.

1. 🔴 **`logfile` trong `odoo.conf` nuốt sạch stdout — "RC=0, 0 ERROR" trên log RỖNG là XANH
   GIẢ.** Ba lần chạy test đầu tiên đọc ra "0 lỗi" từ một file 0 dòng. Bằng chứng thật nằm ở
   `logs/<năm>/<tháng>/<ngày>.log` (`wujia_core` tự xoay log theo ngày). Đọc đúng chỗ mới lộ
   **4 test đỏ**. Luôn `N=$(wc -l < $L)` **trước** mỗi lần chạy rồi `tail -n +$((N+1))`.
2. 🔴 **Đột biến không áp được cũng báo "guard yếu".** `sed` neo `^    --wujia-surface-pad-compact`
   trượt vì dòng thật thụt **8 dấu cách** ⇒ bảng in "KHÔNG ĐỎ" cho một guard hoàn toàn tốt. Phải
   xác nhận đột biến **đã vào file** (`grep` lại) trước khi kết luận.
3. **`xml_id` phải TRA, không được ĐOÁN.** 3/4 test đỏ chỉ vì đoán `..._page` trong khi tên thật
   là `portal_knowledge_detail` / `portal_exam_schedule` / `mres_shell`. Một file XML có nhiều
   `<template id=…>`; dò chủ sở hữu của một dòng bằng `awk '/<template id="/{…} NR==N{print}'`.
4. **Kiểm kê là SÀN — lần này SÀN hụt 26 lượt và một mệnh đề SAI.** Xem `d4-surfacecard-inventory.md`
   §12.2: `wj-empty-state` bị ghi "không khai nền + bo góc" trong khi khai đủ, và là **20** lượt
   chứ không phải 5. Đọc CSS tĩnh không thay được **đo lúc chạy** (§12.3: `mknow-card` đo 16 chứ
   không phải 14 vì `.wujia-mknow-article` đè).
5. **Đo tuyệt đối bắt được cái RULE 1/2 mù.** Bẫy `margin-top: -2px` bù cho `gap: 10` — cặp con
   `wj-filter-dates → wj-filter-chips` đo **8px** trong khi mọi cặp anh em đo **10px**. Giữ `-2px`
   khi gap về 8 sẽ thành **6px** mà **RULE 1/2 vẫn xanh**.
6. **Rule chết phải chứng minh bằng số phần tử khớp lúc chạy, không phải bằng suy luận.**
   `.wujia-mnoti .wujia-mknow-card` khớp **0 phần tử** ⇒ gỡ là vô hại, có bằng chứng.
7. **Không phải màn nào "không đo được" cũng cần DB copy.** Chốt đầu phiên là dựng
   `wujia_tea_d4d` + POST một đơn cho `wujia-mres-card`; hoá ra `/portal/order/rejected` là
   **GET thuần** và `/portal/order/submitted/<id>` chỉ cần **một SO portal sẵn có đúng franchise**
   (`S00002`). **Tra dữ liệu sẵn có trước khi dựng hạ tầng** — và không sinh dữ liệu là đúng QA §10.
8. **Ảnh khác 0 pixel là bằng chứng "không rò rỉ" mạnh hơn mọi bảng số.** `/portal` @1440 trước/sau
   khác **đúng 0 pixel** (`PIL.ImageChops.difference(...).getbbox() is None`).
9. **`:is()` lấy đặc hiệu của đối số MẠNH NHẤT.** Ba danh sách hover/pressed ở `_interaction.css`
   là **(0,3,0)** vì chứa `.wj-pc-page-btn:not(.is-active):not(.is-disabled)` — đây là lý do
   Luật #1 bắt **giữ lớp cũ qua `sc_class`**; bỏ đi là hover/pressed của 41 thẻ chết câm.
10. **Quét đặc hiệu phải loại tên con BEM.** `'.wujia-mexam-card' in selector` khớp cả
    `.wujia-mexam-card-badge` ⇒ 9/15 "vi phạm" là giả. Cũng chính lỗi này thổi kiểm kê thô lên 51.

## R1–R5 — Optimize (sau khi 11 issue cụm D đã `Ready for Retest`)

> Prompt: "làm R&lt;n&gt;". Nội dung + nghiệm thu đã viết sẵn ở `docs/refactor-plan.md`.

R1 dọn comment sử ký + hex→token · R2 date format sót · R3 perf nhỏ + **bug thật
`/portal/reports/orders` 500 do tz `Asia/Saigon`** · R4 spec-drift viết note gửi BA (0 code) ·
R5 quyết định giữ hay bỏ layer utility class.

---

**Cuối lứa:** chapter `.tex` + rebuild PDF qua `scripts/build-doc.sh`, rồi `/wujia-end-sprint`.
Đừng đề xuất end sprint khi chưa đóng hết cụm D.
