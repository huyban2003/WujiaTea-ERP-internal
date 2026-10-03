# G5 — Bảng nghiệm thu: hộp xác nhận gửi đơn (148) + tìm/lọc gửi lại được (147)

**Issue:**
- `WJ-ORD-028` (148, High, POR-018): hộp xác nhận trước khi gửi đơn.
- `WJ-ORD-027` (147, Medium, POR-015): tìm/lọc giữ query cũ.

BA mở cả hai ngày 29/09 (exploratory UAT, đơn S00075). Làm ngày 30/09/2026 (Mac), gộp một commit.

**Module `-u`:**
- `wujia_portal_layout` 19.0.59.2.0
- `wujia_portal_base` 19.0.7.33.0
- `wujia_portal_sale` 19.0.4.27.0

**Chủ dự án chốt:**
- 148 **không đổi schema**. Khoá nút + overlay cho cả PC lẫn mobile, server giữ khoá NOWAIT `_lock_lines`.
- Lần gửi lặp gặp `CART_EMPTY` mà có đơn draft/sent vừa tạo (≤ 2 phút, đúng cửa hàng + đúng user) thì dẫn về
  đơn đó.
- 147: tái hiện trước rồi sửa ở gốc.

**Cách đo:**
- DB `wujia_g5s` = copy `wujia_g3s` (đã có H150/151). Server 8055, `--log-handler=werkzeug:INFO`.
- User `dung.multi`, cửa hàng HCM-01.
- Số "trước" đo trên **cùng DB, cùng giỏ**, bằng code HEAD `d35ebac` (git worktree + `-u` 3 module), rồi `-u` lại
  bằng code G5.

## 1. 148 — theo "Kết quả mong muốn"

| # | Kết quả mong muốn BA | Đo | Đạt |
|---|---|---|---|
| 1 | Bấm "Gửi đơn đặt hàng" → **chưa tạo SO**, hiện modal tóm tắt | `wj_order_confirm.py` 4 kịch bản (PC giỏ 1440 · PC panel trang Đặt hàng 1280 · mobile giỏ 390 · 360): mở hộp → **0 POST** `/portal/order/submit`, **0 SO mới** (đếm Postgres). `wj_order_confirm_probe.py` 8 khổ: 0 request gửi đơn. Test `test_open_modal_creates_nothing` | ✅ |
| 2 | Hủy → đóng modal, **giữ nguyên giỏ**, không tạo dữ liệu | 3 cách đóng (nút Hủy · Esc · bấm nền) × 4 kịch bản: hộp đóng, 0 POST, số SO + số dòng giỏ không đổi, focus về lại nút mở | ✅ |
| 3 | Xác nhận → **đúng 1 SO**, sang màn kết quả, giỏ rỗng | 4/4 kịch bản: 1 POST, +1 SO (SO#5264–5267), giỏ 0 dòng. Mobile về `/portal/order/submitted/<id>`, PC về `/portal/purchase-history/<id>`. Ghi chú 2 dòng lưu đúng vào `portal_note` | ✅ |
| 4 | Double-click / refresh **không tạo đơn trùng** | Double-click Xác nhận: 1 POST, 1 SO. F5 màn kết quả: 0 SO mới. Gửi lặp khi giỏ đã rỗng (Back rồi gửi lại, hoặc request trùng tới sau): **về đúng đơn vừa tạo**, không báo "giỏ trống" (HttpCase PC + mobile). `cart_race.py --rounds 5`: 2 phiên cùng gửi → mỗi vòng đúng 1 đơn, `nowait_hits` 5 | ✅ |
| 5 | Modal tối thiểu: số mặt hàng · tổng số lượng · tổng thanh toán · cửa hàng · ghi chú | Đủ 5 dòng. Số lấy từ `data-oc-*` của chính form gửi đơn, render cùng panel giỏ nên luôn khớp giỏ hiện tại (test so từng ô với form). Ghi chú đọc từ ô đang gõ, giữ xuống dòng. Tổng thanh toán nổi bật 18/700 màu primary | ✅ |
| 6 | 2 action **Hủy \| Xác nhận gửi đơn** | Đúng thứ tự, đúng chữ. Hủy = secondary, Xác nhận = primary (test arch) | ✅ |

**Ngoài AC, đã làm:**
- A11y: `role=dialog` + `aria-modal` + tiêu đề/mô tả. Focus mặc định ở **Hủy**, nên Enter bấm vội không tạo đơn.
  Tab/Shift+Tab không thoát khỏi hộp. Esc = Hủy (bị khoá khi đang gửi).
- Giỏ đổi trong lúc hộp đang mở (user khác cùng cửa hàng): bấm Xác nhận chỉ nạp lại số và hiện "Giỏ hàng vừa thay
  đổi…", không gửi.
- **Lỗi mới phát hiện, đã sửa:** nút "Gửi đơn đặt hàng" **mobile** không gửi POST nào.
  - Nguyên nhân: listener overlay cũ tự kiểm cờ `wjSubmitting`, nhưng khoá chung CMP-BTN-001 (E6a) đã cắm cờ đó
    trước, nên lần gửi đầu tự chặn chính nó.
  - UAT nhiều khả năng cũng dính lỗi này. Chưa thử trên UAT để tránh tạo đơn thật.

## 2. 148 — hộp ở 8 khổ (`wj_order_confirm_probe.py`, chỉ mở rồi Hủy)

| Khổ | Trang | Panel (x0, y0, x1, y1) | Nút cao | Focus đầu | Tab giữ trong hộp | Hủy → đóng + focus về | Đạt |
|---|---|---|---|---|---|---|---|
| 360×800 | giỏ mobile | 16, 201, 344, 599 | 44 / 44 | Hủy | ✅ | ✅ | ✅ |
| 390×844 | giỏ mobile | 16, 223, 374, 621 | 44 / 44 | Hủy | ✅ | ✅ | ✅ |
| 430×932 | giỏ mobile | 16, 278, 414, 654 | 44 / 44 | Hủy | ✅ | ✅ | ✅ |
| 1440×900 | giỏ PC | 510, 258, 930, 642 | 40 / 40 | Hủy | ✅ | ✅ | ✅ |
| 1440×900 | Đặt hàng (panel) | 510, 258, 930, 642 | 40 / 40 | Hủy | ✅ | ✅ | ✅ |
| 1024×768 | giỏ PC | 302, 192, 722, 576 | 40 / 40 | Hủy | ✅ | ✅ | ✅ |
| 992×768 | giỏ PC | 286, 192, 706, 576 | 40 / 40 | Hủy | ✅ | ✅ | ✅ |
| 992×768 | Đặt hàng (panel) | 286, 192, 706, 576 | 40 / 40 | Hủy | ✅ | ✅ | ✅ |

Mobile: panel cách mép 16 hai bên, 2 nút chia đôi, cao 44. PC: panel 420 căn giữa. 0 tràn ngang ở cả 8 khổ.
Ảnh: `scratchpad/g5/probe/`, `g5/shots/` (không đưa vào repo).

## 3. 147 — theo "Kết quả mong muốn"

**Gốc lỗi:**
- Khoá chống bấm lặp CMP-BTN-001 (`wujia_button_loading.js`, E6a 20/09) cắm cờ `wjSubmitting` lên form khi
  submit, và **chỉ gỡ khi trang tải lại**.
- `wj_ajax_list.js` lọc không reload nên cờ dính mãi: mọi form lọc chỉ gửi được **một lần**, lần sau bị chặn im
  và danh sách giữ kết quả cũ.
- Lỗi này dính **cả 11 màn danh sách**, không riêng trang Đặt hàng.

**Sửa:**
- `wj_ajax_list` bắn `wj:form:release` khi swap xong, và cả khi lượt đó bị lượt sau huỷ ngang.
- Khoá chung nghe sự kiện này để gỡ cờ.
- Phụ: ô ẩn `category_id` của form tìm mobile nay **luôn render**. Trước đây nó chỉ có khi trang mở kèm danh mục,
  nên chọn chip rồi tìm thì mất danh mục.

| # | Kết quả mong muốn BA | Đo | Đạt |
|---|---|---|---|
| 1 | Đang có kết quả Matcha, đổi keyword sang chuỗi không tồn tại → URL/query dùng keyword mới + trạng thái **không có kết quả** | Kịch bản BA ở PC 1440 và mobile 390: URL `?keyword=<mới>`, fragment request đúng keyword, danh sách hiện "Không có sản phẩm phù hợp". Trước sửa: URL + danh sách giữ Matcha | ✅ |
| 2 | Đổi danh mục → request + danh sách dùng **đúng danh mục mới** | Chip danh mục → URL có `category_id` mới. Chip rồi tìm keyword: vẫn giữ danh mục ở cả PC và mobile. Test `test_mobile_search_always_has_category` | ✅ |
| 3 | Desktop = mobile; **Enter = click**; không giữ kết quả cũ | `wj_resubmit.py`: 11 màn × PC 1440 / mobile 390, mỗi màn gửi form lọc 3 lần liên tiếp với 3 giá trị khác nhau. **Trước 0/19 → sau 19/19** lần nào cũng ra request + URL đúng giá trị mới (3 cặp không có form lọc: không áp dụng). Enter và click đi cùng một listener `submit` | ✅ |
| 4 | Reset về trang 1; giữ điều kiện khi phân trang và Back/Forward | Submit dựng URL chỉ từ field của form, không mang `page` cũ ⇒ về trang 1. Back/Forward: popstate tải lại đúng URL và đồng bộ ô lọc (đo PC + mobile). Pager: link do server dựng kèm điều kiện, hành vi E3 không đổi (`wj_ajax_list` chỉ thêm bước gỡ cờ) | ✅ |

## 4. Kênh bên kia + hiệu năng (trước = HEAD `d35ebac`, sau = G5; cùng DB, cùng giỏ)

- **Số query:** `wj_density` 27 route. Lấy min mỗi route trong lượt đo.
  - **Δ0 ở cả 27 route.** `/portal/order` 38 → 38, `/portal/order/cart` 31 → 31, `/portal/purchase-history` 21 → 21.
  - `/portal/login` 5 → 23 là request nguội đầu tiên sau khi bật lại server, không phải trang của G5.
  - Nhánh "gửi lặp" thêm **1 search có `limit=1`**, chỉ chạy khi submit gặp `CART_EMPTY`.
- **Mobile:** 27 route × 360/390/430: PageHeader · SectionHeader · BottomNav · khoảng cuối trang đều **Δ0**.
- **PC:** 27 route × 1440/1024/992.
  - 69/81 ảnh trùng md5, **kể cả `/portal/order` và `/portal/order/cart`**, vì hộp đang ẩn không làm đổi pixel nào.
  - 12 ảnh lệch md5 nhưng cao trang không đổi, ở các trang G5 không chạm template/CSS: `/portal`,
    `/portal/reports/orders`, `/portal/knowledge` (+ bài viết), `/portal/debt/payment-history` @1440.
  - Chạy lại **hai lần trên cùng code G5**, `/portal` và `/portal/reports/orders` vẫn lệch. Vậy đây là nhiễu dữ
    liệu: đồng hồ khung giờ, id ngẫu nhiên của apexcharts. Knowledge lệch vì `view_count` tăng do chính lượt đo.
    Cùng loại nhiễu đã ghi ở G3.

## 5. Test + kiểm tra

- **Test mới:** `wujia_portal_sale/tests/test_g5_submit_confirm.py`, 13 test, tag `wujia_g5`.
  - Kế thừa fixture F6, không chạy lại test F6.
  - Nhóm server: gửi lặp về đúng đơn (PC + mobile); không có đơn gần đây thì vẫn `CART_EMPTY`; không nhận đơn
    của user khác, đơn > 2 phút, đơn đã xác nhận; nhiều đơn thì lấy đơn mới nhất.
  - Nhóm markup: hộp, nút, `data-oc-*` ở giỏ + trang Đặt hàng; ô `category_id` mobile.
  - Nhóm JS tĩnh: `wj:form:release` hai phía; `portal_order.js` không tự kiểm cờ.
- **Mutation 12/12 đỏ:**
  - bỏ nhánh redirect;
  - bỏ lọc user / cửa sổ 2 phút / lọc trạng thái;
  - lấy đơn cũ nhất;
  - nút PC mất móc;
  - trang Đặt hàng thiếu hộp;
  - `category_id` render có điều kiện;
  - không gỡ cờ khi bị huỷ ngang;
  - khoá chung không nghe sự kiện;
  - JS tự chặn theo cờ;
  - thiếu `store_name`.
- **Test E6 phải sửa theo:** `test_scan_e6_button.MOC_JS` ghim móc JS của giỏ. Móc cũ `wujia-mcart-submit` đổi
  thành `data-wj-confirm-open` / `data-wj-confirm-form` ở cả `portal_order_cart.xml` và `pc_cart_panel.xml`.
  Lớp cũ vẫn ở view làm móc đo QA.
- `-u` 3 module + test 3 module: **612/0/0**.
- Suite 20 module (`-u` cả 20): 1006 test.
  - 1 FAIL là móc E6 ở trên, đã sửa, chạy lại 3 module 612/0/0.
  - 1 error `setUpClass` fixture `wujia_sale` (`TestWujiaSupplyDemandReport`) có sẵn từ trước, không liên quan.
- `check_layers`: 0 vi phạm tầng mới (R7 2 dòng `wujia_franchise` có sẵn, code anh Thái).

## 6. LIMIT

- **Back + gửi lại bằng trình duyệt:** không dựng được, vì Back tải lại trang từ server (không từ BFCache) nên giỏ
  đã rỗng và nút gửi ẩn. Nhánh server (giỏ rỗng + đơn vừa tạo ⇒ về đơn đó) khoá bằng HttpCase.
- **Không có JS:** nút vẫn là `type=submit` nên form gửi thẳng, **không qua hộp xác nhận**. Chọn vậy để không mất
  khả năng gửi đơn; chống trùng vẫn do server lo.
- **Thông báo "Giỏ hàng vừa thay đổi":** có code và test markup, chưa đo bằng 2 trình duyệt song song.
- **UAT:** chỉ mở hộp rồi Hủy (`wj_order_confirm_probe.py` chặn mọi request gửi đơn). **Không bấm Xác nhận** vì
  sẽ tạo đơn thật. Luồng tạo đơn chỉ đo ở local.
- **Cửa sổ 2 phút:** gửi lặp sau hơn 2 phút mà giỏ đã rỗng thì báo "Giỏ hàng chưa có sản phẩm" như cũ. Đơn vẫn
  không trùng.

**Tổng:** 148 6/6, 147 4/4 → **100% "Kết quả mong muốn"** (ngưỡng ≥ 90%).
