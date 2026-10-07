@echo off
chcp 65001 >nul
echo ========================================================
echo    🛑 STOPPING TRADE GUARDIAN BOT...
echo ========================================================
powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"name = 'python.exe'\" | Where-Object { $_.CommandLine -like '*bot.py*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force; Write-Host 'Stopped bot process ID:' $_.ProcessId }"
echo.
echo [*] Done! Bot is now stopped.
timeout /t 3 >nul
