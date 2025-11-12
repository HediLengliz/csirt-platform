# PowerShell script to showcase Docker implementation
# Usage: .\showcase.ps1

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "CSIRT Platform - Docker Showcase" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "1. Service Status:" -ForegroundColor Green
docker-compose ps
Write-Host ""

Write-Host "2. Container Resource Usage:" -ForegroundColor Green
docker stats --no-stream
Write-Host ""

Write-Host "3. Network Information:" -ForegroundColor Green
$networkInfo = docker network inspect projects_default 2>$null
if ($networkInfo) {
    Write-Host $networkInfo
} else {
    Write-Host "Network not found. Make sure services are running." -ForegroundColor Yellow
}
Write-Host ""

Write-Host "4. Volume Information:" -ForegroundColor Green
docker volume ls | Select-String "projects"
Write-Host ""

Write-Host "5. Database Health:" -ForegroundColor Green
docker-compose exec postgres pg_isready -U csirt_user 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ PostgreSQL is ready" -ForegroundColor Green
} else {
    Write-Host "✗ PostgreSQL is not ready" -ForegroundColor Red
}
Write-Host ""

Write-Host "6. Redis Health:" -ForegroundColor Green
$redisPing = docker-compose exec redis redis-cli ping 2>$null
if ($redisPing -eq "PONG") {
    Write-Host "✓ Redis is responding" -ForegroundColor Green
} else {
    Write-Host "✗ Redis is not responding" -ForegroundColor Red
}
Write-Host ""

Write-Host "7. API Health:" -ForegroundColor Green
try {
    $apiResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/ml/stats" -Method Get -TimeoutSec 5
    Write-Host "✓ API is responding" -ForegroundColor Green
    Write-Host "  Anomaly Detector: $($apiResponse.anomaly_detector_trained)" -ForegroundColor White
    Write-Host "  Events in Window: $($apiResponse.events_in_window)" -ForegroundColor White
    Write-Host "  Patterns Loaded: $($apiResponse.patterns_loaded)" -ForegroundColor White
} catch {
    Write-Host "✗ API is not responding" -ForegroundColor Red
    Write-Host "  Error: $_" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "8. Recent API Logs:" -ForegroundColor Green
docker-compose logs --tail=5 api
Write-Host ""

Write-Host "9. Service URLs:" -ForegroundColor Green
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "  ML Stats: http://localhost:3000/ml" -ForegroundColor Cyan
Write-Host ""

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Showcase Complete!" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

