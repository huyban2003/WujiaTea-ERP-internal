---
description: Load Beesuite CORE kickoff context — dev lõi dùng chung (beesuite2.0), sửa lan mọi client, focus theme/backend
---

You are starting a **Beesuite CORE** session. Đây là **LÕI dùng chung** — KHÁC client (VTM/Draho/Wujia/GNF): sửa ở đây lan ra mọi deployment. Do these steps **in order**, no shortcut:

**Step 1.** Read the compact summary file directly:

```
Read tool → /home/huyban/odoo-dev/beesuite2.0/docs/beesuite-compact-summary.md
```

5 mục: §1 overview, §2 nhóm module, §3 conventions, §4 theme stack, §5 credentials pointer.

**Step 2.** Apply §3 (conventions) as operating rules cho **toàn session**, đặc biệt:

- **Repo**: `/home/huyban/odoo-dev/beesuite2.0/` (core monorepo, `.git` RIÊNG). Core web Odoo 16 ở `/home/huyban/odoo-dev/odoo16/addons/web`.
- **Scope (BẮT BUỘC):**
  - ✅ Được sửa `beesuite_*` **TRỰC TIẾP** (đây là source — ngược với client nơi beesuite là override-only).
  - ⚠️ Mọi sửa đổi **lan ra TẤT CẢ client** → backward-compatible, KHÔNG breaking; tính năng mới ưu tiên cờ cấu hình thay vì đổi mặc định.
  - ❌ KHÔNG đụng deployment client từ session core: `vietthuong/`, `draho/`, `WujiaTea/`, `gkitchen/`, `pgi/`, `gotco/`, `viet-thanh/`, `landed_cost_*/`, `bms/`.
- **Read-before-write** (module nhiều, pattern không đồng nhất). **Ask-don't-assume** với nghiệp vụ ảnh hưởng nhiều client.
- **Commit**: tiếng Việt, ngắn gọn. **Credentials**: agentmemory `type="secret"` `["beesuite","credentials",<service>]`, KHÔNG vào markdown.

**Step 3.** Echo cho user 6 dòng status snapshot (rút từ §1 + §2 + §4):

```
✓ Beesuite CORE ready — lõi dùng chung (beesuite2.0/, .git riêng), nền Odoo 16 CE (OWL 2.2.5).
  Quy mô: ~688 manifest. Nhóm lớn: tools 171, POS 111, sales 78, base 73, accounting 57.
  ⚠️ Sửa CORE = lan ra mọi client (VTM/Draho/Wujia/GNF/PGI/Gotco…) → backward-compatible.
  Theme stack: themes/ (8 nhóm), base = muk_web_theme.
  🎨 Dự án mở: beesuite_web19_theme — port áo v19. Phase 0→5 XONG (15 file SCSS), live beesuite_1305:8069. Tiếp: muk19 shell + tinh chỉnh.
  ⭐ Làm tiếp → ĐỌC docs/v19-theme-porting-guide.md (method + bảng root-cause + next steps). Status đầy đủ ở summary §4.
  DB test: beesuite_1305 / beesuite_tt99_clean (config/beesuite.conf, port 8069).
```

Số trên từ summary tại thời điểm tạo. Nếu summary đã update → echo theo số mới (đọc từ §2), không bịa.

**Step 4.** Optionally call `memory_smart_search` (agentmemory MCP) nếu user nhắc topic cần ad-hoc recall (vd quirk theme, decision module core trước đó). Skip nếu task fresh.

**Step 5.** Hỏi user: **"Task core gì hôm nay?"** — đợi trả lời trước khi làm gì khác.

> **Nếu task liên quan theme v19 / `beesuite_web19_theme` (làm tiếp, sửa, muk19…):** BẮT BUỘC đọc trước `docs/v19-theme-porting-guide.md` (method, nguyên tắc global, bảng root-cause đã trace, quy trình compile→update→restart) + `docs/v19-muk-shell-backport-TODO.md` (nếu làm muk shell). Rồi mới code. Module: `beesuite2.0/themes/beesuite_web19_theme/`.

---

**Why đọc file trực tiếp thay vì agentmemory recall:** tool agentmemory trả `mode: compact` (titles only), không reliably fetch body. Đọc markdown deterministic — luôn full content. agentmemory vẫn dùng để save/search ad-hoc insight trong session.

**Khi scope đổi (thêm/bớt module, đổi theme stack, …):** edit thẳng [beesuite-compact-summary.md](/home/huyban/odoo-dev/beesuite2.0/docs/beesuite-compact-summary.md) §2/§4.

**Nếu summary file mất** → fallback:
1. `ls /home/huyban/odoo-dev/beesuite2.0/` → biết các nhóm.
2. `find /home/huyban/odoo-dev/beesuite2.0 -maxdepth 3 -name __manifest__.py | wc -l` → đếm module.
3. `ls /home/huyban/odoo-dev/beesuite2.0/themes/` → theme stack.
4. Rebuild summary, báo user lưu lại file.
