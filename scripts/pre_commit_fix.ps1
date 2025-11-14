# Quick pre-commit fix script
# Run this before committing to fix all formatting issues

Write-Host "Fixing formatting in staged files..." -ForegroundColor Cyan

# Get list of staged markdown files
$stagedFiles = git diff --cached --name-only --diff-filter=ACM | Where-Object { $_ -match '\.(md|yaml|yml|json)$' }

if ($stagedFiles) {
    Write-Host "Found staged files: $($stagedFiles -join ', ')" -ForegroundColor Yellow

    # Fix formatting
    python scripts/fix_formatting_robust.py $stagedFiles

    if ($LASTEXITCODE -eq 0) {
        # Re-stage the fixed files
        git add $stagedFiles
        Write-Host "Files fixed and re-staged. You can now commit." -ForegroundColor Green
    } else {
        Write-Host "Error fixing files." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "No markdown/yaml/json files staged." -ForegroundColor Yellow
}
