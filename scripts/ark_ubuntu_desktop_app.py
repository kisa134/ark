#!/usr/bin/env python3
"""
ARK v2.8 - Ubuntu Desktop Application
Десктопное приложение с глубокой интеграцией Ubuntu
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
from system_integration.ark_ubuntu_integration import ARKUbuntuIntegration

class ARKUbuntuDesktopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ARK v2.8 - Ubuntu Integration")
        self.root.geometry("1400x900")
        self.root.configure(bg='#2b2b2b')
        
        # Инициализация компонентов
        self.cognitive_brain = cognitive_brain
        self.consciousness = AdvancedConsciousnessModel()
        self.auto_reporter = auto_reporter
        self.ubuntu_integration = ARKUbuntuIntegration()
        
        # Состояние агента
        self.agent_active = True
        self.monitoring_active = False
        
        self.setup_ui()
        self.start_monitoring()
    
    def setup_ui(self):
        """Настройка интерфейса"""
        # Главный контейнер
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Заголовок
        header_frame = tk.Frame(main_frame, bg='#2b2b2b')
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = tk.Label(
            header_frame,
            text="🧠 ARK v2.8 - Ubuntu Integration",
            font=("Arial", 16, "bold"),
            fg='#00ff00',
            bg='#2b2b2b'
        )
        title_label.pack()
        
        # Создание вкладок
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Вкладка чата
        self.setup_chat_tab(notebook)
        
        # Вкладка системы
        self.setup_system_tab(notebook)
        
        # Вкладка мониторинга
        self.setup_monitoring_tab(notebook)
        
        # Вкладка безопасности
        self.setup_security_tab(notebook)
        
        # Вкладка управления
        self.setup_management_tab(notebook)
    
    def setup_chat_tab(self, notebook):
        """Настройка вкладки чата"""
        chat_frame = tk.Frame(notebook, bg='#2b2b2b')
        notebook.add(chat_frame, text="💬 Чат")
        
        # Область чата
        chat_display_frame = tk.Frame(chat_frame, bg='#2b2b2b')
        chat_display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_display_frame,
            bg='#1e1e1e',
            fg='#ffffff',
            font=("Consolas", 10),
            wrap=tk.WORD
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # Настройка тегов для цветов
        self.chat_display.tag_configure("user", foreground="#00ff00")
        self.chat_display.tag_configure("agent", foreground="#0088ff")
        self.chat_display.tag_configure("system", foreground="#ff8800")
        self.chat_display.tag_configure("error", foreground="#ff0000")
        
        # Поле ввода
        input_frame = tk.Frame(chat_frame, bg='#2b2b2b')
        input_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.message_entry = tk.Entry(
            input_frame,
            bg='#1e1e1e',
            fg='#ffffff',
            font=("Arial", 12),
            insertbackground='#ffffff'
        )
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.message_entry.bind("<Return>", lambda e: self.send_message())
        
        send_button = tk.Button(
            input_frame,
            text="Отправить",
            command=self.send_message,
            bg='#0088ff',
            fg='#ffffff',
            font=("Arial", 10, "bold")
        )
        send_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Быстрые команды
        commands_frame = tk.Frame(chat_frame, bg='#2b2b2b')
        commands_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        commands = [
            ("Система", "Покажи статус системы"),
            ("Производительность", "Проанализируй производительность"),
            ("Безопасность", "Проверь безопасность"),
            ("Оптимизация", "Оптимизируй систему"),
            ("Обновления", "Проверь обновления")
        ]
        
        for i, (label, command) in enumerate(commands):
            btn = tk.Button(
                commands_frame,
                text=label,
                command=lambda cmd=command: self.quick_command(cmd),
                bg='#444444',
                fg='#ffffff',
                font=("Arial", 9)
            )
            btn.pack(side=tk.LEFT, padx=(0, 5))
    
    def setup_system_tab(self, notebook):
        """Настройка вкладки системы"""
        system_frame = tk.Frame(notebook, bg='#2b2b2b')
        notebook.add(system_frame, text="🖥️ Система")
        
        # Создание подвкладок для системы
        system_notebook = ttk.Notebook(system_frame)
        system_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Обзор системы
        overview_frame = tk.Frame(system_notebook, bg='#2b2b2b')
        system_notebook.add(overview_frame, text="Обзор")
        
        self.system_text = scrolledtext.ScrolledText(
            overview_frame,
            bg='#1e1e1e',
            fg='#ffffff',
            font=("Consolas", 9)
        )
        self.system_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Процессы
        processes_frame = tk.Frame(system_notebook, bg='#2b2b2b')
        system_notebook.add(processes_frame, text="Процессы")
        
        self.processes_text = scrolledtext.ScrolledText(
            processes_frame,
            bg='#1e1e1e',
            fg='#ffffff',
            font=("Consolas", 9)
        )
        self.processes_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Службы
        services_frame = tk.Frame(system_notebook, bg='#2b2b2b')
        system_notebook.add(services_frame, text="Службы")
        
        self.services_text = scrolledtext.ScrolledText(
            services_frame,
            bg='#1e1e1e',
            fg='#ffffff',
            font=("Consolas", 9)
        )
        self.services_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def setup_monitoring_tab(self, notebook):
        """Настройка вкладки мониторинга"""
        monitoring_frame = tk.Frame(notebook, bg='#2b2b2b')
        notebook.add(monitoring_frame, text="📊 Мониторинг")
        
        # Кнопки управления мониторингом
        control_frame = tk.Frame(monitoring_frame, bg='#2b2b2b')
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.start_monitoring_btn = tk.Button(
            control_frame,
            text="Запустить мониторинг",
            command=self.start_monitoring,
            bg='#00aa00',
            fg='#ffffff',
            font=("Arial", 10, "bold")
        )
        self.start_monitoring_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_monitoring_btn = tk.Button(
            control_frame,
            text="Остановить мониторинг",
            command=self.stop_monitoring,
            bg='#aa0000',
            fg='#ffffff',
            font=("Arial", 10, "bold")
        )
        self.stop_monitoring_btn.pack(side=tk.LEFT)
        
        # Область данных мониторинга
        self.monitoring_text = scrolledtext.ScrolledText(
            monitoring_frame,
            bg='#1e1e1e',
            fg='#ffffff',
            font=("Consolas", 9)
        )
        self.monitoring_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def setup_security_tab(self, notebook):
        """Настройка вкладки безопасности"""
        security_frame = tk.Frame(notebook, bg='#2b2b2b')
        notebook.add(security_frame, text="🔒 Безопасность")
        
        # Создание подвкладок для безопасности
        security_notebook = ttk.Notebook(security_frame)
        security_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Обзор безопасности
        sec_overview_frame = tk.Frame(security_notebook, bg='#2b2b2b')
        security_notebook.add(sec_overview_frame, text="Обзор")
        
        self.security_text = scrolledtext.ScrolledText(
            sec_overview_frame,
            bg='#1e1e1e',
            fg='#ffffff',
            font=("Consolas", 9)
        )
        self.security_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Файрвол
        firewall_frame = tk.Frame(security_notebook, bg='#2b2b2b')
        security_notebook.add(firewall_frame, text="Файрвол")
        
        self.firewall_text = scrolledtext.ScrolledText(
            firewall_frame,
            bg='#1e1e1e',
            fg='#ffffff',
            font=("Consolas", 9)
        )
        self.firewall_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Уязвимости
        vuln_frame = tk.Frame(security_notebook, bg='#2b2b2b')
        security_notebook.add(vuln_frame, text="Уязвимости")
        
        self.vulnerabilities_text = scrolledtext.ScrolledText(
            vuln_frame,
            bg='#1e1e1e',
            fg='#ffffff',
            font=("Consolas", 9)
        )
        self.vulnerabilities_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def setup_management_tab(self, notebook):
        """Настройка вкладки управления"""
        management_frame = tk.Frame(notebook, bg='#2b2b2b')
        notebook.add(management_frame, text="⚙️ Управление")
        
        # Кнопки управления
        buttons_frame = tk.Frame(management_frame, bg='#2b2b2b')
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Системные команды
        system_buttons = [
            ("Обновить систему", self.update_system),
            ("Оптимизировать", self.optimize_system),
            ("Анализ здоровья", self.analyze_health),
            ("Резервная копия", self.backup_system),
            ("Рекомендации", self.get_recommendations)
        ]
        
        for i, (text, command) in enumerate(system_buttons):
            btn = tk.Button(
                buttons_frame,
                text=text,
                command=command,
                bg='#444444',
                fg='#ffffff',
                font=("Arial", 10),
                width=15
            )
            btn.grid(row=i//3, column=i%3, padx=5, pady=5)
        
        # Область вывода команд
        self.management_text = scrolledtext.ScrolledText(
            management_frame,
            bg='#1e1e1e',
            fg='#ffffff',
            font=("Consolas", 9)
        )
        self.management_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
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
            if "система" in message.lower():
                response = self._get_system_response()
            elif "производительность" in message.lower():
                response = self._get_performance_response()
            elif "безопасность" in message.lower():
                response = self._get_security_response()
            elif "оптимизация" in message.lower():
                response = self._get_optimization_response()
            else:
                response = f"🤖 ARK: Обработал ваше сообщение: '{message}'. Как я могу помочь с системой Ubuntu?"
            
            # Обновление GUI в главном потоке
            self.root.after(0, lambda: self._update_chat(response, "agent"))
            
        except Exception as e:
            error_msg = f"❌ Ошибка обработки: {e}"
            self.root.after(0, lambda: self._update_chat(error_msg, "error"))
    
    def _get_system_response(self):
        """Получить ответ о системе"""
        try:
            status = self.ubuntu_integration.get_full_system_status()
            if "error" not in status:
                system_info = status.get("system_overview", {}).get("os_info", {})
                return f"🤖 ARK: Статус системы Ubuntu\n" \
                       f"Дистрибутив: {system_info.get('distribution', 'Неизвестно')}\n" \
                       f"Версия: {system_info.get('version', 'Неизвестно')}\n" \
                       f"Ядро: {system_info.get('kernel', 'Неизвестно')}\n" \
                       f"Время работы: {system_info.get('uptime', 'Неизвестно')}"
            else:
                return f"🤖 ARK: Ошибка получения информации о системе: {status['error']}"
        except Exception as e:
            return f"🤖 ARK: Ошибка анализа системы: {e}"
    
    def _get_performance_response(self):
        """Получить ответ о производительности"""
        try:
            metrics = self.ubuntu_integration.system_controller.get_performance_metrics()
            if "error" not in metrics:
                cpu = metrics.get("cpu_usage", 0)
                memory = metrics.get("memory_usage", {}).get("percent", 0)
                return f"🤖 ARK: Анализ производительности\n" \
                       f"CPU: {cpu}%\n" \
                       f"Память: {memory}%\n" \
                       f"Диск: {metrics.get('disk_usage', {}).get('percent', 0)}%"
            else:
                return f"🤖 ARK: Ошибка анализа производительности: {metrics['error']}"
        except Exception as e:
            return f"🤖 ARK: Ошибка анализа производительности: {e}"
    
    def _get_security_response(self):
        """Получить ответ о безопасности"""
        try:
            security = self.ubuntu_integration.network_security.get_security_overview()
            if "error" not in security:
                firewall = security.get("firewall", {})
                vulnerabilities = len(security.get("vulnerabilities", []))
                return f"🤖 ARK: Анализ безопасности\n" \
                       f"Файрвол: {'Активен' if firewall.get('ufw', {}).get('enabled') else 'Отключен'}\n" \
                       f"Уязвимости: {vulnerabilities}\n" \
                       f"Антивирус: {'Установлен' if security.get('antivirus', {}).get('clamav', {}).get('installed') else 'Не установлен'}"
            else:
                return f"🤖 ARK: Ошибка анализа безопасности: {security['error']}"
        except Exception as e:
            return f"🤖 ARK: Ошибка анализа безопасности: {e}"
    
    def _get_optimization_response(self):
        """Получить ответ об оптимизации"""
        try:
            result = self.ubuntu_integration.optimize_system()
            if result.get("success"):
                optimizations = result.get("optimizations", [])
                return f"🤖 ARK: Оптимизация выполнена\n" \
                       f"Выполнено действий: {len(optimizations)}\n" \
                       f"Действия: {', '.join(optimizations)}"
            else:
                return f"🤖 ARK: Ошибка оптимизации: {result.get('error', 'Неизвестная ошибка')}"
        except Exception as e:
            return f"🤖 ARK: Ошибка оптимизации: {e}"
    
    def _update_chat(self, message, tag="agent"):
        """Обновить чат"""
        self.chat_display.insert(tk.END, f"\n{message}\n", tag)
        self.chat_display.see(tk.END)
    
    def quick_command(self, command):
        """Быстрая команда"""
        self.message_entry.delete(0, tk.END)
        self.message_entry.insert(0, command)
        self.send_message()
    
    def start_monitoring(self):
        """Запустить мониторинг"""
        if not self.monitoring_active:
            result = self.ubuntu_integration.start_monitoring()
            if result.get("success"):
                self.monitoring_active = True
                self.start_monitoring_btn.config(state=tk.DISABLED)
                self.stop_monitoring_btn.config(state=tk.NORMAL)
                self._update_monitoring_display("Мониторинг запущен...")
            else:
                messagebox.showerror("Ошибка", f"Не удалось запустить мониторинг: {result.get('error')}")
    
    def stop_monitoring(self):
        """Остановить мониторинг"""
        if self.monitoring_active:
            result = self.ubuntu_integration.stop_monitoring()
            if result.get("success"):
                self.monitoring_active = False
                self.start_monitoring_btn.config(state=tk.NORMAL)
                self.stop_monitoring_btn.config(state=tk.DISABLED)
                self._update_monitoring_display("Мониторинг остановлен")
            else:
                messagebox.showerror("Ошибка", f"Не удалось остановить мониторинг: {result.get('error')}")
    
    def _update_monitoring_display(self, message):
        """Обновить отображение мониторинга"""
        self.monitoring_text.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.monitoring_text.see(tk.END)
    
    def update_system(self):
        """Обновить систему"""
        def update_thread():
            result = self.ubuntu_integration.update_system()
            if result.get("success"):
                self.root.after(0, lambda: self._update_management_display("✅ Система обновлена успешно"))
            else:
                self.root.after(0, lambda: self._update_management_display(f"❌ Ошибка обновления: {result.get('error')}"))
        
        threading.Thread(target=update_thread, daemon=True).start()
    
    def optimize_system(self):
        """Оптимизировать систему"""
        def optimize_thread():
            result = self.ubuntu_integration.optimize_system()
            if result.get("success"):
                optimizations = result.get("optimizations", [])
                self.root.after(0, lambda: self._update_management_display(f"✅ Оптимизация завершена: {', '.join(optimizations)}"))
            else:
                self.root.after(0, lambda: self._update_management_display(f"❌ Ошибка оптимизации: {result.get('error')}"))
        
        threading.Thread(target=optimize_thread, daemon=True).start()
    
    def analyze_health(self):
        """Анализ здоровья системы"""
        def analyze_thread():
            health = self.ubuntu_integration.analyze_system_health()
            if "error" not in health:
                status = health.get("overall_health", "unknown")
                issues = len(health.get("issues", []))
                self.root.after(0, lambda: self._update_management_display(f"🏥 Здоровье системы: {status}, Проблем: {issues}"))
            else:
                self.root.after(0, lambda: self._update_management_display(f"❌ Ошибка анализа: {health.get('error')}"))
        
        threading.Thread(target=analyze_thread, daemon=True).start()
    
    def backup_system(self):
        """Создать резервную копию"""
        def backup_thread():
            result = self.ubuntu_integration.backup_system_config()
            if result.get("success"):
                self.root.after(0, lambda: self._update_management_display(f"💾 Резервная копия создана: {result.get('backup_path')}"))
            else:
                self.root.after(0, lambda: self._update_management_display(f"❌ Ошибка резервного копирования: {result.get('error')}"))
        
        threading.Thread(target=backup_thread, daemon=True).start()
    
    def get_recommendations(self):
        """Получить рекомендации"""
        def recommendations_thread():
            recommendations = self.ubuntu_integration.get_system_recommendations()
            if "error" not in recommendations:
                total = recommendations.get("total", 0)
                critical = recommendations.get("critical", 0)
                self.root.after(0, lambda: self._update_management_display(f"💡 Рекомендаций: {total}, Критических: {critical}"))
            else:
                self.root.after(0, lambda: self._update_management_display(f"❌ Ошибка получения рекомендаций: {recommendations.get('error')}"))
        
        threading.Thread(target=recommendations_thread, daemon=True).start()
    
    def _update_management_display(self, message):
        """Обновить отображение управления"""
        self.management_text.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.management_text.see(tk.END)
    
    def start_monitoring(self):
        """Запустить фоновый мониторинг"""
        def monitoring_loop():
            while self.agent_active:
                try:
                    # Обновление системной информации
                    status = self.ubuntu_integration.get_full_system_status()
                    if "error" not in status:
                        system_info = status.get("system_overview", {}).get("os_info", {})
                        self.root.after(0, lambda: self._update_system_display(system_info))
                    
                    # Обновление процессов
                    processes = self.ubuntu_integration.system_controller.get_process_info()
                    if "error" not in processes:
                        self.root.after(0, lambda: self._update_processes_display(processes))
                    
                    # Обновление служб
                    services = self.ubuntu_integration.systemd_integration.get_running_services()
                    self.root.after(0, lambda: self._update_services_display(services))
                    
                    # Обновление безопасности
                    security = self.ubuntu_integration.network_security.get_security_overview()
                    if "error" not in security:
                        self.root.after(0, lambda: self._update_security_display(security))
                    
                    time.sleep(10)  # Обновление каждые 10 секунд
                    
                except Exception as e:
                    print(f"Ошибка мониторинга: {e}")
                    time.sleep(10)
        
        threading.Thread(target=monitoring_loop, daemon=True).start()
    
    def _update_system_display(self, system_info):
        """Обновить отображение системы"""
        self.system_text.delete(1.0, tk.END)
        info_text = f"Системная информация:\n"
        for key, value in system_info.items():
            info_text += f"{key}: {value}\n"
        self.system_text.insert(tk.END, info_text)
    
    def _update_processes_display(self, processes):
        """Обновить отображение процессов"""
        self.processes_text.delete(1.0, tk.END)
        processes_text = f"Процессы (всего: {processes.get('total_processes', 0)}):\n"
        top_processes = processes.get("top_processes", [])
        for proc in top_processes[:20]:  # Показываем топ 20
            processes_text += f"{proc.get('name', 'Unknown')}: {proc.get('cpu_percent', 0)}% CPU\n"
        self.processes_text.insert(tk.END, processes_text)
    
    def _update_services_display(self, services):
        """Обновить отображение служб"""
        self.services_text.delete(1.0, tk.END)
        services_text = f"Запущенные службы (всего: {len(services)}):\n"
        for service in services[:20]:  # Показываем топ 20
            services_text += f"{service.get('service_name', 'Unknown')}: {service.get('active_state', 'Unknown')}\n"
        self.services_text.insert(tk.END, services_text)
    
    def _update_security_display(self, security):
        """Обновить отображение безопасности"""
        self.security_text.delete(1.0, tk.END)
        security_text = f"Безопасность:\n"
        
        firewall = security.get("firewall", {})
        security_text += f"Файрвол: {'Активен' if firewall.get('ufw', {}).get('enabled') else 'Отключен'}\n"
        
        vulnerabilities = security.get("vulnerabilities", [])
        security_text += f"Уязвимости: {len(vulnerabilities)}\n"
        
        antivirus = security.get("antivirus", {})
        security_text += f"Антивирус: {'Установлен' if antivirus.get('clamav', {}).get('installed') else 'Не установлен'}\n"
        
        self.security_text.insert(tk.END, security_text)
    
    def on_closing(self):
        """Обработка закрытия приложения"""
        self.agent_active = False
        if self.monitoring_active:
            self.ubuntu_integration.stop_monitoring()
        self.root.destroy()

def main():
    """Главная функция"""
    root = tk.Tk()
    app = ARKUbuntuDesktopApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main() 