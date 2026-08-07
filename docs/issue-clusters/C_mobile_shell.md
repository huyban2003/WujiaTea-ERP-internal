# Cụm C — Mobile shell

**Issue:** UI-04 · RESP-MOB-SHELL-003 *(+ RESP-MOB-ORDER-001 nếu BA xác nhận — xem cụm I)*
**Sev:** Low · **Rủi ro:** Trung bình — RESP-MOB-SHELL-003 chạm ~10 trang

---

## 1. Actual đã đo (UAT, 391×844, DPR=1, 02/08/2026)

### UI-04 — cụm action header mobile

```
.wujia-mheader        0, 0, 391 × 104
.wujia-mheader-logo   16, 30, 116 × 44
actions (3 nút)       229,33,38×38 · 283,33,38×38 · 337,33,38×38
  → tâm y = 52        cần 58  (cao hơn 6px)
  → tâm x = 248/302/356   cần 247/301/355 (lệch phải 1px)
avatar glyph i.feather.icon-user   343.4, 43, 18.1 × 18   margin-right: 7px
  → tâm x glyph = 352.5 vs tâm circle 356 → lệch trái 3.5px
```

### RESP-MOB-SHELL-003 — mốc đầu content lệch tới 14px

Store strip đồng nhất mọi trang: `y = 104 → 152`. Page header thực tế:

| Route | y actual | Expected |
|---|---|---|
| `/portal/notification` | **162** | 168 |
| `/portal/knowledge` | **163** | 168 |
| `/portal/delivery` · `/support` · `/profile` | **166** | 168 |
| `/portal/return` | **168** ✅ | 168 |
| `/portal/purchase-history` | **169** | 168 |
| `/portal/order` · `/portal/order/cart` | **176** | 168 |
| `/portal` (hero) | 168 ✅ | 168 |

Khớp 100% con số BA ghi ngày 01/08.

## 2. Root cause

### UI-04
- Cụm action bị đẩy lên do chiều cao/`align-items` của `.wujia-mheader-actions` chưa neo theo mốc y=39 của Blank Shell.
- `margin-right: 7px` trên glyph avatar (`i.feather.icon-user`) — dư từ markup cũ → lệch tâm 3.5px.
- Icon dùng **font Feather 18px**; source là SVG `stroke-width 2.4, linecap/linejoin round` → nét mảnh hơn thấy rõ.

### RESP-MOB-SHELL-003
`custom/wujia_portal_layout/static/assets/css/_wujia_theme.css:392-403` — mỗi trang một giá trị:
```css
.content-wrapper:has(.wujia-morder) { padding-top: 8px !important; }
.content-wrapper:has(.wujia-mcart)  { padding-top: 8px !important; }
.content-wrapper:has(.wujia-mhist)  { padding-top: 1px !important; }
.content-wrapper:has(.wujia-mhome)  { padding-top: 0   !important; }
.content-wrapper.wujia-mreport-wrap { padding-top: 14px !important; }
```
Cộng thêm `margin-top` nội bộ của từng wrapper trang (`*-titlerow` 4px…) → ra 6 giá trị khác nhau.
Đây là **tích tụ nhiều sprint vá lẻ**, không phải lỗi 1 trang.

## 3. Cách sửa đề xuất

1. **Một token duy nhất**: thêm `--wujia-mcontent-top: 16px` vào `_variables.css`.
   Mốc chuẩn: strip kết ở `y=152` → content bắt đầu `152 + 16 = 168`.
2. **Bỏ hết 5 rule `:has()` per-page**, thay bằng 1 rule:
   ```css
   @media (max-width: 991.98px) {
       html body .content .content-wrapper { padding-top: var(--wujia-mcontent-top) !important; }
   }
   ```
3. **Trung hoà margin nội bộ**: mỗi wrapper trang (`.wujia-morder`, `.wujia-mcart`, `.wujia-mhist`,
   `.wujia-mhome`, `.wujia-mreport-wrap`, và các trang dùng `wj-page-header--m`) đặt `margin-top: 0`
   cho phần tử đầu tiên. **Đây là phần dễ sót nhất** — phải đo đủ 9 route, không suy luận.
4. **UI-04**: đặt `.wujia-mheader-actions { top: 39px }` (hoặc `padding-top` tương đương), dịch tâm x −1px,
   xoá `margin-right:7px` trên glyph, thay glyph feather bằng SVG inline stroke 2.4 round
   (pattern đã dùng ở `bottomnav`/`store_picker` — tái sử dụng, đừng viết mới).
5. Bump `?v=` cho `_wujia_theme.css` + `_variables.css`.

## 4. Blast radius

```bash
grep -rn ":has(.wujia-m" custom/ --include=*.css
grep -rn "wujia-mheader-action\|wujia-mheader-avatar" custom/ --include=*.css --include=*.xml
grep -rn "wj-page-header--m" custom/ --include=*.xml | wc -l     # số trang bị ảnh hưởng
grep -rn "wujia-page-content-top\|wujia-mcontent-top" custom/ --include=*.css
```
⚠️ Đổi padding chung sẽ **dịch toàn bộ nội dung mọi trang mobile**. Đây chính là lý do
RESP-MOB-SHELL-003 từng bị defer ở Sprint 38 ("page-header y regression ~10 trang").
→ Bắt buộc chụp/đo **trước và sau** cho đủ 9 route.

## 5. Verify

- 9 route mobile: `/portal`, `/order`, `/order/cart`, `/purchase-history`, `/delivery`, `/notification`,
  `/knowledge`, `/support`, `/profile`, `/return` → page header **y = 168 ± 1**, x = 16.
- UI-04: 3 circle 38×38 tâm `(247,58) (301,58) (355,58)`; glyph avatar tâm x = 356 (trùng tâm circle).
- Overflow ngang = 0; header 104px và strip 104→152 **không đổi**.
- PC 1920 **bất biến** (mọi rule trong `@media max-width:991.98px`).

## 6. Ghi sheet

- K (UI-04): `FIX: dịch cụm action header mobile về y=39-77, căn tâm x theo Blank Shell, bỏ margin-right 7px trên glyph avatar, đổi icon sang SVG stroke 2.4 round | IMPACT: header mobile mọi trang portal | RETEST: 391×844 đo 3 circle 38×38 tâm (247/301/355, 58) và tâm glyph avatar trùng tâm circle | LIMIT: logo mobile theo dõi riêng ở UI-MOB-SHELL-001 (chờ BA cấp asset 100×34)`
- K (RESP-MOB-SHELL-003): `FIX: gộp 5 rule padding-top per-page thành 1 token --wujia-mcontent-top=16px, chuẩn hoá mốc content y=168 | IMPACT: TOÀN BỘ trang mobile portal (~10 trang) | RETEST: 391×844, 9 route, page header y=168 x=16 | LIMIT: Không có`
- R: `Custom`
