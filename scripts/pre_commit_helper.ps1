# Pre-commit helper script for Windows PowerShell
# Run this before committing to fix formatting issues

Write-Host "Running formatting fixes..." -ForegroundColor Cyan

# Fix formatting in common files
python scripts/fix_formatting.py ROADMAP.md README.md CHANGELOG.md

if ($LASTEXITCODE -eq 0) {
    Write-Host "Formatting fixes complete!" -ForegroundColor Green
    Write-Host "You can now commit your changes." -ForegroundColor Green
} else {
    Write-Host "Error running formatting fixes." -ForegroundColor Red
    exit 1
}
