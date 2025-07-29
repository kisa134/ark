#!/usr/bin/env python3
"""
ARK v2.8 - Запуск приложений
Выберите режим работы с агентом
"""

import sys
import os
from pathlib import Path

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

def print_banner():
    """Вывод баннера"""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                           ARK v2.8 - Когнитивный ИИ-агент                    ║
║                                                                              ║
║  🧠 Когнитивная архитектура    🎯 Система внимания    💾 Рабочая память     ║
║  😊 Эмоциональная система      🔧 Инструменты         🚀 Эволюция           ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)

def show_menu():
    """Показать меню выбора"""
    menu = """
📋 ВЫБЕРИТЕ РЕЖИМ РАБОТЫ:

1. 🖥️  GUI приложение (десктопное)
   - Графический интерфейс
   - Вкладки: чат, мониторинг, система, эволюция
   - Визуальное отображение состояния

2. 💻 Консольное приложение
   - Текстовый интерфейс
   - Команды и чат
   - Подробные логи

3. 🚀 Простое консольное приложение
   - Упрощенная версия
   - Быстрый запуск
   - Без сложных зависимостей

4. 🔧 Тестирование компонентов
   - Проверка когнитивной архитектуры
   - Тест LLM интеграции
   - Диагностика системы

5. 📊 Мониторинг системы
   - Системная информация
   - Логи агента
   - Статус компонентов

6. 🚀 Эволюция агента
   - Планирование эволюции
   - Автоматические улучшения
   - Отчеты о развитии

0. ❌ Выход

Введите номер (0-6): """
    
    return input(menu).strip()

def run_gui_app():
    """Запуск GUI приложения"""
    print("🖥️ Запуск GUI приложения...")
    try:
        from scripts.ark_desktop_app import main
        main()
    except Exception as e:
        print(f"❌ Ошибка запуска GUI: {e}")
        print("💡 Убедитесь, что установлен tkinter: sudo apt install python3-tk")

def run_console_app():
    """Запуск консольного приложения"""
    print("💻 Запуск консольного приложения...")
    try:
        from scripts.ark_console_app import main
        main()
    except Exception as e:
        print(f"❌ Ошибка запуска консоли: {e}")

def run_simple_console_app():
    """Запуск простого консольного приложения"""
    print("🚀 Запуск простого консольного приложения...")
    try:
        from scripts.ark_simple_console import main
        main()
    except Exception as e:
        print(f"❌ Ошибка запуска простого консоли: {e}")

def run_tests():
    """Запуск тестов"""
    print("🔧 Запуск тестов компонентов...")
    try:
        import subprocess
        result = subprocess.run([sys.executable, "scripts/test_cognitive_brain.py"], 
                              capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Ошибки:", result.stderr)
    except Exception as e:
        print(f"❌ Ошибка запуска тестов: {e}")

def run_monitoring():
    """Запуск мониторинга"""
    print("📊 Запуск мониторинга системы...")
    try:
        import subprocess
        result = subprocess.run([sys.executable, "scripts/ark_evolution_monitor.py"], 
                              capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Ошибки:", result.stderr)
    except Exception as e:
        print(f"❌ Ошибка запуска мониторинга: {e}")

def run_evolution():
    """Запуск эволюции"""
    print("🚀 Запуск эволюции агента...")
    try:
        import subprocess
        result = subprocess.run([sys.executable, "scripts/ark_self_evolution.py"], 
                              capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Ошибки:", result.stderr)
    except Exception as e:
        print(f"❌ Ошибка запуска эволюции: {e}")

def main():
    """Главная функция"""
    print_banner()
    
    while True:
        choice = show_menu()
        
        if choice == "0":
            print("👋 До свидания!")
            break
        elif choice == "1":
            run_gui_app()
        elif choice == "2":
            run_console_app()
        elif choice == "3":
            run_simple_console_app()
        elif choice == "4":
            run_tests()
        elif choice == "5":
            run_monitoring()
        elif choice == "6":
            run_evolution()
        else:
            print("❌ Неверный выбор. Попробуйте снова.")
        
        input("\nНажмите Enter для продолжения...")

if __name__ == "__main__":
    main() 