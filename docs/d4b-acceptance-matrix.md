# D4b — bảng nghiệm thu SurfaceCard lượt 1

**Ngày:** 2026-09-04 · **Cơ sở:** `c9073c7` · **Spec:** `CMP-SC-001`, `UI-SURFACECARD-001` (STT 127)
· **Phạm vi:** `wujia-kpi-card` (4) + `wujia-content-card` (8) = **12 lượt / 6 file**.

Đây là **lượt hiệu chỉnh** của cụm D4: chọn nó đi đầu không phải vì nhỏ nhất mà vì **cả 5 route
dùng nó đều đo được ở local** — bảng dựng ở đây là khuôn cho D4c…D4f.

---

## 1. Đã làm

| | |
|---|---|
| Component mới | `wujia_portal_layout/views/wj_surface_card.xml` — 4 biến thể × `density` × `bodyMode` × `interactive`, thân đi qua slot `0` |
| Token mới | `--wujia-surface-radius/-pad-compact/-pad-regular/-gap` (+ override `@media max-width:991.98px`) |
| Token gỡ | `--wujia-kpi-card-min-height/-padding/-gap` (chết sau khi dáng khung dời đi) |
| CSS | rút `background/border-radius/box-shadow/padding/gap` khỏi `.wujia-kpi-card` và `.wujia-content-card`; `.wj-surface-card` là **chủ sở hữu duy nhất** |
| Call site | 12/12 chuyển sang `t-call`, **giữ nguyên lớp cũ** qua `sc_class`/`sc_link_class` |
| `-u` | đúng **một lần**, 6 module, RC=0, **0 ERROR** |
| Version | `wujia_portal_layout` 19.0.32.9.0 → **19.0.33.0.0** |

## 2. Số đo bề mặt — đối chiếu bảng BA

Đo bằng `getComputedStyle` trên trang thật, 5 khổ × 5 route (`scratchpad/d4b_measure.py`).

| Thuộc tính | BA desktop | ĐO SAU | BA mobile | ĐO SAU | |
|---|---|---|---|---|---|
| radius | 16 | **16** | 14 | **14** | ✅ |
| viền | 1px `#EEF2F5` | **1px `rgb(238,242,245)`** | 1px `#E5E7EB` | **1px `rgb(229,231,235)`** | ✅ |
| shadow mặc định | không | **none** | không | **none** | ✅ |
| padding compact | 16 | **16** | 12 | **12** | ✅ |
| padding regular | 20 | **20** | 14 | **14** | ✅ |
| gap trong | 12 | **12** (biến thể xếp ngang) | 8 | **8** | ✅ |
| chiều cao | không khoá cứng | **min-height đã gỡ hẳn** | — | — | ✅ |

**Trước** thì cả hai họ đều: `shadow rgba(15,23,42,.04) 0 2px 6px` · **không viền** ·
kpi `padding 16/14` + `min-height 100/92` · content `padding 22` · radius 16 ở mọi khổ.

## 3. Sức khoẻ trang — acceptance BA #11

25/25 ô đo trả trang đúng · 60 bề mặt duyệt được · 0 lỗi JS · 0 tràn ngang · 0 redirect ngầm.

**Số record thấy trong viewport: KHÔNG Ô NÀO GIẢM** (12→12 · 4→4 · 1→1 · 0→0).
Chiều cao trang không đổi ở 24/25 ô; `/portal/knowledge` desktop **−2px** (995 so với 997).

## 4. Hai phát hiện chỉ có phép đo mới thấy

### 4.1 🔴 `min-height` không hề làm 4 thẻ KPI cao bằng nhau — chúng vốn ĐANG SO LE

| | 1440 | 1024 | 992 |
|---|---|---|---|
| trước (có `min-height: 100px`) | **140 / 140 / 105 / 105** | 156/140/140/140 | 175/156/140/140 |
| sau (`height: 100%`) | **142 × 4** | 158 × 4 | 177 × 4 |

Ảnh chụp `/portal@1440` xác nhận bằng mắt. Bỏ `min-height` theo lệnh BA **đồng thời sửa một lỗi
bố cục có sẵn**, chứ không phải đánh đổi. Cách đúng là `height: 100%` trên **cả** thẻ `<a>` bọc
ngoài lẫn card — `.row` đã `align-items: stretch`, chỉ thiếu chỗ chuyền chiều cao qua `<a>`.

### 4.2 🔴 Bẫy #4 của inventory §7 CÓ THẬT — và RULE 1/2 **không bắt được**

Đặt `gap: 12px` ở rule gốc SurfaceCard làm nhịp header→body thành **24px** (12 margin của
`wj_card_header` **cộng chồng** 12 gap), trong khi D3 vừa hội tụ về **12px**.

RULE 1 + RULE 2 vẫn **sạch tuyệt đối** vì chúng đo *sự không đều giữa các card cùng trang* —
mà lỗi này đều tay trên **mọi** card. Phải đo THẲNG giá trị tuyệt đối mới thấy
(`scratchpad/d4b_rhythm.py`).

⇒ Phán quyết: **`gap` chỉ thuộc biến thể xếp ngang `--summary`, KHÔNG đặt ở base.**
Đo lại sau khi sửa: **12px ở cả 8 card** trên cả 5 route.

*Bài học cho D4c…D4f: phép đo quan hệ của D3 REVIEW là điều kiện CẦN, không đủ. Mỗi lượt D4
phải kèm một phép đo tuyệt đối cho nhịp header→body.*

## 5. RULE 1 + RULE 2 chạy lại

`scratchpad/d3_review.py` 29 route × 4 viewport, so với baseline chụp trên **code sạch**
(phải `git stash` để lấy, vì Odoo 19 **tự regenerate asset bundle theo checksum** kể cả khi
không bật `--dev` — sửa CSS là ăn ngay):

| | baseline | sau D4b |
|---|---|---|
| Cờ PHẦN 1 | 5 (4 × `debt-pay` redirect + `inspection@360` tràn 11px) | **giống hệt** |
| Histogram RULE 2 | `[m] 16px ×62` · `[pc] 18px ×86` · `[pc] 20px ×2` | **giống hệt** |
| Nhóm DRIFT chưa giải trình | 0 | **0** |

Cả 5 cờ đều **có sẵn và đã giải trình**: `debt-pay` redirect `no_due` là hành vi đúng của
WJ-DEBT-007; `inspection@360` tràn 11px nằm ngoài phạm vi D4b.

## 6. Test + chứng minh bằng đột biến

`wujia_portal_layout` tag `wujia_surface_card_d4`: **22 test, 0 failed, 0 error**.

Guard xanh sẵn không chứng minh gì — mỗi guard bị làm sai một lần để xem có đỏ đúng chỗ không
(`scratchpad/d4b_mutate.sh`):

| Đột biến | Test phải đỏ | |
|---|---|---|
| trả `box-shadow` về `.wj-surface-card` | `test_surface_card_has_no_default_shadow` | ✅ |
| gỡ viền khỏi `.wj-surface-card` | `test_surface_card_has_one_pixel_border` | ✅ |
| trả `min-height` về `.wujia-kpi-card` | `test_kpi_card_no_longer_locks_height` | ✅ |
| cho `.wujia-content-card` khai lại `padding` | `test_legacy_families_no_longer_declare_surface_shape` | ✅ |
| trả token `--wujia-kpi-card-min-height` | `test_no_kpi_min_height_token_left` | ✅ |
| cắt slot `0` khỏi component | `test_body_passes_through_untouched` | ✅ |
| khoá cứng density về compact | `test_density_regular_replaces_compact` | ✅ |
| bỏ nhánh bọc `<a>` | `test_href_wraps_the_card_in_an_anchor` | ✅ |
| trả `gap` về base | `test_base_card_declares_no_gap` | ✅ |
| gỡ `gap` khỏi `--summary` | `test_summary_variant_owns_the_gap` | ✅ |

**10/10 đỏ đúng chỗ**, đối chứng không đột biến 0 failed.

## 7. Ảnh

`/portal` @1440 và @390, `/portal/support` · `/return` · `/info-request` · `/knowledge` @1440,
trước và sau (`scratchpad/scratchpad/shots_d4b_{before,after}/`). Soi mắt: bố cục không vỡ chỗ
nào; khác biệt thấy được là **viền hiện ra**, **bóng biến mất**, **4 thẻ KPI hết so le**, và chữ
xuống dòng thoáng hơn do padding 22→20.

## 8. LIMIT

1. **Hai họ này là PC-only.** Dưới 992px chúng render `0×0` ở 4/5 route (portal mobile dùng khối
   `wujia-mdash-*` riêng) ⇒ **cột mobile của bảng BA gần như không quan sát được**; chỉ
   `/portal/info-request` cho một điểm đo mobile thật. Rule mobile vẫn viết đủ vì **D4d dùng lại
   chính component này** cho các họ mobile. Hệ quả: `@media` override `padding 14 / min-height 92`
   của KPI trước đây là **code chết** — nay đã dọn.
2. `/portal/support` có sẵn bảng tràn khỏi card ở 1024 (**−7px**) và 992 (**−39px**). Sau D4b:
   1024 **hết hẳn**, 992 còn **−8px**. Lỗi CÓ SẴN, D4b thu hẹp chứ không gây ra; chưa xử vì
   nguyên nhân là bề rộng cột bảng, thuộc `CMP-DL-001` (cụm D5).
3. Mới phủ **12/384 lượt (~3%)** ⇒ issue **giữ `Ready for Dev`**, chưa handoff, chưa chạy
   `qa_sync.py` — đúng tiền lệ C8a→C8b và D3a→D3f.

## 9. Cách tái lập

```
python3 scratchpad/d4b_measure.py before|after   # bảng §2, §3
python3 scratchpad/d4b_rhythm.py  after          # §4.2 — nhịp header→body
python3 scratchpad/d4b_shot.py    before|after   # §7
bash    scratchpad/d4b_mutate.sh                 # §6
cd scratchpad && python3 d3_review.py --base http://127.0.0.1:8072 \
    --portal-login anh.owner --out d4b_d3_final.json && \
    python3 d3_analyze.py d4b_d3_final.json      # §5
```

🔴 `d3_review.py` **mặc định `--portal-login=None`** và rơi về đăng nhập `admin` ⇒ **0 CardHeader
trên mọi route mà vẫn chạy xong** — đúng bẫy "Pass rỗng". Luôn truyền `--portal-login anh.owner`.

Harness đều là **dev-only, gitignored, KHÔNG commit**.
