#!/bin/bash

# ARK Project Cleanup Script
# Удаляет неиспользуемые файлы и оптимизирует проект

set -e

echo "🧹 Очистка проекта ARK..."

# Создание резервной копии
echo "📦 Создание резервной копии..."
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Резервное копирование важных файлов
cp -r OpenRGB/ "$BACKUP_DIR/" 2>/dev/null || true
cp requirements_minimal.txt "$BACKUP_DIR/" 2>/dev/null || true
cp requirements_fixed.txt "$BACKUP_DIR/" 2>/dev/null || true
cp ARK_v2.8_*.md "$BACKUP_DIR/" 2>/dev/null || true

echo "✅ Резервная копия создана: $BACKUP_DIR"

# Удаление неиспользуемых файлов
echo "🗑️ Удаление неиспользуемых файлов..."

# Удаление OpenRGB директории (C++ код)
if [ -d "OpenRGB" ]; then
    echo "  - Удаление OpenRGB/ (C++ код)"
    rm -rf OpenRGB/
fi

# Удаление дублирующих requirements файлов
if [ -f "requirements_minimal.txt" ]; then
    echo "  - Удаление requirements_minimal.txt"
    rm requirements_minimal.txt
fi

if [ -f "requirements_fixed.txt" ]; then
    echo "  - Удаление requirements_fixed.txt"
    rm requirements_fixed.txt
fi

# Удаление старых отчетов
for file in ARK_v2.8_*.md; do
    if [ -f "$file" ]; then
        echo "  - Удаление $file"
        rm "$file"
    fi
done

# Очистка кэша Python
echo "🐍 Очистка Python кэша..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true

# Очистка временных файлов
echo "🗂️ Очистка временных файлов..."
rm -rf temp/* 2>/dev/null || true
rm -rf logs/*.log 2>/dev/null || true

# Создание .gitignore если не существует
if [ ! -f ".gitignore" ]; then
    echo "📝 Создание .gitignore..."
    cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
logs/*.log
*.log

# Data
data/*.json
data/*.db

# Temporary files
temp/
*.tmp

# Environment variables
.env
secrets.env

# Backup
backup_*/
EOF
fi

# Проверка размера проекта
echo "📊 Анализ размера проекта..."
PROJECT_SIZE=$(du -sh . | cut -f1)
echo "  Размер проекта: $PROJECT_SIZE"

# Подсчет файлов
PYTHON_FILES=$(find . -name "*.py" | wc -l)
TOTAL_FILES=$(find . -type f | wc -l)
echo "  Python файлов: $PYTHON_FILES"
echo "  Всего файлов: $TOTAL_FILES"

# Проверка зависимостей
echo "📦 Проверка зависимостей..."
if [ -f "requirements.txt" ]; then
    DEPENDENCIES=$(wc -l < requirements.txt)
    echo "  Зависимостей в requirements.txt: $DEPENDENCIES"
else
    echo "  ❌ requirements.txt не найден"
fi

echo ""
echo "✅ Очистка завершена!"
echo ""
echo "📋 Что было удалено:"
echo "  - OpenRGB/ (C++ код)"
echo "  - requirements_minimal.txt"
echo "  - requirements_fixed.txt"
echo "  - ARK_v2.8_*.md (старые отчеты)"
echo "  - Python кэш"
echo "  - Временные файлы"
echo ""
echo "💾 Резервная копия сохранена в: $BACKUP_DIR"
echo "📁 Размер проекта после очистки: $PROJECT_SIZE"
echo ""
echo "🚀 Проект готов к дальнейшей разработке!" 