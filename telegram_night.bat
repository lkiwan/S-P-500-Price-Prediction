@echo off
REM Late Night Update - 7:00 PM ET / 1:00 AM Morocco
cd /d "C:\Users\arhou\OneDrive\Bureau\projet omar\S&P USA"
python telegram_bot_pro.py night >> logs\telegram_night.log 2>&1
