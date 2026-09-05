---
description: Load WujiaTea kickoff context — reads compact summary directly, no MCP dependency
---

You are starting a WujiaTea session. Do these steps **in order**, no shortcut:

**Step 1.** Read the compact summary file directly:

```
Read tool → /home/huyban/odoo-dev/WujiaTea/docs/wujia-compact-summary.md
```

It has: §1 overview, §2 modules, §3 ADR summary, §4 sprint history, §5 current status, §6 deploy, §7 start instruction, §8 session template, §9 sprint-9 history, §10 lessons, §11 shared-utils, **§12 QA · UAT · Nightly agent**.

**Step 2.** Apply §7 (start-instruction) as the operating rules for **the entire conversation**:

- Project paths: v14 reference at `/home/huyban/odoo-dev/wujia_tea_odoo14`, v19 active at `/home/huyban/odoo-dev/WujiaTea`.
- BA spec = **Google Sheet "Internal ERP Master Plan_Update"** online (§7 tab/gid; xlsm local = legacy fallback).
- **UAT (dev server): `http://113.161.187.126:8019/`** — login `admin/Wujia@2026`. Có thể tự smoke-test (đọc/nhìn), theo giới hạn QA §10 (không tạo đơn/hoá đơn/email thật).
- **QA Operating Standard** = `docs/01_NGO_GIA_QA_OPERATING_STANDARD.md`: Dev KHÔNG tự đóng `Done`, chỉ tới `Ready for Retest` (+ Build/Deploy, FIX/IMPACT/RETEST/LIMIT, Odoo Fit, dòng History). Xong issue → `scripts/ba_spec/qa_sync.py`.
- Progress doc: `WujiaTea/docs/wujia-tea-doc.pdf` (split into `chapters/` since 2026-05-16).
- **UI-only rule**: button có nhưng chưa cần wire backend, miễn layout đúng BA.
- **Performance-first**: portal 1500 user → ormcache, store + index field tính toán phổ biến, cron daily thay vì compute on-the-fly.
- **Ask-don't-assume**: không chắc → hỏi, đừng tự code.
- **Read-before-write**: xem v19 hiện tại đã có gì rồi mới làm tiếp.
- **End of sprint**: update sprint log + `.tex` (file con trong `chapters/` tương ứng) + recompile PDF qua `WujiaTea/scripts/build-doc.sh`.
- **End of session**: trình bày 1 vòng về mặt nghiệp vụ — đã làm được gì.

**Step 2b (BẮT BUỘC, trước khi hỏi task).** `Tasks!STT1` = "Fix lỗi issue list" là task
thường trực, **ưu tiên CAO NHẤT**. Tab `5. Issue List` BA cập nhật liên tục nên phải check
mỗi phiên:

```
cd /home/huyban/odoo-dev/WujiaTea/scripts/ba_spec && python3 issue_queue.py --dev
```

- Có issue `Ready for Dev` / `Retest Failed` (Owner=Dev, Need BA Confirm≠Yes) → báo ở Step 3
  và **đề xuất làm trước mọi task khác**.
- ⚠️ **Reconcile code ↔ sheet trước khi nhận việc**: `git log --all -S"<ISSUE-ID>"` +
  `grep -rn "<ISSUE-ID>" custom/`. Issue có thể ĐÃ fix mà sheet chưa sync (WJ-ORD-023 fix
  `63dc4bc` 08-04, sheet vẫn `Ready for Dev` tới 08-10) → chỉ cần ledger + `qa_sync.py`,
  KHÔNG code lại.
- **KHÔNG làm hết một lượt** — bám bảng batch §13 compact summary, mỗi session một batch.
- Xong mỗi issue phải **đối chiếu cột `Kết quả mong muốn` của chính issue, đạt ≥90%** rồi
  mới ghi ledger (§13).

**Step 3.** Echo to user a status snapshot. **Fill EVERY value dynamically from the Read** —
do NOT hardcode a sprint number, module count, or chapter count (the file moves fast; the old
template said "Sprint 5 / 16 modules" and was stale within weeks):

```
✓ Wujia session ready — <latest sprint + one-line outcome, from §5 State header>.
  Project type: Odoo 19 ERP + Vuexy portal, ~1500 user target.
  Last sprint: <most recent sprint + date + chapter, from §4/§5>.
  Still pending: <list the live pending/deferred bullets from §5>
  Modules: <count from §2 heading> active.
  Issue List: <n> Ready for Dev — batch kế: <Bx từ §13>.
  Docs: WujiaTea/docs/wujia-tea-doc.tex (master) + chapters/.
```

**Step 4.** Ask the user: **"Sprint/task nào hôm nay?"** — wait for their answer before doing anything else.

---

**Controller task workflow (BA gửi spec qua ChatGPT + xlsm):**

Từ Sprint 30, **mọi task controller BA giao đều nằm trong 1 chat ChatGPT share** + đối chiếu
`docs/Wujia_Internal ERP Master Plan.xlsm`. Khi user yêu cầu "làm controller <X>":

1. **Đọc chat BA** — chạy `python3 WujiaTea/scripts/ba_spec/fetch_ba_chat.py "<share_url>" -o /tmp/ba_X.md`
   rồi Read file đó (parse turbo-stream ra bảng controller mapping BA).
2. **Dump xlsm** đối chiếu: `python3 WujiaTea/scripts/ba_spec/read_xlsm.py "1. Model Field" <kw>`
   (+ sheet `2. FE - Portal`, `3. Controller`, `FEATURE CHECKLIST`).
3. **Đối chiếu spec BA ↔ source model THẬT** (`custom/<mod>/models/`). ⚠️ BA hay đặt tên model/field
   **lý tưởng hoá** khác source (vd sheet ghi `wujia.announcement` nhưng module thật là
   `wujia.notification`; priority keys lệch nhau). Luôn `grep -rn "_name = '"` trước khi code.
4. **Hỏi ở mọi fork** (đổi tên model / schema change / read scope / targeting…) — đừng tự quyết.
5. **Perf-first 1500 user**: read/unread = 1 batched query + index kép, không query per-record.

Toolchain `scripts/ba_spec/` là **dev-only, gitignored, KHÔNG lên server** (xem README trong đó).

---

**QA sheet writeback + Nightly agent (từ 2026-07-21):**

- BA log việc lên tab **`Tasks`** + lỗi lên tab **`5. Issue List`** của Google Sheet. Chuẩn lên task cho agent: `docs/02_TASKS_INTAKE_SPEC_FOR_GPT.md` (đã gửi BA/GPT).
- **Làm xong 1 issue** → thêm entry vào `docs/qa-issue-ledger.yaml` rồi `cd scripts/ba_spec && python3 qa_sync.py --dry-run` (xem) → `--apply` (ghi sheet: status `Ready for Retest` + P/K/R/J/O + dòng History). ĐỌC sheet = CSV công khai (chạy được ngay); GHI cần cổng Apps Script bridge deploy 1 lần (`docs/03_OAUTH_SHEET_SETUP.md`).
- **Nightly agent** `scripts/ba_spec/qa_nightly/run.sh` (cron 22h local): reconcile Issue List + nếu có task Ready-for-AI thì tự code/test/push (deploy tay). Gặp fork → defer `Need Clarification`.

---

**Why this command reads the file directly:**

Reading the markdown source is deterministic — you always get the full content of the compact summary, which is the single source of session context. Do **not** use agentmemory in this project (per user decision).

If `wujia-compact-summary.md` is missing, fall back to reading `wujia-tea-doc.tex` Chapter 1 directly + tell the user the summary file is gone.
