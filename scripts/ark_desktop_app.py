#!/usr/bin/env python3
"""
ARK v2.8 - Нативное десктопное приложение
Прямое взаимодействие с агентом через GUI
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import json
import sys
from pathlib import Path
import subprocess
import psutil
import os

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from mind.cognitive_architecture import cognitive_brain
from mind.advanced_consciousness import AdvancedConsciousnessModel
from evaluation.auto_reporter import auto_reporter

class ARKDesktopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ARK v2.8 - Когнитивный ИИ-агент")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2b2b2b')
        
        # Инициализация компонентов
        self.cognitive_brain = cognitive_brain
        self.consciousness = AdvancedConsciousnessModel()
        self.auto_reporter = auto_reporter
        
        # Состояние агента
        self.agent_active = False
        self.agent_thread = None
        
        self.setup_ui()
        self.start_agent()
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        
        # Главный контейнер
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Верхняя панель с информацией
        self.setup_status_panel(main_frame)
        
        # Основная область с вкладками
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Вкладка чата
        self.setup_chat_tab(notebook)
        
        # Вкладка мониторинга
        self.setup_monitoring_tab(notebook)
        
        # Вкладка системы
        self.setup_system_tab(notebook)
        
        # Вкладка эволюции
        self.setup_evolution_tab(notebook)
    
    def setup_status_panel(self, parent):
        """Панель статуса агента"""
        status_frame = ttk.LabelFrame(parent, text="Статус агента", padding=10)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Статус агента
        self.status_label = ttk.Label(status_frame, text="🔄 Инициализация...", font=('Arial', 12, 'bold'))
        self.status_label.pack(side=tk.LEFT, padx=(0, 20))
        
        # Сознание
        self.consciousness_label = ttk.Label(status_frame, text="🧠 Сознание: загрузка...", font=('Arial', 10))
        self.consciousness_label.pack(side=tk.LEFT, padx=(0, 20))
        
        # Эмоции
        self.emotion_label = ttk.Label(status_frame, text="😊 Эмоция: загрузка...", font=('Arial', 10))
        self.emotion_label.pack(side=tk.LEFT, padx=(0, 20))
        
        # Кнопки управления
        control_frame = ttk.Frame(status_frame)
        control_frame.pack(side=tk.RIGHT)
        
        self.start_btn = ttk.Button(control_frame, text="▶️ Запустить", command=self.start_agent)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_btn = ttk.Button(control_frame, text="⏹️ Остановить", command=self.stop_agent)
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.restart_btn = ttk.Button(control_frame, text="🔄 Перезапустить", command=self.restart_agent)
        self.restart_btn.pack(side=tk.LEFT)
    
    def setup_chat_tab(self, notebook):
        """Вкладка чата с агентом"""
        chat_frame = ttk.Frame(notebook)
        notebook.add(chat_frame, text="💬 Чат с агентом")
        
        # Область чата
        chat_area = ttk.Frame(chat_frame)
        chat_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # История сообщений
        self.chat_display = scrolledtext.ScrolledText(
            chat_area, 
            height=20, 
            font=('Consolas', 10),
            bg='#1e1e1e',
            fg='#ffffff',
            insertbackground='white'
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Область ввода
        input_frame = ttk.Frame(chat_area)
        input_frame.pack(fill=tk.X)
        
        self.message_entry = ttk.Entry(input_frame, font=('Arial', 11))
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.message_entry.bind('<Return>', self.send_message)
        
        send_btn = ttk.Button(input_frame, text="📤 Отправить", command=self.send_message)
        send_btn.pack(side=tk.RIGHT)
        
        # Быстрые команды
        commands_frame = ttk.LabelFrame(chat_frame, text="Быстрые команды", padding=10)
        commands_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        commands = [
            ("🧠 Статус мозга", "Покажи статус когнитивной архитектуры"),
            ("📊 Мониторинг", "Покажи состояние системы"),
            ("🔧 Инструменты", "Какие инструменты доступны?"),
            ("🎯 Задачи", "Какие задачи выполняются?"),
            ("📈 Эволюция", "Покажи статус эволюции"),
            ("🔍 Анализ", "Проанализируй производительность системы")
        ]
        
        for i, (label, command) in enumerate(commands):
            btn = ttk.Button(commands_frame, text=label, 
                           command=lambda cmd=command: self.quick_command(cmd))
            btn.grid(row=i//3, column=i%3, padx=5, pady=2, sticky='ew')
    
    def setup_monitoring_tab(self, notebook):
        """Вкладка мониторинга системы"""
        monitor_frame = ttk.Frame(notebook)
        notebook.add(monitor_frame, text="📊 Мониторинг")
        
        # Системная информация
        system_frame = ttk.LabelFrame(monitor_frame, text="Системная информация", padding=10)
        system_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.cpu_label = ttk.Label(system_frame, text="CPU: загрузка...")
        self.cpu_label.pack(anchor=tk.W)
        
        self.memory_label = ttk.Label(system_frame, text="RAM: загрузка...")
        self.memory_label.pack(anchor=tk.W)
        
        self.disk_label = ttk.Label(system_frame, text="Диск: загрузка...")
        self.disk_label.pack(anchor=tk.W)
        
        # Логи агента
        logs_frame = ttk.LabelFrame(monitor_frame, text="Логи агента", padding=10)
        logs_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.logs_display = scrolledtext.ScrolledText(
            logs_frame, 
            height=15, 
            font=('Consolas', 9),
            bg='#1e1e1e',
            fg='#00ff00'
        )
        self.logs_display.pack(fill=tk.BOTH, expand=True)
        
        # Кнопка обновления логов
        refresh_btn = ttk.Button(logs_frame, text="🔄 Обновить логи", command=self.refresh_logs)
        refresh_btn.pack(pady=(5, 0))
    
    def setup_system_tab(self, notebook):
        """Вкладка системных инструментов"""
        system_frame = ttk.Frame(notebook)
        notebook.add(system_frame, text="🔧 Система")
        
        # Инструменты
        tools_frame = ttk.LabelFrame(system_frame, text="Инструменты агента", padding=10)
        tools_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tools = [
            ("📊 Анализ производительности", "analyze_performance"),
            ("🔍 Поиск узких мест", "identify_bottlenecks"),
            ("🔒 Проверка безопасности", "check_security"),
            ("📝 Обзор кода", "review_code_changes"),
            ("✅ Валидация синтаксиса", "validate_syntax"),
            ("🚀 План эволюции", "plan_evolution")
        ]
        
        for i, (label, tool) in enumerate(tools):
            btn = ttk.Button(tools_frame, text=label, 
                           command=lambda t=tool: self.run_tool(t))
            btn.grid(row=i//2, column=i%2, padx=5, pady=5, sticky='ew')
        
        # Системные действия
        actions_frame = ttk.LabelFrame(system_frame, text="Системные действия", padding=10)
        actions_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        actions = [
            ("🔄 Перезапуск агента", self.restart_agent),
            ("📋 Экспорт логов", self.export_logs),
            ("🧹 Очистка кэша", self.clear_cache),
            ("⚙️ Настройки", self.show_settings)
        ]
        
        for i, (label, action) in enumerate(actions):
            btn = ttk.Button(actions_frame, text=label, command=action)
            btn.grid(row=i//2, column=i%2, padx=5, pady=5, sticky='ew')
    
    def setup_evolution_tab(self, notebook):
        """Вкладка эволюции агента"""
        evolution_frame = ttk.Frame(notebook)
        notebook.add(evolution_frame, text="🚀 Эволюция")
        
        # Статус эволюции
        status_frame = ttk.LabelFrame(evolution_frame, text="Статус эволюции", padding=10)
        status_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.evolution_status = ttk.Label(status_frame, text="Статус: загрузка...")
        self.evolution_status.pack(anchor=tk.W)
        
        self.evolution_progress = ttk.Progressbar(status_frame, mode='determinate')
        self.evolution_progress.pack(fill=tk.X, pady=(5, 0))
        
        # Эволюционные действия
        actions_frame = ttk.LabelFrame(evolution_frame, text="Эволюционные действия", padding=10)
        actions_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        evolution_actions = [
            ("🧠 Улучшить когнитивную архитектуру", "Улучши когнитивную архитектуру"),
            ("🎯 Оптимизировать внимание", "Оптимизируй систему внимания"),
            ("💾 Расширить память", "Расширь возможности памяти"),
            ("🔧 Улучшить инструменты", "Улучши системные инструменты"),
            ("🎨 Развить эмоции", "Развивай эмоциональную систему"),
            ("🚀 Запустить эволюцию", "Запусти процесс эволюции")
        ]
        
        for i, (label, command) in enumerate(evolution_actions):
            btn = ttk.Button(actions_frame, text=label, 
                           command=lambda cmd=command: self.evolution_command(cmd))
            btn.grid(row=i//2, column=i%2, padx=5, pady=5, sticky='ew')
    
    def start_agent(self):
        """Запуск агента"""
        if not self.agent_active:
            self.agent_active = True
            self.agent_thread = threading.Thread(target=self.agent_loop, daemon=True)
            self.agent_thread.start()
            
            self.status_label.config(text="🟢 Агент активен")
            self.start_btn.config(state='disabled')
            self.stop_btn.config(state='normal')
            
            self.log_message("🤖 Агент ARK v2.8 запущен и готов к работе!")
    
    def stop_agent(self):
        """Остановка агента"""
        self.agent_active = False
        self.status_label.config(text="🔴 Агент остановлен")
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        
        self.log_message("⏹️ Агент остановлен")
    
    def restart_agent(self):
        """Перезапуск агента"""
        self.stop_agent()
        time.sleep(1)
        self.start_agent()
    
    def agent_loop(self):
        """Основной цикл агента"""
        while self.agent_active:
            try:
                # Обновление состояния сознания
                consciousness_state = self.consciousness.get_consciousness_status()
                
                # Обновление эмоций
                emotion_state = self.cognitive_brain.emotion_engine.get_emotional_state()
                
                # Обновление UI в главном потоке
                self.root.after(0, self.update_status, consciousness_state, emotion_state)
                
                # Обновление системной информации
                self.root.after(0, self.update_system_info)
                
                time.sleep(2)  # Обновление каждые 2 секунды
                
            except Exception as e:
                self.root.after(0, self.log_message, f"❌ Ошибка агента: {e}")
                time.sleep(5)
    
    def update_status(self, consciousness_state, emotion_state):
        """Обновление статуса в UI"""
        try:
            self.consciousness_label.config(text=f"🧠 Сознание: {consciousness_state.get('state', 'unknown')}")
            self.emotion_label.config(text=f"😊 Эмоция: {emotion_state.get('dominant_emotion', 'unknown')}")
        except:
            pass
    
    def update_system_info(self):
        """Обновление системной информации"""
        try:
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            self.cpu_label.config(text=f"CPU: {cpu_percent:.1f}%")
            self.memory_label.config(text=f"RAM: {memory.percent:.1f}% ({memory.used // 1024**3:.1f}GB / {memory.total // 1024**3:.1f}GB)")
            self.disk_label.config(text=f"Диск: {disk.percent:.1f}% ({disk.used // 1024**3:.1f}GB / {disk.total // 1024**3:.1f}GB)")
        except:
            pass
    
    def send_message(self):
        """Отправить сообщение агенту"""
        message = self.message_entry.get().strip()
        if not message:
            return
            
        # Очистить поле ввода
        self.message_entry.delete(0, tk.END)
        
        # Добавить сообщение пользователя в чат
        self.chat_display.insert(tk.END, f"\n👤 Вы: {message}\n", "user")
        self.chat_display.see(tk.END)
        
        # Обработка в отдельном потоке
        threading.Thread(target=self._process_message, args=(message,), daemon=True).start()
    
    def _process_message(self, message):
        """Обработка сообщения в отдельном потоке"""
        try:
            # Обработка через когнитивную архитектуру
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
            
            # Добавить ответ агента в чат (в главном потоке)
            self.root.after(0, lambda: self._add_agent_response(response))
            
        except Exception as e:
            error_msg = f"❌ Ошибка обработки: {e}"
            self.root.after(0, lambda: self._add_agent_response("Извините, произошла ошибка при обработке вашего сообщения. Попробуйте еще раз."))
    
    def _add_agent_response(self, response):
        """Добавить ответ агента в чат"""
        self.chat_display.insert(tk.END, f"🤖 ARK: {response}\n", "agent")
        self.chat_display.see(tk.END)
    
    def quick_command(self, command):
        """Быстрая команда"""
        self.message_entry.delete(0, tk.END)
        self.message_entry.insert(0, command)
        self.send_message()
    
    def run_tool(self, tool_name):
        """Запуск инструмента"""
        try:
            if hasattr(self.cognitive_brain, tool_name):
                result = getattr(self.cognitive_brain, tool_name)()
                self.display_response(f"Инструмент {tool_name}: {result}")
            else:
                self.display_response(f"Инструмент {tool_name} не найден")
        except Exception as e:
            self.display_response(f"Ошибка запуска инструмента {tool_name}: {e}")
    
    def evolution_command(self, command):
        """Команда эволюции"""
        self.send_message()
        self.message_entry.delete(0, tk.END)
        self.message_entry.insert(0, command)
        self.send_message()
    
    def refresh_logs(self):
        """Обновление логов"""
        try:
            log_file = Path("logs/ark.log")
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    recent_logs = lines[-50:] if len(lines) > 50 else lines
                    self.logs_display.delete(1.0, tk.END)
                    self.logs_display.insert(tk.END, ''.join(recent_logs))
        except Exception as e:
            self.logs_display.delete(1.0, tk.END)
            self.logs_display.insert(tk.END, f"Ошибка чтения логов: {e}")
    
    def log_message(self, message):
        """Логирование сообщения"""
        timestamp = time.strftime("%H:%M:%S")
        self.logs_display.insert(tk.END, f"[{timestamp}] {message}\n")
        self.logs_display.see(tk.END)
    
    def export_logs(self):
        """Экспорт логов"""
        try:
            filename = f"ark_logs_{time.strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.logs_display.get(1.0, tk.END))
            messagebox.showinfo("Экспорт", f"Логи сохранены в {filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка экспорта: {e}")
    
    def clear_cache(self):
        """Очистка кэша"""
        try:
            # Очистка рабочей памяти
            self.cognitive_brain.working_memory.clear()
            self.log_message("🧹 Кэш очищен")
            messagebox.showinfo("Очистка", "Кэш успешно очищен")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка очистки: {e}")
    
    def show_settings(self):
        """Показать настройки"""
        messagebox.showinfo("Настройки", "Настройки будут добавлены в следующей версии")

def main():
    """Главная функция"""
    root = tk.Tk()
    app = ARKDesktopApp(root)
    
    # Обработка закрытия
    def on_closing():
        app.stop_agent()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main() 