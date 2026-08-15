# Cụm C1–C10 — prompt cho từng session

**Nguồn:** phiên phân cụm 2026-08-14 (32 issue `Ready for Dev`, `5. Issue List` STT 83–114).
Bảng cụm + điểm đã soi trong source → `wujia-compact-summary.md` §13.

**Cách dùng:** `/wujia-start` → nói "làm cụm C<n>" → Claude đọc file này, lấy đúng khối
prompt của cụm đó rồi bắt tay. Không cần nhớ nội dung, chỉ cần nhớ số cụm.

**Thứ tự chạy:** C1 → C2 → C3 → C4 → C5 → C9 → C10 → **C6 → C7** → C8.
Lý do ràng buộc: C1 sửa gốc dữ liệu mà C2/C3/C5 cần để retest · C6 phải xong trước C7
(WJ-HOME-007 đòi trạng thái pressed/focus của component chung) · C8 cuối vì chạm heading
mọi trang, chạy sau khi C7 sắp lại block Home thì khỏi làm hai lần.

**3 quyết định chủ dự án đã chốt 08-14 — đừng hỏi lại:**
1. Giữ 10 cụm, mỗi cụm 1 session 1 lần `-u`.
2. WJ-DEBT-008 = **ẩn hẳn khối QR** (nhánh OR của BA), KHÔNG sinh VietQR thật.
3. WJ-DEBT-004 = **tách tổng theo từng loại tiền**, KHÔNG quy đổi tỷ giá.

> 🔴 **LUẬT CHỦ DỰ ÁN CHỐT 15/08/2026 — KHÔNG `/wujia-end-sprint` cho tới khi ĐỦ 10 CỤM
> C1–C10 xong.** Mỗi phiên làm 1 cụm, ghi tiến độ vào dòng dưới, commit + push `main` để
> chủ dự án deploy UAT rồi BA retest. Chỉ khi cả 10 cụm ✅ mới chốt sprint (viết chapter
> `.tex`, recompile PDF, tổng kết). Đừng đề xuất end sprint sớm.

> 🔴 **Clean code (chốt 15/08/2026):** fix ở đúng chỗ gốc, tách helper dùng chung thay vì
> copy-paste; không thêm field/file khi cái sẵn có đủ; comment ít thôi, chỉ giải thích *tại
> sao* ở chỗ khó đoán. Đừng để code phình sau mỗi cụm.

**Tiến độ cụm:** C1 ✅ 15/08/2026 `b623b70` (3 issue → Ready for Retest, đã push `main`,
chờ deploy UAT; bảng đối chiếu `docs/c1-acceptance-matrix.md`) · C2 ✅ 15/08/2026 `c656b95`
(4 issue → Ready for Retest, `-u wujia_portal_debt` không cập nhật dữ liệu; 38/38 đo đạt,
113 test xanh; bảng đối chiếu `docs/c2-acceptance-matrix.md`) · C3 ✅ 15/08/2026 `0398fa3`
(5 issue → Ready for Retest, `-u wujia_portal_debt` không cập nhật dữ liệu; 115/115 đo đạt ở
6 breakpoint, 38 test + 116 hồi quy xanh; bảng đối chiếu `docs/c3-acceptance-matrix.md`) ·
C4 ✅ 15/08/2026 `a292547` (4 issue → Ready for Retest, `-u wujia_portal_knowledge` không cập
nhật dữ liệu; 60/60 đo đạt 2 viewport, 14 test mới + 87 hồi quy xanh; bảng đối chiếu
`docs/c4-acceptance-matrix.md`) · C5 ✅ 15/08/2026 `94756ff` (4 issue → Ready for Retest,
`-u wujia_portal_delivery,wujia_portal_base` không cập nhật dữ liệu; 20/20 đo đạt 2 viewport,
9 test mới + 75 hồi quy xanh; bảng đối chiếu `docs/c5-acceptance-matrix.md`) · C9 ✅ 15/08/2026 `9a8784b` (3 issue → Ready for Retest,
**`-u wujia_portal_layout,wujia_portal_sale,wujia_portal_purchase_history`** — chú ý có
`wujia_portal_layout` vì CSS gốc nằm ở đó, không cập nhật dữ liệu; 26/26 đo đạt ở 360/391/1920,
8 test mới + 57 hồi quy xanh; bảng đối chiếu `docs/c9-acceptance-matrix.md`) ·
C6 ☐ · C7 ☐ · C8 ☐ · C10 ☐
(đánh ✅ + ngày + commit khi xong, để phiên sau biết đang tới đâu.)

---

## Prompt từng session

> Mỗi prompt dán nguyên văn vào phiên mới **sau khi** chạy `/wujia-start`.
> Mọi prompt đều ngầm áp: đo trên **DB copy cô lập port riêng** (KHÔNG đụng
> `wujia_tea_19`/8019), bảng đối chiếu `Yêu cầu | Đo được | Pass/Fail` ≥90%, regression ≥3
> trang × 2 viewport, xong mới ledger → `qa_sync.py --dry-run` → `--apply`, **Dev không tự
> đóng Done**. ⚠️ DB local chính đang ở `wujia_sale 19.0.4.1.0` ⇒ mọi lệnh `-u` chạm
> `wujia_portal_return` phải kèm `wujia_sale`.

### C1 — Franchise backend

```
Cụm C1: WJ-FRANCHISE-001 (STT 85), WJ-FRANCHISE-002 (STT 89), WJ-DEBT-006 (STT 103).
Gốc rễ chung: franchise_id không suy được từ partner, không được validate, không kế thừa
khi tạo giấy báo có. Module: wujia_sale + wujia_account.

Đọc source trước: wujia_sale/models/sale_order.py (đang chỉ có onchange chiều
franchise_id → franchise_partner_id), wujia_account/models/account_move.py,
account_payment.py, sale_order.py.

Việc:
1. Suy franchise từ partner: partner ↔ cửa hàng đang map qua
   wujia.franchise.management.partner_id. Viết MỘT helper dùng chung (đặt ở wujia_account
   hoặc wujia_core, tự chọn nhưng nói rõ lý do) trả về franchise duy nhất của 1 partner;
   gọi từ onchange partner_id trên sale.order, account.move và stock.picking. Đổi partner
   phải tính lại, KHÔNG giữ franchise cũ. Map 0 hoặc >1 cửa hàng → cảnh báo rõ, không đoán.
2. Validate backend (không chỉ onchange): chặn ở action_confirm của SO, button_validate
   của picking, action_post của invoice khi partner map duy nhất mà franchise_id trống/lệch.
   Phải chặn được cả khi tạo qua import/API.
3. Kế thừa khi reversal: override đường tạo credit note của Odoo (_reverse_moves /
   _prepare_default_reversal — đọc source Odoo 19 rồi chọn seam đúng) để copy franchise_id
   từ hoá đơn gốc. Áp cho cả "Đảo" và "Đảo ngược và tạo hóa đơn".

Perf 1500 store: helper partner→franchise phải là 1 query có index, KHÔNG search trong loop;
nếu gọi ở write/create hàng loạt thì batch lại.

Đối chiếu acceptance GIVEN/WHEN/THEN của cả 3 issue (cột "Kết quả mong muốn"), đo bằng ORM
test thật trên DB copy: tạo SO chọn partner → kiểm franchise+partner cửa hàng+khu vực tự
điền; đổi partner → kiểm tính lại; xoá franchise rồi confirm → phải bị chặn; tạo credit note
từ hoá đơn HCM-01 → kiểm franchise kế thừa và portal HCM-01 thấy, cửa hàng khác không thấy.

Out of scope: không đụng portal template, không đụng tầng UI công nợ (đó là C2/C3).
```

### C2 — Debt: số liệu & business rule

```
Cụm C2: WJ-DEBT-001 (98), WJ-DEBT-004 (101), WJ-DEBT-007 (104), WJ-DEBT-010 (113).
Toàn bộ nằm ở tầng model wujia_portal_debt/models/wujia_portal_debt.py (AbstractModel, không
bảng, không migration). Module -u: wujia_portal_debt.

Chủ dự án đã chốt: đa tệ thì TÁCH TỔNG THEO TỪNG LOẠI TIỀN, không quy đổi tỷ giá.

Việc:
1. WJ-DEBT-001 — _week_payload đang trả state='partial' khi remaining>0 và không quá hạn,
   kể cả lúc paid==0. Dùng CÙNG một rule với _invoice_status: chỉ 'partial' khi
   0 < residual < total. Card tổng quan và dòng hoá đơn phải ra cùng chữ.
2. WJ-DEBT-004 — get_payments đang gọi _currency_symbol() không truyền moves nên luôn ra
   tiền công ty (₫) trong khi payment là USD. Format từng giao dịch theo currency_id của
   chính account.payment; khối Tổng cộng hiện nhiều dòng, mỗi loại tiền một dòng; tuyệt đối
   không cộng số khác currency.
3. WJ-DEBT-007 — residual tuần <= 0 do credit note: hiện state='paid' nhưng dòng credit note
   ra 'Chưa thanh toán' và trang pay in "Số tiền cần chuyển -72.450" + memo "HCM-01 K33 -72450".
   Thêm rule dư có: trạng thái riêng cho residual < 0, credit note không được gắn nhãn nợ,
   controller /portal/debt/pay CHẶN khi amount_due <= 0 (trả về trang công nợ kèm thông báo,
   không render hướng dẫn chuyển khoản), memo không bao giờ chứa số âm.
4. WJ-DEBT-010 — _resolve_week đang fallback options[0] = tuần hiện tại. Đổi mặc định khi
   URL không có ?week=: ưu tiên tuần quá hạn CŨ NHẤT chưa thanh toán, không có thì tuần liền
   trước, không có dữ liệu tuần trước thì mới tuần hiện tại. ?week= hợp lệ vẫn thắng. Thêm
   dòng ngay dưới số tiền: đã thanh toán → "Ngô Gia xác nhận ngày dd/mm/yyyy"; chưa thanh
   toán và có hoá đơn → "Hạn thanh toán: dd/mm/yyyy" (thứ Năm tuần kế tiếp); tuần hiện tại
   chưa có hoá đơn → còn phải trả 0 + "Hạn thanh toán: -". Giữ nguyên dropdown, KHÔNG thêm
   nút tuần trước/sau.

Perf: mặc định tuần mới không được quét N tuần bằng N query — dùng 1 truy vấn gộp
(_read_group theo tuần hoặc đọc field store portal_debt_remaining sẵn có) rồi mới chọn tuần.

Bổ sung test vào wujia_portal_debt/tests/ cho cả 4 nhánh số liệu. Đo thêm bằng Playwright ở
391×844 + 1920×1080. Giữ 100% key/kiểu dict của payload (mobile và PC dùng chung).
```

### C3 — Debt: trang thanh toán & khoảng cách mobile

```
Cụm C3: WJ-DEBT-002 (99), WJ-DEBT-003 (100), WJ-DEBT-005 (102), WJ-DEBT-008 (105),
WJ-DEBT-009 (112). Toàn bộ là template/CSS/JS của wujia_portal_debt.
Chạy SAU C2 (C2 đã đổi payload và đã chặn route pay khi amount_due <= 0).

Chủ dự án đã chốt WJ-DEBT-008: ẨN HẲN khối QR (nhánh OR của BA) ở cả trang mobile và modal
PC — gỡ tiêu đề "Quét QR để chuyển khoản", khung QR giả và nhãn "QR minh họa", chỉ giữ thông
tin chuyển khoản thủ công. KHÔNG sinh VietQR thật (mở issue riêng khi BA chốt tĩnh/động,
câu hỏi CT-055 treo từ S48). Nút "Tải mã QR" no-op cũng gỡ theo.

Việc:
1. WJ-DEBT-002 — get_bank_info khi không có res.partner.bank bật portal đang trả dict rỗng
   nhưng template vẫn dựng đủ 2 nút copy. Cho backend trả cờ trạng thái rõ ràng và template
   rẽ MỘT empty state duy nhất: chỉ thông báo chưa cấu hình, không nút copy, không trường rỗng.
2. WJ-DEBT-003 — template portal_debt_pay (portal_debt.xml ~dòng 621) bọc ".wj-debt
   wj-debt--back", THIẾU d-lg-none và thiếu class shell mobile mà trang /portal/debt overview
   (dòng 68 ".wj-debt--overview d-lg-none") đang có. Đưa trang pay về cùng shell; đo tại
   360/391/500/768 phải hết sidebar và hết cuộn ngang, ≥1200 vẫn đúng shell PC.
3. WJ-DEBT-005 — copyText() trong static/src/js/portal_debt.js đã có fallback execCommand
   nhưng nuốt lỗi im lặng. ĐO TRÊN UAT trước để biết thất bại ở đâu (clipboard API bị chặn vì
   HTTP? execCommand trả false? giá trị rỗng?), rồi mới sửa: phản hồi "Đã sao chép" nhìn thấy
   được, thất bại thì báo lỗi/hướng dẫn, không copy chuỗi rỗng.
4. WJ-DEBT-009 — /portal/debt/payment-history mobile: filter→banner 12px, banner→tiêu đề
   24px, tiêu đề→giao dịch đầu 12px, giữa giao dịch 12px, danh sách→Tổng cộng 12px, padding
   ngang 16px. Desktop giữ nguyên. Dùng token 8/12/16/24, không hex/px rời rạc.

Nhắc rule: KHÔNG sửa _components.css / _pc_components.css dùng chung (8 module) — delta px
scope trong portal_debt.css. Đo bằng Playwright ở 360/391/430/500/768/1440.
```

### C4 — Knowledge

```
Cụm C4: WJ-KNW-001 (90), WJ-KNW-002 (91), WJ-KNW-003 (92), WJ-KNW-004 (93).
Một module: wujia_portal_knowledge. Không migration.

Việc:
1. WJ-KNW-001 (High, lộ thông tin) — controllers/portal.py dòng 65 browse(cat_id) không
   .exists() nên template chạm .name là MissingError, portal in ra
   "wujia.knowledge.category(999999,), User: 2". Validate category_id (và tag_id cùng kiểu)
   trước khi dùng: không tồn tại/inactive → bỏ lọc và chuyển về /portal/knowledge, thông báo
   thân thiện "Danh mục đã chọn không còn khả dụng.", chi tiết chỉ vào server log.
2. WJ-KNW-002 (High) — 6 chỗ in publish_date.strftime() trong views/portal_knowledge.xml
   (dòng 93, 201, 228, 277, 292, 338) ⇒ lệch -7h. TÁI DÙNG fmt_local_dt + qcontext wj_dt của
   wujia_portal_base (§11), inject ở mọi render của controller này. KHÔNG viết helper mới,
   KHÔNG override _prepare_qcontext toàn cục — làm y hệt cách WJ-NOTI-001 đã sửa ở S52.
3. WJ-KNW-003 — search chỉ ('name','ilike',kw). Mở rộng sang summary và phần text của
   content sau khi loại HTML. Giữ nguyên điều kiện is_published_portal/active/hiệu lực.
   Cân nhắc perf 1500 user: nếu ilike trên content là quá nặng thì nói rõ và đề xuất cách
   (field text stripped store+index) trước khi code — hỏi chủ dự án ở fork này.
4. WJ-KNW-004 — detail dòng 76 redirect trần. Thêm thông báo "Bài viết không tồn tại hoặc
   không còn khả dụng." khi bài draft/archived/inactive/chưa tới ngày/hết hạn. Không lộ
   trạng thái nội bộ. Áp cả route slug lẫn route attachment.

Đo: mở /portal/knowledge?category_id=999999 và ?tag_id=999999 → không traceback, không tên
model; đổi publish_date ở backend rồi so giờ list/detail/backend; search bằng chuỗi chỉ có
trong summary và chỉ có trong content; unpublish 1 bài rồi vào thẳng slug → có thông báo.
```

### C5 — Delivery & dữ liệu giao hàng

```
Cụm C5: WJ-DELIVERY-005 (86), WJ-DELIVERY-006 (87), WJ-DELIVERY-007 (88), WJ-HOME-003 (108).
Module: wujia_portal_delivery + wujia_portal_base. Gộp chung vì 005 và HOME-003 là CÙNG một
hàm get_upcoming_batches, còn 006/007 cùng khái niệm "chưa hoàn thành / giờ thực tế".

Việc:
1. WJ-DELIVERY-007 — portal đang in planned_departure ở 4 chỗ
   (wujia_portal_delivery/controllers/portal.py dòng 171, 175, 300, 305). Field
   stock.picking.batch.actual_departure ĐÃ CÓ SẴN (wujia_delivery/models/
   stock_picking_batch.py:130, set ở dòng 246). Quy tắc: có actual thì hiện actual, chưa có
   thì hiện planned, đúng timezone portal (dùng helper tz sẵn có, đừng strftime thẳng).
   Nói rõ trong ledger đây là technical mapping mà BA nhờ Dev xác nhận.
2. WJ-DELIVERY-006 — _chip_counts(Batch, base_domain) ở dòng 146 cố ý bỏ keyword khỏi domain
   đếm nên badge "Tất cả" vẫn 2 khi search ra 1. Cho chip đếm trên ĐÚNG tập đã lọc (kể cả
   search lẫn khoảng ngày); xoá search thì count trở về tập đầy đủ theo current store.
   Giữ 1 _read_group (helper group_counts §11), KHÔNG đếm N lần.
3. WJ-HOME-003 + WJ-DELIVERY-005 — get_upcoming_batches (wujia_portal_base/controllers/
   utils.py:459) đang lọc planned_departure >= đầu hôm nay nhưng KHÔNG loại trạng thái đã
   giao xong/đã huỷ, nên block "Giao hàng sắp tới" hiện BATCH đã giao xong. Loại
   done/cancel, sắp theo lịch dự kiến gần nhất, và bổ sung tổng số đơn chưa giao + danh sách
   đúng các đơn đó (BA yêu cầu ở 005). Dùng cùng rule phân quyền current store với
   /portal/delivery — kiểm lại xem 2 chỗ có đang dùng chung domain không, nếu chưa thì tách
   ra một helper dùng chung.

Lưu ý: block Home hiện chỉ có nhánh mobile (m_upcoming_batches). Nếu BA muốn cả PC thì đó là
fork — hỏi chủ dự án, đừng tự dựng. Số bản ghi mỗi block Home để cụm C7 xử lý, cụm này chỉ
lo ĐÚNG DỮ LIỆU.
```

### C6 — Interaction state toàn portal

```
Cụm C6: WJ-PORTAL-UI-001 (STT 97) — một issue nhưng blast radius là TOÀN BỘ portal.
Module: wujia_portal_layout (_components.css + _pc_components.css).

Yêu cầu BA: card/row/menu/button/chip/tab/icon-button KHÔNG gạch chân chữ (chỉ inline text
link mới giữ underline). Card mặc định nền #FFFFFF viền #E5E7EB. Hover PC: nền #EAF7FD,
viền #28A9DF, shadow nhẹ 0 4px 12px rgba(17,24,39,.08), transition 150ms. Primary button
hover dùng token primary_dark; secondary/icon hover #EAF7FD. Focus-visible: outline 2px theo
token primary_dark + offset 2px, không được xoá focus indicator. Mobile pressed: đổi nền/viền
lúc chạm, không giữ underline sau tap. Dùng token, không hex rải rác.

Bắt buộc trước khi sửa (§5 non-negotiable): grep -rn selector/token trong custom/ để biết
blast radius; hover/focus mới phải KHÔNG làm dịch chuyển layout (dùng box-shadow + border
sẵn có, đừng thêm border làm đổi kích thước). Token màu #EAF7FD/#BFE8F7 đã có từ B4
(--wujia-primary-border-soft) — tái dùng, đừng đẻ token trùng nghĩa.

Đo: sau khi sửa phải chạy hồi quy RỘNG như B4 (286 ô) — tối thiểu toàn bộ 17 route của
PAGE NAMING MATRIX × 2 breakpoint: không trang nào đổi chiều cao/xuống dòng/tràn ngang,
mọi phần tử bấm được không còn text-decoration underline ở default/hover/focus/tap, và
focus-visible vẫn nhìn thấy rõ khi đi bằng Tab.

Đây là nền cho C7 (WJ-HOME-007 nói rõ dùng trạng thái pressed/focus của component chung)
⇒ chạy trước C7.
```

### C7 — Home mobile UI

```
Cụm C7: WJ-HOME-001 (106), WJ-HOME-002 (107), WJ-HOME-006 (109), WJ-HOME-007 (110),
WJ-HOME-008 (111). Module: wujia_portal_base (+ layout CSS nếu cần).
Chạy SAU C5 (dữ liệu giao hàng đã đúng) và SAU C6 (đã có trạng thái tương tác chung).

Việc:
1. WJ-HOME-001 — 4 KPI "Tổng quan cửa hàng" bị cắt nhãn ("ĐƠN HÀ...", "THÔNG ..."). BA chốt:
   ƯU TIÊN giảm font-size/gap để giữ 4 KPI trên MỘT hàng và hiện đủ chữ; chỉ khi 360px vẫn
   không đủ thì chuyển lưới 2×2. Cấm ellipsis. Desktop/tablet không được ảnh hưởng.
2. WJ-HOME-002 (High) — mã đơn ở "Đơn hàng gần đây" bị rút thành "S0…"/"S…". Ưu tiên chiều
   rộng cho mã, đẩy số tiền/trạng thái xuống dòng phụ nếu cần; các đơn phải phân biệt được
   trước khi mở chi tiết; không cuộn ngang.
3. WJ-HOME-006 — _dashboard_values đang lấy recent_orders limit 5, notifications 3,
   returns 3, articles 3. BA muốn MỌI block danh sách preview còn 2 bản ghi mới nhất, giữ
   "Xem tất cả". Sửa limit ở controller (không cắt bằng CSS).
4. WJ-HOME-007 — bỏ hết chevron/mũi tên "xem chi tiết" ở cấp dòng/card của mọi block Home
   (Giao hàng, Đơn hàng, Kiến thức, Đổi trả, Thông báo, Hỗ trợ). Giữ link "Xem tất cả" ở
   tiêu đề block. Dòng/card bấm được thì TOÀN VÙNG là vùng bấm, dùng trạng thái pressed/focus
   của component chung (đã chuẩn hoá ở C6). Bỏ icon không được để lại khoảng trống thừa.
5. WJ-HOME-008 — thống nhất cấu trúc: mỗi block danh sách dùng ĐÚNG MỘT card container, các
   bản ghi là các dòng bên trong, phân cách bằng divider chung. "Yêu cầu đổi trả" hiện tách
   mỗi bản ghi một card → gộp lại. Hành động nhanh và Tổng quan KPI GIỮ layout riêng.

Nhắc: .wj-empty-state--row (S50) và các token Home hiện có phải tái dùng, không đẻ selector
mới khi modifier sẵn có đủ. Đo Playwright 360/391/430/500 + regression PC.
```

### C8 — SectionHeader `CMP-SH-001`

```
Cụm C8: UI-SECTIONHEADER-001 (STT 83). Component dùng chung thứ 3 sau CMP-PG-001 và
CMP-BPH-001. Đây là cụm TO NHẤT — làm y hệt cách B3a/B3b đã làm với PageHeader: dựng
component trước + áp vài route mẫu, đo xong rồi mới nhân ra hết. Nếu 1 phiên không xong thì
tách C8a/C8b, đừng ép.

Spec: tab `UI Component` gid 488333015 dòng 33 (Status BA Confirmed). Tóm tắt:
- PC: title 22/30/800; meta/action 14/20/700; section trước → header 20px; header → content
  12px; cách title ↔ right slot ≥16px.
- Mobile: title 20/28/800; meta/action 14/20/700; spacing 16 trước / 8 sau; cách ≥12px;
  action touch target ≥44×44.
- Màu: title #111827, meta #6B7280, action #28A9DF; compact control chữ #374151 nền #FFFFFF
  viền #E5E7EB.
- Variants: default / meta / action / control — TỐI ĐA MỘT right slot, không đồng thời.
- Title phải là heading THẬT (không <span>), mỗi màn truyền headingLevel phù hợp, không
  hard-code tất cả thành H3. Wrap tối đa 2 dòng, right slot không wrap, thiếu chỗ thì right
  slot xuống dòng căn phải (KHÔNG tự ẩn), không ellipsis nếu không có cách xem đầy đủ.
- Count: hiện cả count = 0, dùng TỪ ĐẦY ĐỦ "5 sản phẩm" (không "5 SP"), cùng domain với danh
  sách và đổi theo filter.
- SectionHeader đầu tiên sau PageHeader/FilterBar không cộng margin-top nếu container đã có
  padding; không cộng đồng thời margin-bottom của header và margin-top của content.
- /portal/delivery "Danh sách chuyến giao" dùng variant meta.

Hiện trạng đã khảo sát: chỉ có 4 class rời (wujia-mhist-listhead ×4, wujia-morder-listhead
×2, wujia-mcart-listhead, wj-pc-order-cardhead), phần còn lại là h2/h3/h4 tự do — nhiều nhất
ở portal_exam.xml (21), portal_home.xml (13), portal_debt.xml (12), portal_franchise_
information.xml (10). Bước đầu tiên của phiên: liệt kê ĐỦ heading của mọi trang portal và
phân loại PageHeader / SectionHeader / CardHeader — spec nói rõ heading NẰM TRONG card thì
là CardHeader, KHÔNG phải SectionHeader.

Ràng buộc: đặt component ở wujia_portal_layout cạnh wj_page_header.xml, cùng pattern t-set
props. Học bài học B3a: nếu chỗ nào Meta là slot swap của wj_ajax_list thì slot phải render
markup thô, KHÔNG bọc thêm element.
```

### C9 — Order / History nhỏ

```
Cụm C9: RESP-MOB-ORDER-002 (94), WJ-ORD-026 (95), WJ-PH-008 (96).
Module: wujia_portal_sale + wujia_portal_purchase_history. Ba lỗi độc lập, đều nhỏ.

1. WJ-ORD-026 (High) — /portal/order/cart ở 391×844: nút "Gửi đơn đặt hàng" y≈722–768 bị
   Footer Action Bar (bắt đầu y≈761) che ~7px. Thêm khoảng an toàn dưới nội dung giỏ theo
   đúng chiều cao footer (dùng biến/token chiều cao footer sẵn có, đừng gõ số cứng) hoặc đưa
   CTA sticky lên trên footer. Không được sinh cuộn ngang, không che khối tổng tiền.
   Đo ở 360 và 391, kể cả khi giỏ có nhiều dòng và có ghi chú dài.
2. RESP-MOB-ORDER-002 (Low) — tên sản phẩm trên card mobile /portal/order bị co hẹp, chưa
   dùng hết chiều rộng card. Cho vùng tên chiếm hết chiều rộng khả dụng trước khi xuống
   dòng/cắt; tối đa 2 dòng; không chồng giá, ĐVT, nút giỏ; không tràn ở 360/391. BA đã chấp
   nhận card cao động 61/82px của RESP-MOB-ORDER-001 nên chiều cao thay đổi là hợp lệ.
3. WJ-PH-008 — wujia_portal_purchase_history/controllers/portal.py:15 PAGE_SIZE = 20, source
   PC v1.5 quy định mặc định 10. Đổi về 10 và kiểm luôn nhánh dòng 299
   (page_size if page_size != PAGE_SIZE else '') để querystring không đảo ngược ý nghĩa sau
   khi đổi hằng số. Giữ page_size khi search/filter/chuyển trang; validate giá trị không hợp
   lệ ở controller; không trùng/thiếu đơn giữa các trang.
```

### C10 — Exam + Ngôn ngữ

```
Cụm C10: WJ-EXAM-007 (84), WJ-LANG-001 (114). Hai chỗ hard-code, khác module.

1. WJ-EXAM-007 — views/portal_exam.xml:265 ghi cứng "Mỗi phiếu được đăng ký tối đa 4 người"
   trong khi giới hạn thật là session/course.max_participants_per_registration (controller đã
   trả key max_per_reg; JS PC portal_exam_pc.js:198 và mobile portal_exam_wizard.js:144 lại
   fallback "|| 4"). Dùng MỘT nguồn duy nhất cho: câu hướng dẫn, ô "Giới hạn mỗi phiếu 0/N",
   chặn nút thêm người, và validate lại ở server khi gửi phiếu. Bỏ mọi số 4/2 hard-code.
   Ghi chú BA: chưa xác định giới hạn đúng là 2 hay 4 — Dev đối chiếu cấu hình nghiệp vụ
   hiện tại và nói rõ trong ledger giá trị nào đang là nguồn. KHÔNG tạo/gửi phiếu thật khi test.
2. WJ-LANG-001 — bộ chọn ngôn ngữ hard-code 2 thẻ <a> ở wujia_portal_layout/views/
   layouts.xml:78-82 (PC) và mobile_header.xml:42-46 (mobile), nên cài thêm tiếng Thái không
   hiện. Lấy động danh sách ngôn ngữ đang bật (đọc source trước để chọn nguồn đúng: website
   của portal hay res.lang active — BA nói "cấu hình website", xác nhận lại rồi mới code),
   render cờ/tên đúng, giữ route /portal/set-lang sẵn có
   (wujia_portal_layout/controllers/portal.py:211) và kiểm nó có whitelist cứng 2 mã không.
   Phải chạy cả ở màn đăng nhập. Giữ ngôn ngữ sau điều hướng và sau đăng nhập.
   Lưu ý §5 tồn S44: portal cố ý pin nhãn tiếng Việt ở 3 seam controller — kiểm xem việc bật
   thêm ngôn ngữ có làm 3 chỗ đó kẹt tiếng Việt không, nếu có thì ghi LIMIT chứ đừng tự gỡ.
```

---

---

## Chuẩn nghiệm thu — áp cho MỌI cụm (§13)

1. Build sạch `-u <mod> --stop-after-init` trên **DB copy cô lập** (port riêng, KHÔNG đụng
   `wujia_tea_19`/8019): RC=0, 0 ERROR/Traceback. Kèm `wujia_sale` nếu `-u` kéo theo
   `wujia_portal_return` (local chưa chạy pre-migrate S52).
2. Unit test module liên quan `--test-enable --test-tags <tag>`: 0 failed / 0 error.
3. **Đo bằng máy, không nhìn ảnh** — `scripts/ba_spec/qa_visual_check.py` (Playwright +
   chromium có sẵn env `odoo`), 391×844 và 1920×1080 (thêm 360/430/500/768 cho issue
   responsive). Gotcha §12: `wait_until="load"`, login submit bằng Enter, set sẵn cookie
   `wujia_active_franchise_id` kẻo overlay che làm assert pass rỗng.
4. Bảng đối chiếu `Yêu cầu | Đo được | Pass/Fail` theo **từng gạch đầu dòng** cột
   "Kết quả mong muốn" của chính issue đó; ngưỡng **≥90% Pass**; dòng Fail phải sửa hoặc
   ghi LIMIT tường minh.
5. Regression ≥3 trang khác × 2 viewport: 200, overflow ngang 0, 0 JS pageerror.
   Riêng **C6 và C8** hồi quy rộng như B4 (17 route × 2 breakpoint).
6. Harness sai thì sửa harness (L7/L9) — chân lý là spec BA, không phải kỳ vọng gõ tay.
7. Đạt rồi mới thêm entry `docs/qa-issue-ledger.yaml` → `cd scripts/ba_spec &&
   python3 qa_sync.py --dry-run` → `--apply` (`Ready for Retest`, **Dev KHÔNG tự Done**)
   → verify lại bằng `export?format=csv` (không dùng gviz).
8. Cuối mỗi cụm: `/wujia-end-sprint` (chapter `.tex` + PDF + compact summary §4/§5/§13).
