# D4f — bảng nghiệm thu SurfaceCard lượt cuối (gỡ `.card` của Bootstrap)

Issue `UI-SURFACECARD-001` · STT 127 · `CMP-SC-001` · tab `UI Component` gid 488333015.
Đo trên bản sao `wujia_tea_d4f`, cổng **8075**, đăng nhập portal `anh.owner`.
Harness ở `scratchpad/` — **dev-only, gitignored, KHÔNG commit**.

---

## 0. Vì sao lượt này khác mọi lượt trước

`.card` **không phải lớp của Wujia**, và Wujia đang **mất quyền kiểm soát nó**. Truy chủ rule
bằng CSSOM (`scratchpad/d4f_who75.py`, `/portal/support/40` @1440) cho ra chuỗi rule khớp theo
đúng thứ tự nạp:

| # | File | Khai gì cho `.card` |
|---|---|---|
| 1 | `bootstrap.css` | nền #fff · viền 1px rgba(34,41,47,.125) · radius .5rem |
| 2 | `bootstrap-extended.css` | border-width medium · radius .5rem · shadow `0 4px 25px` · `margin-bottom: 2.2rem` |
| 3 | `_wujia_theme.css?v=1200` | nền `--wujia-bg-card` · viền `--wujia-border` · radius **!important** · `overflow:hidden` · shadow |
| 4 | `_components.css?v=1210` | `box-shadow: var(--wujia-card-shadow)` |
| 5 | **`web.assets_frontend.min.css`** | `background-color` · `border` · `border-radius` — **nạp SAU cùng** |

Kết quả tính ra thật:

```
border: 1px solid rgba(0, 0, 0, 0.176)   ← của ODOO, không phải --wujia-border #E5E7EB
border-radius: 16px                       ← Wujia chỉ đứng được nhờ !important
box-shadow: rgba(15,23,42,.04) 0 2px 6px  ← cái bóng BA cấm
```

`card-footer` đo ra nền `rgba(33,37,41,.03)` (xám Bootstrap) dù Wujia khai `transparent` —
điểm thứ hai Odoo thắng.

⇒ **Luật chung #1 ("giữ lớp cũ qua `sc_class`") KHÔNG áp dụng được cho lượt này.** Giữ chữ
`card` là để Odoo tiếp tục thắng. Phải bỏ hẳn, kéo theo `card-header/body/footer` vốn sống
nhờ selector `.card > …`.

## 0b. Đính chính con số của prompt

Đếm bằng **token lớp** (tách `class=` rồi so cả từ), không `grep` chuỗi con:

| Lớp | Prompt ghi | Đếm thật | Trong phạm vi |
|---|---:|---:|---:|
| `card` | 35 | **44** | **31** |
| `card-body` | – | 47 | 28 |
| `card-header` | – | 18 | 16 |
| `card-footer` | – | 4 | 4 |
| file bên thứ ba | 3 | **12** | – |

31 = 28 của prompt **+ 3 màn auth** theo chốt #4 của chủ dự án.

## 0c. Bốn chốt của chủ dự án (06/09)

| # | Câu hỏi | Chốt | Đã làm |
|---|---|---|---|
| 1 | Con của card: giữ `card-body` hay migrate? | **Đường A** — "làm cho đồng bộ thì migrate đi rồi fix dần" | migrate hết sang `__head/__body/__foot` |
| 2 | 3 rule `.card` toàn cục | chỉ gỡ nếu không còn thẻ `.card` nào | đếm lúc chạy = **0** ⇒ **đã gỡ** |
| 3 | ~18 thẻ PC mất shadow | "cứ làm theo BA" | đã bỏ, có ảnh trước/sau ở §7 |
| 4 | `forgot_pass.xml` template chết | "làm thì làm hết đi" | đã migrate cả 3 call site auth |

---

## 1. Chặn kỹ thuật — gỡ trên bản copy, KHÔNG sửa bug

| Route | Vướng | Cách gỡ |
|---|---|---|
| `/portal/return/<id>` | redirect ngầm (phiếu khác franchise) | dùng phiếu **2** của franchise 1 |
| `/portal/support/<id>` | như trên | ticket **40** |
| `/portal/info-request` | bảng rỗng | seed 2 bản ghi `INF-000001/2` **trên copy** bằng ORM |
| `/portal/reports/orders` | 500 có sẵn — tz `Asia/Saigon` | `UPDATE res_partner SET tz='Asia/Ho_Chi_Minh'` (4 dòng) **chỉ trên copy**; bug thuộc cụm **R3**, KHÔNG sửa `utils.py:38` |
| `/portal/login`, `/portal/forgot-pass` | đã đăng nhập ⇒ redirect | đo bằng context **chưa đăng nhập** |
| `portal_franchise_information_locked` | chỉ render khi khoá | `d4f_locked.py` bật `portal_locked` rồi trả lại trong `finally` |

`wujia_portal_inspection` vẫn `uninstalled` ⇒ `/portal/inspection` trả 404, trang 404 của Odoo
tràn ngang 11px @360 — **cờ RULE 1 có sẵn**, không phải hồi quy.

---

## 2. Đã làm

**CSS — dựng con BEM, gỡ chủ sở hữu cũ**

| File | Thay đổi |
|---|---|
| `_components.css` | **+** `.wj-surface-card__head/__body/__body--flush/__foot/__media`; **−** rule toàn cục `.card { box-shadow }`; danh sách selector cỡ chữ tiêu đề trỏ sang `__head` (giá trị **không đổi** — địa hạt D3) |
| `_wujia_theme.css` | **−43 dòng**: trọn khối `.card`, `.card > .card-header`, `.card > .card-header .card-title/h2–h6`, `.card-footer`, `.card-body .wujia-section-header`. Giữ 2 rule `.card-title` ở dòng 26/37 (không cần tổ tiên `.card`) |
| `portal_return.css` | `.card-body > .wj-card-header…` → `.wj-surface-card__body > …` (2 rule, cùng đặc hiệu (0,3,0) nên vẫn thắng) |
| `portal_support.css` | `.support-chatter .card-body` → `.support-chatter .wj-surface-card__body` |

`overflow: hidden` **không** đưa vào shell — 113 thẻ D4b–D4e chạy không có nó, thêm là đổi hành
vi cả cụm. Ảnh bìa (`card-img-top`) trước đây bo góc **nhờ** `overflow` của cha; nay bo góc thẳng
vào ảnh qua `.wj-surface-card__media`.

**XML — 31 call site, 82 phép thay**

| Module | File | Số call site |
|---|---|---:|
| `wujia_portal_base` | `portal_franchise_profile.xml` | 4 |
| | `portal_franchise_information.xml` | 1 |
| | `portal_franchises_in_layout.xml` | 2 |
| `wujia_portal_info_request` | `_list` · `_form` · `_detail` | 3 |
| `wujia_portal_knowledge` | `portal_knowledge.xml` | 4 |
| `wujia_portal_return` | `_detail` (5) · `_form` · `_list` | 7 |
| `wujia_portal_sale` | `portal_order_product_detail.xml` | 2 |
| `wujia_portal_support` | `portal_support.xml` | 5 |
| `wujia_portal_layout` | `forgot_pass.xml` (2) · `login_page.xml` (1) | 3 |
| | **tổng** | **31** |

- Shell nướng đủ 4 lớp `wj-surface-card wj-surface-card--section wj-surface-card--compact
  wj-surface-card--flush` (tiền lệ D4e2 phần A).
- Call site **không phải `<div>`** giữ nguyên thẻ, gắn lớp thẳng: `portal_return_form.xml:21`
  (`<form>`), `portal_info_request_form.xml:28` (`<form>`), `portal_knowledge.xml:288`
  (`<article>`) — QWeb O19 không có directive đổi tên thẻ (`ir_qweb.py:1705`).
- Utility `p-2` / `py-2` **giữ lại**: baseline chứng minh đó là nhịp cố ý (thanh lọc + thẻ
  sản phẩm nhỏ), gỡ đi là đệm nhảy 7 → 16.
- Lớp riêng của module **giữ nguyên** (`knowledge-detail`, `support-chatter`,
  `wujia-return-form`) — Luật #1 phần còn áp dụng được.

**Bump + `-u` đúng một lần**: `assets.xml` `?v=1200|1210 → 1220`; manifest `19.0.37.0.0 →
19.0.38.0.0`; một lệnh cho 7 module. Log UTC `2026-09-05.log`: **0 ERROR · 0 CRITICAL**,
99 dòng loading, `latest_version` DB = `19.0.38.0.0`, `ir_ui_view` còn **0** view mang token
`card` (trừ ngoại lệ ở §12).

---

## 3. Số đo TRƯỚC → SAU (`scratchpad/d4f_{before,after}.json`)

125 lượt tải (25 route × 5 khổ 1440/1024/992/390/360) mỗi lượt · **250 bề mặt hiện** cả hai lần.

**Thẻ `.card` hiện lúc chạy: `89 → 0`** (thêm 5 thẻ của biến thể `_locked` → 0). Đây là con số
quyết định chốt #2.

| | TRƯỚC (89 thẻ `.card`) | SAU (`.wj-surface-card`) |
|---|---|---|
| radius | 16 (mọi khổ, đứng nhờ `!important`) | 16 PC · **14 mobile** (token) |
| viền | `1px rgba(0,0,0,.176)` — **của Odoo** | `1px #EEF2F5` PC · `1px #E5E7EB` mobile — **của Wujia** |
| bóng | `rgba(15,23,42,.04) 0 2px 6px` | **none** (BA) |
| overflow | `hidden` | `visible` |
| padding | `0/0/0/0` (Bootstrap) | `0` khi `--flush`, `16` PC / `12` mobile khi có đệm |

**Ba vùng con:**

| Vùng | TRƯỚC | SAU |
|---|---|---|
| header | ×49 `pad 14/20/14/6` · nền trong suốt · `border-bottom 1px` | ×33 `16/16/12/16` · ×10 `12/12/12/12` · ×6 `7/16/7/16` (`py-2`) — đều `border-bottom 1px` |
| body | ×56 `14` · ×14 `7` · ×13 `0` — nền `rgba(255,255,255,.9)` | ×42 `16` · ×14 `7` (`p-2` giữ) · ×14 `12` (mobile) · ×13 `0` (`--flush`) — nền **trong suốt** |
| footer | ×16 `7/14/7/14` · nền **`rgba(33,37,41,.03)`** (xám Bootstrap lọt qua) | ×12 `12/16/12/16` · ×4 `12/12/12/12` — nền **trong suốt**, `border-top 1px` |

**Sức khoẻ trang — 125 ô, 0 cờ:** không ô nào đổi HTTP status, không ô nào sinh tràn ngang mới,
không ô nào redirect ngầm mới, **không ô nào giảm số bản ghi trong viewport** (BA #11).

**Chiều cao trang:** 114 ô **không đổi** · 11 ô **thấp bớt** · **0 ô cao lên**. Sâu nhất
`-155px` ở `/portal/franchises/1/profile` @360 (4 thẻ × mất `margin-bottom` thừa + đệm mobile
14 → 12). Đúng hướng BA muốn: đặc hơn, không thưa ra.

---

## 4. Rủi ro `margin-bottom: 2.2rem` — đã tháo ngòi bằng số đo, không bằng suy đoán

Vuexy cho `.card` `margin-bottom: 2.2rem` (31px). Bỏ `.card` là mất nó. `scratchpad/d4f_stack.py`
xếp mọi bề mặt hiện theo `top`, ghép cặp chồng nhau >50% chiều ngang:

| | TRƯỚC | SAU |
|---|---|---|
| cặp xếp chồng | 55 | 55 |
| cặp **có dính** `.card` | 35 — **tất cả hở đúng 7px** | 0 (không còn `.card`) |
| histogram khoảng hở | `0×6 · 7×35 · 14×12 · 30×2` | `0×6 · 7×35 · 14×12 · 30×2` — **y hệt** |

`d4f_gap.py` cho biết 27/33 thẻ có `mb=31` là **phần tử hiện cuối cùng** trong cha ⇒ 31px là
khoảng thừa đuôi, không phải nhịp giữa hai thẻ. Nhịp giữa các thẻ do `mb-2` ở call site giữ,
và `mb-2` đã được giữ nguyên.

---

## 5. Nhịp header→body đo TUYỆT ĐỐI (`scratchpad/d4f_rhythm_{before,after}.json`)

| | TRƯỚC | SAU |
|---|---|---|
| histogram | `0px ×2 · 12px ×50` | `0px ×2 · 12px ×50` |
| ô ≠ 12 | 2 (`wj-pc-noti-rule`, `/portal/notification/41` — thuộc **R2**) | 2, **cùng ô đó** |

Mốc D4e2 giữ nguyên trên 52 ô. RULE 1/2 mù trước sai số đều tay (bài học D4b) nên phép đo này
là bắt buộc.

---

## 6. RULE 1 + RULE 2 (`d3_review.py --portal-login anh.owner` → `d3_analyze.py`)

| | TRƯỚC | SAU |
|---|---|---|
| route/viewport có cờ | **5** | **5** |
| nhóm cỡ chữ DRIFT chưa giải trình | 0 | 0 |

5 cờ = 4× `debt-pay` redirect ngầm (`WJ-DEBT-007`) + 1× `inspection` 404 tràn ngang 11px @360.
Cả hai đều có sẵn từ baseline, không phải hồi quy.

RULE 2 sau lượt có thêm một dòng **đã được chính bộ phân tích tự giải trình**:
`[pc] THIẾT KẾ 12.3px ×2 return-detail — 4 nhãn phụ .875rem giữa thân card (D3e, RULE 1)`.
Đây là **đổi phạm vi phát hiện**, không phải đổi dáng: 4 nhãn phụ này trước đây nằm dưới
`.card-body` nên bộ quét không nhận là "tiêu đề mở đầu card"; nay chúng nằm dưới
`.wj-surface-card__body` nên được nhận. Cỡ chữ vẫn `.875rem` như trước — rule màu ở
`portal_return.css` đã trỏ lại đúng tên mới nên không đổi giá trị nào.

---

## 7. Ảnh trước–sau + diff pixel (69 ảnh, 23 route × 1440/390/360)

`PIL.ImageChops.difference(...).getbbox() is None`:

| Kết quả | Số ảnh |
|---|---:|
| **giống hệt từng pixel** | 37 |
| khác | 23 |
| đổi cỡ ảnh (trang thấp bớt) | 9 |

**Mọi ảnh khác/đổi cỡ đều nằm trong phạm vi**, trừ 4 ảnh — đã truy tận nơi:

| Ảnh | px khác | Δ tối đa | Kết luận |
|---|---:|---:|---|
| `portal@390` | 1077 | 224 | **đồng hồ đếm ngược** — cắt ảnh phóng to đọc được `còn 03:00` → `còn 02:37`, kèm thanh tiến trình. `portal@1440` **giống hệt**. |
| `portal@360` | 271 | 224 | như trên |
| `portal_exam@1440` | 9 | **1/255** | khử răng cưa góc bo |
| `portal_purchase-history@390` | 40 | **3/255** | khử răng cưa |

Soi mắt `/portal/support/40` @1440 (chỗ chốt #3 bỏ shadow): bóng biến mất, viền nhạt lại về token
Wujia, đệm nhích 14 → 16, bố cục nguyên vẹn, không vỡ chỗ nào.

**9 ảnh đổi cỡ** đều là **thấp bớt**, không ảnh nào cao lên:
`franchises/1` −33 · `franchises/1/profile` −155 · `info-request/1` −25 · `info-request/new` −10
(@360/@390) · `return/new` @1440 −2.

---

## 8. Guard chứng minh bằng ĐỘT BIẾN — `scratchpad/d4f_mut.py`

**13/13 đột biến bị bắt.** Mỗi vòng: sửa cho sai → `-u` 9 module → chạy `wujia_surface_card_d4`
→ trừ 2 lỗi đỏ có sẵn → khôi phục file trong `finally`.

| # | Đột biến | Guard đỏ |
|---|---|---|
| 1 | call site giữ lại token `.card` | `test_no_d4f_view_keeps_the_bootstrap_card_class` |
| 2 | con BEM tụt về `card-body` | `test_children_migrated_to_the_bem_names` |
| 3 | shell rơi mất modifier `--flush` | `test_call_sites_bake_all_four_shell_classes` |
| 4 | lớp riêng của module bị rút | `test_module_own_classes_survive_next_to_the_shell` |
| 5 | `__head` mất viền dưới | `test_bem_children_declare_their_own_frame` |
| 5b | `__head` hardcode px thay token | `test_bem_children_use_the_tokens_not_raw_px` |
| 6 | rule `.card` toàn cục sống lại | `test_global_card_shape_rules_are_gone` |
| 7 | shadow quay lại trên shell | `test_surface_card_still_has_no_shadow` + `…D4b.test_surface_card_has_no_default_shadow` |
| 8 | `portal_return.css` tụt về `.card-body >` | `test_module_css_retargeted_off_card_body` |
| 9 | `portal_support.css` tụt về `.card-body` | `test_module_css_retargeted_off_card_body` |
| 10 | ảnh bìa mất bo góc riêng | `test_media_class_carries_the_radius_itself` |
| 11 | shell thêm `overflow` | `test_media_class_carries_the_radius_itself` |
| 12 | `__foot` mất viền trên | `test_bem_children_declare_their_own_frame` |

**Đối chứng:** 74 test, đỏ đúng **2 lỗi có sẵn**
(`TestSurfaceCardD4e1.test_all_metric_call_sites_use_the_component` và
`test_call_sites_bake_summary_and_flush`, do `wujia_portal_inspection` chưa cài).
Trước lượt này là 60 test ⇒ **+14 test D4f**.

### Vòng đột biến bắt được 3 lỗi THẬT trong chính guard của tôi

Ba lần đầu chạy đều không sạch, và mỗi lần đều là lỗi thật chứ không phải nhiễu:

1. **Đột biến #3 không đỏ.** `test_call_sites_bake_all_four_shell_classes` dùng phép `in`:
   `portal_order_product_detail.xml` có 2 thẻ, rút `--flush` khỏi một thẻ thì thẻ kia vẫn còn
   chuỗi đó ⇒ xanh oan. Sửa thành **đếm**: `arch.count(4-lớp) == arch.count('wj-surface-card
   wj-surface-card--section')`.
2. **Đột biến #11 không đỏ.** `_rule()` chỉ trả **rule đầu tiên**; đột biến thêm một rule
   `.wj-surface-card { overflow: hidden }` **đứng sau** nên lọt. Sửa sang `_rules_anywhere()`
   rồi quét mọi thân rule.
3. **Đột biến #1 không đỏ.** Regex dò token viết `(?:^|\s)card`, mà `^` chỉ khớp đầu chuỗi
   ⇒ token đứng **đầu** thuộc tính (`class="card wj-…"`) không có ký tự trắng đứng trước và
   lọt sạch. Sửa sang **tách token** bằng `.split()`.

Bẫy thứ tư đã chặn được **trước khi** nó cho kết quả sai: một lần sửa test làm hỏng cú pháp
(`re.compile(r"""…'"""")` — dấu nháy cuối nuốt mất khối `"""`), `-u` abort, 0 test chạy, và
bộ đếm `post-tests` trong `d4f_mut.py` báo **"KHÔNG CÓ TEST NÀO CHẠY — kết quả vô nghĩa"** cho
cả 13 vòng thay vì báo 13 màu xanh giả.

---

## 9. Đặc hiệu CSS — quét toàn bộ `custom/**/*.css`

Loại con BEM (`__head/__body/__foot/__media/…` là **nội dung**, không phải khung — D4e2 từng
tự báo dương tính giả) và loại rule trạng thái `:hover/:active/:focus`:

```
5 rule khai dáng khung cho .wj-surface-card · ngoài file chủ: 0
  _components.css:608  .wj-surface-card           background,border,border-radius,padding
  _components.css:617  .wj-surface-card--regular  padding
  _components.css:620  .wj-surface-card--summary  gap
  _components.css:624  .wj-surface-card--flush    padding
  _components.css:627  .wj-surface-card--tonal    background,border,border-radius,box-shadow
```

**Một chủ sở hữu duy nhất.** Và `_rules_anywhere('.card')` trả **rỗng** ở cả `_wujia_theme.css`
lẫn `_components.css` — 3 rule toàn cục đã gỡ theo chốt #2.

---

## 10. Biến thể `portal_franchise_information_locked`

Chỉ render khi cửa hàng bị khoá nên phải bật cờ trên bản copy mới đo được. 5 khổ, đều HTTP 200,
0 tràn ngang, thẻ đúng dáng mới: radius 16/viền `#EEF2F5` ở PC, radius 14/viền `#E5E7EB` ở
mobile, `shadow none`.

---

## 11. Đối chiếu `Kết quả mong muốn` (phần thuộc D4f)

| Yêu cầu BA | Kết quả |
|---|---|
| Một chủ sở hữu duy nhất cho dáng khung | ✅ 5 rule, 0 ngoài file chủ |
| Bỏ shadow mặc định | ✅ 89 thẻ `shadow none`, guard + đột biến khoá |
| Có viền 1px | ✅ token Wujia, không còn viền của Odoo |
| Không khoá cứng chiều cao | ✅ không rule nào khai `min-height` cho shell |
| bodyMode padded/flush | ✅ `__body` / `__body--flush` |
| Compact-first | ✅ 4 lớp shell nướng `--compact` |
| Không giảm số bản ghi trong viewport (#11) | ✅ 125/125 ô, không ô nào giảm |
| Nhịp header→body 12px | ✅ `0×2 · 12×50`, y mốc D4e2 |

**Phần thuộc D4f: 8/8.**

---

## 12. LIMIT phải ghi vào ledger

1. **12 call site module bên thứ ba** (`wj_ks_dashboard_ninja` ×10, `wj_ks_dn_advance` ×1,
   `mcp_server` ×1 đang `uninstalled`) — bundle **backend**, không nạp CSS Portal. Không đụng.
2. **`/my/franchises/<id>`** (`wujia_portal_base.portal_my_franchise_detail`,
   `portal_templates.xml:106`) chạy trên bundle `portal.portal_layout` của Odoo. Đo lúc chạy:
   **không nạp một dòng CSS Wujia nào** (radius 6px, shadow none). Đổi lớp ở đó là sửa dáng một
   màn không thuộc shell Vuexy ⇒ **để nguyên**. Test `test_no_portal_view_at_all_keeps_the_card_class`
   ghim đúng ngoại lệ này thành một danh sách 1 phần tử, thêm chỗ rò mới là đỏ ngay.
3. **`wujia_portal_inspection` uninstalled** ⇒ 2 test đỏ có sẵn + 1 cờ RULE 1 (404 tràn ngang
   11px @360). Không phải hồi quy của D4f.
4. **Bug tz `Asia/Saigon`** làm `/portal/reports/orders` trả 500 — thuộc cụm **R3**, chỉ vá trên
   bản copy để đo được, **không sửa** `wujia_portal_base/controllers/utils.py:38`.
5. **3 call site auth là template CHẾT** — `/portal/login` và `/portal/forgot-pass` render **0
   thẻ `.card`** ở cả 5 khổ, chứng minh lúc chạy. Đã migrate theo chốt #4 nhưng **không có bằng
   chứng ảnh** vì chúng không hiện; nếu lượt sau bật lại các màn này thì phải đo riêng, đặc biệt
   `login_page.xml:277` thuộc cụm auth **khoá thiết kế S39**.
6. **`card-img-top` không đo được trên DB này** — không bài viết nào có ảnh bìa nên nhánh `t-if`
   không bao giờ render. Rủi ro mất bo góc do gỡ `overflow:hidden` đã được xử lý **tường minh**
   bằng `.wj-surface-card__media` + guard, nhưng **chưa có số đo lúc chạy**.
7. ~~Chưa soi UAT.~~ **Đã soi 06/09 (D4g, §13)** — khớp local ở cả 5 khổ, 0 rule ngoài
   `_components.css` kể cả bundle `website`/`website_sale` của UAT. LIMIT này đóng.

---

## 13. Soi UAT chỉ-đọc sau deploy (lượt D4g, 06/09/2026)

**Điều kiện vào** (XML-RPC `ir.module.module`, 03:07–03:08 UTC): 21 module Wujia có
`latest_version == installed_version == version manifest trên `main``, không module nào lệch;
`wujia_portal_layout` **19.0.38.0.0**, 9 module đụng D4e/D4f hậu tố `.2`. HTML `/portal/login` nạp
`_components.css?v=1220`, `_pc_components.css?v=1220`, `_wujia_theme.css?v=1220`, `_variables.css?v=1200`;
md5 `_components.css` tải từ UAT (bỏ CRLF) **bằng** repo: `5eaf3c24…`.

**Cách đo**: `scratchpad/d4g_uat_measure.py` = `exec` nguyên `d4f_measure.py` (không chép logic), đổi
đúng 3 chỗ: `BASE`/`DB` UAT, đăng nhập `admin` qua `/web/session/authenticate` + cookie
`wujia_active_franchise_id=3` (HCM-01 — form portal không dùng được trên UAT, bẫy L13/3), id thật của
UAT (`/portal/support/16`, `/portal/return/13`, `/portal/franchises/3/profile`, `/portal/knowledge/ui12-01`,
`/portal/order/product/4`). 14 route scope + 9 route đối chứng + 2 route ẩn danh × **5 khổ**
1440/1024/992/390/360. Chỉ GET + đọc DOM; không tạo dữ liệu. Kết quả `scratchpad/d4g_uat.json`
(+ `d4g_uat360.json` chạy lại vì 1 lượt `/portal/franchises@360` timeout mạng 45 s, lượt hai trả 200).

### 13.1 Ba con số prompt yêu cầu

| # | Câu hỏi | UAT | Local D4f | Khớp |
|---|---|---|---|---|
| 1 | Thẻ `.card` Bootstrap **hiện** trên 25 route × 5 khổ | **0** (DOM cũng 0) | 0 | ✅ |
| 2 | Shell `.wj-surface-card` — viền / radius / shadow | PC (1440/1024/992): `1px #EEF2F5` · 16px · none — **86/86 shell mỗi khổ**. Mobile (390/360): `1px #E5E7EB` · 14px · none — 86/86 và 85/85 | y hệt | ✅ |
| 3 | Rule CSSOM **ngoài** `_components.css` khớp shell (`d4g_uat_who.py`, 4 route × 2 khổ, duyệt cả `@media`/`@supports`) | **0** — kể cả `website`/`website_sale` không nạp rule nào chạm `.wj-surface-card` | 0 | ✅ |

Số đo phụ: 429 bề mặt duyệt (local 440 — chênh do dữ liệu UAT khác: HCM-01 không có yêu cầu cập
nhật thông tin nên `/portal/info-request` ra trạng thái rỗng), **0 lỗi JS**, **0 HTTP ≠ 200**, **0
redirect ngầm**, **0 bề mặt trắng lồng bề mặt trắng**. Route D4e1/D4e2 (`/portal/reports/orders`)
lần đầu lên UAT: 7 shell `--summary --flush` PC, 3 shell mobile, đúng token.

### 13.2 Điều thấy nhưng KHÔNG thuộc D4f

- `/portal/login` và `/portal/forgot-pass` **tràn ngang** ở 1024/992/390/360 — **giống hệt local D4f**
  (`d4f_after.json` cùng 8 ô), tức có sẵn trước cụm D4; màn auth khoá thiết kế S39 (LIMIT 5, chốt
  `wj-auth-card` 06/09). Ghi để lượt auth (nếu có) đo riêng, không sửa ở đây.

### 13.3 Việc đã làm với sheet

`qa_deploy_mark.py UI-SURFACECARD-001 --apply` — chỉ đổi cột P (Build/Deploy) + Ngày cập nhật + 1 dòng
History; **trạng thái giữ `Ready for Dev`** vì cụm mới phủ 144/384 token (37%) và 2 họ còn lại
(`wj-auth-card` LIMIT, nhóm Khảo sát → D4h) chưa có chủ lúc đánh dấu. Verify bằng
`export?format=csv` đối chiếu cột ID dòng tuyệt đối 120.
