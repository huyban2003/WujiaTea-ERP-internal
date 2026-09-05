# D4f — SurfaceCard lượt cuối: Bootstrap `.card` thô

> Dán nguyên khối này sau khi chạy `/wujia-start`.

## 0. Bối cảnh

`UI-SURFACECARD-001` (STT 127 · `CMP-SC-001` · tab `UI Component` gid 488333015) là issue BA
`Ready for Dev` chuẩn hoá **khung card** toàn Portal: một chủ sở hữu duy nhất của
`background` / `border` / `border-radius` / `padding` / `box-shadow` / `gap`.

Component `wujia_portal_layout.wj_surface_card` dựng ở D4b, đã chạy thật trên **113/384 lượt
≈ 29%** qua D4b → D4e2. Nợ D4d đã trả hết ở D4e2.

D4f là **lượt cuối và rủi ro nhất**: nhóm dùng thẳng lớp Bootstrap `.card`. Khác mọi lượt trước
ở một điểm quyết định — **`.card` không phải lớp của Wujia**. Nó là lớp dùng chung của Bootstrap,
đang bị **bốn tầng CSS tranh nhau**, trong đó có **chính bundle của Odoo**.

Hồ sơ phải đọc trước khi gõ dòng code đầu tiên:

| File | Đọc phần nào |
|---|---|
| `docs/d4e2-acceptance-matrix.md` | **toàn bộ** — khuôn nghiệm thu D4f theo đúng file này |
| `docs/d4e1-acceptance-matrix.md` | §3 (min-height là SÀN thiết kế) · 7 LIMIT |
| `docs/d4-surfacecard-inventory.md` | **§14** (đính chính sau D4e2) · §13 · §12 |
| `docs/next-session-clusters-D.md` | **Luật chung #1…#9** · **🔴 Bài học D4e2 (8 mục)** · D4e1 (7) · D4d (10) |
| `docs/qa-issue-ledger.yaml` | 5 khối tiến độ D4b→D4e2 — **giữ nguyên `Ready for Dev`** |
| `custom/wujia_portal_layout/views/wj_surface_card.xml` | hợp đồng props |

---

## 1. Phạm vi — con số trong bảng cụm **SAI**, đã đếm lại 06/09

Bảng `next-session-clusters-D.md` ghi **“75 lượt / 13 file”**. Đếm bằng **token lớp** (tách
`class=` rồi so khớp cả từ, không `grep` chuỗi):

| Lớp | Số |
|---|---:|
| `card` | **35** |
| `card-body` | 31 |
| `card-header` | 16 |
| `card-footer` | 4 |

Con số **75** là cộng gộp mấy lớp con lại. **Shell thật cần migrate là `.card` = 35**, trong đó:

| Loại | Số | Xử lý |
|---|---:|---|
| Module bên thứ ba / backend (`mcp_server` — **uninstalled**, `wj_ks_dashboard_ninja`, `wj_ks_dn_advance`) | 3 | 🔴 **KHÔNG ĐỤNG** — bundle backend, ngoài Portal |
| `forgot_pass.xml` template `forgot_pass_back` | 2 | ☠️ **TEMPLATE CHẾT** — `grep` toàn repo **không ai `t-call`**. Xác minh lại lúc chạy rồi mới kết luận |
| `login_page.xml:277` template `signup_form` | 1 | 🔒 Màn auth — **THIẾT KẾ S39**, xem §3.5 |
| `portal_templates.xml:106` (`/my/franchises/<id>`) | 1 | Bundle **`portal.portal_layout` của Odoo**, không phải portal Vuexy (đo ra `r=6`, không shadow) — ngoài phạm vi |
| **Trong phạm vi** | **28** | 6 module |

### 28 call site trong phạm vi — neo thật (dòng ngày 06/09, vẫn phải đếm lại)

| Module | File | Dòng | Template |
|---|---|---|---|
| `wujia_portal_base` | `portal_franchise_information.xml` | 296 | `..._locked` (controller `portal.py:550` mới render) |
| `wujia_portal_base` | `portal_franchise_profile.xml` | 29 · 67 · 99 · 132 | `portal_franchise_profile_full` |
| `wujia_portal_base` | `portal_franchises_in_layout.xml` | 32 · 104 | `portal_franchises_list` · `portal_franchise_detail` |
| `wujia_portal_info_request` | `portal_info_request_{list,form,detail}.xml` | 32 · 28 · 32 | 3 template |
| `wujia_portal_knowledge` | `portal_knowledge.xml` | 34 · 54 · 288 · 306 | `..._list` ×2 · `..._detail` ×2 |
| `wujia_portal_return` | `portal_return_detail.xml` | 23 · 63 · 106 · 129 · 200 | `portal_return_detail` |
| `wujia_portal_return` | `portal_return_{form,list}.xml` | 21 · 36 | 2 template |
| `wujia_portal_sale` | `portal_order_product_detail.xml` | 23 · 90 | `portal_order_product_detail` |
| `wujia_portal_support` | `portal_support.xml` | 22 · 408 · 418 · 434 · 470 | `..._list` · `..._detail` ×4 |

⚠️ **Call site ≠ số thẻ hiện ra.** 4 route là danh sách — render **1 thẻ / 1 bản ghi**, nên số
thẻ phụ thuộc dữ liệu. Đếm thẻ phải đếm **lúc chạy**, đừng suy từ số call site.

---

## 2. 🔴 Neo CSS — `.card` đang có **bốn chủ**, một trong số đó là Odoo

Hỏi thẳng trình duyệt (CSSOM, `el.matches(rule.selectorText)`) trên `/portal/support/40` @1440:

| Thứ tự nạp | File | Khai gì |
|---|---|---|
| 1 | `bootstrap.css:4527` | `bg #fff` · `border 1px rgba(34,41,47,.125)` · `radius .5rem` |
| 2 | `bootstrap-extended.css:2405` (Vuexy) | `border: none` · `radius .5rem` · **`box-shadow 0 4px 25px rgba(0,0,0,.1)`** · **`margin-bottom: 2.2rem`** |
| 3 | `_wujia_theme.css:324` | `radius var(--wujia-card-radius) **!important**` · `border 1px var(--wujia-border)` · `bg` · **`overflow: hidden`** · `box-shadow 0 1px 2px rgba(0,0,0,.02)` |
| 4 | `_components.css:12` | `box-shadow: var(--wujia-card-shadow)` |
| 5 | 🔴 **`web.assets_frontend.min.css`** — bundle **của Odoo**, nạp **SAU** mọi `<link>` của Wujia | `background-color: var(--card-bg)` · `border-radius: var(--card-border-radius)` |

**Giá trị thắng cuộc thật sự** (đo, không suy):

```
background   rgb(255,255,255)          border-radius  16px   ← chỉ vì _wujia_theme có !important
border-top   1px rgba(0,0,0,0.176)     ← 🔴 CỦA ODOO, không phải --wujia-border (#E5E7EB)
box-shadow   rgba(15,23,42,.04) 0 2px 6px   ← _components.css:12 (BA nói KHÔNG shadow)
padding      0            overflow  hidden        margin-bottom  7px (.mb-2 = .5rem, gốc 14px)
```

Ba điều rút ra, và đây là **lý do thật sự phải làm D4f**:

1. **Viền của thẻ hiện do Odoo quyết**, không phải Wujia. Rule Wujia `border: 1px solid
   var(--wujia-border)` **thua** vì bundle frontend của Odoo nạp sau. Nâng cấp Odoo là đổi dáng
   thẻ. Đây không phải chuyện dọn dẹp — là **mất quyền kiểm soát**.
2. **Radius 16 chỉ đứng được nhờ `!important`.** Gỡ `!important` là rơi về Bootstrap.
3. **Mọi `.card` đang CÓ shadow**, chỏi câu BA *“border nhẹ, không shadow mặc định”* và chỏi
   chính D4b (lượt đó gỡ shadow khỏi `wujia-kpi-card`). Migrate = **mất shadow ở ~18 thẻ đang
   hiện** — thay đổi nhìn thấy được, phải chốt trước (§3.1).

`card-body` cũng có **ba** giá trị đệm đo được: `0/0/0/0` · `7/7/7/7` · `14/14/14/14`.
`.card > .card-header` thì `padding: 14px 20px 14px 6px !important` — **6px bên trái**, bất đối xứng.

---

## 3. 🔴 Năm câu phải HỎI CHỦ DỰ ÁN trước khi sửa — đừng tự quyết

### 3.1 Mất shadow ở ~18 thẻ đang hiện — có duyệt không?

`_components.css:12` cấp shadow cho **mọi** `.card`. `wj-surface-card` thì `box-shadow: none`
theo BA. Migrate là 18 thẻ PC phẳng đi. Đo trước rồi trình số, kèm ảnh @1440.

### 3.2 Sau khi migrate, có **gỡ ba rule `.card` toàn cục** không?

Nếu còn để `_wujia_theme.css:324` + `_components.css:12`, thì mọi `.card` **còn sót** (kể cả
của Odoo tự sinh trong portal) vẫn mang dáng Wujia ⇒ **vẫn hai chủ sở hữu**, đúng thứ issue cấm.
Nếu gỡ, mọi `.card` chưa migrate rơi thẳng về Bootstrap trần — **nhìn thấy ngay**.
**Đề xuất:** chỉ gỡ khi đếm lúc chạy ra **0 `.card` còn hiện** trên toàn bộ route đo được, và
phải có ảnh trước/sau. Không đạt thì **giữ rule, ghi LIMIT**, để lượt sau.

### 3.3 `card-body`: giữ hay gỡ, và đệm về số nào?

Ba giá trị đang chạy (`0` / `7` / `14`). Hai đường:

- **Đường A** — `sc_body='padded'` + **gỡ** `card-body`: một chủ sở hữu đệm, nhưng phải sửa
  markup con và **dễ vỡ layout** ở thẻ có `card-header` + `card-footer`.
- **Đường B** — `sc_body='flush'` + **giữ** `card-body`, chỉ hội tụ đệm của nó về token: ít rủi
  ro hơn, nhưng đệm vẫn do lớp Bootstrap giữ ⇒ **chưa trọn** tinh thần “một chủ sở hữu”.

🔴 Chọn nhầm là **đệm đúp** (20 của card + 14 của card-body = 34). Phải đo, đừng suy.

### 3.4 `overflow: hidden` và `margin-bottom` — hai thứ đi kèm không ai để ý

`_wujia_theme.css` cho `.card` **`overflow: hidden`**; `wj-surface-card` **không có**. Nếu trong
thẻ có dropdown/tooltip/popover đang bị cắt (hoặc đang **dựa vào** việc bị cắt để bo góc ảnh),
migrate sẽ đổi hành vi. Tương tự `margin-bottom`: Vuexy cho `2.2rem`, call site nào có `mb-2`
thì thành `7px`, **không có `mb-*` thì nhảy 2.2rem → 0**. Đếm call site không có `mb-*` trước.

### 3.5 Ba call site màn auth + 2 template chết — xử ra sao?

`forgot_pass_back` (2 lượt) **không ai gọi** ⇒ đề xuất **xoá hẳn file**, nhưng phải chứng minh
chết **lúc chạy** trước (bẫy D4d #4). `signup_form` (1 lượt) là màn auth — cụm `wj-auth-card`
đang **🔒 THIẾT KẾ S39, giữ dáng** ⇒ đề xuất **để nguyên, ghi LIMIT**.

---

## 4. 🔴 Chặn kỹ thuật — đọc hết trước khi đo

### 4.1 `wujia_tea_19` **CHƯA có D4e1 + D4e2**

DB dev cài `wujia_portal_layout` ở **`19.0.35.0.0`** trong khi manifest đã là `19.0.37.0.0`;
trình duyệt còn nhận `_wujia_theme.css?v=1180` và `_components.css?v=1190` (assets.xml đã ghi
1200/1210). **D4e1 và D4e2 đều chưa commit** trên nhánh `dev/2026-09-05-d4c`.

⇒ **Việc đầu tiên của phiên D4f**, trước khi đo một con số nào:
`git diff --stat` + so `ir_module_module.latest_version` với manifest, rồi `-u` cho DB đo để nạp
đúng trạng thái D4e2. Bỏ qua bước này thì cột “trước” lẫn cả ba lượt — **D4e2 đã dính đúng bẫy
này và phải đo lại toàn bộ** (bề mặt 210 → 230).

### 4.2 Route redirect ngầm / cần id đúng

| Route | Vướng | Cách gỡ |
|---|---|---|
| `/portal/return/1` | **redirect ngầm** — phiếu thuộc franchise khác | tìm id đúng bằng SQL (`franchise_id` của `anh.owner` = **5**, franchise `wujia_franchise_management` id 1) |
| `/portal/login` | đã đăng nhập ⇒ redirect | đo bằng context **chưa đăng nhập** |
| `/my/franchises/1` | bundle Odoo, ngoài Portal | không đo |
| `/portal/info-request` | bảng thật là **`wujia_info_update_request`** và **đang rỗng** | seed 1 bản ghi trên **bản copy**, hoặc ghi LIMIT |
| `/portal/reports/orders` | **500 có sẵn** — tz `Asia/Saigon` (cụm **R3**) | `UPDATE res_partner SET tz='Asia/Ho_Chi_Minh'` **chỉ trên copy**. 🔴 KHÔNG sửa `wujia_portal_base/controllers/utils.py:38` |

`wujia_portal_inspection` vẫn **`uninstalled`** ⇒ `/portal/inspection` trả **404**, trang 404 của
Odoo **tràn ngang 11px @360**. Đó là **cờ RULE 1 có sẵn**, không phải hồi quy — baseline D4e2 có
đúng 5 cờ (4× `debt-pay` redirect + 1× cái này). Và **2 test đỏ có sẵn** cũng do module này.

### 4.3 Phần lớn `.card` **chỉ hiện ở PC**

Đo runtime 06/09 (`scratchpad/d4f_recon.json`): ở **390** thì `knowledge`, `knowledge/<slug>`,
`return`, `support`, `support/40` đều **`hiện = 0`** — mobile đã có markup riêng (họ
`wujia-mdash-*` migrate ở D4d). Nhưng `franchises`, `franchises/1/profile`, `info-request`,
`order/product/1` **hiện ở cả hai khổ**. ⇒ **đừng cho là lượt này chỉ-PC**; phải đo cả 5 khổ.

---

## 5. Việc phải làm

1. **Hạ tầng đo trước khi sửa dòng CSS đầu tiên.** Clone `wujia_tea_19` → `wujia_tea_d4f`
   (`pg_dump | pg_restore`, đừng `TEMPLATE` — phải giết server đo). Copy `config/odoo.conf`
   thành `scratchpad/odoo.d4f.conf`, **sửa cả `db_name` lẫn `dbfilter`** (gốc `^wujia_tea_19$`,
   không sửa là *Database not found*). Cổng **8075** đang rảnh.
   `8070`/`8071` cụm R · `8072` server đo · `8019` UAT — **đừng đụng**.
2. **Nạp D4e1+D4e2 lên DB đo** (§4.1) rồi mới chụp baseline.
3. **Đo baseline** 5 khổ **1440/1024/992/390/360** × mọi route ở §1, ghi `pageH`,
   **số record trong viewport**, và với mỗi `.card`: `h` · `radius` · `border` · `pad` ·
   `box-shadow` · `margin-bottom` · `overflow`. Harness: copy `scratchpad/d4e2_measure.py`.
   Đã có sẵn `scratchpad/d4f_recon.py` (đếm runtime) và `d4f_who.py` (truy chủ rule CSS) —
   dùng lại.
4. **Hỏi 5 câu §3, chờ trả lời.** Đừng code trước.
5. **Migrate 28 call site** theo phương án đã chốt. Luật #1: **giữ lớp cũ** ở call site qua
   `sc_class` nếu lớp đó còn nuôi CSS con (`knowledge-detail`, `support-chatter`,
   `wujia-return-form` — kiểm từng cái). Luật #7: rút dáng khung khỏi rule cũ.
   Call site nào **không phải `<div>`** thì giữ thẻ và gắn thẳng lớp (cách §12.4 / D4e2 phần A).
6. **Bump + `-u` đúng MỘT lần**, một lệnh, đủ 6 module + `wujia_portal_layout`.
   `?v=` hiện là **1210** → `1220`. `wujia_portal_layout` **19.0.37.0.0 → 19.0.38.0.0**.
7. **Test**: thêm lớp `TestSurfaceCardD4f` vào
   `custom/wujia_portal_layout/tests/test_d4_surface_card.py` (**60 `def test_` sẵn, 5 lớp**,
   tag `wujia_surface_card_d4`) — **không đẻ file test song song**. Dùng lại helper
   `_rule()` · `_rules_anywhere()` (bắt cả rule trong `@media`) · `_declares()` · `_mod_css()`.
8. **Đột biến**: copy `scratchpad/d4e2_mutate.sh`. Bốn bẫy đã trả giá, **không dính lại**:
   bộ dò phải là `FAIL: (Subtest )?[A-Za-z0-9]+\.[a-z_0-9]+`; xác nhận đột biến vào file bằng
   **`grep -qF --`** (thiếu `--` là chuỗi bắt đầu bằng `--` bị nuốt như tuỳ chọn);
   đột biến XML phải **giữ file hợp lệ** (`ExpatError` ⇒ `-u` abort ⇒ xanh oan); `-u` của vòng
   đột biến phải liệt kê **đủ mọi module có test `post_install`**.

---

## 6. Nghiệm thu — không đủ thì không ghi ledger

1. **Bảng trước–sau 5 khổ** × mọi route, gồm `pageH` **và số record trong viewport**
   (acceptance BA #11: không được giảm).
2. **Số thẻ `.card` còn lại đếm LÚC CHẠY** trên mọi route — đây là con số quyết định §3.2.
3. **Nhịp header→body đo TUYỆT ĐỐI** (`scratchpad/d4e2_rhythm.py`). Mốc sau D4e2 là
   **`0×2 · 12×50`** trên 52 ô. Lượt này **không được làm vỡ** con số đó — thẻ mới vào phải
   hoặc ra đúng `12`, hoặc giải trình từng ô.
4. **RULE 1 + RULE 2**: `python3 scratchpad/d3_review.py --base http://127.0.0.1:8075
   --portal-login anh.owner --out <x>.json` → `d3_analyze.py`. `--portal-login` **bắt buộc**
   (mặc định rơi về `admin` ⇒ Pass rỗng). Mốc baseline: **5 cờ** (4× `debt-pay` + 1× inspection
   404) · RULE 2 `[pc] 18px ×92 · [m] 16px ×62 · [pc] 20px ×2`. **Cờ mới nào cũng phải giải trình.**
5. **Ảnh trước–sau @1440 và @390 + soi mắt** (bắt buộc — lượt đổi shadow và đệm), cộng **diff
   pixel** `PIL.ImageChops.difference(...).getbbox() is None` trên trang **ngoài** phạm vi.
   ⚠️ Trang `/portal` có **đồng hồ đếm ngược** — đọc chữ số trong ảnh rồi mới kết luận.
   ⚠️ Khác vài pixel ở mức chênh **1/255** có thể là **khử răng cưa góc bo**, không phải hồi quy:
   chụp control 2 lần cùng trạng thái, rồi bisect từng file CSS. Xem LIMIT 7 của D4e2.
6. **Đột biến 100% đỏ đúng chỗ** + run đối chứng xanh. Mốc: **60 test**, **2 lỗi đỏ có sẵn**
   (`TestSurfaceCardD4e1.test_all_metric_call_sites_use_the_component` và
   `test_call_sites_bake_summary_and_flush`, do `wujia_portal_inspection` uninstalled).
7. **Quét đặc hiệu CSS toàn bộ `custom/**/*.css`** — **loại tên con BEM** khỏi phép khớp
   (`__head { gap }` là nội dung, không phải khung: D4e2 đã tự báo dương tính giả), phân biệt
   rule trạng thái nghỉ với `:hover`/`:active`.
8. 0 lỗi JS · 0 tràn ngang · 0 redirect ngầm · HTTP 200 toàn bộ · 0 bề mặt trắng lồng bề mặt trắng.
9. Đối chiếu cột `Kết quả mong muốn` của `UI-SURFACECARD-001` — **≥90%** cho phần thuộc D4f.

🔴 **Đọc log đúng chỗ.** `logfile` trong `config/odoo.conf` nuốt sạch stdout — “RC=0, 0 ERROR”
đọc từ file rỗng là **XANH GIẢ** (đã dính 3 lần ở D4d). Bằng chứng nằm ở
`logs/<năm>/<tháng>/<ngày>.log`; luôn `N=$(wc -l < $L)` **trước** mỗi lần chạy rồi `tail -n +$((N+1))`.
🔴 **`nohup … &` báo exit 0 ngay trong khi script còn chạy.** Chờ bằng
`until ! pgrep -f "<script>"; do sleep 30; done`.
⚠️ Đừng `pkill -f "odoo.d4f.conf"` — chuỗi đó nằm trong chính dòng lệnh của shell đang chạy nên
**tự giết phiên**. Lấy PID bằng `ps aux | grep "[o]doo.d4f.conf" | awk '{print $2}'`.

Đo xong: **drop `wujia_tea_d4f` + xoá `data/filestore/wujia_tea_d4f`**.

---

## 7. Hồ sơ phải viết

- `docs/d4f-acceptance-matrix.md` — theo đúng khuôn `docs/d4e2-acceptance-matrix.md`.
- `docs/d4-surfacecard-inventory.md` **§15** — đính chính con số (**75 → 35 → 28 trong phạm vi**)
  + các chốt của lượt + tiến độ.
- Mục D4 của `docs/next-session-clusters-D.md` — bài học D4f, tiến độ mới, bảng thứ tự lượt.
- `docs/qa-issue-ledger.yaml` — khối tiến độ dạng chú thích như D4b→D4e2.
  **Nếu D4f khép trọn cụm** (0 `.card` còn hiện + các nhóm còn lại đã có chủ) thì mới bàn tới
  `Ready for Retest`; còn không thì **giữ `Ready for Dev`**. `qa_sync.py` chạy **dry-run**;
  `--apply` chỉ khi chủ dự án chốt. ⚠️ `scripts/ba_spec` là **symlink** ra `~/wujia-devkit/ba_spec`
  ⇒ `qa_sync.py` tính ledger thành `/home/huyban/docs/qa-issue-ledger.yaml` và chết
  `FileNotFoundError`; nạp script với `LEDGER` trỏ đúng repo, **đừng sửa file toolchain**.
- **LIMIT phải ghi**: 3 call site module bên thứ ba · `/my/franchises` khác bundle · màn auth
  S39 · `wujia_portal_inspection` uninstalled (2 test đỏ + 1 cờ RULE) · bug tz = R3 ·
  chưa soi UAT (**phải đo lại chỉ-đọc sau deploy rồi mới `qa_deploy_mark.py`** — L14/L10: UAT có
  `website`/`website_sale` nên bundle frontend khác local, từng lật ngược kết quả ở C6 và D2).
- Hết cụm D4 thì chạy `/wujia-end-sprint`.

---

## 8. Ngoài phạm vi — thấy cũng để yên

`wj-auth-card` (15) 🔒 THIẾT KẾ S39 · 9 họ còn lại nhóm Khảo sát (BA ghi *provisional*) ·
26 lượt bề mặt trắng mobile (§12.2: 20 → `CMP-ES-001`, 4 → `UI-DATALIST-001`, 2 chưa có chủ) ·
hội tụ token `--wujia-border` ↔ `--wujia-morder-border` (**phải hỏi trước**) · migrate CardHeader
= cụm **D3**, issue riêng đang `Need Clarification` · `.wj-empty-state` RULE 1 vỡ ở
`/portal/delivery` → `CMP-ES-001` · 4 màn tiêu đề card lệch 18px → D7+ · bug tz = **R3** ·
2 ô nhịp `0px` ở `/portal/notification/41` (lỗi outline `h3`/`h2`) = **R2**.

---

## 9. Môi trường

- v19 active `/home/huyban/odoo-dev/WujiaTea` · v14 tham chiếu
  `/home/huyban/odoo-dev/wujia_tea_odoo14` (**không sửa**).
- Portal đo bằng **`anh.owner` / `wujia@test123`** — quá 5 lần sai dính *Too many login failures*.
  `/portal/_pc-preview` cần phiên **`admin`** (`auth='user'`, chặn user không phải nội bộ).
- **UAT `http://113.161.187.126:8019/`** — `admin` / `Wujia@2026`. Tự smoke-test được (đọc/nhìn),
  theo giới hạn **QA §10: không tạo đơn/hoá đơn/email thật**.
- Harness ở `scratchpad/` và toolchain `scripts/ba_spec/` là **dev-only, gitignored, KHÔNG commit,
  KHÔNG lên server**. ⚠️ `.gitignore:41` ghi `scripts/ba_spec/` **có `/` cuối** nên **không khớp
  symlink** — nó vẫn hiện `??` trong `git status`; đừng `git add -A`.
- **Dev không tự đóng `Done`** — chỉ tới `Ready for Retest`, kèm Build/Deploy + FIX/IMPACT/
  RETEST/LIMIT + Odoo Fit + dòng History (`docs/01_NGO_GIA_QA_OPERATING_STANDARD.md`).
