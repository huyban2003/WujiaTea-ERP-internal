# Cụm C9 — bảng đối chiếu acceptance (RESP-MOB-ORDER-002, WJ-ORD-026, WJ-PH-008)

**Ngày:** 15/08/2026 · **Module:** `wujia_portal_layout` `19.0.31.16.0` → `19.0.31.17.0`,
`wujia_portal_sale` `19.0.4.12.0` → `19.0.4.13.0`, `wujia_portal_purchase_history`
`19.0.3.5.0` → `19.0.3.6.0`. Không migration.

⚠️ **Deploy phải có `wujia_portal_layout`** (khác câu lệnh trong prompt): CSS gốc của card đặt
hàng và khối tổng tiền giỏ nằm ở `wujia_portal_layout/static/assets/css/_components.css`, và
`?v=` của `_variables.css`/`_components.css` bump 1168 → 1169 ở `views/assets.xml`:

```
-u wujia_portal_layout,wujia_portal_sale,wujia_portal_purchase_history
```

**Cách đo:** DB copy cô lập `wujia_tea_c9` (tạo từ `wujia_tea_c5`), Odoo riêng **port 8059** —
không đụng `wujia_tea_19`/8019. Playwright + chromium ở **360×640**, **391×844**, **1920×1080**
(`scratchpad/c9_measure.py`; login qua `/web/session/authenticate` rồi gắn cookie
`wujia_active_franchise_id`, theo L13). Test chạy trên copy thứ hai `wujia_tea_c9t`.

**Kết quả tổng:** đo **26/26 đạt (100%)** · test mới **8/8 xanh** (5 `wujia_history` + 3
`wujia_catalog_layout`), tổng **36 test** 3 tag của 2 module 0 failed · hồi quy **57 test**
(`wujia_debt` C2+C3, `wujia_delivery_c5` C5, `wujia_knowledge` C4) 0 failed · build `-u` RC=0.

**Dữ liệu đo:** cửa hàng HCM-01, giỏ **6 dòng** + ghi chú dài 3 câu, catalog 5 sản phẩm (1 tên
dài 92 ký tự để ép xuống 2 dòng), lịch sử **14 đơn**.

---

## WJ-ORD-026 (High) — CTA "Gửi đơn đặt hàng" không được Footer Action Bar che

Gốc: `.wujia-mcart-summary` ghi cứng `bottom: 64px` từ thời footer cao 64, trong khi footer
hiện tại là token `--wujia-mnav-height: 83px` → CTA thò xuống dưới mép trên footer đúng ~7px
(khớp số BA: CTA y≈722–768, footer y≈761). Sửa: token mới `--wujia-mnav-total` = chiều cao nav
**thực** (đã cộng phần safe-area vượt padding 6px của chính nav), dùng cho khối tổng tiền,
khoảng chừa của trang giỏ và floatbar catalog. Không gõ số cứng, không đổi sang sticky.

| Yêu cầu (Kết quả mong muốn) | Đo được | Pass |
|---|---|---|
| 391×844: toàn bộ CTA nằm trên Footer Action Bar | CTA đáy **y=749**, footer đỉnh **y=761** → cách **12px** (trước: che 7px) | ✅ |
| 360×640: toàn bộ CTA nằm trên Footer Action Bar | CTA đáy **y=545**, footer đỉnh **y=557** → cách **12px** | ✅ |
| Không phần nào bị che / nằm dưới footer | `bottom(CTA) − top(footer) = −12` ở cả 2 viewport | ✅ |
| Vùng bấm CTA còn nguyên | CTA 359×46 (391) / 328×46 (360), không phần tử fixed nào chồng lên | ✅ |
| Ghi chú vẫn đọc/thao tác được khi nội dung dài | giỏ 6 dòng, cuộn hết (scrollY 727/931): đáy ô ghi chú cách đỉnh khối tổng **54.5px** | ✅ |
| Tổng tiền vẫn đọc được | `.wujia-mcart-grand` hiển thị đủ trong khối tổng, không bị footer cắt | ✅ |
| Không sinh cuộn ngang | `scrollWidth − clientWidth = 0` ở 360 và 391 | ✅ |
| Không lỗi JS | 0 pageerror ở cả 2 viewport | ✅ |

Ghi chú: khoảng chừa của trang giỏ đổi từ `180px` cố định sang
`calc(var(--wujia-mnav-total) + 116px)` — giữ đúng khoảng dư như trước (≈40px) nhưng nay tự đổi
theo chiều cao footer, footer có sửa lại cũng không tái phát.

## RESP-MOB-ORDER-002 (Low) — tên sản phẩm dùng hết chiều rộng card

Gốc: card mobile là **1 hàng flex** (thumb 42 + tên + giá + nút giỏ) nên tên chỉ còn ~150px /
391. Sửa theo đúng đề xuất BA ("tách giá và nút giỏ xuống hàng riêng"): `.wujia-morder-row`
thành grid 2 hàng `"thumb name name" / "thumb meta ctl"`, tên là ô riêng ở hàng trên.

| Yêu cầu | Đo được | Pass |
|---|---|---|
| 391: tên dùng hết chiều rộng khả dụng của card | **277.4px** / card 357.4 (trước **150.3px**) = toàn bộ phần còn lại sau thumb + padding, **+85%** | ✅ |
| 360: tên dùng hết chiều rộng khả dụng | **246.4px** / card 326.4 (trước 122.4) = **+101%** | ✅ |
| Tối đa 2 dòng | tên 92 ký tự → **2 dòng**, `-webkit-line-clamp: 2` giữ nguyên; 4 tên còn lại về **1 dòng** (trước có tên 2 dòng) | ✅ |
| Có "…" khi thực sự vượt quá | tên dài: `scrollHeight > clientHeight` → ellipsis của line-clamp; các tên khác không bị cắt | ✅ |
| Không chồng giá | bbox tên ∩ bbox giá = ∅ ở mọi dòng, 2 viewport | ✅ |
| Không chồng ĐVT / quy cách | tên và `.wujia-morder-row-spec` khác hàng grid, không giao nhau | ✅ |
| Không chồng nút giỏ | bbox tên ∩ bbox `.wujia-morder-cartctl` = ∅ (kể cả khi control ở dạng stepper 112px) | ✅ |
| Card không tràn ngang tại 360 và 391 | `scrollWidth − clientWidth = 0` ở cả hai | ✅ |
| Chiều cao card động (BA đã chấp nhận) | 1 dòng tên **85px**, 2 dòng **106px** (trước 64 / 85) | ✅ |
| Lọc không reload vẫn đúng | `/portal/order/results` 200, mảnh `mbody` chứa đúng cấu trúc mới | ✅ |

## WJ-PH-008 (Medium) — mặc định 10 dòng/trang

Gốc: `PAGE_SIZE = 20`. Sửa về 10; thêm `PAGE_SIZE_OPTIONS = (10, 20, 50)` làm **nguồn duy nhất**
cho cả selector (template bỏ `[10,20,50]` gõ tay) lẫn validate; 2 form lọc (PC + mobile) nay
mang theo `page_size`.

| Yêu cầu | Đo được | Pass |
|---|---|---|
| URL không truyền page_size → selector "10 / trang" | `/portal/purchase-history` → `select.value = 10` (PC 1920 và mobile 391) | ✅ |
| Trang 1 tối đa 10 dòng | 10 dòng / 14 bản ghi | ✅ |
| Tổng bản ghi đúng | "Hiển thị 1–10 / 14 bản ghi", trang 2: "11–14 / 14" | ✅ |
| Số trang đúng | 2 trang (14 ÷ 10), pager: Trước · 1 · 2 · Sau | ✅ |
| Giữ page_size khi chuyển trang | `?page=2` → selector vẫn 10; querystring pager mang `page_size` khi ≠ mặc định | ✅ |
| Giữ page_size khi search | `page_size=20` + bấm Tìm "S0" → URL `?page_size=20&q=S0` | ✅ |
| Giữ page_size khi filter trạng thái | `?page_size=20&state=draft` → selector **20**, 12 dòng 1 trang | ✅ |
| Validate giá trị không hợp lệ ở controller | `page_size=abc` → 10; `page_size=7` → 10; test phủ `0/-5/9999/3.5/[]/None` | ✅ |
| Không trùng đơn giữa các trang | mã đơn trang 1 ∩ trang 2 = ∅ | ✅ |
| Không thiếu đơn giữa các trang | hợp 2 trang = **14** mã phân biệt = tổng bản ghi | ✅ |

---

## Hồi quy

| Kiểm tra | Kết quả |
|---|---|
| `/portal` 391×844 + 1920×1080 | 200 · tràn ngang 0 · 0 JS error |
| `/portal/delivery` 391×844 + 1920×1080 | 200 · tràn ngang 0 · 0 JS error |
| `/portal/debt` 391×844 + 1920×1080 | 200 · tràn ngang 0 · 0 JS error |
| Fragment AJAX `/portal/order/results`, `/portal/purchase-history/results` | 200, render đủ mảnh, không lỗi QWeb |
| Test `wujia_history` + `wujia_pricing` + `wujia_catalog_layout` | **36 test, 0 failed / 0 error** |
| Test `wujia_debt` + `wujia_delivery_c5` + `wujia_knowledge` (C2–C5) | **57 test, 0 failed / 0 error** |
| Build `-u` 3 module `--stop-after-init` | RC=0, 0 ERROR / Traceback |

## Đo lại trên UAT sau khi deploy (15/08/2026)

Deploy xong `-u wujia_portal_layout,wujia_portal_sale,wujia_portal_purchase_history`; đối chiếu
XML-RPC: 3/3 module trên UAT khớp đĩa (`19.0.31.17.0` / `19.0.4.13.0` / `19.0.3.6.0`). Đo lại
**chỉ đọc** trên `http://113.161.187.126:8019` bằng Playwright, dữ liệu thật (giỏ HCM-01 4 dòng,
15 đơn lịch sử).

| Kiểm tra trên UAT | Đo được | Pass |
|---|---|---|
| CTA giỏ vs footer @391×844 | CTA đáy 749 · footer đỉnh 761 → cách **12px** | ✅ |
| CTA giỏ vs footer @360×640 | CTA đáy 545 · footer đỉnh 557 → cách **12px** | ✅ |
| Ghi chú còn đọc được khi cuộn hết | đáy ô ghi chú cách khối tổng **54.5px** | ✅ |
| Token nav sống trên UAT | `--wujia-mnav-total` resolve, `.wujia-mcart` padding-bottom = **199px** (83+116) | ✅ |
| Tên SP @391 / @360 | **277.4px** / **246.4px**, 5/5 sản phẩm về 1 dòng, 0 chồng lấn | ✅ |
| Lịch sử mặc định | selector **10**, trang 1 "1–10 / 15", trang 2 "11–15 / 15", 0 mã trùng | ✅ |
| `page_size` không hợp lệ (`abc`, `7`) | về 10 | ✅ |
| Giữ `page_size` khi lọc/tìm | `?page_size=20&state=sale` và `&q=S` → hidden input giữ **20**, selector 20 | ✅ |
| Hồi quy `/portal`, `/portal/delivery`, `/portal/debt` × 2 viewport | 200 · tràn ngang 0 · 0 JS error | ✅ |

**Không sửa dữ liệu UAT**: giỏ HCM-01 vốn đã có 4 dòng (lần đo đầu thấy trống chỉ vì phiên
trình duyệt chưa chọn cửa hàng), nên không phải thêm/xoá gì.

**LIMIT:** trên UAT chưa có sản phẩm nào tên đủ dài để ép xuống 2 dòng — nhánh 2 dòng + dấu ba
chấm đã đo ở bản sao local (tên 92 ký tự → 2 dòng, thẻ 106px). Và chưa đo trên thiết bị thật
có home-indicator (safe-area > 6px) — nhánh đó đi qua
`env(safe-area-inset-bottom)` trong `--wujia-mnav-total`, headless Chromium luôn trả 0px.
Công thức bám đúng `padding-bottom: max(6px, env(...))` của chính thanh nav nên chỉ chừa thừa
chứ không thể chừa thiếu.
