# D4g + D4h — Soi UAT cho D4f · chốt `wj-auth-card` · nhóm Khảo sát lên SurfaceCard (06/09/2026)

Issue `UI-SURFACECARD-001` (STT 127, sheet dòng tuyệt đối 120, gid 335593633) · component `CMP-SC-001`.
Prompt: `docs/prompt-d4g.md`. Kiểm kê: `docs/d4-surfacecard-inventory.md` §16–§17.

## 0. Ba việc của phiên và kết quả một dòng

| Việc | Kết quả |
|---|---|
| **Bước 0** gỡ lệch nhánh (main máy Mac ↔ D4e1/e2/f máy Linux) | merge `cbd9b21`, main `1c3ac12`, chủ dự án deploy 03:07 UTC |
| **Phần 1** soi UAT chỉ-đọc cho D4f | **KHỚP** cả 3 con số — `d4f-acceptance-matrix.md` §13, LIMIT 7 đóng, sheet cột P đã đánh dấu |
| **Phần 2a** `wj-auth-card` | đính chính 15 → **4 shell**, chủ dự án chốt **giữ nguyên + LIMIT** (S39), 0 code |
| **Phần 2b = D4h** nhóm Khảo sát | **7 shell** migrate (3 họ CSS + 4 hộp inline), 3 token phân loại KHÔNG phải SurfaceCard, 83 test 0 đỏ |

---

## 1. Phần 1 — UAT (tóm tắt, chi tiết ở `d4f-acceptance-matrix.md` §13)

| # | Câu hỏi | UAT 06/09 | Local D4f |
|---|---|---|---|
| 1 | `.card` hiện, 25 route × 5 khổ | **0** | 0 |
| 2 | shell viền/radius/shadow | `1px #EEF2F5`·16·none PC (86/86) · `1px #E5E7EB`·14·none mobile | y hệt |
| 3 | rule ngoài `_components.css` khớp shell | **0** (kể cả `website`/`website_sale`) | 0 |

Điều kiện vào đã kiểm: 21 module `latest == installed == manifest`, layout `19.0.38.0.0`, `?v=1220`,
md5 `_components.css` bằng repo. 0 lỗi JS · 0 HTTP≠200 · 0 redirect ngầm · 0 lồng trắng-trắng.

---

## 2. D4h — nhóm Khảo sát: kiểm kê LÚC CHẠY trên `wujia_tea_d4g` (8076)

Module `wujia_portal_inspection` **installed** trên copy (clone `wujia_tea_d4c`), 1 phiếu
`D4C-INSP-001` (state `need_remediation`, 1 dòng fail id 2) ⇒ render đủ 3 route + 2 popup (ép hiện
bằng class `show-modal`/`show-warning`, chỉ đọc DOM). `scratchpad/d4h_inv.py`, token lớp khớp
`/card|-box$/`, 1440 + 390:

| Token | Số | Ở đâu | Khai dáng ở đâu | Phân loại | Việc |
|---|---:|---|---|---|---|
| `inspection-card-item` | 1 | list mobile, trong `<a>` | CSS `:87` r14 · b1 `#e2e8f0` · bg · **overflow:hidden** · hover shadow | khung record, wholeCard | **migrate** `--record`, `<a>` → `wj-surface-card-link` |
| `detail-card-box` | 1 | hộp mobile duy nhất của chi tiết | CSS `:173` r16 · b1 `#f1f5f9` · shadow `0 2px 8px` | khung section | **migrate** `--section`, rule gỡ hẳn |
| `summary-2x2-card` (+`.severe-card`) | 1 | ô tổng PC, là `<a>` | CSS `:198` r14 · b1.5 `#38bdf8` · p12 · hover shadow | khung summary, wholeCard | **migrate** `--summary`, giữ `border-color` tông xanh (token) |
| `form-card-box` | **4** | remediation, `style=""` tại call site | **inline**: bg · r16 · b1 `#f1f5f9` · shadow | khung section | **migrate** `--section`, xoá 4 `style` |
| `wj-dist-card` | 1 | ô 60×60 phân bổ mobile | CSS `:519` w/h 60 · b2 + `border-top` 4px màu · r12 | **ô chỉ báo** (một con số, viền trên là chỉ báo màu), không phải khung nội dung | để nguyên, **ghim** trong guard |
| `wj-success-card` / `wj-warning-card` | 1+1 | overlay cố định, `transform: scale`, `max-width` | CSS `:446`/`:636` r24/20 · p28/24 · shadow 0 20px 40px | **hộp thoại nổi**, không nằm trong dòng nội dung | để nguyên, **hỏi chủ dự án** (§9) |
| `table-card` · `exam-card` (kiểm kê §2 cũ) | 0 | — | không có trong view lẫn CSS của module | kiểm kê cũ đếm nhầm | đính chính |

Cộng: **7 shell** migrate, **3 token** phân loại ngoài SurfaceCard, 2 token ma. Guard
`test_no_card_token_leaks_into_inspection_views` quét toàn bộ view `wujia_portal_inspection.%`: 0 token
`card` Bootstrap.

## 3. Đã sửa (nhánh `dev/2026-09-06-d4h`)

- `portal_inspection.css`: `.inspection-card-item` chỉ còn `position` + `transition: transform`; hover
  còn `translateY(-2px)`, **bỏ bóng** (chốt D4b: wholeCard hover không thêm bóng). `.detail-card-box`
  gỡ hẳn. `.summary-2x2-card` chỉ còn `border-color: var(--wujia-primary)` + text-align/cursor/display/
  transition; hover bỏ bóng. `.severe-card` **không đụng** (đã là modifier tông: border-color + bg).
- 4 view: list `:189-191`, detail `:131` + `:361`, remediation `:192/224/239/270` — nướng 4 lớp shell,
  giữ lớp riêng module + utility `p-3`/`mb-3`/`mb-4` (bài học D4f #8).
- `wujia_portal_inspection` **19.0.1.3.2 → 19.0.1.4.0**. `_components.css` **không đổi** ⇒ layout và
  `?v=` giữ nguyên (CSS module đi qua `web.assets_frontend`, tự đổi hash).
- Test: `TestSurfaceCardD4h` **+9** ⇒ 74 → **83**, `-u wujia_portal_layout,wujia_portal_inspection`
  RC=0, 0 ERROR, **0 failed / 0 error**.

## 4. Số đo TRƯỚC → SAU (`scratchpad/d4f_d4h_{before,after}.json`, 6 route × 5 khổ)

| | Trước | Sau |
|---|---|---|
| `.card` hiện / DOM | 0 / 0 | 0 / 0 |
| Bề mặt duyệt | 168 | 175 (+7 shell mới) |
| Lỗi JS · HTTP≠200 · redirect ngầm · tràn ngang | 0 · 0 · 0 · 0 | 0 · 0 · 0 · 0 |
| `pageH` | 30/30 ô | **30/30 ô KHÔNG ĐỔI** |
| Record trong viewport (BA #11) | — | **0 ô giảm**; 3 ô mobile tăng 0→1/3 vì hộp mới được đếm là bề mặt; detail PC 5→6 (ô tổng) |
| Bề mặt trắng lồng bề mặt trắng | 6 (detail PC ×3 khổ, 2 cặp) | 6 — **y nguyên**, có sẵn (§9) |

Token đo lúc chạy sau sửa: 7 shell đúng `1px #EEF2F5`·16·none (PC) / `1px #E5E7EB`·14·none (mobile),
riêng ô tổng viền `#28A9DF` do modifier tông; `overflow: visible` ở `inspection-card-item`.

## 5. Nhịp header→body tuyệt đối (`d4h_rhythm.py`, 3 route × 1440/1024)

`-2px ×2 · 12px ×4` **trước = sau**. Hai ô −2px là `wj-card-header` → `<form>` ở remediation PC (có
sẵn, không thuộc dáng khung — địa hạt CardHeader, ghi lại không sửa).

## 6. RULE 1 + RULE 2 (`d3_review.py --base 127.0.0.1:8076 --portal-login anh.owner` → `d3_analyze.py`)

**4 cờ trước = 4 cờ sau**, đều là `debt-pay` redirect ngầm (dữ liệu copy, không có kỳ nợ). Cờ RULE 1
"404 tràn ngang 11px @360" của D4f (LIMIT 3) **biến mất** vì inspection nay installed. 0 nhóm cỡ chữ drift.

## 7. Ảnh trước–sau + diff pixel (`shots_d4f/d4h_{before,after}/`, 6 route × 1440/390/360 = 18 tấm)

| Nhóm | Kết quả |
|---|---|
| Ngoài phạm vi: `/portal/support` ×3, `/portal/franchises/1/profile` ×3, `/portal@1440` | **giống hệt từng pixel** |
| `/portal@390/360` | khác 86–1132 px trong đúng hộp *Khung giờ đặt hàng* = **đồng hồ đếm ngược** (`còn 17:35` → `17:31`, cắt ảnh đọc được) |
| `/portal/inspection@1440` | 0 px vượt ngưỡng (khử răng cưa) |
| `/portal/inspection@390/360` | thẻ list mobile: viền `#e2e8f0` → `#E5E7EB`, hết `overflow:hidden` — mắt thường như cũ |
| `/portal/inspection/detail/1@1440` | ô tổng: viền 1.5px sky → 1px `--wujia-primary`, r14 → 16, đệm 12 → 16 |
| `/portal/inspection/detail/1@390/360` | hộp mobile: **mất bóng**, r16 → 14 |
| `/portal/inspection/remediation/2@1440` | **giống hệt** (PC dùng shell từ trước) |
| `/portal/inspection/remediation/2@390/360` | 3 hộp form: **mất bóng**, viền `#f1f5f9` → `#E5E7EB`, r16 → 14 |

## 8. Guard chứng minh bằng ĐỘT BIẾN — `scratchpad/d4h_mut.py`, 15 đột biến

**15/15 đột biến bị bắt**, mỗi vòng `-u layout,inspection --test-tags wujia_surface_card_d4` có đếm `post-tests`
(bài học D4f #5 — "0 test đã chạy" là xanh giả). Danh sách: `<a>` mất `wj-surface-card-link` · item rơi `--padded`
· `.detail-card-box` khai dáng lại · ô tổng hex thay token · ô tổng khai padding · `.severe-card` khai radius ·
hover có bóng lại · `overflow:hidden` quay lại · ô tổng mất shell · hộp mobile mất shell · 1/4 hộp form lấy lại
`style` inline · 1/4 hộp rơi `--padded` (3 đủ 1 thiếu — guard **đếm** bắt được) · hộp thoại bị ép vào shell ·
hộp thoại mất bóng (đổi phân loại lén) · thẻ Bootstrap `card` lọt vào view (đỏ **2 test**: D4f toàn portal + D4h).
Sau vòng: file gốc khôi phục, `git diff` chỉ còn thay đổi cố ý (§3).

## 9. Hai câu hỏi cho chủ dự án (không tự quyết)

1. **Hộp thoại `wj-success-card` / `wj-warning-card`** — hiện phân loại *không phải SurfaceCard* (overlay
   cố định, `scale` animation, shadow là độ nổi của dialog). Ép vào shell thì mất bóng + đệm 28/24 → 16.
   Ảnh: `scratchpad/d4h_before_wj-success-overlay_{1440,390}.png`. Chủ dự án chốt: giữ (mặc định) hay ép?
2. **Ô tổng trắng lồng trong card trắng** (`summary-2x2-card` trong `wj-pc-card`, + 1 hộp `border rounded
   bg-white` inline ở `:222`) — có sẵn từ trước D4h, BA ghi "không lồng white card". Muốn hết lồng thì đổi
   ô tổng sang `--tonal` (mất viền xanh điểm nhấn) — cần chủ dự án chốt vì là đổi thiết kế.

## 10. Đối chiếu `Kết quả mong muốn` — TOÀN ISSUE sau D4b→D4h

| Yêu cầu BA | Kết quả |
|---|---|
| Radius 16/14 | ✅ token, đo UAT 86/86 + copy 7/7 |
| Compact pad 16/12 · regular 20/14 | ✅ token; utility tại call site giữ (nhịp cố ý) |
| Gap 12/8 | ✅ `--summary` |
| Viền nhẹ, không shadow mặc định | ✅ UAT + copy; hover wholeCard cũng không bóng |
| Không lồng white card | ⚠ 2 cặp có sẵn ở chi tiết khảo sát PC — chờ chủ dự án (§9.2) |
| Không thưa hơn (#11 record trong viewport) | ✅ 0 ô giảm ở mọi lượt |
| Test 1440/1024/992/390/360 | ✅ mọi lượt + UAT |
| Một chủ sở hữu dáng khung | ✅ 0 rule ngoài `_components.css` (UAT + repo) |
| Màn Khảo sát chỉ nghiệm thu field mapping sau khi có seed | ✅ D4h chỉ động **khung**; field mapping không đụng |
| Auth (S39) | LIMIT — chủ dự án chốt giữ |

**9/10 ✅, 1 ⚠ chờ chốt ⇒ ≥ 90%.** Phủ **151/380 token đã xử lý**; số còn lại là token con/modifier
không phải khung (xem inventory §17).

## 11. LIMIT ghi vào ledger

1. `wj-auth-card` (4 shell) giữ thiết kế S39 — chủ dự án chốt 06/09.
2. Hộp thoại `wj-success-card`/`wj-warning-card` + ô chỉ báo `wj-dist-card` phân loại ngoài SurfaceCard, ghim guard.
3. 2 cặp trắng-lồng-trắng ở chi tiết khảo sát PC có sẵn, chờ chốt thiết kế.
4. D4h **chưa lên UAT** — cần deploy lượt 3 `-u wujia_portal_inspection` (`docs/deploy-d4h-2026-09-06.md`), đo lại chỉ-đọc.
5. LIMIT 1/2/4/5/6 của D4f còn nguyên (module bên thứ ba, `/my/franchises`, tz R3, template chết, `card-img-top`).
