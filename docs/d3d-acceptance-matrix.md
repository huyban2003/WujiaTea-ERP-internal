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

**L3 · ĐÃ SỬA (bổ sung 04/09, sau khi đo trên UAT thật).** Xem §11.

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


---

## 11. Bổ sung sau deploy — vá bố cục `/portal/exam/register` dưới 1600px

Đo lại chỉ-đọc trên UAT ngay sau khi deploy: **123/128 header đạt toàn bộ số BA**. 5 dòng còn lại
đều thuộc **cùng một trang** (harness đo lặp trang đó 5 lần vì 4 bước wizard dùng chung URL), gồm
đúng 2 phát hiện:

**(a) `wj-exam-pc-sectitle` còn 1 — ĐÚNG THIẾT KẾ, không phải sót.** Đó là `<h3>` "Người tham gia"
ở `:398`, chính là call site **defer chờ BA** (2 trailing). Nó vẫn là **heading thật**, chỉ chưa
dùng component chung. Harness ban đầu chặn nhầm theo tên `wj-exam-pc-parthead` (tên của **div bọc**)
nên không nhận ra — đã sửa danh sách bỏ qua.

**(b) Tiêu đề "Khung giờ ngày" ra 3 DÒNG ở ≤1450 — vi phạm spec (tối đa 2), PHẢI SỬA.**

Gốc rễ là lỗi **có sẵn**: `.wj-exam-pc-schedule` khai `grid-template-columns: 646fr 390fr`, nhưng
track `fr` mặc định có `min-width: auto` ⇒ cột lịch **không chịu co** dưới min-content 572px của
lưới 7 ngày, nên **toàn bộ phần thiếu dồn hết sang cột "Khung giờ"**:

| Bề rộng | 1920 | 1600 | 1560 | 1520 | 1450 | 1440 |
|---|---|---|---|---|---|---|
| Cột "Khung giờ" | 389px | 235px | 206px | 178px | **135px** | **135px** |
| Tiêu đề | 1 dòng | 1 dòng | 1 dòng | **2 dòng** | **3 dòng** | **3 dòng** |
| Tiêu đề "Người tham gia" | 295px | 159px | 130px | 102px | **59px** | **59px** |

D3d **không gây ra** lỗi này (đo trên bản trước migrate ra squeeze y hệt), nhưng tiêu đề lên 18px
theo chuẩn BA đã đẩy nó **từ 2 dòng thành 3** ⇒ vượt ngưỡng spec, không để lại thành nợ được.

**Cách xử (chủ dự án chốt "sửa gọn ngay trong D3d"):** dưới 1600 thì **xếp dọc**, mỗi khối full
width. **KHÔNG** bóp `min-width` của lịch (bóp = vỡ lưới 7 ngày), **KHÔNG** đổi số đo BA của tiêu đề.
Mốc 1600 lấy từ số đo thật: tại đúng 1600 cột còn 235px và tiêu đề vẫn 1 dòng.

Kèm 2 vá phụ trên cùng trang, mỗi cái đều **đo ra dải áp dụng riêng** chứ không đoán:

- `.wj-exam-pc-tablebox` đang `overflow: hidden` ⇒ cột "Thao tác" **bị cắt cụt**. Cho cuộn ngang
  trong chính hộp, phủ **toàn bộ PC**.
- Bảng `table-layout: fixed` chia 6 cột theo % (tỉ lệ dựng cho hộp 1050px). Đo mép chữ so với mép ô:
  **1920 dư 3px · 1700 dư 1px · 1600 THIẾU 5px** ⇒ dải cần vá là **dưới 1700**, không phải dưới 1600.
  Trả `table-layout: auto` trong đúng dải đó; từ 1700 trở lên giữ nguyên tỉ lệ Figma.

> ⚠️ **Một hướng đã thử và BỎ:** `min-width: 1000px` trên bảng + cuộn ngang. Hỏng hơn — bảng
> **kéo phình cả thẻ cha** từ 723px lên 1002px (đo `.wj-exam-pc-schedule`). Ghi lại để đừng thử lại.

**Nghiệm thu bản vá:** 8 bề rộng **1920 / 1700 / 1650 / 1600 / 1560 / 1520 / 1440 / 1280** — **8/8
đạt**: ≥1600 giữ 2 cột, <1600 xếp dọc, tiêu đề **luôn 1 dòng**, số BA vẫn **18/24/700**, chữ cột
cuối không bị cắt, **0 tràn ngang**. Số đo CardHeader chạy lại: **32/32 ô đạt chuẩn BA**, giả-heading
vẫn đúng 1 (chỗ defer), **243 test 0 failed / 0 error**. Ảnh: `scratchpad/d3d-shots/fix-reg-*.png`.

`wujia_portal_exam` **19.0.5.8.0 → 19.0.5.9.0** ⇒ cần **deploy lượt 2**: `-u wujia_portal_exam`.


---

## 12. Kết quả đo lại trên UAT sau deploy lượt 2 (04/09)

`wujia_portal_exam` **19.0.5.9.0** trên UAT (đối chiếu `ir.module.module` qua XML-RPC chỉ-đọc).

**`scratchpad/d3d_uat_verify.py`: 128/128 header đạt toàn bộ số BA · 0 VẤN ĐỀ.**
22 route × 3 breakpoint (1440/390/360), gồm 13 route regression D3a+D3b+D3c và 9 route exam
(3 màn × PC/mobile + 4 bước wizard). 0 giả-heading ngoài chỗ defer, 0 tràn ngang, 0 JS error,
HTTP 200 toàn bộ. Ảnh: `scratchpad/d3d-uat-shots/`.

> 🔴 **Hai lỗi của chính harness, không phải của sản phẩm** — ghi lại vì đều thuộc loại "báo
> động giả làm che lỗi thật", đúng bài học đã trả giá ở D3a/D3c:
> 1. Danh sách bỏ qua chỗ defer viết theo tên **div bọc** (`wj-exam-pc-parthead`) trong khi
>    heading mang tên `wj-exam-pc-sectitle` ⇒ báo lỗi giả.
> 2. Vòng in báo cáo **tách khỏi** vòng đo, nhưng vẫn đọc biến `real` của vòng đo ⇒ luôn nhận
>    giá trị rơi rớt của lần lặp CUỐI, điều kiện bỏ qua không bao giờ đúng. Phải lấy từ `key`.

**Đã ghi sheet:** `qa_deploy_mark.py UI-CARDHEADER-001 --apply` (dòng 118) — cột P dẫn đầu bằng
cảnh báo **"⚠ MỚI PHỦ 61/103 CALL SITE — issue vẫn Ready for Dev, CHƯA retest toàn issue"**, kèm
phạm vi retest được ngay là **riêng 3 màn Đăng ký thi**. Trạng thái issue **không đổi**
(`Ready for Dev`), **KHÔNG** chạy `qa_sync.py`, ledger vẫn dạng comment.

**Câu hỏi BA cho 3 chỗ defer:** `docs/ba-question-cardheader-trailing.md` (gộp 1 lượt: 1 chỗ treo
từ D3a + 2 chỗ exam của D3d).
