# Install fastmcp / beautifulsoup4 / requests into the Houdini Python environment
# ASCII-only to avoid encoding issues on PowerShell 5.1

Write-Host "==============================================================" -ForegroundColor Cyan
Write-Host "Houdini Python - Install fastmcp / bs4 / requests" -ForegroundColor Green
Write-Host "==============================================================" -ForegroundColor Cyan
Write-Host ""

# Common Houdini Python locations (newest to oldest)
$houdiniPythons = @(
    "C:\\Program Files\\Side Effects Software\\Houdini 21.5.*\\python310\\python.exe",
    "C:\\Program Files\\Side Effects Software\\Houdini 21.0.*\\python310\\python.exe",
    "C:\\Program Files\\Side Effects Software\\Houdini 21.0.*\\python39\\python.exe",
    "C:\\Program Files\\Side Effects Software\\Houdini 20.5.*\\python39\\python.exe",
    "C:\\Program Files\\Side Effects Software\\Houdini 20.0.*\\python39\\python.exe"
)

$foundPython = $null
Write-Host "Searching for Houdini Python..." -ForegroundColor Yellow
foreach ($pattern in $houdiniPythons) {
    $matches = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue
    if ($matches) {
        $foundPython = $matches[0].FullName
        Write-Host "Found: $foundPython" -ForegroundColor Green
        break
    }
}

if (-not $foundPython) {
    Write-Host "Houdini Python not found." -ForegroundColor Red
    Write-Host ""
    Write-Host "Please run manually, for example:" -ForegroundColor Yellow
    Write-Host '  & "C:\\Program Files\\Side Effects Software\\Houdini 21.0.000\\python310\\python.exe" -m pip install fastmcp beautifulsoup4 requests' -ForegroundColor Gray
    Write-Host ""
    pause
    exit 1
}

$packages = @("fastmcp", "beautifulsoup4", "requests")
Write-Host ""
Write-Host ("Installing packages: " + ($packages -join ", ")) -ForegroundColor Yellow
Write-Host ""

try {
    foreach ($pkg in $packages) {
        Write-Host "Installing $pkg ..." -ForegroundColor Cyan
        & $foundPython -m pip install --upgrade $pkg
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Failed to install $pkg, exit code: $LASTEXITCODE" -ForegroundColor Red
            throw "Install failed: $pkg"
        }
    }
    Write-Host ""
    Write-Host "==============================================================" -ForegroundColor Cyan
    Write-Host "Dependencies installed successfully." -ForegroundColor Green
    Write-Host "==============================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "You can now start Houdini UI and the FastMCP server will auto-start." -ForegroundColor Green
    Write-Host "If not effective, please restart Houdini." -ForegroundColor Yellow
} catch {
    Write-Host ""
    Write-Host ("Error during installation: " + $_) -ForegroundColor Red
}

Write-Host ""
pause
