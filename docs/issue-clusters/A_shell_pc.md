# Cụm A — Shell PC: hình học khung

**Issue:** UI-PC-SHELL-001 · UI-PC-BASE-010 · UI-01 · UI-PC-BASE-001
**Sev:** High (010, UI-01) / Low (SHELL-001, BASE-001) · **Rủi ro:** Cao — chạm mọi trang PC

---

## 1. Actual đã đo (UAT `/portal`, 1920×1080, DPR=1, 02/08/2026)

```
.main-menu              x=0    y=0   260 × 1080     ← cần 300 × 1080
.header-navbar          x=300  y=0   1620 × 72      ← ĐÚNG
.navbar-container       x=600  y=7   1320 × 58      ← cần x=300
.app-content            x=300  y=0   1620 × 1040.4
.content-wrapper        x=300  y=84  1620 × 956.4   ← cần y=72
  padding               24px 30.8px 0px             ← cần 24px đều
  margin-top            84px                        ← cần 72px
--wujia-sidebar-width   300px                       ← token ĐÚNG, CSS không áp được
```

Đo đủ 5 route (`/portal`, `/order`, `/delivery`, `/notification`, `/profile`) → **kết quả giống hệt nhau**,
đúng như BA ghi. Không phải lỗi riêng trang nào.

## 2. Root cause

### (a) Sidebar kẹt 260px — thua cascade, không phải thiếu rule

Duyệt `document.styleSheets` trên UAT, các rule set `width` khớp `.main-menu`:

| File | Media | Selector | Giá trị | Spec |
|---|---|---|---|---|
| `vertical-menu.css` | `(min-width:992px)` | `body.vertical-layout.vertical-menu-modern .main-menu` | `260px` | 0,3,0 |
| **`style.css?v=1010`** | **`(min-width:1200px)`** | **`body.vertical-layout.vertical-menu-modern .main-menu`** | **`260px !important`** | **0,3,0** |
| `_wujia_theme.css?v=1156` | `(min-width:1200px)` | `.main-menu, .main-menu.menu-fixed` | `var(--wujia-sidebar-width) !important` | 0,1,0 |

Cả hai đều `!important` → **specificity quyết định** → `style.css` (0,3,0) thắng.
Fix Sprint 35 (`_wujia_theme.css:132-140`) đúng ý tưởng nhưng **spec quá thấp**.

> Ghi chú `qa_visual_check.py` nói "sidebar `.main-menu` width bị JS điều khiển, CSS bất lực" là **kết luận sai** —
> nó là thuần cascade. Đã xác minh: `.main-menu` không có inline `style` nào chứa `width`
> (inline chỉ có `touch-action / user-select / -webkit-user-drag / tap-highlight`).

### (b) UI-01 — store block lệch +300px vì rule sửa sidebar "ăn nhầm" header

`_wujia_theme.css:137-139`:
```css
@media (min-width: 1200px) {
    html body .content { margin-left: var(--wujia-sidebar-width) !important; }  /* 300px */
}
```
Nhưng Vuexy đặt class `content` **cả trên header**:
`layouts.xml:33` → `<div class="navbar-container content">`.
→ `.navbar-container` nhận `margin-left:300px` → x = 300 (navbar) + 300 = **600**.
Store block (`store_picker_navbar.xml:78-99`, nằm trong `.bookmark-wrapper`) do đó ở **x=624** thay vì 324.

Đây là **fix của UI-PC-SHELL-001 đẻ ra UI-01** — hai issue phải sửa cùng lúc, không tách được.

### (c) UI-PC-BASE-001 — padding/margin gốc Vuexy chưa bị override

`components.css` (Vuexy): `html body .content .content-wrapper { padding: calc(2.2rem - .4rem) 2.2rem 0; margin-top: 6rem; }`
Với `html{font-size:14px}` → `2.2rem = 30.8px`, `6rem = 84px`. Khớp chính xác số BA đo.
`_wujia_theme.css:356-358` chỉ đặt `padding-top`, không đụng padding ngang / margin-top ở desktop.

## 3. Cách sửa đề xuất

1. **Sidebar** — nâng specificity trong `_wujia_theme.css`, giữ nguyên `style.css` (file legacy dùng chung, blast radius lớn):
   ```css
   @media (min-width: 1200px) {
       body.vertical-layout.vertical-menu-modern .main-menu,
       body.vertical-layout.vertical-menu-modern .main-menu.menu-fixed {
           width: var(--wujia-sidebar-width) !important;   /* 0,4,0 > 0,3,0 */
       }
   }
   ```
2. **Margin-left** — loại `.navbar-container` khỏi rule:
   ```css
   html body .content:not(.navbar-container) { margin-left: var(--wujia-sidebar-width) !important; }
   ```
   *(hoặc đổi target sang `.app-content` — nhưng `:not()` an toàn hơn vì không đổi selector đang chạy đúng.)*
3. **Content wrapper**:
   ```css
   @media (min-width: 1200px) {
       html body .content .content-wrapper {
           padding-left: 24px !important; padding-right: 24px !important;
           margin-top: var(--wujia-header-height) !important;   /* 72px */
       }
   }
   ```
4. **UI-PC-BASE-010 phần grid sidebar** (logo card 260×132 @20/16, MENU CHÍNH y≈188, item rộng 260 lề x=20):
   sửa `.main-menu .navbar-header` (`_wujia_theme.css:160-174`, đang `height:200px`, ảnh `max-height:160px`)
   + `.main-menu .navigation > li > a { margin: 3px 12px }` → lề 20px.
5. **Bump `?v=`** `_wujia_theme.css` trong `views/assets.xml` (đang 1156).

## 4. Blast radius — chạy trước khi sửa

```bash
grep -rn "html body .content\b" custom/ --include=*.css
grep -rn "navbar-container" custom/ --include=*.xml --include=*.css
grep -rn "wujia-sidebar-width\|wujia-sidebar-logo-h" custom/ --include=*.css
grep -rn "content-wrapper" custom/ --include=*.css | grep -v "\.min\."
```
`--wujia-sidebar-width` là token global → đổi giá trị token sẽ lan mọi trang. **Chỉ đổi selector, giữ nguyên token 300px.**

## 5. Verify

| Điểm đo | Expected |
|---|---|
| `.main-menu` | `0, 0, 300 × 1080` |
| `.header-navbar` | `300, 0, 1620 × 72` |
| `.navbar-container` | `x = 300` (không còn 600) |
| store block `.wujia-store-current-block` | `x = 324, y = 12, 430 × 48`; role `x≈650, 82 × 26` |
| `.content-wrapper` | `y = 72`, padding `24px` đều, content-body `x = 324` |
| Dải trống x=260–300 | **không còn** |

- Đo lại 5 route PC. Smoke thêm 3 route mobile 391×844 (rule nằm trong `@media min-width:1200px` nên mobile phải **bất biến**).
- Overflow ngang = 0 ở cả 2 breakpoint.

## 6. Ghi sheet (sau khi deploy UAT)

- Cột P: `UAT | YYYY-MM-DD HH:mm | commit: <sha> | URL: /portal`
- Cột K: `FIX: nâng specificity rule sidebar 300px + loại .navbar-container khỏi margin-left + chuẩn hoá content-wrapper 24px/72px | IMPACT: toàn bộ shell PC ≥1200px (mọi trang portal) | RETEST: 1920×1080 đo sidebar 0–300, navbar-container x=300, store block x=324, content-body x=324, wrapper y=72 | LIMIT: <ghi nếu grid sidebar chưa khớp 100% source>`
- Cột R: `Custom` · Cột O: `BA/Tester` · thêm 1 dòng `7. ISSUE HISTORY` cho **từng** issue ID.
