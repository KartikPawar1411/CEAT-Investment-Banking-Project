$ErrorActionPreference='Stop'
$file=(Resolve-Path (Join-Path $PSScriptRoot '../output/CEAT_Financial_Valuation_Model.xlsx')).Path
$excel=New-Object -ComObject Excel.Application
$book=$null
try {
    $excel.Visible=$false
    $excel.DisplayAlerts=$false
    $excel.AutomationSecurity=3
    $book=$excel.Workbooks.Open($file,0,$false)
    $excel.CalculateFullRebuild()
    $book.Save()
    $sheet=$book.Worksheets.Item('Cover & Dashboard')
    $sheet.PageSetup.PrintArea='A1:C18'
    $sheet.PageSetup.Orientation=2
    $sheet.PageSetup.Zoom=$false
    $sheet.PageSetup.FitToPagesWide=1
    $sheet.PageSetup.FitToPagesTall=1
    $qa=Join-Path $PSScriptRoot '../.qa'
    New-Item -Force -ItemType Directory $qa | Out-Null
    $sheet.ExportAsFixedFormat(0,(Join-Path $qa 'dashboard.pdf'))
    $inputs=$book.Worksheets.Item('Funding Inputs')
    $decision=$book.Worksheets.Item('Funding Decision')
    $baseline=[string]$decision.Range('B10').Value2
    $original=[double]$inputs.Range('B5').Value2
    $changed=$false
    foreach ($newAmount in @($original*1.5; $original*0.5; 1.0; $original*3.0)) {
        $inputs.Range('B5').Value2=[double]$newAmount
        $excel.CalculateFullRebuild()
        if ([string]$decision.Range('B10').Value2 -ne $baseline) {
            $book.SaveCopyAs((Join-Path $qa 'threshold.xlsx'))
            $changed=$true
            break
        }
    }
    if (-not $changed) {throw 'Capex probe could not cross a release threshold.'}
} finally {
    if ($book) {$book.Close($false)}
    $excel.Quit()
    [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($excel)
}
