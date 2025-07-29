.PHONY: install run test lint clean build docker-build docker-run

# Переменные
PYTHON = python3
PIP = pip3
PROJECT_NAME = ark

# Установка зависимостей
install:
	@echo "Установка зависимостей проекта $(PROJECT_NAME)..."
	$(PIP) install -r requirements.txt
	@echo "Зависимости установлены успешно"

# Запуск основного приложения
run:
	@echo "Запуск $(PROJECT_NAME)..."
	$(PYTHON) main.py

# Запуск в режиме разработки
dev:
	@echo "Запуск $(PROJECT_NAME) в режиме разработки..."
	$(PYTHON) -m streamlit run main.py --server.port 8501

# Тестирование
test:
	@echo "Запуск тестов..."
	$(PYTHON) -m pytest tests/ -v --tb=short

# Проверка качества кода
lint:
	@echo "Проверка стиля кода..."
	black --check .
	flake8 . --max-line-length=88 --extend-ignore=E203,W503
	mypy . --ignore-missing-imports

# Автоматическое форматирование кода
format:
	@echo "Форматирование кода..."
	black .
	isort .

# Очистка временных файлов
clean:
	@echo "Очистка временных файлов..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf .mypy_cache

# Сборка Docker образа
docker-build:
	@echo "Сборка Docker образа..."
	docker build -t $(PROJECT_NAME):latest .

# Запуск в Docker
docker-run:
	@echo "Запуск в Docker..."
	docker run --rm -it \
		-v /var/log:/var/log \
		-v /proc:/host/proc:ro \
		-v /sys:/host/sys:ro \
		$(PROJECT_NAME):latest

# Инициализация Git репозитория
init-git:
	@echo "Инициализация Git репозитория..."
	git init -b main
	git add .
	git commit -m "feat(ark)!: GENESIS - Initial bootstrap of the Ark v1.3 architecture"

# Полная установка и настройка
setup: install init-git
	@echo "Проект $(PROJECT_NAME) успешно настроен!"

# Помощь
help:
	@echo "Доступные команды:"
	@echo "  install     - Установка зависимостей"
	@echo "  run         - Запуск основного приложения"
	@echo "  dev         - Запуск в режиме разработки"
	@echo "  test        - Запуск тестов"
	@echo "  lint        - Проверка качества кода"
	@echo "  format      - Автоматическое форматирование"
	@echo "  clean       - Очистка временных файлов"
	@echo "  docker-build- Сборка Docker образа"
	@echo "  docker-run  - Запуск в Docker"
	@echo "  init-git    - Инициализация Git"
	@echo "  setup       - Полная установка и настройка" 