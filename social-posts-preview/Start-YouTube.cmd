@echo off
cd /d "%~dp0"
where node >nul 2>nul
if errorlevel 1 (
 echo Install Node.js 20 or newer, then run this file again.
 pause
 exit /b 1
)
echo Open http://127.0.0.1:8125 in your browser.
echo Keep this window open for automatic updates.
node youtube-server.mjs
pause
