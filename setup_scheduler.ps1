# S&P 500 Telegram Bot - Task Scheduler Setup (PowerShell)
# Run as Administrator

$workDir = "C:\Users\arhou\OneDrive\Bureau\projet omar\S&P USA"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "S&P 500 Telegram Bot Scheduler Setup" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Create logs directory
if (!(Test-Path "$workDir\logs")) {
    New-Item -ItemType Directory -Path "$workDir\logs" | Out-Null
}

# Define tasks
$tasks = @(
    @{Name="SP500_Telegram_Opening"; Time="14:00"; Arg="opening"; Desc="Market Opening (14:00 Morocco)"},
    @{Name="SP500_Telegram_Signal"; Time="16:00"; Arg="signal"; Desc="First Signal (16:00 Morocco)"},
    @{Name="SP500_Telegram_Midday"; Time="18:00"; Arg="midday"; Desc="Mid-Day Review (18:00 Morocco)"},
    @{Name="SP500_Telegram_Preclose"; Time="21:00"; Arg="preclose"; Desc="Pre-Close (21:00 Morocco)"},
    @{Name="SP500_Telegram_Summary"; Time="23:00"; Arg="summary"; Desc="End of Day (23:00 Morocco)"},
    @{Name="SP500_Telegram_Night"; Time="01:00"; Arg="night"; Desc="Late Night (01:00 Morocco)"}
)

$count = 1
foreach ($task in $tasks) {
    Write-Host "[$count/6] Creating: $($task.Desc)..." -ForegroundColor Yellow

    $action = New-ScheduledTaskAction -Execute "python" -Argument "telegram_bot_pro.py $($task.Arg)" -WorkingDirectory $workDir
    $trigger = New-ScheduledTaskTrigger -Daily -At $task.Time
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

    # Remove existing task if exists
    Unregister-ScheduledTask -TaskName $task.Name -Confirm:$false -ErrorAction SilentlyContinue

    # Create new task
    Register-ScheduledTask -TaskName $task.Name -Action $action -Trigger $trigger -Settings $settings -Description $task.Desc | Out-Null

    Write-Host "   [OK] Created: $($task.Name)" -ForegroundColor Green
    $count++
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "All 6 tasks created successfully!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Schedule (Morocco Time):"
Write-Host "  14:00 - Market Opening Update"
Write-Host "  16:00 - First Signal Update"
Write-Host "  18:00 - Mid-Day Review"
Write-Host "  21:00 - Pre-Close Update"
Write-Host "  23:00 - End of Day Summary"
Write-Host "  01:00 - Late Night Update"
Write-Host ""
Write-Host "To view tasks: Get-ScheduledTask -TaskName 'SP500_Telegram_*'"
