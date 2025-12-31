@echo off
REM Market Opening Update - 8:00 AM ET / 2:00 PM Morocco
cd /d "C:\Users\arhou\OneDrive\Bureau\projet omar\S&P USA"
python telegram_bot_pro.py opening >> logs\telegram_opening.log 2>&1
