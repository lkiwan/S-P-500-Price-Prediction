@echo off
REM First Signal Update - 10:00 AM ET / 4:00 PM Morocco
cd /d "C:\Users\arhou\OneDrive\Bureau\projet omar\S&P USA"
python telegram_bot_pro.py signal >> logs\telegram_signal.log 2>&1
