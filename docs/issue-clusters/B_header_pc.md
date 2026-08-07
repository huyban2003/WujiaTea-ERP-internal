# Cụm B — Header PC: cụm hành động bên phải

**Issue:** UI-03 · UI-PC-BASE-011 · UI-02 *(chỉ phần hình học — phần cờ/nhãn xem cụm I)*
**Sev:** High (UI-03) / Low · **Rủi ro:** Trung bình — chỉ 1 template + 1 khối CSS

> ⚠️ **Chạy sau cụm A.** Cụm A đổi `.navbar-container` từ x=600 về x=300 — cụm bên trái dịch,
> cụm bên phải (right-aligned) đứng yên. Nhưng phải đo lại sau A để không sửa theo số cũ.

---

## 1. Actual đã đo (UAT `/portal`, 1920×1080)

| Phần tử | Actual | Source v1.5 |
|---|---|---|
| `.navbar-collapse` | `614, 4.9, 1306 × 62.3` | — |
| `li.dropdown-language` | `1491.7, 4.9, 118 × 62.3` | `1450, 16, 118 × 40` |
| `li` cart (`.wujia-header-icon-item`) | `1609.7, 4.9, 42.1 × 62.3` | `1590, 16, 40 × 40` circle glass |
| `li` notification | `1651.9, 4.9, 42.1 × 62.3` | `1642, 16, 40 × 40` circle glass |
| `li.dropdown-user` | `1694, 4.9, 226 × 62.3` | `1696, 10, 204 × 52` glass pill |
| Mép phải cụm | **1920** (sát biên) | 1900 → **thiếu padding phải 20px** |

Thứ tự trong account block hiện tại: **text → avatar 40×40 → chevron**.
Source: **avatar/user-icon 36px bên TRÁI → tên + role → chevron**, nền trắng opacity `.18`, radius 18.
Avatar hiện `x=1812.9`, source cần `x≈1706–1742`.

## 2. Root cause

1. **Chiều cao 62.3px**: các `<li>` là `nav-item` bọc `.nav-link` — Vuexy cho `.nav-link{padding:.5rem 1rem}` +
   `.navbar-container` cao 58px → item ăn hết chiều cao. Chưa có rule ép circle 40×40 / pill 52.
2. **Thiếu padding phải**: `.navbar-container` không có `padding-right` → `ul.float-right` dính mép viewport.
   Source chừa 20px.
3. **Anatomy account sai thứ tự**: `layouts.xml:83-99` render `div.wj-pc-user-nav` (tên+role) **trước** `<span><img></span>`.
   Muốn avatar bên trái phải đảo DOM (hoặc `order` trên flex — nên đảo DOM cho đúng thứ tự đọc màn hình).
4. **Không có nền glass**: chưa có rule `background: rgba(255,255,255,.18); border-radius:18px` cho `.dropdown-user-link`.

## 3. Cách sửa đề xuất

- **Template** `custom/wujia_portal_layout/views/layouts.xml`, template `layout_top_navbar`:
  - Đảo thứ tự trong `a.dropdown-user-link`: `<span><img></span>` **lên trước** `div.wj-pc-user-nav`, chevron giữ cuối.
  - Thêm class định danh cho cụm phải để CSS bám chắc, ví dụ `wj-pc-navactions` trên `ul.nav.navbar-nav.float-right`.
- **CSS** — thêm block mới trong `_wujia_theme.css`, **scope trong `.wujia-navbar`**, đặt sau các rule hiện có
  (đồng cấp specificity thì thứ tự source quyết định — L4):
  ```css
  @media (min-width: 1200px) {
      .wujia-navbar .navbar-container { padding-right: 20px; }
      .wujia-navbar .wj-pc-navactions { align-items: center; gap: 12px; }
      /* cart + notification: circle glass 40×40 */
      .wujia-navbar .wujia-header-icon-item > a {
          width: 40px; height: 40px; padding: 0; border-radius: 20px;
          display: inline-flex; align-items: center; justify-content: center;
          background: rgba(255,255,255,.18);
      }
      /* account: glass pill 204×52, avatar 36 bên trái */
      .wujia-navbar .dropdown-user > a.dropdown-user-link {
          height: 52px; padding: 0 14px; border-radius: 18px;
          background: rgba(255,255,255,.18);
          display: inline-flex; align-items: center; gap: 10px;
      }
      .wujia-navbar .dropdown-user img.round { width: 36px; height: 36px; border-width: 0; }
      /* language pill 118×40 */
      .wujia-navbar .dropdown-language > a { height: 40px; padding: 0 12px; display: inline-flex; align-items: center; }
  }
  ```
- **KHÔNG** đụng `_components.css` (8 module dùng chung) và `style.css` (legacy).
- Giữ nguyên hành vi click, dropdown, badge count (`header_cart_badge.js` bám `.wujia-header-badge`).
- Bump `?v=` cho `_wujia_theme.css`.

## 4. Blast radius

```bash
grep -rn "wujia-header-icon-item\|dropdown-user-link\|wujia-header-badge" custom/ --include=*.xml --include=*.css --include=*.js
grep -rn "wj-pc-user-nav" custom/ --include=*.css --include=*.xml
```
`.wujia-header-icon-item` được `wujia_portal_sale/views/header_cart_inherit.xml` và
`wujia_portal_notification/views/header_bell_inherit.xml` chèn vào → **sửa CSS phải kiểm cả hai badge**.

## 5. Verify

| Điểm đo | Expected |
|---|---|
| language pill | `1450, 16, 118 × 40` |
| cart circle | `1590, 16, 40 × 40`, `border-radius: 20px`, nền `rgba(255,255,255,.18)` |
| notification circle | `1642, 16, 40 × 40` |
| account pill | `1696, 10, 204 × 52`, radius 18, nền glass |
| avatar circle | tâm `(1724, 36)`, đường kính 36, **bên trái** tên |
| badge cart/notification | không lệch/chồng, vẫn cập nhật đúng số |

Regression: mở dropdown ngôn ngữ + dropdown tài khoản, bấm từng mục; kiểm 391×844 header mobile **bất biến**
(rule nằm trong `@media min-width:1200px`).

## 6. Ghi sheet

- K: `FIX: cụm action header PC theo source v1.5 — cart/notification circle glass 40×40, account glass pill 204×52 avatar bên trái, language pill 118×40, thêm padding-right 20px | IMPACT: header PC mọi trang portal ≥1200px | RETEST: 1920×1080 đo toạ độ 4 phần tử + mở 2 dropdown + badge còn đúng số | LIMIT: phần cờ/nhãn ngôn ngữ theo dõi riêng ở UI-02 (câu hỏi BA)`
- R: `Custom`
