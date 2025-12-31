@echo off
REM Mid-Day Review - 12:00 PM ET / 6:00 PM Morocco
cd /d "C:\Users\arhou\OneDrive\Bureau\projet omar\S&P USA"
python telegram_bot_pro.py midday >> logs\telegram_midday.log 2>&1
