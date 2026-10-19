param([switch]$Rebuild)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$editorExe = 'D:\Epic\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
if (!(Test-Path -LiteralPath (Join-Path $projectRoot 'Transfer\scene.json'))) { throw 'Run the isolated Unity export first; Transfer/scene.json is missing.' }
if ($Rebuild) { $env:TIANNANGE_REBUILD = '1' }
try {
    & $editorExe (Join-Path $projectRoot 'TianNanGe.uproject') '-run=pythonscript' "-script=$PSScriptRoot\import_scene.py" '-unattended' '-NullRHI' '-nop4' "-abslog=$projectRoot\Saved\Logs\migration.log"
    if ($LASTEXITCODE) { throw "Unreal import failed: $LASTEXITCODE" }
    if (Test-Path -LiteralPath (Join-Path $projectRoot 'Transfer\kloofendal_4k.hdr')) {
        & $editorExe (Join-Path $projectRoot 'TianNanGe.uproject') '-run=pythonscript' "-script=$PSScriptRoot\install_hdri.py" '-unattended' '-NullRHI' '-nop4' "-abslog=$projectRoot\Saved\Logs\hdri-import.log"
        if ($LASTEXITCODE) { throw "Unreal HDRI import failed: $LASTEXITCODE" }
    }
    & $editorExe (Join-Path $projectRoot 'TianNanGe.uproject') '-run=pythonscript' "-script=$PSScriptRoot\add_review_camera.py" '-unattended' '-NullRHI' '-nop4' "-abslog=$projectRoot\Saved\Logs\review-camera.log"
    if ($LASTEXITCODE) { throw "Unreal review camera creation failed: $LASTEXITCODE" }
    & $editorExe (Join-Path $projectRoot 'TianNanGe.uproject') '-run=pythonscript' "-script=$PSScriptRoot\validate_scene.py" '-unattended' '-NullRHI' '-nop4' "-abslog=$projectRoot\Saved\Logs\validation.log"
    if ($LASTEXITCODE) { throw "Unreal validation failed: $LASTEXITCODE" }
} finally { Remove-Item Env:\TIANNANGE_REBUILD -ErrorAction SilentlyContinue }
