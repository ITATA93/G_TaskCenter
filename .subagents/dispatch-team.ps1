<#
.SYNOPSIS
    Multi-vendor Agent Team orchestrator for Windows
.DESCRIPTION
    Executes a group of agents sequentially or in parallel based on manifest.json.
    PowerShell equivalent of dispatch-team.sh
.PARAMETER TeamName
    Name of the team defined in manifest.json (e.g., full-review)
.PARAMETER Prompt
    The overall task for the team
.EXAMPLE
    .\dispatch-team.ps1 full-review "Audit the auth module"
#>

param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$TeamName,

    [Parameter(Mandatory=$true, Position=1)]
    [string]$Prompt
)

$ErrorActionPreference = "Stop"

# Paths
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ManifestPath = Join-Path $ScriptDir "manifest.json"
$DispatchScript = Join-Path $ScriptDir "dispatch.ps1"

# Colors
function Write-Info    { param($msg) Write-Host "[TEAM INFO] $msg" -ForegroundColor Cyan }
function Write-Warn    { param($msg) Write-Host "[TEAM WARN] $msg" -ForegroundColor Yellow }
function Write-Err     { param($msg) Write-Host "[TEAM ERROR] $msg" -ForegroundColor Red }
function Write-Success { param($msg) Write-Host "[TEAM OK] $msg" -ForegroundColor Green }

# Load manifest
if (!(Test-Path $ManifestPath)) {
    Write-Err "Manifest not found: $ManifestPath"
    exit 1
}

$manifest = Get-Content $ManifestPath -Raw | ConvertFrom-Json

# Find team — supports both .teams (v2) and .agent_teams.teams (legacy)
$teams = $null
if ($manifest.teams) {
    $teams = $manifest.teams
} elseif ($manifest.agent_teams -and $manifest.agent_teams.teams) {
    $teams = $manifest.agent_teams.teams
}

$team = $null
if ($teams -and $teams.PSObject.Properties.Match($TeamName).Count -gt 0) {
    $team = $teams.$TeamName
}

if (!$team) {
    Write-Err "Team '$TeamName' not found in manifest"
    Write-Host ""
    Write-Host "Available teams:"
    if ($teams) { $teams.PSObject.Properties | ForEach-Object { Write-Host "  - $($_.Name) ($($_.Value.mode // $_.Value.execution) execution)" } }
    exit 1
}

Write-Info "Deploying team: $TeamName ($($team.mode) execution - $($team.agents.Count) agents)"
Write-Host ""

if ($team.mode -eq "parallel") {
    $jobs = @()
    foreach ($agent in $team.agents) {
        Write-Info "Starting agent $agent in background..."
        $job = Start-Job -ScriptBlock {
            param($DispatchPath, $AgentName, $PromptArg)
            & $DispatchPath $AgentName $PromptArg
        } -ArgumentList $DispatchScript, $agent, $Prompt

        $jobs += [PSCustomObject]@{ Agent = $agent; Job = $job }
    }

    Write-Info "Waiting for all parallel agents to complete..."
    $failures = 0
    foreach ($item in $jobs) {
        Wait-Job $item.Job | Out-Null
        $result = Receive-Job $item.Job
        if ($item.Job.State -ne 'Completed' -or $item.Job.HasMoreData -eq $true) {
             # Note: Start-Job error handling can be tricky, we check job state
             if ($item.Job.State -eq 'Failed') {
                 Write-Err "Agent $($item.Agent) failed"
                 $failures++
             } else {
                 Write-Success "Agent $($item.Agent) completed"
                 # Output the job stream if needed
                 $result | ForEach-Object { Write-Host $_ }
             }
        } else {
             Write-Success "Agent $($item.Agent) completed"
             $result | ForEach-Object { Write-Host $_ }
        }
        Remove-Job $item.Job
    }

    if ($failures -gt 0) {
        Write-Err "Team execution finished with $failures failures."
        exit 1
    }
}
elseif ($team.mode -eq "sequential") {
    foreach ($agent in $team.agents) {
        Write-Info "Starting agent $agent..."

        try {
            & $DispatchScript $agent $Prompt
        } catch {
            Write-Err "Agent $agent failed. Halting sequential team execution."
            exit 1
        }

        if ($LASTEXITCODE -ne 0 -and $null -ne $LASTEXITCODE) {
            Write-Err "Agent $agent failed with exit code $LASTEXITCODE. Halting sequential team execution."
            exit 1
        }

        Write-Success "Agent $agent completed successfully"
        Write-Host ""
    }
}
else {
    Write-Err "Unknown execution mode: $($team.mode)"
    exit 1
}

# Auto-Memory Hook
$AutoMemScript = Join-Path $ScriptDir "auto-memory.ps1"
if (Test-Path $AutoMemScript) {
    & $AutoMemScript -TeamName $TeamName -Prompt $Prompt
}

Write-Success "Team execution '$TeamName' completed successfully"
