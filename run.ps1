$ErrorActionPreference = 'Stop'

# Change to the directory of this script, then into 'main'
$scriptDir = Split-Path -LiteralPath $PSCommandPath -Parent
Set-Location -LiteralPath $scriptDir
Set-Location -LiteralPath (Join-Path -Path $scriptDir -ChildPath 'main')

# Run python with passthrough args
$python = 'python'
& $python 'main.py' @args

# Keep window open on double-click
Write-Host ''
Write-Host 'Press Enter to continue . . .'
[void][System.Console]::ReadLine()
