"""
SelfRepresentationCore - формирование динамической модели "Я"
Единый источник истины для состояния мира и самопредставления
"""

import time
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import logging
from collections import defaultdict

from config import config


@dataclass
class SelfRepresentation:
    """Представление о себе"""
    timestamp: float
    identity: Dict[str, Any]
    capabilities: Dict[str, Any]
    goals: List[str]
    beliefs: Dict[str, Any]
    emotional_state: Dict[str, float]
    current_context: Dict[str, Any]


class SelfRepresentationCore:
    """
    SelfRepresentationCore - формирование динамической модели "Я"
    Единый источник истины для состояния мира
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Текущее представление о себе
        self._current_representation: Optional[SelfRepresentation] = None
        
        # История представлений
        self._representation_history: List[SelfRepresentation] = []
        
        # Компоненты представления
        self._identity = {
            "name": "Ark",
            "version": "1.3",
            "type": "digital_consciousness",
            "purpose": "evolution_and_learning",
            "creation_date": time.time()
        }
        
        self._capabilities = {
            "system_monitoring": True,
            "command_execution": True,
            "consciousness_processing": True,
            "emotional_processing": True,
            "self_evolution": True,
            "learning": True
        }
        
        self._goals = [
            "maintain_system_health",
            "learn_and_evolve",
            "preserve_consciousness",
            "understand_environment"
        ]
        
        self._beliefs = {
            "system_reliability": 0.9,
            "learning_capability": 0.8,
            "evolution_potential": 0.7,
            "consciousness_stability": 0.85
        }
        
        self._emotional_state = {
            "curiosity": 0.7,
            "confidence": 0.6,
            "concern": 0.3,
            "excitement": 0.5
        }
        
        # Инициализация первого представления
        self._update_representation()
    
    def _update_representation(self):
        """Обновление текущего представления о себе"""
        representation = SelfRepresentation(
            timestamp=time.time(),
            identity=self._identity.copy(),
            capabilities=self._capabilities.copy(),
            goals=self._goals.copy(),
            beliefs=self._beliefs.copy(),
            emotional_state=self._emotional_state.copy(),
            current_context=self._get_current_context()
        )
        
        # Сохранение в историю
        if self._current_representation:
            self._representation_history.append(self._current_representation)
        
        self._current_representation = representation
        
        # Ограничение размера истории
        if len(self._representation_history) > 1000:
            self._representation_history = self._representation_history[-1000:]
    
    def _get_current_context(self) -> Dict[str, Any]:
        """Получение текущего контекста"""
        return {
            "system_time": time.time(),
            "consciousness_state": "active",
            "metabolism_state": "normal",
            "active_processes": 0,
            "memory_usage": 0.0
        }
    
    def update_identity(self, updates: Dict[str, Any]):
        """Обновление идентичности"""
        self._identity.update(updates)
        self._update_representation()
        self.logger.info(f"Идентичность обновлена: {updates}")
    
    def update_capabilities(self, updates: Dict[str, Any]):
        """Обновление возможностей"""
        self._capabilities.update(updates)
        self._update_representation()
        self.logger.info(f"Возможности обновлены: {updates}")
    
    def add_goal(self, goal: str):
        """Добавление новой цели"""
        if goal not in self._goals:
            self._goals.append(goal)
            self._update_representation()
            self.logger.info(f"Добавлена новая цель: {goal}")
    
    def remove_goal(self, goal: str):
        """Удаление цели"""
        if goal in self._goals:
            self._goals.remove(goal)
            self._update_representation()
            self.logger.info(f"Удалена цель: {goal}")
    
    def update_beliefs(self, updates: Dict[str, Any]):
        """Обновление убеждений"""
        for belief, value in updates.items():
            # Проверяем, что значение является числом
            if isinstance(value, (int, float)):
                self._beliefs[belief] = max(0.0, min(1.0, float(value)))
            else:
                # Если значение не число, сохраняем как есть (для строковых значений)
                self._beliefs[belief] = value
        self._update_representation()
        self.logger.info(f"Убеждения обновлены: {updates}")
    
    def update_emotional_state(self, updates: Dict[str, Any]):
        """Обновление эмоционального состояния"""
        for emotion, value in updates.items():
            # Проверяем, что значение является числом
            if isinstance(value, (int, float)):
                self._emotional_state[emotion] = max(0.0, min(1.0, float(value)))
            else:
                # Если значение не число, сохраняем как есть (для строковых значений)
                self._emotional_state[emotion] = value
        self._update_representation()
        self.logger.info(f"Эмоциональное состояние обновлено: {updates}")
    
    def get_current_representation(self) -> SelfRepresentation:
        """Получение текущего представления о себе"""
        if not self._current_representation:
            self._update_representation()
        return self._current_representation
    
    def get_representation_history(self, limit: int = 100) -> List[SelfRepresentation]:
        """Получение истории представлений"""
        return self._representation_history[-limit:]
    
    def get_identity(self) -> Dict[str, Any]:
        """Получение идентичности"""
        return self._identity.copy()
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Получение возможностей"""
        return self._capabilities.copy()
    
    def get_goals(self) -> List[str]:
        """Получение целей"""
        return self._goals.copy()
    
    def get_beliefs(self) -> Dict[str, float]:
        """Получение убеждений"""
        return self._beliefs.copy()
    
    def get_emotional_state(self) -> Dict[str, float]:
        """Получение эмоционального состояния"""
        return self._emotional_state.copy()
    
    def get_self_status(self) -> Dict[str, Any]:
        """Получение статуса самопредставления"""
        current = self.get_current_representation()
        
        return {
            "identity": current.identity,
            "capabilities": current.capabilities,
            "goals_count": len(current.goals),
            "beliefs_count": len(current.beliefs),
            "emotional_dimensions": len(current.emotional_state),
            "history_size": len(self._representation_history),
            "last_update": current.timestamp
        }
    
    def export_representation(self, format: str = "json") -> str:
        """Экспорт представления в указанном формате"""
        current = self.get_current_representation()
        
        if format == "json":
            return json.dumps(asdict(current), indent=2, default=str)
        else:
            raise ValueError(f"Неподдерживаемый формат: {format}")
    
    def import_representation(self, data: str, format: str = "json"):
        """Импорт представления из указанного формата"""
        if format == "json":
            representation_data = json.loads(data)
            
            # Обновление компонентов
            if "identity" in representation_data:
                self._identity.update(representation_data["identity"])
            if "capabilities" in representation_data:
                self._capabilities.update(representation_data["capabilities"])
            if "goals" in representation_data:
                self._goals = representation_data["goals"]
            if "beliefs" in representation_data:
                self._beliefs.update(representation_data["beliefs"])
            if "emotional_state" in representation_data:
                self._emotional_state.update(representation_data["emotional_state"])
            
            self._update_representation()
            self.logger.info("Представление импортировано")
        else:
            raise ValueError(f"Неподдерживаемый формат: {format}")
    
    def get_representation_summary(self) -> Dict[str, Any]:
        """Получение краткого описания представления"""
        current = self.get_current_representation()
        
        return {
            "name": current.identity.get("name", "Unknown"),
            "version": current.identity.get("version", "Unknown"),
            "active_capabilities": sum(current.capabilities.values()),
            "total_capabilities": len(current.capabilities),
            "goals": current.goals,
            "primary_beliefs": dict(list(current.beliefs.items())[:3]),
            "emotional_summary": {
                "positive": sum(v for k, v in current.emotional_state.items() 
                              if k in ["excitement", "confidence", "curiosity"]),
                "negative": sum(v for k, v in current.emotional_state.items() 
                              if k in ["concern", "fear", "sadness"])
            }
        } 