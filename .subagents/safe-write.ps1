<#
.SYNOPSIS
    Safe Write Output Governance Hook
.DESCRIPTION
    Validates output paths against docs/standards/output_governance.md rules
    and automatically creates missing directories (mkdir -p equivalent).
.PARAMETER TargetPath
    The file path requested to be written
#>

param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$TargetPath
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$WorkspaceRoot = Split-Path -Parent $ScriptDir

# Resolve relative paths
if (![System.IO.Path]::IsPathRooted($TargetPath)) {
    $TargetPath = Join-Path $WorkspaceRoot $TargetPath
}

$AllowedZones = @(
    (Join-Path $WorkspaceRoot "docs\audit"),
    (Join-Path $WorkspaceRoot "docs\plans"),
    (Join-Path $WorkspaceRoot "docs\research"),
    (Join-Path $WorkspaceRoot "docs\decisions"),
    (Join-Path $WorkspaceRoot "scripts\temp"),
    (Join-Path $WorkspaceRoot ".subagents\skills"),
    (Join-Path $WorkspaceRoot ".agent\workflows")
)

$RootExceptions = @("GEMINI.md", "CLAUDE.md", "AGENTS.md", "CHANGELOG.md", "README.md", "DEVLOG.md", "TASKS.md")
$BaseName = Split-Path -Leaf $TargetPath
$ParentDir = Split-Path -Parent $TargetPath

$IsAllowed = $false

# Check root exceptions
if ($RootExceptions -contains $BaseName) {
    if ($ParentDir -eq $WorkspaceRoot -or $ParentDir -eq (Join-Path $WorkspaceRoot "docs")) {
        $IsAllowed = $true
    }
}

# Check allowed output zones
if (!$IsAllowed) {
    foreach ($zone in $AllowedZones) {
        if ($TargetPath.StartsWith($zone, [StringComparison]::InvariantCultureIgnoreCase)) {
            $IsAllowed = $true
            break
        }
    }
}

# Source code is inherently allowed
if (!$IsAllowed -and ($TargetPath.StartsWith((Join-Path $WorkspaceRoot "src"), [StringComparison]::InvariantCultureIgnoreCase) -or $TargetPath.StartsWith((Join-Path $WorkspaceRoot "tests"), [StringComparison]::InvariantCultureIgnoreCase))) {
    $IsAllowed = $true
}

if (!$IsAllowed) {
    Write-Host "[GOVERNANCE ERROR] Cannot auto-create file: $TargetPath" -ForegroundColor Red
    Write-Host "Path violates Output Governance (Rule: Missing allowed zone docs/audit, docs/plans, etc.)." -ForegroundColor Yellow
    exit 1
}

# Mkdir -p logic
if (!(Test-Path $ParentDir)) {
    New-Item -ItemType Directory -Path $ParentDir -Force | Out-Null
    Write-Host "[GOVERNANCE PASS] Auto-created directory tree: $ParentDir" -ForegroundColor Green
}

# Create dummy file if missing
if (!(Test-Path $TargetPath)) {
    New-Item -ItemType File -Path $TargetPath -Force | Out-Null
    Write-Host "[GOVERNANCE PASS] Secured and created file pointer -> $TargetPath" -ForegroundColor Green
} else {
    Write-Host "[GOVERNANCE WARN] Target file already exists, skipping creation -> $TargetPath" -ForegroundColor Yellow
}

exit 0
