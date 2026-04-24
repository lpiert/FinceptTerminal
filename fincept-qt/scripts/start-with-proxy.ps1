# ============================================================================
# Fincept Terminal - 代理模式启动脚本
# ============================================================================
# 此脚本会以代理模式启动 Fincept Terminal，加速 Python 包下载
# 
# 使用方法:
#   .\start-with-proxy.ps1                    # 使用已设置的代理
#   .\start-with-proxy.ps1 -Proxy "url"       # 指定代理地址
# ============================================================================

param(
    [string]$Proxy = ""
)

$ErrorActionPreference = "Stop"

# 颜色定义
$Green = "Green"
$Yellow = "Yellow"
$Cyan = "Cyan"
$Red = "Red"

function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

# 获取程序路径
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$ExePath = Join-Path $ProjectRoot "build\Desktop_Qt_6_8_3_MSVC2022_64bit-Debug\FinceptTerminal.exe"

# 检查可执行文件是否存在
if (-not (Test-Path $ExePath)) {
    Write-ColorOutput "错误: 找不到 FinceptTerminal.exe" $Red
    Write-ColorOutput "路径: $ExePath" $Red
    Write-Host ""
    Write-Host "请先编译项目或检查路径是否正确" $Yellow
    exit 1
}

# 如果指定了代理，先设置代理
if ($Proxy) {
    Write-ColorOutput "`n=== 设置代理 ===" $Cyan
    & "$ScriptDir\set-proxy.ps1" -Proxy $Proxy
    Start-Sleep -Seconds 1
}

# 检查当前代理设置
$proxySet = $false
$httpProxy = [System.Environment]::GetEnvironmentVariable("HTTP_PROXY", "User")
if (-not $httpProxy) {
    $httpProxy = [System.Environment]::GetEnvironmentVariable("HTTP_PROXY", "Process")
}

if ($httpProxy) {
    $proxySet = $true
    Write-ColorOutput "`n=== 代理配置 ===" $Cyan
    Write-ColorOutput "✓ HTTP_PROXY = $httpProxy" $Green
    Write-ColorOutput "✓ HTTPS_PROXY = $([System.Environment]::GetEnvironmentVariable('HTTPS_PROXY', 'User'))" $Green
} else {
    Write-ColorOutput "`n⚠ 警告: 未检测到代理设置" $Yellow
    Write-ColorOutput "  建议使用: .\start-with-proxy.ps1 -Proxy `"http://127.0.0.1:12334`"" $Yellow
    Write-Host ""
}

# 停止已运行的实例
Write-ColorOutput "`n=== 准备启动 ===" $Cyan
$existingProcess = Get-Process -Name "FinceptTerminal" -ErrorAction SilentlyContinue
if ($existingProcess) {
    Write-ColorOutput "检测到正在运行的实例，正在关闭..." $Yellow
    Stop-Process -Name "FinceptTerminal" -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

# 启动程序
Write-ColorOutput "正在启动 Fincept Terminal..." $Green
if ($proxySet) {
    Write-ColorOutput "模式: 代理加速 ✓" $Green
    Write-ColorOutput "代理: $httpProxy" $Green
} else {
    Write-ColorOutput "模式: 直接连接" $Yellow
}

Start-Process $ExePath

Write-Host ""
Write-ColorOutput "✓ 程序已启动" $Green
Write-Host ""
Write-ColorOutput "提示:" $Cyan
Write-Host "  • 程序会自动检测并使用代理加速 Python 包下载"
Write-Host "  • 如需清除代理，运行: .\set-proxy.ps1 -Clear"
Write-Host "  • 查看日志确认代理是否生效: [INFO] PythonSetup: Proxy detected"
Write-Host ""
