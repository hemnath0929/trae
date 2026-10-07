@echo off
chcp 65001 >nul
title Trade Guardian Bot - Options Assistant
color 0A

echo ========================================================
echo    🛡️ TRADE GUARDIAN BOT - OPTIONS ASSISTANT
echo ========================================================
echo.
echo [*] Folder: d:\personal project\trading
echo [*] Telegram Bot: @Trading_phs_bot
echo [*] Starting Live Trading Assistant...
echo.
echo [*] Status: ONLINE! (Indha window close pannina bot offline aagum)
echo ========================================================
echo.

cd /d "d:\personal project\trading"

"C:\Python313\python.exe" bot.py

echo.
echo ========================================================
echo [!] Bot stopped. Press any key to close this window.
pause >nul
