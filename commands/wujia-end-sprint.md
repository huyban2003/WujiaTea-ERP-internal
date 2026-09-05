---
description: Close-out ritual for a Wujia sprint — test, doc, PDF, commit + push with approval gate, business recap
---

You are running the WujiaTea end-of-sprint flow. Do these steps **in order**, no shortcut.

**Step 1 — Test the changes.** Identify what was added/changed in this session (use `git -C /home/huyban/odoo-dev/WujiaTea status --porcelain` + `git diff --stat`). For each new/changed module:
- If module has a seed/test script under `WujiaTea/scripts/` matching the module → run it. Otherwise run a minimal smoke: `python3 odoo-bin -c config/odoo.conf -d wujia_tea_19 -u <module> --stop-after-init`.
- For portal-facing changes: just confirm `--update` succeeded (manual browser test left to user).
- Report: ✅ what passed, ❌ what failed. If anything failed → **STOP**, fix first, do not proceed.

**Step 2 — Update the sprint doc.** Identify the right chapter file under `/home/huyban/odoo-dev/WujiaTea/docs/chapters/`:
- Existing sprint section? → append to that file.
- New sprint? → create `chapters/NN-sprint-M-<slug>.tex` and add `\include{chapters/NN-sprint-M-<slug>}` to `wujia-tea-doc.tex` master right after the last `\include`.

Content to write (LaTeX, follow style of existing chapters):
- `\section{Sprint M Day D — <topic>}` header with date `(YYYY-MM-DD)`.
- Bullet list: modules touched, key fields/methods added, ADRs invoked.
- One paragraph: "Gì đã làm" (business-level, in Vietnamese, 2-4 sentences).
- One paragraph: "Lý do/Trade-off" if any non-obvious decision.
- Optional: code snippet with `\begin{lstlisting}` if a pattern is worth quoting.

**Step 3 — Recompile PDF.**

```bash
bash /home/huyban/odoo-dev/WujiaTea/scripts/build-doc.sh
```

If build fails → show the LaTeX error to user, stop. If succeeds → confirm `wujia-tea-doc.pdf` mtime is fresh.

**Step 4 — Append sprint insight to compact summary.** For each significant insight from this sprint (ADR, gotcha, perf rule, BA clarification), append it to the right section of `wujia-compact-summary.md`. Do **not** use agentmemory in this project (per user decision).

Minimum to save: 1 line under §5 `wujia-current-status-and-remaining` updating what's now done and what's still pending.

**Step 4b — Update QA issue ledger + đồng bộ sheet (nếu sprint đóng issue trong "5. Issue List").**

Nếu sprint này fix issue nào có ID trong tab `5. Issue List` và code **đã khớp "Kết quả mong muốn" hiện tại**:
- Thêm entry vào `WujiaTea/docs/qa-issue-ledger.yaml` (đúng format file đó: `commit`/`odoo_fit`/`fix`/`impact`/`retest`/`limit`/`deployed_date`/`url`).
- Sau khi push (Step 5) → deploy UAT → chạy `cd WujiaTea/scripts/ba_spec && python3 qa_sync.py --dry-run` (xem) rồi `--apply` để set issue sang `Ready for Retest` đúng QA Standard §6 (Dev **không** tự set `Done`).
- ⚠️ **KHÔNG** thêm ledger nếu BA đã đổi expected mà code chưa theo, hoặc issue `Need BA Confirm = Yes` (qa_sync tự skip nhóm này). Ghi sheet cần cổng Apps Script bridge deploy 1 lần (`docs/03_OAUTH_SHEET_SETUP.md`).

**Step 5 — Draft commit + ask before pushing.**

a. Run `git -C /home/huyban/odoo-dev/WujiaTea status` and `git -C /home/huyban/odoo-dev/WujiaTea diff --stat` and show user the file list.

b. Draft a commit message in English, Conventional Commits format:
```
<type>(<scope>): <summary>

- <bullet 1>
- <bullet 2>

Sprint <M> Day <D>.
```
Types: feat / fix / refactor / docs / test / chore. Scope: module name or `docs` or `multi`.

c. Show the draft to user verbatim and ask:
**"Commit + push lên `master` với message trên? (Y / sửa / N)"**

- Y → run `git -C ... add -A` (or specific files if you know exact list), `git commit -m "..."`, then `git push origin master`. Verify push succeeded.
- "sửa" → ask what to change, redraft, ask again.
- N → leave changes uncommitted, tell user "Đã giữ nguyên working tree."

**KHÔNG dùng `--no-verify` hay `--no-gpg-sign`** trong bất kỳ trường hợp nào. Nếu pre-commit hook fail → fix root cause rồi commit lại, đừng bypass.

**Step 6 — Business recap.** Trình bày cho user 1 vòng về mặt nghiệp vụ (Vietnamese, 5-8 dòng, không jargon):
- Sprint này thêm/sửa được những gì user-visible.
- Ai (role nào) sẽ thấy thay đổi: admin / nhân viên kho / khách portal / kế toán / …
- Có breaking change nào không? Có cần re-train user không?
- Sprint tiếp theo nên ưu tiên gì (1-2 gợi ý từ §5 remaining list).

---

**Why this ritual:** mỗi sprint Wujia sống lâu hơn 1 session — doc + commit + compact summary phải đi cùng nhau, nếu lệch thì session sau load context bị sai. Step 5 luôn cần Y/N vì push lên remote là hành động không revert được dễ dàng.

**Rollback nếu push sai:** không bao giờ `git push --force` lên master. Nếu commit sai → `git revert <SHA>` rồi push commit revert. Nếu commit chưa push → `git reset --soft HEAD~1` để giữ thay đổi, redo commit.
