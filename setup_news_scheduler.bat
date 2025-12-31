@echo off
echo ============================================
echo  S&P 500 News Scheduler Setup
echo  Posts market news every 30 minutes
echo ============================================

set "PROJECT_DIR=C:\Users\arhou\OneDrive\Bureau\projet omar\S&P USA"

echo.
echo Creating 22 scheduled tasks for news updates...
echo Time range: 14:00 - 00:30 (Morocco Time)
echo.

:: 14:00 - 14:30
schtasks /create /tn "SP500_News_1400" /tr "cmd /c cd /d \"%PROJECT_DIR%\" && python telegram_ai_bot.py news" /sc daily /st 14:00 /f >nul 2>&1 && echo [OK] News at 14:00 || echo [ERROR] 14:00
schtasks /create /tn "SP500_News_1430" /tr "cmd /c cd /d \"%PROJECT_DIR%\" && python telegram_ai_bot.py news" /sc daily /st 14:30 /f >nul 2>&1 && echo [OK] News at 14:30 || echo [ERROR] 14:30

:: 15:00 - 15:30
schtasks /create /tn "SP500_News_1500" /tr "cmd /c cd /d \"%PROJECT_DIR%\" && python telegram_ai_bot.py news" /sc daily /st 15:00 /f >nul 2>&1 && echo [OK] News at 15:00 || echo [ERROR] 15:00
schtasks /create /tn "SP500_News_1530" /tr "cmd /c cd /d \"%PROJECT_DIR%\" && python telegram_ai_bot.py news" /sc daily /st 15:30 /f >nul 2>&1 && echo [OK] News at 15:30 || echo [ERROR] 15:30

:: 16:00 - 16:30
schtasks /create /tn "SP500_News_1600" /tr "cmd /c cd /d \"%PROJECT_DIR%\" && python telegram_ai_bot.py news" /sc daily /st 16:00 /f >nul 2>&1 && echo [OK] News at 16:00 || echo [ERROR] 16:00
schtasks /create /tn "SP500_News_1630" /tr "cmd /c cd /d \"%PROJECT_DIR%\" && python telegram_ai_bot.py news" /sc daily /st 16:30 /f >nul 2>&1 && echo [OK] News at 16:30 || echo [ERROR] 16:30

:: 17:00 - 17:30
schtasks /create /tn "SP500_News_1700" /tr "cmd /c cd /d \"%PROJECT_DIR%\" && python telegram_ai_bot.py news" /sc daily /st 17:00 /f >nul 2>&1 && echo [OK] News at 17:00 || echo [ERROR] 17:00
schtasks /create /tn "SP500_News_1730" /tr "cmd /c cd /d \"%PROJECT_DIR%\" && python telegram_ai_bot.py news" /sc daily /st 17:30 /f >nul 2>&1 && echo [OK] News at 17:30 || echo [ERROR] 17:30

:: 18:00 - 18:30
schtasks /create /tn "SP500_News_1800" /tr "cmd /c cd /d \"%PROJECT_DIR%\" && python telegram_ai_bot.py news" /sc daily /st 18:00 /f >nul 2>&1 && echo [OK] News at 18:00 || echo [ERROR] 18:00
schtasks /create /tn "SP500_News_1830" /tr "cmd /c cd /d \"%PROJECT_DIR%\" && python telegram_ai_bot.py news" /sc daily /st 18:30 /f >nul 2>&1 && echo [OK] News at 18:30 || echo [ERROR] 18:30

:: 19:00 - 19:30
schtasks /create /tn "SP500_News_1900" /tr "cmd /c cd /d \"%PROJECT_DIR%\" && python telegram_ai_bot.py news" /sc daily /st 19:00 /f >nul 2>&1 && echo [OK] News at 19:00 || echo [ERROR] 19:00
schtasks /create /tn "SP500_News_1930" /tr "cmd /c cd /d \"%PROJECT_DIR%\" && python telegram_ai_bot.py news" /sc daily /st 19:30 /f >nul 2>&1 && echo [OK] News at 19:30 || echo [ERROR] 19:30

:: 20:00 - 20:30
schtasks /create /tn "SP500_News_2000" /tr "cmd /c cd /d \"%PROJECT_DIR%\" && python telegram_ai_bot.py news" /sc daily /st 20:00 /f >nul 2>&1 && echo [OK] News at 20:00 || echo [ERROR] 20:00
schtasks /create /tn "SP500_News_2030" /tr "cmd /c cd /d \"%PROJECT_DIR%\" && python telegram_ai_bot.py news" /sc daily /st 20:30 /f >nul 2>&1 && echo [OK] News at 20:30 || echo [ERROR] 20:30

:: 21:00 - 21:30
schtasks /create /tn "SP500_News_2100" /tr "cmd /c cd /d \"%PROJECT_DIR%\" && python telegram_ai_bot.py news" /sc daily /st 21:00 /f >nul 2>&1 && echo [OK] News at 21:00 || echo [ERROR] 21:00
schtasks /create /tn "SP500_News_2130" /tr "cmd /c cd /d \"%PROJECT_DIR%\" && python telegram_ai_bot.py news" /sc daily /st 21:30 /f >nul 2>&1 && echo [OK] News at 21:30 || echo [ERROR] 21:30

:: 22:00 - 22:30
schtasks /create /tn "SP500_News_2200" /tr "cmd /c cd /d \"%PROJECT_DIR%\" && python telegram_ai_bot.py news" /sc daily /st 22:00 /f >nul 2>&1 && echo [OK] News at 22:00 || echo [ERROR] 22:00
schtasks /create /tn "SP500_News_2230" /tr "cmd /c cd /d \"%PROJECT_DIR%\" && python telegram_ai_bot.py news" /sc daily /st 22:30 /f >nul 2>&1 && echo [OK] News at 22:30 || echo [ERROR] 22:30

:: 23:00 - 23:30
schtasks /create /tn "SP500_News_2300" /tr "cmd /c cd /d \"%PROJECT_DIR%\" && python telegram_ai_bot.py news" /sc daily /st 23:00 /f >nul 2>&1 && echo [OK] News at 23:00 || echo [ERROR] 23:00
schtasks /create /tn "SP500_News_2330" /tr "cmd /c cd /d \"%PROJECT_DIR%\" && python telegram_ai_bot.py news" /sc daily /st 23:30 /f >nul 2>&1 && echo [OK] News at 23:30 || echo [ERROR] 23:30

:: 00:00 - 00:30
schtasks /create /tn "SP500_News_0000" /tr "cmd /c cd /d \"%PROJECT_DIR%\" && python telegram_ai_bot.py news" /sc daily /st 00:00 /f >nul 2>&1 && echo [OK] News at 00:00 || echo [ERROR] 00:00
schtasks /create /tn "SP500_News_0030" /tr "cmd /c cd /d \"%PROJECT_DIR%\" && python telegram_ai_bot.py news" /sc daily /st 00:30 /f >nul 2>&1 && echo [OK] News at 00:30 || echo [ERROR] 00:30

echo.
echo ============================================
echo  News Scheduler Setup Complete!
echo ============================================
echo.
echo 22 news updates scheduled (every 30 min)
echo Time range: 14:00 - 00:30 (Morocco Time)
echo.
echo To test now: python telegram_ai_bot.py news
echo.
pause
