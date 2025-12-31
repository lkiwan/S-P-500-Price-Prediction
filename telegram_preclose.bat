@echo off
REM Pre-Close Update - 3:00 PM ET / 9:00 PM Morocco
cd /d "C:\Users\arhou\OneDrive\Bureau\projet omar\S&P USA"
python telegram_bot_pro.py preclose >> logs\telegram_preclose.log 2>&1
