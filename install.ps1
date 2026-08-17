# neovibe installer for Windows.
#   irm https://raw.githubusercontent.com/neomnia/neovibe/main/install.ps1 | iex
#
# neovibe itself is a bash + Python client (kubectl port-forward, streamed terminal UI) --
# there is no native Windows rewrite. Instead, this script installs into WSL (Windows
# Subsystem for Linux), where the exact same install.sh runs unmodified, same as on
# Linux/macOS. This keeps a single source of truth (one repo, one codebase) instead of
# maintaining a separate PowerShell implementation.

$ErrorActionPreference = "Stop"

Write-Host "=== Installing neovibe (via WSL) ===" -ForegroundColor Cyan

$wslInstalled = $false
try {
    wsl.exe --status *> $null
    $wslInstalled = $true
} catch {
    $wslInstalled = $false
}

if (-not $wslInstalled) {
    Write-Host ""
    Write-Host "WSL (Windows Subsystem for Linux) is not installed." -ForegroundColor Yellow
    Write-Host "neovibe needs it -- it's a bash/kubectl/Python tool, same as on Linux/macOS." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Open PowerShell as Administrator and run:"
    Write-Host "     wsl --install" -ForegroundColor Green
    Write-Host "2. Restart your machine when prompted."
    Write-Host "3. Re-run this script."
    exit 1
}

Write-Host "WSL detected -- installing neovibe inside it..."
wsl.exe -- bash -c "curl -fsSL https://raw.githubusercontent.com/neomnia/neovibe/main/install.sh | bash"

Write-Host ""
Write-Host "=== Done ===" -ForegroundColor Cyan
Write-Host "Launch neovibe from a WSL terminal (Ubuntu app, or 'wsl' in PowerShell), then run:"
Write-Host "    neo" -ForegroundColor Green
