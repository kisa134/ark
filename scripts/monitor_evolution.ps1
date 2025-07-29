# Скрипт мониторинга эволюции "Ковчега"
# Показывает ключевые метрики и события

Write-Host "=== МОНИТОРИНГ ЭВОЛЮЦИИ 'КОВЧЕГА' ===" -ForegroundColor Cyan

while ($true) {
    Clear-Host
    Write-Host "=== МОНИТОРИНГ ЭВОЛЮЦИИ 'КОВЧЕГА' ===" -ForegroundColor Cyan
    Write-Host "Время: $(Get-Date)" -ForegroundColor Gray
    
    # Проверка статуса контейнера
    $container_status = docker ps --filter "name=ark_sanctuary" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    Write-Host "`n📦 Статус контейнера:" -ForegroundColor Blue
    Write-Host $container_status -ForegroundColor White
    
    # Последние логи
    Write-Host "`n📝 Последние события (последние 5 записей):" -ForegroundColor Blue
    $recent_logs = docker-compose logs --tail=5 ark
    Write-Host $recent_logs -ForegroundColor White
    
    # Проверка файлов логов
    if (Test-Path "logs/ark.log") {
        $log_size = (Get-Item "logs/ark.log").Length
        Write-Host "`n📊 Размер лог-файла: $([math]::Round($log_size/1MB, 2)) MB" -ForegroundColor Green
    }
    
    # Проверка изменений в коде
    $git_status = git status --porcelain 2>$null
    if ($git_status) {
        Write-Host "`n🔄 Обнаружены изменения в коде:" -ForegroundColor Yellow
        Write-Host $git_status -ForegroundColor White
    } else {
        Write-Host "`n✅ Код не изменялся" -ForegroundColor Green
    }
    
    Write-Host "`n⏰ Обновление через 30 секунд... (Ctrl+C для выхода)" -ForegroundColor Gray
    Start-Sleep 30
} 