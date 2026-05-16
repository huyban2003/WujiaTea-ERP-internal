# Deploy Sprint 5 — WujiaTea Odoo 19

Sprint 5 thực hiện **rename + đổi kiểu field** trên hai module skeleton (`wujia_portal_knowledge`, `wujia_portal_support`). Odoo 19 khi `-u` sẽ **drop cột cũ** (subject, user_id, handler_user_id, category, published) → nếu chỉ làm `git pull + nssm restart` thì hệ thống crash khi đọc ticket / article cũ.

Phương án chốt với user (16/05/2026): cả dev và prod đều là **skeleton, không có data quan trọng** → drop+init DB rồi seed lại.

## Trên server Windows (sau khi auto-deploy push xong)

`auto-deploy.yml` chỉ làm `git pull + nssm restart Odoo`. Cần chạy thêm các bước dưới qua RDP/PowerShell.

### Bước 0 — Verify code mới nhất (belt-and-suspenders)

Auto-deploy đã `git pull` rồi nhưng vẫn nên xác nhận:

```powershell
cd D:\wujia-tea
git pull origin main
git log -1 --oneline   # phải là `docs(sprint-log): record sprint 5 chapter` hoặc mới hơn
```

### Bước 1 — Stop Odoo service (đang crash với code mới + schema cũ)

```powershell
nssm stop Odoo
```

(Tuỳ chọn) backup DB phòng cần rollback:

```powershell
$env:PGPASSWORD = "wujia_admin"
pg_dump -h 127.0.0.1 -U odoo wujia_tea > D:\backup\wujia_tea_pre_sprint5_$(Get-Date -Format yyyyMMdd_HHmm).sql
```

### Bước 2 — Drop + create DB

Đăng nhập psql với master pass `wujia_admin`:

```powershell
$env:PGPASSWORD = "wujia_admin"
dropdb -h 127.0.0.1 -U odoo wujia_tea
createdb -h 127.0.0.1 -U odoo -O odoo wujia_tea
```

Tên DB, user, password lấy từ `D:\wujia-tea\config\odoo.conf` — sửa lại nếu khác.

### Bước 3 — Install full module chain

```powershell
cd D:\wujia-tea\odoo19
python odoo-bin -c ..\config\odoo.conf -d wujia_tea `
  -i wujia_core,wujia_franchise,wujia_sale,wujia_fleet,wujia_delivery,wujia_portal_base,wujia_portal_layout,wujia_portal_sale,wujia_portal_purchase_history,wujia_portal_delivery,wujia_portal_return,wujia_portal_notification,wujia_portal_exam,wujia_portal_knowledge,wujia_portal_report,wujia_portal_support `
  --without-demo=True --stop-after-init
```

Sequence categories cho support (7 record) tự load từ `data/wujia_support_category_data.xml` qua install.

### Bước 4 — Seed sample data y chang dev

Lấy 5 script từ repo:

```powershell
python odoo-bin shell -c ..\config\odoo.conf -d wujia_tea --no-http < D:\wujia-tea\scripts\seed_admin_franchise.py
python odoo-bin shell -c ..\config\odoo.conf -d wujia_tea --no-http < D:\wujia-tea\scripts\seed_fleet_demo.py
python odoo-bin shell -c ..\config\odoo.conf -d wujia_tea --no-http < D:\wujia-tea\scripts\seed_portal_demo.py
python odoo-bin shell -c ..\config\odoo.conf -d wujia_tea --no-http < D:\wujia-tea\scripts\seed_knowledge_demo.py
python odoo-bin shell -c ..\config\odoo.conf -d wujia_tea --no-http < D:\wujia-tea\scripts\seed_support_demo.py
```

### Bước 5 — Smoke test

```powershell
python odoo-bin shell -c ..\config\odoo.conf -d wujia_tea --no-http < D:\wujia-tea\scripts\test_sprint5.py
```

Output mong đợi: `=== RESULT: 20 PASS / 0 FAIL ===` (có 1 SKIP cho `batch_id` test nếu seed chưa tạo picking — không phải lỗi).

### Bước 6 — Start Odoo

```powershell
nssm start Odoo
```

Kiểm tra portal: `http://<server-ip>:8019/portal` → đăng nhập admin, xem trang Knowledge + Support có data demo.

## Trên server Linux (nếu có)

Script một-phát `scripts/reseed_full.sh` đã có sẵn (chạy được trên Linux). Cần điều chỉnh biến môi trường nếu DB name / credentials khác dev:

```bash
DB_NAME=wujia_tea PG_USER=odoo PG_PASS=wujia_admin \
  bash /path/to/wujia-tea/scripts/reseed_full.sh
```

Sau đó chạy `test_sprint5.py` để verify, restart Odoo service.

## Phòng ngừa lần sau

Khi commit code có **rename hoặc đổi kiểu field** trên model có data thật, KHÔNG chạy `git pull` rồi `-u` trên prod. Thay vào đó:

1. Viết `<module>/migrations/<new_version>/pre-migrate.py` copy data sang cột mới trước khi Odoo drop.
2. Hoặc nếu chấp nhận mất data (skeleton): drop+init theo doc này.

Đã ghi rule này vào memory `feedback_field_rename_data_loss` để tránh lặp lại.

## Rollback nếu cần

Sprint 5 không có migration ngược — nếu cần rollback:

```bash
# revert commits trên main rồi force-push
git revert <commit-A>..<commit-E>
git push origin main
# trên server: lặp lại drop+init+seed với code cũ
```

Backup DB trước khi drop nếu prod có bất kỳ data nào nghi ngờ cần giữ:

```powershell
$env:PGPASSWORD = "wujia_admin"
pg_dump -h 127.0.0.1 -U odoo wujia_tea > D:\backup\wujia_tea_pre_sprint5_$(Get-Date -Format yyyyMMdd_HHmm).sql
```
