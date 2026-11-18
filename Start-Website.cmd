@echo off
if not exist "%~dp0tools\server.mjs" (
 echo Open Start-Website.cmd inside the complete Electrol-India.Com project folder.
 pause
 exit /b 1
)
cd /d "%~dp0"
echo Starting Electrol India.Com. The server will print the available local address.
node --watch tools/server.mjs
pause
