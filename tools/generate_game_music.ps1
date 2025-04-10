# Runic Lands Game Music Generator Script
Write-Host "=== Runic Lands Game Music Generator ===" -ForegroundColor Cyan

# Kill any running Python processes to release file locks
try {
    Stop-Process -Name python -Force -ErrorAction SilentlyContinue
    Write-Host "Stopped any running Python processes" -ForegroundColor Yellow
} catch {
    Write-Host "No Python processes found to stop" -ForegroundColor Yellow
}

# Define paths
$audioDir = Join-Path -Path $PSScriptRoot -ChildPath "..\assets\audio"
$gameDir = Join-Path -Path $audioDir -ChildPath "game"

# Create game audio directory if it doesn't exist
if (-not (Test-Path $gameDir)) {
    New-Item -Path $gameDir -ItemType Directory -Force | Out-Null
    Write-Host "Created game audio directory: $gameDir" -ForegroundColor Green
}

# Remove old files if they exist
Write-Host "Cleaning up old game audio files..." -ForegroundColor Yellow
$oldFiles = @(
    "game_theme.wav",
    "enhanced_game_theme.wav"
)

foreach ($file in $oldFiles) {
    $filePath = Join-Path -Path $audioDir -ChildPath $file
    if (Test-Path $filePath) {
        try {
            Remove-Item -Path $filePath -Force
            Write-Host "Removed old file: $file" -ForegroundColor Green
        } catch {
            Write-Host "Warning: Could not remove $file. It may be in use." -ForegroundColor Yellow
        }
    }
}

# Remove any existing game sections
$gameSections = Get-ChildItem -Path $gameDir -Filter "game_section*.wav" -ErrorAction SilentlyContinue
if ($gameSections) {
    foreach ($section in $gameSections) {
        try {
            Remove-Item -Path $section.FullName -Force
            Write-Host "Removed old section file: $($section.Name)" -ForegroundColor Green
        } catch {
            Write-Host "Warning: Could not remove $($section.Name). It may be in use." -ForegroundColor Yellow
        }
    }
}

# Make sure numpy is installed
Write-Host "Checking for numpy dependency..." -ForegroundColor Yellow
try {
    python -c "import numpy" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Installing numpy..." -ForegroundColor Yellow
        python -m pip install numpy -q
    } else {
        Write-Host "Numpy is already installed" -ForegroundColor Green
    }
} catch {
    Write-Host "Installing numpy..." -ForegroundColor Yellow
    python -m pip install numpy -q
}

Write-Host "Starting game music generation..." -ForegroundColor Cyan

# Run the Python script to generate game music
try {
    python generate_game_music.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Game music generation completed successfully!" -ForegroundColor Green
    } else {
        Write-Host "Game music generation failed with exit code $LASTEXITCODE" -ForegroundColor Red
    }
} catch {
    Write-Host "Error running game music generator: $_" -ForegroundColor Red
    exit 1
}

# Verify the files were created
$successCount = 0
$totalExpected = 10

# Check generated files
for ($i = 1; $i -le $totalExpected; $i++) {
    $sectionFile = Join-Path -Path $gameDir -ChildPath "game_section$i.wav"
    if (Test-Path $sectionFile) {
        $successCount++
    }
}

# Check combined files
$gameTheme = Join-Path -Path $audioDir -ChildPath "game_theme.wav"
$enhancedGameTheme = Join-Path -Path $audioDir -ChildPath "enhanced_game_theme.wav"

$message = "$successCount of $totalExpected section files were successfully generated"
if ($successCount -eq $totalExpected) {
    Write-Host $message -ForegroundColor Green
    
    if ((Test-Path $gameTheme) -and (Test-Path $enhancedGameTheme)) {
        Write-Host "Combined game theme files were created successfully" -ForegroundColor Green
        
        # Get file info
        $fileSize = (Get-Item $gameTheme).Length / 1KB
        Write-Host "Game theme size: $([math]::Round($fileSize, 2)) KB" -ForegroundColor Cyan
        
        Write-Host "`nMusic generation complete! In-game music is ready to use.`n" -ForegroundColor Green
    } else {
        Write-Host "Warning: Combined game theme files were not created" -ForegroundColor Yellow
    }
} else {
    Write-Host $message -ForegroundColor Yellow
    Write-Host "Some section files are missing. Check the log for errors." -ForegroundColor Yellow
} 