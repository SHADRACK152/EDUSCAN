# EDUSCAN Windows Installer Builder (PowerShell)
# Usage: .\build.ps1

param(
    [switch]$SkipDeps = $false,
    [switch]$CleanOnly = $false
)

function Write-Header {
    param([string]$Text)
    Write-Host "`n$('='*60)" -ForegroundColor Cyan
    Write-Host "▶ $Text" -ForegroundColor Cyan
    Write-Host "$('='*60)" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Text)
    Write-Host "✅ $Text" -ForegroundColor Green
}

function Write-Error {
    param([string]$Text)
    Write-Host "❌ $Text" -ForegroundColor Red
}

function Write-Info {
    param([string]$Text)
    Write-Host "ℹ️  $Text" -ForegroundColor Yellow
}

# Main script
Clear-Host
Write-Host "EDUSCAN Windows Installer Builder" -ForegroundColor Cyan -BackgroundColor Black

# Check Python
Write-Info "Checking Python installation..."
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Error "Python not found. Please install from: https://www.python.org/downloads/"
    exit 1
}
Write-Success "Python found: $($python.Source)"

# Setup virtual environment
Write-Header "Setting up environment"
if (-not (Test-Path ".\.venv")) {
    Write-Info "Creating virtual environment..."
    & python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to create virtual environment"
        exit 1
    }
}
Write-Success "Virtual environment ready"

# Activate venv
& .\.venv\Scripts\Activate.ps1

# Create icon if missing
Write-Header "Checking for application icon"
if (-not (Test-Path ".\assets\icon.ico")) {
    Write-Info "Creating application icon..."
    & python create_icon.py
}
Write-Success "Icon ready"

# Install dependencies
if (-not $SkipDeps) {
    Write-Header "Installing dependencies"
    Write-Info "This may take a few minutes..."
    
    & python -m pip install -q --upgrade pip
    & python -m pip install -q PyInstaller
    & python -m pip install -q -r requirements.txt
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to install dependencies"
        exit 1
    }
    Write-Success "Dependencies installed"
}

# Clean previous builds
Write-Header "Cleaning previous builds"
@("build", "dist", "__pycache__") | ForEach-Object {
    if (Test-Path $_) {
        Remove-Item -Path $_ -Recurse -Force
        Write-Info "Removed: $_/"
    }
}

if ($CleanOnly) {
    Write-Success "Clean completed"
    exit 0
}

# Build executable
Write-Header "Building executable"
$pyinstaller_args = @(
    "main.py",
    "--onedir",
    "--windowed",
    "--name", "EDUSCAN",
    "--add-data", "gui;gui",
    "--add-data", "face_engine;face_engine",
    "--add-data", "voice_engine;voice_engine",
    "--add-data", "database;database",
    "--add-data", "assets;assets",
    "--add-data", "themes;themes"
)

& python -m PyInstaller @pyinstaller_args

if ($LASTEXITCODE -ne 0) {
    Write-Error "Build failed"
    exit 1
}
Write-Success "Executable built successfully"

# Create portable ZIP
Write-Header "Creating portable ZIP"
if (Test-Path "dist\EDUSCAN") {
    Compress-Archive -Path "dist\EDUSCAN" -DestinationPath "dist\EDUSCAN-Portable.zip" -Force
    Write-Success "Created: dist/EDUSCAN-Portable.zip"
}

# Final summary
Write-Header "BUILD COMPLETE!"
Write-Host "
📁 Output files:
  • dist/EDUSCAN-Portable.zip
  • dist/EDUSCAN/EDUSCAN.exe

▶ Next steps:
  1. Test: .\dist\EDUSCAN\EDUSCAN.exe
  2. Share: dist\EDUSCAN-Portable.zip
  3. Install: Extract and run EDUSCAN.exe

" -ForegroundColor Green

Write-Host "For advanced options:" -ForegroundColor Yellow
Write-Host "  .\build.ps1 -SkipDeps   (Skip dependency installation)
  .\build.ps1 -CleanOnly  (Clean builds only)" -ForegroundColor Yellow
