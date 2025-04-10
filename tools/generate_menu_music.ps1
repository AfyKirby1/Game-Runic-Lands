# Runic Lands Menu Music Generator PowerShell Script

Write-Host "`nCleaning up old audio files..."
$audioDir = Join-Path $PSScriptRoot "..\assets\audio"

# Kill any Python processes that might be holding files
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Remove old files
Get-ChildItem -Path $audioDir -Filter "menu_section*.wav" | ForEach-Object {
    try {
        Remove-Item $_.FullName -Force -ErrorAction Stop
        Write-Host "Removed $($_.Name)"
    } catch {
        Write-Host "Warning: Could not remove $($_.Name): $_"
    }
}

Write-Host "`nGenerating new menu music sections..."
# Run the Python script
$pythonScript = Join-Path $PSScriptRoot "generate_menu_music.py"
python $pythonScript

Write-Host "`nDone! Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 