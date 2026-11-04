param([string]$PresentationPath = (Join-Path $PSScriptRoot 'output\Nuwa Talk rev3.pptx'))
$ErrorActionPreference = 'Stop'
$renderDirectory = Join-Path $PSScriptRoot 'review-orange'
New-Item -ItemType Directory -Path $renderDirectory -Force | Out-Null
$powerPoint = New-Object -ComObject PowerPoint.Application
$deck = $null
try {
    $deck = $powerPoint.Presentations.Open($PresentationPath, -1, 0, 0)
    for ($slideNumber = 1; $slideNumber -le $deck.Slides.Count; $slideNumber++) {
        $slideFile = Join-Path $renderDirectory ('slide-{0:00}.png' -f $slideNumber)
        $deck.Slides.Item($slideNumber).Export($slideFile, 'PNG', 1600, 900)
    }
    Write-Output ('Rendered {0} slides' -f $deck.Slides.Count)
} finally {
    if ($null -ne $deck) { $deck.Close() }
    if ($powerPoint.Presentations.Count -eq 0) { $powerPoint.Quit() }
    [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($powerPoint)
}
