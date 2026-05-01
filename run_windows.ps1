# Run Project: Kangaroo on Windows 10
# Usage: Right-click -> Run with PowerShell or open PowerShell and run: .\run_windows.ps1

param(
    [string[]]$Args
)

$ErrorActionPreference = 'Stop'

$root = Split-Path -Path $MyInvocation.MyCommand.Definition -Parent
Set-Location $root

# Create virtual environment if missing
$venvPath = Join-Path $root ".venv"
if (-not (Test-Path $venvPath)) {
    Write-Host "Creating virtual environment at $venvPath"
    python -m venv $venvPath
}

# Activate venv
$activate = Join-Path $venvPath "Scripts\Activate.ps1"
if (Test-Path $activate) {
    Write-Host "Activating virtual environment"
    . $activate
} else {
    Write-Host "Virtual environment activate script not found. Ensure Python is installed and in PATH." -ForegroundColor Yellow
}

# Upgrade pip and install requirements if file exists
$req = Join-Path $root "requirements.txt"
if (Test-Path $req) {
    Write-Host "Installing dependencies from requirements.txt"
    python -m pip install --upgrade pip
    python -m pip install -r $req
} else {
    Write-Host "No requirements.txt found. Skipping dependency installation." -ForegroundColor Yellow
}

# Run the main orchestrator
Write-Host "Starting Project: Kangaroo (jscjr_multiverse.py)"
$python = "python"
$script = Join-Path $root "jscjr_multiverse.py"
& $python $script @Args
