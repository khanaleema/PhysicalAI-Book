# .specify\scripts\powershell\analyze_artifacts.ps1

[CmdletBinding()]
param(
    [switch]$Json # For potential future structured output
)

$ErrorActionPreference = 'Stop'

# Load SpecKit Utilities
Import-Module (Join-Path $PSScriptRoot "spec_kit_utils.psm1") -ErrorAction Stop

try {
    $featureDir = Get-FeatureDir
    if (-not $featureDir) {
        Write-Error "Could not determine feature directory. Aborting analysis."
        exit 1
    }

    $specPath = Join-Path $featureDir "spec.md"
    $planPath = Join-Path $featureDir "plan.md"
    $tasksPath = Join-Path $featureDir "tasks.md"

    # Ensure all required artifacts exist for analysis
    if (-not (Test-Path $specPath -PathType Leaf)) {
        Write-Error "spec.md not found at $specPath. Cannot perform analysis."
        exit 1
    }
    if (-not (Test-Path $planPath -PathType Leaf)) {
        Write-Error "plan.md not found at $planPath. Cannot perform analysis."
        exit 1
    }
    if (-not (Test-Path $tasksPath -PathType Leaf)) {
        Write-Error "tasks.md not found at $tasksPath. Cannot perform analysis."
        exit 1
    }

    $constitutionContent = Get-Constitution
    if (-not $constitutionContent) {
        Write-Error "Constitution not loaded. Cannot perform constitutional validation."
        exit 1
    }

    Write-Host "--- Artifact Analysis Report ---"
    Write-Host "Feature Directory: $featureDir"
    Write-Host "Analyzing spec.md: $specPath"
    Write-Host "Analyzing plan.md: $planPath"
    Write-Host "Analyzing tasks.md: $tasksPath"
    Write-Host ""

    $issues = @()

    # T023: Implement detection of vague success criteria in spec.md
    Write-Host "--> Checking spec.md for vague success criteria..."
    $specContent = Get-Content $specPath -Raw
    $vagueTerms = @("fast", "scalable", "robust", "intuitive", "efficient", "good", "performant")
    foreach ($term in $vagueTerms) {
        if ($specContent -match "(?i)\b$term\b") { # Case-insensitive word match
            $issues += [PSCustomObject]@{
                ID = "SQA001"
                Category = "Ambiguity"
                Severity = "HIGH"
                Location = "spec.md"
                Summary = "Vague term `'$term'` found in spec. Success criteria should be measurable."
                Recommendation = "Quantify or remove vague terms. Ensure SCs are measurable."
            }
        }
    }
    if ($issues.Count -eq 0) { Write-Host "  No obvious vague terms found in spec.md." }
    Write-Host ""

    # T024: Implement detection of constitutional principle violations in plan.md
    Write-Host "--> Checking plan.md for constitutional principle violations (simulated)..."
    # This is a simulation. Real implementation would parse plan.md and constitution.md
    # and compare the technical context/decisions against the 'Rule' sections of principles.
    # For now, we'll use our existing placeholder validation.
    if (-not (Validate-ArtifactAgainstConstitution -ArtifactPath $planPath -ConstitutionContent $constitutionContent)) {
        $issues += [PSCustomObject]@{
            ID = "CVA001"
            Category = "Constitution Violation"
            Severity = "CRITICAL"
            Location = "plan.md"
            Summary = "Plan.md fails constitutional validation (simulated)."
            Recommendation = "Review plan.md and constitution.md to resolve violations."
        }
    } else {
        Write-Host "  Plan.md passed simulated constitutional validation."
    }
    Write-Host ""

    # T025: Generate a structured markdown analysis report
    $reportPath = Join-Path $featureDir "analysis_report.md"
    Write-Host "Generating analysis report at $reportPath..."

    $reportContent = "# Analysis Report for '$featureDir'\n\n"
    $reportContent += "Generated on: $(Get-Date)\n\n"
    $reportContent += "## Findings\n\n"

    if ($issues.Count -gt 0) {
        $reportContent += "| ID | Category | Severity | Location(s) | Summary | Recommendation |\n"
        $reportContent += "|----|----------|----------|-------------|---------|----------------|\n"
        foreach ($issue in $issues) {
            $reportContent += "| $($issue.ID) | $($issue.Category) | $($issue.Severity) | $($issue.Location) | $($issue.Summary) | $($issue.Recommendation) |\n"
        }
    } else {
        $reportContent += "No critical issues found. All artifacts passed analysis checks.\n"
    }
    $reportContent += "\n## Metrics\n\n"
    $reportContent += "- Total Issues Found: $($issues.Count)\n"
    $reportContent += "- Critical Issues: $($issues | Where-Object { $_.Severity -eq 'CRITICAL' } | Measure-Object).Count\n"
    $reportContent += "- High Issues: $($issues | Where-Object { $_.Severity -eq 'HIGH' } | Measure-Object).Count\n"
    $reportContent += "\n## Next Steps\n\n"
    if ($issues.Count -gt 0) {
        $reportContent += "- Review the findings above and address reported issues in the respective artifact files.\n"
        $reportContent += "- Re-run `/sp.analyze` to verify fixes.\n"
    } else {
        $reportContent += "- All good! Proceed to implementation or next phase.\n"
    }

    Set-Content -Path $reportPath -Value $reportContent
    Write-Host "Analysis report generated successfully."

} catch {
    Write-Error "An error occurred during artifact analysis: $($_.Exception.Message)"
    exit 1
}

exit 0
