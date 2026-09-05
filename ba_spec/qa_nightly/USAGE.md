# Nightly Dev Agent — INTERACTIVE trong tmux (cách xài)

> Default từ **2026-07-22**: agent nightly chạy **interactive** (opus/xhigh, HỎI ở mỗi fork)
> trong **tmux**, không còn headless. User luôn ngồi trực → attach vào xem + trả lời.

---

## 1. Nó là gì / làm gì
- Mỗi **22:00** cron tự mở phiên `claude` interactive trong tmux tên **`wujia-nightly`**.
- Agent: đọc context → **làm HẾT issue Dev-actionable** (`issue_queue.py --dev`, ưu tiên
  Critical>High>Medium>Low) + **review lại issue `Ready for Retest`** xem code có khớp
  "Kết quả mong muốn" chưa → mỗi issue 1 branch, `-u <module>` RC=0 → **hỏi trước khi push main**
  → xong thì ghi ngược sheet (`qa_sync --apply`, set `Ready for Retest`, KHÔNG `Done`).
- Gặp **fork** (spec mơ hồ / tên model lệch source / cần quyết định) → **HỎI bạn ngay và chờ**.

## 2. Vào lái nó (attach)
Mở **terminal thường** trong VSCode (Terminal → New Terminal), rồi:
```bash
tmux attach -t wujia-nightly
```

## 3. Trả lời prompt xin phép Bash
```
 Bash command: python3 issue_queue.py --status
 Do you want to proceed?  ❯ 1. Yes   2. Yes, and don't ask again   3. No
```
- Bấm **số** (`1`/`2`/`3`) hoặc mũi tên ↑↓ + Enter.
- **Cứ `2`** cho các lệnh lặp vô hại: `issue_queue.py`, `task_sync.py`, `qa_sync.py`,
  `read_xlsm.py`, `git status/log/checkout/commit`, `grep`, `-u <module>` (chỉ đụng DB dev).
- **RIÊNG `git push`** → bấm **`1`** (Yes 1 lần) để nó vẫn hỏi mỗi lần trước khi đẩy lên server.
- File-edit: mode `acceptEdits` tự nhận, không hỏi.

## 4. Trả lời câu hỏi nghiệp vụ (fork)
Agent hỏi spec/quyết định → **gõ câu trả lời** vào ô nhập cuối màn hình → **Enter**.
(Gõ bình thường = gõ vào Claude. Muốn ra lệnh cho tmux thì bấm `Ctrl-b` trước.)

## 5. Phím tmux cốt lõi (prefix = `Ctrl-b`)
| Việc | Thao tác |
|---|---|
| Rời ra, agent VẪN chạy | `Ctrl-b` rồi `d` (detach) |
| Vào lại | `tmux attach -t wujia-nightly` |
| Cuộn đọc lịch sử | `Ctrl-b` rồi `[` → ↑↓/PageUp → `q` thoát |
| Liệt kê phiên | `tmux ls` |
| Dừng hẳn agent | trong phiên `/exit` hoặc `Ctrl-C`; ngoài: `tmux kill-session -t wujia-nightly` |

## 6. Chạy TAY bất cứ lúc nào (không đợi 22h)
- **Giống hệt cron:** `scripts/ba_spec/qa_nightly/cron-tmux-launch.sh` rồi `tmux attach -t wujia-nightly`.
- **Thẳng trong terminal (thấy inline):** `cd scripts/ba_spec/qa_nightly && ./run-interactive.sh`.
- **Session Claude Code mới:** dán prompt trong `agent_prompt_interactive.md` (hoặc prompt gọn đã đưa).

## 7. File liên quan (đều gitignored — dev-only, KHÔNG lên server)
- `cron-tmux-launch.sh` — cron entrypoint, mở tmux detached (guard trùng phiên).
- `run-interactive.sh` — chạy `claude --model opus --effort xhigh --permission-mode acceptEdits` + seed prompt.
- `agent_prompt_interactive.md` — vai trò/quy trình/phạm vi/guardrails của agent.
- `install-cron.sh install|uninstall` — cài/gỡ cron `0 22 * * *`.
- `run.sh` + `agent_prompt.md` — **bản headless cũ (fallback không-người-trực)**, KHÔNG còn là cron default.
- Log launcher: `logs/qa-nightly-tmux-YYYY-MM-DD.log`.

## 8. Cài lại từ đầu (máy mới)
```bash
sudo apt-get install -y tmux
cd scripts/ba_spec/qa_nightly && ./install-cron.sh install
```

## 9. Trục trặc thường gặp
- **`attach` báo "no server / can't find session"** → phiên chưa mở (chưa tới 22h / chưa launch tay).
  Chạy `cron-tmux-launch.sh` hoặc đợi cron.
- **Muốn agent làm khác phạm vi** → sửa `agent_prompt_interactive.md`.
- **Lỡ mở 2 phiên** → `cron-tmux-launch.sh` đã guard `has-session`, không mở đè; muốn reset thì
  `tmux kill-session -t wujia-nightly` rồi mở lại.
- **Agent kẹt/lỗi** → detach (`Ctrl-b d`), quay lại phiên Claude Code chính nhờ gỡ.
