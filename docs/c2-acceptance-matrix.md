# C2 — Bảng đối chiếu acceptance (WJ-DEBT-001 / 004 / 007 / 010)

**Ngày đo:** 2026-08-15 · **Môi trường:** DB copy cô lập `wujia_tea_c2`, Odoo port **8052**
(KHÔNG đụng `wujia_tea_19`/8019) · **Viewport:** 391×844 (M) + 1920×1080 (PC) ·
**Harness:** `scratchpad/c2_measure.py` (Playwright + chromium, đo text/DOM thật).

**Dữ liệu dựng để đo** (`scratchpad/seed_c2.py`, cửa hàng HCM-01, company currency USD):
tuần W33 hoá đơn 55.000 $ chưa trả, hạn 20/08 (chưa quá hạn) · W32 trả một phần · W31 quá hạn
chưa trả · W30 hoá đơn trả đủ + giấy báo có 72.450 $ còn dư · W29 không phát sinh · trong tháng
có 1 payment EUR + 2 payment USD.

## Build & test

| Bước | Kết quả |
|---|---|
| `-u wujia_portal_debt --stop-after-init` | RC=0, 0 ERROR/Traceback |
| `--test-tags wujia_debt` | **29 test, 0 failed / 0 error** (13 test mới cho C2) |
| Hồi quy `-u wujia_portal_debt,wujia_account,wujia_portal_base --test-enable` | **113 test, 0 failed / 0 error** |

## Đo giao diện

| Issue | Yêu cầu | Đo được | Kết quả |
|---|---|---|---|
| 001 | [M] card == dòng hoá đơn (Chưa thanh toán) | `card='Chưa thanh toán' dòng=['Chưa thanh toán']` | PASS |
| 001 | [M] Còn phải trả = số dư, không âm | `55.000,00 $` | PASS |
| 010 | [M] dòng hạn thanh toán dưới số tiền | `['Hạn thanh toán: 20/08/2026']` | PASS |
| 007 | [M] card tuần dư có = 'Dư có' | `Dư có` | PASS |
| 007 | [M] credit note KHÔNG mang nhãn 'Chưa thanh toán' | `['Đã thanh toán', 'Giấy báo có']` | PASS |
| 007 | [M] card tổng quan không in số âm | `CÒN PHẢI TRẢ Dư có 0,00 $ Dư có 72.450,00 $ được khấu trừ kỳ sau Tổng giá trị hóa đơn 0,00 $ Đã thanh toán 72.` | PASS |
| 007 | [M] không có CTA thanh toán khi dư có | `None` | PASS |
| 010 | [M] không có ?week= → tuần quá hạn cũ nhất (2026-W31) | `2026-W31` | PASS |
| 010 | [M] tuần chưa có hoá đơn → 'Hạn thanh toán: -' | `True` | PASS |
| 010 | [M] ?week= hợp lệ vẫn thắng mặc định | `2026-W29` | PASS |
| 007 | [M] /pay khi hết nợ → về /portal/debt kèm thông báo | `http://127.0.0.1:8052/portal/debt?week=2026-W30&notice=no_due | banner` | PASS |
| 007 | [M] nội dung CK không chứa số âm | `['HCM-01 K33 55000']` | PASS |
| 004 | [M] mỗi giao dịch theo currency của chính nó | `['42.450,00 €', '30.000,00 $', '30.000,00 $']` | PASS |
| 004 | [M] tổng tách theo từng loại tiền, không quy đổi | `Tổng đã xác nhận: 42.450,00 €` | PASS |
| REG | [M] /portal: 200, overflow ngang 0 | `0` | PASS |
| REG | [M] /portal/order: 200, overflow ngang 0 | `0` | PASS |
| REG | [M] /portal/purchase-history: 200, overflow ngang 0 | `0` | PASS |
| REG | [M] /portal/debt: 200, overflow ngang 0 | `0` | PASS |
| REG | [M] 0 JS pageerror | `[]` | PASS |
| 001 | [PC] card == dòng hoá đơn (Chưa thanh toán) | `card='Chưa thanh toán' dòng=['Chưa thanh toán']` | PASS |
| 001 | [PC] Còn phải trả = số dư, không âm | `55.000,00 $` | PASS |
| 010 | [PC] dòng hạn thanh toán dưới số tiền | `['Hạn thanh toán: 20/08/2026']` | PASS |
| 007 | [PC] card tuần dư có = 'Dư có' | `Dư có` | PASS |
| 007 | [PC] credit note KHÔNG mang nhãn 'Chưa thanh toán' | `['Đã thanh toán', 'Giấy báo có']` | PASS |
| 007 | [PC] card tổng quan không in số âm | `Tổng giá trị hóa đơn 0,00 $ Đã thanh toán 72.450,00 $ Còn phải trả 0,00 $ Dư có 72.450,00 $ được khấu trừ kỳ s` | PASS |
| 007 | [PC] không có CTA thanh toán khi dư có | `None` | PASS |
| 010 | [PC] không có ?week= → tuần quá hạn cũ nhất (2026-W31) | `2026-W31` | PASS |
| 010 | [PC] tuần chưa có hoá đơn → 'Hạn thanh toán: -' | `True` | PASS |
| 010 | [PC] ?week= hợp lệ vẫn thắng mặc định | `2026-W29` | PASS |
| 007 | [PC] /pay khi hết nợ → về /portal/debt kèm thông báo | `http://127.0.0.1:8052/portal/debt?week=2026-W30&notice=no_due | banner` | PASS |
| 007 | [PC] nội dung CK không chứa số âm | `['HCM-01 K33 55000']` | PASS |
| 004 | [PC] mỗi giao dịch theo currency của chính nó | `['42.450,00 €', '30.000,00 $', '30.000,00 $']` | PASS |
| 004 | [PC] tổng tách theo từng loại tiền, không quy đổi | `Tổng thanh toán trong thời gian lọc:42.450,00 € • 60.000,00 $` | PASS |
| REG | [PC] /portal: 200, overflow ngang 0 | `0` | PASS |
| REG | [PC] /portal/order: 200, overflow ngang 0 | `0` | PASS |
| REG | [PC] /portal/purchase-history: 200, overflow ngang 0 | `0` | PASS |
| REG | [PC] /portal/debt: 200, overflow ngang 0 | `0` | PASS |
| REG | [PC] 0 JS pageerror | `[]` | PASS |

38/38 PASS (100%)

## Ghi chú phạm vi

- Bảng hoá đơn PC vẫn giữ **dấu kế toán** của giấy báo có (`-72.450,00` ở cột Tổng tiền /
  Còn phải trả) — acceptance BA chỉ cấm số âm ở *trạng thái nợ*, *card tổng quan* và *nội dung
  chuyển khoản*; dòng đó nay mang nhãn **"Giấy báo có"**, mobile hiển thị "Được trừ 72.450,00 $".
- 3 quyết định Dev tự chốt (chủ dự án 15/08 bảo "đề xuất tôi"), BA đổi được ở vòng retest:
  nhãn `Chưa thanh toán` / `Dư có` / `Giấy báo có` · mobile tuần rỗng chèn 2 dòng vào empty-state
  Figma frame 05 (không dựng card mới) · `/portal/debt/pay` khi hết nợ **302** về `/portal/debt`
  kèm banner thay vì đứng lại trang pay.
- Ngoài phạm vi C2 (đã có ở cụm C3): QR thật, spacing mobile trang lịch sử, nút copy, sidebar
  desktop lọt vào trang pay.
