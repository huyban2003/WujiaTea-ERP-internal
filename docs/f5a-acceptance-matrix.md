# F5a — Bảng nghiệm thu (đo bằng máy, 18/09/2026)

Phạm vi: mục 0 (vá điểm mù mốc đo) + mục 1 (menu về module sở hữu route) + mục 3
(redirect legacy) của phiên F5. Mục 2 (dời test cross-module của `wujia_portal_layout`)
để **F5b**. DB `wujia_f0`, server đo cổng 8099, 2 tài khoản `anh.owner` + `em.hcm`.

| # | Phép đo | Ngưỡng | Kết quả |
|---|---|---|---|
| 1 | `nav_dump.py` trước/sau · PC + mobile · 2 tài khoản × 2 khổ (46 + 28 route) | 0 khác biệt | **Đạt có giải trình** — 0 lệch về href/nhãn/icon/active/thứ tự/hiển thị; 296 ô lệch duy nhất là **thuộc tính `id` thêm vào 2 `<li>` tiêu đề nhóm** (`nav_header_main`, `nav_header_utils`) làm neo kế thừa. Không thêm/bớt phần tử DOM nào. |
| 2 | `wj_measure --diff` mốc F5a (74 route, có trạng thái rỗng) | 0 ô lệch không giải trình | **Đạt** — 0 ô lệch chiều cao, 0 ô mất record, cả 2 tài khoản |
| 3 | 148 ảnh 2 khổ, so từng cặp | 0 khác biệt ngoài đồng hồ/dữ liệu | **Đạt** — 136/148 giống hệt (bỏ thanh tiến trình 3px trên cùng); 12 ảnh còn lệch đều là đồng hồ đếm ngược ("còn 14:17"→"13:49"), lượt xem bài viết, và pha hoạt hình biểu đồ báo cáo — soi từng cặp bằng ảnh ghép |
| 4 | Suite 12 module portal, chạy kèm `-u` | ≥ 543/543, 0 failed 0 error | **Đạt — 571/571**, 0 failed 0 error (mốc 543 + 28 test mới) |
| 5 | `b4_regression.py` | 286/286 | **Đạt — 286/286 PASS** |
| 6 | `check_layers.py` | vi phạm cũ 1 (`portal_order_window`, F7); phép kiểm mới 0 | **Đạt** — R1–R5: đúng 1 vi phạm cũ đã biết; **R6 (mới): 0** |
| 7 | Mutation mọi guard mới | đỏ khi phá, xanh khi hoàn tác | **Đạt — 5/5** (bảng dưới) |
| 8 | `ir.ui.view` mồ côi sau `-u` | 0 | **Đạt — 0** (SQL: không còn `ir_ui_view` thiếu `ir_model_data`, 6 xmlid chết đã biến mất) |
| 9 | Test 301 của 3 route cũ | xanh, đúng đích | **Đạt** — 3 test mới ở đúng module đích |
| 10 | Bump `version` mọi module bị đụng | 0 sót | **Đạt — 13 module** (+1 patch); F5a không sửa CSS ⇒ không đụng `?v=` |

## Mutation (luật FR-B: phá phải đỏ, hoàn tác phải xanh)

| # | Phá gì | Guard phải bắt | Kết quả |
|---|---|---|---|
| M1 | Chèn lại `<a href="/portal/knowledge">` vào `layouts.xml` | `check_layers` R6 + `test_f5_frame_routes` | đỏ: R6 báo 1 vi phạm, 2 test fail |
| M2 | Đổi nhãn mục "Đăng ký thi" → "Đăng ký thi MUT" | danh sách vàng + test module exam | đỏ: 2 test fail |
| M3 | Đổi `priority` mục Đặt hàng 20 → 70 (sai thứ tự menu) | danh sách vàng | đỏ: 1 test fail |
| M4 | `code=301` → `302` ở redirect legacy của return | test 301 | đỏ: 1 test fail |
| M5 | Đổi `id="nav_item_exam"` → `nav_item_exam_x` (gãy neo xpath của anh Thái) | validate view lúc `-u` | đỏ: `-u` gãy ngay, không lên được registry |
| — | Hoàn tác cả 5 | | xanh: 28/28 test F5, 571/571 suite |

⚠️ **Bẫy của chính khung mutation** (không phải lỗi sản phẩm): khôi phục file `.py` bằng
`mv/cp` giữ nguyên `mtime` cũ ⇒ Python dùng lại `__pycache__` biên dịch từ bản ĐÃ PHÁ và
test vẫn đỏ sau khi hoàn tác. Phải `rm -rf __pycache__` (hoặc `touch`) rồi chạy lại.
⚠️ **Không dùng `git checkout <file>` để hoàn tác mutation** khi cây làm việc còn thay đổi
chưa commit — đã cắn một lần, mất toàn bộ sửa F5a trong `layouts.xml`, phải dựng lại tay.

## Thay đổi chính

1. **Khung chỉ còn khung.** `views/pc_sidenav.xml` (`layout_sidenav_figma`, priority 99,
   `position="replace"`, 10 link cứng) **đã xoá**. `layout_sidenav` giữ `<ul>` + 2 tiêu đề
   nhóm có `id` làm neo + mục "Tài khoản" (route của chính khung). `mobile_bottomnav` giữ
   nút "Thêm" + vỏ sheet; `mobile_header` bỏ giỏ hàng và "Thông tin cửa hàng"; navbar PC và
   shell Tài khoản PC bỏ link `/portal/franchise-information`.
2. **Mục menu về module sở hữu route**: 9 `sidenav_inherit.xml` (base 10 → exam 65),
   4 tab + 7 dòng sheet `bottomnav_inherit.xml`, 2 `mheader_inherit.xml`, 2 mục PC của
   `wujia_portal_base` (`pc_nav_inherit.xml`).
3. **Khuôn kế thừa**: `<li id=... t-attf-class=...>` do module viết thẳng vào arch (xpath
   kế thừa làm việc trên ARCH — `t-att-id` sinh lúc render thì neo `//li[@id='nav_item_exam']`
   của anh Thái không thấy gì), thân mục gọi component `wujia_portal_layout.wj_nav_item`.
   Neo luôn theo thuộc tính (`@id`, `@href`, `@data-wujia-more`), không dùng chỉ số `a[1]`/`t[1]`.
4. **Biến tích luỹ** (vì `t-set` trong `t-call` không ra được scope ngoài):
   `_nav_acct_extra` (base khai `/portal/franchise-information` vào vùng sáng mục Tài khoản),
   `_bnav_order_extra` (purchase_history làm sáng tab Đặt hàng), `_bnav_hit` (cờ "đã có tab
   sáng" để nút "Thêm" sáng khi không tab nào sáng). **Phải là cờ, không phải danh sách tiền
   tố**: tab Trang chủ khớp tuyệt đối `/portal`, góp tiền tố thì mọi route con đều "khớp".
5. **Redirect legacy** `/portal/purchase_history`, `/portal/return-request-list`,
   `/portal/exam-registration` về đúng module đích, giữ `code=301`; `redirects.py` của khung đã xoá.
6. **Xoá view chết + migration**: 6 view chỉ còn trong DB (`layout_sidenav_figma`,
   `layout_sidenav_franchises`, `sidenav_franchise_information`, `layout_sidenav_return`,
   `_info_request`, `_report`) xoá bằng `migrations/<version>/pre-10-drop-dead-navs.py` —
   Odoo chỉ dọn record mồ côi ở CUỐI lượt nạp nên view cũ vẫn bị validate giữa chừng và làm
   gãy `-u` (đã cắn: `ParseError … //li[@id='nav_item_home']`).
7. **Sửa nhỏ kèm đo lại**: `pc_preview.xml` trỏ form về `/portal/pc-preview` (route thật là
   `/portal/_pc-preview`) — link chết trên trang xem trước nội bộ.

## Đính chính plan cụm F

- §1.A3 ghi "10 link cứng, 12 sidenav_inherit là code chết": thực tế
  `wujia_portal_inspection.pc_sidenav_inspection` có priority **101** > 99 nên mục "Khảo sát"
  vẫn hiện ⇒ **sidebar PC đang có 11 mục**, và nghiệm thu là diff = 0 kể cả mục đó.
- Mốc F0 mù 2 chỗ (đã vá ở mục 0): thiếu `/portal/franchise-information` và không màn nào
  được đo ở **trạng thái rỗng** — xem `docs/f5-route-inventory.md`.

## Lệnh chạy lại

```bash
# 1. nâng cấp + suite (13 module)
cd ~/odoo-dev/WujiaTea/odoo19 && MODS=$(tr '\n' ',' < /tmp/f5_mods.txt | sed 's/,$//')
python odoo-bin -c ../config/odoo.conf -d wujia_f0 --db-filter='^wujia_f0$' \
  --http-port=8299 --gevent-port=8399 --stop-after-init --test-enable -u "$MODS"
# chỉ bộ F5a:  --test-tags wujia_f5

# 2. server đo + B4
python odoo-bin -c ../config/odoo.conf -d wujia_f0 --db-filter='^wujia_f0$' \
  --http-port=8099 --gevent-port=8199 &
python scripts/ba_spec/b4_regression.py --base http://127.0.0.1:8099

# 3. menu + hình học + ảnh (zsh: PHẢI ${=R})
R=$(tr '\n' ' ' < docs/f5-baseline/routes_anh.txt)
python scripts/qa/nav_dump.py --base http://127.0.0.1:8099 --portal-login anh.owner \
  --routes ${=R} --widths 1440 390 --out /tmp/nav_after_anh.json
python scripts/qa/nav_dump.py --diff docs/f5-baseline/nav_anh.json /tmp/nav_after_anh.json
python scripts/qa/wj_measure.py --base http://127.0.0.1:8099 --portal-login anh.owner \
  --routes ${=R} --breakpoints 1440 390 --screenshots --shots scratchpad/f5/shots-after/anh \
  --out /tmp/after_anh.json
python scripts/qa/wj_measure.py --diff docs/f5-baseline/measure_anh.json /tmp/after_anh.json

# 4. tầng + CSS
python scripts/qa/check_layers.py        # R6 mới nằm cuối bảng
python scripts/qa/css_owner.py --layout-domain && python scripts/qa/css_owner.py --overrides
```

Dừng server bằng PID lấy từ `ps -eo pid,args` (**không `pkill -f`** — sẽ giết cả
PID `wujia_tea_19` của môi trường khác).
