$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$sourceFile = Join-Path $scriptRoot "CrystallicReorganizer.cs"
$distDir = Join-Path $scriptRoot "dist"
$outputFile = Join-Path $distDir "CrystallicReorganizer.exe"
$compiler = "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"

if (-not (Test-Path $compiler)) {
    throw "C# compiler not found at $compiler"
}

New-Item -ItemType Directory -Force -Path $distDir | Out-Null

& $compiler `
    /nologo `
    /target:exe `
    /out:$outputFile `
    /r:System.Web.Extensions.dll `
    $sourceFile

Write-Host "Built $outputFile"
