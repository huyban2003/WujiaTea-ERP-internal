# ===========================================================
# WujiaTea — Windows Server Setup Script
# Chạy bằng PowerShell với quyền Administrator
# ===========================================================

Write-Host "=== WujiaTea Server Setup ===" -ForegroundColor Cyan

# 1. Cài Chocolatey (package manager cho Windows)
Write-Host "[1/5] Cài Chocolatey..." -ForegroundColor Yellow
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# 2. Cài Git
Write-Host "[2/5] Cài Git..." -ForegroundColor Yellow
choco install git -y
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine")

# 3. Cài Docker Desktop
Write-Host "[3/5] Cài Docker Desktop..." -ForegroundColor Yellow
choco install docker-desktop -y

# 4. Clone repo (thay URL bằng repo của bạn)
Write-Host "[4/5] Clone WujiaTea repo..." -ForegroundColor Yellow
$repoUrl = "https://github.com/YOUR_USERNAME/wujia-tea.git"  # <-- đổi lại
$targetDir = "C:\wujia-tea"
if (!(Test-Path $targetDir)) {
    git clone $repoUrl $targetDir
} else {
    Write-Host "  Folder đã tồn tại, chạy git pull..." -ForegroundColor Gray
    Set-Location $targetDir
    git pull origin main
}

# 5. Cài OpenSSH Server (để SSH từ Ubuntu vào được)
Write-Host "[5/5] Bật OpenSSH Server..." -ForegroundColor Yellow
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
Start-Service sshd
Set-Service -Name sshd -StartupType Automatic
# Mở firewall port 22
New-NetFirewallRule -Name "OpenSSH-Server" -DisplayName "OpenSSH Server (sshd)" `
    -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22

Write-Host ""
Write-Host "=== XONG! Các bước tiếp theo ===" -ForegroundColor Green
Write-Host "1. Khởi động lại máy để Docker Desktop hoạt động"
Write-Host "2. Sau khi restart, mở PowerShell tại C:\wujia-tea và chạy:"
Write-Host "   docker compose up -d"
Write-Host "3. Trỏ domain về IP: 113.161.187.126"
Write-Host "4. Chạy certbot lấy SSL:"
Write-Host "   docker compose run --rm certbot certonly --webroot -w /var/www/certbot -d wujiatea.com"
