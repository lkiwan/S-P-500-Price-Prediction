@echo off
REM ============================================================================
REM S&P 500 Telegram Bot - 15-Minute Posts Scheduler Setup
REM ============================================================================
REM
REM Posts educational content every 15 minutes during market hours
REM Market Hours: 9:30 AM - 4:00 PM ET (14:30 - 22:00 Morocco)
REM
REM Schedule (Morocco Time): Every 15 minutes from 14:30 to 22:00
REM
REM ============================================================================

echo ============================================
echo S&P 500 - 15-Minute Content Scheduler
echo ============================================
echo.

REM Set working directory
set WORKDIR=C:\Users\arhou\OneDrive\Bureau\projet omar\S&P USA

echo Creating 15-minute scheduled tasks (Morocco time)...
echo This will create tasks from 14:30 to 22:00 every 15 minutes
echo.

REM Market Hours: 14:30 - 22:00 Morocco Time (9:30 AM - 5:00 PM ET)

REM 14:30 - Market Open
schtasks /create /tn "SP500_15min_1430" /tr "cmd /c cd /d \"%WORKDIR%\" && python telegram_15min_bot.py auto >> logs\15min.log 2>&1" /sc daily /st 14:30 /f
REM 14:45
schtasks /create /tn "SP500_15min_1445" /tr "cmd /c cd /d \"%WORKDIR%\" && python telegram_15min_bot.py auto >> logs\15min.log 2>&1" /sc daily /st 14:45 /f
REM 15:00
schtasks /create /tn "SP500_15min_1500" /tr "cmd /c cd /d \"%WORKDIR%\" && python telegram_15min_bot.py auto >> logs\15min.log 2>&1" /sc daily /st 15:00 /f
REM 15:15
schtasks /create /tn "SP500_15min_1515" /tr "cmd /c cd /d \"%WORKDIR%\" && python telegram_15min_bot.py auto >> logs\15min.log 2>&1" /sc daily /st 15:15 /f
REM 15:30
schtasks /create /tn "SP500_15min_1530" /tr "cmd /c cd /d \"%WORKDIR%\" && python telegram_15min_bot.py auto >> logs\15min.log 2>&1" /sc daily /st 15:30 /f
REM 15:45
schtasks /create /tn "SP500_15min_1545" /tr "cmd /c cd /d \"%WORKDIR%\" && python telegram_15min_bot.py auto >> logs\15min.log 2>&1" /sc daily /st 15:45 /f
REM 16:00
schtasks /create /tn "SP500_15min_1600" /tr "cmd /c cd /d \"%WORKDIR%\" && python telegram_15min_bot.py auto >> logs\15min.log 2>&1" /sc daily /st 16:00 /f
REM 16:15
schtasks /create /tn "SP500_15min_1615" /tr "cmd /c cd /d \"%WORKDIR%\" && python telegram_15min_bot.py auto >> logs\15min.log 2>&1" /sc daily /st 16:15 /f
REM 16:30
schtasks /create /tn "SP500_15min_1630" /tr "cmd /c cd /d \"%WORKDIR%\" && python telegram_15min_bot.py auto >> logs\15min.log 2>&1" /sc daily /st 16:30 /f
REM 16:45
schtasks /create /tn "SP500_15min_1645" /tr "cmd /c cd /d \"%WORKDIR%\" && python telegram_15min_bot.py auto >> logs\15min.log 2>&1" /sc daily /st 16:45 /f
REM 17:00
schtasks /create /tn "SP500_15min_1700" /tr "cmd /c cd /d \"%WORKDIR%\" && python telegram_15min_bot.py auto >> logs\15min.log 2>&1" /sc daily /st 17:00 /f
REM 17:15
schtasks /create /tn "SP500_15min_1715" /tr "cmd /c cd /d \"%WORKDIR%\" && python telegram_15min_bot.py auto >> logs\15min.log 2>&1" /sc daily /st 17:15 /f
REM 17:30
schtasks /create /tn "SP500_15min_1730" /tr "cmd /c cd /d \"%WORKDIR%\" && python telegram_15min_bot.py auto >> logs\15min.log 2>&1" /sc daily /st 17:30 /f
REM 17:45
schtasks /create /tn "SP500_15min_1745" /tr "cmd /c cd /d \"%WORKDIR%\" && python telegram_15min_bot.py auto >> logs\15min.log 2>&1" /sc daily /st 17:45 /f
REM 18:00
schtasks /create /tn "SP500_15min_1800" /tr "cmd /c cd /d \"%WORKDIR%\" && python telegram_15min_bot.py auto >> logs\15min.log 2>&1" /sc daily /st 18:00 /f
REM 18:15
schtasks /create /tn "SP500_15min_1815" /tr "cmd /c cd /d \"%WORKDIR%\" && python telegram_15min_bot.py auto >> logs\15min.log 2>&1" /sc daily /st 18:15 /f
REM 18:30
schtasks /create /tn "SP500_15min_1830" /tr "cmd /c cd /d \"%WORKDIR%\" && python telegram_15min_bot.py auto >> logs\15min.log 2>&1" /sc daily /st 18:30 /f
REM 18:45
schtasks /create /tn "SP500_15min_1845" /tr "cmd /c cd /d \"%WORKDIR%\" && python telegram_15min_bot.py auto >> logs\15min.log 2>&1" /sc daily /st 18:45 /f
REM 19:00
schtasks /create /tn "SP500_15min_1900" /tr "cmd /c cd /d \"%WORKDIR%\" && python telegram_15min_bot.py auto >> logs\15min.log 2>&1" /sc daily /st 19:00 /f
REM 19:15
schtasks /create /tn "SP500_15min_1915" /tr "cmd /c cd /d \"%WORKDIR%\" && python telegram_15min_bot.py auto >> logs\15min.log 2>&1" /sc daily /st 19:15 /f
REM 19:30
schtasks /create /tn "SP500_15min_1930" /tr "cmd /c cd /d \"%WORKDIR%\" && python telegram_15min_bot.py auto >> logs\15min.log 2>&1" /sc daily /st 19:30 /f
REM 19:45
schtasks /create /tn "SP500_15min_1945" /tr "cmd /c cd /d \"%WORKDIR%\" && python telegram_15min_bot.py auto >> logs\15min.log 2>&1" /sc daily /st 19:45 /f
REM 20:00
schtasks /create /tn "SP500_15min_2000" /tr "cmd /c cd /d \"%WORKDIR%\" && python telegram_15min_bot.py auto >> logs\15min.log 2>&1" /sc daily /st 20:00 /f
REM 20:15
schtasks /create /tn "SP500_15min_2015" /tr "cmd /c cd /d \"%WORKDIR%\" && python telegram_15min_bot.py auto >> logs\15min.log 2>&1" /sc daily /st 20:15 /f
REM 20:30
schtasks /create /tn "SP500_15min_2030" /tr "cmd /c cd /d \"%WORKDIR%\" && python telegram_15min_bot.py auto >> logs\15min.log 2>&1" /sc daily /st 20:30 /f
REM 20:45
schtasks /create /tn "SP500_15min_2045" /tr "cmd /c cd /d \"%WORKDIR%\" && python telegram_15min_bot.py auto >> logs\15min.log 2>&1" /sc daily /st 20:45 /f
REM 21:00
schtasks /create /tn "SP500_15min_2100" /tr "cmd /c cd /d \"%WORKDIR%\" && python telegram_15min_bot.py auto >> logs\15min.log 2>&1" /sc daily /st 21:00 /f
REM 21:15
schtasks /create /tn "SP500_15min_2115" /tr "cmd /c cd /d \"%WORKDIR%\" && python telegram_15min_bot.py auto >> logs\15min.log 2>&1" /sc daily /st 21:15 /f
REM 21:30
schtasks /create /tn "SP500_15min_2130" /tr "cmd /c cd /d \"%WORKDIR%\" && python telegram_15min_bot.py auto >> logs\15min.log 2>&1" /sc daily /st 21:30 /f
REM 21:45
schtasks /create /tn "SP500_15min_2145" /tr "cmd /c cd /d \"%WORKDIR%\" && python telegram_15min_bot.py auto >> logs\15min.log 2>&1" /sc daily /st 21:45 /f
REM 22:00 - Market Close
schtasks /create /tn "SP500_15min_2200" /tr "cmd /c cd /d \"%WORKDIR%\" && python telegram_15min_bot.py auto >> logs\15min.log 2>&1" /sc daily /st 22:00 /f

echo.
echo ============================================
echo All 31 tasks created successfully!
echo ============================================
echo.
echo Schedule: Every 15 minutes from 14:30 to 22:00 Morocco time
echo (9:30 AM - 5:00 PM Eastern Time)
echo.
echo Content Types (rotating randomly):
echo   - Technical Analysis (20%%)
echo   - Fundamental Analysis (15%%)
echo   - Historical Quotes (15%%)
echo   - Market History (15%%)
echo   - Trading Tips (15%%)
echo   - Market Statistics (10%%)
echo   - Did You Know Facts (10%%)
echo.
echo To remove all: Run remove_15min_scheduler.bat
echo.
pause
