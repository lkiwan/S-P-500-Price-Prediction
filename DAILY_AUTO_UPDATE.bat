@echo off
REM ========================================================================
REM S&P 500 DAILY AUTOMATED UPDATE
REM ========================================================================
REM This script runs the automated daily update:
REM - Fetches latest prices
REM - Generates new prediction
REM - Updates accuracy for previous predictions
REM ========================================================================

cd /d "%~dp0"

echo.
echo ========================================================================
echo S&P 500 DAILY AUTOMATED UPDATE
echo ========================================================================
echo Time: %date% %time%
echo ========================================================================
echo.

REM Run the daily update script and save output to log
python daily_update.py >> daily_update.log 2>&1

REM Check if it succeeded
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================================================
    echo SUCCESS - Daily update completed
    echo ========================================================================
    echo.
) else (
    echo.
    echo ========================================================================
    echo ERROR - Daily update failed
    echo ========================================================================
    echo.
)

REM Optionally restart the Docker container if you're running the dashboard
REM Uncomment the line below if you want to auto-restart the dashboard
REM docker-compose restart

echo Log saved to: daily_update.log
echo.
