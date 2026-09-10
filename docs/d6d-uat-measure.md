# D6d — đo lại chỉ-đọc trên UAT sau deploy

**Ngày:** 2026-09-10 · **Máy chủ:** `http://113.161.187.126:8019` · **DB:** `wujia_tea_19`
**Phạm vi:** chỉ đọc (QA §10) — không tạo đơn, không hoá đơn, không email, không seed.

---

## 1. Bước mở đầu — deploy đã ăn thật (hai bằng chứng độc lập)

Bốn lượt liên tiếp (D3c · D4f · D5h.2 · D6) đã trả giá vì tin "đã chạy lệnh rồi", nên đây là
điều kiện tiên quyết, làm trước khi đo bất cứ thứ gì.

### (a) XML-RPC `ir.module.module`

| Module | Cần | UAT | `write_date` (UTC) |
|---|---|---|---|
| `wujia_portal_layout` | 19.0.47.0.0 | **19.0.47.0.0** ✅ | 2026-09-10 16:24:00 |
| `wujia_portal_return` | 19.0.3.1.0 | **19.0.3.1.0** ✅ | 2026-09-10 16:24:08 |
| `wujia_portal_support` | 19.0.3.18.0 | **19.0.3.18.0** ✅ | 2026-09-10 16:24:08 |
| `wujia_portal_info_request` | 19.0.1.8.0 | **19.0.1.8.0** ✅ | 2026-09-10 16:24:06 |

So **cả hai chiều**, không chỉ số phiên bản: `write_date` 16:24 UTC = **23:24 giờ VN**, muộn hơn
commit D6c `c202734` (22:38 VN) **46 phút** ⇒ loại được biến thể của lượt D6, nơi deploy chạy
*sớm hơn* commit nên số phiên bản trùng mà mã nguồn thì cũ.

### (b) DOM trang chạy thật

`/portal/return/new` trả 200 · `?v=1281` có · `id="wj-ret-m-line-full"` có ·
`<form class="wj-mform" data-wj-dirty-guard="1">` có.

**Đính chính bảng giao việc:** "3 thẻ `wj-mform`" không nằm trên một trang. Grep mã nguồn ra 3
call site ở **ba trang khác nhau**; đã đo đủ cả ba trên UAT, mỗi trang đúng 1 thẻ, đều 200:
`/portal/return/new` · `/portal/support/new` · `/portal/info-request/new`.

---

## 2. `wj_formcontrol.py` — khớp tuyệt đối bảng d6c

⚠️ **Lượt đầu suýt thành mẫu thiếu.** Chạy mặc định `--scope .wujia-mpage` chỉ ra **52** control
(bảng d6c local là 80), và `/portal/info-request/new` — chính là **form thứ ba mang `wj-mform`** —
ra **0 control**. Đúng phát hiện gốc của D6c: `.wujia-mpage` không phủ hết portal, sale/debt/
info-request dùng vỏ khác. Chạy lại `--scope body` (khối PC ẩn bằng `d-none` nên guard tự bỏ qua):

| Chỉ số (390 + 360) | Local trước | Local sau | **UAT sau deploy** |
|---|---:|---:|---:|
| control đo được | 80 | 80 | **82** |
| dưới ngưỡng chạm | 64 | 0 | **0** ✅ |
| lệch radius | 20 | 0 | **0** ✅ |
| cao 20 control của 3 form | 30,4 · 35,9 · 56,8 · 79,2 · 101,6 | 48×15 · 96×4 · 101,6 | **48×15 · 96×4 · 101,6** ✅ |
| radius 20 control đó | 5,25×20 | 12×20 | **12×20** ✅ |
| vùng chạm control còn lại | 28,1×2 · 38×15 · 44 · 54×2 | 44×18 · 54×2 | **44×17 · 48×2 · 54×2** |
| thiếu nhãn | 58 | 18 | **16** |

**Giá trị chỉ có sau khi sửa** (không chỉ nhìn cờ sạch): radius **12** chứ không phải 5,25 trên
cả 20 control; hai ô lọc `/portal/info-request` **44** chứ không phải 28; ba form 9 + 4 + 7 = **20
control** đều 48/96.

Hai chỗ lệch so với local, đã truy nguyên, **không phải lỗi**:

- **82 thay vì 80** và **48×2** trong vùng chạm: UAT gánh thêm luồng quà tặng (`wujia_sale`
  19.0.4.4.0) — control mới ở `/portal/order`, ngoài phạm vi D6.
- **16 thay vì 18** ô thiếu nhãn: local đếm thêm route nhóm Khảo sát, không nằm trong `ROUTES`
  của guard. Danh sách 8 ô/khổ trên UAT đúng nhóm đã đề nghị BA mở issue riêng
  (`docs/ba-notice-d6-filter-labels.md`): search của order · purchase-history · delivery · return ·
  notification · knowledge, cộng 2 select của info-request.

## 3. `wj_returncard.py` — 0 vi phạm, và mẫu KHÁC 0

⚠️ **Rủi ro Pass rỗng lớn nhất của lượt này, đã né được bằng cách chọn tài khoản.** Kiểm kê UAT
bằng XML-RPC chỉ-đọc: 13 phiếu bù hàng (HCM-01 7 · HN-01 4 · HN-02 2), **chỉ 2 phiếu có
`resolution_type='compensation'` và cả hai thuộc HCM-01**. Badge tiến độ bù chỉ render khi
`resolution_type == 'compensation'` ⇒ đo bằng `anh.owner` (HN-01) sẽ ra **0 cặp badge**, cờ sạch
mà rỗng. Đo bằng **`em.hcm`**:

| Khổ | card | có tên SP | cắt dòng 1 | **cặp badge** | badge cùng hàng | bố cục metadata |
|---:|---:|---:|---:|---:|---:|---:|
| 991 | 7 | 7 | 0 | **2** | **0** | 1 |
| 390 | 7 | 7 | 0 | **2** | **0** | 1 |
| 360 | 7 | 7 | 0 | **2** | **0** | 1 |

**Tổng vi phạm: 0.** Giá trị chỉ có sau khi sửa, đọc từ computed style của chính UAT:

- `lineClamp = 2` trên **7/7** card (trước D6b là `none`);
- `whiteSpace = normal` (trước là `nowrap`);
- hai cặp badge cách nhau **Δ = 35px** theo `top` (`RTN/26/00001`, `RTN/26/00002`) — trước D6b
  chúng cùng hàng, Δ ≤ 2;
- metadata chỉ **một** bộ `left = (31, 185)` cho mọi card ⇒ grid `1fr 1fr` thẳng cột.

**Mẫu UAT nhỏ hơn mẫu local** (7 card / 2 cặp badge, so với 20 card / 5 cặp badge), vì không được
seed trên UAT. Kèm theo đó, tên sản phẩm dài nhất trên UAT là ASCII ngắn (`Hong tra bi dao`), không
có tên CJK nào — đúng như D6a đã kiểm kê. Nên vế *"không cắt giữa nội dung"* của `UAT-BH-007` trên
UAT được chứng minh bằng **cấu trúc** (`line-clamp:2` + `overflow-wrap`), chứ không bằng một tên
bị cắt thật; phần chứng minh bằng tên 73 ký tự có CJK nằm ở bảng d6c, đo trên bản sao có seed.

## 4. `wj_measure.py` — hồi quy toàn portal

13 route × 5 khổ. **Tràn ngang 0 · lỗi JS 0 · redirect ngầm 0 · 0 màn mất record.**
RULE 2 histogram cỡ tiêu đề card `16×2 · 18×54 · 22×6 · 24×3`; nhịp header→body `0×9 · 8×2 · 12×33`.

🔴 **RULE 1 HIERARCHY = 3, trong khi bảng d6c local là 0.** Không kết luận vội — UAT lượt này gánh
hai luồng. Truy ra **cả ba cờ là MỘT chỗ duy nhất**, ở `/portal/delivery`, ba khổ PC 1440/1024/992:
chữ trạng thái rỗng *"Không có chuyến giao"* cỡ **28** lớn hơn tiêu đề card *"Danh sách chuyến
giao"* cỡ **22**. Ba bằng chứng độc lập cho thấy **không phải hồi quy D6**:

1. **Hai commit D6 không đụng một file nào của `wujia_portal_delivery`** (`git show --name-only`).
2. **Cùng route, cùng bản build, đổi tài khoản thì hết cờ**: `em.hcm` (có chuyến giao) ra
   **HIERARCHY 0** ở cả 5 khổ. Cờ chỉ hiện ở nhánh **trống dữ liệu**, mà `anh.owner` (HN-01) tình
   cờ không có chuyến giao nào trên UAT.
3. **Chữ đó có từ `f507ba0`**, commit dựng màn giao hàng PC, rất lâu trước cụm D6.

⇒ Lỗi có sẵn, lộ ra do dữ liệu của tài khoản đo, không do đợt sửa này. Đề nghị gộp vào lứa D7+
cùng nhóm chuẩn component (trạng thái rỗng chưa có spec riêng).

## 5. Kết luận

| Ngưỡng chủ dự án đặt | Kết quả UAT |
|---|---|
| `wj_formcontrol`: dưới ngưỡng chạm 0 · control 48 (textarea 96) · radius 12 · ô lọc 44 | **đạt cả bốn** ✅ |
| `wj_returncard`: 0 vi phạm | **0**, mẫu 7 card / 2 cặp badge (khác 0) ✅ |
| `wj_measure`: 0 tràn ngang · 0 lỗi JS · 0 ô mất record | **0 · 0 · 0** ✅ |

⇒ Đủ điều kiện đánh dấu `ĐÃ DEPLOY UAT` cho `UAT-BH-007` · `UAT-BH-008` · `UAT-BH-009`.
Dev **không** tự đóng `Done`.

**Số liệu thô:** `scratchpad/d6d_uat_formcontrol_body.json` · `d6d_uat_returncard_hcm.json` ·
`d6d_uat_measure.json` · `d6d_uat_delivery_hcm.json`.
