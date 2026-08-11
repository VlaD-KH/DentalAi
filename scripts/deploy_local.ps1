# DentalAi Local Deployment Script (PowerShell)
# Запуск полного стека Docker Compose (PostgreSQL, FastMCP Backend, Next.js Frontend)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " DentalAi — Autonomous CAD/CAM Solo Lab OS Deployment" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$ScriptDir = Split-Path -Path $MyInvocation.MyCommand.Definition -Parent
Set-Location "$ScriptDir\.."

# 1. Проверка установки Docker
if (-not (Get-Command "docker" -ErrorAction SilentlyContinue)) {
    Write-Error "Docker не обнаружен! Пожалуйста, установите Docker Desktop."
    exit 1
}

# 2. Сборка и запуск контейнеров Docker Compose
Write-Host "[1/3] Запуск сервисов PostgreSQL, Backend FastAPI & Frontend Next.js..." -ForegroundColor Yellow
docker-compose up -d --build

# 3. Применение миграций БД Prisma
Write-Host "[2/3] Применение миграций базы данных Prisma PostgreSQL..." -ForegroundColor Yellow
docker-compose exec -T backend npx prisma db push --schema=app/db/schema.prisma

# 4. Прогон тестового набора pytest
Write-Host "[3/3] Запуск автоматических интеграционных тестов..." -ForegroundColor Yellow
$env:PYTHONPATH="."
python -m pytest backend/tests/

Write-Host "==========================================================" -ForegroundColor Green
Write-Host " DentalAi успешно развернут и готов к автономной работе!" -ForegroundColor Green
Write-Host "  — REST API & FastMCP Backend: http://localhost:8000" -ForegroundColor Green
Write-Host "  — Dashboard UI:               http://localhost:3000" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
