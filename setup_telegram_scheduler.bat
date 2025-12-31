@echo off
REM ============================================================================
REM S&P 500 Telegram Bot - Windows Task Scheduler Setup
REM ============================================================================
REM
REM Schedule (Morocco Time):
REM   14:00 (2:00 PM)  - Market Opening Update
REM   16:00 (4:00 PM)  - First Signal Update
REM   18:00 (6:00 PM)  - Mid-Day Review
REM   21:00 (9:00 PM)  - Pre-Close Update
REM   23:00 (11:00 PM) - End of Day Summary
REM   01:00 (1:00 AM)  - Late Night Update (next day)
REM
REM ============================================================================

echo ============================================
echo S&P 500 Telegram Bot Scheduler Setup
echo ============================================
echo.

REM Create logs directory
if not exist "logs" mkdir logs

REM Set working directory
set WORKDIR=C:\Users\arhou\OneDrive\Bureau\projet omar\S&P USA

echo Creating scheduled tasks for Morocco time...
echo.

REM 1. Market Opening Update - 14:00 Morocco (8:00 AM ET)
echo [1/6] Creating Market Opening task (14:00)...
schtasks /create /tn "SP500_Telegram_Opening" /tr "cmd /c cd /d \"%WORKDIR%\" && python telegram_bot_pro.py opening >> logs\telegram_opening.log 2>&1" /sc daily /st 14:00 /f
echo.

REM 2. First Signal Update - 16:00 Morocco (10:00 AM ET)
echo [2/6] Creating First Signal task (16:00)...
schtasks /create /tn "SP500_Telegram_Signal" /tr "cmd /c cd /d \"%WORKDIR%\" && python telegram_bot_pro.py signal >> logs\telegram_signal.log 2>&1" /sc daily /st 16:00 /f
echo.

REM 3. Mid-Day Review - 18:00 Morocco (12:00 PM ET)
echo [3/6] Creating Mid-Day Review task (18:00)...
schtasks /create /tn "SP500_Telegram_Midday" /tr "cmd /c cd /d \"%WORKDIR%\" && python telegram_bot_pro.py midday >> logs\telegram_midday.log 2>&1" /sc daily /st 18:00 /f
echo.

REM 4. Pre-Close Update - 21:00 Morocco (3:00 PM ET)
echo [4/6] Creating Pre-Close task (21:00)...
schtasks /create /tn "SP500_Telegram_Preclose" /tr "cmd /c cd /d \"%WORKDIR%\" && python telegram_bot_pro.py preclose >> logs\telegram_preclose.log 2>&1" /sc daily /st 21:00 /f
echo.

REM 5. End of Day Summary - 23:00 Morocco (5:00 PM ET)
echo [5/6] Creating End of Day task (23:00)...
schtasks /create /tn "SP500_Telegram_Summary" /tr "cmd /c cd /d \"%WORKDIR%\" && python telegram_bot_pro.py summary >> logs\telegram_summary.log 2>&1" /sc daily /st 23:00 /f
echo.

REM 6. Late Night Update - 01:00 Morocco (7:00 PM ET)
echo [6/6] Creating Late Night task (01:00)...
schtasks /create /tn "SP500_Telegram_Night" /tr "cmd /c cd /d \"%WORKDIR%\" && python telegram_bot_pro.py night >> logs\telegram_night.log 2>&1" /sc daily /st 01:00 /f
echo.

echo ============================================
echo All tasks created successfully!
echo ============================================
echo.
echo Scheduled Tasks (Morocco Time):
echo   14:00 - Market Opening Update
echo   16:00 - First Signal Update
echo   18:00 - Mid-Day Review
echo   21:00 - Pre-Close Update
echo   23:00 - End of Day Summary
echo   01:00 - Late Night Update
echo.
echo To view tasks: schtasks /query /tn "SP500_Telegram_*"
echo To delete all: Run remove_telegram_scheduler.bat
echo.
pause
