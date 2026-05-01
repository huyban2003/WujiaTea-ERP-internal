# ===========================================================
# WujiaTea — Windows Server Setup Script
# Chay bang PowerShell voi quyen Administrator
# ===========================================================

Write-Host "=== WujiaTea Server Setup ===" -ForegroundColor Cyan

$targetDir = "D:\wujia-tea"
$pgBin = "C:\Program Files\PostgreSQL\16\bin"
$repoUrl = "https://github.com/huyban2003/WujiaTea-ERP-internal.git"
$odooRepo = "https://github.com/odoo/odoo.git"

# 1. Cai Git (neu chua co)
Write-Host "[1/6] Kiem tra / Cai Git..." -ForegroundColor Yellow
if (!(Get-Command git -ErrorAction SilentlyContinue)) {
    winget install Git.Git -e --silent
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine")
}
Write-Host "  Git OK" -ForegroundColor Green

# 2. Cai Python 3.10 (neu chua co)
Write-Host "[2/6] Kiem tra / Cai Python 3.10..." -ForegroundColor Yellow
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    winget install Python.Python.3.10 -e --silent
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine")
}
Write-Host "  Python OK" -ForegroundColor Green

# 3. Cai PostgreSQL 16 (neu chua co)
Write-Host "[3/6] Kiem tra / Cai PostgreSQL 16..." -ForegroundColor Yellow
if (!(Test-Path "$pgBin\psql.exe")) {
    winget install PostgreSQL.PostgreSQL.16 -e --silent
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine")
    Start-Sleep -Seconds 5
}
# Doi pg_hba.conf de dung trust (khong can password)
$hbaFile = "C:\Program Files\PostgreSQL\16\data\pg_hba.conf"
(Get-Content $hbaFile) -replace "scram-sha-256", "trust" | Set-Content $hbaFile
net stop postgresql-x64-16 | Out-Null
net start postgresql-x64-16 | Out-Null
Start-Sleep -Seconds 3
# Tao user va database
& "$pgBin\psql.exe" -U postgres -c "CREATE USER odoo19 WITH PASSWORD '1';" 2>$null
& "$pgBin\psql.exe" -U postgres -c "ALTER USER odoo19 CREATEDB;" 2>$null
& "$pgBin\psql.exe" -U postgres -c "CREATE DATABASE wujia_tea_19 OWNER odoo19;" 2>$null
Write-Host "  PostgreSQL OK" -ForegroundColor Green

# 4. Clone WujiaTea repo
Write-Host "[4/6] Clone WujiaTea repo..." -ForegroundColor Yellow
if (!(Test-Path $targetDir)) {
    git clone $repoUrl $targetDir
} else {
    Write-Host "  Folder da ton tai, chay git pull..." -ForegroundColor Gray
    Set-Location $targetDir
    git pull origin main
}

# 5. Clone Odoo 19 source
Write-Host "[5/6] Clone Odoo 19 source..." -ForegroundColor Yellow
if (!(Test-Path "$targetDir\odoo19")) {
    git clone $odooRepo --branch 19.0 --depth 1 "$targetDir\odoo19"
} else {
    Write-Host "  odoo19 da ton tai, bo qua." -ForegroundColor Gray
}

# Cai pip dependencies
Write-Host "  Cai pip dependencies..." -ForegroundColor Gray
Set-Location $targetDir
python -m pip install --upgrade pip
python -m pip install -r odoo19\requirements.txt

Write-Host "  Dependencies OK" -ForegroundColor Green

# 6. Bat OpenSSH Server + mo firewall
Write-Host "[6/6] Bat OpenSSH Server va mo firewall..." -ForegroundColor Yellow
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0 | Out-Null
Start-Service sshd -ErrorAction SilentlyContinue
Set-Service -Name sshd -StartupType Automatic -ErrorAction SilentlyContinue
New-NetFirewallRule -Name "OpenSSH-Server" -DisplayName "OpenSSH Server" `
    -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22 -ErrorAction SilentlyContinue
New-NetFirewallRule -Name "Odoo-8019" -DisplayName "Odoo HTTP 8019" `
    -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 8019 -ErrorAction SilentlyContinue
New-NetFirewallRule -Name "Odoo-8020" -DisplayName "Odoo Longpolling 8020" `
    -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 8020 -ErrorAction SilentlyContinue
Write-Host "  Firewall OK" -ForegroundColor Green

Write-Host ""
Write-Host "=== XONG! ===" -ForegroundColor Green
Write-Host "Chay Odoo bang lenh sau:"
Write-Host "  cd D:\wujia-tea"
Write-Host "  python odoo19\odoo-bin -c config\odoo.conf"
