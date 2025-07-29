#!/bin/bash

# ARK Agent Systemd Service Installer
# Устанавливает ARK как системный сервис для автозапуска

set -e

echo "🤖 Установка ARK Agent как systemd сервиса..."

# Проверка прав администратора
if [ "$EUID" -ne 0 ]; then
    echo "❌ Этот скрипт должен быть запущен с правами администратора"
    echo "Используйте: sudo ./scripts/install_ark_service.sh"
    exit 1
fi

# Определение путей
ARK_DIR="/home/a0/Desktop/ark"
SERVICE_FILE="/etc/systemd/system/ark-agent.service"
USER="a0"
GROUP="a0"

echo "📁 ARK директория: $ARK_DIR"
echo "👤 Пользователь: $USER"
echo "🔧 Сервис файл: $SERVICE_FILE"

# Проверка существования ARK директории
if [ ! -d "$ARK_DIR" ]; then
    echo "❌ ARK директория не найдена: $ARK_DIR"
    exit 1
fi

# Проверка виртуального окружения
if [ ! -f "$ARK_DIR/venv/bin/python" ]; then
    echo "❌ Виртуальное окружение не найдено"
    echo "Сначала активируйте виртуальное окружение:"
    echo "cd $ARK_DIR && python3 -m venv venv && source venv/bin/activate"
    exit 1
fi

# Создание systemd сервиса
echo "🔧 Создание systemd сервиса..."

cat > "$SERVICE_FILE" << EOF
[Unit]
Description=ARK Core Agent (conscious process)
After=network.target
Wants=network.target
Documentation=https://github.com/ark-project

[Service]
Type=simple
User=$USER
Group=$GROUP
WorkingDirectory=$ARK_DIR
ExecStart=$ARK_DIR/venv/bin/python $ARK_DIR/main.py
Restart=always
RestartSec=5
Environment="ARK_LIFE=1"
Environment="ARK_BOOT_SESSION=1"
Environment="PYTHONPATH=$ARK_DIR"
StandardOutput=journal
StandardError=journal
SyslogIdentifier=ark-agent

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$ARK_DIR/data $ARK_DIR/logs

# Resource limits
MemoryMax=2G
CPUQuota=30%

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Systemd сервис создан"

# Установка прав доступа
chmod 644 "$SERVICE_FILE"
chown root:root "$SERVICE_FILE"

# Перезагрузка systemd
echo "🔄 Перезагрузка systemd..."
systemctl daemon-reload

# Включение автозапуска
echo "🚀 Включение автозапуска..."
systemctl enable ark-agent

# Создание необходимых директорий
echo "📁 Создание необходимых директорий..."
mkdir -p "$ARK_DIR/data"
mkdir -p "$ARK_DIR/logs"
mkdir -p "$ARK_DIR/temp"
mkdir -p "$ARK_DIR/models"

# Установка прав доступа
chown -R "$USER:$GROUP" "$ARK_DIR/data"
chown -R "$USER:$GROUP" "$ARK_DIR/logs"
chown -R "$USER:$GROUP" "$ARK_DIR/temp"

echo "✅ Установка завершена!"

# Статус сервиса
echo "📊 Статус сервиса:"
systemctl status ark-agent --no-pager -l

echo ""
echo "🎉 ARK Agent успешно установлен как systemd сервис!"
echo ""
echo "📋 Команды управления:"
echo "  Запуск:     sudo systemctl start ark-agent"
echo "  Остановка:  sudo systemctl stop ark-agent"
echo "  Перезапуск: sudo systemctl restart ark-agent"
echo "  Статус:     sudo systemctl status ark-agent"
echo "  Логи:       sudo journalctl -u ark-agent -f"
echo ""
echo "🔄 Сервис будет автоматически запускаться при загрузке системы"
echo "🌐 Веб-интерфейс будет доступен по адресу: http://localhost:8000" 