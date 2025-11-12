# PowerShell script to push CSIRT Platform to GitHub
# Usage: .\push_to_github.ps1

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "CSIRT Platform - GitHub Push Script" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if remote already exists
$remoteExists = git remote get-url origin 2>$null
if ($remoteExists) {
    Write-Host "Remote 'origin' already exists: $remoteExists" -ForegroundColor Yellow
    $overwrite = Read-Host "Do you want to overwrite it? (y/n)"
    if ($overwrite -eq "y" -or $overwrite -eq "Y") {
        git remote remove origin
    } else {
        Write-Host "Aborted." -ForegroundColor Red
        exit
    }
}

Write-Host ""
Write-Host "Step 1: Create a new repository on GitHub" -ForegroundColor Green
Write-Host "  1. Go to: https://github.com/new" -ForegroundColor White
Write-Host "  2. Repository name: csirt-platform" -ForegroundColor White
Write-Host "  3. Description: Enterprise-grade Security Incident Response Team Platform with Real-time ML/AI Detection" -ForegroundColor White
Write-Host "  4. Choose Public or Private" -ForegroundColor White
Write-Host "  5. DO NOT initialize with README, .gitignore, or license" -ForegroundColor Yellow
Write-Host "  6. Click 'Create repository'" -ForegroundColor White
Write-Host ""

$continue = Read-Host "Have you created the repository on GitHub? (y/n)"
if ($continue -ne "y" -and $continue -ne "Y") {
    Write-Host "Please create the repository first, then run this script again." -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "Step 2: Adding remote and pushing to GitHub" -ForegroundColor Green

# Get repository name
$repoName = Read-Host "Enter repository name (default: csirt-platform)"
if ([string]::IsNullOrWhiteSpace($repoName)) {
    $repoName = "csirt-platform"
}

$githubUser = Read-Host "Enter your GitHub username (default: HediLengliz)"
if ([string]::IsNullOrWhiteSpace($githubUser)) {
    $githubUser = "HediLengliz"
}

$remoteUrl = "https://github.com/$githubUser/$repoName.git"
Write-Host ""
Write-Host "Adding remote: $remoteUrl" -ForegroundColor Cyan
git remote add origin $remoteUrl

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Remote added successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to add remote" -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "Pushing to master branch..." -ForegroundColor Cyan
git push -u origin master

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "✓ Successfully pushed to GitHub!" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Repository URL: $remoteUrl" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Visit your repository: $remoteUrl" -ForegroundColor White
    Write-Host "  2. Verify all files are uploaded" -ForegroundColor White
    Write-Host "  3. Check that README.md displays correctly" -ForegroundColor White
    Write-Host "  4. Add repository topics: security, incident-response, siem, soar, machine-learning" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Red
    Write-Host "✗ Failed to push to GitHub" -ForegroundColor Red
    Write-Host "==========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Possible issues:" -ForegroundColor Yellow
    Write-Host "  - Repository doesn't exist on GitHub" -ForegroundColor White
    Write-Host "  - Authentication required (use GitHub CLI or Personal Access Token)" -ForegroundColor White
    Write-Host "  - Wrong repository name or username" -ForegroundColor White
    Write-Host ""
    Write-Host "To authenticate:" -ForegroundColor Yellow
    Write-Host "  - Install GitHub CLI: winget install GitHub.cli" -ForegroundColor White
    Write-Host "  - Run: gh auth login" -ForegroundColor White
    Write-Host "  - Or use Personal Access Token in URL" -ForegroundColor White
}

