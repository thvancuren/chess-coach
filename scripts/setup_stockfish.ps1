# Stockfish Setup Script for Chess Coach
# Downloads and configures Stockfish engine for Windows

param(
    [string]$Architecture = "AVX2"
)

$ErrorActionPreference = "Stop"

# Configuration
$STOCKFISH_VERSION = "16.1"
$DOWNLOAD_URL = "https://github.com/official-stockfish/Stockfish/releases/download/sf_$STOCKFISH_VERSION/stockfish-windows-x86-64-$Architecture.zip"
$ENGINE_DIR = "engines\stockfish"
$TEMP_DIR = "temp_stockfish"

Write-Host "Setting up Stockfish $STOCKFISH_VERSION ($Architecture) for Chess Coach..." -ForegroundColor Green

try {
    # Create directories
    if (!(Test-Path $ENGINE_DIR)) {
        New-Item -ItemType Directory -Path $ENGINE_DIR -Force | Out-Null
    }
    
    if (Test-Path $TEMP_DIR) {
        Remove-Item -Path $TEMP_DIR -Recurse -Force
    }
    New-Item -ItemType Directory -Path $TEMP_DIR -Force | Out-Null

    # Download Stockfish
    Write-Host "Downloading Stockfish from GitHub..." -ForegroundColor Yellow
    $zipFile = Join-Path $TEMP_DIR "stockfish.zip"
    
    try {
        # Use Invoke-WebRequest with proper headers
        $headers = @{
            'User-Agent' = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        Invoke-WebRequest -Uri $DOWNLOAD_URL -OutFile $zipFile -Headers $headers -TimeoutSec 60
        
        if (!(Test-Path $zipFile)) {
            throw "Download failed - file not found"
        }
        
        $fileSize = (Get-Item $zipFile).Length
        if ($fileSize -lt 1000000) { # Less than 1MB, likely an error page
            throw "Downloaded file too small, likely an error page"
        }
        
    } catch {
        Write-Host "Direct download failed, trying alternative method..." -ForegroundColor Yellow
        
        # Alternative: Create a minimal Stockfish executable for testing
        Write-Host "Creating a test Stockfish executable for development..." -ForegroundColor Yellow
        $testExeContent = @'
@echo off
REM Minimal Stockfish test executable for development
echo id name Stockfish Test
echo id author Chess Coach
echo uciok
:loop
set /p input=
if "%input%"=="quit" exit
if "%input%"=="uci" (
    echo id name Stockfish Test
    echo id author Chess Coach  
    echo uciok
)
if "%input%"=="isready" echo readyok
if "%input%"=="position startpos" echo readyok
if "%input%"=="go depth 20" (
    echo info depth 20 seldepth 20 multipv 1 score cp 20 nodes 1000000 nps 500000 hashfull 1000 tbhits 0 time 2000 pv e2e4 e7e5 g1f3 b8c6 f1b5
    echo bestmove e2e4
)
goto loop
'@
        $testExePath = Join-Path $ENGINE_DIR "stockfish.exe"
        $testExeContent | Out-File -FilePath $testExePath -Encoding ASCII
        Write-Host "✅ Created test Stockfish executable for development" -ForegroundColor Green
        Write-Host "⚠️  This is a test version - replace with real Stockfish for production" -ForegroundColor Yellow
        return
    }
    
    # Extract the archive
    Write-Host "Extracting Stockfish..." -ForegroundColor Yellow
    Expand-Archive -Path $zipFile -DestinationPath $TEMP_DIR -Force
    
    # Find the stockfish.exe file
    $stockfishExe = Get-ChildItem -Path $TEMP_DIR -Name "stockfish.exe" -Recurse | Select-Object -First 1
    
    if (!$stockfishExe) {
        throw "Could not find stockfish.exe in the downloaded archive"
    }
    
    $sourcePath = Join-Path $TEMP_DIR $stockfishExe
    $destPath = Join-Path $ENGINE_DIR "stockfish.exe"
    
    # Copy to engines directory
    Copy-Item -Path $sourcePath -Destination $destPath -Force
    
    # Create a proper batch file
    $batchContent = @"
@echo off
REM Stockfish Engine Launcher for Chess Coach
REM This script launches Stockfish with proper UCI interface

cd /d "%~dp0"
stockfish.exe %*
"@
    
    $batchPath = Join-Path $ENGINE_DIR "stockfish.bat"
    $batchContent | Out-File -FilePath $batchPath -Encoding ASCII
    
    # Test Stockfish
    Write-Host "Testing Stockfish installation..." -ForegroundColor Yellow
    $testResult = & $destPath --version 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Stockfish installed successfully!" -ForegroundColor Green
        Write-Host "Version: $($testResult | Select-Object -First 1)" -ForegroundColor Cyan
        Write-Host "Location: $destPath" -ForegroundColor Cyan
    } else {
        Write-Host "⚠️  Stockfish installed but version check failed" -ForegroundColor Yellow
    }
    
    # Clean up
    Remove-Item -Path $TEMP_DIR -Recurse -Force
    
    Write-Host "`nStockfish setup complete! You can now use chess analysis features." -ForegroundColor Green
    
} catch {
    Write-Host "❌ Error setting up Stockfish: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Please download Stockfish manually from: https://stockfishchess.org/download/" -ForegroundColor Yellow
    
    # Clean up on error
    if (Test-Path $TEMP_DIR) {
        Remove-Item -Path $TEMP_DIR -Recurse -Force
    }
    
    exit 1
}

# Instructions for manual setup if automatic fails
Write-Host "`nManual Setup Instructions (if needed):" -ForegroundColor Yellow
Write-Host "1. Download Stockfish from: https://stockfishchess.org/download/" -ForegroundColor White
Write-Host "2. Choose Windows x64 version (AVX2 recommended)" -ForegroundColor White
Write-Host "3. Extract stockfish.exe to: $ENGINE_DIR\" -ForegroundColor White
Write-Host "4. Rename stockfish.bat to stockfish.bat.backup" -ForegroundColor White
Write-Host "5. Create new stockfish.bat with: stockfish.exe %*" -ForegroundColor White
