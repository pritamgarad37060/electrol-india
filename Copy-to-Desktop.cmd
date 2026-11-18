@echo off
if not exist "%~dp0js\integration.js" (
 echo Run this command from inside the complete Electrol-India.Com project folder.
 pause
 exit /b 1
)
set "ELECTROL_COPY_SOURCE=%~dp0"
powershell -NoProfile -Command "$ErrorActionPreference='Stop'; $target=Join-Path ([Environment]::GetFolderPath('Desktop')) 'Electrol India.Com'; if(Test-Path -LiteralPath $target){throw 'Desktop target already exists; it was not overwritten.'}; Copy-Item -LiteralPath $env:ELECTROL_COPY_SOURCE -Destination $target -Recurse; Write-Output ('Created '+$target)"
pause
