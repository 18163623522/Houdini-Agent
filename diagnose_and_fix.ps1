# DeepSeek API 环境诊断和修复脚本
# 检测并修复代理、SSL、证书等问题

param(
    [switch]$FixProxy = $false,
    [switch]$SkipInstall = $false
)

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host "DeepSeek API 环境诊断与修复工具" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host ""

# 1. 检查代理设置
Write-Host "1. 检查系统代理配置..." -ForegroundColor Yellow
Write-Host ""

$httpProxy = [System.Environment]::GetEnvironmentVariable("HTTP_PROXY", "User")
$httpsProxy = [System.Environment]::GetEnvironmentVariable("HTTPS_PROXY", "User")
$noProxy = [System.Environment]::GetEnvironmentVariable("NO_PROXY", "User")

if ($httpProxy -or $httpsProxy) {
    Write-Host "   检测到代理配置:" -ForegroundColor Yellow
    if ($httpProxy) { Write-Host "   HTTP_PROXY = $httpProxy" -ForegroundColor Gray }
    if ($httpsProxy) { Write-Host "   HTTPS_PROXY = $httpsProxy" -ForegroundColor Gray }
    if ($noProxy) { Write-Host "   NO_PROXY = $noProxy" -ForegroundColor Gray }
    
    Write-Host ""
    Write-Host "   ⚠️ 代理可能导致连接问题！" -ForegroundColor Red
    
    if ($FixProxy) {
        Write-Host "   正在临时禁用代理..." -ForegroundColor Yellow
        $env:HTTP_PROXY = $null
        $env:HTTPS_PROXY = $null
        $env:http_proxy = $null
        $env:https_proxy = $null
        Write-Host "   ✓ 已在当前会话中禁用代理" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "   建议：重新运行脚本并添加 -FixProxy 参数自动禁用" -ForegroundColor Yellow
        Write-Host "   或手动清除代理环境变量：" -ForegroundColor Yellow
        Write-Host '   [Environment]::SetEnvironmentVariable("HTTP_PROXY", $null, "User")' -ForegroundColor Gray
        Write-Host '   [Environment]::SetEnvironmentVariable("HTTPS_PROXY", $null, "User")' -ForegroundColor Gray
    }
} else {
    Write-Host "   ✓ 未检测到代理配置" -ForegroundColor Green
}

Write-Host ""

# 2. 检查 Houdini Python
Write-Host "2. 查找 Houdini Python..." -ForegroundColor Yellow
Write-Host ""

$houdiniPaths = @(
    "C:\Program Files\Side Effects Software\Houdini 21.0.*\python39\python.exe",
    "C:\Program Files\Side Effects Software\Houdini 20.5.*\python39\python.exe",
    "C:\Program Files\Side Effects Software\Houdini 20.0.*\python39\python.exe"
)

$foundPython = $null

foreach ($pattern in $houdiniPaths) {
    $matches = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue
    if ($matches) {
        $foundPython = $matches[0].FullName
        Write-Host "   ✓ 找到: $foundPython" -ForegroundColor Green
        break
    }
}

if (-not $foundPython) {
    Write-Host "   ✗ 未找到 Houdini Python" -ForegroundColor Red
    Write-Host "   尝试使用系统 Python..." -ForegroundColor Yellow
    $foundPython = "python"
}

Write-Host ""

# 3. 检查 Python 环境
Write-Host "3. 检查 Python 环境..." -ForegroundColor Yellow
Write-Host ""

try {
    $pythonVersion = & $foundPython --version 2>&1
    Write-Host "   Python 版本: $pythonVersion" -ForegroundColor Gray
    
    $sslVersion = & $foundPython -c "import ssl; print(ssl.OPENSSL_VERSION)" 2>&1
    Write-Host "   OpenSSL 版本: $sslVersion" -ForegroundColor Gray
    
    if ($sslVersion -match "OpenSSL 1\.0\.") {
        Write-Host "   ✗ OpenSSL 版本过旧（1.0.x），无法支持 TLS 1.2+" -ForegroundColor Red
    } elseif ($sslVersion -match "OpenSSL 1\.1\.0") {
        Write-Host "   ⚠️ OpenSSL 版本较旧（1.1.0），可能不支持 TLS 1.3" -ForegroundColor Yellow
    } else {
        Write-Host "   ✓ OpenSSL 版本可接受" -ForegroundColor Green
    }
    
    Write-Host ""
    
    # 检查 requests
    $hasRequests = & $foundPython -c "import requests; print(requests.__version__)" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ requests 库: $hasRequests" -ForegroundColor Green
    } else {
        Write-Host "   ✗ requests 库: 未安装" -ForegroundColor Red
        $needInstall = $true
    }
    
    # 检查 certifi
    $hasCertifi = & $foundPython -c "import certifi; print(certifi.__version__)" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ certifi 库: $hasCertifi" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️ certifi 库: 未安装" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "   ✗ 无法检查 Python 环境: $_" -ForegroundColor Red
}

Write-Host ""

# 4. 安装依赖
if (-not $SkipInstall -and $needInstall) {
    Write-Host "4. 安装必要的库..." -ForegroundColor Yellow
    Write-Host ""
    
    Write-Host "   正在安装 requests..." -ForegroundColor Cyan
    & $foundPython -m pip install requests --no-warn-script-location 2>&1 | Out-Host
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "   ✓ requests 安装成功" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "   ✗ requests 安装失败" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "   正在安装/更新 certifi..." -ForegroundColor Cyan
    & $foundPython -m pip install --upgrade certifi --no-warn-script-location 2>&1 | Out-Host
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "   ✓ certifi 安装/更新成功" -ForegroundColor Green
    }
    
    Write-Host ""
}

# 5. 测试 API 连接
Write-Host "5. 测试 DeepSeek API 连接..." -ForegroundColor Yellow
Write-Host ""

$testScript = @"
import sys
import os
# 禁用代理
os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''
os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''

sys.path.insert(0, r'C:\Users\KazamaSuichiku\Desktop\DCC-ASSET-MANAGER')

try:
    from HOUDINI_HIP_MANAGER.utils.ai_client import OpenAIClient
    client = OpenAIClient()
    
    if not client.has_api_key('deepseek'):
        print('✗ DeepSeek API Key 未配置')
        sys.exit(1)
    
    print('✓ API Key 已配置')
    print('正在测试连接...')
    
    result = client.test_connection('deepseek')
    if result.get('ok'):
        print('✓ 连接成功！')
        print(f'URL: {result.get("url")}')
    else:
        print(f'✗ 连接失败: {result.get("error")}')
        sys.exit(1)
except Exception as e:
    print(f'✗ 测试出错: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
"@

$testScriptPath = Join-Path $env:TEMP "test_deepseek.py"
$testScript | Out-File -FilePath $testScriptPath -Encoding UTF8

& $foundPython $testScriptPath 2>&1 | Out-Host

Write-Host ""

# 总结
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host "诊断完成" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host ""

Write-Host "如果仍有问题，请尝试：" -ForegroundColor Yellow
Write-Host "1. 在 Houdini 中，AI 助手选择 'Ollama（本地免费）' 而非 DeepSeek" -ForegroundColor Gray
Write-Host "2. 重启 Houdini 以加载新安装的库" -ForegroundColor Gray
Write-Host "3. 手动清除系统代理设置" -ForegroundColor Gray
Write-Host "4. 联系技术支持并提供此诊断结果" -ForegroundColor Gray
Write-Host ""

pause
