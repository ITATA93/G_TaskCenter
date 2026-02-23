param(
    [string]$TeamName,
    [string]$Prompt
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$WorkspaceRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)
$DocsDir = Join-Path $WorkspaceRoot "docs"
$DevLogPath = Join-Path $DocsDir "DEVLOG.md"

if (!(Test-Path $DocsDir)) {
    New-Item -ItemType Directory -Path $DocsDir | Out-Null
}

if (!(Test-Path $DevLogPath)) {
    Set-Content -Path $DevLogPath -Value "# Development Log" -Encoding UTF8
}

$Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

$LogEntry = @"

## [Auto-Memory] Team Execution: $TeamName
**Date**: $Timestamp
**Task**: $Prompt
**Result**: Completed successfully.
"@

Add-Content -Path $DevLogPath -Value $LogEntry -Encoding UTF8
Write-Host "[MEMORY INFO] DEVLOG.md updated autonomously." -ForegroundColor Cyan
