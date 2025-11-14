@echo off
echo ======================================================================
echo AUTO-UPDATE S&P 500 PRICES
echo ======================================================================
echo.
echo Updating latest market prices...
echo.

cd /d "%~dp0"
python update_latest_data.py

echo.
echo ======================================================================
echo Restarting Docker container with updated prices...
echo ======================================================================
echo.

docker-compose restart

echo.
echo ======================================================================
echo PRICES UPDATED AND DASHBOARD RESTARTED!
echo ======================================================================
echo.
echo Dashboard is ready at: http://localhost:5000
echo.
pause
