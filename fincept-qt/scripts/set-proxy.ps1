# ============================================================================
# Fincept Terminal - Proxy Setup Script
# ============================================================================
# This script helps you set up proxy for faster package downloads.
# 
# Usage:
#   .\set-proxy.ps1                          # Use system default proxy
#   .\set-proxy.ps1 -Proxy "http://proxy:8080"  # Set custom proxy
#   .\set-proxy.ps1 -Clear                   # Clear proxy settings
# ============================================================================

param(
    [string]$Proxy = "",
    [switch]$Clear = $false,
    [switch]$ShowStatus = $false
)

$ErrorActionPreference = "Stop"

# Colors for output
$Green = "Green"
$Yellow = "Yellow"
$Red = "Red"
$Cyan = "Cyan"

function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Show-CurrentProxy {
    Write-ColorOutput "`n=== Current Proxy Settings ===" $Cyan
    
    $proxyVars = @("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "NO_PROXY", "no_proxy")
    $hasProxy = $false
    
    foreach ($var in $proxyVars) {
        $value = [System.Environment]::GetEnvironmentVariable($var, "User")
        if (-not $value) {
            $value = [System.Environment]::GetEnvironmentVariable($var, "Process")
        }
        
        if ($value) {
            Write-ColorOutput "$var = $value" $Green
            $hasProxy = $true
        }
    }
    
    if (-not $hasProxy) {
        Write-ColorOutput "No proxy configured" $Yellow
    }
    
    Write-Host ""
}

function Set-Proxy {
    param([string]$ProxyUrl)
    
    Write-ColorOutput "`n=== Setting Proxy ===" $Cyan
    Write-ColorOutput "Proxy URL: $ProxyUrl" $Green
    
    # Set both uppercase and lowercase variants for compatibility
    $proxyVars = @(
        @{Name="HTTP_PROXY"; Value=$ProxyUrl},
        @{Name="HTTPS_PROXY"; Value=$ProxyUrl},
        @{Name="http_proxy"; Value=$ProxyUrl},
        @{Name="https_proxy"; Value=$ProxyUrl}
    )
    
    foreach ($item in $proxyVars) {
        [System.Environment]::SetEnvironmentVariable($item.Name, $item.Value, "User")
        [System.Environment]::SetEnvironmentVariable($item.Name, $item.Value, "Process")
        Write-ColorOutput "✓ Set $($item.Name)" $Green
    }
    
    Write-ColorOutput "`nProxy has been set for current user." $Green
    Write-ColorOutput "Note: You may need to restart your terminal/IDE for changes to take effect." $Yellow
    Write-Host ""
}

function Clear-Proxy {
    Write-ColorOutput "`n=== Clearing Proxy Settings ===" $Cyan
    
    $proxyVars = @("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "NO_PROXY", "no_proxy")
    
    foreach ($var in $proxyVars) {
        [System.Environment]::SetEnvironmentVariable($var, $null, "User")
        [System.Environment]::SetEnvironmentVariable($var, $null, "Process")
    }
    
    Write-ColorOutput "✓ All proxy settings cleared" $Green
    Write-ColorOutput "Note: You may need to restart your terminal/IDE for changes to take effect." $Yellow
    Write-Host ""
}

function Show-Help {
    Write-ColorOutput "`n=== Fincept Terminal Proxy Setup ===" $Cyan
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor $Cyan
    Write-Host "  .\set-proxy.ps1                              Show current proxy status"
    Write-Host "  .\set-proxy.ps1 -Proxy <url>                 Set custom proxy"
    Write-Host "  .\set-proxy.ps1 -Clear                       Clear all proxy settings"
    Write-Host "  .\set-proxy.ps1 -ShowStatus                  Show detailed proxy status"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor $Cyan
    Write-Host '  .\set-proxy.ps1 -Proxy "http://127.0.0.1:7890"'
    Write-Host '  .\set-proxy.ps1 -Proxy "socks5://127.0.0.1:1080"'
    Write-Host "  .\set-proxy.ps1 -Clear"
    Write-Host ""
    Write-Host "Common proxy URLs:" -ForegroundColor $Cyan
    Write-Host "  Clash:           http://127.0.0.1:7890"
    Write-Host "  V2Ray:           http://127.0.0.1:10809"
    Write-Host "  Shadowsocks:     socks5://127.0.0.1:1080"
    Write-Host "  System default:  (auto-detect from Windows settings)"
    Write-Host ""
}

# Main logic
if ($Clear) {
    Clear-Proxy
} elseif ($Proxy) {
    Set-Proxy -ProxyUrl $Proxy
} elseif ($ShowStatus) {
    Show-CurrentProxy
} else {
    Show-Help
    Show-CurrentProxy
}

Write-ColorOutput "Tip: After setting proxy, restart Fincept Terminal to apply changes." $Cyan
