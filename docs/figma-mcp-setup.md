# Figma ↔ Code — MCP setup (Wujia)

> **Mục tiêu.** Nối file Figma Wujia vào codebase để Claude Code đọc design → sinh/đối chiếu
> code. Dùng **Framelink `figma-developer-mcp`** (community, free, chỉ cần Personal Access Token,
> chạy với mọi tài khoản Figma). Không dùng official Dev Mode MCP (cần Dev seat trả phí +
> Figma desktop mở sẵn).
>
> **File Figma Wujia:** `https://www.figma.com/design/vfVcqN5zPJvlcjZU4NYim0/Wujia`
> → **file key = `vfVcqN5zPJvlcjZU4NYim0`**

---

## 1. Tại sao Framelink (community) thay vì official

| | Framelink `figma-developer-mcp` | Official Dev Mode MCP |
|---|---|---|
| Chi phí | **Free**, mọi tài khoản | Cần **Dev/Full seat trả phí** |
| Cần gì | 1 Personal Access Token (PAT) | Figma **desktop** mở + plan Professional+ |
| Hướng | Đọc design → code (đúng nhu cầu) | Thêm code-to-canvas, Code Connect |
| Transport | stdio / HTTP | localhost:3845 (desktop) |

→ Nhu cầu của ta là **đọc Figma → đối chiếu/sinh CSS token** ⇒ Framelink đủ và rẻ.

---

## 2. Tạo Figma Personal Access Token (PAT)

1. Đăng nhập Figma (web) → góc trên-phải avatar → **Settings**.
2. Tab **Security** → mục **Personal access tokens** → **Generate new token**.
3. Đặt tên (vd `wujia-mcp`), chọn scopes:
   - **File content: Read** (bắt buộc — để đọc node/layout/style).
   - *(tùy chọn, nếu sau này lên plan trả phí)* **Variables: Read**, **Dev resources: Read**.
4. **Copy token ngay** (Figma chỉ hiện 1 lần). Dạng `figd_...`.

---

## 3. Cất token an toàn (KHÔNG commit)

Token đi vào [`.env.local`](../.env.local) — file đã được `.gitignore` (cùng chỗ với `GITHUB_TOKEN`).
Thêm dòng:

```
FIGMA_API_KEY=figd_xxxxxxxxxxxxxxxxxxxxxxxx
```

`.mcp.json` (committed) **chỉ tham chiếu** `${FIGMA_API_KEY}` — không bao giờ chứa token thật.

Export biến vào shell trước khi mở Claude Code (fish):

```fish
# nạp .env.local vào session hiện tại
for line in (cat /home/huyban/odoo-dev/WujiaTea/.env.local)
    set -gx (string split -m1 '=' $line)
end
# kiểm tra
echo $FIGMA_API_KEY
```

(bash/zsh: `set -a; source .env.local; set +a`)

---

## 4. Bật MCP server trong project

File [`.mcp.json`](../.mcp.json) ở root project đã khai báo server `figma` (project-scoped,
chia sẻ cho cả team):

```json
{
  "mcpServers": {
    "figma": {
      "command": "npx",
      "args": ["-y", "figma-developer-mcp", "--figma-api-key=${FIGMA_API_KEY}", "--stdio"]
    }
  }
}
```

Sau khi `FIGMA_API_KEY` có trong env:

```bash
claude mcp list          # phải thấy: figma
```

Lần đầu Claude Code sẽ hỏi **approve** project MCP server `figma` → chọn Yes.
(`npx -y` tự tải `figma-developer-mcp` lần đầu, cần Node.js đã cài.)

---

## 5. Cách dùng trong session

1. Mở 1 frame trong Figma → copy URL, lấy **node-id** ở query (`?node-id=123-456`).
2. Trong chat, yêu cầu Claude đọc node đó. Claude gọi tool figma MCP với:
   - **file key**: `vfVcqN5zPJvlcjZU4NYim0`
   - **node-id**: lấy ở bước 1
3. Framelink trả về layout + style đã rút gọn (LLM-friendly) + tải được image/SVG.
4. Đối chiếu với [`wujia-design-system.md`](wujia-design-system.md) → chỉnh `_variables.css`
   nếu token lệch (nhớ regression check + bump `?v=` theo gotcha §9).

> Workflow điển hình: "đọc frame `<node-id>` của file Wujia, so token màu/spacing với
> `_variables.css`, liệt kê chỗ lệch" → rồi mới quyết sửa.

---

## 6. REST API fallback (optional, cho CI/headless — chưa build script)

Khi cần chạy ngoài session Claude (vd CI, export token tự động), dùng thẳng REST API
với header `X-Figma-Token: $FIGMA_API_KEY`:

```bash
KEY=vfVcqN5zPJvlcjZU4NYim0
# Toàn bộ document tree
curl -s -H "X-Figma-Token: $FIGMA_API_KEY" \
  "https://api.figma.com/v1/files/$KEY"
# 1 node cụ thể
curl -s -H "X-Figma-Token: $FIGMA_API_KEY" \
  "https://api.figma.com/v1/files/$KEY/nodes?ids=123:456"
# Render PNG/SVG 1 node
curl -s -H "X-Figma-Token: $FIGMA_API_KEY" \
  "https://api.figma.com/v1/images/$KEY?ids=123:456&format=png&scale=2"
# Published styles (color/text styles)
curl -s -H "X-Figma-Token: $FIGMA_API_KEY" \
  "https://api.figma.com/v1/files/$KEY/styles"
```

> `/v1/files/$KEY/variables/local` (Figma Variables) chỉ khả dụng trên **plan trả phí** +
> scope Variables:Read. Đây mới là "design tokens" chuẩn để auto-sync 2 chiều sau này.
> Hiện chỉ ghi tham khảo — **chưa** viết script `scripts/figma_pull.py`.

---

## 7. Ghi chú: vì sao summary giữ `.md`, không convert `.html`

(Quyết định 2026-06-02, kèm task Figma.)

- **Claude Code đọc Markdown hiệu quả hơn HTML**: ít token, ít noise tag (`<div>/<p>/<table>`),
  cấu trúc sạch → giữ `wujia-compact-summary.md` và `wujia-design-system.md` ở **markdown**.
- File summary được `/wujia-start` đọc trực tiếp qua Read tool → markdown là format tối ưu,
  deterministic.
- HTML chỉ hơn khi cần **người** xem trên browser có style — việc đó `wujia-tea-doc.pdf`
  đã lo. Nếu thật sự cần bản browser, build **HTML/PDF dẫn xuất** từ md (một chiều), giữ md
  làm nguồn:
  ```bash
  pandoc docs/wujia-design-system.md -o docs/wujia-design-system.pdf   # hoặc .html
  ```
- ⇒ **Không** đổi nguồn sang html. md là source, html/pdf chỉ là artifact dẫn xuất khi cần.

---

## 8. Đọc structure (không phải ảnh) + xử lý Figma "phẳng"

### 8.1 API trả về structure, không phải pixel
Mỗi node trong file Figma là JSON có: `type` (FRAME/RECTANGLE/TEXT/VECTOR/GROUP/COMPONENT/INSTANCE),
`name`, `absoluteBoundingBox` (x/y/**W×H px**), `fills` (**màu hex**), `cornerRadius` (**bo góc**),
`strokes` + `strokeWeight`, `effects` (**shadow**), và với TEXT: `style.fontSize/fontWeight/fontFamily`
+ màu chữ. Auto-layout: `layoutMode` + `itemSpacing` (gap) + `padding*`.

⇒ Đọc được **đâu là button/card/field, to bao nhiêu, màu gì, bo góc bao nhiêu, font ra sao** — đủ
dựng code, không phải đoán bằng mắt. Render PNG (`/v1/images`) chỉ để **người** xem.

Ví dụ trích từ màn "Add to cart" (2026-06-02):
- Button "Chuyển đến giỏ hàng": `FRAME 184×44`, bg `#000000`, radius `10`, text `16px/700` `#FFFFFF`.
- Stepper số lượng: `FRAME 83×38`, bg `#FFFFFF`, text "− 1 +" `14px/700` `#000000`.
- Field cyan: `RECTANGLE 357×50`, bg `#00ADEF`, radius `10`.

### 8.2 ⚠️ Figma hiện "phẳng" — card KHÔNG phải container
Trong file Wujia hiện tại, nhiều "card" nhìn là 1 khối nhưng designer xếp các phần
(title + status + progress bar + text + nền) **cùng cấp (siblings)**, KHÔNG node nào bọc node nào.
Đã verify: card "KHUNG GIỜ ĐẶT HÀNG" → tìm rect bao trọn title = **0** (không có container).
Khung 358×92 nét đứt khi click = **selection của Figma**, không phải 1 node.

### 8.3 Cách mình xử lý — geometry grouping
Vì có `absoluteBoundingBox` cho mọi node → gom theo **toạ độ** thay vì hierarchy:
1. Xác định vùng card (từ rect nền, hoặc cụm theo vị trí + kích thước đã biết).
2. Lấy mọi node có bbox **lọt trong vùng** đó → tái dựng "card logic" (title/status/bar/text).
3. Dùng vị trí tương đối + font + màu để map sang component `.wujia-content-card` / `.wujia-kpi-card`.

Đây là cách chuẩn các tool design→code rebuild cây phân cấp từ Figma lộn xộn. **Heuristic** —
chạy tốt nhưng có thể nhầm khi nhiều card sát/chồng nhau.

### 8.4 Đề nghị cho BA (làm Figma "MCP-friendly")
Để design→code sạch + sync 1-1 (giảm đoán):
- **Bọc nội dung mỗi card vào 1 Frame + auto-layout** → card thành container thật, gap/padding đọc trực tiếp.
- **Dùng Component** cho phần lặp (button, card, KPI) + **đặt tên** rõ (`Button/Primary`, `Card/KPI`).
- **Tạo Color/Text styles + Variables** đặt tên trùng token (§7) — hiện published styles = 0, màu hardcode
  (còn lệch nội bộ: cyan `#00ADEF` ở Add-to-cart vs `#28A9DF` ở Dashboard).
- Đặt tên layer có nghĩa thay vì `Rectangle`/`Frame` mặc định.

---

## 9. Nhiều màn / file lớn — scale + tránh rate-limit

Rate-limit Figma là **cost-based**: kéo CẢ FILE (mọi màn) = đắt → dễ `429`; kéo **1 màn (node-id)** = rẻ.
File nhiều màn KHÔNG sao — chỉ cần **làm từng màn một**, đừng slurp cả cây.

**Workflow đúng khi nhiều màn:**
1. **Index trước (1 call nông, rẻ):** `GET /v1/files/{KEY}?depth=1` (list pages) hoặc `depth=2` (pages + frames) → lấy node-id từng màn.
2. **Drill từng màn:** `GET /v1/files/{KEY}/nodes?ids=<node-id>` — chỉ màn đang cần.
3. **Render ảnh per-frame:** `GET /v1/images/{KEY}?ids=<node-id>` khi cần xem.
4. **Cache** JSON/PNG (vd `/tmp/wujia_figma/`) để khỏi pull lại.
5. **Giãn nhịp** — đừng >10 call/phút. Dính `429` thì nghỉ ~1–3 phút (cost budget hồi lại).

**Framelink MCP vs REST trần:** MCP target node-id + simplify/dedupe response (giảm token) → hợp file
lớn hơn REST thô. Vẫn chung quota token nên vẫn theo per-screen.

> Note: `429` gặp 2026-06-02 là do demo gọi dồn cả tree, KHÔNG phải giới hạn bản chất. Dùng đúng
> workflow per-screen thì file bao nhiêu màn cũng chạy ổn.

---

## 10. Cơ chế + giới hạn free + "treo" không?

**Cơ chế:** Framelink chạy local (`npx`, stdio). Claude gọi tool (`get_figma_data`/`download_images`)
với file-key + node-id → MCP gọi Figma REST API (token bạn) → **simplify** JSON (gọn token) →
trả Claude + tải ảnh/SVG. Read-only.

**Free yếu không?** Framelink free = **lựa chọn free tốt nhất**: official free bị cap ~6 call/tháng;
Framelink dùng rate-limit Figma API chuẩn (rộng hơn). Free KHÔNG có: Code Connect + đọc Figma
Variables (cần Figma plan trả phí — giới hạn của Figma). Đọc screen lấy px/màu/structure → đủ mạnh.

**Sửa nhiều / xem nhiều trang có treo?** Không — mỗi call độc lập, Edit code và xem Figma là 2 bước
riêng. 2 ma sát (né được, KHÔNG phải treo): (1) `429` nếu kéo dồn → nghỉ 1–3 phút; (2) context phình
nếu nạp nhiều màn 1 lúc → làm per-screen + cache. Task nhiều màn: index 1 lần → loop {pull 1 màn →
sửa code → màn kế}. Mẹo nặng: render PNG cả lượt (rẻ) để tổng quan, JSON chỉ pull màn đang code.
