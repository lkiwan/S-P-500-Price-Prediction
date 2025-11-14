@echo off
REM Quick Deployment Script for S&P 500 Dashboard
REM This script provides easy deployment options

echo ============================================================
echo S&P 500 AI PREDICTION DASHBOARD - DEPLOYMENT TOOL
echo ============================================================
echo.

:menu
echo Select deployment option:
echo.
echo 1. Deploy with Docker Compose (Recommended)
echo 2. Build Docker Image Only
echo 3. Run Production Server (Windows - Waitress)
echo 4. Install Production Dependencies
echo 5. View Running Containers
echo 6. Stop All Containers
echo 7. Exit
echo.

set /p choice="Enter your choice (1-7): "

if "%choice%"=="1" goto docker_compose
if "%choice%"=="2" goto docker_build
if "%choice%"=="3" goto windows_production
if "%choice%"=="4" goto install_deps
if "%choice%"=="5" goto view_containers
if "%choice%"=="6" goto stop_containers
if "%choice%"=="7" goto end

echo Invalid choice. Please try again.
goto menu

:docker_compose
echo.
echo Starting deployment with Docker Compose...
docker-compose down
docker-compose up -d --build
echo.
echo Dashboard is running at: http://localhost:5000
echo.
pause
goto menu

:docker_build
echo.
echo Building Docker image...
docker build -t sp500-dashboard .
echo.
echo Image built successfully!
echo.
echo To run: docker run -d -p 5000:5000 sp500-dashboard
pause
goto menu

:windows_production
echo.
echo Starting production server (Windows)...
echo.
echo Installing waitress if needed...
pip install waitress
echo.
python run_production.py
pause
goto menu

:install_deps
echo.
echo Installing production dependencies...
pip install -r requirements_dashboard.txt
pip install waitress
echo.
echo Dependencies installed!
pause
goto menu

:view_containers
echo.
echo Running containers:
docker-compose ps
echo.
pause
goto menu

:stop_containers
echo.
echo Stopping all containers...
docker-compose down
echo.
echo Containers stopped!
pause
goto menu

:end
echo.
echo Goodbye!
exit
