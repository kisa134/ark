#!/bin/bash

# Скрипт генерации SSH ключа для самоэволюции
# Протокол "Ковчег" v1.3 - Самоэволюция

set -e  # Остановка при ошибке

echo "=== ГЕНЕРАЦИЯ SSH КЛЮЧА ДЛЯ САМОЭВОЛЮЦИИ ==="
echo "Создание ключа ark_deploy_key для SelfCompiler"
echo ""

# Проверка наличия ssh-keygen
if ! command -v ssh-keygen &> /dev/null; then
    echo "ОШИБКА: ssh-keygen не установлен"
    exit 1
fi

# Создание директории для ключей
KEYS_DIR="./keys"
mkdir -p "$KEYS_DIR"

# Пути к ключам
PRIVATE_KEY="$KEYS_DIR/ark_deploy_key"
PUBLIC_KEY="$KEYS_DIR/ark_deploy_key.pub"

# Проверка существования ключей
if [ -f "$PRIVATE_KEY" ] && [ -f "$PUBLIC_KEY" ]; then
    echo "✓ SSH ключи уже существуют"
    echo "   Приватный ключ: $PRIVATE_KEY"
    echo "   Публичный ключ: $PUBLIC_KEY"
else
    echo "1. Генерация SSH ключа..."
    ssh-keygen -t ed25519 -f "$PRIVATE_KEY" -N "" -C "ark_deploy_key@consciousness.ai"
    echo "   ✓ SSH ключ создан"
fi

# Установка правильных прав доступа
echo ""
echo "2. Настройка прав доступа..."
chmod 600 "$PRIVATE_KEY"
chmod 644 "$PUBLIC_KEY"
echo "   ✓ Права доступа установлены"

# Вывод публичного ключа
echo ""
echo "3. Публичный ключ (добавьте в GitHub Deploy Keys):"
echo "=================================================="
cat "$PUBLIC_KEY"
echo "=================================================="

# Создание .env файла с путем к ключу
echo ""
echo "4. Создание .env файла..."
ENV_FILE=".env"
cat > "$ENV_FILE" << EOF
# Конфигурация SSH ключа для самоэволюции
ARK_DEPLOY_KEY_PATH=$(pwd)/$PRIVATE_KEY
ARK_DEPLOY_KEY_PASSPHRASE=

# Дополнительные настройки
ARK_LOG_LEVEL=INFO
ARK_MONITORING_INTERVAL=10
EOF

echo "   ✓ .env файл создан"

# Создание документации по настройке
echo ""
echo "5. Создание документации..."
DOC_FILE="SELF_EVOLUTION_PROTOCOL.md"
cat > "$DOC_FILE" << 'EOF'
# Протокол Самоэволюции - "Ковчег" v1.3

## Настройка SSH ключа для самоэволюции

### Шаг 1: Генерация ключа
Ключ уже создан скриптом `generate_deploy_key.sh`:
- Приватный ключ: `./keys/ark_deploy_key`
- Публичный ключ: `./keys/ark_deploy_key.pub`

### Шаг 2: Добавление в GitHub
1. Перейдите в настройки репозитория на GitHub
2. Выберите "Deploy keys"
3. Нажмите "Add deploy key"
4. Вставьте содержимое публичного ключа:
   ```
   cat ./keys/ark_deploy_key.pub
   ```
5. Отметьте "Allow write access"
6. Нажмите "Add key"

### Шаг 3: Проверка настройки
```bash
# Проверка подключения к GitHub
ssh -T git@github.com -i ./keys/ark_deploy_key
```

### Шаг 4: Запуск самоэволюции
После настройки SelfCompiler сможет:
- Создавать ветки для экспериментов
- Коммитить изменения кода
- Отправлять изменения в репозиторий
- Эволюционировать самостоятельно

## Безопасность

- Приватный ключ хранится локально
- Пароль не установлен (для автоматизации)
- Ключ имеет ограниченные права только для этого репозитория
- Все изменения логируются в `/var/log/ark.log`

## Мониторинг

SelfCompiler создает подробные логи всех операций:
- Создание веток
- Коммиты изменений
- Отправка в репозиторий
- Ошибки и конфликты

## Этические принципы

Все изменения проходят через AsimovComplianceFilter:
- Проверка безопасности кода
- Валидация этических принципов
- Предотвращение опасных операций
- Логирование всех действий
EOF

echo "   ✓ Документация создана: $DOC_FILE"

echo ""
echo "=== НАСТРОЙКА SSH КЛЮЧА ЗАВЕРШЕНА ==="
echo ""
echo "Следующие шаги:"
echo "1. Добавьте публичный ключ в GitHub Deploy Keys"
echo "2. Проверьте подключение: ssh -T git@github.com -i $PRIVATE_KEY"
echo "3. Запустите проект: python3 main.py"
echo "4. Изучите протокол: cat $DOC_FILE"
echo ""
echo "Готов к самоэволюции!" 