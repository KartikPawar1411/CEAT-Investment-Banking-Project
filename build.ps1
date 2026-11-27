# One command rebuilds everything from the frozen evidence in data/:
#   powershell -ExecutionPolicy Bypass -File build.ps1
# Needs Python 3.12+ with requirements.txt, and desktop Excel and PowerPoint (Windows) for recalculation and rendering.
$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $MyInvocation.MyCommand.Path)
$env:PYTHONUTF8 = "1"
$py = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $py)) { $py = "python" }

function Step($name, [scriptblock]$cmd) {
    Write-Host "==> $name" -ForegroundColor Cyan
    & $cmd
    if ($LASTEXITCODE -ne 0) { throw "$name failed" }
}

Step "Validated staged build (evidence, workbook, Excel recalc, checks, deck, brief, report, README)" { & $py build.py --render }
Step "Build tearsheet"         { & $py build_tearsheet.py }
Step "Export README images"    { powershell -NoProfile -ExecutionPolicy Bypass -File scripts/export_images.ps1 }
Step "Run tests"               { & $py -m pytest -q }
Write-Host "Build complete." -ForegroundColor Green
