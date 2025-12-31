@echo off
REM Remove all 15-minute scheduled tasks
echo ============================================
echo Removing 15-Minute Content Tasks
echo ============================================
echo.

for %%t in (1430 1445 1500 1515 1530 1545 1600 1615 1630 1645 1700 1715 1730 1745 1800 1815 1830 1845 1900 1915 1930 1945 2000 2015 2030 2045 2100 2115 2130 2145 2200) do (
    schtasks /delete /tn "SP500_15min_%%t" /f 2>nul
)

echo.
echo All 15-minute tasks have been removed.
pause
