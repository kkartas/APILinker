# Safe commit script that fixes formatting before committing
# Usage: .\scripts\commit_safe.ps1 "Your commit message"

param(
    [Parameter(Mandatory=$true)]
    [string]$Message
)

Write-Host "Preparing for commit..." -ForegroundColor Cyan

# Get all staged files
$stagedFiles = git diff --cached --name-only

if (-not $stagedFiles) {
    Write-Host "No files staged for commit." -ForegroundColor Red
    exit 1
}

Write-Host "Staged files: $($stagedFiles -join ', ')" -ForegroundColor Yellow

# Fix formatting in staged files (markdown, yaml, json, etc.)
$textFiles = $stagedFiles | Where-Object { $_ -match '\.(md|yaml|yml|json|py|sh|ps1)$' }
if ($textFiles) {
    Write-Host "Fixing formatting in: $($textFiles -join ', ')" -ForegroundColor Cyan
    python scripts/fix_formatting_robust.py $textFiles

    if ($LASTEXITCODE -eq 0) {
        # Re-stage the fixed files
        git add $textFiles
        Write-Host "Files fixed and re-staged." -ForegroundColor Green
    } else {
        Write-Host "Error fixing files." -ForegroundColor Red
        exit 1
    }
}

# Check for unstaged changes that might conflict
$unstagedFiles = git diff --name-only
if ($unstagedFiles) {
    Write-Host "Warning: You have unstaged changes in: $($unstagedFiles -join ', ')" -ForegroundColor Yellow
    Write-Host "These may cause pre-commit hook conflicts." -ForegroundColor Yellow
    Write-Host "Consider staging all changes: git add ." -ForegroundColor Yellow
    $response = Read-Host "Continue anyway? (y/n)"
    if ($response -ne 'y') {
        Write-Host "Commit cancelled." -ForegroundColor Yellow
        exit 0
    }
}

# Commit
Write-Host "Committing..." -ForegroundColor Cyan
git commit -m $Message

if ($LASTEXITCODE -eq 0) {
    Write-Host "Commit successful!" -ForegroundColor Green
} else {
    Write-Host "Commit failed. Check the errors above." -ForegroundColor Red
    exit 1
}
