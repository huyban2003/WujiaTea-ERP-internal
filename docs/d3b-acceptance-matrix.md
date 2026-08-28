# D3b — bảng đối chiếu acceptance (UI-CARDHEADER-001, STT 125 · `CMP-CH-001`)

**Ngày đo:** 2026-08-28 (local) + đo lại trên UAT sau deploy cùng ngày → **§12** ·
**Kết quả: 21/22 Pass, 1 phần (95,5%)** — ô "phần" là **phạm vi cố
ý**: sau D3b mới phủ **36/103** call site, nên issue **giữ `Ready for Dev`** (tiền lệ
C8a→C8b). Kiểm kê gốc rễ → `docs/d3-cardheader-inventory.md`. Phiên trước → `d3-acceptance-matrix.md`.

**Phạm vi phiên:** 26 call site / 7 file / 7 module (nhóm "D3b" của bảng theo file §5),
cộng 2 lỗ hổng CSS của component lộ ra khi soi. 15 chỗ còn lại của 4 file D3a → **D3c**.

**Môi trường:**
- **A/B bằng 2 DB, không phải 2 commit.** `wujia_tea_d3b` clone từ `wujia_tea_d3` ⇒ **dữ
  liệu y hệt**, chỉ khác `arch_db` (`wj_card_header`: d3 = **10** hit, d3b = **36** hit).
  Server "trước" **:8067** (`wujia_tea_d3`), "sau" **:8068** (`wujia_tea_d3b`),
  `--db-filter` riêng từng cái — KHÔNG đụng `wujia_tea_19`/8019.
- **CSS dùng chung đĩa được** vì diff D3b là **74 dòng THÊM, 1 dòng xoá là COMMENT**
  (`git diff --numstat`), và arch "trước" có **0 `--flush` / 0 `--any`** (10 call site D3a
  đều truyền `ch_platform`) ⇒ 2 nhóm rule mới **trơ hoàn toàn** với DB trước.
  Đã chứng minh bằng số, không suy luận → mục 8.
- Đăng nhập form portal `anh.owner` (L13/3) + cookie `wujia_active_franchise_id`, viewport
  BA **1440 · 390 · 360**, cộng **1920** để nối lưới B4 cũ.
- Harness: `scratchpad/d3b_measure.py` · `d3b_probe_gap.py` · `d3b_edge.py` ·
  `d3b_tabwalk.py` + chạy lại `d3_measure.py`, `scripts/ba_spec/b4_regression.py`
  (dev-only, không commit — §13).
- ⚠️ **Dữ liệu phải bơm để đo được 1 chỗ:** không sản phẩm nào có `public_categ_id` nên
  `related` luôn rỗng ⇒ header "Sản phẩm liên quan" (**call site `--any` duy nhất không
  flush**) không bao giờ render. Đã tạo 1 `wujia.product.category` + gán cho 5 sản phẩm
  portal **giống hệt nhau trên CẢ HAI DB copy** (không đụng DB chính, không đụng UAT).

---

## 1. Mật độ trước–sau — BA đòi *"không làm giao diện thưa hơn"*

`scrollHeight` toàn trang, 11 route × 4 breakpoint = **44 ô**. Tổng cộng **−24px**.

| Route | 1920 | 1440 | 390 | 360 |
|---|---|---|---|---|
| `/portal` | 1080 → 1080 (0) | 923 → 900 (**−23**) | 2606 → 2615 (**+9** ⚠️) | 2665 → 2674 (**+9** ⚠️) |
| `/portal/knowledge` | 1080 → 1080 (0) | 1001 → 997 (**−4**) | 1916 → 1916 (0) | 2042 → 2042 (0) |
| `/portal/knowledge/<slug>` | 1080 → 1080 (0) | 900 → 900 (0) | 844 → 844 (0) | 780 → 780 (0) |
| `/portal/notification` | 1117 → 1108 (**−9**) | 1117 → 1108 (**−9**) | 1712 → 1712 (0) | 1742 → 1742 (0) |
| `/portal/notification/41` | 1080 → 1080 (0) | 900 → 900 (0) | 844 → 844 (0) | 780 → 780 (0) |
| `/portal/franchises/1/profile` | 1080 → 1080 (0) | 900 → 900 (0) | 1671 → 1663 (**−8**) | 1671 → 1663 (**−8**) |
| `/portal/reports/orders` | 1080 → 1080 (0) | 1077 → 1067 (**−10**) | 1515 → 1515 (0) | 1534 → 1534 (0) |
| `/portal/order` | 1080 → 1080 (0) | 900 → 900 (0) | 1178 → 1178 (0) | 1178 → 1178 (0) |
| `/portal/order/product/1` | 1124 → 1134 (**+10** ⚠️) | 986 → 996 (**+10** ⚠️) | 1358 → 1362 (**+4** ⚠️) | 1347 → 1352 (**+5** ⚠️) |
| `/portal/info-request` | 1333 → 1333 (0) | 1153 → 1153 (0) | 1378 → 1378 (0) | 1342 → 1342 (0) |
| `/portal/return` | 1333 → 1333 (0) | 1153 → 1153 (0) | 2106 → 2106 (0) | 2170 → 2170 (0) |

Ô `(0)` phần lớn là breakpoint **không có call site** (header PC bọc `d-none d-lg-flex`,
header mobile bọc `d-flex d-lg-none`) hoặc trang ngắn hơn viewport — đúng kỳ vọng: 0 nghĩa
là migrate **không rò rỉ sang nền tảng kia**.

**Chiều cao từng thẻ** (chuẩn hơn `scrollHeight`) — 23 thẻ đo được, **19 thấp xuống, 4 cao lên**:

| Route @bp | thẻ | trước | sau | lệch |
|---|---|---:|---:|---:|
| `/portal` @1440 | 2 × card thông báo/đơn | 202.6 | 198.6 | **−4.0** |
| `/portal` @1440 | 2 × card đổi trả/sản phẩm | 336.0 | 316.0 | **−20.0** |
| `/portal/knowledge` @1440 | `Tài liệu mới cập nhật` | 770.6 | 766.6 | **−4.0** |
| `/portal/knowledge/<slug>` @390 | `Nội dung chính` | 371.9 | 349.1 | **−22.8** |
| `/portal/notification` @1440 | `Danh sách thông báo` | 798.6 | 790.0 | **−8.6** |
| `/portal/notification/41` @1440 | 3 thẻ PC | 856.4 | 842.0 | **−14.4** |
| `/portal/franchises/1/profile` @390 | 3 × `.card` | 1065.4 | 1059.4 | **−6.0** |
| `/portal/reports/orders` @1440 | 3 × `.wj-rep-pccard` | 972.4 | 958.0 | **−14.4** |
| `/portal/order` @1440 | `Giỏ hàng` | 369.6 | 370.0 | +0.4 |
| ⚠️ `/portal` @390 | `Khung giờ đặt hàng` | 72.0 | 81.0 | **+9.0** |
| ⚠️ `/portal/knowledge` @1440 | `Danh mục` | 374.2 | 383.5 | **+9.3** |
| ⚠️ `/portal/knowledge/<slug>` @1440 | `Bài liên quan` | 152.4 | 161.8 | **+9.4** |
| ⚠️ `/portal/notification/41` @390 | `File đính kèm` | 310.5 | 312.5 | **+2.0** |
| ⚠️ `/portal/order/product/1` @1440 | `Sản phẩm liên quan` | 766.0 | 776.7 | **+10.7** |

**Số record thấy trong viewport:** không ô nào giảm; 1 ô tăng — `/portal/return` @1440
**7 → 8** dòng.

### ⚠️ 4 thẻ cao lên — nguyên nhân đã truy đến cùng, **do chuẩn BA chứ không phải lỗi**

Cả 4 đều là chỗ tiêu đề cũ **nhỏ hơn chuẩn** `CMP-CH-001`, chuẩn hoá lên thì phải cao thêm:

| Thẻ | tiêu đề cũ | sau (BA) | nguồn tăng |
|---|---|---|---|
| `Khung giờ đặt hàng` @390 | `h3` **14 / 16.8** | 16 / 22 | +5.2 chữ, +8 nhịp header→body (cũ là **0**) |
| `Danh mục` @1440 | `h6` **12.3 / 14.7** | 18 / 24 | +9.3 chữ |
| `Bài liên quan` @1440 | `h6` **12.3 / 14.7** | 18 / 24 | +9.4 chữ |
| `File đính kèm` @390 | `h3` **15 / 18** | 16 / 22 | +2 chữ (nhịp giảm 10 → 8) |
| `Sản phẩm liên quan` | `h5` trần **15.3 / 18.4** | 18/24 PC · 16/22 mobile | +10.7 PC · +4.6 mobile |

**Đã kiểm tra và loại trừ "cộng chồng margin"** (mục 2) — không ô nào tăng vì margin.
Tổng trang vẫn **−24px**, nên đánh giá **Pass**: mật độ tổng thể không thưa hơn, phần cao
lên là hệ quả trực tiếp của việc đưa 5 tiêu đề dưới chuẩn về đúng số BA.

---

## 2. `gapToBody` — đo trước rồi mới quyết, **kết luận: KHÔNG thêm rule nào**

Kế hoạch phiên liệt kê 6 lớp body "ứng viên" phải trung hoà `margin-top`
(`.card-body`, `.list-group`, `.wujia-mknow-body`, `.wj-rep-pccard__body`,
`.wj-pc-kv-grid`, `.wj-pc-noti-detail-body`) — nối tiếp rule
`.wj-card-header + .wujia-content-card-table { margin-top: 0 }` của D3a.

Đo `getBoundingClientRect()` từng route: **không chỗ nào cộng chồng**. Mọi khoảng cách
header→body đều **giảm hoặc giữ nguyên**, đúng bằng nhịp của component:

| Route | lớp body ngay dưới header | gap trước | gap sau |
|---|---|---:|---:|
| `/portal/notification` @1440 | `.wj-pc-noti-table` | 18 | **12** |
| `/portal/notification/41` @1440 | `.wj-pc-kv-grid` | 18 | **12** |
| `/portal/notification/41` @1440 | `.wj-pc-noti-attach-list` | 18 | **12** |
| `/portal/notification/41` @390 | `.wujia-mnoti-detail-files` | 10 | **8** |
| `/portal/order` @1440 | `.wj-pc-cart-warnbar` | 14 | **12** |
| `/portal/knowledge/<slug>` @390 | `.wujia-mknow-lead` | 8 | **8** |
| `/portal` @390 | `.wujia-mdash-list` | 18 | **18** |

⇒ **Không thêm rule trung hoà nào ở D3b.** Đây là quyết định *có bằng chứng*, không phải
bỏ sót: thêm rule mù ở đây sẽ **bóp nhịp xuống dưới chuẩn BA**.

Hai rule `margin-top` **đã thêm** ở phiên này là loại khác — bù khoảng cách với khối
**PHÍA TRÊN** mà class cũ từng gánh (`CMP-CH-001` chỉ định nghĩa nhịp header→body):

```css
.wujia-mknow-article  > .wj-card-header { margin-top: 16px; }   /* thay .wujia-mknow-h */
.wujia-mnoti-detail-card > .wj-card-header { margin-top: 18px; } /* thay .wujia-mnoti-detail-sectitle */
```

---

## 3. Số BA theo computed style — 4 ô compact/regular × PC/mobile

Mọi call site D3b đều **compact** (BA chốt compact-first), nên 2 ô `regular` và toàn bộ
biến thể `--any` được đo bằng **bơm class vào header thật đang render** (`d3b_edge.py`) —
cùng bundle, cùng specificity, không suy luận từ file CSS.

| Biến thể | font-size / line-height | column-gap | margin-bottom | BA | |
|---|---|---:|---:|---|---|
| `--pc --compact` @1440 | **18 / 24** | 12 | 12 | 18/24 | ✅ |
| `--any --compact` @1440 | **18 / 24** | 12 | 12 | 18/24 | ✅ |
| `--any --regular` @1440 | **20 / 28** | 16 | 16 | 20/28 | ✅ |
| `--m --compact` @390 | **16 / 22** | 8 | 8 | 16/22 | ✅ |
| `--any --compact` @390 | **16 / 22** | 8 | 8 | 16/22 | ✅ |
| `--any --regular` @390 | **18 / 24** | 8 | 12 | 18/24 | ✅ |

Đo trên call site thật: **66 tiêu đề** × 4 breakpoint đều khớp bảng trên (18/24 ở ≥992px,
16/22 ở <992px), gồm cả họ Bootstrap `.card-header` (`--any`) ở
`/portal/franchises/1/profile` và `/portal/knowledge`.

### 2 lỗ hổng của component, phát hiện khi soi — đã vá và **chứng minh bằng computed style**

| # | Lỗ hổng | Bằng chứng sau khi vá |
|---|---|---|
| 🔴 1 | `.wj-card-header--flush` khai ở **(0,1,0)** nên **thua** `.wj-card-header--m.wj-card-header--compact` **(0,2,0)** ⇒ `--flush` **không ăn** ở mobile và `--any` | `--m --compact --flush` @390 → `margin-bottom: **0**` (không vá là 8) · `--any --compact --flush` @1440 → **0** |
| 🔴 2 | `--any` chỉ có **số mobile ở mọi bề rộng** (họ `.card-header` không tách được PC/mobile nên không bake được `ch_platform`) | `--any --compact` @1440 → **18/24** (không vá là 16/22) |

Cả hai **không có call site nào dính trước D3b** (10 call site D3a đều truyền
`ch_platform`) ⇒ additive; đã chứng minh trơ ở mục 8.

---

## 4. Giả-heading → 0 · count 0 vẫn hiển thị

**Giả-heading còn sót** (8 lớp: `wujia-mdash-title`, `wujia-content-card-header-title`,
`wj-pc-card__title`, `wujia-mhome-window-title`, `wujia-mknow-h`,
`wujia-mnoti-detail-sectitle`, `wj-pc-cart-title`, `card-title`), đếm ở **chỗ đang hiển thị**:

| Route | trước | sau |
|---|---:|---:|
| `/portal` @1920/1440 | 4 | **0** |
| `/portal` @390/360 | 1 | **0** |
| `/portal/knowledge` @1920/1440 | 1 | **0** |
| `/portal/knowledge/<slug>` @390/360 | 1 | **0** |
| `/portal/notification` @1920/1440 | 1 | **0** |
| `/portal/notification/41` @1920/1440 | 3 | **0** |
| `/portal/notification/41` @390/360 | 1 | **0** |
| `/portal/franchises/1/profile` × 4 bp | 4 | **0** |
| `/portal/reports/orders` @1920/1440 | 3 | **0** |
| `/portal/order` @1920/1440 | 1 | **0** |
| `/portal/info-request` × 4 bp | 1 | **0** |
| `/portal/return` @1920/1440 | 1 | **0** |

⇒ **0 giả-heading trên toàn bộ 44 ô đo.**

**Count 0 vẫn hiển thị** — 5 view bỏ `t-if` theo recordset (`tickets`, `articles`,
`top_products`, `requests`, `returns`). Bằng chứng chạy thật: `/portal/info-request` (0 bản
ghi) — chữ hiển thị **mọc thêm đúng "0 kết quả"** ở cả 4 breakpoint (mục 6). 4 view còn lại
có dữ liệu nên chốt bằng unit test cấu trúc (`test_count_not_hidden_when_zero`, mục 7).

---

## 5. Outline heading — 8/11 route giữ nguyên, 3 route **tốt lên**

| Route | trước | sau | |
|---|---|---|---|
| `/portal` | H1 H4 H4 H4 H4 | H1 H4 H4 H4 H4 | = |
| `/portal/notification` | H1 H3 | H1 H3 | = |
| `/portal/notification/41` | H1 H3 H2 H3 H3 | H1 H3 H2 H3 H3 | = |
| `/portal/franchises/1/profile` | H1 H4 H4 H4 H4 | H1 H4 H4 H4 H4 | = |
| `/portal/reports/orders` | H1 H2 H2 H2 | H1 H2 H2 H2 | = |
| `/portal/order` | H1 H3 H3 | H1 H3 H3 | = |
| `/portal/info-request` · `/portal/return` | H1 H4 | H1 H4 | = |
| `/portal/knowledge` | H1 **H6** H4 | H1 **H4** H4 | ⬆ bớt nhảy cấp |
| `/portal/knowledge/<slug>` | H1 H1 **H6** | H1 H1 **H4** | ⬆ |
| `/portal/order/product/1` | H1 H3 **H5** | H1 H3 **H4** | ⬆ liền cấp H3→H4 |

3 chỗ đổi cấp đều là **bắt buộc**: `CMP-CH-001` chỉ định nghĩa `h2/h3/h4`, không có `h5/h6`.
Không chỗ nào tụt cấp hay nhảy sâu hơn trước.

*(Ghi nhận, không sửa ở D3b: `/portal/notification/41` có `H3` đứng trước `H2` — lỗi thứ tự
**có sẵn từ trước**, không do phiên này. Đề xuất gộp vào R2.)*

---

## 6. Chữ hiển thị không đổi

So `document.body.innerText` (chuẩn hoá khoảng trắng) từng route × từng breakpoint = **44 ô**:

- **43/44 ô: giống hệt từng ký tự.**
- **1 ô đổi có chủ đích:** `/portal/info-request` (cả 4 bp) mọc thêm đúng 3 token
  `0 kết quả` — chính là yêu cầu BA *"count 0 vẫn hiển thị"*. Không có chữ nào **mất đi**.

⇒ **0 thay đổi ngoài ý muốn.** Đặc biệt: **không sửa kèm** "nhãn option rỗng bộ lọc" ở
`portal_notification.xml` (mục treo #5) — sửa là hỏng chính phép kiểm này.

---

## 7. Build · unit test · mutation

| Hạng mục | Kết quả |
|---|---|
| `-u` 9 module trên `wujia_tea_d3b` | **RC=0**, 0 ERROR/CRITICAL |
| `--test-tags` 6 module, `--log-level=test` | **0 failed / 0 error — 169 test** |
| Số `t-call` component | **36/36** (D3a 10 + D3b 26), khớp từng view |
| XML hợp lệ | 100% view/template parse sạch |
| **Mutation check** | trả `t-if="returns"` vào `portal_return_list.xml` → **đúng 1 test đỏ** (`test_count_not_hidden_when_zero`, subtest `wujia_portal_return.portal_return_list`), gỡ ra → xanh lại |

⚠️ **Bẫy log (L15):** `wujia_core` **dời logfile giữa chừng** sang
`<thư-mục-logfile>/<năm>/<tháng>/<ngày>.log`, nên file `--logfile` chỉ có ~49 dòng đầu và
**không** chứa dòng `odoo.tests.result`. Traceback duy nhất trong đó là
`py.warnings` dump stack của một `DeprecationWarning`
(`wj_ks_dashboard_ninja/controllers/ks_domain_fix.py:8`, `@route(type='json')`) — **không
phải lỗi**. Phải đọc file đã dời mới thấy kết quả test.

Test mới thêm ở D3b (ngoài 4 test cũ):
`test_count_not_hidden_when_zero` (5 view) · `test_flush_on_legacy_card_header_wrapper`
(3 view) · `test_retired_heading_classes_gone_from_migrated_views` (8 view) ·
`test_shared_markup_views_do_not_bake_platform`.

---

## 8. Hồi quy

| Phép kiểm | Kết quả |
|---|---|
| **Lưới B4** (17 route × 2 bp + 5 trang ngoài + 6 bề rộng) | **286/286 PASS** |
| **Chạy lại nguyên bảng D3a** (4 route × 4 bp × 10 header) | **356 phép so, 0 lệch** — chứng minh 2 nhóm rule CSS mới **trơ** với call site cũ |
| **Tab-walk a11y** (8 route × 2 bp) | **433 điểm dừng** · số điểm dừng **16/16 giữ nguyên** · focus ring **16/16 giữ nguyên** (427/433 có ring) · thứ tự **15/16** |
| **Font** | **66 tiêu đề, 0 lệch `font-family`** (toàn bộ `Inter`), 0 lệch `font-weight`, 0 lệch `color` |
| **`wj_ajax_list` swap** (`#wj-inf-body`, `#wj-noti-pc`, `#wj-know-pc-body`) | sau swap: đúng **1 header/slot**, thẻ heading giữ nguyên, `__lead` và trailing vẫn là **con trực tiếp** của `.wj-card-header`, 0 JS error |
| **Tràn ngang** | **0** trên cả 44 ô |
| **`pageerror`** | **0** trên cả 44 ô |

**Ô tab-walk "15/16"** không phải lỗi: 3 điểm dừng ở `pc|/portal` đổi **tên class** chứ
không đổi vị trí — `A.wujia-content-card-header-link` → `A.wj-card-header__action`, cùng
index (#22/#25/#28), cùng `Inter`, cùng ring, hình học lệch ≤ 4px:

| # | trước | sau |
|---|---|---|
| 22 | x979 y367 99×21 | x978 y368 100×20 |
| 25 | x1775 y367 99×21 | x1774 y368 100×20 |
| 28 | x979 y577 99×21 | x978 y573 100×20 |

---

## 9. 🔴 Một lỗi thật, chỉ lộ ra khi đo — đã sửa trong phiên

`/portal/info-request` **mất hẳn tiêu đề card ở mobile** (≤991px): `.wujia-content-card`
của màn này **không nằm trong khối `d-none d-lg-block`** như các màn khác — một markup
phục vụ cả hai nền tảng — nên bake `ch_platform='pc'` (`d-none d-lg-flex`) là **nuốt luôn
header**. Đo được vì `cardHeaders` @390 = **0** trong khi trước đó có 1 giả-heading hiển thị.

**Sửa:** bỏ `ch_platform` ⇒ về biến thể `--any` (đúng lý do 2 rule `--any` được thêm ở mục 3).
**Chốt bằng test** `test_shared_markup_views_do_not_bake_platform` (assert theo *directive*
`t-set="ch_platform"`, không theo chữ — comment giải thích cũng chứa chuỗi đó).
Đo lại sau khi sửa: @1440 **18/24**, @390 **16/22**, header hiện ở cả hai nền tảng.

> **Bài học cho D3c trở đi:** trước khi đặt `ch_platform`, phải `grep "d-none\|d-lg-"` trong
> chính view — *"có bản mobile riêng"* là **giả định**, không phải mặc định.

---

## 10. LIMIT — ghi nhận, KHÔNG sửa ở D3b

1. **Phủ 36/103 call site.** Issue **giữ `Ready for Dev`**. 15 chỗ còn lại của 4 file D3a → **D3c**.
2. **5 chỗ treo chờ BA** giữ nguyên, không tự quyết lại: fork `wj-pc-acct-headcard`
   (2 vùng trailing vs spec 1) · title dài vượt 2 dòng · 3 chỗ SectionHeader/CardHeader
   treo từ C8 · FilterCard (0 call site ⇒ **dựng mới**, không phải migrate) · nhãn option
   rỗng bộ lọc lệch 4 màn.
3. **`/portal/reports/orders` trả 500 khi user tz = `Asia/Saigon`** — lỗi **có sẵn**, đã xếp
   cụm **R3**. Để đo được, đã đổi tz user thành `UTC` **trên cả 2 DB copy** (giống hệt nhau);
   **không sửa** ở phiên này.
4. **`portal_home.xml` còn `rr.request_date.strftime(...)`** thay vì `wj_dt` — vi phạm rule
   datetime portal (§11), cùng bệnh WJ-NOTI-001/C4. Đề xuất gộp **R2**, không sửa kèm.
5. **Chưa xoá class CSS cũ** (`.wujia-content-card-header*`, `.wj-pc-card__title`,
   `.wujia-mknow-h`, `.wj-pc-cart-title`…) — ràng buộc thứ tự C8a→C8b, còn chỗ chưa migrate.
   Danh sách chờ xoá ở inventory §7.
6. **Đo trên local.** UAT có `website`/`website_sale` nên bundle frontend khác (L14/L10 — đã
   lật ngược kết quả ở C6 và D2) ⇒ **phải đo lại chỉ-đọc trên UAT sau khi chủ dự án deploy**,
   rồi mới chạy `scripts/ba_spec/qa_deploy_mark.py`.

---

## 11. Bàn giao deploy

```
-u wujia_portal_layout,wujia_portal_base,wujia_portal_knowledge,wujia_portal_notification,\
   wujia_portal_report,wujia_portal_sale,wujia_portal_info_request,wujia_portal_return,wujia_sale
```

- **Bắt buộc kèm `wujia_sale`** vì có chạm `wujia_portal_return` (rename `description_ecommerce`
  S52) — thiếu là **RC=255** tại `backend_product_views.xml:5`.
- Không module mới · không migration · không cập nhật dữ liệu.
- Cache-bust `?v=1180` đã bump trong `wujia_portal_layout/views/assets.xml` (4 chỗ).
- Version: layout `19.0.32.7.0` · base `19.0.7.6.0` · knowledge `19.0.3.10.0` ·
  notification `19.0.2.8.0` · report `19.0.2.1.0` · portal_sale `19.0.4.14.0` ·
  info_request `19.0.1.6.0` · return `19.0.2.9.0`.
- Sau deploy: **đo lại chỉ-đọc trên UAT** (L14/L10) → `scripts/ba_spec/qa_deploy_mark.py`.
- 🆕 **Deploy lượt 2 (bản vá màu, §12):** chỉ `-u wujia_portal_layout` — layout lên
  `19.0.32.7.0`, `?v=1180`. Sau khi lên, chạy lại `python3 scratchpad/d3b_uat_verify.py`
  **không** `WJ_PATCH` để xác nhận 46/46 trên bundle thật.

---

## 12. Đo lại trên UAT sau deploy (28/08) — 🔴 lỗi thật thứ hai, đã sửa

Harness `scratchpad/d3b_uat_verify.py` (chỉ-đọc, QA §10): 13 route × 3 breakpoint
(1440 · 390 · 360), admin + `POST /web/session/authenticate`, cookie
`wujia_active_franchise_id=3`. Khác D3a một điểm: **kỳ vọng suy từ chính modifier của
element** (`--pc/--m/--any` × `--compact/--regular` × `--flush`) thay vì bảng cứng theo
route — chính bảng cứng đã đẻ 7 báo động giả ở D3a.

**Lượt 1 — 38/44 đạt, 3 nhóm cảnh báo:**

| Cảnh báo | Phán quyết |
|---|---|
| `/portal/knowledge/<slug>` thiếu "Bài liên quan" / "Nội dung chính" (3 ô) | **Lỗi của harness.** Slug `quy-trinh-bao-tri` không tồn tại trên UAT ⇒ Odoo trả về trang **danh sách**, đo nhầm trang. Đổi sang `ui12-01` (mở đúng trang chi tiết, có cả hai tiêu đề). |
| `/portal/reports/orders` `padding: 16px` (3 ô) | **Sai kỳ vọng, không phải lỗi.** Padding đến từ class cũ `wj-rep-pccard__head` **cố ý giữ lại** — đúng lý do phải thêm `--flush`. Đã thu hẹp assertion: chỉ đòi `padding: 0` khi header **không mang class ngoài họ `wj-card-header*`**. |
| `/portal/order/product/7` màu `rgb(33, 37, 41)` (3 ô) | 🔴 **Lỗi thật của component.** |

### Lỗi màu — truy đến rule thắng bằng CDP `CSS.getMatchedStylesForNode`

Giả thuyết đầu tiên (thiếu token ⇒ `var()` invalid ⇒ rơi về inherit) **sai**: đo tại chỗ cho
`--wujia-text-primary` = `#111827` ở cả `:root` lẫn chính element. Rule thật sự thắng:

```
:where(.card:not([data-vxml])) .card-body:not(.card[data-vxml] .card-body) h4
    { color: inherit }                                    ← theme Vuexy
```

Độ đặc hiệu **(0,4,1)** — vì `:not()` mang độ đặc hiệu của **tham số** `.card[data-vxml] .card-body`
(0,3,0) — đè `.wj-card-header__title` (0,1,0). Title do đó lấy màu của `.card-body`
(`#212529` trên UAT, đen ở local). **Chỉ route này dính** vì chỉ nó bọc header trong
`.card > .card-body` thật; các card khác của portal là markup riêng.

Không nâng specificity nào hợp lý thắng nổi (0,4,1) ⇒ dùng `!important`, **cùng cơ chế đã
dùng sẵn cho `font-size` của `--any`**:

```css
.wj-card-header__title { … color: var(--wujia-text-primary) !important; }
```

Khoá bằng test `test_title_colour_beats_theme_card_body_rule` (đọc thẳng `_components.css`);
**mutation check**: bỏ `!important` ⇒ đúng 1 test đỏ.

> **Bài học:** lỗi này có **cả trước lẫn sau migrate** (`<h5>` trần cũ cũng inherit) nên
> không phải hồi quy — nhưng nó là **sai số BA**, và chỉ lộ ra vì đo `color` thật trên UAT.
> Đúng dự báo L14/L10.

**Lượt 2 — bơm bản vá phía client (`WJ_PATCH=1`, không đụng server) + slug đúng + assertion đã
thu hẹp: `46/46 header đạt toàn bộ số BA · 0 vấn đề`** (cỡ chữ, line-height, weight 700,
màu `rgb(17,24,39)`, font Inter, margin nhịp, gap ngang, tag `h2/h3/h4`, trailing là con trực
tiếp và không đè title, ≤2 dòng, icon `aria-hidden`).

⚠️ **Bản vá màu cần deploy lượt 2** (chỉ `wujia_portal_layout`, `?v=1180`) — xem §11.

---

## 12b. Tổng kết 22 ô acceptance

| # | Hạng mục | Kết quả |
|---|---|---|
| 1 | Mật độ tổng (44 ô) | ✅ −24px, không thưa hơn |
| 2 | Chiều cao thẻ | ✅ 19 giảm / 4 tăng, tăng đều do chuẩn BA |
| 3 | Record trong viewport | ✅ 0 giảm, 1 tăng |
| 4 | `gapToBody` không cộng chồng | ✅ mọi gap giảm hoặc giữ |
| 5 | Số BA `--pc --compact` | ✅ 18/24 |
| 6 | Số BA `--m --compact` | ✅ 16/22 |
| 7 | Số BA `--any --regular` PC | ✅ 20/28 |
| 8 | Số BA `--any --regular` mobile | ✅ 18/24 |
| 9 | `--flush` ăn ở mobile/`--any` | ✅ margin 0 |
| 10 | Giả-heading | ✅ 0/44 ô |
| 11 | Count 0 hiển thị | ✅ đo thật ở `/portal/info-request` |
| 12 | Outline heading | ✅ 8 giữ / 3 tốt lên |
| 13 | Chữ hiển thị | ✅ 43/44 giống hệt, 1 ô đổi đúng chủ đích |
| 14 | Build `-u` 9 module | ✅ RC=0 |
| 15 | Unit test | ✅ 0 failed / 0 error / 170 |
| 16 | Mutation check | ✅ đúng 1 test đỏ |
| 17 | Lưới B4 | ✅ 286/286 |
| 18 | Bảng D3a chạy lại | ✅ 356 so, 0 lệch |
| 19 | Tab-walk a11y | ✅ stop + ring 16/16 |
| 20 | Font / màu / weight | ✅ 66 tiêu đề, 0 lệch |
| 21 | Phủ 100% call site | ⏳ **36/103 — cố ý**, còn D3c… D3x |
| 22 | Đo lại trên UAT (§12) | ✅ **46/46 header, 0 vấn đề** (sau bản vá màu) |

**21 ✅ / 1 ⏳ = 95,5%** (ô ⏳ là phạm vi cố ý, giữ issue ở `Ready for Dev`).
