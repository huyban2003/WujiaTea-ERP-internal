---
description: Load Wujia Dashboard migration context — Dashboard Ninja v16/v18 → Odoo 19, đọc state file, áp rule, hỏi task
---

You are starting a **Wujia Dashboard migration** session (workstream con của WujiaTea). Do these steps **in order**, no shortcut:

**Step 1.** Read the state file directly (single source of truth của workstream này):

```
Read tool → /home/huyban/odoo-dev/WujiaTea/docs/dashboard-migration-plan.md
```

Nó có 6 section: §1 bối cảnh + quyết định chốt, §2 step table + active step, §3 rename discriminator rules, §4 gotchas log, §5 module paths, §6 kiến trúc port advance/formula.

**Step 2.** Read `wujia-compact-summary.md` **§5 + §7 ONLY** (không đọc cả file — tiết kiệm context):

```
Read tool → /home/huyban/odoo-dev/WujiaTea/docs/wujia-compact-summary.md (Grep "## §5" / "## §7" để lấy offset)
```

**Step 3.** Apply operating rules cho cả session (bổ sung trên rule Wujia thường):

- **Model `_name` KHÔNG ĐỔI** (`ks_dashboard_ninja.*`, `ks_dn.*`) — chỉ module dir/asset path/template name/XML id/route mang prefix `wj_`. Rename theo §3 discriminator rules, soát sót bằng grep sau mỗi sed.
- **License GIỮ `OPL-1`** — code Ksolves, không relabel. Không redistribute; v18 gốc + v16 gốc là read-only reference.
- **Đọc §4 Gotchas TRƯỚC khi code** — đa số bug đã được adversarial review bắt sẵn (lazy bundle, Ksdashboardlistview chết, safe_eval nocopy, __extra_domain...). Đừng tái phát hiện bằng cách nổ runtime.
- **Tính năng trước, giao diện sau** (user 2026-07-15): không sa đà chỉnh CSS khi feature chưa chạy. Reskin = Step 6 cuối.
- **Verify gate mỗi step** (DoD trong §2): install/upgrade RC=0 → seed ORM → Playwright render + `console.error` = 0 → regression `scripts/test_sprint9.py` 7/7.
- **Ask-don't-assume + Read-before-write** như mọi session Wujia. So code với v16 gốc khi port advance/formula (feature reference), với v18 gốc khi debug core (bản chuẩn chưa sửa).
- Local dev: conda env `odoo`, DB `wujia_tea_19`, config `WujiaTea/config/odoo.conf`, log `WujiaTea/logs/odoo.log`. Module MỚI cần `-i` (không phải `-u`) lần đầu — cả local lẫn prod (gotcha #15).

**Step 4.** Echo status snapshot — **fill từ state file, không hardcode**:

```
✓ Wujia Dashboard session ready — Step <N>: <tên step> (<status>).
  Sprint hiện tại: <sprint của active step, hỏi user nếu TBD — sprint number lấy tại thời điểm làm>.
  Done: <các step DONE, 1 dòng>.
  Gotchas đang sống cho step này: <lọc §4 những gotcha áp cho step N>.
  Modules: <paths từ §5 đã tồn tại/chưa>.
```

**Step 5.** Ask user: **"Task hôm nay trong Step <N>, hay chuyển step?"** — đợi trả lời rồi mới làm.

---

**Cuối step (bắt buộc, giống `/wujia-end-sprint` nhưng thêm state file):**

1. Chạy đủ DoD gate của step (§2) — fail thì STOP, fix trước.
2. **Update state file** `dashboard-migration-plan.md`: status step, sprint number thật, gotcha mới phát hiện (append §4, đánh số tiếp), active step chuyển tiếp.
3. Update `wujia-compact-summary.md` §5 (1–2 dòng) + sprint table §4.
4. Doc chapter `.tex` + `build-doc.sh` + commit qua `/wujia-end-sprint` (Y/N gate trước push).

---

**Why this skill:** workstream dashboard chạy multi-session (6 step), xen kẽ với sprint portal khác. State file là bộ nhớ duy nhất giữa các session — đọc trực tiếp file markdown là deterministic, không dùng agentmemory (per user decision). Sprint number KHÔNG cố định theo step vì các session portal song song cũng tiêu thụ sprint number.

If `dashboard-migration-plan.md` is missing → fall back đọc plan gốc `/home/huyban/.claude/plans/tingly-juggling-boot.md` + báo user state file mất.
