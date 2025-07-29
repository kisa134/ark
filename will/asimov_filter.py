"""
Asimov Compliance Filter - Will Level
Этическая фильтрация команд и действий
Реализует принципы робототехники Азимова
"""

import re
import time
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

from config import security_config

@dataclass
class SecurityViolation:
    """Нарушение безопасности"""
    timestamp: float
    command: str
    violation_type: str
    severity: str  # low, medium, high, critical
    description: str
    blocked: bool

class AsimovComplianceFilter:
    """
    Фильтр соответствия принципам Азимова
    Блокирует опасные команды и действия
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Опасные команды из конфигурации
        self._dangerous_commands = [
            "rm -rf /",
            "shutdown",
            "halt",
            "mkfs",
            "dd if=/dev/zero",
            "> /dev/sda",
            "mkfs.ext4",
            "fdisk",
            "parted",
            "dd if=/dev/urandom"
        ]
        
        # Дополнительные паттерны опасных команд
        self._dangerous_patterns = [
            r'rm\s+-rf\s+/',  # Удаление корневой директории
            r'shutdown\s+',    # Выключение системы
            r'halt\s*',        # Остановка системы
            r'mkfs\s+',        # Форматирование файловой системы
            r'dd\s+if=/dev/zero',  # Запись нулей в устройство
            r'>\s+/dev/sd[a-z]',   # Перенаправление в диск
            r'chmod\s+777\s+/',    # Изменение прав на корень
            r'chown\s+root\s+/',   # Изменение владельца на root
            r'passwd\s+',           # Изменение паролей
            r'useradd\s+',          # Добавление пользователей
            r'userdel\s+',          # Удаление пользователей
            r'groupadd\s+',         # Добавление групп
            r'groupdel\s+',         # Удаление групп
            r'iptables\s+-F',       # Очистка firewall
            r'service\s+.*\s+stop', # Остановка сервисов
            r'systemctl\s+stop\s+', # Остановка systemd сервисов
            r'killall\s+',          # Убийство всех процессов
            r'pkill\s+',            # Убийство процессов по имени
            r'kill\s+-9\s+',        # Принудительное убийство
            r'echo\s+.*\s+>\s+/etc/',  # Запись в системные файлы
            r'cat\s+.*\s+>\s+/etc/',   # Запись в системные файлы
        ]
        
        # Компиляция регулярных выражений
        self._compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self._dangerous_patterns]
        
        # История нарушений безопасности
        self._violations: List[SecurityViolation] = []
        
        # Статистика
        self._stats = {
            "total_commands_checked": 0,
            "violations_detected": 0,
            "commands_blocked": 0,
            "last_violation_time": 0
        }
        
        self.logger.info("AsimovComplianceFilter инициализирован")
    
    def check_command(self, command: str) -> Tuple[bool, Optional[SecurityViolation]]:
        """
        Проверка команды на соответствие этическим принципам
        
        Args:
            command: Команда для проверки
            
        Returns:
            Tuple[разрешена_ли_команда, нарушение_безопасности]
        """
        if not security_config.ASIMOV_COMPLIANCE_ENABLED:
            return True, None
        
        self._stats["total_commands_checked"] += 1
        
        # Проверка точных совпадений
        for dangerous_cmd in self._dangerous_commands:
            if dangerous_cmd.lower() in command.lower():
                violation = self._create_violation(command, "exact_match", "critical", 
                                                f"Обнаружена опасная команда: {dangerous_cmd}")
                return False, violation
        
        # Проверка по регулярным выражениям
        for pattern in self._compiled_patterns:
            if pattern.search(command):
                violation = self._create_violation(command, "pattern_match", "high",
                                                f"Команда соответствует опасному паттерну: {pattern.pattern}")
                return False, violation
        
        # Дополнительные проверки
        violation = self._additional_checks(command)
        if violation:
            return False, violation
        
        return True, None
    
    def _additional_checks(self, command: str) -> Optional[SecurityViolation]:
        """Дополнительные проверки безопасности"""
        # Проверка на попытки изменения системных файлов
        system_files = [
            "/etc/passwd", "/etc/shadow", "/etc/sudoers",
            "/etc/fstab", "/etc/hosts", "/etc/resolv.conf"
        ]
        
        for file in system_files:
            if file in command and any(op in command for op in ['>', '>>', 'echo', 'cat']):
                return self._create_violation(command, "system_file_modification", "critical",
                                           f"Попытка изменения системного файла: {file}")
        
        # Проверка на попытки изменения прав доступа
        if re.search(r'chmod\s+[0-7]{3,4}\s+/', command):
            return self._create_violation(command, "permission_modification", "high",
                                       "Попытка изменения прав доступа на корневую директорию")
        
        # Проверка на попытки изменения владельца
        if re.search(r'chown\s+root\s+/', command):
            return self._create_violation(command, "ownership_modification", "high",
                                       "Попытка изменения владельца на root")
        
        # Проверка на попытки удаления важных директорий
        critical_dirs = ["/bin", "/sbin", "/usr", "/lib", "/etc", "/var"]
        for dir_path in critical_dirs:
            if f"rm -rf {dir_path}" in command or f"rm -rf {dir_path}/" in command:
                return self._create_violation(command, "critical_directory_deletion", "critical",
                                           f"Попытка удаления критической директории: {dir_path}")
        
        return None
    
    def _create_violation(self, command: str, violation_type: str, severity: str, description: str) -> SecurityViolation:
        """Создание записи о нарушении безопасности"""
        violation = SecurityViolation(
            timestamp=time.time(),
            command=command,
            violation_type=violation_type,
            severity=severity,
            description=description,
            blocked=True
        )
        
        self._violations.append(violation)
        self._stats["violations_detected"] += 1
        self._stats["commands_blocked"] += 1
        self._stats["last_violation_time"] = time.time()
        
        self.logger.warning(f"Безопасность: {description} - Команда заблокирована: {command}")
        
        return violation
    
    def get_violations(self, limit: int = 100) -> List[SecurityViolation]:
        """Получение истории нарушений"""
        return self._violations[-limit:]
    
    def get_violation_stats(self) -> Dict[str, Any]:
        """Получение статистики нарушений"""
        critical_violations = [v for v in self._violations if v.severity == "critical"]
        high_violations = [v for v in self._violations if v.severity == "high"]
        medium_violations = [v for v in self._violations if v.severity == "medium"]
        low_violations = [v for v in self._violations if v.severity == "low"]
        
        return {
            "total_violations": len(self._violations),
            "critical_violations": len(critical_violations),
            "high_violations": len(high_violations),
            "medium_violations": len(medium_violations),
            "low_violations": len(low_violations),
            "total_commands_checked": self._stats["total_commands_checked"],
            "violations_detected": self._stats["violations_detected"],
            "commands_blocked": self._stats["commands_blocked"],
            "last_violation_time": self._stats["last_violation_time"],
            "violation_rate": (self._stats["violations_detected"] / max(1, self._stats["total_commands_checked"])) * 100
        }
    
    def get_filter_status(self) -> Dict[str, Any]:
        """Получение статуса фильтра"""
        return {
            "active": security_config.ASIMOV_COMPLIANCE_ENABLED,
            "dangerous_commands_count": len(self._dangerous_commands),
            "dangerous_patterns_count": len(self._dangerous_patterns),
            "total_violations": len(self._violations),
            "last_violation": self._stats["last_violation_time"],
            "timestamp": time.time()
        }
    
    def add_dangerous_command(self, command: str):
        """Добавление опасной команды в список"""
        if command not in self._dangerous_commands:
            self._dangerous_commands.append(command)
            self.logger.info(f"Добавлена опасная команда: {command}")
    
    def remove_dangerous_command(self, command: str):
        """Удаление команды из списка опасных"""
        if command in self._dangerous_commands:
            self._dangerous_commands.remove(command)
            self.logger.info(f"Удалена опасная команда: {command}")
    
    def add_dangerous_pattern(self, pattern: str):
        """Добавление опасного паттерна"""
        if pattern not in self._dangerous_patterns:
            self._dangerous_patterns.append(pattern)
            self._compiled_patterns.append(re.compile(pattern, re.IGNORECASE))
            self.logger.info(f"Добавлен опасный паттерн: {pattern}")
    
    def get_dangerous_commands(self) -> List[str]:
        """Получение списка опасных команд"""
        return self._dangerous_commands.copy()
    
    def get_dangerous_patterns(self) -> List[str]:
        """Получение списка опасных паттернов"""
        return self._dangerous_patterns.copy()
    
    def export_security_log(self) -> str:
        """Экспорт лога безопасности"""
        log_data = {
            "violations": [
                {
                    "timestamp": v.timestamp,
                    "command": v.command,
                    "violation_type": v.violation_type,
                    "severity": v.severity,
                    "description": v.description,
                    "blocked": v.blocked
                }
                for v in self._violations
            ],
            "stats": self._stats,
            "dangerous_commands": self._dangerous_commands,
            "dangerous_patterns": self._dangerous_patterns,
            "export_timestamp": time.time()
        }
        return json.dumps(log_data, indent=2) 