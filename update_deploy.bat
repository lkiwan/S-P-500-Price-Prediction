@echo off
REM Quick script to commit and deploy updates to Render

echo ============================================================
echo Deploying Updates to Render
echo ============================================================
echo.

REM Show current status
echo Current changes:
git status --short
echo.

REM Ask for confirmation
set /p confirm="Deploy these changes? (y/n): "
if /i not "%confirm%"=="y" (
    echo Deployment cancelled.
    exit /b
)

REM Add all changes
echo.
echo Adding files...
git add .

REM Commit with timestamp
echo.
set commit_msg=Update: %date% %time:~0,5%
set /p custom_msg="Commit message (or press Enter for default): "
if not "%custom_msg%"=="" set commit_msg=%custom_msg%

echo Committing: %commit_msg%
git commit -m "%commit_msg%"

REM Push to GitHub (triggers Render auto-deploy)
echo.
echo Pushing to GitHub...
git push

echo.
echo ============================================================
echo ✅ Changes pushed to GitHub!
echo ============================================================
echo.
echo Render will automatically deploy your changes in ~2 minutes
echo Check status at: https://dashboard.render.com
echo.
pause
