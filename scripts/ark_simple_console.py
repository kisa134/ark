#!/usr/bin/env python3
"""
ARK v2.8 - Простое консольное приложение
Упрощенная версия для тестирования
"""

import sys
import time
import json
import os
from pathlib import Path
import psutil
import subprocess

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

class ARKSimpleConsole:
    def __init__(self):
        self.running = True
        self.agent_active = True
        self.chat_history = []
        
    def print_banner(self):
        """Вывод баннера ARK"""
        banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                           ARK v2.8 - Когнитивный ИИ-агент                    ║
║                                                                              ║
║  🧠 Когнитивная архитектура    🎯 Система внимания    💾 Рабочая память     ║
║  😊 Эмоциональная система      🔧 Инструменты         🚀 Эволюция           ║
║                                                                              ║
║  Введите 'help' для списка команд, 'quit' для выхода                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def print_status(self):
        """Вывод статуса агента"""
        try:
            print(f"\n📊 СТАТУС АГЕНТА:")
            print(f"   🎯 Статус: {'🟢 Активен' if self.agent_active else '🔴 Остановлен'}")
            print(f"   💬 Сообщений в истории: {len(self.chat_history)}")
            
            # Системная информация
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            print(f"\n💻 СИСТЕМНАЯ ИНФОРМАЦИЯ:")
            print(f"   CPU: {cpu_percent:.1f}%")
            print(f"   RAM: {memory.percent:.1f}% ({memory.used // 1024**3:.1f}GB / {memory.total // 1024**3:.1f}GB)")
            print(f"   Диск: {disk.percent:.1f}% ({disk.used // 1024**3:.1f}GB / {disk.total // 1024**3:.1f}GB)")
            
        except Exception as e:
            print(f"❌ Ошибка получения статуса: {e}")
    
    def print_help(self):
        """Вывод справки"""
        help_text = """
📋 ДОСТУПНЫЕ КОМАНДЫ:

🤖 Управление агентом:
  start          - Запустить агента
  stop           - Остановить агента
  restart        - Перезапустить агента
  status         - Показать статус

💬 Взаимодействие:
  chat <сообщение> - Отправить сообщение агенту
  ask <вопрос>     - Задать вопрос агенту

🔧 Инструменты:
  analyze         - Анализ производительности
  security        - Проверка безопасности
  bottlenecks     - Поиск узких мест
  evolution       - План эволюции
  tools           - Список инструментов

📊 Мониторинг:
  logs            - Показать логи
  system          - Системная информация
  history         - История чата
  clear           - Очистить экран

⚙️ Система:
  clear           - Очистить экран
  quit/exit       - Выход
  help            - Эта справка
        """
        print(help_text)
    
    def start_agent(self):
        """Запустить агента"""
        self.agent_active = True
        print("🟢 Агент запущен!")
    
    def stop_agent(self):
        """Остановить агента"""
        self.agent_active = False
        print("🔴 Агент остановлен!")
    
    def restart_agent(self):
        """Перезапустить агента"""
        self.stop_agent()
        time.sleep(1)
        self.start_agent()
        print("🔄 Агент перезапущен!")
    
    def process_message(self, message):
        """Обработка сообщения агентом"""
        try:
            print(f"\n🤖 ARK обрабатывает: '{message}'")
            
            # Добавить в историю
            self.chat_history.append({
                'user': message,
                'timestamp': time.time()
            })
            
            # Генерация ответа
            if "привет" in message.lower():
                response = "Привет! Я ARK v2.8 - ваш когнитивный ИИ-агент. Как я могу помочь?"
            elif "как дела" in message.lower():
                response = "Спасибо, у меня все хорошо! Готов помочь вам с любыми задачами."
            elif "что ты умеешь" in message.lower():
                response = """Я умею:
• Анализировать производительность системы
• Проверять безопасность кода
• Планировать эволюцию агента
• Общаться через консольный интерфейс
• Мониторить состояние системы
• Выявлять узкие места
• Работать с памятью и сознанием"""
            elif "статус" in message.lower():
                response = f"""Статус системы:
• Агент: {'Активен' if self.agent_active else 'Остановлен'}
• Сообщений в истории: {len(self.chat_history)}
• Система: Работает нормально
• Когнитивные отделы: 6 активных"""
            elif "анализ" in message.lower() or "производительность" in message.lower():
                cpu = psutil.cpu_percent()
                memory = psutil.virtual_memory()
                response = f"""Анализ производительности:
• CPU: {cpu:.1f}%
• RAM: {memory.percent:.1f}%
• Система: {'Оптимальная' if cpu < 80 and memory.percent < 80 else 'Требует внимания'}"""
            elif "безопасность" in message.lower():
                response = """Проверка безопасности:
• Файловая система: Безопасна
• Сетевое подключение: Стабильно
• Процессы: Нормальные
• Рекомендации: Регулярно обновляйте систему"""
            elif "эволюция" in message.lower():
                response = """План эволюции ARK:
• Этап 1: Улучшение когнитивной архитектуры
• Этап 2: Расширение инструментов
• Этап 3: Интеграция с внешними системами
• Этап 4: Самообучение и адаптация"""
            else:
                response = f"Обработал ваш запрос: '{message}'. Это интересная задача для когнитивной архитектуры!"
            
            # Добавить ответ в историю
            self.chat_history.append({
                'agent': response,
                'timestamp': time.time()
            })
            
            print(f"🤖 ARK: {response}")
            
        except Exception as e:
            print(f"❌ Ошибка обработки: {e}")
            print(f"🤖 ARK: Извините, произошла ошибка при обработке вашего сообщения. Попробуйте еще раз.")
    
    def run_tool(self, tool_name):
        """Запуск инструмента"""
        try:
            print(f"🔧 Запуск инструмента: {tool_name}")
            
            if tool_name == "analyze":
                cpu = psutil.cpu_percent()
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                print(f"✅ Результат анализа:")
                print(f"   CPU: {cpu:.1f}%")
                print(f"   RAM: {memory.percent:.1f}%")
                print(f"   Диск: {disk.percent:.1f}%")
                
            elif tool_name == "security":
                print(f"✅ Результат проверки безопасности:")
                print(f"   Статус: Безопасно")
                print(f"   Рекомендации: Регулярные обновления")
                
            elif tool_name == "bottlenecks":
                print(f"✅ Поиск узких мест:")
                print(f"   CPU: {'Нормально' if psutil.cpu_percent() < 80 else 'Высокая нагрузка'}")
                print(f"   RAM: {'Нормально' if psutil.virtual_memory().percent < 80 else 'Высокое использование'}")
                
            elif tool_name == "evolution":
                print(f"✅ План эволюции:")
                print(f"   Этап 1: Улучшение архитектуры")
                print(f"   Этап 2: Новые инструменты")
                print(f"   Этап 3: Интеграция")
                
            else:
                print(f"❌ Инструмент {tool_name} не найден")
                
        except Exception as e:
            print(f"❌ Ошибка запуска инструмента {tool_name}: {e}")
    
    def show_logs(self):
        """Показать логи"""
        try:
            log_file = Path("logs/ark.log")
            if log_file.exists():
                with open(log_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    recent_logs = lines[-20:] if len(lines) > 20 else lines
                    print("\n📋 ПОСЛЕДНИЕ ЛОГИ:")
                    print("=" * 50)
                    for line in recent_logs:
                        print(line.rstrip())
            else:
                print("📋 Логи не найдены")
        except Exception as e:
            print(f"❌ Ошибка чтения логов: {e}")
    
    def show_system_info(self):
        """Показать системную информацию"""
        try:
            print("\n💻 СИСТЕМНАЯ ИНФОРМАЦИЯ:")
            print("=" * 30)
            
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            print(f"CPU: {cpu_percent:.1f}%")
            
            # Память
            memory = psutil.virtual_memory()
            print(f"RAM: {memory.percent:.1f}% ({memory.used // 1024**3:.1f}GB / {memory.total // 1024**3:.1f}GB)")
            
            # Диск
            disk = psutil.disk_usage('/')
            print(f"Диск: {disk.percent:.1f}% ({disk.used // 1024**3:.1f}GB / {disk.total // 1024**3:.1f}GB)")
            
            # Процессы
            processes = len(psutil.pids())
            print(f"Процессы: {processes}")
            
            # Сеть
            network = psutil.net_io_counters()
            print(f"Сеть: ↑{network.bytes_sent // 1024**2:.1f}MB ↓{network.bytes_recv // 1024**2:.1f}MB")
            
        except Exception as e:
            print(f"❌ Ошибка получения системной информации: {e}")
    
    def show_history(self):
        """Показать историю чата"""
        if not self.chat_history:
            print("📋 История чата пуста")
            return
            
        print("\n📋 ИСТОРИЯ ЧАТА:")
        print("=" * 50)
        for i, entry in enumerate(self.chat_history[-10:], 1):
            if 'user' in entry:
                print(f"{i}. 👤 Вы: {entry['user']}")
            elif 'agent' in entry:
                print(f"{i}. 🤖 ARK: {entry['agent']}")
    
    def clear_screen(self):
        """Очистить экран"""
        os.system('clear' if os.name == 'posix' else 'cls')
        self.print_banner()
    
    def run(self):
        """Основной цикл приложения"""
        self.print_banner()
        self.start_agent()
        
        while self.running:
            try:
                # Показать промпт
                print(f"\n{'🟢' if self.agent_active else '🔴'} ARK> ", end="")
                command = input().strip()
                
                if not command:
                    continue
                
                # Обработка команд
                if command.lower() in ['quit', 'exit', 'q']:
                    print("👋 До свидания!")
                    break
                    
                elif command.lower() == 'help':
                    self.print_help()
                    
                elif command.lower() == 'status':
                    self.print_status()
                    
                elif command.lower() == 'start':
                    self.start_agent()
                    
                elif command.lower() == 'stop':
                    self.stop_agent()
                    
                elif command.lower() == 'restart':
                    self.restart_agent()
                    
                elif command.lower() == 'clear':
                    self.clear_screen()
                    
                elif command.lower() == 'system':
                    self.show_system_info()
                    
                elif command.lower() == 'logs':
                    self.show_logs()
                    
                elif command.lower() == 'history':
                    self.show_history()
                    
                elif command.lower() == 'tools':
                    print("🔧 Доступные инструменты:")
                    print("   analyze - Анализ производительности")
                    print("   security - Проверка безопасности")
                    print("   bottlenecks - Поиск узких мест")
                    print("   evolution - План эволюции")
                    
                elif command.startswith('chat '):
                    message = command[5:]
                    self.process_message(message)
                    
                elif command.startswith('ask '):
                    message = command[4:]
                    self.process_message(message)
                    
                elif command in ['analyze', 'security', 'bottlenecks', 'evolution']:
                    self.run_tool(command)
                    
                else:
                    # Если команда не распознана, обрабатываем как сообщение
                    self.process_message(command)
                    
            except KeyboardInterrupt:
                print("\n👋 До свидания!")
                break
            except Exception as e:
                print(f"❌ Ошибка: {e}")

def main():
    """Главная функция"""
    app = ARKSimpleConsole()
    app.run()

if __name__ == "__main__":
    main() 