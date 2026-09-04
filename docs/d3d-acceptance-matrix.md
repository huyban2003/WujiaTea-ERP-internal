# D3d — bảng đối chiếu acceptance (UI-CARDHEADER-001, STT 125 · `CMP-CH-001`)

**Ngày đo:** 2026-09-04 (local, chưa deploy) · **Kết quả: 21/23 Pass, 2 phần (95,7%)** — hai ô
"phần" đều là **phạm vi cố ý**, không phải lỗi: (a) 3 call site defer chờ BA, (b) sau D3d mới phủ
**61/103** call site nên issue **giữ `Ready for Dev`** (tiền lệ C8a→C8b) ⇒ phiên này **KHÔNG** chạy
`qa_sync.py`. Kiểm kê gốc rễ → `d3-cardheader-inventory.md`. Ba phiên trước →
`d3-acceptance-matrix.md`, `d3b-acceptance-matrix.md`, `d3c-acceptance-matrix.md`.

**Phạm vi phiên:** **14 call site / 1 file / 1 module** — `wujia_portal_exam/views/portal_exam.xml`,
file đông call site nhất của cụm D3.

> ⚠️ **Đính chính con số bàn giao (lặp lại bài học D3c: đừng tin doc bàn giao).**
> `docs/next-session-clusters-D.md` ghi "21 chỗ". Chạy lại `scratchpad/d3_inventory.py` cho thấy
> con số đó **cộng cả 4 dòng đã bị §3 inventory loại** (`:279` cal-head không title · `:378` slot
> phải · `:521`/`:527` chữ vùng kéo-thả) ⇒ còn **17**. Chủ dự án chốt **defer 3** ⇒ **14 làm thật**.

**Môi trường:**
- **A/B bằng 2 DB, không phải 2 commit** (thay đổi nằm ở `arch_db`). `wujia_tea_d3d_b` = "trước"
  **:8070** · `wujia_tea_d3d_a` = "sau" **:8071**, `--db-filter` riêng từng cái — **KHÔNG đụng
  `wujia_tea_19`/8019**. Hai DB clone cùng nguồn **kèm filestore** (thiếu filestore → hàng chục
  `FileNotFoundError` attachment).
- Đăng nhập form portal `anh.owner` (L13/3) + cookie `wujia_active_franchise_id=1`, viewport BA
  **1440 · 390 · 360**, cộng **1920** để nối lưới B4 cũ.
- Harness: `scratchpad/d3d_measure.py` · `d3d_shot.py` · `d3d_wizard_behavior.py` ·
  `d3d_tabwalk.py` · `d3d_uat_versions.py` + chạy lại `d3_measure.py`, `d3b_measure.py`,
  `d3c_measure.py`, `scripts/ba_spec/b4_regression.py` (dev-only, không commit — §13).
- ⚠️ **Phải bơm dữ liệu để wizard chạy được:** mọi ca thi trong DB đều **đã quá khứ** ⇒ khóa thi
  render `is-closed`, không có link "Chọn", wizard đứng ở bước 1. Đã seed session `id=900`
  (2026-09-20) **giống hệt nhau trên cả hai DB**. `_selectable()` đọc field **stored**, nên ngoài
  `name` (NOT NULL) còn phải set `available_participant_count=20`, `reserved_participant_count=0`,
  `max_participants_per_registration=4` — thiếu thì ngày vẫn xám.

---

## 1. Giả-heading — yêu cầu cốt lõi của `CMP-CH-001`

| Route | Nền tảng | Giả-heading trước | sau | `.wj-card-header` sau |
|---|---|---|---|---|
| `/portal/exam` | PC | 1 | **0** | 1 |
| `/portal/exam` | mobile | 3 | **0** | 3 |
| `/portal/exam/register` | PC | 7 | **1** ⚠️ | 4 |
| `/portal/exam/register` | mobile (4 bước) | 5 | **0** | 5 |
| `/portal/exam/registration/14` | PC | 4 | **0** | 2 |
| `/portal/exam/registration/14` | mobile | 1 | **0** | 1 |

**21 → 1.** Ô ⚠️ duy nhất còn lại là `wj-exam-pc-parthead` — **defer có chủ đích** (mục 6), không
phải sót. **Pass.**

## 2. Số đo BA — 32 ô đo (mỗi header × mỗi breakpoint)

Chuẩn: PC compact **18/24/700**, mobile compact **16/22/700**, subtitle **14/20/400**, màu
**`rgb(17,24,39)`**.

**32/32 ô đúng cả 4 thuộc tính** (`fontSize`, `lineHeight`, `fontWeight`, `color`). Không ô nào lệch.

Sai lệch trước→sau **đều đi về phía chuẩn BA**:

| Header | trước | sau |
|---|---|---|
| "Lịch sử đăng ký" (PC) | 22 / 26,4 | **18 / 24** |
| "Thông tin đăng ký", "Tóm tắt đăng ký", "Kết quả thi" (PC) | 20 / 24 | **18 / 24** |
| "Khung giờ ngày" (PC) | `<p>` 16 / 21 | **`<h4>` 18 / 24** |
| "Chọn lịch thi" (PC) | 18 / 22 | 18 / **24** |
| Tiêu đề bản ghi mobile | 16 / 19,2 | 16 / **22** |
| Thẻ "đã chọn" mobile | 15 / 18 | **16 / 22** |
| "Thông tin lịch thi", "Nhân sự tham gia" (mobile) | 16 / 20,8 | 16 / **22** |

## 3. Mật độ trước–sau — BA đòi *"không làm giao diện thưa hơn"*

`cardH` của chính thẻ chứa header (đọc `cardH` chứ không đọc `scrollHeight` vì trang ngắn hơn
viewport bị kẹp — bài học D3c):

| Route @1920 | trước | sau | Δ |
|---|---|---|---|
| `/portal/exam` card danh sách | 460,4 | 454 | **−6,4** |
| `/portal/exam/register` card chính | 828,5 | 821,5 | **−7** |
| `/portal/exam/register` card tóm tắt | 626 | 620 | **−6** |
| `/portal/exam/registration/14` | 664 | 652 | **−12** |

**Ở 1920 mọi thẻ đều thấp hơn sau migrate.** Ba ô mobile cao thêm **+3 → +9px** (`exam-reg-m1`
113,4→116,3 · `m2/m3` 73→77 · `m4` 68,8→78) là **hệ quả trực tiếp của chuẩn BA** — line-height
19,2→22 trên chính dòng tiêu đề, không phải khoảng trắng thừa. **Pass.**

`textDigest` **giống hệt nhau ở cả 18/18 ô đo** ⇒ không chữ nào mất, không chữ nào thêm.
`overflowX = 0` ở cả 18 ô. **Pass.**

## 4. Cấu trúc heading

`outline` cải thiện thật, không chỉ đổi CSS: `/portal/exam/register` PC **realHeadings 5 → 6** vì
`<p class="wj-exam-pc-slots__title">` trở thành `<h4>` thật. Các route còn lại giữ nguyên số heading
và đúng thứ bậc h1 → h2 → h3 → h4, không nhảy cấp. **Pass.**

## 5. ⚠️ Bẫy specificity lặp lại lần thứ hai (D3b `--flush` → D3d `--sechead`)

Rule nhịp dọc cũ `.wj-exam-pc-sechead--2 { margin-top: 28px }` là **(0,1,0)**, thua rule component
`.wj-card-header--pc.wj-card-header--compact { margin: 0 0 12px }` **(0,2,0)** ⇒ "Kết quả thi" **mất
sạch 28px nhịp trên** mà **mọi số đo font/màu/gap vẫn Pass**.

**Chỉ ảnh chụp mới bắt được.** Sửa: bám kèm `.wj-card-header` để lên (0,2,0):

```css
.wj-card-header.wj-exam-pc-sechead--2 { margin-top: 28px; }
.wj-exam-pc-fcard .wj-card-header.wj-exam-pc-sechead--sm { margin-top: 16px; }
```

Đo lại: `hbMarginTop` = **28** ("Kết quả thi") và **16** ("Chọn lịch thi") — đúng nhịp cũ. Đây là
**2 rule duy nhất** thêm vào `portal_exam.css`; `_components.css` chung **không đụng**.

## 6. JS coupling — rủi ro riêng của D3d, đã chứng minh hai chiều

`portal_exam_wizard.js` đọc **thẳng tên class tiêu đề** để chép tên khóa thi sang thẻ "đã chọn" ở
bước 2/3. Migrate mà quên sửa là **chết im lặng, 0 lỗi JS**.

Đã đổi sang class component, **giữ nguyên gốc tìm kiếm** (`card` / `wizard`) để không bắt nhầm
tiêu đề khác:

```js
var titleEl = card.querySelector('.wj-card-header__title');
wizard.querySelectorAll('.wujia-mexam-selcard .wj-card-header__title').forEach(...)
```

Chứng minh ràng buộc là **load-bearing**, hai chiều:
1. Server "trước" (markup cũ + JS mới trên đĩa) **đứng ở bước 1** — không chọn được khóa thi.
2. Cố tình đổi selector về class cũ ⇒ tên khóa thi **biến mất khỏi bước 2 và 3**, console sạch bong.

`.wujia-mexam-course-meta`, `.wujia-mexam-selcard-meta`, `[data-exam-sched-line]`,
`.wujia-mexam-person-name` **cố ý không đụng** — JS sở hữu các hợp đồng đó. **Pass.**

**Hành vi wizard chạy tay end-to-end trên DB copy: 6/6** (chọn khóa → chọn ngày → chọn khung giờ →
thêm người → xóa người → xem tóm tắt).

## 7. Hồi quy

| Phép | Kết quả |
|---|---|
| Lưới B4 | **286/286** |
| Tab-walk bàn phím | **12/12** — cùng số stop, cùng thứ tự, còn ring (253/259 stop có ring) |
| Chạy lại bảng D3c | **0 lệch** |
| Chạy lại bảng D3b | 6 lệch — **đã truy nguyên, không phải hồi quy** (mục 8) |
| `pageerror` | **0** |
| Tràn ngang | **0** |
| HTTP | 200 toàn bộ route |
| Test `wujia_portal_layout` | **73 test, 0 failed / 0 error** |
| Test 10 module đụng tới | **316 test, 0 failed / 0 error** |
| Mutation check | **đỏ đúng 1 test** (`test_wizard_still_scopes_selected_card_title_to_that_card`) |
| `-u` build | **RC=0, 0 ERROR** |

Test mới: `TestCardHeaderExamJsContract` (3 test) + 14 dòng `CALL_SITES` + `RETIRED_IN_VIEW` cho
các class exam đã nghỉ hưu, đặt trong `wujia_portal_layout/tests` (nơi chứa test `post_install`;
`-u wujia_portal_exam --test-tags` ra "0 tests" mà RC vẫn 0 — bẫy cũ).

## 8. LIMIT — ghi tường minh, không giấu

**L1 · 3 call site defer chờ BA (không đụng file).**
- `:375` `wj-exam-pc-parthead` — trailing có **HAI** vùng (ô "Ghi chú" + nút "Thêm người"), spec
  `CMP-CH-001` cho **tối đa MỘT** ⇒ xếp cùng danh sách chờ BA với `wj-pc-acct-headcard`
  (§6 inventory, treo từ D3a).
- `:769` `wujia-mexam-person-head` — cũng 2 trailing (badge "Bắt buộc" + nút xóa) **và** là node bị
  `portal_exam_wizard.js` `cloneNode` làm template ⇒ rủi ro cao, chờ BA cùng lượt.
- `:858` `wujia-mexam-sheet-title` — bottom-sheet overlay, **loại** theo đúng tiền lệ §3
  (`mobile_bottomnav.xml:58`): không phải tiêu đề card trong trang.

**L2 · Phủ 61/103 (59,2%).** Issue **giữ `Ready for Dev`**, ledger giữ dạng comment, **không** chạy
`qa_sync.py`. Còn lại D3e trở đi.

**L3 · Cột PC bị bóp ở ≤1440 — lỗi có sẵn, KHÔNG phải hồi quy D3d.** `.wj-exam-pc-slots` còn 135px
và `.wj-exam-pc-parthead > div` còn 59px ở 1440 ⇒ chữ xuống dòng từng ký tự. **Đo trên cả server
"trước"** ra y hệt: trang `/portal/exam/register` được dựng cho 1920. Ảnh `reg-1440-before.png` vs
`reg-1440-after.png` chồng khít về bố cục. Ghi nhận thành **finding riêng**, không sửa trong D3d
(ngoài phạm vi issue CardHeader).

**L4 · 6 lệch của bảng D3b ở `/portal/reports/orders` là artifact của DB baseline.** Đo lặp 3 lần
mỗi server — **ổn định**, nên không phải nhiễu. Truy bằng listener `requestfailed`: server "trước"
**không tải nổi `web.assets_frontend.min.js`** ⇒ ApexCharts không render (`chartH` None vs 250),
kéo `cardH` 308→322. **Bản thân CardHeader giống hệt nhau (56px) ở cả hai bên** ⇒ không liên quan
D3d.

**L5 · Chưa xóa class CSS cũ.** `wj-pc-card__head`, `wujia-mexam-card-top`, `wujia-mexam-course-main`,
`wujia-mexam-selcard-main`… vẫn giữ qua `ch_class` — **khóa theo ràng buộc thứ tự C8a→C8b**, dọn
một lượt khi D3 đủ 100%.

## 9. Ảnh trước/sau

`scratchpad/d3d-shots/` — 9 cặp (list PC/mobile · register PC + 4 bước mobile · detail PC/mobile).
Chụp **lại sau khi sửa specificity** ở mục 5. Đối chiếu mắt: nhịp dọc khôi phục, badge trạng thái
không trôi ra mép (bẫy `.wj-card-header__lead{flex:1 1 auto}` của D3c **không tái diễn** ở file này),
bố cục chồng khít bản "trước" ngoài phần cao/thấp đã giải thích ở mục 3.

## 10. Deploy

```
-u wujia_portal_layout,wujia_portal_exam
```

`wujia_portal_exam` **19.0.5.7.0 → 19.0.5.8.0**. **Không** module mới, **không** migration,
**không** cần bump `?v=` (CSS/JS exam nằm trong `web.assets_frontend`, không phải `<link>` tay).

**Harness đo lại UAT đã viết sẵn và đã chạy thử TRƯỚC deploy** (chỉ-đọc, giới hạn QA §10 — không
submit wizard, 4 bước mobile kích hoạt bằng gỡ `hidden` chứ không bấm nút). Baseline trước deploy:
**74/74 header D3a+D3b+D3c vẫn đạt toàn bộ số BA**, và 3 route exam ra **đúng 21 giả-heading** khớp
tuyệt đối với phía "trước" đo ở local ⇒ harness đo đúng chỗ, sau deploy con số này phải về **1**.
id phiếu thi **scrape từ chính trang danh sách** (ra `/portal/exam/registration/4` — id DB copy là
14, **không dùng lại được**; bẫy D3b/D3c). Đã gỡ 2 false-positive mà audit 03/09 đã kết luận:
lớp `card-header` (vừa là div Bootstrap bao ngoài vừa là `ch_class` của chính component) và 4 tiêu
đề gõ nhầm route ở `/portal/support/new` (chúng thuộc `/portal/return/new`).

Sau khi chủ dự án deploy: chạy `scratchpad/d3d_uat_verify.py` **chỉ-đọc** trên UAT, 3 breakpoint
1440/390/360, **kỳ vọng theo nền tảng** (khối `d-none d-lg-*` ĐÚNG RA phải vắng ở mobile — harness
mù nền tảng từng báo 7 lỗi giả ở D3a), rồi mới `qa_deploy_mark.py`.

---

## Phụ lục — smoke review D3a→D3c (30 phút, chỉ đọc)

Không mở lại kết luận của audit sâu 03/09; chỉ kiểm ba thứ dễ trôi:

1. **Version đĩa ↔ UAT khớp 9/9 module** (đọc `ir.module.module` qua XML-RPC). Bẫy 02/09 (D3c code
   xong quên merge+push, cả ngày không ai biết) **không tái diễn**. `main == origin/main`.
2. **Grep 47 call site cũ**: còn nguyên 47, **không** còn `mb-*` sót trên `t-call` CardHeader,
   **không** còn class tiêu đề cũ chưa gỡ trong khối đã chuyển.
3. **Đo lại UAT ở 1440**: **38/38 header đạt số BA**. 6 mục harness gắn cờ đều tái hiện đúng các
   **false-positive đã ghi trong audit 03/09** (mù nền tảng + heading ngoài card).

⇒ D3a–D3c **sạch**, không phát sinh việc.
