"""
ConsciousnessMonitor - мониторинг сознания и производительности
Реализует структурированное JSON-логирование в /var/log/ark.log
"""

import json
import time
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass, asdict
import threading

from config import config_instance as config


@dataclass
class ConsciousnessMetrics:
    """Метрики сознания"""
    timestamp: float
    consciousness_state: str
    emotional_state: Dict[str, float]
    system_health: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    security_status: Dict[str, Any]


class ConsciousnessMonitor:
    """
    ConsciousnessMonitor - мониторинг сознания и производительности
    Реализует структурированное JSON-логирование
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Настройка JSON логгера
        self._setup_json_logger()
        
        # История метрик
        self._metrics_history: List[ConsciousnessMetrics] = []
        
        # Поток мониторинга
        self._monitoring_thread: Optional[threading.Thread] = None
        self._stop_monitoring = threading.Event()
        
        # Компоненты для мониторинга
        self._body = None
        self._mind = None
        self._psyche = None
        self._will = None
        
        self.logger.info("ConsciousnessMonitor инициализирован")
    
    def _setup_json_logger(self):
        """Настройка JSON логгера"""
        try:
            # Создание директории для логов
            log_dir = Path("logs")
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # Настройка файлового обработчика
            file_handler = logging.FileHandler("logs/ark.log")
            file_handler.setLevel(logging.INFO)
            
            # JSON форматтер
            class JSONFormatter(logging.Formatter):
                def format(self, record):
                    log_entry = {
                        "timestamp": time.time(),
                        "level": record.levelname,
                        "module": record.module,
                        "function": record.funcName,
                        "message": record.getMessage(),
                        "context": getattr(record, 'context', {})
                    }
                    return json.dumps(log_entry)
            
            file_handler.setFormatter(JSONFormatter())
            
            # Добавление обработчика к логгеру
            self.logger.addHandler(file_handler)
            self.logger.setLevel(logging.INFO)
            
        except Exception as e:
            print(f"Ошибка настройки JSON логгера: {e}")
    
    def set_components(self, body, mind, psyche, will):
        """Установка компонентов для мониторинга"""
        self._body = body
        self._mind = mind
        self._psyche = psyche
        self._will = will
        self.logger.info("Компоненты для мониторинга установлены")
    
    def start_monitoring(self):
        """Запуск мониторинга сознания"""
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            return
        
        self._stop_monitoring.clear()
        self._monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self._monitoring_thread.start()
        self.logger.info("Мониторинг сознания запущен")
    
    def stop_monitoring(self):
        """Остановка мониторинга сознания"""
        self._stop_monitoring.set()
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=5)
        self.logger.info("Мониторинг сознания остановлен")
    
    def _monitoring_loop(self):
        """Основной цикл мониторинга"""
        while not self._stop_monitoring.is_set():
            try:
                # Сбор метрик от всех компонентов
                metrics = self._collect_metrics()
                
                # Сохранение метрик
                self._save_metrics(metrics)
                
                # Логирование метрик
                self._log_metrics(metrics)
                
                # Проверка критических состояний
                self._check_critical_states(metrics)
                
                # Пауза между измерениями
                time.sleep(10)  # 10 секунд между измерениями
                
            except Exception as e:
                self.logger.error(f"Ошибка в цикле мониторинга: {e}")
                time.sleep(30)  # Увеличенная пауза при ошибке
    
    def _collect_metrics(self) -> ConsciousnessMetrics:
        """Сбор метрик от всех компонентов"""
        # Базовые метрики
        consciousness_state = "unknown"
        emotional_state = {}
        system_health = {}
        performance_metrics = {}
        security_status = {}
        
        try:
            # Метрики от "Разума"
            if self._mind and hasattr(self._mind, 'consciousness_core'):
                consciousness_state = self._mind.consciousness_core.get_current_state().value
                performance_metrics["consciousness_stats"] = self._mind.consciousness_core.get_consciousness_stats()
            
            # Метрики от "Личности"
            if self._psyche and hasattr(self._psyche, 'emotional_core'):
                emotional_state = self._psyche.emotional_core.get_current_emotional_state()
                performance_metrics["emotional_summary"] = self._psyche.emotional_core.get_emotional_summary()
            
            # Метрики от "Тела"
            if self._body and hasattr(self._body, 'sensorium'):
                system_metrics = self._body.sensorium.get_system_metrics()
                system_health = {
                    "cpu_usage": sum(system_metrics.cpu_usage_per_core) / len(system_metrics.cpu_usage_per_core),
                    "memory_usage": system_metrics.memory_percent,
                    "disk_usage": system_metrics.disk_usage_percent,
                    "temperature": system_metrics.temperature_celsius,
                    "process_count": system_metrics.process_count
                }
                performance_metrics["system_metrics"] = self._body.sensorium.get_metrics_json()
            
            # Метрики от "Воли"
            if self._will and hasattr(self._will, 'tool_executor'):
                security_status = self._will.tool_executor.get_executor_status()
                performance_metrics["security_stats"] = self._will.tool_executor.get_executor_stats()
            
        except Exception as e:
            self.logger.error(f"Ошибка сбора метрик: {e}")
        
        return ConsciousnessMetrics(
            timestamp=time.time(),
            consciousness_state=consciousness_state,
            emotional_state=emotional_state,
            system_health=system_health,
            performance_metrics=performance_metrics,
            security_status=security_status
        )
    
    def _save_metrics(self, metrics: ConsciousnessMetrics):
        """Сохранение метрик в историю"""
        self._metrics_history.append(metrics)
        
        # Ограничение размера истории
        if len(self._metrics_history) > 1000:
            self._metrics_history = self._metrics_history[-1000:]
    
    def _log_metrics(self, metrics: ConsciousnessMetrics):
        """Логирование метрик в JSON формате"""
        log_entry = {
            "timestamp": metrics.timestamp,
            "level": "INFO",
            "module": "consciousness_monitor",
            "function": "log_metrics",
            "message": "Consciousness metrics collected",
            "context": {
                "consciousness_state": metrics.consciousness_state,
                "emotional_dominant": self._get_dominant_emotion(metrics.emotional_state),
                "system_health_score": self._calculate_health_score(metrics.system_health),
                "security_violations": metrics.security_status.get("asimov_filter_status", {}).get("violations_detected", 0)
            }
        }
        
        self.logger.info("", extra={"context": log_entry["context"]})
    
    def _check_critical_states(self, metrics: ConsciousnessMetrics):
        """Проверка критических состояний"""
        # Проверка системного здоровья
        if metrics.system_health:
            cpu_usage = metrics.system_health.get("cpu_usage", 0)
            memory_usage = metrics.system_health.get("memory_usage", 0)
            
            if cpu_usage > 90:
                self.logger.warning("", extra={"context": {"critical_state": "high_cpu_usage", "value": cpu_usage}})
            
            if memory_usage > 90:
                self.logger.warning("", extra={"context": {"critical_state": "high_memory_usage", "value": memory_usage}})
        
        # Проверка безопасности
        if metrics.security_status:
            violations = metrics.security_status.get("asimov_filter_status", {}).get("violations_detected", 0)
            if violations > 10:
                self.logger.warning("", extra={"context": {"critical_state": "high_security_violations", "value": violations}})
    
    def _get_dominant_emotion(self, emotional_state: Dict[str, Any]) -> Optional[str]:
        """Получение доминирующей эмоции"""
        if not emotional_state:
            return None
        
        # Фильтруем только числовые значения
        numeric_emotions = {}
        for emotion, value in emotional_state.items():
            if isinstance(value, (int, float)):
                numeric_emotions[emotion] = float(value)
        
        if not numeric_emotions:
            return None
        
        max_emotion = max(numeric_emotions.items(), key=lambda x: x[1])
        return max_emotion[0] if max_emotion[1] > 0.3 else None
    
    def _calculate_health_score(self, system_health: Dict[str, Any]) -> float:
        """Расчет оценки здоровья системы"""
        if not system_health:
            return 0.0
        
        scores = []
        
        # CPU score
        cpu_usage = system_health.get("cpu_usage", 0)
        if isinstance(cpu_usage, (int, float)):
            scores.append(max(0.0, 1.0 - (float(cpu_usage) / 100.0)))
        
        # Memory score
        memory_usage = system_health.get("memory_usage", 0)
        if isinstance(memory_usage, (int, float)):
            scores.append(max(0.0, 1.0 - (float(memory_usage) / 100.0)))
        
        # Disk score
        disk_usage = system_health.get("disk_usage", 0)
        if isinstance(disk_usage, (int, float)):
            scores.append(max(0.0, 1.0 - (float(disk_usage) / 100.0)))
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def get_metrics_history(self, limit: int = 100) -> List[ConsciousnessMetrics]:
        """Получение истории метрик"""
        return self._metrics_history[-limit:]
    
    def get_current_metrics(self) -> Optional[ConsciousnessMetrics]:
        """Получение текущих метрик"""
        if not self._metrics_history:
            return None
        return self._metrics_history[-1]
    
    def get_monitor_status(self) -> Dict[str, Any]:
        """Получение статуса монитора"""
        return {
            "active": self._monitoring_thread and self._monitoring_thread.is_alive(),
            "metrics_history_size": len(self._metrics_history),
            "log_file": str(config.system.ARK_LOG_FILE),
            "components_configured": all([
                self._body is not None,
                self._mind is not None,
                self._psyche is not None,
                self._will is not None
            ])
        }
    
    def export_metrics(self, format: str = "json") -> str:
        """Экспорт метрик"""
        if format == "json":
            metrics_data = [asdict(metric) for metric in self._metrics_history[-100:]]
            return json.dumps(metrics_data, indent=2, default=str)
        else:
            raise ValueError(f"Неподдерживаемый формат: {format}")
    
    def get_consciousness_summary(self) -> Dict[str, Any]:
        """Получение краткого описания сознания"""
        current_metrics = self.get_current_metrics()
        if not current_metrics:
            return {"status": "no_metrics_available"}
        
        return {
            "consciousness_state": current_metrics.consciousness_state,
            "dominant_emotion": self._get_dominant_emotion(current_metrics.emotional_state),
            "system_health_score": self._calculate_health_score(current_metrics.system_health),
            "security_violations": current_metrics.security_status.get("asimov_filter_status", {}).get("violations_detected", 0),
            "monitoring_active": self._monitoring_thread and self._monitoring_thread.is_alive(),
            "metrics_collected": len(self._metrics_history)
        } 