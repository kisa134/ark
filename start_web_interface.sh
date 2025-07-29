#!/bin/bash

# ARK Web Interface Launcher
# Быстрый запуск веб-интерфейса ARK v2.8

echo "🚀 Запуск веб-интерфейса ARK v2.8..."

# Проверяем, что мы в правильной директории
if [ ! -f "main.py" ]; then
    echo "❌ Ошибка: Запустите скрипт из корневой директории проекта ARK"
    exit 1
fi

# Активируем виртуальное окружение
if [ -d "venv" ]; then
    echo "📦 Активация виртуального окружения..."
    source venv/bin/activate
else
    echo "❌ Ошибка: Виртуальное окружение не найдено. Создайте его командой:"
    echo "python3 -m venv venv"
    exit 1
fi

# Проверяем, что порт 8000 свободен
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Порт 8000 уже занят. Останавливаем существующий процесс..."
    pkill -f "python3 web/chat_server.py"
    sleep 2
fi

# Создаем необходимые директории
echo "📁 Создание необходимых директорий..."
mkdir -p logs data models temp

# Запускаем веб-сервер
echo "🌐 Запуск веб-сервера на http://localhost:8000..."
echo "📊 Статус: http://localhost:8000/api/status"
echo "💬 Чат: http://localhost:8000"
echo ""
echo "Для остановки нажмите Ctrl+C"
echo ""

# Запускаем сервер
python3 web/chat_server.py 