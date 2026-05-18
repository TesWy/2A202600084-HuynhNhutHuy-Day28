param(
    [switch]$Recreate
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$VenvPath = Join-Path $ProjectRoot ".venv"
$PythonExe = Join-Path $VenvPath "Scripts\python.exe"

Set-Location $ProjectRoot

function Invoke-Checked {
    param(
        [Parameter(Mandatory=$true)]
        [scriptblock]$Command
    )
    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code $LASTEXITCODE"
    }
}

if ($Recreate -and (Test-Path $VenvPath)) {
    Remove-Item -LiteralPath $VenvPath -Recurse -Force
}

if (-not (Test-Path $PythonExe)) {
    Invoke-Checked { python -m venv .venv }
}

Invoke-Checked { & $PythonExe -m pip install --upgrade pip setuptools wheel }
Invoke-Checked { & $PythonExe -m pip install -r requirements.txt }

if (-not (Test-Path ".env") -and (Test-Path ".env.example")) {
    Copy-Item ".env.example" ".env"
}

Write-Host ""
Write-Host "Local Python environment is ready."
Write-Host "Activate it with:"
Write-Host "  .\.venv\Scripts\Activate.ps1"
Write-Host ""
Write-Host "Next:"
Write-Host "  1. Fill .env with Kaggle tunnel URLs."
Write-Host "  2. Run docker compose up -d."
Write-Host "  3. Run pytest smoke-tests/ -v after the services are ready."
