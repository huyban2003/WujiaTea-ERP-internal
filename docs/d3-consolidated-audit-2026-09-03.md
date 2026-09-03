# D3 — audit hợp nhất D3a+D3b+D3c (2026-09-03)

Phiên này KHÔNG code thêm call site nào (D3d/e/f để phiên sau). Việc làm: (1) phát hiện
D3c bị bỏ sót bước merge+push, (2) audit code + regression cho toàn bộ 47/103 call site
đã migrate, (3) đo lại chỉ-đọc trên chính UAT sau khi chủ dự án deploy.

## 1. Phát hiện: D3c chưa từng lên UAT (không phải deploy hỏng — thiếu merge+push)

Kiểm phiên bản module qua XML-RPC (đọc-chỉ) lúc đầu phiên: `wujia_portal_base` =
`19.0.7.6.0`, `wujia_portal_support` = `19.0.3.13.0`, `wujia_portal_delivery` =
`19.0.3.7.0` trên UAT — đúng bằng số của **D3b**, không phải D3c (`19.0.7.7.0` /
`19.0.3.14.0` / `19.0.3.8.1` trên đĩa). `git log --oneline -1 origin/main` = `aef14e1`
(merge D3b colorfix); commit D3c `b6cfcbe` chỉ có trên nhánh cục bộ `dev/2026-09-02-d3c`,
chưa từng `merge`/`push`. Mọi module khác (`wujia_sale`, `wujia_franchise`,
`wujia_portal_return`) khớp tuyệt đối giữa UAT và đĩa ⇒ không phải deploy lỗi, chỉ là
bước cuối của phiên D3c (02/09) bị bỏ sót. `git merge-base --is-ancestor main
dev/2026-09-02-d3c` xác nhận **fast-forward sạch, 0 rủi ro conflict** trước khi merge.

Đã xử lý: `git merge --ff-only dev/2026-09-02-d3c` vào `main` + `git push origin main`
(`b6cfcbe` nay là tip của `origin/main`). Chủ dự án deploy `-u
wujia_portal_layout,wujia_portal_base,wujia_portal_support,wujia_portal_delivery` ngay
trong phiên — xác nhận lại qua XML-RPC: cả 3 module lên đúng version D3c.

## 2. Audit code — 2 kiểu lỗi đã từng dính, quét lại trên cả 47 call site

**(a) Tràn `.wj-card-header__lead{flex:1 1 auto}`** (bug D3c gốc: badge trạng thái
`/portal/delivery/<id>` trôi ra mép vì component tự khai `width:100%` và lead tự nở hết
cỡ). Root cause thật: `.wj-pc-order-head{display:flex; justify-content:space-between}`
không khai `flex-basis` cho con ⇒ `width:100%` của component "kéo" cả div cha giành hết
chỗ, đẩy sibling `.wj-pc-dlv-head-kv` ra ngoài. Đã fix scope tại
`portal_delivery.css:277`.

Quét lại **13/13 call site còn lại dùng slot `ch_control`/`ch_meta`** (trailing có nội
dung, rủi ro cao nhất) theo đúng cơ chế: chỉ tái diễn khi CardHeader nằm trong một hàng
flex/grid có sibling giành chỗ. Kết quả: **không có chỗ nào khác lặp lại cấu trúc này**
— `.wj-pc-card`/`.wj-pc-cart` là `display:block` (không cạnh tranh ngang), `.wujia-
content-card` là `flex-direction:column` (xếp dọc), `.wj-rep-pcrow` dùng CSS Grid với
cột khai cứng `minmax(0,744fr)`/`minmax(0,378fr)` (không phải flex tự co giãn) nên
`width:100%` của component không đẩy được sibling. Chỉ `wj-pc-order-head` (dùng chung bởi
delivery ĐÃ migrate và `portal_history.xml` CHƯA migrate, để dành D3e) có cấu trúc này.

**(b) Màu bị theme đè** (`:where(.card:not([data-vxml])) .card-body:not(…) h4{color:
inherit}` — specificity (0,4,1) do `:not()` mang độ đặc hiệu của tham số). Fix đã lên
**component** (`_components.css:3189`, `!important` trên `.wj-card-header__title`), tức
tự động phủ MỌI call site kể cả tương lai — không cần quét từng chỗ. Xác nhận qua đo UAT
§4: `rgb(17, 24, 39)` đúng 74/74.

**(c) Rò CSS ra ngoài scope** (bài học C6/D2 — `a:hover`/`.content-wrapper` từng leak
toàn cục). `git diff` D3a→D3c chỉ đụng 4 file CSS, không file nào là `_wujia_theme.css`
hay `_variables.css`; mọi rule mới đều khoá bằng lớp `.wj-card-header*` hoặc combinator
cha-con cụ thể (`.wujia-mknow-article > .wj-card-header`, `.wujia-mnoti-detail-card >
.wj-card-header`) — không có selector global mới.

**Kết luận (a)+(b)+(c): không có regression tiềm ẩn nào chưa lộ ra bằng số đo.**

## 3. Regression test — 183 test, 0 failed/0 error

DB copy `wujia_tea_d3c` (đã ở đúng state D3c từ phiên trước) upgrade lại `main` mới
merge, `--db-filter` khớp tên DB (bẫy dbfilter S48 tái hiện lúc đầu — 10 test
`wujia_portal_knowledge` "fail" hoá ra là bị đá về trang login vì `dbfilter` config chỉ
cho `wujia_tea_19`, không phải lỗi code; sửa bằng `--db-filter='^wujia_tea_d3c$'` thì
sạch):

- `wujia_portal_layout` + `wujia_portal_base` + `wujia_portal_support` +
  `wujia_portal_delivery`: **72 test, 0 failed/0 error**.
- `wujia_portal_knowledge` + `wujia_portal_notification` + `wujia_portal_sale` +
  `wujia_portal_info_request` + `wujia_portal_return` + `wujia_portal_report`: **111
  test, 0 failed/0 error**.

## 4. Đo lại chỉ-đọc trên chính UAT sau deploy (L14/L10)

`scratchpad/d3c_uat_verify.py` — gộp nguyên 13 route D3a+D3b (regression) + 6 route mới
D3c (`/portal/support`, `/portal/support/new`, `/portal/support/16`,
`/portal/delivery/2`, `/portal/franchise-information` PC+mobile), 3 breakpoint
(1440/390/360), thêm 1 kiểm tra mới `trailOverflowsCard` (trailing có trôi ra ngoài card
cha không — đúng bài học §2a).

**Kết quả: 74/74 header đạt toàn bộ số BA** (cỡ chữ/line-height theo variant, weight 700,
màu `rgb(17,24,39)`, font Inter, padding 0, nhịp margin đúng compact/regular, gap ngang,
tag H2-H4, trailing không đè/không tràn/không bị bọc, tối đa 2 dòng, icon
`aria-hidden`). 0 tràn ngang, 0 JS error, HTTP 200 toàn bộ 19 route × 3 viewport.

Danh sách "VẤN ĐỀ" script tự in ra ban đầu có 9 dòng — **cả 9 đều false-positive của
chính script audit này**, đã xác minh bằng đọc lại source:

- **7 dòng "còn N giả-heading `{card-header:N}`"**: script tự thêm lớp `card-header` vào
  danh sách quét pseudo-heading để rộng lưới hơn D3b, nhưng lớp đó vừa là div Bootstrap
  BAO NGOÀI component đã migrate (`portal_franchise_profile.xml:30/68/100/133`,
  `portal_knowledge.xml:55/305`) vừa là chính `ch_class` gắn thêm lên component
  (`portal_support.xml:405/415/431/467`) — không phải tiêu đề giả cạnh tranh. Đối chiếu
  source xác nhận cả 2 trường hợp đều là phần tử hợp lệ, không phải nợ migrate.
- **2 dòng "KHÔNG THẤY" ở `/portal/support/new`**: script tự sao chép nhầm 4 tiêu đề của
  màn "Tạo yêu cầu bù hàng" (`wujia_portal_return`, D3a ledger) vào route
  `/portal/support/new` — lỗi gõ route trong chính file audit, trang thật hiển thị đúng
  "Thông tin ticket" (dòng 49-50 output). Không phải lỗi sản phẩm.

## 5. Kết luận

D3a+D3b+D3c (47/103) **ổn định trên UAT thật**, không có breakage nào lộ ra ngoài phạm
vi từng cụm đã tự đo. Không có fix nào cần code thêm phiên này. `UI-CARDHEADER-001`
**giữ nguyên `Ready for Dev`** (47/103, đúng tiền lệ C8a→C8b) — ledger vẫn dạng comment,
không chạy `qa_sync.py`. **Kế tiếp: D3d = `portal_exam.xml` (21 call site)**, đúng như
`docs/next-session-clusters-D.md` đã chốt.
