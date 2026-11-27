# Exports the README images: key pitch-book slides (via PowerPoint COM), the tearsheet render (via PyMuPDF)
# and two of the generated charts. Needs desktop PowerPoint on Windows.
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$img = Join-Path $root "docs\img"
New-Item -ItemType Directory -Force $img | Out-Null
$py = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) { $py = "python" }

$slides = @(@(2, "decision.png"), @(3, "funding-cases.png"), @(12, "relative-valuation.png"), @(14, "dcf.png"), @(15, "market-implied.png"), @(19, "ncd-case.png"))
$ppt = New-Object -ComObject PowerPoint.Application
try {
    $deck = $ppt.Presentations.Open((Join-Path $root "output\CEAT_Investment_Banking_Pitch_Book.pptx"), $true, $false, $false)
    foreach ($s in $slides) { $deck.Slides.Item($s[0]).Export((Join-Path $img $s[1]), "PNG", 1600, 900) }
    $deck.Close()
}
finally {
    $ppt.Quit()
    [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($ppt)
}

& $py -c "import pymupdf,sys; pymupdf.open(sys.argv[1])[0].get_pixmap(dpi=110).save(sys.argv[2])" `
    (Join-Path $root "output\CEAT_Deal_Tearsheet.pdf") (Join-Path $img "tearsheet.png")
if ($LASTEXITCODE -ne 0) { throw "tearsheet render failed" }
foreach ($c in "03_ebitda.png", "06_cash_capex.png") { Copy-Item (Join-Path $root "charts\$c") (Join-Path $img ("chart-" + $c.Substring(3))) -Force }
Write-Output "exported images to $img"
