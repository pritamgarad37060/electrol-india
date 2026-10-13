# ELECTROL INDIA — PowerShell Election Data Launcher
# Run from project root: .\pipeline\upload.ps1
#
# EXAMPLES:
#   .\pipeline\upload.ps1 -File "data\ap_2024.xlsx" -Type assembly -State "Andhra Pradesh" -Year 2024
#   .\pipeline\upload.ps1 -File "data\ls_2019.pdf"  -Type loksabha -Year 2019
#   .\pipeline\upload.ps1 -Scan "data\new_data\" -State "Karnataka" -Type assembly
#   .\pipeline\upload.ps1 -Install
#   .\pipeline\upload.ps1 -Help

param(
    [string]$File,
    [string]$Cands,
    [string]$Sheet,
    [string]$Scan,
    [string]$Type = 'assembly',
    [int]$Year = 2024,
    [string]$State,
    [string]$Name,
    [switch]$Replace,
    [switch]$DryRun,
    [switch]$Install,
    [switch]$StartServer,
    [switch]$Help
)

$ErrorActionPreference = 'Stop'
$PROJ_ROOT = Split-Path -Parent $PSScriptRoot
Set-Location $PROJ_ROOT

function Write-Banner {
    Write-Host ""
    Write-Host "  ============================================================" -ForegroundColor Cyan
    Write-Host "    ELECTROL INDIA --- Election Data Pipeline" -ForegroundColor Cyan
    Write-Host "    $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
    Write-Host "  ============================================================" -ForegroundColor Cyan
    Write-Host ""
}

function Write-OK   { param([string]$msg) Write-Host "  [OK]  $msg" -ForegroundColor Green }
function Write-ERR  { param([string]$msg) Write-Host "  [ERR] $msg" -ForegroundColor Red }
function Write-INFO { param([string]$msg) Write-Host "  [..]  $msg" -ForegroundColor Yellow }
function Write-STEP { param([string]$msg) Write-Host "`n  >> $msg" -ForegroundColor Cyan }

if ($Help) {
    Write-Host @"
ELECTROL INDIA - PowerShell Election Data Launcher

USAGE:
  .\pipeline\upload.ps1 [options]

OPTIONS:
  -File <path>    Excel/CSV/PDF/JSON file to import
  -Cands <path>   Separate candidates file with EVM + postal breakdown
  -Sheet <name>   Excel sheet name (uses active sheet by default)
  -Scan <folder>  Auto-scan folder and import all election files found
  -Type <type>    Election type: loksabha | assembly | bypoll | municipal | panchayat
  -Year <int>     Election year (default: 2024)
  -State <name>   State name, e.g. "Andhra Pradesh"
  -Name <title>   Custom election title
  -Replace        Delete existing records for this election before upload
  -DryRun         Parse and clean only, do not upload
  -Install        Install all required Python packages
  -StartServer    Start local web server on http://localhost:8000
  -Help           Show this help

EXAMPLES:
  .\pipeline\upload.ps1 -Install
  .\pipeline\upload.ps1 -File "data\ap_2024.xlsx" -Type assembly -State "Andhra Pradesh" -Year 2024
  .\pipeline\upload.ps1 -File "data\ls_2024.pdf" -Type loksabha -Year 2024
  .\pipeline\upload.ps1 -Scan "data\pending\" -Type assembly -Year 2023
  .\pipeline\upload.ps1 -File "data\test.xlsx" -DryRun -Type assembly -State Bihar -Year 2020
"@
    exit 0
}

Write-Banner

if ($Install) {
    Write-STEP "Installing Python dependencies..."
    $reqs = "$PROJ_ROOT\pipeline\requirements.txt"
    if (Test-Path $reqs) {
        python -m pip install -r $reqs --upgrade
    } else {
        python -m pip install supabase openpyxl pdfplumber python-dotenv
    }
    Write-OK "All dependencies installed."
    exit 0
}

if ($StartServer) {
    Write-STEP "Starting local web server at http://localhost:8000 ..."
    Write-INFO "Press Ctrl+C to stop"
    python -m http.server 8000
    exit 0
}

$envFile = "$PROJ_ROOT\.env"
if (-not (Test-Path $envFile)) {
    Write-ERR ".env file not found! Create it with SUPABASE_URL and SUPABASE_KEY"
    exit 1
}
Write-OK ".env found"

try {
    $pyVersion = python --version 2>&1
    Write-OK "Python: $pyVersion"
} catch {
    Write-ERR "Python not found. Install from https://python.org"
    exit 1
}

$pipelineScript = "$PROJ_ROOT\pipeline\election_pipeline.py"
$pyArgs = @()

if ($Scan) {
    if (-not (Test-Path $Scan)) { Write-ERR "Folder not found: $Scan"; exit 1 }
    $pyArgs += "--scan", $Scan
} elseif ($File) {
    if (-not (Test-Path $File)) { Write-ERR "File not found: $File"; exit 1 }
    $pyArgs += "--file", $File
} else {
    Write-ERR "Provide -File <path> or -Scan <folder>  (use -Help for details)"
    exit 1
}

if ($Cands)  { $pyArgs += "--cands", $Cands }
if ($Sheet)  { $pyArgs += "--sheet", $Sheet }
$pyArgs += "--type", $Type
$pyArgs += "--year", $Year
if ($State)  { $pyArgs += "--state", $State }
if ($Name)   { $pyArgs += "--name", $Name }
if ($Replace){ $pyArgs += "--replace" }
if ($DryRun) { $pyArgs += "--dry-run" }

$targetPath = if ($File) { $File } else { $Scan }
Write-INFO "Target: $targetPath  Type: $Type  State: $State  Year: $Year"
Write-Host ""

try {
    python $pipelineScript @pyArgs
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-OK "Pipeline completed successfully!"
        Write-INFO "Open http://localhost:8000 to see updated data"
        Write-INFO "Check upload_log.json for history"
    } else {
        Write-ERR "Pipeline exited with code $LASTEXITCODE"
        exit 1
    }
} catch {
    Write-ERR "Error: $_"
    exit 1
}
