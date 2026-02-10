# 在 Houdini Python 环境中安装 requests 库
# 用于解决 SSL 协议兼容性问题

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 58) -ForegroundColor Cyan
Write-Host "Houdini Python - 安装 requests 库" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 58) -ForegroundColor Cyan
Write-Host ""

# 查找 Houdini 安装路径
$houdiniPaths = @(
    "C:\Program Files\Side Effects Software\Houdini 21.0.*\python39\python.exe",
    "C:\Program Files\Side Effects Software\Houdini 20.5.*\python39\python.exe",
    "C:\Program Files\Side Effects Software\Houdini 20.0.*\python39\python.exe"
)

$foundPython = $null

Write-Host "正在查找 Houdini Python..." -ForegroundColor Yellow

foreach ($pattern in $houdiniPaths) {
    $matches = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue
    if ($matches) {
        $foundPython = $matches[0].FullName
        Write-Host "✓ 找到: $foundPython" -ForegroundColor Green
        break
    }
}

if (-not $foundPython) {
    Write-Host "✗ 未找到 Houdini Python 安装" -ForegroundColor Red
    Write-Host ""
    Write-Host "请手动指定 Houdini Python 路径，例如：" -ForegroundColor Yellow
    Write-Host '  & "C:\Program Files\Side Effects Software\Houdini 21.0.000\python39\python.exe" -m pip install requests' -ForegroundColor Gray
    Write-Host ""
    pause
    exit 1
}

Write-Host ""
Write-Host "准备安装 requests 库..." -ForegroundColor Yellow
Write-Host ""

# 安装 requests
try {
    Write-Host "执行命令: $foundPython -m pip install requests" -ForegroundColor Cyan
    Write-Host ""
    
    & $foundPython -m pip install requests
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "=" -NoNewline -ForegroundColor Cyan
        Write-Host ("=" * 58) -ForegroundColor Cyan
        Write-Host "✓ requests 库安装成功！" -ForegroundColor Green
        Write-Host "=" -NoNewline -ForegroundColor Cyan
        Write-Host ("=" * 58) -ForegroundColor Cyan
        Write-Host ""
        Write-Host "现在可以在 Houdini 中使用 DeepSeek API 了。" -ForegroundColor Green
        Write-Host "请重启 Houdini 以加载新安装的库。" -ForegroundColor Yellow
    } else {
        Write-Host ""
        Write-Host "✗ 安装失败，退出码: $LASTEXITCODE" -ForegroundColor Red
    }
} catch {
    Write-Host ""
    Write-Host "✗ 安装过程出错: $_" -ForegroundColor Red
}

Write-Host ""
pause
