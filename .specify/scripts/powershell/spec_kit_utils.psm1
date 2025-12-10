# .specify\scripts\powershell\spec_kit_utils.psm1

function Write-Log {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$Message,
        [string]$Level = "INFO" # INFO, WARN, ERROR
    )
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    Write-Output $logEntry # For console output

    # Optionally, write to a log file
    # $logFile = ".\spec_kit.log"
    # Add-Content -Path $logFile -Value $logEntry
}

function Get-FeatureDir {
    [CmdletBinding()]
    param()
    $currentBranch = (git rev-parse --abbrev-ref HEAD).Trim()
    if ($currentBranch -match '^\d{3}-(.+)$') {
        $featureName = $matches[0]
        return "specs/$featureName"
    } else {
        Write-Error "Could not determine feature directory from branch name '$currentBranch'."
        return $null
    }
}

function Test-SpecExists {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$FeatureDir
    )
    $specPath = Join-Path $FeatureDir "spec.md"
    if (Test-Path $specPath -PathType Leaf) {
        Write-Verbose "spec.md exists at $specPath"
        return $true
    } else {
        Write-Error "spec.md not found at $specPath"
        return $false
    }
}

function Test-PlanExists {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$FeatureDir
    )
    $planPath = Join-Path $FeatureDir "plan.md"
    if (Test-Path $planPath -PathType Leaf) {
        Write-Verbose "plan.md exists at $planPath"
        return $true
    } else {
        Write-Error "plan.md not found at $planPath"
        return $false
    }
}

function Test-TasksExists {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$FeatureDir
    )
    $tasksPath = Join-Path $FeatureDir "tasks.md"
    if (Test-Path $tasksPath -PathType Leaf) {
        Write-Verbose "tasks.md exists at $tasksPath"
        return $true
    } else {
        Write-Error "tasks.md not found at $tasksPath"
        return $false
    }
}

function Get-Constitution {
    [CmdletBinding()]
    param()
    $constitutionPath = ".specify/memory/constitution.md"
    if (Test-Path $constitutionPath -PathType Leaf) {
        Write-Verbose "Loading constitution from $constitutionPath"
        return (Get-Content $constitutionPath -Raw)
    } else {
        Write-Error "Constitution not found at $constitutionPath"
        return $null
    }
}

function Validate-ArtifactAgainstConstitution {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$ArtifactPath,
        [Parameter(Mandatory=$true)]
        [string]$ConstitutionContent # Pass raw content to avoid re-reading
    )
    # This is a placeholder for actual validation logic.
    # For now, it will simply return true, but in a real scenario,
    # it would parse the constitution and the artifact and apply rules.
    # For this task, we assume the artifact (like spec.md) would be checked
    # for adherence to principles (e.g., existence of measurable SCs,
    # absence of implementation details, etc.).

    Write-Verbose "Simulating validation of $ArtifactPath against constitution."

    # Example of a simple check: does the artifact path end with .md?
    # This is just for demonstration, real validation is complex.
    if ($ArtifactPath.EndsWith(".md")) {
        Write-Verbose "$ArtifactPath is a Markdown file, passing simulated validation."
        return $true
    } else {
        Write-Warning "$ArtifactPath is not a Markdown file, failing simulated validation."
        return $false
    }
}

Export-ModuleMember -Function Write-Log, Test-SpecExists, Test-PlanExists, Test-TasksExists, Get-Constitution, Validate-ArtifactAgainstConstitution, Get-FeatureDir
