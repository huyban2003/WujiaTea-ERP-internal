# Bật GHI Google Sheet (Apps Script bridge) + Nightly agent — làm 1 lần

**ĐỌC sheet = công khai** → không cần setup gì (qa_sync dry-run / task_sync --list chạy được ngay).
Chỉ phần **GHI** (đổi trạng thái, ghi chú, thêm dòng History) mới cần cổng.

> Vì sao không dùng OAuth/gcloud: Google **đã chặn** quyền Sheets trên client OAuth mặc định
> ("must provide your own client ID"). Cách gọn + bền nhất: một **Apps Script** gắn trong sheet,
> chạy dưới danh nghĩa tài khoản **Người chỉnh sửa của bạn** (`huyban.han@gmail.com`) nên có quyền ghi.

---

## A. Deploy cổng ghi (làm trong Sheet, ~6 bấm)

1. Mở sheet → menu **Extensions → Apps Script**.
2. Xoá code mẫu, **dán toàn bộ** nội dung file `scripts/ba_spec/qa_nightly/WujiaSheetBridge.gs`.
   (SECRET trong đó đã khớp sẵn với `sheet_endpoint.json` — không cần đổi.)
3. Bấm **Deploy → New deployment** → (bánh răng ⚙️) chọn **Web app**.
4. **Execute as: Me** (`huyban.han@gmail.com`) · **Who has access: Anyone** → **Deploy**.
5. Lần đầu hỏi quyền → chọn tài khoản editor → **Advanced → Go to … (unsafe)** → **Allow**.
6. Copy **Web app URL** (dạng `https://script.google.com/macros/s/…/exec`).

## B. Đưa URL cho AI

Dán URL cho AI, **hoặc** tự sửa `scripts/ba_spec/sheet_endpoint.json` → điền vào `webapp_url`.

## C. Test ghi

```bash
cd /home/huyban/odoo-dev/WujiaTea/scripts/ba_spec
python3 sheet_io.py --ping                 # {ok: true, sheet: Tasks}
python3 task_sync.py --init-headers        # thêm nhãn cột H..R vào tab Tasks
python3 qa_sync.py --dry-run               # xem: UI-01/02/03/05 -> Ready for Retest
python3 qa_sync.py --apply --only UI-01    # ghi thử 1 issue -> mở sheet kiểm cột I/P/K/R/J/O
python3 qa_sync.py --apply --only UI-01    # chạy lại -> "idempotent"
```

> Cần tab **`7. ISSUE HISTORY`** để ghi dòng lịch sử. Chưa có thì tạo tab đó, hàng tiêu đề:
> `Ngày | Issue ID | Trạng thái cũ | Trạng thái mới | Owner | Người cập nhật | Lý do | Build/Deploy | Evidence`.

## D. Bật Nightly agent (cron 22h, trần 3h/đêm)

```bash
./qa_nightly/install-cron.sh install       # cài cron 22:00
./qa_nightly/run.sh                          # chạy thử ngay (không đợi 22h) -> đọc log
```

Log mỗi đêm: `WujiaTea/logs/qa-nightly-YYYY-MM-DD.log`. Máy phải **bật lúc 22h**. Trần thời gian
`WUJIA_NIGHTLY_MAX_HOURS` (mặc định 3) + trần tiền `WUJIA_NIGHTLY_BUDGET` (mặc định $8) — cái nào tới trước.

> ⚠ **Headless không hỏi được bạn:** `run.sh` chạy `claude -p` (một chiều, không TTY) nên
> khi gặp fork nó **KHÔNG hỏi bạn mà ghi `Need Clarification` vào sheet** rồi nhảy task kế.
> Muốn agent **hỏi thẳng + chờ bạn trả lời** thì dùng phiên interactive (mục E).

## E. Phiên INTERACTIVE (có người trực — agent hỏi & chờ bạn)

Khi bạn **ngồi canh máy** (vd 22h) và muốn agent hỏi trực tiếp như Claude Code thường:

```bash
cd /home/huyban/odoo-dev/WujiaTea/scripts/ba_spec
./qa_nightly/run-interactive.sh
```

- In sẵn **bảng trạng thái Issue List** (`issue_queue.py --status`) + task tab Tasks → bạn thấy ngay "hôm nay cần làm gì".
- Mở Claude Code **interactive** (KHÔNG `-p`) seed bằng `qa_nightly/agent_prompt_interactive.md`:
  agent đề xuất việc, **gặp fork thì hỏi bạn và chờ**, được spawn sub-agent (sonnet/low) để dò/khảo sát song song.
- **Nguồn việc hybrid:** ưu tiên tab Tasks (`M=Yes`), hết thì nhặt Issue List `Ready for Dev`
  (`issue_queue.py --dev` — đã lọc Owner=Dev + Need BA Confirm=No).
- Phải chạy trong **terminal thật** (có TTY); cron không dùng được mode này.
- Xem nhanh không cần agent: `python3 issue_queue.py --status` / `--dev`.

## Bảo mật & sự cố

- `sheet_endpoint.json` (URL+secret) đã **gitignored**. Ai có URL+secret mới ghi được → giữ kín;
  lộ thì đổi `SECRET` ở **cả** `WujiaSheetBridge.gs` (re-deploy) **và** `sheet_endpoint.json`.
- Ghi 403/forbidden → sai secret hoặc chưa deploy lại sau khi sửa script.
- Cron báo lỗi auth **claude** headless → chạy `run.sh` tay 1 lần soi log (máy này phải đang đăng nhập Claude Code).

> Phương án dự phòng dùng OAuth client (nếu sau này Google mở lại scope): `gsheet_auth.py` vẫn còn.
