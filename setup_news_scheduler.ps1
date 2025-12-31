# Setup News Scheduler - Every 30 minutes during market hours
# Morocco timezone (14:00 - 01:00 = 8:00 AM - 7:00 PM ET)

$projectDir = "C:\Users\arhou\OneDrive\Bureau\projet omar\S&P USA"
$pythonExe = "python"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host " S&P 500 News Scheduler Setup" -ForegroundColor Cyan
Write-Host " Posts market news every 30 minutes" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# News posting times (Morocco time - every 30 min from 14:00 to 01:00)
$newsTimes = @(
    "14:00", "14:30",
    "15:00", "15:30",
    "16:00", "16:30",
    "17:00", "17:30",
    "18:00", "18:30",
    "19:00", "19:30",
    "20:00", "20:30",
    "21:00", "21:30",
    "22:00", "22:30",
    "23:00", "23:30",
    "00:00", "00:30"
)

Write-Host "`nCreating scheduled tasks for news updates..." -ForegroundColor Yellow

foreach ($time in $newsTimes) {
    $taskName = "SP500_News_$($time.Replace(':', ''))"

    # Create the action
    $action = New-ScheduledTaskAction -Execute $pythonExe `
        -Argument "telegram_ai_bot.py news" `
        -WorkingDirectory $projectDir

    # Create trigger for the time
    $trigger = New-ScheduledTaskTrigger -Daily -At $time

    # Create settings
    $settings = New-ScheduledTaskSettings -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries `
        -StartWhenAvailable `
        -ExecutionTimeLimit (New-TimeSpan -Minutes 5)

    # Remove existing task if it exists
    try {
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
    } catch {}

    # Register the task
    try {
        Register-ScheduledTask -TaskName $taskName `
            -Action $action `
            -Trigger $trigger `
            -Settings $settings `
            -Description "S&P 500 Market News Update at $time" | Out-Null

        Write-Host "  [OK] Created: $taskName at $time" -ForegroundColor Green
    } catch {
        Write-Host "  [ERROR] Failed to create: $taskName - $_" -ForegroundColor Red
    }
}

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host " News Scheduler Setup Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "`n22 news updates scheduled (every 30 min)" -ForegroundColor White
Write-Host "Time range: 14:00 - 00:30 (Morocco Time)" -ForegroundColor White
Write-Host "`nTo test now: python telegram_ai_bot.py news" -ForegroundColor Yellow
