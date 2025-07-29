"""
Актуаторы - система воздействия "тела"
Выполнение системных команд с полным контролем
"""

import subprocess
import psutil
import os
import signal
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import logging
import json
import time

from config import config


@dataclass
class CommandResult:
    """Результат выполнения команды"""
    command: str
    return_code: int
    stdout: str
    stderr: str
    execution_time: float
    success: bool
    pid: Optional[int] = None


class Actuator:
    """
    Актуатор - система воздействия "тела"
    Выполняет команды с контролем stdout, stderr и кодов возврата
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._active_processes: Dict[int, subprocess.Popen] = {}
        self._command_history: List[CommandResult] = []
    
    def execute_shell(self, command: str, timeout: int = 30, 
                     capture_output: bool = True) -> CommandResult:
        """
        Выполнение shell команды с полным контролем
        
        Args:
            command: Команда для выполнения
            timeout: Таймаут в секундах
            capture_output: Захватывать ли вывод
            
        Returns:
            CommandResult с результатами выполнения
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"Выполнение команды: {command}")
            
            # Выполнение команды
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE if capture_output else None,
                stderr=subprocess.PIPE if capture_output else None,
                text=True,
                preexec_fn=os.setsid  # Создание новой группы процессов
            )
            
            # Сохранение процесса для возможного управления
            self._active_processes[process.pid] = process
            
            try:
                # Ожидание завершения с таймаутом
                stdout, stderr = process.communicate(timeout=timeout)
                return_code = process.returncode
                success = return_code == 0
                
            except subprocess.TimeoutExpired:
                # Убийство процесса при таймауте
                self.logger.warning(f"Таймаут команды: {command}")
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                
                stdout, stderr = process.communicate()
                return_code = -1
                success = False
                
        except Exception as e:
            self.logger.error(f"Ошибка выполнения команды {command}: {e}")
            return CommandResult(
                command=command,
                return_code=-1,
                stdout="",
                stderr=str(e),
                execution_time=time.time() - start_time,
                success=False
            )
        
        finally:
            # Удаление из активных процессов
            if process.pid in self._active_processes:
                del self._active_processes[process.pid]
        
        execution_time = time.time() - start_time
        
        result = CommandResult(
            command=command,
            return_code=return_code,
            stdout=stdout or "",
            stderr=stderr or "",
            execution_time=execution_time,
            success=success,
            pid=process.pid
        )
        
        # Логирование результата
        self._log_command_result(result)
        
        # Сохранение в историю
        self._command_history.append(result)
        
        return result
    
    def execute_python(self, code: str, timeout: int = 30) -> CommandResult:
        """
        Выполнение Python кода
        
        Args:
            code: Python код для выполнения
            timeout: Таймаут в секундах
            
        Returns:
            CommandResult с результатами выполнения
        """
        command = f"python3 -c '{code}'"
        return self.execute_shell(command, timeout)
    
    def kill_process(self, pid: int, signal_type: str = "TERM") -> bool:
        """
        Убийство процесса
        
        Args:
            pid: ID процесса
            signal_type: Тип сигнала (TERM, KILL)
            
        Returns:
            True если процесс успешно убит
        """
        try:
            if signal_type == "TERM":
                os.kill(pid, signal.SIGTERM)
            elif signal_type == "KILL":
                os.kill(pid, signal.SIGKILL)
            else:
                raise ValueError(f"Неизвестный тип сигнала: {signal_type}")
            
            self.logger.info(f"Процесс {pid} убит сигналом {signal_type}")
            return True
            
        except ProcessLookupError:
            self.logger.warning(f"Процесс {pid} не найден")
            return False
        except Exception as e:
            self.logger.error(f"Ошибка убийства процесса {pid}: {e}")
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """Получение системной информации"""
        try:
            # Информация о системе
            uname_result = self.execute_shell("uname -a")
            cpu_info = self.execute_shell("lscpu | grep 'Model name'")
            memory_info = self.execute_shell("free -h")
            
            return {
                "system": uname_result.stdout.strip() if uname_result.success else "Unknown",
                "cpu": cpu_info.stdout.strip() if cpu_info.success else "Unknown",
                "memory": memory_info.stdout.strip() if memory_info.success else "Unknown"
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения системной информации: {e}")
            return {}
    
    def cleanup_processes(self) -> int:
        """
        Очистка всех активных процессов
        
        Returns:
            Количество убитых процессов
        """
        killed_count = 0
        
        for pid, process in list(self._active_processes.items()):
            try:
                if process.poll() is None:  # Процесс еще работает
                    os.killpg(os.getpgid(pid), signal.SIGTERM)
                    killed_count += 1
            except Exception as e:
                self.logger.error(f"Ошибка убийства процесса {pid}: {e}")
        
        self._active_processes.clear()
        return killed_count
    
    def get_active_processes(self) -> List[Dict[str, Any]]:
        """Получение списка активных процессов"""
        active = []
        
        for pid, process in self._active_processes.items():
            try:
                status = "running" if process.poll() is None else "finished"
                active.append({
                    "pid": pid,
                    "status": status,
                    "command": getattr(process, 'args', 'unknown')
                })
            except Exception as e:
                self.logger.error(f"Ошибка получения информации о процессе {pid}: {e}")
        
        return active
    
    def get_command_history(self, limit: int = 100) -> List[CommandResult]:
        """Получение истории команд"""
        return self._command_history[-limit:]
    
    def _log_command_result(self, result: CommandResult):
        """Логирование результата команды"""
        level = logging.INFO if result.success else logging.WARNING
        
        self.logger.log(level, 
            f"Команда: {result.command} | "
            f"Код: {result.return_code} | "
            f"Время: {result.execution_time:.2f}s | "
            f"Успех: {result.success}"
        )
        
        if result.stderr and not result.success:
            self.logger.error(f"Ошибка команды: {result.stderr}")
    
    def get_actuator_status(self) -> Dict[str, Any]:
        """Получение статуса актуатора"""
        return {
            "active_processes": len(self._active_processes),
            "command_history_size": len(self._command_history),
            "last_command": self._command_history[-1].command if self._command_history else None,
            "success_rate": self._calculate_success_rate()
        }
    
    def _calculate_success_rate(self) -> float:
        """Расчет процента успешных команд"""
        if not self._command_history:
            return 0.0
        
        successful = sum(1 for cmd in self._command_history if cmd.success)
        return (successful / len(self._command_history)) * 100 