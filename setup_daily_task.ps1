# ========================================================================
# Setup Windows Task Scheduler for S&P 500 Daily Updates
# ========================================================================
# This PowerShell script creates a scheduled task that runs daily
# at 5:00 PM (after market close) to update predictions
# ========================================================================

Write-Host ""
Write-Host "========================================================================"
Write-Host "SETTING UP DAILY AUTOMATED UPDATE TASK"
Write-Host "========================================================================"
Write-Host ""

# Get the current directory
$CurrentDir = Get-Location
$ScriptPath = Join-Path $CurrentDir "DAILY_AUTO_UPDATE.bat"
$LogPath = Join-Path $CurrentDir "daily_update.log"

Write-Host "Script location: $ScriptPath"
Write-Host "Log location: $LogPath"
Write-Host ""

# Check if script exists
if (-Not (Test-Path $ScriptPath)) {
    Write-Host "ERROR: DAILY_AUTO_UPDATE.bat not found in current directory"
    Write-Host "Please run this script from the project root directory"
    exit 1
}

# Task details
$TaskName = "SP500_Daily_Update"
$TaskDescription = "Automatically fetch S&P 500 prices and generate daily predictions"
$TriggerTime = "17:00"  # 5:00 PM (after market close at 4:00 PM EST)

Write-Host "Creating scheduled task: $TaskName"
Write-Host "Trigger time: $TriggerTime daily"
Write-Host ""

# Remove existing task if it exists
$ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($ExistingTask) {
    Write-Host "Removing existing task..."
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# Create the action (what to run)
$Action = New-ScheduledTaskAction -Execute $ScriptPath -WorkingDirectory $CurrentDir

# Create the trigger (when to run)
$Trigger = New-ScheduledTaskTrigger -Daily -At $TriggerTime

# Create task settings
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 30)

# Register the task
try {
    Register-ScheduledTask `
        -TaskName $TaskName `
        -Description $TaskDescription `
        -Action $Action `
        -Trigger $Trigger `
        -Settings $Settings `
        -User $env:USERNAME `
        -RunLevel Highest

    Write-Host ""
    Write-Host "========================================================================"
    Write-Host "SUCCESS - Scheduled task created!"
    Write-Host "========================================================================"
    Write-Host ""
    Write-Host "Task details:"
    Write-Host "  Name: $TaskName"
    Write-Host "  Schedule: Daily at $TriggerTime"
    Write-Host "  Script: $ScriptPath"
    Write-Host "  Log: $LogPath"
    Write-Host ""
    Write-Host "The task will run automatically every day at $TriggerTime"
    Write-Host ""
    Write-Host "To manage the task:"
    Write-Host "  - Open Task Scheduler (taskschd.msc)"
    Write-Host "  - Look for '$TaskName' in Task Scheduler Library"
    Write-Host ""
    Write-Host "To run manually right now:"
    Write-Host "  Start-ScheduledTask -TaskName '$TaskName'"
    Write-Host ""
    Write-Host "To remove the task:"
    Write-Host "  Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false"
    Write-Host ""
    Write-Host "========================================================================"
    Write-Host ""

} catch {
    Write-Host ""
    Write-Host "========================================================================"
    Write-Host "ERROR - Failed to create scheduled task"
    Write-Host "========================================================================"
    Write-Host ""
    Write-Host "Error details: $_"
    Write-Host ""
    Write-Host "NOTE: You may need to run PowerShell as Administrator"
    Write-Host ""
    exit 1
}

# Ask if user wants to test run now
Write-Host ""
$Response = Read-Host "Would you like to test run the task now? (y/n)"
if ($Response -eq 'y' -or $Response -eq 'Y') {
    Write-Host ""
    Write-Host "Running task now..."
    Start-ScheduledTask -TaskName $TaskName
    Write-Host "Task started! Check the output in the console or log file."
}

Write-Host ""
