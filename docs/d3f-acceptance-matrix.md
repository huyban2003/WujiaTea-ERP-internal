# D3f — nghiệm thu `CMP-CH-001` cho `wujia_portal_debt` + `wujia_portal_inspection`

Issue: `UI-CARDHEADER-001` (STT 125). Nhánh `dev/2026-09-04-d3f`, 5 commit:
`dc1fc26` (lượt 1) · `0e4dce0` (lượt 2) · `c409225` (3a) · `20b122e` (3b) · `b54de2a` (3c + test).

> **Điều kiện chặn của cụm này là ẢNH CHỤP, không phải bảng số.** D3c/D3d/D3e đều Pass sạch mọi
> số đo mà giao diện vẫn vỡ. Mọi mục dưới đây đều có ảnh trước/sau đối chiếu.

## 1. Khối lượng thật

| | |
|---|---:|
| Kiểm kê chạy thô | 53 |
| Sau khi **vá bug đếm của harness** (thiếu `wj_card_header` trong danh sách skip) | **40** |
| Trừ §3 (loại tay) + §6 (chờ BA) | **12 actionable** |
| Loại vì sai component (`debt:40`, `detail:176`, `success:78`) | 3 |
| **Đã migrate** | **9 + 1 phát sinh = 10** |
| Kiểm kê sau khi làm | 40 → **31** |

Chỗ phát sinh: bản **mobile** của head khối `t-foreach sections`
(`portal_inspection_detail_templates.xml:450`) — harness không bắt vì tổ tiên không qua được phép
thử "là card". Lòi ra nhờ guard `_sec_sev`. Không migrate thì PC và mobile lệch nhau.

## 2. Từng chỗ — trước ⇢ sau

| # | Chỗ | Trước | Sau | Phán quyết |
|---|---|---|---|---|
| 1 | `debt:373` "Hóa đơn trong tuần" | `h3.wj-pc-card__title` 22px, gap 18 | `h3.wj-card-header__title` 18px/24, gap 12 | hội tụ |
| 2 | `debt:610` "Các khoản thanh toán" | như trên | như trên | hội tụ |
| 3 | `debt:736` nhãn hint | `span` 11.5px amber | `h3`, **11.5px amber y nguyên** | thiết kế → rule scope |
| 4 | `debt:164` nhãn card tổng S43 | `span` 11px muted | `h3`, **11px muted y nguyên** | thiết kế → rule scope |
| 5 | `detail:93` "Kết quả đánh giá chi tiết" | `h2` 24px + 2 nút | `h2` 18px, nút vào `ch_control`, **giữ id** | hội tụ |
| 6 | `detail:108` "Phân bổ kết quả" | `h3.h6` | `h3` `.875rem` | thiết kế → rule scope |
| 7 | `detail:137` head section PC | `h3` 15px + sub + badge | `h3` **15px y nguyên**, badge vào `ch_meta` | thiết kế → rule scope |
| 8 | `detail:450` head section **mobile** | `h3` .95rem xanh | **y nguyên** | thiết kế → rule scope |
| 9 | `remediation:43` "Cập nhật báo cáo khắc phục" | `h2` 24px | `h2` 18px | hội tụ |
| 10 | `remediation:70` tiêu đề tiêu chí | `h3` 14px | `h3` **14px y nguyên** | thiết kế → rule scope |

## 3. Số đo A/B (2 DB clone, 2 server: A `:8070` mã gốc — B `:8071` mã mới)

| Bộ đo | Kết quả |
|---|---|
| **S43 — card tổng 359×142, cả 5 biến thể** (`d3f_s43.py`) | card 359×142 · head 15px · badge `absolute` phải 0 / trên 2 / cao 26 · số tiền y=28 cỡ 25px · nhãn 11px/700/.02em muted — **trùng tuyệt đối 6/6 bộ số**. Khác biệt duy nhất: `SPAN` → `H3` |
| **Head section PC** (`d3f_sechead.py`) | title 15px/18px/700 y nguyên · nền `rgb(185,28,28)` y nguyên · **badge vẫn cách mép phải đúng 14px** (bẫy badge trôi D3c). Hội tụ: subtitle 13.125→14px, màu `rgb(33,37,41)`→`rgb(17,24,39)`, hộp 64.5→62px |
| **Head section mobile** (`d3f_sechead_m.py`) | nền, badge, `.95rem`/`.82rem`, `#0284c7` y nguyên; hộp 58.9→57.4px |
| **Hai chỗ lượt 2** (`d3f_l2check.py`) | hộp 52.8px và 137.9px, font/lh/weight/màu — **y hệt từng giá trị** |
| **Hình học C3/S43** (probe `GEO` của `d3f_measure.py`) | 16 sai khác, **tất cả đều là chủ đích**: 3 class cũ biến mất (đã migrate), card PC cao 252.4→244 (title 22→18), 2 khối tụt/lên theo. **Không** đổi width, padding, position, color ở đâu |
| **Hồi quy D3c** (4 route × 4 viewport) | **0 lệch** (chỉ khác trường `url` vì đổi cổng) |
| **Hồi quy D3d** (9 route exam) | **0 lệch** |
| **Hồi quy D3e** (5 route) | **0 lệch** |
| Route / JS / tràn ngang | mọi route 200 · **0 lỗi JS** · `overflowX` 0 · số bản ghi không đổi · `textDigest` không đổi |

## 4. Ảnh chụp — điều kiện chặn

7 route × {1920, 1440, 390, 360}, so **before / after** từng lượt. Kết quả pixel-diff:

- `/portal/debt` @390, `/portal/debt/pay` @390, `/portal/inspection` @1920 — **khớp từng pixel**.
- `/portal/debt` @1920, `/portal/debt/payment-history` @1920, `/portal/inspection/remediation/*` —
  chỉ khác đúng vùng tiêu đề (22/24 → 18px), đã soi mắt.
- `/portal/inspection/detail/*` @1920 và @390 — soi mắt cả hai nhánh nghiêm trọng / thường.

**Ảnh còn bắt được 1 bug bố cục có sẵn và D3f sửa miễn phí:** trang khắc phục, dòng phụ
"Vui lòng cung cấp hình ảnh…" bị `justify-content: space-between` của `.wj-pc-card__head` **văng
sang mép phải card**. Vào component thì nó về đúng dưới tiêu đề.

**Và bắt được 1 bug do chính D3f gây ra** (số đo bắt, không phải mắt): tiêu đề nhánh nghiêm trọng
bản mobile ra **màu xanh trên nền đỏ** — rule severe (0,3,0) thua rule màu xanh (0,4,0)`!important`
ngay trên nó. Đã nâng lên (0,5,0) và có test giữ.

## 5. Test

`custom/wujia_portal_layout/tests/test_d3_card_header.py` → lớp mới **`TestCardHeaderD3f`**
(10 test, **không đẻ file mới**). Bộ `wujia_card_header_d3`: **0 failed / 44 test**.

Guard bám **cả khai báo** bằng `assertRegex` chứ không `assertIn` chuỗi con (bài học D3e §10):
đếm call site từng view · `div.wj-debt-summary__head` còn nguyên (2 rule hình học Figma bám vào
nó) · 4 rule scope đúng cỡ đúng đặc hiệu · id `pc_tab_btn_*` còn khớp JS · cờ severe tính đúng
một lần mỗi vòng lặp.

**Mutation cố ý 2 lần** — đổi tên selector severe; đổi `11px` → `18px`. Mỗi lần **đỏ đúng 1 test**,
đã khôi phục.

## 6. LIMIT

1. **5 biến thể S43 đo qua CSS** (nhân bản DOM rồi đổi lớp trạng thái), không seed đủ 5 trạng thái
   dữ liệu. Hợp lệ vì D3f không đụng nhánh QWeb nào của 5 trạng thái — chúng chỉ đổi các dòng
   `<p>` meta bên dưới đầu card.
2. **Chưa deploy UAT.** Số đo/ảnh trên DB clone cục bộ.
3. `UI-CARDHEADER-001` **chưa 100%** (95/105, còn 4 chỗ chờ BA + các chỗ §3) ⇒ **chưa chạy
   `qa_sync.py`**, ledger giữ dạng comment.
4. 2 test `test_c10_lang` fail trên DB thử nghiệm là **lỗi có sẵn, không liên quan D3f** (DB clone
   thiếu ngôn ngữ `th_TH`); chúng không nằm trong tag `wujia_card_header_d3`.

## 7. Việc bàn giao

- Phiên kế: **review lại toàn cụm D3 bằng ảnh chụp** (chủ dự án chốt 2026-09-04).
- Một lượt hỏi BA gộp: `franchise_information:40/49` · `exam:375` parthead · `exam:769` ·
  `inspection_list:34` · `debt:688`.
- Badge "Đã Gửi" mờ ở `/portal/return/<id>` PC — **tách issue riêng** (chủ dự án chốt), gốc rễ đã
  truy xong: `.state-badge` khai SAU `.wujia-badge-*` ở cùng `_components.css`, cùng đặc hiệu
  (0,1,0) nên nuốt màu ngữ nghĩa. Ảnh hưởng `portal_return_detail.xml:18` +
  `portal_info_request_detail.xml:23`. Sửa = bỏ `badge state-badge`, dùng `wujia-badge` như chính
  dòng 243 cùng file đã làm. Thuộc `CMP-SB-001` — BA **chưa có spec**, không tự đoán px/màu.
