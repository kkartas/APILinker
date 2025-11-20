# Version Bump Script for Windows
# Usage: .\bump.ps1 [patch|minor|major]

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('patch', 'minor', 'major')]
    [string]$Part
)

# Set UTF-8 encoding to avoid Unicode issues
$env:PYTHONIOENCODING = 'utf-8'

Write-Host "Bumping $Part version..." -ForegroundColor Cyan

# Run bump-my-version
& .\.venv\Scripts\bump-my-version bump $Part

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nVersion bumped successfully!" -ForegroundColor Green
    Write-Host "Remember to push with tags: git push origin main --tags" -ForegroundColor Yellow
} else {
    Write-Host "`nVersion bump failed!" -ForegroundColor Red
    exit 1
}
