$ErrorActionPreference = "Stop"
$projectRoot = $PSScriptRoot
$assetData = "$(Join-Path $projectRoot 'assets');assets"
$icon = Join-Path $projectRoot "assets\violino.ico"

Push-Location $projectRoot
try {
    & python -m pip install -r requirements-build.txt
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install build dependencies."
    }

    & python -m PyInstaller `
        --noconfirm `
        --clean `
        --windowed `
        --onedir `
        --name ViolinMentor `
        --icon $icon `
        --add-data $assetData `
        --collect-all customtkinter `
        --collect-data matplotlib `
        --collect-all PIL `
        --collect-all _sounddevice_data `
        main.py
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller failed to build the application."
    }

    $executable = Join-Path $projectRoot "dist\ViolinMentor\ViolinMentor.exe"
    if (-not (Test-Path -LiteralPath $executable)) {
        throw "The executable was not found at the expected path: $executable"
    }

    $desktop = [Environment]::GetFolderPath("Desktop")
    $shortcutPath = Join-Path $desktop "ViolinMentor.lnk"
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($shortcutPath)
    $shortcut.TargetPath = $executable
    $shortcut.WorkingDirectory = Split-Path -Parent $executable
    $shortcut.Description = "Open ViolinMentor"
    $shortcut.IconLocation = "$icon,0"
    $shortcut.Save()

    Write-Host "Executable: $executable"
    Write-Host "Desktop shortcut: $shortcutPath"
    Write-Host "Keep the entire dist\ViolinMentor folder when moving the application."
}
finally {
    Pop-Location
}
