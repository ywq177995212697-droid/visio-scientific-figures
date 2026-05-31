param(
    [string]$DestinationRoot = $(if ($env:CODEX_HOME) { Join-Path $env:CODEX_HOME 'skills' } else { Join-Path $env:USERPROFILE '.codex\skills' })
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$source = Join-Path $repoRoot 'skills\visio-scientific-figures'
$destination = Join-Path $DestinationRoot 'visio-scientific-figures'

if (!(Test-Path $source)) {
    throw "Cannot find skill folder: $source"
}

New-Item -ItemType Directory -Force -Path $destination | Out-Null
Copy-Item -Recurse -Force -Path (Join-Path $source '*') -Destination $destination
Write-Host "Installed Codex skill to $destination"
Write-Host "Run: python `"$destination\scripts\check_environment.py`""
