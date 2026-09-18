# ★FR-B — Review toàn khối B (F2 + F3 + F4)

*Phiên 18/09/2026 · Mac · DB `wujia_f0` port 8099 · không commit/push/deploy*

Khối B = 3 phiên chạy liên tiếp trong một ngày (17/09):

| Phiên | Commit | Nội dung |
|---|---|---|
| F2 | `dab6f4c` | dời CSS 8 màn nhỏ ra khỏi `wujia_portal_layout` |
| F3 | `584e3aa` | dời CSS Đặt hàng + Home ra khỏi layout (tổng F2+F3 = 230 rule) |
| F4 | `52c7650` | duyệt 44 rule module viết đè component; viết lại `_interaction.css` theo marker `wj-state-surface` |

**Lý do phải có phiên này:** mỗi phiên F2/F3/F4 tự đo bằng mốc của chính nó (F3 phải lấy mốc mới
vì mốc F0 đã trôi) ⇒ **chưa từng có một phép đo đi suốt F0 → HEAD**. Thêm tiền lệ D3e: mọi số đo
từng lượt đều Pass mà thẻ tóm tắt vẫn vỡ, chỉ ảnh chụp bắt được.

---

## 1. Kết luận

✅ **Khối B đạt.** Đi suốt từ mốc F0 tới `52c7650`, giao diện **không đổi ngoài bảng đã duyệt**
(`docs/f4-override-review.md` §8). Mọi ô lệch đều quy được về dữ liệu/đồng hồ và đã chứng minh
bằng ảnh. 0 lỗi mới.

Sau đó chủ dự án chốt **sửa luôn 2 khoản nợ F4 trong phiên** (mục 6): đầu bảng PC về **14px chuẩn**
và **gỡ hiệu ứng rê chuột ở 40 chỗ bấm không ăn gì**. Kèm 3 việc dọn nhỏ và **3 guard mới** (đã
mutation, không rỗng) khoá lại để lỗi không quay về.

**Số chốt cuối phiên:** suite **543/543** · B4 **286/286** · 8 ô `wj_measure` lệch, **cả 8 là hệ
quả trực tiếp của việc sửa 14px và đã đo A/B chứng minh**.

## 2. Bảng Pass/Fail

Mốc so sánh: `docs/f0-baseline/` (measure_anh.json 26 route · measure_em.json 15 route ·
css_owner.json · check_layers.json · b4.txt) + ảnh `scratchpad/f0-before/shots/{anh,em}/`.

| # | Phép đo | Ngưỡng | Kết quả | Pass |
|---|---|---|---|---|
| 1 | suite 12 module portal | 0 failed / 0 error | **543/543** (540 + 3 guard mới) | ✅ |
| 2 | `b4_regression.py` | 286/286 | **286/286** | ✅ |
| 3 | `wj_measure --diff` anh.owner vs F0 | 0 ô lệch không giải trình | **130/130 ô trùng khít** (0 diff) | ✅ |
| 4 | `wj_measure --diff` em.hcm vs F0 | nt | 4 ô lệch — **cả 4 là dữ liệu/đồng hồ** (§3) | ✅ |
| 5 | `css_owner --layout-domain` | 0 nhóm màn ở layout ngoài danh sách giữ | **20 nhóm, cả 20 trong danh sách giữ** | ✅ |
| 6 | `css_owner --overrides` | 9 rule đổi dáng, cả 9 có comment `F4(c)` | **đúng 9, cả 9 có `F4(c)`** (grep từng chỗ) | ✅ |
| 7 | `check_layers.py` | 1 vi phạm đã biết | **1** (`portal_order_window` thiếu `portal_base`, để F7) | ✅ |
| 8 | hover/active ép trên **mọi** phần tử, 2 tài khoản × 2 khổ | 0 mất / 0 thừa | **82 ô: 0 mất, 0 thừa** | ✅ |
| 9 | ảnh mọi route × 2 khổ (390/1440) | mọi khác biệt quy được về đồng hồ/dữ liệu hoặc bảng F4 §8 | **205 cặp ảnh, xem từng cặp bằng mắt** — xem §4 | ✅ |
| 10 | nguyên tử CSS toàn portal, F2+F3 | dời rule là phép giữ nguyên ⇒ 0 mất / 0 thừa | **121902 → 121902, 0/0** | ✅ |
| 11 | nguyên tử CSS, F4 | delta phải khớp bảng §8 | **149 mất / 42 thừa**, gom theo selector, giải trình đủ | ✅ |
| 12 | mutation 5 guard D4 F3 trỏ lại | 5/5 đỏ | **5/5 đỏ** (nợ F3 đã trả) | ✅ |
| 13 | bump version + `?v=` | 0 sót | **12/12 manifest khớp DB**; mọi file layout sửa đều có `?v=` mới | ✅ |
| 14 | selector đụng nhóm Khảo sát (code anh Thái) | 0 ca ngoài ca đã duyệt | **0** — chỉ 1 ca đã duyệt (tiêu đề PC 700→800) | ✅ |
| 15 | thứ tự nạp CSS | `web.assets_frontend` luôn nạp SAU 4 file `<link>` của layout | **đúng** — đây là giả định cả F2/F3 dựa vào | ✅ |
| 16 | cỡ đầu bảng PC sau khi sửa (a) | mọi bảng = 14px | **16/17** — bảng còn lại là bảng kết quả Thi, vốn 13px từ trước, cố ý | ✅ |
| 17 | marker trên bề mặt không bấm được sau khi sửa (b) | 0 | **0** (2 tài khoản × 2 khổ) · 110 chỗ mất hover đều là `<div>`, 0 chỗ bấm được bị mất | ✅ |
| 18 | mutation 3 guard mới | 3/3 đỏ | **3/3 đỏ**, hoàn tác xanh lại | ✅ |

---

## 3. Bốn ô lệch của em.hcm — chứng minh là dữ liệu/đồng hồ

| Route | Lệch | Nguyên nhân đã chứng minh |
|---|---|---|
| `/portal` | mất 1 thẻ chuyến giao (`BATCH/OUT/00015`) | dữ liệu: chuyến đã rời khung thời gian. **Mọi bề mặt có ở cả hai lượt đều lệch 0px.** |
| `/portal/order` ×3 | −20px chiều cao | đồng hồ: lúc chụp mốc đang **ngoài** khung đặt hàng (banner đỏ 3 dòng), giờ đang **trong** khung (banner xanh 2 dòng). Ảnh `D-khunggio-moc.png` vs `D-khunggio-nay.png`. |

Không ô nào do CSS.

---

## 4. Khác biệt nhìn thấy trên 205 cặp ảnh — đã quy hết về nguyên nhân

- khung giờ đặt hàng đổi banner (đồng hồ)
- chuông thông báo 45 → 44, "Chưa đọc" → "Đã đọc" (dữ liệu, do chính lượt đo trước mở ra)
- Kiến thức lượt xem 0 → 15 (dữ liệu)
- `Product` → `Sản phẩm` (bản dịch nạp thêm)
- ngày báo cáo 09/17 → 09/18 (đồng hồ)
- avatar PNG server sinh lại → khác vài pixel khi nén (không phải CSS)
- các khác biệt thuộc **bảng F4 §8 đã duyệt**: Thi PC đậm nút/ô/crumb, chip Thông báo mobile 11.3,
  giỏ trống 18px, nhãn phụ Đổi trả, tiêu đề Khảo sát PC 800

**0 khác biệt chưa từng được duyệt.**

Ảnh đáng chú ý lưu ở `docs/f-review-B-img/`:

| Ảnh | Nội dung |
|---|---|
| `A-dau-bang-16-vs-14.png` | nợ (a): đầu bảng Giao hàng 16px vs Thi 14px |
| `B-hover-hang-khong-bam-duoc.png` | nợ (b): hàng "Địa chỉ …" sáng lên khi rê chuột dù bấm không ăn gì |
| `C-congno-man-rong.png` | Công nợ ở khổ rộng — đối chiếu mốc |
| `D-khunggio-moc.png` / `D-khunggio-nay.png` | banner khung giờ đặt hàng: mốc (ngoài giờ) vs nay (trong giờ) |

---

## 5. Đã sửa trong phiên (đều <30 dòng, không đổi hành vi)

| # | Việc | Phạm vi | Chứng minh không đổi hành vi |
|---|---|---|---|
| 1 | Sửa số test sai ở nhật ký F4: **537 → 540** | `docs/f-progress.md` | đếm lại: 534 `def test_` ở `584e3aa` + 6 test mới `test_f4_overrides.py` = 540. **Không test nào bị xoá.** |
| 2 | Bỏ số dòng đã lệch trong **12 comment "dời từ"** (giữ nguyên chữ "dời từ portal_layout") | 7 module | comment thuần; số dòng trỏ vào file layout đã đổi nên gây hiểu nhầm |
| 3 | Xoá **2 khối `@media` rỗng + 5 comment mồ côi** | `_components.css` (layout) | 2 khối đã rỗng từ trước khối B |

**Chứng minh tổng cho cả 3 việc:** so nguyên tử CSS (media, selector, thuộc tính, giá trị) của
**282 file CSS portal** giữa `HEAD` và cây làm việc → **121795 → 121795, 0 mất / 0 thừa**.

**Chạy lại toàn bộ sau khi dọn** (đây mới là số chốt của bảng §2): suite **540/540** (0 failed 0 error) ·
B4 **286/286** · `wj_measure` anh.owner **130/130 ô trùng khít** cả với lượt trước-dọn lẫn với **mốc F0** ·
em.hcm 0 ô lệch so với lượt trước-dọn.

Kèm theo: `?v=` `_components.css` 1296 → **1297**, và **7 manifest** bump +1 patch
(layout `19.0.51.0.5`, base `19.0.7.17.4`, notification `19.0.2.14.3`, sale `19.0.4.17.3`,
support `19.0.3.21.4`, purchase_history `19.0.3.12.3`, knowledge `19.0.3.14.3`).

---

## 6. Hai khoản nợ F4 — chủ dự án chốt **SỬA TRONG PHIÊN**

### (a) Cỡ chữ đầu bảng PC → thống nhất **14px** (chuẩn thiết kế)

**Gốc rễ (khác với chẩn đoán của F4):** không phải "Vuexy" mà là một luật quét chung
`table th { font-size: 16px!important }` nằm trong `portal_layout/static/assets/css/style.css`,
**có từ commit đầu tiên của dự án**. Vì là `!important` trên selector theo THẺ, nó thắng mọi
component và mọi khai báo của từng màn.

Kiểm kê bằng máy (17 bảng portal, PC 1440): **14 bảng đang 16px**, 2 bảng màn Thi 14px (tự viết
`!important` đè ngược), 1 bảng Báo cáo 14px.

> ⚠️ Nhật ký F4 ghi "8 màn" — sai. Số đúng là **14/17 bảng**.

**Đã sửa (4 thay đổi):**

| # | Việc | File |
|---|---|---|
| 1 | **Gỡ hẳn** luật quét chung `table th{16px!important}`, thay bằng ghi chú cấm thêm lại | `portal_layout/.../style.css` |
| 2 | Đầu bảng Đặt hàng 13 → 14 (13 là khai báo cũ của module, **chưa bao giờ ăn** vì bị luật chung nuốt) | `portal_sale/.../portal_order.css` |
| 3 | Bảng sản phẩm ở chi tiết Đổi trả là `<table>` thô ⇒ cho class riêng `wj-return-ptable` + khai 14px tại module (không mượn selector của layout) | `portal_return` XML + CSS |
| 4 | **Xoá 4 rule `!important`** của F4(c) ở màn Thi — chúng chỉ tồn tại để chống luật chung; mỗi bảng nay tự ăn cỡ khai ở luật thường (res 13 · part/sum 12) | `portal_exam/.../portal_exam.css` |

**Kết quả đo lại:** **16/17 bảng = 14px**. Bảng còn lại là bảng kết quả thi (`wj-exam-pc-res-table`)
ở 13px — nó **vốn đã 13px từ trước**, không nằm trong 14 bảng bị lỗi, và 13px là khai báo cố ý của
module cho bảng 7 cột. Ảnh: `E-dau-bang-TRUOC-16px.png` vs `E-dau-bang-SAU-14px.png`.

**Tác dụng phụ đo được — bảng ngắn lại thật:** đầu bảng nhỏ đi ⇒ cột giãn lại ⇒ chữ trong ô hết
phải xuống dòng. Chứng minh bằng A/B tiêm lại luật cũ ngay trên trình duyệt:

| Màn (khổ 992) | cao hàng CŨ | cao hàng NAY | cao trang CŨ | cao trang NAY |
|---|---|---|---|---|
| Hỗ trợ | 89px × 20 hàng | **72px** | 2234 | **1894** (−340) |
| Yêu cầu thông tin | 72px × 5 hàng | **55px** (3 hàng) | 1654 | **1603** (−51) |

8 ô `wj_measure` lệch so mốc F0 đều là hệ quả này (trang thấp đi ⇒ số bản ghi lọt màn đầu tăng:
29→31, 32→33, 29→30). Không ô nào do dữ liệu — đo lại 2 lượt ra số y hệt.

### (b) Rê chuột sáng ở bề mặt không bấm được → **đã gỡ marker**

**Luật rút ra từ chính template `wj_surface_card`:** có `sc_href` ⇒ bọc `<a>` ⇒ bấm được, marker
phải đi với `sc_link_class`. Không có `sc_href` ⇒ `<div>` thuần ⇒ **mọi marker đặt ở `sc_class`
đều là hover trên chỗ bấm không ăn gì.**

**Đã gỡ marker ở 40 chỗ** (36 + 4 tìm thêm được, xem dưới): 27 chỗ qua `sc_class` · 13 chỗ gắn
thẳng trên `<div>` (`wujia-mhome-kpi` ô Công nợ hiện "—", `wujia-mdash-row` ở Home / Hỗ trợ /
Thông tin cửa hàng, skeleton Giao hàng). Không đụng một dòng CSS nào.

> ⚠️ Nhật ký F4 ghi "`wujia-mdash-card` ×33" — sai. Con số đúng: **40 chỗ trong XML**;
> `wujia-mhome-kpi` phần lớn là thẻ `<a>` **bấm được** (chỉ 1 trong 4 là `<div>`).

**Đo lại:** 0 phần tử không bấm được còn mang marker (cả 2 tài khoản × 2 khổ) · **110 chỗ mất
hover, 100% là `<div>`, 0 chỗ bấm được bị mất hover, 0 chỗ thừa.**
Ảnh: `F-hover-SAU-khong-sang.png`.

### (c) Trạng thái rỗng màn Công nợ — **không phải lỗi, không sửa**

`584e3aa` có 4 rule riêng cho `.wj-debt-empty`; F4 xoá, để component lo. Chỗ này **vẫn render**
(`portal_debt.xml:140,533`) nên không phải code chết, nhưng mọi phép đo của khối B **mù** vì DB seed
không bao giờ ra trạng thái rỗng. FR-B ép hiện bằng `/portal/debt/payment-history?q=zzzkhongcogi`:

| | Trước (F3) | Sau (F4) | Chuẩn component |
|---|---|---|---|
| icon | 68×68 | **64×64** | 64 ✅ |
| lề dưới icon | 9px | **4px** | 4 ✅ |
| chữ trong icon | 27px | **28px** | 28 ✅ |
| tiêu đề | 19px | **18px** | 18 ✅ |
| chữ phụ | 12.5px | **14px** | 14 ✅ |

⇒ Sau F4 khớp chuẩn component. Chỉ cần BA biết là nó có đổi, để khỏi tưởng lỗi khi retest.

### Ba guard mới khoá lại cả ba điều trên

| Guard | Khoá điều gì | Mutation |
|---|---|---|
| `test_marker_never_on_a_plain_surface_card` | marker không bao giờ nằm ở `sc_class` | **đỏ** khi gắn lại |
| `test_marker_only_on_clickable_tags` | marker chỉ nằm trên `a/button/input/select` | **đỏ** khi gắn lại |
| `test_no_blanket_tag_rule_for_table_headers` | cấm thêm lại luật quét theo thẻ cho đầu bảng | **đỏ** khi thêm lại |

Cả 3 đã chạy mutation từng cái: nguyên trạng xanh → mỗi phép phá làm đúng guard đó đỏ → hoàn tác
xanh lại. **Không guard nào rỗng.**

### Hai lỗi guard bắt được (mà người soi đã bỏ sót)

1. **`/portal/franchise-information` (Thông tin cửa hàng) không có trong danh sách route đo của mốc
   F0** ⇒ 4 chỗ gắn marker sai ở màn này lọt qua cả F4 lẫn vòng soi đầu của FR-B. Guard mới bắt
   được. **Phải bổ sung route này vào danh sách đo trước F5.**
2. Guard `test_screen_surfaces_carry_the_marker` (F4) chốt `wujia-mhome-kpi wj-state-surface` = 4 —
   đúng việc của nó: gỡ 1 chỗ là nó đỏ ngay. Đã sửa 4 → 3 kèm lý do tại chỗ.

## 7. Lệnh chạy lại

```bash
# server đo (DB wujia_f0)
cd ~/odoo-dev/WujiaTea/odoo19 && python odoo-bin -c ../config/odoo.conf -d wujia_f0 \
  --db-filter='^wujia_f0$' --http-port=8099 --gevent-port=8199

# 1. suite 12 module + B4
cd ~/odoo-dev/WujiaTea/odoo19 && python odoo-bin -c ../config/odoo.conf -d wujia_f0 \
  --db-filter='^wujia_f0$' --http-port=8099 --gevent-port=8199 --stop-after-init --test-enable \
  -u wujia_portal_layout,wujia_portal_base,wujia_portal_sale,wujia_portal_debt,wujia_portal_delivery,\
wujia_portal_exam,wujia_portal_knowledge,wujia_portal_notification,wujia_portal_purchase_history,\
wujia_portal_report,wujia_portal_return,wujia_portal_support
python scripts/ba_spec/b4_regression.py --base http://127.0.0.1:8099

# 2. quyền sở hữu CSS + tầng
python scripts/qa/css_owner.py --layout-domain
python scripts/qa/css_owner.py --overrides
python scripts/qa/check_layers.py

# 3. đo hình học + ảnh, so mốc F0  (zsh: PHẢI dùng ${=R} để tách chuỗi route)
R=$(tr '\n' ' ' < docs/f0-baseline/measure_anh.txt)
python scripts/qa/wj_measure.py --base http://127.0.0.1:8099 --login anh.owner \
  --routes ${=R} --widths 1440,1024,992,390,360 --out /tmp/after_anh.json
python scripts/qa/wj_measure.py --diff docs/f0-baseline/measure_anh.json /tmp/after_anh.json
# ảnh: thêm --screenshots --widths 390,1440 ; mốc ở scratchpad/f0-before/shots/{anh,em}/
```

⚠️ **Bẫy đã cắn:** sửa CSS xong phải `DELETE FROM ir_attachment WHERE url LIKE '/web/assets/%'`
rồi restart, nếu không đo trên bundle cũ.

---

## 8. Bài học cho F5 và các khối sau

1. **Trạng thái rỗng / trạng thái hiếm là điểm mù của phép đo.** DB seed không bao giờ ra trạng
   thái rỗng ⇒ mọi rule của nó đi qua mọi phép đo mà không ai thấy (mục 6c). Từ F5: mỗi màn phải
   có **1 route ép ra trạng thái rỗng** trong danh sách đo (`?q=<chuỗi vô nghĩa>`).
2. **Không tin con số chép tay trong nhật ký.** Phiên này bắt 3 con số sai của F4 (537 test, "8 màn"
   bảng PC, "×33" chỗ hover). Con số nào vào doc cũng phải đếm lại bằng máy.
3. **Guard đọc thẳng CSS phải có mutation test kèm.** F3 trỏ lại 5 guard D4 sang file module nhưng
   không chứng minh chúng còn đỏ khi phá; FR-B mới làm (5/5 đỏ). Từ F5: phiên nào đổi đường dẫn
   guard thì **cùng phiên** phải chạy mutation.
4. **So nguyên tử CSS là phép kiểm rẻ và mạnh nhất cho việc dời file.** Dời rule = phép giữ nguyên
   ⇒ tổng nguyên tử phải bằng nhau tuyệt đối. Nên chạy mặc định ở mọi phiên dời CSS.
5. **Ảnh vẫn bắt được cái số không bắt được** (bài học D3e vẫn đúng): 4 ô lệch của em.hcm chỉ chứng
   minh được là đồng hồ khi nhìn banner khung giờ trong ảnh.
6. **zsh không tách chuỗi khi không ngoặc** — `--routes $R` thành 1 route dài 500 ký tự. Dùng `${=R}`.
7. **Guard bắt được cái mắt người bỏ sót.** Vòng soi tay của FR-B đếm 21 chỗ hover sai; guard mới
   quét toàn bộ `wujia_portal_*` ra **40 chỗ**, trong đó có nguyên một màn (`/portal/franchise-
   information`) **không nằm trong danh sách route đo của mốc F0**. ⇒ Trước F5 phải rà lại danh
   sách route: mọi `@http.route` của portal phải có mặt, không chỉ những màn hay dùng.
8. **Sửa CSS bằng script Python có thể âm thầm đổi kiểu xuống dòng.** `style.css` dùng CRLF; đọc
   ghi bằng Python mặc định biến 274 dòng thành LF, diff phình từ 5 lên 550 dòng. Luôn mở với
   `newline=''` và kiểm `git diff --stat` sau mỗi lần sửa bằng script.
9. **Một luật quét theo THẺ có `!important` là mìn hẹn giờ.** `table th{16px!important}` tồn tại từ
   commit đầu, làm 14 bảng sai cỡ suốt nhiều sprint, và khiến 3 module viết thêm `!important` để
   chống lại nó. Gỡ 1 luật gốc xoá được 4 rule đối phó. ⇒ Cấm luật quét theo thẻ trong CSS layout
   (đã có guard).

