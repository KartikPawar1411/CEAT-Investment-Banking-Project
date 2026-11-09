$ErrorActionPreference='Stop'
$deckPath=(Resolve-Path (Join-Path $PSScriptRoot '../output/CEAT_Investment_Banking_Pitch_Book.pptx')).Path
$qa=Join-Path $PSScriptRoot '../.qa'
New-Item -Force -ItemType Directory $qa | Out-Null
$app=New-Object -ComObject PowerPoint.Application
$deck=$null
try {
    $deck=$app.Presentations.Open($deckPath,$true,$false,$false)
    $deck.SaveAs((Join-Path $qa 'pitch_book.pdf'),32)
    Write-Output ("PowerPoint rendered " + $deck.Slides.Count + " slides.")
} finally {
    if ($deck) {$deck.Close()}
    $app.Quit()
    [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($app)
}
