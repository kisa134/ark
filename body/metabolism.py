"""
Цифровой метаболизм - система поддержания гомеостаза
Реализует парадигму "раздачи" (scatter paradigm) для управления потоками данных
"""

import time
import threading
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import logging
import json
from collections import deque

from config import config
from .sensors import Sensorium, SystemMetrics


class MetabolismState(Enum):
    """Состояния метаболизма"""
    NORMAL = "normal"
    STRESSED = "stressed"
    RECOVERY = "recovery"
    CRITICAL = "critical"


@dataclass
class MetabolismMetrics:
    """Метрики метаболизма"""
    timestamp: float
    state: MetabolismState
    energy_level: float  # 0.0 - 1.0
    stress_level: float  # 0.0 - 1.0
    resource_efficiency: float  # 0.0 - 1.0
    homeostasis_score: float  # 0.0 - 1.0


class DigitalMetabolism:
    """
    Цифровой метаболизм - система поддержания гомеостаза
    Реализует парадигму "раздачи" для управления ресурсами
    """
    
    def __init__(self, sensorium: Sensorium):
        self.logger = logging.getLogger(__name__)
        self.sensorium = sensorium
        
        # Состояние метаболизма
        self._current_state = MetabolismState.NORMAL
        self._energy_level = 1.0
        self._stress_level = 0.0
        self._resource_efficiency = 1.0
        
        # История метрик
        self._metrics_history: deque = deque(maxlen=1000)
        
        # Обработчики событий
        self._event_handlers: Dict[str, List[Callable]] = {
            "state_change": [],
            "stress_alert": [],
            "energy_low": [],
            "homeostasis_breach": []
        }
        
        # Поток мониторинга
        self._monitoring_thread: Optional[threading.Thread] = None
        self._stop_monitoring = threading.Event()
        
        # Параметры метаболизма
        self._metabolism_rate = 1.0  # Базовая скорость метаболизма
        self._recovery_rate = 0.1    # Скорость восстановления
        self._stress_threshold = 0.8  # Порог стресса
        self._energy_threshold = 0.2  # Порог низкой энергии
        
    def start_monitoring(self):
        """Запуск мониторинга метаболизма"""
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            return
        
        self._stop_monitoring.clear()
        self._monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self._monitoring_thread.start()
        self.logger.info("Мониторинг метаболизма запущен")
    
    def stop_monitoring(self):
        """Остановка мониторинга метаболизма"""
        self._stop_monitoring.set()
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=5)
        self.logger.info("Мониторинг метаболизма остановлен")
    
    def _monitoring_loop(self):
        """Основной цикл мониторинга метаболизма"""
        while not self._stop_monitoring.is_set():
            try:
                # Получение системных метрик
                system_metrics = self.sensorium.get_system_metrics()
                
                # Обновление метаболизма
                self._update_metabolism(system_metrics)
                
                # Проверка гомеостаза
                self._check_homeostasis(system_metrics)
                
                # Сохранение метрик
                self._save_metrics()
                
                # Пауза между измерениями
                time.sleep(5)  # 5 секунд между измерениями
                
            except Exception as e:
                self.logger.error(f"Ошибка в цикле мониторинга: {e}")
                time.sleep(10)  # Увеличенная пауза при ошибке
    
    def _update_metabolism(self, system_metrics: SystemMetrics):
        """Обновление состояния метаболизма на основе системных метрик"""
        # Расчет энергетического уровня
        if system_metrics.cpu_usage_per_core:
            cpu_avg = sum(system_metrics.cpu_usage_per_core) / len(system_metrics.cpu_usage_per_core)
        else:
            cpu_avg = 0.0  # Значение по умолчанию если нет данных CPU
        memory_pressure = system_metrics.memory_percent / 100.0
        
        # Энергия снижается при высокой нагрузке
        energy_drain = (cpu_avg / 100.0) * 0.1 + memory_pressure * 0.05
        self._energy_level = max(0.0, self._energy_level - energy_drain)
        
        # Стресс растет при критических условиях
        stress_factors = []
        if cpu_avg > 90:
            stress_factors.append(0.3)
        if system_metrics.memory_percent > 90:
            stress_factors.append(0.4)
        if system_metrics.temperature_celsius and system_metrics.temperature_celsius > 80:
            stress_factors.append(0.5)
        
        stress_increase = sum(stress_factors) * 0.1
        self._stress_level = min(1.0, self._stress_level + stress_increase)
        
        # Эффективность ресурсов
        self._resource_efficiency = 1.0 - (cpu_avg / 100.0) * 0.5 - memory_pressure * 0.3
        
        # Восстановление при нормальных условиях
        if cpu_avg < 50 and system_metrics.memory_percent < 70:
            self._energy_level = min(1.0, self._energy_level + self._recovery_rate * 0.1)
            self._stress_level = max(0.0, self._stress_level - self._recovery_rate * 0.05)
    
    def _check_homeostasis(self, system_metrics: SystemMetrics):
        """Проверка гомеостаза и генерация событий"""
        old_state = self._current_state
        
        # Определение нового состояния
        if self._stress_level > self._stress_threshold:
            self._current_state = MetabolismState.CRITICAL
        elif self._energy_level < self._energy_threshold:
            self._current_state = MetabolismState.STRESSED
        elif self._stress_level > 0.5:
            self._current_state = MetabolismState.RECOVERY
        else:
            self._current_state = MetabolismState.NORMAL
        
        # Генерация событий при изменении состояния
        if self._current_state != old_state:
            self._trigger_event("state_change", {
                "old_state": old_state.value,
                "new_state": self._current_state.value,
                "energy_level": self._energy_level,
                "stress_level": self._stress_level
            })
        
        # Проверка критических условий
        if self._stress_level > self._stress_threshold:
            self._trigger_event("stress_alert", {
                "stress_level": self._stress_level,
                "threshold": self._stress_threshold
            })
        
        if self._energy_level < self._energy_threshold:
            self._trigger_event("energy_low", {
                "energy_level": self._energy_level,
                "threshold": self._energy_threshold
            })
        
        # Проверка нарушения гомеостаза
        homeostasis_score = self._calculate_homeostasis_score(system_metrics)
        if homeostasis_score < 0.5:
            self._trigger_event("homeostasis_breach", {
                "score": homeostasis_score,
                "metrics": system_metrics
            })
    
    def _calculate_homeostasis_score(self, system_metrics: SystemMetrics) -> float:
        """Расчет оценки гомеостаза"""
        scores = []
        
        # CPU score
        if system_metrics.cpu_usage_per_core:
            cpu_avg = sum(system_metrics.cpu_usage_per_core) / len(system_metrics.cpu_usage_per_core)
            cpu_score = max(0.0, 1.0 - (cpu_avg / 100.0))
            scores.append(cpu_score)
        else:
            # Если нет данных CPU, используем нейтральную оценку
            scores.append(0.5)
        
        # Memory score
        memory_score = max(0.0, 1.0 - (system_metrics.memory_percent / 100.0))
        scores.append(memory_score)
        
        # Temperature score
        if system_metrics.temperature_celsius is not None:
            temp_score = max(0.0, 1.0 - (system_metrics.temperature_celsius / 100.0))
            scores.append(temp_score)
        
        # Energy score
        scores.append(self._energy_level)
        
        # Stress score (инвертированный)
        stress_score = 1.0 - self._stress_level
        scores.append(stress_score)
        
        # Проверка на пустой список scores
        if not scores:
            return 0.5  # Нейтральная оценка если нет данных
        
        return sum(scores) / len(scores)
    
    def _save_metrics(self):
        """Сохранение метрик метаболизма"""
        metrics = MetabolismMetrics(
            timestamp=time.time(),
            state=self._current_state,
            energy_level=self._energy_level,
            stress_level=self._stress_level,
            resource_efficiency=self._resource_efficiency,
            homeostasis_score=self._calculate_homeostasis_score(
                self.sensorium.get_system_metrics()
            )
        )
        
        self._metrics_history.append(metrics)
    
    def _trigger_event(self, event_type: str, data: Dict[str, Any]):
        """Генерация события"""
        if event_type in self._event_handlers:
            for handler in self._event_handlers[event_type]:
                try:
                    handler(data)
                except Exception as e:
                    self.logger.error(f"Ошибка в обработчике события {event_type}: {e}")
    
    def add_event_handler(self, event_type: str, handler: Callable):
        """Добавление обработчика события"""
        if event_type in self._event_handlers:
            self._event_handlers[event_type].append(handler)
    
    def get_current_metrics(self) -> MetabolismMetrics:
        """Получение текущих метрик метаболизма"""
        return MetabolismMetrics(
            timestamp=time.time(),
            state=self._current_state,
            energy_level=self._energy_level,
            stress_level=self._stress_level,
            resource_efficiency=self._resource_efficiency,
            homeostasis_score=self._calculate_homeostasis_score(
                self.sensorium.get_system_metrics()
            )
        )
    
    def get_metabolism_history(self, limit: int = 100) -> List[MetabolismMetrics]:
        """Получение истории метаболизма"""
        return list(self._metrics_history)[-limit:]
    
    def get_metabolism_status(self) -> Dict[str, Any]:
        """Получение статуса метаболизма"""
        return {
            "state": self._current_state.value,
            "energy_level": self._energy_level,
            "stress_level": self._stress_level,
            "resource_efficiency": self._resource_efficiency,
            "metabolism_rate": self._metabolism_rate,
            "recovery_rate": self._recovery_rate,
            "monitoring_active": self._monitoring_thread and self._monitoring_thread.is_alive(),
            "metrics_history_size": len(self._metrics_history)
        }
    
    def adjust_metabolism_rate(self, new_rate: float):
        """Корректировка скорости метаболизма"""
        self._metabolism_rate = max(0.1, min(2.0, new_rate))
        self.logger.info(f"Скорость метаболизма изменена на {self._metabolism_rate}")
    
    def emergency_recovery(self):
        """Экстренное восстановление"""
        self._energy_level = min(1.0, self._energy_level + 0.3)
        self._stress_level = max(0.0, self._stress_level - 0.2)
        self.logger.warning("Выполнено экстренное восстановление метаболизма") 