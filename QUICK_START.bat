@echo off
echo ======================================================================
echo S&P 500 AI PREDICTION DASHBOARD
echo ======================================================================
echo.
echo Starting dashboard...
echo.

docker-compose up -d

echo.
echo ======================================================================
echo Dashboard is starting up...
echo Waiting 10 seconds for services to be ready...
echo ======================================================================
echo.

timeout /t 10 /nobreak

echo ======================================================================
echo DASHBOARD IS READY!
echo ======================================================================
echo.
echo Open your browser and visit:
echo.
echo   http://localhost:5000
echo.
echo OR try:
echo   http://127.0.0.1:5000
echo.
echo ======================================================================
echo.
echo Press any key to open the dashboard in your default browser...
pause > nul

start http://localhost:5000

echo.
echo ======================================================================
echo To view logs:    docker-compose logs -f
echo To stop:         docker-compose down
echo ======================================================================
echo.
