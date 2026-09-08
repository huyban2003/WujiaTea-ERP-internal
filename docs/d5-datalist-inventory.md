# D5 — Kiểm kê & phân loại DataList (`UI-DATALIST-001`, STT 126)

**Ngày:** 2026-09-06 · **Cơ sở:** `3c9d9d1` · **Spec:** `CMP-DL-001`, tab `UI Component`
gid `488333015`, **dòng 36, Status `BA Confirmed`, Need BA Confirm = No** · **Phiên:** D5a —
kiểm kê, **0 dòng code sản phẩm**.

Bước 1 của cụm D5, mắt xích thứ tư của bộ component chung sau `CMP-PG-001` (B3),
`CMP-SH-001` (C8), `CMP-CH-001` (D3) và `CMP-SC-001` (D4).

**Điều làm D5 khác hẳn ba cụm trước:** D3 đổi cỡ chữ *trong* thẻ, D4 đổi *khung* thẻ — cả hai
thuần CSS, markup gần như đứng yên. D5 đụng **cấu trúc** (`table/thead/tbody/th[scope]`),
**trạng thái dữ liệu** (loading/empty/no-result/error), **điều kiện hiện pager**, và ràng buộc
**PC ↔ mobile chung một nguồn field/count/filter/sort/pagination**. Ít call site hơn D4 nhưng
mỗi call site sâu hơn.

---

## 1. Phép thử phân loại — và vì sao KHÔNG đếm bằng tên class

D4 phải đính chính con số **ba lần trong cùng một cụm** (51→50, 36→7, 24→4), cả ba lần cùng một
nguyên nhân: `grep` bắt luôn tên con BEM. D5 tránh hẳn đường đó bằng cách đếm theo **cấu trúc**.

> **Phép thử D5.** Một khối **LÀ DataList** khi nó render **tập record nghiệp vụ lặp lại**
> (`t-foreach` trên recordset/list dữ liệu) **và** người dùng đọc nó như một danh sách để chọn
> ra một record. PC thường là `<table>`; mobile là chuỗi row/card.

Cách đếm: parse XML bằng `lxml`, lấy mọi element mang `t-foreach`, rồi **lần xuống element thật
đầu tiên** nếu vòng lặp gắn trên `<t>` (QWeb không render thẻ `<t>`, nên class của item nằm ở
con). Kết quả thô: **133 element `t-foreach`** trong view portal → lọc bỏ vòng lặp không phải
record (option của `<select>`, nút trang, tuần lịch, attachment, ngôn ngữ) → **64 vòng lặp
render record**.

### Ba ranh giới phải viết ra trước, vì chắc chắn gặp

| Không phải DataList | Vì sao |
|---|---|
| Bảng dòng *trong một chứng từ* (`portal_history.xml:497`, `portal_delivery.xml:500`, `portal_return_detail.xml:188`, `portal_exam.xml:1035`) | Là nội dung của MỘT record, không phải danh sách record. BA loại thẳng "form line editor" |
| Lưới sản phẩm đặt hàng (`portal_order_catalog.xml:43/135`) + giỏ hàng (`pc_cart_panel.xml:57`) | BA ghi rõ Out of scope: product grid, cart quantity editor |
| `wujia-msheet-item` (9 call site, `mobile_bottomnav.xml`) | Bottom-sheet **điều hướng**, không phải record nghiệp vụ. Đếm nhầm chỗ này là thổi số y như D4d/D4e |
| `wujia-mknow-feat` (`portal_knowledge.xml:208`) | BA ghi "featured/editorial card nằm ngoài" |
| Báo cáo (`portal_report_orders.xml:336/144`) | **Không nằm trong 10 route** BA liệt kê ở mục "Màn hình áp dụng" |
| Khối khảo sát chi tiết (`portal_inspection_detail_templates.xml` ×8, `inspection_survey_web_templates.xml` ×2) | Nội dung của một phiếu, không phải danh sách phiếu |

**Ngược lại, dashboard preview LÀ DataList** — BA viết thẳng ở "Màn hình áp dụng"
(`/portal: dashboard preview nghiệp vụ`), variant `compact-row`, **không pager**, dùng
"Xem tất cả" ở CardHeader.

---

## 2. Kiểm kê — 31 call site trong phạm vi BA

10 route BA liệt kê. Cột "đo được" = có dữ liệu thật trên DB dev để đo hôm nay (§5).

| # | Route | PC | file:dòng | Mobile | file:dòng | Đo được |
|---|---|---|---|---|---|---|
| 1–3 | `/portal` preview ×3 ✅D5d | `li.wujia-content-card-row` | `portal_home.xml:135/164/195` | `a.wujia-mdash-row` | `portal_home.xml:381/467/539` | ✅ |
| 4 | `/portal` top sản phẩm | `tr` trong `wujia-content-card-table` | `portal_home.xml:234` | — | — | ✅ |
| 5 | `/portal` chuyến sắp giao | — | — | `a.wujia-mdash-row is-stacked` | `portal_home.xml:429` | ✅ |
| 6 | `/portal` bài viết | — | — | `a.wujia-mdash-row` | `portal_home.xml:506` | ✅ |
| 7 | `/portal/purchase-history` | `tr` trong `wj-pc-table` | `portal_history.xml:66` | `a.wujia-mhist-row` | `:155` | ✅ |
| 8 | `/portal/return` | `tr` trong `wujia-content-card-table` | `portal_return_list.xml:110` | `a.wujia-mreturn-row` | `:245` | ✅ |
| 9 | `/portal/delivery` | `tr` trong `wj-pc-dlv-table` | `portal_delivery.xml:61` | `a.wujia-mdelivery-row` | `:159` | ⚠️ 1 record |
| 10 | `/portal/debt` hoá đơn ✅D5g | `tr` trong `wj-debt-pc-table` | `portal_debt.xml:406` | `div.wj-debt-inv` | `:233` | ❌ 0 record |
| 11 | `/portal/debt` thanh toán ✅D5g | `tr` trong `wj-debt-pc-table` | `portal_debt.xml:647` | `div.wj-debt-pay` | `:551` | ❌ 0 record |
| 12 | `/portal/notification` | `tr.wj-pc-noti-row` | `portal_notification.xml:59` | `a.wujia-mnoti-row` | `:161` | ✅ |
| 13 | `/portal/support` | `tr` trong `wujia-content-card-table` | `portal_support.xml:80` | `a.wujia-mdash-row` | `:185` | ⚠️ 1 record |
| 14 | `/portal/exam` | `tr` trong `wj-exam-pc-list-table` | `portal_exam.xml:103` | `a.wj-surface-card--record` | `:202` | ✅ |
| 15 | `/portal/exam` khoá thi | — | — | `div.wujia-mexam-course` | `:686` | ✅ |
| 16 | `/portal/exam` người dự thi | — | — | `div.wujia-mexam-rrow` | `:1126` | ✅ |
| 17 | `/portal/knowledge` ✅D5d | `li.wujia-content-card-row` | `portal_knowledge.xml:99` | `a.wujia-mknow-row` | `:234` | ✅ |
| 18 | `/portal/inspection` | `tr` trong `wj-pc-table` | `portal_inspection_list_templates.xml:81` | `a.wj-surface-card-link` | `:188` | ❌ 0 record |

**Ngoài 10 route BA nhưng CÙNG bệnh** (ghi lại để đừng bỏ quên, xử lý ở lượt cuối):
`/portal/info-request` (`portal_info_request_list.xml:102`, `wujia-content-card-table`) ·
`/portal/franchise-information` danh sách thành viên (`portal_franchise_information.xml:119`
PC + `:272` mobile `wujia-mdash-row`).

**Tổng: 31 call site trong phạm vi BA + 3 call site kề cận = 34.**

> **Đính chính 08/09/2026 (đo trên UAT sau D5h):** thiếu **một** call site — bảng PC *Kết quả thi*
> `table.wj-pc-table.wj-exam-pc-res-table` (`portal_exam.xml:1037`, 7 cột) ở màn con
> `/portal/exam/registration/N`. Nó **là danh sách bản ghi** (mỗi dòng một người dự thi) nên thuộc
> phạm vi, khác `wj-exam-pc-part-table` (bảng nhập liệu) và `wj-exam-pc-sum-table` (bảng xác nhận
> trong wizard). Kiểm kê D5a bỏ sót vì chưa ai mở màn con trên PC. ⇒ **Tổng thật: 32 + 3 = 35**,
> và sau D5h là **29/32** trong phạm vi BA. Bản mobile của chính màn đó (`wujia-mexam-rrow`) đã
> migrate ở D5h nên PC/mobile đang lệch — đề xuất lượt vá **D5h.1**.
>
> **✅ D5h.1 đã vá 08/09/2026:** bảng *Kết quả thi* vào `wj_data_list` variant `table`
> (`th[scope]` 0/7 → 7/7 · header 50 → **44** · đệm ô `0 22px` → **`10px 16px`** · row 58 cứng →
> **56 mềm**), rule dáng cũ khoá bằng `:not(.wj-data-table)`. Không đẻ pager (bảng render trọn
> theo `pc_detail['lines']`, không phân trang phía server) và có `dl_empty` + DataState.
> ⇒ **30/32 trong phạm vi BA (+3 kề cận = 33/35)**; 2 chỗ còn lại là khảo sát, **defer có chủ ý**.
So sánh quy mô: D3 = 103 · D4 = 384 · **D5 = 34**. Nhỏ nhất về số lượng, sâu nhất về bản chất.

Phân rã 31 call site trong phạm vi — đây mới là con số dùng để chia lượt, **không phải** số lần
xuất hiện của tên class (`wj-pc-table` xuất hiện 15 lần nhưng chỉ **5** trong số đó là danh sách
record; phần còn lại là bảng chi tiết chứng từ, gallery `pc_preview` và báo cáo):

| Nhóm | Số |
|---|---:|
| Bảng PC render record | 10 |
| Danh sách PC không phải bảng (`li.wujia-content-card-row`) | 4 |
| Mobile compact-row (`wujia-mdash-row` ×6 · `mhist` · `mnoti` · `mknow`) | 9 |
| Mobile detail-card (`mreturn` · `mdelivery`) | 2 |
| Mobile công nợ (`wj-debt-inv` · `wj-debt-pay`) | 2 |
| Mobile thi (`wj-surface-card--record` · `mexam-course` · `mexam-rrow`) | 3 |
| Mobile khảo sát (`wj-surface-card-link`) | 1 |

⚠️ Bảng §2 ở trên liệt kê **theo route** nên một dòng có thể chứa 2 call site (PC + mobile);
cộng theo dòng là ra sai. Bảng phân rã này mới là bảng cộng được.

### Chủ sở hữu CSS của từng họ

| Họ | Rule | File CSS |
|---|---|---|
| `wj-pc-table` | 12 | `wujia_portal_layout/…/_pc_components.css` |
| `wujia-content-card-table` | 10 | `wujia_portal_layout/…/_components.css` |
| `wujia-content-card-row` | 4 | `_components.css` |
| `wujia-mdash-row` | 3 | `_components.css` |
| `wujia-mhist-row` | 4 | `_components.css` + `_interaction.css` |
| `wujia-mreturn-row` | 4 | `_interaction.css` + `wujia_portal_return/portal_return.css` |
| `wujia-mnoti-row` | 1 | `wujia_portal_notification/portal_notification.css` |
| `wujia-mknow-row` | 1 | `_components.css` |
| `wujia-mdelivery-row` | 1 | `wujia_portal_delivery/portal_delivery.css` |
| `wj-debt-inv` / `wj-debt-pay` | 1 + 1 | `wujia_portal_debt/portal_debt.css` |
| `wujia-mexam-course` | 1 | `wujia_portal_exam/portal_exam.css` |
| `wj-pc-noti-row` | **0** | ❗ không rule nào — dáng đến hoàn toàn từ `wj-pc-table` |

---

## 3. Mốc đo TRƯỚC — số thật, đối chiếu số BA

Bộ đo: **`scripts/qa/wj_datalist.py`** (mới, trong repo — bộ cũ `wj_measure.py` đo *khung card*,
không đo được row/gap/padding của danh sách). Kết quả: `docs/d5-datalist-before.json`.
6 khổ BA chỉ định **1440 · 1024 · 992 · 991 · 390 · 360**, 10 route, 60 lượt tải trang,
**0 lỗi JS · 0 tràn ngang · 0 redirect ngầm**.

### 3.1 Bảng PC — 7 bảng đo được (@1440)

| Route | Bảng | Cột | `th[scope]` | Header | Row | Cell padding |
|---|---|---:|---|---:|---|---|
| `/portal` | `wujia-content-card-table` | 4 | **0/4** | 46 | 45–46 | `14px 20px` |
| `/portal/purchase-history` | `wj-pc-table` | 7 | **0/7** | 50 | 58 | `0 22px` |
| `/portal/return` | `wujia-content-card-table` | 7 | **0/7** | 46 | 60–61 | `14px 20px` |
| `/portal/delivery` | `wj-pc-dlv-table` | 8 | **0/8** | 50 | 58 | `0 22px` |
| `/portal/notification` | `wj-pc-noti-table` | 5 | **0/5** | 50 | 58 | `0 22px` |
| `/portal/support` | `wujia-content-card-table` | 8 | **0/8** | 46 | 62 | `14px 20px` |
| `/portal/exam` | `wj-exam-pc-list-table` | 8 | **0/8** | 50 | 68 | `0 22px` |

**Ba khoảng cách với spec, đo được chứ không suy:**

1. **`th[scope]` = 0/21 lượt đo — không một bảng nào có `scope`.** Kiểm chéo tĩnh trên **14
   bảng** trong mã nguồn: cũng 0. Yêu cầu SEMANTIC của BA *"th có scope"* hiện **vỡ 100%**.
   Đây là hạng mục rẻ nhất và chắc ăn nhất của cả cụm.
2. **Header 46 hoặc 50, BA đòi 44.** Hai giá trị vì hai họ bảng khác nhau, không phải ngẫu nhiên.
3. **Cell padding không họ nào đúng `10px 16px`**: `wj-pc-table` cho `0 22px` (row cao 58 nhờ
   `height` chứ không nhờ padding), `wujia-content-card-table` cho `14px 20px`.
   Row thấp nhất đo được là **45px ở `/portal`** — dưới sàn `min 52` của BA.

### 3.2 Danh sách mobile (@390)

| Route | Container | Item | Cao | Gap | Radius | Padding |
|---|---|---|---|---:|---:|---|
| `/portal` ×6 khối | `wj-surface-card--section` | `wujia-mdash-row` | 63–112 | **0** | 0 | `12px 0` |
| `/portal/delivery` ⚠️ | `wujia-mdelivery-list` | `wujia-mdelivery-row` | **128.98** | **12** | 14 | `12px 16px` |
| `/portal/purchase-history` | `wujia-mhist-list` | `wujia-mhist-row` | 74.3 | **8** | 12 | `10px 14px` |
| `/portal/return` | `wujia-mreturn-list` | `wujia-mreturn-row` | 122.3 | **12** | 14 | `14px` |
| `/portal/notification` | `wujia-mnoti-list` | `wujia-mnoti-row` | 99.9–129.3 | **8** | 12 | `12px 14px 12px 16px` |
| `/portal/exam` | `wujia-mexam-list` | `wj-surface-card--record` | 109.2 | **12** | 14 | `12px` |
| `/portal/knowledge` | `wujia-mknow-list` | `wujia-mknow-row` | 83.8–133.4 | **10** | 14 | `14px` |

**Đối chiếu BA** (compact-row 64–76 · detail-card 96–120 · gap 8 · radius 12 · padding
compact `10–12px 12–14px`, detail `12px 14px`):

- Đúng chuẩn compact-row: **chỉ `wujia-mhist-row`** (74.3 / gap 8 / radius 12 / `10px 14px`).
- `wujia-mdash-row` **gap 0** — các dòng preview dính liền nhau, và cao 63–112 tuỳ khối.
- `wujia-mreturn-row` **122.3** vượt trần detail-card 120; `wujia-mnoti-row` **99.9–129.3** và
  `wujia-mknow-row` **83.8–133.4** — cùng một danh sách mà biên độ cao gấp rưỡi.
- Bốn giá trị gap cho một quy tắc: **0 · 8 · 10 · 12**.
- ⚠️ Dòng `/portal/delivery` **bổ sung ngày 08/09 khi làm D5f**, không có trong lần đo gốc: lúc kiểm
  kê cửa hàng chỉ có **1 chuyến** nên hàng này không đo được. Sau khi seed 14 chuyến mới lộ ra
  **128.98 — vượt trần detail-card 120**, và đệm dọc vốn đã là 12px nên không hạ được bằng padding.

### 3.3 Điều đã ĐÚNG sẵn — đừng đụng vào

**Ngưỡng 992/991 đã chuẩn tuyệt đối:** đo 30 ô ở `991/390/360` ra **0 bảng nào còn render**,
và 21/21 ô ở `1440/1024/992` đều có bảng. Ranh giới `>=992px DataTable / <992px list` của BA
**không cần sửa gì** — đây là kết quả của việc mọi màn đã tách khối `d-none d-lg-*` từ các
sprint trước.

---

## 4. Trạng thái dữ liệu & pagination — chỗ lệch nặng nhất

### 4.1 Sáu cách viết cho MỘT quy tắc

BA: *"Pager chỉ khi `totalPages > 1`"*. Truy điều kiện `t-if` của chính khối pager **và mọi tổ
tiên** (`lxml`, không grep):

| Điều kiện thật | Route | Đúng spec? |
|---|---|---|
| `pager.get('page_count', 0) > 1` | knowledge · return · support ×2 · info-request · order catalog | ✅ |
| `total_pages > 1` | inspection | ✅ |
| `rows and pager['page_total'] > 10` | purchase-history | ❌ chôn cứng số 10 |
| `notifications and pager and total > 10` | notification | ❌ chôn cứng số 10 |
| `m_pager.get('page_total', 0)` | delivery | ❌ chỉ cần CÓ record |
| `pc_invoices` · `pc_payments` · `pc_regs` | debt ×2 · exam | ❌ **1 trang vẫn hiện pager** |

⇒ **5/11 khối pager vi phạm** quy tắc BA. Hai khối chôn số `10` còn tự vỡ nếu đổi page-size.

### 4.2 Bốn trạng thái

| Route | empty | no-result + "Xoá lọc" | loading skeleton | error |
|---|---|---|---|---|
| purchase-history · return · support · delivery | ✅ | ✅ | delivery ✅ (17 chỗ), còn lại ✗ | ✗ |
| notification · knowledge | ✅ | ✅ 1 chỗ | ✗ | ✗ |
| exam | ✅ | ✗ | ✅ (2 chỗ) | ✗ |
| debt | ✅ | ✗ | ✗ | ✗ |
| info-request | ⚠️ 1 chỗ | ✗ | ✗ | ✗ |
| inspection | ⚠️ `wj-pc-empty` + `py-5 text-center` tự dựng | ✗ | ✗ | ✗ |
| `/portal` preview | ✅ (`wj-empty-state--row`, S50) | — (không lọc) | ✗ | ✗ |

**`error` = 0/10 route.** Trạng thái lỗi BA yêu cầu ("thông báo + Thử lại") hiện **chưa tồn tại
ở đâu cả**.

### 4.3 Tầng state đã có sẵn — tái dùng, không viết mới

**11/11 route** trong phạm vi đã `t-call="wujia_portal_base.wj_ajax_list_config"` (S49). Tức là
tầng fetch/filter/pagination **đã dùng chung rồi**; cái chưa dùng chung là **tầng render**.
Đó chính là chỗ DataList phải chen vào, và là lý do D5 không được đẻ cơ chế fetch mới.

Tái dùng: `wj_ajax_list` (`wujia_portal_base/{views,static/src/js,static/src/css}/wj_ajax_list.*`)
· `page_numbers()` `controllers/utils.py:267` · `group_counts()` `:283`.
`CMP-ES-001` EmptyState và `CMP-PGNT-001` Pagination là **component riêng của BA** — D5 chỉ định
nghĩa *chỗ đứng* của chúng trong `DataList [DataViewport + DataItem(s) + DataState + Pagination]`,
không nuốt phạm vi.

---

## 5. Ràng buộc đo được — quyết định thứ tự lượt nhiều hơn kích cỡ

Đúng như D4a, cái quyết định thứ tự không phải họ nào to, mà **họ nào đo được**.

| Route | Trở ngại | Kéo theo |
|---|---|---|
| `/portal/debt` | **0 hoá đơn có `franchise_id`** trên DB dev ⇒ PC bảng lẫn mobile đều ra empty state | `wj-debt-pc-table` ×2 · `wj-debt-inv` · `wj-debt-pay` |
| `/portal/inspection` | **0 phiếu khảo sát** (module nay đã `installed`, route trả 200, chỉ thiếu dữ liệu) | bảng PC + list mobile khảo sát |
| `/portal/support` · `/portal/delivery` | **đúng 1 record/cửa hàng** ⇒ không đo được gap, không thử được pager | `wujia-mdash-row` (support) · `wujia-mdelivery-row` |

⇒ **Việc phải làm trước D5b: bổ seed.** BA acceptance #7 đòi thử ở **0/1/2/10/11/50+ record**;
DB dev hiện nhiều nhất 7 ticket / 5 phiếu bù hàng / 1 chuyến / 0 hoá đơn / 0 khảo sát. Không có
dữ liệu thì không có bảng đo trước–sau, mà không có bảng đo thì **không được migrate** (luật D4 #2).

### Một lỗi CÓ SẴN lộ ra khi đo — không thuộc D5, và đính chính ghi chú 05/09

`/portal/reports/orders` trả **500** trên máy này. Ghi chú 05/09 kết luận *"chặn kỹ thuật đã hết
hạn, route trả 200"* — **kết luận đó chỉ đúng trên máy Mac**. Nguyên nhân thật, đọc từ traceback:

```
custom/wujia_portal_report/controllers/portal.py:97  _read_group(...)
psycopg2.errors.InvalidParameterValue: time zone "Asia/Saigon" not recognized
```

Thủ phạm là **PostgreSQL**, không phải Odoo: PG 16.15 trên Ubuntu 24.04 chỉ biết
`Asia/Ho_Chi_Minh`, không còn bí danh `Asia/Saigon`; user `anh.owner` lại đang mang tz
`Asia/Saigon` (admin thì `Asia/Ho_Chi_Minh`). Chuỗi tz đi thẳng từ bản ghi user vào SQL của
`_read_group`, nên `portal_tz()` có nhánh fallback cũng không cứu được. Máy Mac hết lỗi vì
tzdata của PG bên đó còn giữ bí danh — **khác môi trường, không phải đã sửa**.
Đây là việc của cụm **R3**; ghi vào đây để phiên sau khỏi kết luận nhầm lần nữa. **Không chặn
D5** vì báo cáo không nằm trong 10 route BA liệt kê.

---

## 6. Bảng chia lượt D5b…D5h

Nguyên tắc kế thừa D4: **lượt đầu là lượt đo được rẻ nhất để hiệu chỉnh chính bảng đo**, không
phải lượt gọn nhất về file. Mỗi lượt: đúng **một** lần `-u`, một bảng đo trước–sau đủ 6 khổ,
chạy lại RULE 1/RULE 2 (`wj_measure.py`) vì đổi row là đổi nhịp trong card, guard chứng minh
bằng **mutation**.

| Lượt | Nội dung | Call site | `-u` | Rủi ro chính | Vì sao xếp ở đây |
|---|---|---:|---|---|---|
| **D5b** | Dựng nền: token + `wj_data_list` (`DataViewport`/`DataItem`/`DataState`/slot Pagination); hiệu chỉnh trên **`wujia-content-card-table`** (`/portal` top sản phẩm · `/portal/return` · `/portal/support`) + `th[scope]` và guard pager cho đúng 3 file đó | **3** | `wujia_portal_layout`, `_base`, `_return`+`wujia_sale`, `_support` | Thấp — cả 3 đo được ngay, `th[scope]` là thêm thuộc tính, không đổi dáng | Rẻ và đo được ⇒ dùng để **hiệu chỉnh chính bảng đo** trước khi đụng họ lớn (đúng bài học D4b) |
| **D5c** | Bảng PC họ `wj-pc-table`: `/portal/purchase-history` · `/portal/delivery` · `/portal/notification` | **3** | `_layout`, `_purchase_history`, `_delivery`, `_notification` | 🔴 Nặng nhất: header 50→44, padding `0 22px`→`10px 16px`, và **row 58 hiện do `height` chứ không do padding** ⇒ đổi cả cơ chế dựng chiều cao | Sau khi bảng đo đã hiệu chỉnh. Ba route này dùng chung một tầng CSS `_pc_components.css` |
| **D5d** | Danh sách PC **không phải bảng**: 3 khối preview `/portal` + `/portal/knowledge` (`li.wujia-content-card-row`) | **4** | `_layout`, `_base`, `_knowledge` | Preview không có pager (BA: dùng "Xem tất cả" ở CardHeader) ⇒ đừng gắn Pagination vào | Cùng họ CSS với D5b, làm liền mạch |
| **D5e** | Mobile compact-row: `wujia-mdash-row` ×6 (5 khối `/portal` + `/portal/support`) · `mhist` · `mnoti` · `mknow` | **9** | `_layout`, `_base`, `_purchase_history`, `_notification`, `_knowledge`, `_support` | Gom gap **0/8/10/12** về 8; `wujia-mdash-row` nằm trong 6 khối Home nên đụng là đụng Home | `wujia-mhist-row` **đã đúng chuẩn sẵn** (74.3 / gap 8 / radius 12) ⇒ dùng làm mẫu, không phải đoán số |
| **D5f** ✅ | Mobile detail-card (ngoại lệ BA): `wujia-mreturn-row` · `wujia-mdelivery-row` | **2** | `_return`+**`wujia_sale`**, `_delivery` | XONG 08/09 — dựng variant `detail-card` (chưa từng có CSS); `mreturn` 122.3 → **118.3** ✅ trong dải, `mdelivery` **128.98 vẫn vượt trần 120** (chỉ lộ ra SAU khi seed, kiểm kê cũ chỉ có 1 chuyến) ⇒ báo BA; skeleton mang luôn `wj-data-item` để không nhảy hình lúc tải | Lượt đầu tiên làm trang **ngắn lại** (−156/−52) và **không thủng ô acceptance #9 nào**. Số đo `docs/d5f-acceptance-matrix.md` |
| **D5g** ✅ | Công nợ: `wj-debt-pc-table` ×2 + `wj-debt-inv` (compact-row) + `wj-debt-pay` (detail-card), kèm sửa guard `page_count > 1` | **4** | `_layout`, `wujia_portal_debt` | XONG 08/09 — `th[scope]` 0/14 → **14/14**, header 50 → 44, row **58 cứng** → 52–55, padding `0 22px` → `10px 16px`; mobile 62 → **75,5** và 96 → **104/116**, **cả hai vào đúng dải BA**. Guard pager **tách đôi**: nút trang theo `page_count`, dòng *Tổng thanh toán* là thông tin của kỳ lọc nên giữ | Variant chọn theo **số đo sau khi seed**, không theo tên gọi. Acceptance #9 thủng **1 ô** (@360, 5→4) + hover mới xuất hiện trên `wj-debt-inv` ⇒ báo BA. Số đo `docs/d5g-acceptance-matrix.md` |
| **D5h** ✅ | Thi: `wj-exam-pc-list-table` + `mexam-card` + `mexam-course` + `mexam-rrow`; **kề cận**: bảng PC `/portal/info-request` + bảng PC & list mobile `/portal/franchise-information` | **7** | `_exam`, `_base`, `_info_request`, `_layout` | XONG 08/09 — `th[scope]` 0/20 → **20/20**, header 50/46 → **44**, padding → **`10px 16px`**; mobile: `mexam-card` & `mexam-course` `detail-card`, `mexam-rrow` & `mdash-row` `compact-row`, **cả bốn vào đúng dải BA**. Guard pager thi theo key **`pages`** (không phải `page_count`); **gỡ pager giả** ở màn thông tin cửa hàng (3 `<span>` cứng, không hề phân trang server) | ⚠️ **2 call site Khảo sát DEFER** theo quyết định chủ dự án (module nhánh `thai`, lối code khác portal) ⇒ cụm khép **29/31**. Acceptance #9 thủng **2 ô** ở màn Thi + `mexam-rrow` mọc hover dù không bấm được ⇒ báo BA. Số đo `docs/d5h-acceptance-matrix.md` |
| — | Kề cận ngoài 10 route: `/portal/info-request` · danh sách thành viên `/portal/franchise-information` | 3 | — | **Đã làm ở D5h** (08/09) | — |

Cộng: 3+3+4+9+2+4+6 = **31**, khớp bảng phân rã §2.

**Trước D5b:** bổ seed để đạt mốc BA acceptance #7 (0/1/2/10/11/50+) — ít nhất hoá đơn có
`franchise_id`, phiếu khảo sát, và nâng ticket/chuyến giao lên >10 cho một cửa hàng.

---

## 7. Bốn chỗ Dev tự quyết được — và một chỗ phải hỏi BA

**Tự quyết (spec BA đã đủ rõ, không hỏi):**

1. `th[scope]` — BA viết thẳng "th có scope", 0/21 hiện tại, thêm là xong.
2. Guard pager về `page_count > 1` — BA viết thẳng, 5 chỗ sai là sai rõ ràng.
3. `wujia-mhist-row` đã khớp chuẩn compact-row ⇒ lấy làm mẫu, không cần BA duyệt lại.
4. Ngưỡng 992/991 đã đúng ⇒ **không đụng**, ghi nhận là đạt.

**Phải hỏi BA — một câu, khi tới D5d/D5e:** field nào của bảng PC được phép **ẩn trên mobile**,
và ẩn rồi thì xem lại ở đâu. BA đã tự cảnh báo rủi ro *"ẩn field mobile không có detail sẽ làm
mất thông tin nghiệp vụ"*, mà đo thật cho thấy khoảng cách rất rộng — ví dụ `/portal/delivery`
PC có **8 cột** (gồm *Xe · tài xế*, *Biển số*, *Cập nhật*) trong khi mobile chỉ hiện **4 thông
tin** (mã chuyến · trạng thái · giờ xuất phát · đơn liên quan); `/portal/support` PC **8 cột**
còn mobile 4. Dev **không tự quyết** cái nào là P1/P2/P3.

---

## 8. Bẫy đã trả giá ngay trong phiên kiểm kê này

1. **`--password` mặc định sai làm cả bảng đo "Pass rỗng".** Lượt đo đầu chạy với mặc định
   `demo123` của `wj_measure.py`; DB dev dùng `wujia@test123`. Kết quả: **78/78 ô** trả 200,
   `RULE 1 = 0 vi phạm`, `tràn ngang = 0`, `lỗi JS = 0` — sạch bong, và **sai hoàn toàn**, vì mọi
   route đều redirect về `/web/login`. Thứ duy nhất tố giác là dòng `redirect ngầm: 78`.
   ⇒ `wj_datalist.py` **chặn cứng ngay sau login**: thấy còn ở `/web/login` thì `sys.exit`, không
   đo tiếp. Cùng họ bài học với `--portal-login` mặc định `None` của D4.
2. **Harness đo ra số không tồn tại.** Bản đầu của `wj_datalist.py` nhận mọi hộp có con lặp lại
   là danh sách, nên vớ luôn cụm chip xếp ngang và in ra **gap −32 / −58 / −52px**. Sửa: chỉ nhận
   khi các con **xếp dọc** (`kids[1].top >= kids[0].bottom`). Đúng bài học "thà không đo còn hơn
   đo ra số sai" của bản `wj_measure.py` đầu tiên.
3. **Chuẩn hoá quá tay thì đo hụt.** Bản thứ hai đòi hộp phải đồng nhất hoàn toàn ⇒ bỏ sót mọi
   danh sách có header/pager là anh em của item (support, delivery). Sửa: lấy **dãy liên tiếp dài
   nhất các con cùng chữ ký lớp**. Cùng họ với bẫy `sc_class` của D4 — càng migrate, con số càng
   tụt nếu phép đếm không hiểu cả hai dạng.
4. **Bẫy log L15 tái xuất.** `wujia_core` dời logfile sang `<thư-mục>/<năm>/<tháng>/<ngày>.log`,
   nên traceback của lỗi 500 **không nằm trong file `--logfile`** đã chỉ định. Traceback đầu tiên
   tìm thấy trong `logs/` lại là của **tiến trình cũ còn sót** (`wujia_tea_d4g`, filestore đã
   xoá) — suýt quy oan.
5. **DB dev lạc hậu mà không có dấu hiệu nào trên màn hình.** `wujia_portal_layout` ở
   `19.0.35.0.0` trong khi repo đã `19.0.38.0.0`, và `wujia_portal_inspection` còn `uninstalled`
   từ trước reseed 05/09 của máy Mac. Đo lúc đó là đo portal thời **trước D4e** — mốc sai thì mọi
   bảng trước–sau về sau đều sai theo. Phép kiểm rẻ: so `latest_version` trong DB với
   `__manifest__.py` của **từng** module trước khi đo.

---

## 9. Trạng thái issue sau phiên này

~~`UI-DATALIST-001` giữ nguyên `Ready for Dev`~~ → **`Ready for Retest` từ 08/09/2026 (sau D5h)**,
với tư cách **đề xuất của Dev**: BA chưa trả lời 6 câu treo nên bộ số ghi rõ là **`provisional`**,
kèm **2 call site Khảo sát defer**. Dev **không tự đóng `Done`**.

**Tiến độ cụm: 30/32 call site trong phạm vi BA (33/35 kể cả kề cận)** (D5b xong 07/09 — nền `wj_data_list` +
`/portal` top sản phẩm · `/portal/return` · `/portal/support`, số đo `docs/d5b-acceptance-matrix.md`;
**D5c xong 07/09** — họ `wj-pc-table`: `/portal/purchase-history` · `/portal/delivery` ·
`/portal/notification`, số đo `docs/d5c-acceptance-matrix.md`; **D5d xong 07/09** — họ
`li.wujia-content-card-row`: 3 khối preview `/portal` + `/portal/knowledge`, số đo
`docs/d5d-acceptance-matrix.md`; **D5e xong 07/09** — 9 call site mobile của **bốn** họ
`mdash`/`mhist`/`mnoti`/`mknow`, số đo `docs/d5e-acceptance-matrix.md`; **D5f xong 08/09** —
variant `detail-card` dựng mới + 2 call site `mreturn`/`mdelivery`, số đo
`docs/d5f-acceptance-matrix.md`; **D5g xong 08/09** — 4 call site công nợ (2 bảng PC + mobile
`wj-debt-inv` compact-row + `wj-debt-pay` detail-card), lượt **duy nhất phải sửa guard pager**
`page_count > 1`, số đo `docs/d5g-acceptance-matrix.md`; **D5h xong 08/09** — lượt KHÉP: 4 call site
Thi + 3 call site kề cận, số đo `docs/d5h-acceptance-matrix.md`; **D5h.1 xong 08/09** — vá bảng
*Kết quả thi* mà kiểm kê D5a bỏ sót, `docs/d5h-acceptance-matrix.md` §14).

**Tiến độ cụm sau D5h.1: 30/32 trong phạm vi BA + 3 kề cận = 33/35.** Hai call site còn lại là bảng
PC và danh sách mobile của **Khảo sát** (`wujia_portal_inspection`) — **DEFER CÓ CHỦ ĐÍCH**, không
phải sót: module merge từ nhánh `thai` có lối code khác hẳn portal (Bootstrap thô, inline style,
`sudo()` ở đường ghi); chủ dự án quyết 08/09/2026 là mọi cụm UI bỏ qua hai module này cho tới khi
có chỉ thị khác. Luật đã ghi thường trực vào skill `wujia-start`.

**Đã đóng ở D5b, không phải đo lại:** `th[scope]` của 3 bảng này 0→100 % · header 46→44 ·
cell padding `14px 20px`→`10px 16px` · row ≥52 · guard pager `page_count > 1` được ghim bằng test.

**Đã đóng ở D5c, không phải đo lại:** `th[scope]` 20/20 của 3 bảng họ `wj-pc-table` · header
50→44 · cell padding `0 22px`→`10px 16px` · row 58 (cứng, do `height` trên `<td>`) → 54–89 (mềm,
do `height` trên `<tr>` + đệm thật) · guard pager **tách đôi** (nút điều hướng theo BA
`page_count > 1`, ô chọn số dòng/trang giữ `> 10` của `UI-PC-BASE-005`) · 12 bảng `wj-pc-table`
KHÔNG thuộc phạm vi đo lại vẫn nguyên 50/58/`0 22px`. Bộ đo `wj_datalist.py` nay có thêm trường
`rowsInViewport` cho acceptance #9.
**Đã đóng ở D5d, không phải đo lại:** 4 call site `li.wujia-content-card-row` chuyển sang
variant `compact-row` · item 51.8 → **64** (BA 64–76) · gap 0 → **8** · radius 0 → **12** ·
padding `12px 0` → **`12px 14px`** · `.wj-data-item` là chủ sở hữu DUY NHẤT dáng (4 rule cũ khoá
bằng `:not(.wj-data-item)`) · 3 khối preview **không** pager, ghim bằng test · knowledge là call
site đầu tiên đưa Pagination **vào trong** DataList qua `dl_pager`. **Hai chỗ còn treo**: bộ số
64–76 là **provisional** (BA chưa cấp số cho danh sách PC không phải bảng) và acceptance #9 thủng
ở knowledge (12 → 9 dòng đọc-không-cuộn) — cả hai nằm trong `docs/ba-questions-d5-datalist.md`.
`wj_datalist.py` nay ghi `rowsInViewport` cho **cả nhánh danh sách**, không chỉ nhánh bảng.

**Đã đóng ở D5e, không phải đo lại:** 9 call site mobile về `compact-row` · rule D5d **tách làm
hai** (dáng dùng chung ở `.wj-data-item`, layout ở từng họ) · 4 họ khoá `:not(.wj-data-item)` ·
gap `0/10` → **8** · radius `0/14` → **12** · padding `12px 0`/`10px 14px`/`14px` → **`12px 14px`**
(mnoti giữ `padding-left 16` cho thanh accent) · mnoti **không đổi một pixel** · 10 hàng mdash
KHÔNG phải danh sách giữ nguyên, ghim bằng test · hover 4 họ **không đổi** (`:is()` là (0,4,0) nhờ
tham số đặc hiệu nhất). **Ba chỗ còn treo**: mnoti/mknow vượt trần 76, Home mobile nở +145/+245 và
support +271, acceptance #9 thủng một ô (`/portal` @360, 2 → 1) — cả ba trong
`docs/ba-questions-d5-datalist.md` mục 4.

Seed §5 đã bổ xong bằng `scripts/seed_d5_datalist_demo.py` (52 ticket · 28 bù hàng · 14 hoá đơn ·
14 khảo sát · 14 chuyến giao cho HN-01) ⇒ D5c…D5h **không còn bị chặn bởi dữ liệu**.
