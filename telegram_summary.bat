@echo off
REM End of Day Summary - 5:00 PM ET / 11:00 PM Morocco
cd /d "C:\Users\arhou\OneDrive\Bureau\projet omar\S&P USA"
python telegram_bot_pro.py summary >> logs\telegram_summary.log 2>&1
