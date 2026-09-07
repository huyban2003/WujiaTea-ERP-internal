# Prompt phiên D4b — SurfaceCard lượt 1 (`wujia-kpi-card` + `wujia-content-card`)

> Dán nguyên khối dưới đây vào phiên mới. Phiên đó **không có** ngữ cảnh D4a, nên mọi thứ cần đã nằm sẵn ở đây.

---

Chạy `/wujia-start` trước, rồi làm cụm **D4b** — lượt migrate đầu tiên của `UI-SURFACECARD-001`
(STT 127, component `CMP-SC-001`, tab `UI Component` gid 488333015).

## Đọc bắt buộc trước khi gõ dòng code nào

1. `docs/d4-surfacecard-inventory.md` — kiểm kê D4a đã được chủ dự án duyệt. §1 phép thử phân loại,
   §4 bảng họ, §7 năm chỗ chỏi issue đã nghiệm thu, §8 bảng token.
2. `docs/next-session-clusters-D.md`, mục **D4** — kế hoạch chia lượt D4b…D4f + phần
   "🔴 Ràng buộc ĐO ĐƯỢC".
3. `docs/d3-review-matrix.md` §1 — **RULE 1 / RULE 2**: đo *quan hệ* (so với hàng xóm cùng trang,
   so với cùng vai trò ở màn khác), không đo hằng số. D4b phải chạy lại hai rule này.
4. `docs/01_NGO_GIA_QA_OPERATING_STANDARD.md` — Dev không tự đóng `Done`, chỉ tới `Ready for Retest`.

## Phạm vi D4b — ĐÚNG hai họ, 12 lượt dùng, 6 file. Không mở rộng.

| Họ | Lượt | File gọi |
|---|---|---|
| `wujia-kpi-card` (+ `wujia-kpi-card-link`) | 4 | `custom/wujia_portal_base/views/portal_home.xml:33,52,71,90` (link ở `:32,51,70,89`) |
| `wujia-content-card` | 8 | `portal_home.xml:114,141,170,200` · `wujia_portal_info_request/views/portal_info_request_list.xml:69` · `wujia_portal_knowledge/views/portal_knowledge.xml:80` · `wujia_portal_return/views/portal_return_list.xml:79` · `wujia_portal_support/views/portal_support.xml:49` |

**Vì sao lượt này đi trước** (không phải vì nhỏ nhất): cả 5 route của nó **đo được ở local**
— `/portal` (8 surface) · `/portal/knowledge` (2) · `/portal/support` (1) · `/portal/return` (1)
· `/portal/info-request` (1). Họ to hơn (`wj-pc-metric-card`, 44 lượt) nằm trọn trong hai route
**không đo được** (`/portal/reports/orders` đang 500 — cụm R3; `wujia_portal_inspection` chưa cài
ở local), nên không thể ra bảng trước–sau ⇒ đẩy xuống D4e. Đừng đảo lại thứ tự này.

**Một nhóm rủi ro đồng nhất: "bỏ bóng, thêm viền".** Cả hai họ đều đang có
`box-shadow: var(--wujia-card-shadow)` (BA: *không shadow mặc định*) và **không có viền nào**
(BA: viền 1px `#EEF2F5` desktop / `#E5E7EB` mobile).

## Neo CSS chính xác (đã đọc, đừng grep lại từ đầu)

`custom/wujia_portal_layout/static/assets/css/_components.css`
- `:449` `.wujia-kpi-card-link` — `display:block`, không có dáng
- `:454` `.wujia-kpi-card` — `gap:457` `--wujia-kpi-card-gap` · `min-height:458` · `padding:459`
  · `background:460` · `border-radius:461` = `--wujia-card-radius` · **`box-shadow:462`** · `transition:463`
- `:465-466` `.wujia-kpi-card-link:hover .wujia-kpi-card, .wujia-kpi-card:hover` — `translateY(-2px)`
  + shadow đậm. Đây là `interactive: wholeCard`.
- `:533`, `:537` — hai rule trong `@media` cho `wujia-kpi-card-link`
- `:543` `.wujia-content-card` — `background:544` · `border-radius:545` · **`box-shadow:546`**
  · `padding:547` = `--wujia-content-card-padding` · `height:100%` · flex column
- `:625` `.wujia-content-card--flush` — biến thể `flushBody` đã tồn tại
- `:3235` `.wj-card-header + .wujia-content-card-table { margin-top: 0 }` — nhịp D3 vừa hội tụ

`custom/wujia_portal_layout/static/assets/css/_variables.css`
- `:120` `--wujia-card-radius: 16px` (đúng số BA desktop) · `:122` `--wujia-card-shadow`
- `:126-128` `--wujia-kpi-card-min-height 100px` · `-padding 16px` · `-gap 12px`
  → mobile override `:351-352` `min-height 92px` · `padding 14px`
- `:195` `--wujia-content-card-padding: 22px` · `:201` `--wujia-content-card-row-gap: 14px`
- `:34` `--wujia-border: #E5E7EB` · `:35` `--wujia-border-soft: #EEF2F5` — **hai hex BA cần đã có token**, dùng lại, đừng viết hex thô.

## 🔴 Ba cái bẫy đã dò sẵn — đọc kỹ, đây là chỗ dễ làm hỏng ngoài phạm vi

1. **`--wujia-card-shadow` KHÔNG được sửa ở token.** Nó có 3 nơi dùng:
   `_components.css:12` `.card { box-shadow: var(--wujia-card-shadow) }` ← **Bootstrap `.card` toàn cục,
   thuộc D4f**, cộng `:462` và `:546`. Bỏ bóng thì bỏ **tại hai rule của hai họ**, giữ nguyên token.
2. **`--wujia-card-radius` KHÔNG được sửa ở token.** Ngoài hai họ này nó còn nuôi
   `_auth.css:80` (`wj-auth-card` — THIẾT KẾ S39, cấm đụng), `_components.css:417`,
   `_wujia_theme.css:325`, `wujia_portal_sale/.../portal_order.css:2,4,9`,
   `wujia_portal_base/.../store_picker.css:5`. Desktop 16px đã đúng BA rồi ⇒ **không cần đổi gì**.
   Nếu cần bán kính mobile 14px thì viết rule **scope vào đúng hai class** trong `@media`, không đụng token.
3. **`--wujia-content-card-padding` không chỉ là padding khung.** Nó còn là **margin âm** của bảng
   flush: `:635` `margin: 16px calc(-1 * var(--wujia-content-card-padding)) 0`,
   `:636` `width: calc(100% + 2 * ...)`, và padding ô `:645`, `:652`. Đổi 22 → 20 là **đổi mép bảng
   ở 31 chỗ `.wujia-content-card-table` chưa migrate** (xem chú thích `:3233`). Phải đo lại các trang
   có bảng flush, không chỉ 5 route trong phạm vi.

## Số BA phải đạt (`CMP-SC-001`)

| | desktop | mobile |
|---|---|---|
| radius | 16 | 14 |
| border | 1px `#EEF2F5` (`--wujia-border-soft`) | 1px `#E5E7EB` (`--wujia-border`) |
| shadow mặc định | **không** | **không** |
| padding | compact 16 · regular 20 | compact 12 · regular 14 |
| gap trong | 12 | 8 |
| chiều cao | **không khoá cứng** | — |

Biến thể D4a đã map: `wujia-kpi-card` = **`summary`**, `density: compact`, `bodyMode: padded`,
`interactive: wholeCard`. `wujia-content-card` = **`section`**, `density: regular`,
`bodyMode: padded` (biến thể `--flush` = `flushBody`), `interactive: none`.

⇒ Suy ra việc thật: kpi padding 16 desktop **đã đúng**, mobile 14 → **12**; content-card 22 → **20**
desktop, mobile → **14**; `min-height 100px/92px` là **khoá chiều cao**, BA cấm ⇒ đề xuất bỏ,
nhưng phải đo trước–sau xem 4 thẻ KPI ở `/portal` có bị so le không (nếu có, dùng grid
`align-items: stretch` chứ **không** quay lại min-height).

## Nghiệm thu — không đủ thì không được ghi Ready for Retest

1. **Bảng đo trước–sau** ở đủ **5 khổ BA: 1440 / 1024 / 992 / 390 / 360**, cho cả 5 route.
   Mỗi ô ghi: chiều cao trang · **số record thấy trong viewport** (nghiệm thu BA #11:
   *số record thấy trong viewport không được giảm*) · radius/border/padding/shadow đo bằng
   `getComputedStyle`. Đo bằng Playwright, đăng nhập qua `POST /web/session/authenticate`
   + bơm cookie `session_id` — **`page.fill` luôn timeout** vì trang login S39 ẩn form.
   Điều hướng bằng `wait_until="domcontentloaded"` + chờ 1200ms; **`networkidle` không bao giờ
   kích hoạt** trên trang có `bus.bus`.
2. **Chạy lại RULE 1 + RULE 2** bằng `scratchpad/d3_review.py` (đã có sẵn, gitignored) — đổi padding
   khung là đổi nhịp header→body 12px mà D3 vừa hội tụ. Không đủ nếu chỉ "nhìn thấy vẫn ổn".
3. **Chụp ảnh** `/portal` ở 1440 và 390, trước và sau. Bài học D3e: số Pass hết mà bố cục vẫn vỡ,
   chỉ ảnh mới bắt được.
4. **Guard phải chứng minh bằng đột biến**: viết test rồi cố tình sửa CSS cho sai → test phải đỏ →
   hoàn nguyên. Test xanh sẵn không chứng minh được gì.
5. **Đặc hiệu CSS**: rule scope mới phải đếm đặc hiệu **so với các rule cùng file**, không chỉ so với
   component. `:not()` mang đặc hiệu của tham số. Bẫy này đã tái xuất **hai lần** ở D3.
6. `-u` **đúng một lần**: `wujia_portal_layout,wujia_portal_base,wujia_portal_info_request,wujia_portal_knowledge,wujia_portal_return,wujia_portal_support`.
7. Xong → ghi `docs/qa-issue-ledger.yaml` (FIX/IMPACT/RETEST/LIMIT) rồi
   `cd scripts/ba_spec && python3 qa_sync.py --dry-run` → `--apply`.

## Ngoài phạm vi D4b — thấy cũng để yên

- `/portal/exam/register` mang **2 ca vi phạm "thẻ trắng lồng thẻ trắng"** mà quét tĩnh không thấy
  (D4a §3). Đó là **D4c**, không phải D4b.
- `wj-auth-card` (15 lượt) — THIẾT KẾ Figma S39, giữ nguyên dáng.
- `wj-filter-card` (7) và `wj-pc-acct-headcard` (20) — chưa xếp lịch được, xem D4a §6.
- Bootstrap `.card` thô — D4f.
- **Không** `-u` / `-i` `wj_ks_*` và `wujia_portal_remediation` (đã gỡ khỏi DB).

## Môi trường (đã dựng sẵn ở phiên D4a)

- DB dev `wujia_tea_19` **đã nâng cấp**: `wujia_portal_layout` 19.0.31.13.0 → **19.0.32.9.0**, 0 ERROR.
  Nếu route trả 404 kèm *"Không tìm thấy mẫu"* thì là DB cũ hơn code ⇒ chạy `-u`, đừng đi tìm bug logic.
- Server đo: `http://127.0.0.1:8072` (phiên D4a đã tắt, bật lại khi cần).
- Đăng nhập portal: **`anh.owner` / `wujia@test123`** (đã reset). **Đừng dùng `admin`** — uid 2 không
  phải user portal franchise, mọi route portal sẽ 404 mà harness vẫn báo "đo được N surface"
  (bẫy "Pass rỗng"). Dò mật khẩu quá 5 lần sẽ dính *"Too many login failures"*, phải restart server.
- Harness đo để trong `scratchpad/` (**gitignored**, không commit).

## Nguyên tắc xuyên suốt

**Ask-don't-assume** · **Read-before-write** · **Perf-first** (portal 1500 user) ·
comment trong code **gọn, 1 dòng đủ ý** · **kiểm kê là SÀN không phải TRẦN** — nếu tìm thấy lượt
dùng thứ 13 mà D4a bỏ sót thì ghi bổ sung vào `docs/d4-surfacecard-inventory.md`, đừng lặng lẽ sửa.
