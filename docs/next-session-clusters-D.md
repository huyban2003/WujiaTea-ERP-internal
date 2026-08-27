# Cụm D1–D6 + R1–R5 — prompt cho từng session

**Nguồn:** phiên phân cụm 2026-08-25 (11 issue `Ready for Dev` BA đổ lên `5. Issue List`
sau ngày 24/8 — 7 issue bù hàng audit UAT 23/08 + 3 issue chuẩn hoá component + 1 issue font).
Kế hoạch đầy đủ: `~/.claude/plans/bright-conjuring-sutherland.md`; chuẩn nghiệm thu §13
`wujia-compact-summary.md`.

**Cách dùng:** `/wujia-start` → nói "làm cụm D&lt;n&gt;" → Claude đọc file này, lấy đúng khối
prompt của cụm đó rồi bắt tay.

---

## 📌 BÀN GIAO cho phiên sau (chốt 28/08/2026)

**Prompt gõ vào phiên sau:**

> `/wujia-start`
> làm cụm D3b. Đọc `docs/d3-cardheader-inventory.md` §bảng theo file để lấy nhóm màn kế tiếp, và `docs/d3-acceptance-matrix.md` §LIMIT để biết 4 chỗ đang treo chờ BA.

**🚚 CHỜ DEPLOY: D3a.** Nhánh `dev/2026-08-27-d3a` đã merge `main`. Chủ dự án deploy UAT bằng
`-u wujia_portal_layout,wujia_portal_support,wujia_portal_delivery,wujia_portal_base,wujia_portal_return,wujia_sale`
(không module mới, không cập nhật dữ liệu, không migration; `?v=1178` đã bump sẵn). Deploy xong
thì **chạy `qa_deploy_mark.py`** — nhưng lưu ý `UI-CARDHEADER-001` **vẫn `Ready for Dev`**, chưa
có gì để `qa_sync.py` handoff; entry ledger đã soạn sẵn **dạng comment** trong
`docs/qa-issue-ledger.yaml`, D3n bỏ `#` là chạy được (tiền lệ C8a).

**Việc tồn 27/08 — ✅ XONG.** Nhãn option "tất cả" của bộ lọc bù hàng nay gom về **một hằng**
`FILTER_ALL_LABEL` cạnh `FILTER_OPTIONS` (`wujia_portal_return/controllers/portal.py`), cả PC
lẫn mobile đều `t-out="filter_all_label"`. Đo trên browser: PC `— Tất cả —` → **`— Tất cả trạng
thái —`**, khớp mobile. `value=""` không đổi ⇒ kết quả lọc bất biến.

### Còn treo sau D3a — đọc trước khi làm D3b

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

**Tiến độ cụm:** D1 ✅ 25/08/2026 (4 issue → Ready for Retest; `-u wujia_portal_return,wujia_sale,wujia_portal_layout`
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
font Inter 514/514 y hệt; `docs/d3-acceptance-matrix.md`) · D3b…D3n ⬜ · D4 ⬜ · D5 ⬜ ·
D6 ⬜ · R1–R5 ⬜

🚚 **D1 + D2 ĐÃ DEPLOY UAT 27/08** (`wujia_portal_layout 19.0.32.4.0` · `wujia_portal_return
19.0.2.7.0` · `wujia_sale 19.0.4.3.0`, xác nhận XML-RPC) **+ đo lại chỉ-đọc ngay trên UAT**:
D2 **14/14** (chỗ ≠ Inter 145→0, `scrollHeight`/số dòng/`font-weight`/icon **0 lệch trên 80 ô**,
B4 286/286, tab-walk 346 stop) · D1 **27/28**.
🚚 **D3a chờ deploy UAT** — xem lệnh + version ở đầu §Bàn giao.

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
- **D3b…D3n:** migrate hết call site theo **bảng-theo-file** ở §kế hoạch của inventory, mỗi
  session một nhóm màn, mỗi session một lần `-u`, mỗi session đo lại B4 286/286 + tab-walk.
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
