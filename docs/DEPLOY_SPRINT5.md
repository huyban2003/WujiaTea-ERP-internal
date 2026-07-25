# Reseed toàn bộ DB — runbook server Windows

> **Tên file là lịch sử** (viết lần đầu cho Sprint 5, `chapters/13-*.tex` đang trỏ tới) nhưng nội
> dung là **quy trình reseed dùng chung**: khi cần drop + init lại DB rồi seed demo, bất kể sprint.
>
> **Khi nào cần:** commit có **rename / đổi kiểu field** trên model đã có data → Odoo `-u` sẽ
> **drop cột cũ** → hệ thống crash khi đọc record cũ. Nếu data là skeleton (không quan trọng) thì
> drop+init nhanh hơn viết migration.
>
> **Khi nào KHÔNG dùng:** deploy thường (chỉ thêm/sửa code, không đổi schema) → xem
> compact-summary §6: `git pull` + restart service; module MỚI phải `-i` một lần.

---

## TL;DR — 1 lệnh

```powershell
nssm stop Odoo
powershell -ExecutionPolicy Bypass -File D:\wujia-tea\scripts\reseed_full.ps1
nssm start Odoo
```

`reseed_full.ps1` encapsulate hết: set encoding env → drop+create DB → install chain → seed →
smoke test. Bản Linux tương đương: `scripts/reseed_full.sh`
(`DB_NAME=… PG_USER=… PG_PASS=… bash scripts/reseed_full.sh`).

> Biến `$MODULES` trong 2 script đã đủ **18** module (fix 2026-07-25: trước đó thiếu
> `wujia_portal_info_request` + `wujia_portal_order_window`). Module dashboard `wj_ks_*` nằm
> **ngoài** chain — luôn phải `-i` riêng, kèm pip `pandas/xlrd/openpyxl`.

---

## Các bước thủ công (khi không dùng script)

### Bước 0 — Verify code

```powershell
cd D:\wujia-tea
git pull origin main
git log -1 --oneline
```

### Bước 1 — Stop service + backup (tuỳ chọn)

```powershell
nssm stop Odoo
$env:PGPASSWORD = "1"
$env:Path = "C:\Program Files\PostgreSQL\16\bin;" + $env:Path
pg_dump -h 127.0.0.1 -U odoo19 wujia_tea_19 | Out-File -Encoding utf8 D:\backup\wujia_tea_19_$(Get-Date -Format yyyyMMdd_HHmm).sql
```

Backup **bắt buộc** nếu DB có bất kỳ data nào nghi ngờ cần giữ.

### Bước 2 — Drop + create DB

```powershell
dropdb -h 127.0.0.1 -U odoo19 wujia_tea_19
createdb -h 127.0.0.1 -U odoo19 -O odoo19 wujia_tea_19
```

DB name / user / password lấy từ `D:\wujia-tea\config\odoo-server.conf`.
PostgreSQL bin ở `C:\Program Files\PostgreSQL\16\bin\` — **không** có trong PATH mặc định.

### Bước 3 — Install module chain

⚠️ **Set encoding TRƯỚC** — PowerShell mặc định cp1252, Python crash khi log ký tự Đ/â/ô trong tên
module ('Wujia Portal — Đào tạo'). Cần cả 4 (Odoo còn ghi logfile qua `open()`, một mình
`PYTHONIOENCODING` không đủ):

```powershell
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
chcp 65001 > $null
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

```powershell
cd D:\wujia-tea\odoo19
python odoo-bin -c ..\config\odoo-server.conf -d wujia_tea_19 `
  -i wujia_core,wujia_franchise,wujia_sale,wujia_fleet,wujia_delivery,wujia_portal_base,wujia_portal_layout,wujia_portal_sale,wujia_portal_purchase_history,wujia_portal_delivery,wujia_portal_return,wujia_portal_notification,wujia_portal_exam,wujia_portal_knowledge,wujia_portal_report,wujia_portal_support,wujia_portal_info_request,wujia_portal_order_window `
  --without-demo=True --stop-after-init
```

(18 module — danh sách chuẩn ở compact-summary §2. Dashboard `wj_ks_dashboard_ninja` +
`wj_ks_dn_advance` cài riêng, cần pip `pandas/xlrd/openpyxl`.)

### Bước 4 — Seed demo data

```powershell
cmd /c "python odoo-bin shell -c ..\config\odoo-server.conf -d wujia_tea_19 --no-http < D:\wujia-tea\scripts\seed_admin_franchise.py"
cmd /c "… < D:\wujia-tea\scripts\seed_fleet_demo.py"
cmd /c "… < D:\wujia-tea\scripts\seed_portal_demo.py"
cmd /c "… < D:\wujia-tea\scripts\seed_knowledge_demo.py"
cmd /c "… < D:\wujia-tea\scripts\seed_support_demo.py"
```

Seed script khác có sẵn trong `scripts/` khi cần: `seed_notification_demo.py`,
`seed_dashboard_demo.py`, `seed_ui12_demo.py`.
(Demo data **không** vào manifest XML — quy tắc compact-summary §5.)

### Bước 5 — Smoke test

```powershell
cmd /c "… < D:\wujia-tea\scripts\test_sprint5.py"
```

Mong đợi `=== RESULT: 20 PASS / 0 FAIL ===` (1 SKIP cho `batch_id` nếu seed chưa tạo picking —
không phải lỗi). Test sprint sau: `test_sprint9.py`, `test_sprint30/31/32[_http].py`.

### Bước 6 — Start + kiểm portal

```powershell
nssm start Odoo
```

Vào `http://<server-ip>:8019/portal` → login admin → xem Knowledge + Support có data demo.

---

## Phòng ngừa

Commit có **rename / đổi kiểu field** trên model **có data thật** → KHÔNG `git pull` rồi `-u`
thẳng trên prod. Thay vào đó:

1. Viết `<module>/migrations/<new_version>/pre-migrate.py` copy data sang cột mới **trước** khi
   Odoo drop cột cũ (đây là cách đúng, xem `wujia_portal_exam 19.0.3.0.0`).
2. Chỉ drop+init theo doc này khi chấp nhận mất data (skeleton).

## Rollback

```bash
git revert <commit-A>..<commit-B>
git push origin main
# trên server: lặp lại drop+init+seed với code cũ
```

Restore từ backup Bước 1 nếu cần giữ data:
`psql -h 127.0.0.1 -U odoo19 -d wujia_tea_19 -f D:\backup\<file>.sql`
