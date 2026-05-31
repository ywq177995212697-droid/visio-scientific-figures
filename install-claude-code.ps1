param(
    [switch]$Project,
    [string]$ProjectPath = (Get-Location).Path
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$source = Join-Path $repoRoot 'skills\visio-scientific-figures'

if ($Project) {
    $destinationRoot = Join-Path $ProjectPath '.claude\skills'
} else {
    $destinationRoot = Join-Path $env:USERPROFILE '.claude\skills'
}

$destination = Join-Path $destinationRoot 'visio-scientific-figures'

if (!(Test-Path $source)) {
    throw "Cannot find skill folder: $source"
}

New-Item -ItemType Directory -Force -Path $destination | Out-Null
Copy-Item -Recurse -Force -Path (Join-Path $source '*') -Destination $destination
Write-Host "Installed Claude Code skill to $destination"
