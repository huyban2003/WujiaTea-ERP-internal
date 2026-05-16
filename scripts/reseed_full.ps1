# Drop + recreate the WujiaTea DB on Windows, install the full module
# chain, run every seed script, then smoke-test. PowerShell equivalent
# of scripts/reseed_full.sh (Linux dev).
#
# Use after auto-deploy pulled new code that requires DB reset
# (e.g. field renames). Run from D:\wujia-tea\.
#
# Notes:
#   - Uses `cmd /c "python ... < file"` instead of `Get-Content | python`
#     because PowerShell pipes go through $OutputEncoding which adds
#     BOM + re-encodes Vietnamese chars; cmd does raw byte redirect.
#   - Sets PYTHONUTF8 / PYTHONIOENCODING / console codepage so Odoo
#     logging emit() does not crash on Vietnamese module names.

$ErrorActionPreference = "Stop"

# ---- Paths / DB ----
$DB       = "wujia_tea_19"
$DB_USER  = "odoo19"
$DB_HOST  = "127.0.0.1"
$DB_PASS  = "1"
$ROOT     = "D:\wujia-tea"
$ODOO     = "$ROOT\odoo19\odoo-bin"
$CONF     = "$ROOT\config\odoo-server.conf"
$SCRIPTS  = "$ROOT\scripts"
$PG_BIN   = "C:\Program Files\PostgreSQL\16\bin"

$MODULES = "wujia_core,wujia_franchise,wujia_sale,wujia_fleet,wujia_delivery,wujia_portal_base,wujia_portal_layout,wujia_portal_sale,wujia_portal_purchase_history,wujia_portal_delivery,wujia_portal_return,wujia_portal_notification,wujia_portal_exam,wujia_portal_knowledge,wujia_portal_report,wujia_portal_support"

# ---- Env ----
$env:Path              = "$PG_BIN;" + $env:Path
$env:PGPASSWORD        = $DB_PASS
$env:PYTHONUTF8        = "1"
$env:PYTHONIOENCODING  = "utf-8"
chcp 65001 > $null
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# ---- Drop + create ----
Write-Host "==> dropdb $DB" -ForegroundColor Cyan
dropdb -h $DB_HOST -U $DB_USER --if-exists $DB

Write-Host "==> createdb $DB" -ForegroundColor Cyan
createdb -h $DB_HOST -U $DB_USER -O $DB_USER $DB

# ---- Install full module chain ----
Write-Host "==> Installing modules (no demo)" -ForegroundColor Cyan
python $ODOO -c $CONF -d $DB -i $MODULES --without-demo=True --stop-after-init
if ($LASTEXITCODE -ne 0) { throw "Module install failed (exit $LASTEXITCODE)" }

# ---- Helper: run python file as Odoo shell input via cmd ----
function Run-OdooScript([string]$Name) {
    $Path = Join-Path $SCRIPTS $Name
    if (-not (Test-Path $Path)) {
        Write-Warning "Skip: $Path not found"
        return
    }
    Write-Host "==> $Name" -ForegroundColor Cyan
    cmd /c "python `"$ODOO`" shell -c `"$CONF`" -d $DB --no-http < `"$Path`""
    if ($LASTEXITCODE -ne 0) { throw "$Name failed (exit $LASTEXITCODE)" }
}

# ---- Seed pipeline ----
Run-OdooScript "seed_admin_franchise.py"
Run-OdooScript "seed_fleet_demo.py"
Run-OdooScript "seed_portal_demo.py"
Run-OdooScript "seed_knowledge_demo.py"
Run-OdooScript "seed_support_demo.py"

# ---- Smoke test ----
Write-Host "==> Smoke test (expect 20 PASS / 0 FAIL)" -ForegroundColor Cyan
Run-OdooScript "test_sprint5.py"

Write-Host "`n==> DONE. Start Odoo service: nssm start Odoo" -ForegroundColor Green
