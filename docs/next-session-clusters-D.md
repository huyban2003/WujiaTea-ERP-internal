# Cụm D1–D6 + R1–R5 — prompt cho từng session

**Nguồn:** phiên phân cụm 2026-08-25 (11 issue `Ready for Dev` BA đổ lên `5. Issue List`
sau ngày 24/8 — 7 issue bù hàng audit UAT 23/08 + 3 issue chuẩn hoá component + 1 issue font).
Kế hoạch đầy đủ: `~/.claude/plans/bright-conjuring-sutherland.md`; chuẩn nghiệm thu §13
`wujia-compact-summary.md`.

**Cách dùng:** `/wujia-start` → nói "làm cụm D&lt;n&gt;" → Claude đọc file này, lấy đúng khối
prompt của cụm đó rồi bắt tay.

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

**Tiến độ cụm:** D1 ✅ 25/08/2026 (4 issue → Ready for Retest; `-u wujia_portal_return,wujia_sale,wujia_portal_layout`
trên DB copy `wujia_tea_d1` port 8065 → RC=0; **26/26 đo đạt (100%)**, 6 test mới + 33 hồi quy
= 39 test xanh, lưới B4 286/286, tab-walk 2 viewport sạch; bảng đối chiếu
`docs/d1-acceptance-matrix.md`) · **D2 ✅ 26/08/2026** (`b70d26a`, WJ-PORTAL-UI-002 →
Ready for Retest; `-u wujia_portal_layout` trên DB copy `wujia_tea_d2` port 8066 → RC=0;
**14/14 acceptance**, chỗ ≠ Inter **145 → 0** trên 80 ô đo **ngay trên UAT**, B4 286/286,
tab-walk 331 stop giữ nguyên thứ tự + ring; `docs/d2-acceptance-matrix.md` +
`docs/d2-font-inventory.md`) · D3 ⬜ · D4 ⬜ · D5 ⬜ · D6 ⬜ · R1–R5 ⬜

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

- **D3a:** dựng `docs/d3-cardheader-inventory.md` liệt kê mọi heading **nằm trong card**
  (nghi vấn: `wujia-content-card-header*` ~30, `wj-pc-acct-headcard` 33, title trong
  `wj-pc-card` 154, `wujia-mdash-title`, label 11px viết hoa của debt). Phân 3 loại
  PageHeader / SectionHeader / **CardHeader**. Dựng `wj_card_header` cạnh `wj_section_header`,
  API: leading `[icon? + title + subtitle?]` + trailing **tối đa một** trong
  `meta/count | action | control`; props `variant=compact|regular` (compact mặc định).
  Migrate 3–4 route mẫu, đo đủ rồi mới nhân.
- **D3b…D3n:** migrate hết call site, mỗi session một nhóm màn, mỗi session một lần `-u`,
  mỗi session đo lại B4 286/286 + tab-walk. Issue **giữ `Ready for Dev`** cho tới khi đủ 100%
  (tiền lệ C8a→C8b).
- Con số bắt buộc: desktop compact 18/24/600–700, regular 20/28/700; mobile compact 16/22/600–700,
  regular 18/24/700; header→body 12/8. **CardHeader không tự thêm padding, không đặt chiều cao.**
- ⚠️ `_wujia_theme.css:35` ép `.content-wrapper h1..h6{font-weight:700!important}` (UI-06/S35)
  ⇒ weight khác **không ăn**; C8 đã chốt giữ 700 + ghi LIMIT. Cần 600 thì xử ở scope, **không**
  gỡ rule global.
- ⚠️ Odoo 19 QWeb không có directive đặt tên thẻ động (`ir_qweb.py:1705`) ⇒ heading level phải
  rẽ `t-if/t-elif/t-else` như `wj_section_header`.
- ⚠️ Trailing slot render **markup thô không bọc element** để `wj_ajax_list` swap được.

## D4 — SurfaceCard `CMP-SC-001` (UI-SURFACECARD-001) — cụm to nhất, D4a…D4n

> Prompt: "làm cụm D4a". 4 variant BA chốt: `section` / `record` / `summary` / `transactional`;
> props `density` (compact mặc định), `bodyMode` (`padded|flushBody`), `interactive`
> (`none|wholeCard|actions`).

- **D4a:** kiểm kê họ card (`wj-pc-card` 154, `wujia-mdash-card` 36, `wujia-morder-card` 35,
  `wujia-content-card*` ~90, `wujia-mexam/mhist/maccount/mknow-card`…) → bảng
  `docs/d4-surfacecard-inventory.md` map **từng cụm class → variant** theo đúng bảng "MAPPING
  VARIANT + DATA THEO MÀN HÌNH" BA viết sẵn. Dựng component + migrate 1 màn mẫu mỗi variant, đo.
- **D4b…D4n:** migrate theo **nhóm component, không theo route** (BA cấm tạo variant theo tên
  route/màn hình).
- Con số: desktop radius 16, border 1px `#EEF2F5`, **không shadow mặc định**, padding compact 16
  / regular 20, gap 12; mobile radius 14, border `#E5E7EB`, padding 12/14, gap 8; **cấm lồng
  white card trong white card** (vùng phụ dùng tonal inset `#F8FAFC` radius 12).
- 🔴 Đây là chỗ **áp số BA làm đổi mật độ thật** (desktop đang nhiều card padding 22–28) ⇒ mỗi
  màn một bảng đo trước–sau; ghi LIMIT ở chỗ số mới **mâu thuẫn issue đã Pass** (nhịp 16/8 của
  `CMP-SH-001` chốt ở C8b; số đo debt của S43/C3).
- Hex trong spec phải vào `_variables.css` thành token `--wujia-*` (rule "không hex cứng").

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

## R1–R5 — Optimize (sau khi 11 issue cụm D đã `Ready for Retest`)

> Prompt: "làm R&lt;n&gt;". Nội dung + nghiệm thu đã viết sẵn ở `docs/refactor-plan.md`.

R1 dọn comment sử ký + hex→token · R2 date format sót · R3 perf nhỏ + **bug thật
`/portal/reports/orders` 500 do tz `Asia/Saigon`** · R4 spec-drift viết note gửi BA (0 code) ·
R5 quyết định giữ hay bỏ layer utility class.

---

**Cuối lứa:** chapter `.tex` + rebuild PDF qua `scripts/build-doc.sh`, rồi `/wujia-end-sprint`.
Đừng đề xuất end sprint khi chưa đóng hết cụm D.
