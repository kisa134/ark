#!/usr/bin/env python3
"""
ARK v2.8 - Консольное приложение
Прямое взаимодействие с агентом через терминал
"""

import sys
import time
import threading
import json
import os
from pathlib import Path
import psutil
import subprocess

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from mind.cognitive_architecture import cognitive_brain
from mind.advanced_consciousness import AdvancedConsciousnessModel
from evaluation.auto_reporter import auto_reporter

class ARKConsoleApp:
    def __init__(self):
        self.cognitive_brain = cognitive_brain
        self.consciousness = AdvancedConsciousnessModel()
        self.auto_reporter = auto_reporter
        self.running = True
        self.agent_active = False
        
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
            consciousness_state = self.consciousness.get_consciousness_status()
            emotion_state = self.cognitive_brain.emotion_engine.get_emotional_state()
            
            print(f"\n📊 СТАТУС АГЕНТА:")
            print(f"   🧠 Сознание: {consciousness_state.get('state', 'unknown')}")
            print(f"   😊 Эмоция: {emotion_state.get('dominant_emotion', 'unknown')}")
            print(f"   🎯 Статус: {'🟢 Активен' if self.agent_active else '🔴 Остановлен'}")
            
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
  memory          - Состояние памяти
  consciousness   - Состояние сознания

⚙️ Система:
  clear           - Очистить экран
  quit/exit       - Выход
  help            - Эта справка

💡 Примеры:
  chat Привет! Как дела?
  ask Покажи статус системы
  analyze
  status
        """
        print(help_text)
    
    def start_agent(self):
        """Запуск агента"""
        if not self.agent_active:
            self.agent_active = True
            print("🟢 Агент запущен!")
            
            # Запуск фонового мониторинга
            monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
            monitor_thread.start()
        else:
            print("⚠️ Агент уже запущен")
    
    def stop_agent(self):
        """Остановка агента"""
        self.agent_active = False
        print("🔴 Агент остановлен")
    
    def restart_agent(self):
        """Перезапуск агента"""
        print("🔄 Перезапуск агента...")
        self.stop_agent()
        time.sleep(1)
        self.start_agent()
    
    def monitor_loop(self):
        """Цикл мониторинга"""
        while self.agent_active:
            try:
                # Логирование активности
                consciousness_state = self.consciousness.get_consciousness_status()
                emotion_state = self.cognitive_brain.emotion_engine.get_emotional_state()
                
                # Запись в лог
                timestamp = time.strftime("%H:%M:%S")
                log_entry = f"[{timestamp}] Сознание: {consciousness_state.get('state', 'unknown')}, Эмоция: {emotion_state.get('dominant_emotion', 'unknown')}\n"
                
                with open("logs/ark_console.log", "a", encoding="utf-8") as f:
                    f.write(log_entry)
                
                time.sleep(5)  # Обновление каждые 5 секунд
                
            except Exception as e:
                print(f"❌ Ошибка мониторинга: {e}")
                time.sleep(10)
    
    def process_message(self, message):
        """Обработка сообщения агентом"""
        try:
            print(f"\n🤖 ARK обрабатывает: '{message}'")
            
            # Обработка через когнитивную архитектуру
            # Используем asyncio для вызова асинхронного метода
            import asyncio
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(self.cognitive_brain.process_input(message))
                loop.close()
            except Exception as e:
                print(f"⚠️ Предупреждение: {e}")
                result = None
            
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
• Общаться через когнитивную архитектуру
• Мониторить состояние системы
• Выявлять узкие места
• Работать с памятью и сознанием"""
            elif "статус" in message.lower():
                try:
                    consciousness_state = self.consciousness.get_consciousness_status()
                    emotion_state = self.cognitive_brain.emotion_engine.get_emotional_state()
                    response = f"""Статус системы:
• Сознание: {consciousness_state.get('state', 'unknown')}
• Эмоция: {emotion_state.get('dominant_emotion', 'unknown')}
• Когнитивные отделы: 6 активных
• Рабочая память: {len(self.cognitive_brain.working_memory.items)} элементов"""
                except Exception as e:
                    response = f"Статус системы: активен (детали недоступны: {e})"
            else:
                if result and isinstance(result, dict):
                    decision = result.get('final_decision', 'Запрос обработан')
                    confidence = result.get('confidence_score', 0.0)
                    response = f"Результат обработки: {decision} (уверенность: {confidence:.2f})"
                else:
                    response = f"Обработал ваш запрос: '{message}'. Результат: {result if result else 'Запрос обработан когнитивной архитектурой'}"
            
            print(f"🤖 ARK: {response}")
            
        except Exception as e:
            print(f"❌ Ошибка обработки: {e}")
            print(f"🤖 ARK: Извините, произошла ошибка при обработке вашего сообщения. Попробуйте еще раз.")
    
    def run_tool(self, tool_name):
        """Запуск инструмента"""
        try:
            print(f"🔧 Запуск инструмента: {tool_name}")
            
            if hasattr(self.cognitive_brain, tool_name):
                result = getattr(self.cognitive_brain, tool_name)()
                print(f"✅ Результат: {result}")
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
    
    def show_memory_info(self):
        """Показать информацию о памяти агента"""
        try:
            print("\n💾 ПАМЯТЬ АГЕНТА:")
            print("=" * 20)
            
            # Рабочая память
            working_memory_items = len(self.cognitive_brain.working_memory.items)
            print(f"Рабочая память: {working_memory_items} элементов")
            
            # Долговременная память
            if hasattr(self.cognitive_brain, 'long_term_memory'):
                ltm_items = len(self.cognitive_brain.long_term_memory.items)
                print(f"Долговременная память: {ltm_items} элементов")
            
            # Эмоциональная память
            emotion_records = len(self.cognitive_brain.emotion_engine.emotion_history)
            print(f"Эмоциональная память: {emotion_records} записей")
            
        except Exception as e:
            print(f"❌ Ошибка получения информации о памяти: {e}")
    
    def show_consciousness_info(self):
        """Показать информацию о сознании"""
        try:
            print("\n🧠 СОЗНАНИЕ АГЕНТА:")
            print("=" * 25)
            
            consciousness_state = self.consciousness.get_consciousness_status()
            print(f"Состояние: {consciousness_state.get('state', 'unknown')}")
            print(f"Уровень: {consciousness_state.get('level', 'unknown')}")
            print(f"Активность: {consciousness_state.get('activity', 'unknown')}")
            
            emotion_state = self.cognitive_brain.emotion_engine.get_emotional_state()
            print(f"Доминирующая эмоция: {emotion_state.get('dominant_emotion', 'unknown')}")
            print(f"Эмоциональная стабильность: {emotion_state.get('emotional_stability', 'unknown')}")
            
        except Exception as e:
            print(f"❌ Ошибка получения информации о сознании: {e}")
    
    def run(self):
        """Запуск консольного приложения"""
        self.print_banner()
        self.start_agent()
        
        while self.running:
            try:
                # Приглашение к вводу
                command = input("\n🤖 ARK> ").strip()
                
                if not command:
                    continue
                
                # Разбор команды
                parts = command.split(' ', 1)
                cmd = parts[0].lower()
                args = parts[1] if len(parts) > 1 else ""
                
                # Обработка команд
                if cmd in ['quit', 'exit', 'q']:
                    print("👋 До свидания!")
                    self.stop_agent()
                    break
                    
                elif cmd == 'help':
                    self.print_help()
                    
                elif cmd == 'status':
                    self.print_status()
                    
                elif cmd == 'start':
                    self.start_agent()
                    
                elif cmd == 'stop':
                    self.stop_agent()
                    
                elif cmd == 'restart':
                    self.restart_agent()
                    
                elif cmd == 'clear':
                    os.system('clear' if os.name == 'posix' else 'cls')
                    self.print_banner()
                    
                elif cmd == 'chat':
                    if args:
                        self.process_message(args)
                    else:
                        print("❌ Укажите сообщение для отправки")
                        
                elif cmd == 'ask':
                    if args:
                        self.process_message(args)
                    else:
                        print("❌ Укажите вопрос")
                        
                elif cmd == 'analyze':
                    self.run_tool('analyze_performance')
                    
                elif cmd == 'security':
                    self.run_tool('check_security')
                    
                elif cmd == 'bottlenecks':
                    self.run_tool('identify_bottlenecks')
                    
                elif cmd == 'evolution':
                    self.run_tool('plan_evolution')
                    
                elif cmd == 'tools':
                    print("\n🔧 ДОСТУПНЫЕ ИНСТРУМЕНТЫ:")
                    tools = ['analyze_performance', 'check_security', 'identify_bottlenecks', 
                            'review_code_changes', 'validate_syntax', 'plan_evolution']
                    for tool in tools:
                        print(f"  • {tool}")
                        
                elif cmd == 'logs':
                    self.show_logs()
                    
                elif cmd == 'system':
                    self.show_system_info()
                    
                elif cmd == 'memory':
                    self.show_memory_info()
                    
                elif cmd == 'consciousness':
                    self.show_consciousness_info()
                    
                else:
                    # Если команда не распознана, отправляем как сообщение
                    self.process_message(command)
                    
            except KeyboardInterrupt:
                print("\n\n👋 До свидания!")
                self.stop_agent()
                break
            except Exception as e:
                print(f"❌ Ошибка: {e}")

def main():
    """Главная функция"""
    app = ARKConsoleApp()
    app.run()

if __name__ == "__main__":
    main() 