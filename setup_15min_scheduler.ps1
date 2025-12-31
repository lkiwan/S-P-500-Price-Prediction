# S&P 500 Telegram Bot - 15-Minute Posts Scheduler Setup (PowerShell)
# Run as Administrator

$workDir = "C:\Users\arhou\OneDrive\Bureau\projet omar\S&P USA"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "S&P 500 - 15-Minute Content Scheduler" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Times for 15-minute intervals (Morocco time: 14:30 - 22:00)
$times = @(
    "14:30", "14:45", "15:00", "15:15", "15:30", "15:45",
    "16:00", "16:15", "16:30", "16:45", "17:00", "17:15",
    "17:30", "17:45", "18:00", "18:15", "18:30", "18:45",
    "19:00", "19:15", "19:30", "19:45", "20:00", "20:15",
    "20:30", "20:45", "21:00", "21:15", "21:30", "21:45", "22:00"
)

$count = 1
$total = $times.Count

foreach ($time in $times) {
    $taskName = "SP500_15min_$($time.Replace(':', ''))"
    Write-Host "[$count/$total] Creating task for $time..." -ForegroundColor Yellow

    $action = New-ScheduledTaskAction -Execute "python" -Argument "telegram_ai_bot.py auto" -WorkingDirectory $workDir
    $trigger = New-ScheduledTaskTrigger -Daily -At $time
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

    # Remove existing task if exists
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue

    # Create new task
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description "15-min content at $time" | Out-Null

    $count++
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "All $total tasks created successfully!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Schedule: Every 15 minutes from 14:30 to 22:00 Morocco time"
Write-Host ""
Write-Host "Content Types (rotating randomly):"
Write-Host "  - Technical Analysis (20%)"
Write-Host "  - Fundamental Analysis (15%)"
Write-Host "  - Historical Quotes (15%)"
Write-Host "  - Market History (15%)"
Write-Host "  - Trading Tips (15%)"
Write-Host "  - Market Statistics (10%)"
Write-Host "  - Did You Know Facts (10%)"
Write-Host ""
