# E5c — Ma trận nghiệm thu · khép `UI-LISTCARD-001` (STT 136, dòng tuyệt đối **129**)

Phiên đóng issue của cụm E5. E5a dựng component · E5b1 6 call site · E5b2 5 call site cuối
(**22/22 call site** đã về `CMP-LC-001`). E5c **không migrate thêm màn nào**: trả nợ *nhịp* và
*bề ngang của trang*, chạy regression **8 khổ**, chốt 2 câu hỏi BA còn treo, vá một mốc đóng băng
rỗng, rồi ghi sổ đóng issue.

- Đo: DB local `wujia_e4b1`, server **8090/8091** (`--dev=assets`), test **8098/8099**.
- Không đụng `wujia_portal_inspection` · `wujia_franchise*` · `wujia_mobile_*` (code anh Thái).
- Không đổi quyền / ngày / tiền / state / filter / pager / workflow.

## Bảng nghiệm thu

| # | Phép đo | Ngưỡng | Kết quả |
|---|---|---|---|
| 1 | `rhythm.filter_to_next` 7 route | 24 → **16**, 7/7 | ✅ **8/8** (thêm `/portal/reports/orders`) |
| 2 | Đệm item + gutter trang | đệm `12px`, gutter 12/12, 0 cộng dồn | ✅ 16 route đo lại đều 12/12 |
| 3 | `wj_listcard.py` 12 route × **8 khổ** | 0 vi phạm anatomy, 0 cắt mã/tiền | ✅ **96 ô, 0 vi phạm** |
| 4 | Field inventory trước/sau | 0 trường mất, 0 lệch số record | ✅ 16 route × 2 khổ, **194 record, 0 vấn đề** |
| 5 | Chữ ký DOM đóng băng | trước = sau | ✅ Home · bảng PC · `/portal/order` (chữ ký **cả trang** mới) |
| 6 | `wj_nesting` · `wj_datalist` · `wj_measure` | 0 / 0 / 0 tràn · 0 lỗi JS | ✅ 0 / 0 / 0 tràn ngang · 0 lỗi JS · 0 record mất |
| 7 | Suite kèm `-u` | 0 đỏ (mốc E5b2 653) | ✅ **687 tests, 0 failed, 0 error** |
| 8 | `check_layers.py` | đúng 3 R1–R5 + 2 R7 có sẵn | ✅ 3 + 2, không thêm |
| 9 | Mutation | mỗi mũi đỏ đúng guard của nó | ✅ **10/10** + 2 mũi cấp công cụ |
| 10 | Đối chiếu `Kết quả mong muốn` STT 136 | **≥90%** | ✅ **23/24 gạch = 95,8%** (xem §Đối chiếu) |

## Đã làm

### 1. Nhịp *thanh lọc → nội dung* 24 → 16 (G2)

Gốc: `.wj-filter-card { margin-bottom: 16px }` **cộng** `gap: 8px` của khung trang ⇒ 24.
Sửa ở **một chỗ duy nhất** (khung), khai bằng **token** chứ không phải số cứng:

```css
.wj-filter-card { margin-bottom: var(--wujia-mshell-content-gap); }   /* 8 + 8 = 16 */
```

Trang đổi nhịp thì thanh lọc đổi theo — hai con số không còn nằm hai nơi.

### 2. Đệm item 12 (LC-07) + gutter trang 12 (LC-08)

- `_components.css`: `.wj-data-list--compact-row .wj-data-item` và
  `.wj-data-list--detail-card .wj-data-item` — `padding: 12px 14px` → **`padding: 12px`**.
  Nhánh `--inset` (`12px 0`) giữ nguyên: item ở đó không có viền riêng.
- `_variables.css` (khối mobile): `--wujia-mshell-content-pad-x: 16px` → **`12px`**.
- **Ổ gà tìm ra khi đo**: `/portal/purchase-history` và `/portal/order` render **bên trong**
  `.content-wrapper` của Vuexy (đệm 16,8px), còn các màn BlankShell (`.wujia-mpage`) ăn token ⇒
  lệch 5px giữa hai họ màn. Vá ở khung, một rule, không `:has()`, không đổi DOM, **không**
  `!important` (để trang tự bỏ lề — Home — còn thắng được):

```css
@media (max-width: 991.98px) {
    html body .content .content-wrapper {
        padding-left:  var(--wujia-mshell-content-pad-x);
        padding-right: var(--wujia-mshell-content-pad-x);
    }
}
```

### 3. Vùng chạm ≥44 của link hành động

Regression 8 khổ bắt được nút **“Chọn”** ở `/portal/exam/register` chỉ **37×21** — có từ E5b2, không
phải do E5c (đã chứng minh bằng đo TRƯỚC/SAU trên cùng một cây mã). Nới vùng chạm mà **không** đội
cao card, bằng cặp đệm + lề âm:

```css
.wj-lc__link { display: inline-block; padding: 12px 4px; margin: -12px -4px; }
```

⇒ vùng chạm 45×45, chiều cao card **không đổi một pixel** (so `wj_listcard` 5 khổ mobile trước/sau).

### 4. Vá mốc đóng băng rỗng `/portal/order`

`/portal/order` không có `.wj-data-list` lẫn `table.wj-data-table` ⇒ “chữ ký DOM trước = sau” ở đó
**chứng minh rỗng** (E5b2 ghi nhận). `wj_listcard_inventory.py` nay: route đóng băng không có vùng
nào thì lấy chữ ký **cả trang** (`.wujia-mpage` / `.content-wrapper` / `.app-content`), loại phần
biến động (`[data-wj-volatile]`, số giỏ, đồng hồ, canvas/ApexCharts, `.resize-triggers`), và **báo
`MỐC RỖNG`** khi cả hai bên đều rỗng. Khớp route đóng băng đổi từ `startswith` sang **khớp đúng**
(trước đó `--frozen /portal` vô tình đóng băng mọi route con).

### 5. Guard mạnh thêm hai bậc (`scripts/qa/wj_listcard.py`)

- Đọc **variant** của từng card (`compact-row` / `detail-card`) và kiểm **dải cao** theo variant.
- Ở khổ **≥992** danh sách mobile bị media query ẩn ⇒ trước đây guard báo “0 card — CHƯA MIGRATE”
  **33 lần sai**. Nay đếm DOM thật (`pc_bản_ghi`, `pc_khối_nội_dung`) và chỉ kêu khi **cả hai** = 0
  (bẫy: `/portal/exam/register` bản PC là **form**, không có bản ghi mà vẫn đúng).

## Hai câu hỏi BA — Dev tự quyết (chủ dự án uỷ quyền trong phiên)

1. **GIỮ ô icon `.wj-lc__tile` 32×32** (Thông báo · Kiến thức · danh sách nhân sự màn Thi).
   Bỏ thì Thông báo mất tín hiệu màu theo loại. ⇒ **ngoại lệ có chủ đích với LC-06/LC-07**
   (“không icon trang trí lớn trước tên”): 32×32 là **ô tín hiệu trạng thái**, không phải ảnh minh hoạ.
2. **Nới dải cao hai variant** — đề xuất mang từ E5b2 là 64–84 / 96–150, nhưng **đo thật 96 ô** cho
   thấy phân bố rộng hơn: `compact-row` **78–111**, `detail-card` **96–154** (email xuống dòng ở
   `/portal/franchise-information`, ghi chú kết quả thi, chữ xuống dòng ở khổ 320). ⇒ chốt
   **`compact-row` 64–112** · **`detail-card` 96–156**. LC-02 đòi auto-height nên **không** ép cứng
   chiều cao để lấy số đẹp.
   *FYI cho BA*: hai dải nay **chồng nhau** (96–112) ⇒ chiều cao **không còn** là dấu hiệu phân biệt
   variant; phân biệt bằng **class** (`--compact-row` / `--detail-card`), dải cao chỉ còn là phanh
   chống card phình.

## Đối chiếu `Kết quả mong muốn` STT 136 — 23/24 gạch (95,8%)

| Gạch | Ý | Kết quả |
|---|---|---|
| 1 | 1 record = 1 card · name trái / state phải · header + 2–3 hàng phụ · cột linh hoạt · auto-height | ✅ 22/22 call site, `wj_listcard` 96 ô 0 vi phạm |
| 2 | padding 12 · radius 12 · gap 8 · header-body 8 · gap hàng 6–8 · title 15–16/600 · badge 12 · metadata 13–14 | ✅ (padding 12 khép ở phiên này) |
| 2 | **không icon trang trí lớn** | ⚠️ **lệch có chủ đích**: giữ `.wj-lc__tile` 32×32 (quyết định ở trên) |
| 2 | không divider / shadow trong card | ✅ |
| 3 | trường ngắn cùng hàng · dài chiếm cả hàng · không cắt mã/tiền/badge · giữ đủ dữ liệu | ✅ inventory 194 record, 0 trường mất |
| 4 | LC-01–LC-32 + mapping từng route · không đổi quyền/ngày/tiền/state/filter/pager | ✅ (3 mục **ngoài phạm vi** ghi rõ bên dưới) |
| 5 | regression 8 khổ · keyboard/actions/sticky · bằng chứng trước/sau + field inventory · build hợp lệ | ✅ 96 ô · vùng chạm ≥44 · 2 file JSON trước/sau |

**Ba mục ngoài phạm vi (đã chốt từ `prompt-e5c.md`, không tính vào mẫu số):**
`LC-20` Khảo sát — code anh Thái, **defer vĩnh viễn** theo luật 08/09 · `LC-23` Home preview giữ
grouped rows (chính issue yêu cầu **giữ** Home preview) · `LC-27` lệch dữ liệu giữa spec và thực tế,
chỉ **ghi nhận**.

## Số đo trước → sau (khổ 390)

| Route | nhịp lọc→kế | gutter | số record |
|---|---|---|---|
| `/portal` (Home) | — | 16 → **12** | 9 = 9 |
| `/portal/purchase-history` | 24 → **16** | **17 → 12** | 10 = 10 |
| `/portal/delivery` | 24 → **16** | 16 → **12** | 20 = 20 |
| `/portal/notification` | 24 → **16** | 16 → **12** | 10 = 10 |
| `/portal/support` | 24 → **16** | 16 → **12** | 20 = 20 |
| `/portal/return` | 24 → **16** | 16 → **12** | 20 = 20 |
| `/portal/knowledge` | 24 → **16** | 16 → **12** | 12 = 12 |
| `/portal/exam` | 24 → **16** | 16 → **12** | 10 = 10 |
| `/portal/reports/orders` | 24 → **16** | — | 0 = 0 |
| `/portal/exam/register` · `/portal/exam/registration/9` · `/portal/debt?all=1` · `/portal/debt/payment-history` | — | 16 → **12** | 3·2·3·47 không đổi |
| `/portal/franchise-information` | — | 31 → **27** | 10 = 10 |

`/portal/franchise-information` đo **27** chứ không phải 12 vì danh sách ở đó là biến thể `--inset`:
12 (gutter trang) + 14 (đệm trong của SurfaceCard) + 1 (viền). Đây là **phạm vi SurfaceCard**
(`UI-SURFACECARD-001`), không phải LC-08 — ghi nhận, không sửa trong E5c.

## Ba dấu hiệu đã soi và **không** phải lỗi của E5c

| Dấu hiệu | Kết luận |
|---|---|
| `/portal/debt?all=1`: card cuối chạm mép thanh cố định (818 vs 817) | **có từ trước** — số đo TRƯỚC và SAU **giống hệt**; trang còn **125px** đuôi cuộn nên thanh không che bản ghi |
| `/portal/exam/register`: nút “Chọn” 37×21 | **có từ trước** (E5b2) — **đã sửa trong phiên này**, nay 45×45 |
| `/portal/knowledge` ≥992: 12 link chữ nhỏ | bản **PC**, đích chuột — luật chạm 44 không áp cho khổ ≥992 |

## Thay đổi mã

| File | Đổi |
|---|---|
| `_components.css` (`?v=1313 → 1314`) | nhịp `.wj-filter-card` theo token · đệm item `12px` ×2 variant · vùng chạm `.wj-lc__link` |
| `_variables.css` (`?v=1295`) | `--wujia-mshell-content-pad-x: 16px → 12px` (khối mobile) |
| `_wujia_theme.css` (`?v=1221`) | 1 rule: `.content-wrapper` lấy gutter từ token ở khổ mobile |
| `wujia_portal_layout/__manifest__.py` | `19.0.55.0.3 → 19.0.55.1.0` |
| `wujia_portal_layout/tests/test_e5_list_card.py` | +5 test (đệm 12 · không tự thêm gutter · nhịp = 2 nhịp trang · token gutter 12 · vùng chạm ≥44) |
| `wujia_portal_base/tests/test_mobile_rhythm.py` | +3 test quét chéo (token khai ở khối mobile · wrapper lấy token, không `!important` · không trang nào gõ số gutter riêng) + helper `_media_block` |
| `wujia_portal_base/tests/test_scan_d5_data_list.py` | 2 assert `12px 14px` → `12px` |
| `scripts/qa/wj_listcard.py` | dải cao theo variant · nhận diện khổ PC (hết 33 báo sai) |
| `scripts/qa/wj_listcard_inventory.py` | chữ ký **cả trang** cho route không có vùng · `MỐC RỖNG` · khớp route đóng băng **đúng** thay vì `startswith` |

## Sự cố đã xử trong phiên

1. **Baseline phải đo lại bằng công cụ đã vá** — guard cũ báo sai 33 ô ở ≥992. Cách làm:
   `git stash push -- custom/` → đo TRƯỚC → `git stash pop` (3 lần, lần nào cũng kiểm tra cây mã đã
   về đúng).
2. **Dải cao lấy từ ghi chú E5b2 (64–84 / 96–150) cho 38 vi phạm** — số ghi chú là mẫu nhỏ; số đo
   thật rộng hơn. Bài học: **đo trước, chốt ngưỡng sau**, đừng chốt ngưỡng từ ghi chú.
3. **Chữ ký DOM `/portal/reports/orders` nhảy** — hai lần, hai nguyên nhân: id ngẫu nhiên +
   toạ độ animation của ApexCharts, rồi `.resize-triggers` có `width` inline **bám bề ngang khung**
   (357 → 365 sau khi đổi gutter). Loại cả hai khỏi chữ ký; xác nhận DOM ổn định qua **3 lần chạy liên tiếp**.
4. **`--frozen /portal` đóng băng nhầm mọi route con** (khớp tiền tố) → khớp đúng.
5. **Test `test_wrapper_lay_gutter_tu_token` đỏ oan** vì trúng rule PC `@media (min-width: 1200px)`
   có `!important`; regex `\n\}` cắt cụt khối media → thay bằng helper **đếm ngoặc** `_media_block`.

## Lệnh chạy lại

```bash
PY=/opt/homebrew/Caskroom/miniconda/base/envs/odoo19/bin/python3

# server đo (CSS đọc thẳng từ file nhờ --dev=assets)
$PY odoo19/odoo-bin -c config/odoo.conf -d wujia_e4b1 --db-filter='^wujia_e4b1$' \
  --http-port=8090 --gevent-port=8091 --dev=assets

# đo
$PY scripts/qa/wj_listcard.py --base http://127.0.0.1:8090 --portal-login em.hcm \
  --breakpoints 320 360 390 430 991 992 1024 1440 --json docs/e5c-listcard-after.json
$PY scripts/qa/wj_listcard_inventory.py --base http://127.0.0.1:8090 --portal-login em.hcm \
  --diff docs/e5c-inventory-before.json --out docs/e5c-inventory-after.json \
  --frozen /portal/order /portal /portal/reports/orders
$PY scripts/qa/wj_nesting.py  --base http://127.0.0.1:8090 --portal-login em.hcm
$PY scripts/qa/wj_datalist.py --base http://127.0.0.1:8090 --portal-login em.hcm
$PY scripts/qa/wj_measure.py  --base http://127.0.0.1:8090 --portal-login em.hcm --out after.json
$PY scripts/qa/check_layers.py

# mutation (tự phục hồi cây mã kể cả khi bị kill)
$PY scratchpad/e5c/mutations.py

# test — LUÔN kèm -u (tests wujia_franchise còn import file đã xoá) và --log-handler INFO
$PY odoo19/odoo-bin -c config/odoo.conf -d wujia_e4b1 --db-filter='^wujia_e4b1$' \
  --http-port=8098 --gevent-port=8099 \
  -u wujia_portal_layout,wujia_portal_base,wujia_portal_sale,wujia_portal_debt,wujia_portal_exam,\
wujia_portal_delivery,wujia_portal_knowledge,wujia_portal_notification,wujia_portal_return,\
wujia_portal_support,wujia_portal_purchase_history,wujia_portal_report,wujia_portal_order_window,\
wujia_portal_info_request \
  --test-enable --log-handler "odoo.tests.result:INFO" --stop-after-init
# đọc kết quả ở logs/<năm>/<tháng>/<ngày>.log, không đọc stdout
```

## Soi mã đối kháng (Codex) — phạm vi **toàn cụm E5** (`cf6d2b0^..HEAD`)

4 finding, thẩm định lại từng cái trên mã thật:

| # | Finding | Phán quyết | Xử lý |
|---|---|---|---|
| P1 | Lệnh deploy chỉ nâng 2 mô đun, trong khi cụm E5 sửa view nằm trong DB của **8 mô đun** nữa; Odoo không nạp lại XML của mô đun phụ thuộc khi chỉ nâng mô đun nền ⇒ UAT sẽ có CSS mới mà thẻ cũ | **THẬT** — `git diff --name-only cf6d2b0^..HEAD -- '*.xml'` đúng **10 mô đun** | Sửa `build_override` trong ledger thành **10 mô đun** và ghi lại ô Build/Deploy của dòng 129 |
| P2 | Chấm "chưa đọc" `.wujia-mnoti-dot` là `<span>` rỗng **inline** trong `.wj-lc__state` (không phải flex) ⇒ `width/height` không ăn, chấm 0px | **THẬT** — đo trình duyệt: `[0, 19, 'inline']` ×7, và class này **ra đời ở E5b1** nên chấm **chưa từng hiện** | `display: inline-block` + `vertical-align: middle`; đo lại **8×8 inline-block**; +1 test ở `wujia_portal_notification`; bump `19.0.2.18.0` |
| P2 | Nhánh LC-02 của `wj_listcard.py` chỉ có `pass` ⇒ chiều cao ép cứng lọt lưới; `height` tính toán luôn ra px nên không dùng để kết tội | **THẬT** | Thay bằng dấu hiệu **thật**: `scrollHeight > clientHeight` ⇒ "nội dung bị bó". Chứng minh: ép `height: 70px` cả hai variant ⇒ **10 finding LC-02**; gỡ ra ⇒ 0 |
| P2 | `wj_listcard_inventory.py` ghi `final_url` nhưng **không kiểm**: hai lượt cùng đậu ở trang đăng nhập/lỗi vẫn "giống nhau" ⇒ Pass rỗng | **THẬT** | Thêm cờ `redirected` + dòng `CHUYỂN HƯỚNG` trong `diff()`. Chứng minh: `--routes /odoo` (đá về `/my`) ⇒ **1 vấn đề CHUYỂN HƯỚNG** |

Phát sinh khi vá P2 thứ hai: chấm 8×8 nay có ô thật nên `wj_listcard` tính nó là "khung con trong
card" (**35 vi phạm LC-01 giả**). Sửa ở đúng tầng khái niệm: **phần tử ≤ 12px không thể là khung
trong khung** — nó là *chấm tín hiệu*. Đo lại: **0 vi phạm**. Suite sau khi vá: **687 tests, 0 đỏ**.

## Đo lại trên UAT sau khi deploy (19/09/2026, chỉ đọc, tài khoản admin)

`scratchpad/e5c/uat_full.py` — **14 route × 5 khổ** (320 · 390 · 430 · 991 · 1440) trên
`http://113.161.187.126:8019`: **42 ô đạt · 0 ô lệch · 0 lỗi JS**; 28 ô còn lại là **danh sách
rỗng** (admin không gắn cửa hàng nên Lịch sử mua hàng · Thi · Công nợ · Đặt hàng không có bản ghi)
nên không kết luận, đánh dấu riêng chứ không tính là Pass.

| Phép đo | Kết quả trên UAT |
|---|---|
| Nhịp lọc → nội dung | **16** ở mọi màn có thanh lọc (Thông báo · Hỗ trợ · Đổi trả · Kiến thức · Thi · Giao hàng) |
| Gutter item (≤991) | **12/12** ở mọi màn có bản ghi |
| Đệm item | **`12px`** |
| Gutter khung trang | **12/12** ở `/portal/order`, `/portal/purchase-history`, `/portal/notification` và cả `/portal/inspection` (màn của anh Thái) |
| Vùng chạm ≥44 (≤991) | **0 chỗ thiếu** |
| Tràn ngang · lỗi JS | **0 · 0** |
| Bản vá chấm "chưa đọc" | có mặt trong bảng kiểu dáng của máy chủ: `display: inline-block` |

Luật chạm 44 **chỉ áp cho khổ ≤991** (ngón tay); ở 1440 các link chữ của Kiến thức cao 19px là
đích **chuột**, không phải vi phạm — lần chạy đầu tool chưa phân biệt nên báo nhầm 1 ô, đã sửa.

Hai thứ **không** kiểm được bằng tài khoản admin (danh sách rỗng): **chấm "chưa đọc" hiển thị
thật** và **vùng chạm nút “Chọn”** ở bước 1 màn đăng ký thi. Cả hai đã đo bằng trình duyệt trên DB
local (8×8 và 45×45) — xin BA xác nhận bằng tài khoản cửa hàng khi retest.

## Trạng thái issue

`UI-LISTCARD-001` → **`Ready for Retest`**, Build/Deploy *Chờ deploy UAT*. Dev **không** đặt `Done`,
**không** tự deploy UAT. BA retest: nhịp dưới thanh lọc, bề ngang danh sách (12 hai bên, đồng loạt
mọi màn mobile kể cả `/portal/inspection`), nút “Chọn” ở bước 1 màn đăng ký thi.
