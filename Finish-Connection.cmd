@echo off
setlocal
cd /d "%~dp0"
if not exist "tools\sync-public-data.mjs" goto incomplete
echo Checking the configured account backend...
call npm run check:connection
if errorlevel 1 goto failed
echo Uploading only changed public datasets. Existing account tables are preserved.
call npm run data:push
if errorlevel 1 goto failed
call npm run data:verify
if errorlevel 1 goto failed
echo Connection verified. Restart Start-Website.cmd to use this project.
pause
exit /b 0
:incomplete
echo Run Finish-Connection.cmd inside the complete Electrol-India.Com folder.
pause
exit /b 1
:failed
echo Connection is incomplete. Read the error above. Existing local data remains available.
pause
exit /b 1
