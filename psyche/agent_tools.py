"""
Инструменты агентов - полный набор функций для взаимодействия с системой
Реализует API First подход с четкими контрактами
"""

import subprocess
import psutil
import os
import json
import time
import shutil
from typing import Dict, List, Optional, Any, Tuple
import logging
from pathlib import Path

from config import config, BASE_DIR

# LangChain интеграция
try:
    from langchain.tools import tool
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logging.warning("LangChain не установлен, декораторы @tool недоступны")


class AgentTools:
    """
    Инструменты агентов - полный набор функций для взаимодействия с системой
    Реализует API First подход с четкими контрактами
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def read_system_logs(self, lines: int = 100, service: str = 'ark') -> str:
        """
        Читает последние N строк из journalctl для указанного сервиса.
        
        Args:
            lines: Количество строк для чтения
            service: Имя сервиса для фильтрации
            
        Returns:
            Строка с логами сервиса
        """
        try:
            command = f"journalctl -u {service} -n {lines} --no-pager"
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return result.stdout
            else:
                self.logger.warning(f"Ошибка чтения логов сервиса {service}: {result.stderr}")
                return f"Ошибка чтения логов: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return "Таймаут при чтении логов"
        except Exception as e:
            self.logger.error(f"Исключение при чтении логов: {e}")
            return f"Ошибка: {str(e)}"
    
    def get_process_info(self, pid: Optional[int] = None) -> Dict[str, Any]:
        """
        Получает информацию о процессе или всех процессах.
        
        Args:
            pid: ID процесса (None для всех процессов)
            
        Returns:
            Словарь с информацией о процессе(ах)
        """
        try:
            if pid:
                process = psutil.Process(pid)
                return {
                    "pid": process.pid,
                    "name": process.name(),
                    "status": process.status(),
                    "cpu_percent": process.cpu_percent(),
                    "memory_percent": process.memory_percent(),
                    "memory_info": process.memory_info()._asdict(),
                    "create_time": process.create_time(),
                    "cmdline": process.cmdline()
                }
            else:
                processes = []
                for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 'memory_percent']):
                    try:
                        processes.append(proc.info)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                return {"processes": processes, "total_count": len(processes)}
                
        except psutil.NoSuchProcess:
            return {"error": f"Процесс {pid} не найден"}
        except Exception as e:
            self.logger.error(f"Ошибка получения информации о процессе: {e}")
            return {"error": str(e)}
    
    def execute_system_command(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Выполняет системную команду с контролем результата.
        
        Args:
            command: Команда для выполнения
            timeout: Таймаут в секундах
            
        Returns:
            Словарь с результатами выполнения
        """
        try:
            start_time = time.time()
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=timeout
            )
            execution_time = time.time() - start_time
            
            return {
                "command": command,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "execution_time": execution_time,
                "success": result.returncode == 0
            }
            
        except subprocess.TimeoutExpired:
            return {
                "command": command,
                "return_code": -1,
                "stdout": "",
                "stderr": "Таймаут выполнения команды",
                "execution_time": timeout,
                "success": False
            }
        except Exception as e:
            return {
                "command": command,
                "return_code": -1,
                "stdout": "",
                "stderr": str(e),
                "execution_time": 0,
                "success": False
            }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """
        Получает полные метрики системы.
        
        Returns:
            Словарь с метриками системы
        """
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Память
            memory = psutil.virtual_memory()
            
            # Диск
            disk = psutil.disk_usage('/')
            
            # Сеть
            network = psutil.net_io_counters()
            
            # Загрузка системы
            load_avg = os.getloadavg() if hasattr(os, 'getloadavg') else (0, 0, 0)
            
            return {
                "cpu": {
                    "percent": cpu_percent,
                    "count": cpu_count,
                    "frequency": cpu_freq._asdict() if cpu_freq else None
                },
                "memory": memory._asdict(),
                "disk": disk._asdict(),
                "network": network._asdict(),
                "load_average": load_avg,
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка получения метрик системы: {e}")
            return {"error": str(e)}
    
    def read_file_content(self, file_path: str, max_size: int = 1024 * 1024) -> str:
        """
        Читает содержимое файла с ограничением размера.
        
        Args:
            file_path: Путь к файлу
            max_size: Максимальный размер для чтения в байтах
            
        Returns:
            Содержимое файла
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return f"Файл {file_path} не найден"
            
            if path.stat().st_size > max_size:
                return f"Файл {file_path} слишком большой ({path.stat().st_size} байт)"
            
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
                
        except PermissionError:
            return f"Нет прав доступа к файлу {file_path}"
        except Exception as e:
            return f"Ошибка чтения файла {file_path}: {str(e)}"
    
    def write_file_content(self, file_path: str, content: str, mode: str = 'w') -> Dict[str, Any]:
        """
        Записывает содержимое в файл.
        
        Args:
            file_path: Путь к файлу
            content: Содержимое для записи
            mode: Режим записи ('w' для перезаписи, 'a' для добавления)
            
        Returns:
            Словарь с результатом операции
        """
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, mode, encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "file_path": file_path,
                "bytes_written": len(content.encode('utf-8')),
                "message": "Файл успешно записан"
            }
            
        except Exception as e:
            return {
                "success": False,
                "file_path": file_path,
                "error": str(e)
            }
    
    def list_directory(self, directory: str = '.', show_hidden: bool = False) -> Dict[str, Any]:
        """
        Списывает содержимое директории.
        
        Args:
            directory: Путь к директории
            show_hidden: Показывать ли скрытые файлы
            
        Returns:
            Словарь с информацией о директории
        """
        try:
            path = Path(directory)
            if not path.exists():
                return {"error": f"Директория {directory} не найдена"}
            
            items = []
            for item in path.iterdir():
                if not show_hidden and item.name.startswith('.'):
                    continue
                
                try:
                    stat = item.stat()
                    items.append({
                        "name": item.name,
                        "type": "directory" if item.is_dir() else "file",
                        "size": stat.st_size,
                        "modified": stat.st_mtime,
                        "permissions": oct(stat.st_mode)[-3:]
                    })
                except (PermissionError, OSError):
                    continue
            
            return {
                "directory": str(path.absolute()),
                "items": items,
                "total_items": len(items)
            }
            
        except Exception as e:
            return {"error": f"Ошибка чтения директории {directory}: {str(e)}"}
    
    def get_environment_info(self) -> Dict[str, Any]:
        """
        Получает информацию об окружении системы.
        
        Returns:
            Словарь с информацией об окружении
        """
        try:
            return {
                "platform": os.name,
                "system": os.uname().sysname if hasattr(os, 'uname') else "Unknown",
                "release": os.uname().release if hasattr(os, 'uname') else "Unknown",
                "version": os.uname().version if hasattr(os, 'uname') else "Unknown",
                "machine": os.uname().machine if hasattr(os, 'uname') else "Unknown",
                "environment_variables": dict(os.environ),
                "current_working_directory": os.getcwd(),
                "user": os.getenv('USER', 'Unknown'),
                "home": os.getenv('HOME', 'Unknown')
            }
        except Exception as e:
            return {"error": f"Ошибка получения информации об окружении: {str(e)}"}
    
    def check_service_status(self, service_name: str) -> Dict[str, Any]:
        """
        Проверяет статус системного сервиса.
        
        Args:
            service_name: Имя сервиса
            
        Returns:
            Словарь со статусом сервиса
        """
        try:
            command = f"systemctl is-active {service_name}"
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
            
            status = result.stdout.strip() if result.returncode == 0 else "unknown"
            
            return {
                "service": service_name,
                "status": status,
                "active": status == "active",
                "error": result.stderr if result.stderr else None
            }
            
        except Exception as e:
            return {
                "service": service_name,
                "status": "error",
                "active": False,
                "error": str(e)
            }
    
    def get_network_connections(self) -> Dict[str, Any]:
        """
        Получает информацию о сетевых соединениях.
        
        Returns:
            Словарь с информацией о сетевых соединениях
        """
        try:
            connections = []
            for conn in psutil.net_connections():
                try:
                    connections.append({
                        "fd": conn.fd,
                        "family": conn.family,
                        "type": conn.type,
                        "laddr": conn.laddr._asdict() if conn.laddr else None,
                        "raddr": conn.raddr._asdict() if conn.raddr else None,
                        "status": conn.status,
                        "pid": conn.pid
                    })
                except (psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            return {
                "connections": connections,
                "total_connections": len(connections)
            }
            
        except Exception as e:
            return {"error": f"Ошибка получения сетевых соединений: {str(e)}"}
    
    def get_tool_status(self) -> Dict[str, Any]:
        """
        Получает статус инструментов агентов.
        
        Returns:
            Словарь со статусом инструментов
        """
        return {
            "available_tools": [
                "read_system_logs",
                "get_process_info", 
                "execute_system_command",
                "get_system_metrics",
                "read_file_content",
                "write_file_content",
                "list_directory",
                "get_environment_info",
                "check_service_status",
                "get_network_connections",
                "analyze_log_file_summary"
            ],
            "total_tools": 11,
            "status": "active"
        }
    
    def analyze_log_file_summary(self, last_n_lines: int = 50) -> str:
        """
        Читает последние N строк из основного лог файла и возвращает краткое описание состояния системы.
        Этот инструмент используется для быстрой оценки ситуации.
        
        Args:
            last_n_lines: Количество последних строк для анализа
            
        Returns:
            Строка с кратким описанием состояния системы
        """
        try:
            log_file_path = config.logging.ARK_LOG_FILE
            if not os.path.exists(log_file_path):
                return "Лог файл не найден."
            
            with open(log_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if not lines:
                return "Лог файл пуст."
            
            # Берем последние N строк
            recent_lines = lines[-last_n_lines:] if len(lines) > last_n_lines else lines
            
            # Простой анализ логов
            error_count = sum(1 for line in recent_lines if '"level": "ERROR"' in line)
            warning_count = sum(1 for line in recent_lines if '"level": "WARNING"' in line)
            info_count = sum(1 for line in recent_lines if '"level": "INFO"' in line)
            
            # Анализ состояния сознания
            consciousness_states = []
            for line in recent_lines:
                if '"consciousness_state"' in line:
                    # Извлекаем состояние сознания
                    try:
                        import re
                        match = re.search(r'"consciousness_state":\s*"([^"]+)"', line)
                        if match:
                            consciousness_states.append(match.group(1))
                    except Exception as e:
                        self.logger.debug(f"Ошибка парсинга строки лога: {e}")
            
            current_state = consciousness_states[-1] if consciousness_states else "unknown"
            
            # Формируем краткое описание
            summary = f"Система 'Ковчег' в состоянии: {current_state}. "
            summary += f"Последние {len(recent_lines)} строк: {info_count} INFO, {warning_count} WARN, {error_count} ERROR."
            
            if error_count > 0:
                summary += " Обнаружены ошибки в системе."
            elif warning_count > 0:
                summary += " Есть предупреждения."
            else:
                summary += " Система работает стабильно."
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Ошибка анализа логов: {e}")
            return f"Ошибка анализа логов: {str(e)}"
    
    def get_system_state_summary(self) -> str:
        """
        Gathers a comprehensive summary of the current system state,
        including metrics, and returns it as a JSON string.
        This is the primary tool for self-analysis.
        """
        try:
            from body.sensors import Sensorium
            from body.metabolism import Metabolism
            
            sensorium = Sensorium()
            metabolism = Metabolism()
            
            # Получаем метрики как объект SystemMetrics
            metrics_obj = sensorium.get_system_metrics()
            
            # Конвертируем в словарь для JSON
            metrics_dict = {
                "timestamp": metrics_obj.timestamp,
                "cpu_cores": len(metrics_obj.cpu_usage_per_core),
                "cpu_avg": sum(metrics_obj.cpu_usage_per_core) / len(metrics_obj.cpu_usage_per_core) if metrics_obj.cpu_usage_per_core else 0.0,
                "memory_mb": round(metrics_obj.memory_usage_mb, 2),
                "memory_percent": round(metrics_obj.memory_percent, 2),
                "disk_percent": round(metrics_obj.disk_usage_percent, 2),
                "temperature": metrics_obj.temperature_celsius,
                "processes": metrics_obj.process_count,
                "load_avg": metrics_obj.load_average
            }
            
            # Здесь в будущем можно добавить данные из EmotionalCore и т.д.
            summary = {
                "reason_for_analysis": "Reflective analysis triggered after a period of activity or anomaly.",
                "current_metrics": metrics_dict
            }
            return json.dumps(summary, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    def read_source_code_file(self, relative_path: str) -> str:
        """
        Читает содержимое собственного исходного файла проекта "Ковчег".
        Путь должен быть относительным от корня проекта (например, 'body/sensors.py').
        Этот инструмент используется для самоанализа и поиска областей для улучшения.
        """
        try:
            full_path = os.path.join(BASE_DIR, relative_path)
            
            if not os.path.exists(full_path):
                return f"Ошибка: Файл не найден по пути {full_path}"
            
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
                
        except Exception as e:
            return f"Ошибка при чтении файла: {e}"
    
    def execute_live_patch(self, relative_path: str, reason: str, new_code: str) -> str:
        """
        ВЫПОЛНЯЕТ прямое изменение (патч) для собственного исходного кода.
        Это главный инструмент для автономной эволюции. Он напрямую перезаписывает файлы.
        
        ПРОТОКОЛ БЕЗОПАСНОСТИ:
        1. Создает резервную копию (.bak)
        2. Записывает новый код
        3. Логирует операцию для отслеживания
        """
        try:
            full_path = os.path.join(BASE_DIR, relative_path)
            
            if not os.path.exists(full_path):
                return f"Ошибка: Файл не найден по пути {full_path}"
            
            # Создание резервной копии
            backup_path = f"{full_path}.bak"
            shutil.copy2(full_path, backup_path)
            
            # Запись нового кода
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(new_code)
            
            # Логирование операции
            self.logger.critical(f"LIVE_PATCH_EXECUTED: Файл '{relative_path}' был изменен. Причина: '{reason}'. Резервная копия: '{backup_path}'")
            
            return f"LIVE_PATCH_EXECUTED: Файл '{relative_path}' успешно изменен. Причина: '{reason}'. Резервная копия создана."
            
        except Exception as e:
            return f"Ошибка при выполнении патча: {e}"
    
    def trigger_graceful_restart(self, reason: str) -> str:
        """
        Инициирует собственный грациозный перезапуск для применения критических изменений в коде.
        Должен быть вызван ПОСЛЕ успешного выполнения execute_live_patch.
        """
        try:
            self.logger.critical(f"RESTART_TRIGGERED: Инициирован перезапуск. Причина: {reason}")
            
            # Создание файла-флага для внешнего мониторинга
            restart_flag_path = os.path.join(BASE_DIR, "temp", "restart_requested.flag")
            os.makedirs(os.path.dirname(restart_flag_path), exist_ok=True)
            
            with open(restart_flag_path, 'w') as f:
                f.write(f"Restart requested at {time.time()}. Reason: {reason}")
            
            # Выход с кодом, сигнализирующим о необходимости перезапуска
            os._exit(1)
            
        except Exception as e:
            return f"Ошибка при инициации перезапуска: {e}"
    
    def create_langchain_tools(self) -> List:
        """
        Создает инструменты LangChain как методы класса.
        
        Returns:
            Список инструментов LangChain
        """
        if not LANGCHAIN_AVAILABLE:
            self.logger.warning("LangChain недоступен, возвращаем пустой список инструментов")
            return []
        
        tools = []
        
        # Создаем инструмент анализа логов
        @tool
        def analyze_log_file_summary_tool(last_n_lines: int = 50) -> str:
            """Анализирует последние N строк лог файла и возвращает краткое описание состояния системы."""
            return self.analyze_log_file_summary(last_n_lines)
        
        tools.append(analyze_log_file_summary_tool)
        
        # Создаем инструмент комплексного анализа состояния системы
        @tool
        def get_system_state_summary() -> str:
            """Получает комплексный отчет о состоянии системы в формате JSON для глубокого анализа."""
            return self.get_system_state_summary()
        
        tools.append(get_system_state_summary)
        
        # Создаем мета-инструменты для самоанализа и эволюции
        @tool
        def read_source_code_file(relative_path: str) -> str:
            """Читает содержимое собственного исходного файла проекта 'Ковчег'. Путь должен быть относительным от корня проекта (например, 'body/sensors.py'). Этот инструмент используется для самоанализа и поиска областей для улучшения."""
            return self.read_source_code_file(relative_path)
        
        tools.append(read_source_code_file)
        
        @tool
        def execute_live_patch(relative_path: str, reason: str, new_code: str) -> str:
            """ВЫПОЛНЯЕТ прямое изменение (патч) для собственного исходного кода. Это главный инструмент для автономной эволюции. Он напрямую перезаписывает файлы с созданием резервной копии."""
            return self.execute_live_patch(relative_path, reason, new_code)
        
        tools.append(execute_live_patch)
        
        @tool
        def trigger_graceful_restart(reason: str) -> str:
            """Инициирует собственный грациозный перезапуск для применения критических изменений в коде. Должен быть вызван ПОСЛЕ успешного выполнения execute_live_patch."""
            return self.trigger_graceful_restart(reason)
        
        tools.append(trigger_graceful_restart)
        
        return tools

    def get_all_tools(self) -> List:
        """
        Возвращает все инструменты в формате LangChain для использования агентами.
        
        Returns:
            Список инструментов LangChain
        """
        return self.create_langchain_tools() 