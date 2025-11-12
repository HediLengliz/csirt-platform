# GitHub Actions Workflows

This directory contains CI/CD workflows for the CSIRT Platform.

## Workflows

### 1. CI Pipeline (`ci.yml`)
Main continuous integration pipeline that runs on every push and pull request.

**Jobs:**
- **Backend Tests**: Runs Python tests with PostgreSQL and Redis services
- **Frontend Tests**: Builds and tests the React frontend
- **Docker Build**: Builds Docker images to verify they compile correctly
- **Security Scan**: Scans for vulnerabilities using Trivy
- **Code Quality**: Runs SonarCloud analysis (if configured)

**Triggers:**
- Push to `master`, `main`, or `develop` branches
- Pull requests to `master`, `main`, or `develop` branches

### 2. Docker Build and Publish (`docker-publish.yml`)
Builds and publishes Docker images to GitHub Container Registry.

**Features:**
- Builds both API and Frontend images
- Pushes to `ghcr.io` (GitHub Container Registry)
- Tags images with branch names, SHA, and semantic versions
- Uses build cache for faster builds

**Triggers:**
- Push to `master` or `main` branches
- Push of version tags (e.g., `v1.0.0`)
- Manual workflow dispatch

### 3. Lint and Format Check (`lint.yml`)
Checks code quality and formatting.

**Checks:**
- **Backend**: Black, isort, Flake8, Pylint
- **Frontend**: ESLint, TypeScript type checking

**Triggers:**
- Push to `master`, `main`, or `develop` branches
- Pull requests to `master`, `main`, or `develop` branches

### 4. Release (`release.yml`)
Creates GitHub releases with changelog and Docker image tags.

**Features:**
- Automatically creates release from version tags
- Generates changelog from git commits
- Includes Docker image information

**Triggers:**
- Push of version tags (e.g., `v1.0.0`)
- Manual workflow dispatch with version input

### 5. Docker Compose Integration Test (`docker-compose-test.yml`)
Tests the complete Docker Compose setup.

**Tests:**
- Validates `docker-compose.yml`
- Builds all images
- Starts all services
- Checks service health
- Tests API endpoints
- Verifies frontend accessibility

**Triggers:**
- Push to `master`, `main`, or `develop` branches
- Pull requests to `master`, `main`, or `develop` branches
- Manual workflow dispatch

## Dependabot (`dependabot.yml`)
Automatically creates pull requests for dependency updates.

**Monitors:**
- Python dependencies (`requirements.txt`)
- Node.js dependencies (`frontend/package.json`)
- Docker base images
- GitHub Actions

## Secrets Required

Some workflows may require secrets to be configured in GitHub repository settings:

- `SONAR_TOKEN`: SonarCloud token (optional, for code quality)
- `GITHUB_TOKEN`: Automatically provided by GitHub Actions

## Usage

### Running Workflows Manually

1. Go to **Actions** tab in GitHub
2. Select the workflow you want to run
3. Click **Run workflow**
4. Select branch and click **Run workflow**

### Viewing Results

1. Go to **Actions** tab
2. Click on a workflow run to see details
3. Expand job steps to see logs

### Fixing Failures

1. Check the failed job logs
2. Fix the issue locally
3. Commit and push changes
4. Workflow will automatically re-run

## Local Testing

You can test workflows locally using [act](https://github.com/nektos/act):

```bash
# Install act
# Windows: choco install act-cli
# macOS: brew install act
# Linux: See act documentation

# Run CI workflow locally
act push

# Run specific job
act -j backend-tests
```

## Workflow Status Badges

Add these badges to your README.md:

```markdown
![CI Pipeline](https://github.com/USERNAME/REPO/workflows/CI%20Pipeline/badge.svg)
![Docker Build](https://github.com/USERNAME/REPO/workflows/Docker%20Build%20and%20Publish/badge.svg)
![Lint](https://github.com/USERNAME/REPO/workflows/Lint%20and%20Format%20Check/badge.svg)
```

## Best Practices

1. **Always check workflow status** before merging PRs
2. **Fix linting issues** before pushing
3. **Test Docker builds locally** before pushing
4. **Use semantic versioning** for releases
5. **Review security scan results** regularly

