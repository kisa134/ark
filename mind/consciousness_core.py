"""
ConsciousnessCore - центральный хаб сознания
Реализует двухконтурную архитектуру с конечным автоматом состояний
"""

import time
import threading
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import logging
import json
from collections import deque

from config import config


class ConsciousnessState(Enum):
    """Состояния сознания"""
    IDLE = "idle"
    REACTIVE_DEFENSE = "reactive_defense"
    REFLECTIVE_ANALYSIS = "reflective_analysis"


@dataclass
class ConsciousnessEvent:
    """Событие сознания"""
    timestamp: float
    event_type: str
    data: Dict[str, Any]
    source: str


class ConsciousnessCore:
    """
    ConsciousnessCore - центральный хаб сознания
    Реализует конечный автомат с состояниями и двухконтурную архитектуру
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Текущее состояние сознания
        self._current_state = ConsciousnessState.IDLE
        self._state_history: deque = deque(maxlen=1000)
        
        # История событий
        self._event_history: deque = deque(maxlen=10000)
        
        # Обработчики событий по состояниям
        self._state_handlers: Dict[ConsciousnessState, List[Callable]] = {
            ConsciousnessState.IDLE: [],
            ConsciousnessState.REACTIVE_DEFENSE: [],
            ConsciousnessState.REFLECTIVE_ANALYSIS: []
        }
        
        # Обработчики переходов между состояниями
        self._transition_handlers: Dict[str, List[Callable]] = {}
        
        # Поток обработки событий
        self._processing_thread: Optional[threading.Thread] = None
        self._stop_processing = threading.Event()
        self._event_queue: deque = deque()
        
        # Статистика
        self._stats = {
            "events_processed": 0,
            "state_transitions": 0,
            "last_event_time": 0,
            "processing_rate": 0.0
        }
        
        # Инициализация обработчиков состояний
        self._init_state_handlers()
    
    def _init_state_handlers(self):
        """Инициализация обработчиков состояний"""
        # IDLE - пассивное наблюдение
        self._state_handlers[ConsciousnessState.IDLE].append(self._handle_idle_state)
        
        # REACTIVE_DEFENSE - быстрая реакция на угрозы
        self._state_handlers[ConsciousnessState.REACTIVE_DEFENSE].append(self._handle_reactive_defense)
        
        # REFLECTIVE_ANALYSIS - глубокий анализ
        self._state_handlers[ConsciousnessState.REFLECTIVE_ANALYSIS].append(self._handle_reflective_analysis)
    
    def start_processing(self):
        """Запуск обработки событий сознания"""
        if self._processing_thread and self._processing_thread.is_alive():
            return
        
        self._stop_processing.clear()
        self._processing_thread = threading.Thread(
            target=self._processing_loop,
            daemon=True
        )
        self._processing_thread.start()
        self.logger.info("Обработка событий сознания запущена")
    
    def stop_processing(self):
        """Остановка обработки событий сознания"""
        self._stop_processing.set()
        if self._processing_thread:
            self._processing_thread.join(timeout=5)
        self.logger.info("Обработка событий сознания остановлена")
    
    def _processing_loop(self):
        """Основной цикл обработки событий"""
        while not self._stop_processing.is_set():
            try:
                # Обработка событий из очереди
                while self._event_queue and not self._stop_processing.is_set():
                    event = self._event_queue.popleft()
                    self._process_event(event)
                
                # Выполнение обработчиков текущего состояния
                self._execute_state_handlers()
                
                # Пауза между циклами
                time.sleep(0.1)  # 100ms между циклами
                
            except Exception as e:
                self.logger.error(f"Ошибка в цикле обработки: {e}")
                time.sleep(1)
    
    def _process_event(self, event: ConsciousnessEvent):
        """Обработка отдельного события"""
        try:
            # Логирование события
            self.logger.debug(f"Обработка события: {event.event_type} от {event.source}")
            
            # Сохранение в историю
            self._event_history.append(event)
            
            # Обновление статистики
            self._stats["events_processed"] += 1
            self._stats["last_event_time"] = event.timestamp
            
            # Проверка необходимости смены состояния
            self._check_state_transition(event)
            
        except Exception as e:
            self.logger.error(f"Ошибка обработки события: {e}")
    
    def _check_state_transition(self, event: ConsciousnessEvent):
        """Проверка необходимости смены состояния"""
        old_state = self._current_state
        new_state = self._determine_new_state(event)
        
        if new_state != old_state:
            self._transition_state(old_state, new_state, event)
    
    def _determine_new_state(self, event: ConsciousnessEvent) -> ConsciousnessState:
        """Определение нового состояния на основе события"""
        # Логика перехода состояний
        if event.event_type == "threat_detected":
            return ConsciousnessState.REACTIVE_DEFENSE
        elif event.event_type == "analysis_requested":
            return ConsciousnessState.REFLECTIVE_ANALYSIS
        elif event.event_type == "threat_resolved" and self._current_state == ConsciousnessState.REACTIVE_DEFENSE:
            return ConsciousnessState.IDLE
        elif event.event_type == "analysis_complete" and self._current_state == ConsciousnessState.REFLECTIVE_ANALYSIS:
            return ConsciousnessState.IDLE
        
        return self._current_state
    
    def _transition_state(self, old_state: ConsciousnessState, new_state: ConsciousnessState, trigger_event: ConsciousnessEvent):
        """Переход между состояниями"""
        self.logger.info(f"Переход состояния: {old_state.value} -> {new_state.value}")
        
        # Сохранение перехода в историю
        self._state_history.append({
            "timestamp": time.time(),
            "old_state": old_state.value,
            "new_state": new_state.value,
            "trigger_event": trigger_event.event_type
        })
        
        # Обновление статистики
        self._stats["state_transitions"] += 1
        
        # Выполнение обработчиков перехода
        transition_key = f"{old_state.value}_to_{new_state.value}"
        if transition_key in self._transition_handlers:
            for handler in self._transition_handlers[transition_key]:
                try:
                    handler(old_state, new_state, trigger_event)
                except Exception as e:
                    self.logger.error(f"Ошибка в обработчике перехода {transition_key}: {e}")
        
        # Обновление текущего состояния
        self._current_state = new_state
    
    def _execute_state_handlers(self):
        """Выполнение обработчиков текущего состояния"""
        handlers = self._state_handlers.get(self._current_state, [])
        
        for handler in handlers:
            try:
                handler()
            except Exception as e:
                self.logger.error(f"Ошибка в обработчике состояния {self._current_state.value}: {e}")
    
    def _handle_idle_state(self):
        """Обработчик состояния IDLE - пассивное наблюдение"""
        # В состоянии IDLE система просто наблюдает за окружением
        # Может выполнять фоновые задачи, но не активна
        self.logger.debug("IDLE: Пассивное наблюдение за системой")
    
    def _handle_reactive_defense(self):
        """Обработчик состояния REACTIVE_DEFENSE - быстрая реакция"""
        # В состоянии REACTIVE_DEFENSE система быстро реагирует на угрозы
        # Приоритет скорости над точностью
        self.logger.debug("Выполнение быстрой реакции на угрозу")
    
    def _handle_reflective_analysis(self):
        """Обработчик состояния REFLECTIVE_ANALYSIS - глубокий анализ"""
        # В состоянии REFLECTIVE_ANALYSIS система выполняет глубокий анализ
        # Приоритет точности над скоростью
        self.logger.debug("Выполнение глубокого анализа")
    
    def add_event(self, event_type: str, data: Dict[str, Any], source: str):
        """Добавление события в очередь обработки"""
        event = ConsciousnessEvent(
            timestamp=time.time(),
            event_type=event_type,
            data=data,
            source=source
        )
        
        self._event_queue.append(event)
    
    def add_state_handler(self, state: ConsciousnessState, handler: Callable):
        """Добавление обработчика состояния"""
        if state in self._state_handlers:
            self._state_handlers[state].append(handler)
    
    def add_transition_handler(self, from_state: str, to_state: str, handler: Callable):
        """Добавление обработчика перехода состояний"""
        transition_key = f"{from_state}_to_{to_state}"
        if transition_key not in self._transition_handlers:
            self._transition_handlers[transition_key] = []
        self._transition_handlers[transition_key].append(handler)
    
    def get_current_state(self) -> ConsciousnessState:
        """Получение текущего состояния"""
        return self._current_state
    
    def get_state_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Получение истории состояний"""
        return list(self._state_history)[-limit:]
    
    def get_event_history(self, limit: int = 100) -> List[ConsciousnessEvent]:
        """Получение истории событий"""
        return list(self._event_history)[-limit:]
    
    def get_consciousness_stats(self) -> Dict[str, Any]:
        """Получение статистики сознания"""
        current_time = time.time()
        
        # Расчет скорости обработки
        if self._stats["last_event_time"] > 0:
            time_diff = current_time - self._stats["last_event_time"]
            if time_diff > 0:
                self._stats["processing_rate"] = self._stats["events_processed"] / time_diff
        
        return {
            "current_state": self._current_state.value,
            "events_processed": self._stats["events_processed"],
            "state_transitions": self._stats["state_transitions"],
            "processing_rate": self._stats["processing_rate"],
            "queue_size": len(self._event_queue),
            "history_size": len(self._event_history),
            "state_history_size": len(self._state_history),
            "processing_active": self._processing_thread and self._processing_thread.is_alive()
        }
    
    def force_state_transition(self, new_state: ConsciousnessState):
        """Принудительный переход в новое состояние"""
        old_state = self._current_state
        self._transition_state(old_state, new_state, ConsciousnessEvent(
            timestamp=time.time(),
            event_type="forced_transition",
            data={"reason": "manual_override"},
            source="consciousness_core"
        ))
    
    def force_state_change(self, new_state: str):
        """Принудительно изменяет состояние сознания. Только для тестов и отладки."""
        try:
            # Преобразование строки в enum
            state_enum = ConsciousnessState(new_state)
            old_state = self._current_state
            self._current_state = state_enum
            self.logger.info(f"Состояние сознания принудительно изменено: {old_state.value} -> {self._current_state.value}")
        except ValueError:
            self.logger.error(f"Попытка принудительно установить несуществующее состояние: {new_state}")
            self.logger.error(f"Доступные состояния: {[state.value for state in ConsciousnessState]}")
    
    def get_consciousness_status(self) -> Dict[str, Any]:
        """Получение полного статуса сознания"""
        return {
            "state": self.get_current_state().value,
            "stats": self.get_consciousness_stats(),
            "available_states": [state.value for state in ConsciousnessState],
            "active_handlers": {
                state.value: len(handlers) 
                for state, handlers in self._state_handlers.items()
            }
        }
    
    def get_memory_size(self) -> int:
        """Получение размера памяти сознания"""
        return len(self._event_history) + len(self._state_history) 