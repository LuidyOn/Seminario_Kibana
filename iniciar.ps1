[CmdletBinding()]
param([switch] $RestaurarDashboard)

$ErrorActionPreference = 'Stop'
& (Join-Path $PSScriptRoot 'scripts\iniciar_demo.ps1') @PSBoundParameters
exit $LASTEXITCODE
