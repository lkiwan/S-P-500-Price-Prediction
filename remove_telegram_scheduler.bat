@echo off
REM Remove all Telegram bot scheduled tasks
echo ============================================
echo Removing S&P 500 Telegram Bot Tasks
echo ============================================
echo.

schtasks /delete /tn "SP500_Telegram_Opening" /f 2>nul
schtasks /delete /tn "SP500_Telegram_Signal" /f 2>nul
schtasks /delete /tn "SP500_Telegram_Midday" /f 2>nul
schtasks /delete /tn "SP500_Telegram_Preclose" /f 2>nul
schtasks /delete /tn "SP500_Telegram_Summary" /f 2>nul
schtasks /delete /tn "SP500_Telegram_Night" /f 2>nul

echo.
echo All Telegram bot tasks have been removed.
pause
