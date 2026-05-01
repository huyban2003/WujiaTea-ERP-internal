# ===========================================================
# WujiaTea — Windows Server Setup Script
# Chay bang PowerShell voi quyen Administrator
# ===========================================================

Write-Host "=== WujiaTea Server Setup ===" -ForegroundColor Cyan

# 1. Cai Chocolatey
Write-Host "[1/6] Cai Chocolatey..." -ForegroundColor Yellow
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
refreshenv

# 2. Cai Git
Write-Host "[2/6] Cai Git..." -ForegroundColor Yellow
choco install git -y
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine")

# 3. Cai PostgreSQL 16
Write-Host "[3/6] Cai PostgreSQL 16..." -ForegroundColor Yellow
choco install postgresql16 --params "/Password:1" -y
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine")

# Cho PostgreSQL khoi dong xong
Start-Sleep -Seconds 5

# Tao user va database cho Odoo
Write-Host "  Tao user odoo19 va database wujia_tea_19..." -ForegroundColor Gray
$pgBin = "C:\Program Files\PostgreSQL\16\bin"
& "$pgBin\psql.exe" -U postgres -c "CREATE USER odoo19 WITH PASSWORD '1';" 2>$null
& "$pgBin\psql.exe" -U postgres -c "ALTER USER odoo19 CREATEDB;" 2>$null
& "$pgBin\psql.exe" -U postgres -c "CREATE DATABASE wujia_tea_19 OWNER odoo19;" 2>$null
Write-Host "  PostgreSQL OK" -ForegroundColor Green

# 4. Clone repo
Write-Host "[4/6] Clone WujiaTea repo..." -ForegroundColor Yellow
$repoUrl = "https://github.com/huyban2003/WujiaTea-ERP-internal.git"
$targetDir = "D:\wujia-tea"
if (!(Test-Path $targetDir)) {
    git clone $repoUrl $targetDir
} else {
    Write-Host "  Folder da ton tai, chay git pull..." -ForegroundColor Gray
    Set-Location $targetDir
    git pull origin main
}

# 5. Cai Python 3.12 + dependencies Odoo
Write-Host "[5/6] Cai Python 3.12 va Odoo dependencies..." -ForegroundColor Yellow
choco install python312 -y
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine")

# Cai cac thu vien he thong can thiet
choco install vcredist-all -y

# Cai pip packages
Set-Location $targetDir
pip install -r odoo19\requirements.txt

# 6. Cai OpenSSH Server
Write-Host "[6/6] Bat OpenSSH Server..." -ForegroundColor Yellow
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
Start-Service sshd
Set-Service -Name sshd -StartupType Automatic
New-NetFirewallRule -Name "OpenSSH-Server" -DisplayName "OpenSSH Server (sshd)" `
    -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22 -ErrorAction SilentlyContinue

# Mo firewall port Odoo
New-NetFirewallRule -Name "Odoo-8019" -DisplayName "Odoo HTTP 8019" `
    -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 8019 -ErrorAction SilentlyContinue
New-NetFirewallRule -Name "Odoo-8020" -DisplayName "Odoo Longpolling 8020" `
    -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 8020 -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "=== XONG! ===" -ForegroundColor Green
Write-Host "Chay Odoo bang lenh sau:"
Write-Host "  cd D:\wujia-tea"
Write-Host "  python odoo19\odoo-bin -c config\odoo.conf"
