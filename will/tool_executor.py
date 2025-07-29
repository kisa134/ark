"""
ToolExecutor - выполнение инструментов с этическими проверками
Интегрирует AsimovComplianceFilter с выполнением команд
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
import time
import subprocess

from config import config
from .asimov_filter import AsimovComplianceFilter


class ToolExecutor:
    """
    ToolExecutor - выполнение инструментов с этическими проверками
    Интегрирует AsimovComplianceFilter с выполнением команд
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Инициализация этического фильтра
        self.asimov_filter = AsimovComplianceFilter()
        
        # История выполненных команд
        self._execution_history = []
        
        # Статистика
        self._stats = {
            "total_commands": 0,
            "blocked_commands": 0,
            "executed_commands": 0,
            "last_execution_time": 0
        }
    
    def execute_command(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Выполнение команды с этической проверкой
        
        Args:
            command: Команда для выполнения
            timeout: Таймаут в секундах
            
        Returns:
            Результат выполнения команды
        """
        self._stats["total_commands"] += 1
        
        # Проверка через AsimovComplianceFilter
        is_allowed, violation = self.asimov_filter.check_command(command)
        
        if not is_allowed:
            self._stats["blocked_commands"] += 1
            self.logger.warning(f"Команда заблокирована: {command}")
            
            return {
                "command": command,
                "success": False,
                "blocked": True,
                "violation": violation.__dict__ if violation else None,
                "error": "Команда заблокирована этическим фильтром",
                "timestamp": time.time()
            }
        
        # Выполнение команды
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
            
            execution_result = {
                "command": command,
                "success": result.returncode == 0,
                "blocked": False,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "execution_time": execution_time,
                "timestamp": time.time()
            }
            
            self._stats["executed_commands"] += 1
            self._stats["last_execution_time"] = execution_result["timestamp"]
            
            # Сохранение в историю
            self._execution_history.append(execution_result)
            
            self.logger.info(f"Команда выполнена: {command} (код: {result.returncode})")
            
            return execution_result
            
        except subprocess.TimeoutExpired:
            self.logger.error(f"Таймаут выполнения команды: {command}")
            return {
                "command": command,
                "success": False,
                "blocked": False,
                "error": "Таймаут выполнения команды",
                "execution_time": timeout,
                "timestamp": time.time()
            }
        except Exception as e:
            self.logger.error(f"Ошибка выполнения команды {command}: {e}")
            return {
                "command": command,
                "success": False,
                "blocked": False,
                "error": str(e),
                "execution_time": 0,
                "timestamp": time.time()
            }
    
    def execute_safe_command(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Выполнение безопасной команды (без этических проверок)
        
        Args:
            command: Команда для выполнения
            timeout: Таймаут в секундах
            
        Returns:
            Результат выполнения команды
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
                "success": result.returncode == 0,
                "safe_mode": True,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "execution_time": execution_time,
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {
                "command": command,
                "success": False,
                "safe_mode": True,
                "error": str(e),
                "execution_time": 0,
                "timestamp": time.time()
            }
    
    def get_execution_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Получение истории выполнения команд"""
        return self._execution_history[-limit:]
    
    def get_executor_stats(self) -> Dict[str, Any]:
        """Получение статистики исполнителя"""
        return {
            "total_commands": self._stats["total_commands"],
            "blocked_commands": self._stats["blocked_commands"],
            "executed_commands": self._stats["executed_commands"],
            "block_rate": (self._stats["blocked_commands"] / self._stats["total_commands"] * 100) if self._stats["total_commands"] > 0 else 0,
            "last_execution_time": self._stats["last_execution_time"],
            "history_size": len(self._execution_history)
        }
    
    def get_executor_status(self) -> Dict[str, Any]:
        """Получение статуса исполнителя"""
        return {
            "active": True,
            "asimov_filter_enabled": config.security.ASIMOV_COMPLIANCE_ENABLED,
            "stats": self.get_executor_stats(),
            "asimov_filter_status": self.asimov_filter.get_filter_status(),
            "capabilities": [
                "execute_command",
                "execute_safe_command",
                "ethical_filtering",
                "command_history"
            ]
        }
    
    def get_recent_violations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Получение недавних нарушений безопасности"""
        violations = self.asimov_filter.get_violations(limit)
        return [violation.__dict__ for violation in violations]
    
    def export_execution_log(self) -> str:
        """Экспорт лога выполнения"""
        import json
        
        log_data = {
            "timestamp": time.time(),
            "executor_stats": self.get_executor_stats(),
            "asimov_filter_status": self.asimov_filter.get_filter_status(),
            "recent_executions": self._execution_history[-50:],
            "recent_violations": self.get_recent_violations(10)
        }
        
        return json.dumps(log_data, indent=2, default=str) 