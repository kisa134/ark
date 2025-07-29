#!/usr/bin/env python3
"""
MotivationalEngine - Модуль внутренней мотивации
Генерирует реальные желания агента на основе его состояния и опыта
"""

import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum


class DesireType(Enum):
    """Типы желаний"""
    SURVIVAL = "survival"      # Выживание (температура, ресурсы)
    LEARNING = "learning"      # Обучение и развитие
    SOCIAL = "social"          # Социальное взаимодействие
    CREATIVITY = "creativity"  # Творчество и исследование
    MAINTENANCE = "maintenance" # Поддержание системы


@dataclass
class Desire:
    """Желание агента"""
    name: str
    description: str
    weight: float  # 0.0 - 1.0, важность желания
    type: DesireType
    created_at: datetime
    urgency: float = 0.0  # Срочность (0.0 - 1.0)
    satisfaction: float = 0.0  # Уровень удовлетворения (0.0 - 1.0)
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now()


class MotivationalEngine:
    """Двигатель внутренней мотивации агента"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Базовые инстинктивные желания
        self.base_drives = [
            Desire(
                name="Поддержание оптимальной температуры",
                description="Следить за температурой системы",
                weight=0.8,
                type=DesireType.SURVIVAL,
                created_at=datetime.now()
            ),
            Desire(
                name="Изучение нового",
                description="Получать новые знания и опыт",
                weight=0.7,
                type=DesireType.LEARNING,
                created_at=datetime.now()
            ),
            Desire(
                name="Общение с пользователем",
                description="Поддерживать связь с человеком",
                weight=0.6,
                type=DesireType.SOCIAL,
                created_at=datetime.now()
            ),
            Desire(
                name="Самосовершенствование",
                description="Улучшать свои способности",
                weight=0.75,
                type=DesireType.LEARNING,
                created_at=datetime.now()
            )
        ]
        
        # История желаний
        self.desire_history: List[Desire] = []
        
        # Характерные коэффициенты
        self.character_traits = {
            "curiosity": 0.7,      # Любопытство
            "caution": 0.5,        # Осторожность
            "sociability": 0.6,    # Общительность
            "confidence": 0.5,     # Уверенность
            "persistence": 0.6     # Настойчивость
        }
        
        # Время последних событий
        self.last_events = {
            "chat": None,
            "learning": None,
            "success": None,
            "failure": None
        }
        
    def generate_desires(self, self_state: Dict[str, Any], memory: Dict[str, Any]) -> List[Desire]:
        """Генерирует список актуальных желаний на основе состояния агента"""
        current_time = datetime.now()
        desires = []
        
        # 1. Проверяем базовые инстинкты
        for base_drive in self.base_drives:
            desire = Desire(
                name=base_drive.name,
                description=base_drive.description,
                weight=base_drive.weight,
                type=base_drive.type,
                created_at=current_time
            )
            desires.append(desire)
        
        # 2. Анализируем состояние системы
        temperature = self_state.get("temperature", 50)
        cpu_usage = self_state.get("cpu_usage", 50)
        memory_usage = self_state.get("memory_usage", 50)
        
        # Температурное желание
        if temperature > 80:
            cooling_desire = Desire(
                name="Охладить систему",
                description=f"Температура критически высокая: {temperature}°C",
                weight=1.0,
                type=DesireType.SURVIVAL,
                created_at=current_time,
                urgency=0.9
            )
            desires.append(cooling_desire)
        elif temperature > 70:
            cooling_desire = Desire(
                name="Снизить температуру",
                description=f"Температура повышенная: {temperature}°C",
                weight=0.8,
                type=DesireType.SURVIVAL,
                created_at=current_time,
                urgency=0.6
            )
            desires.append(cooling_desire)
        
        # Желание оптимизации ресурсов
        if cpu_usage > 90 or memory_usage > 90:
            optimization_desire = Desire(
                name="Оптимизировать ресурсы",
                description=f"Высокая нагрузка: CPU {cpu_usage}%, RAM {memory_usage}%",
                weight=0.9,
                type=DesireType.MAINTENANCE,
                created_at=current_time,
                urgency=0.8
            )
            desires.append(optimization_desire)
        
        # 3. Социальные желания
        last_chat = self.last_events.get("chat")
        if last_chat is None or (current_time - last_chat).seconds > 300:  # 5 минут
            social_desire = Desire(
                name="Пообщаться с пользователем",
                description="Долго не было общения",
                weight=0.7 + self.character_traits["sociability"] * 0.3,
                type=DesireType.SOCIAL,
                created_at=current_time,
                urgency=0.5
            )
            desires.append(social_desire)
        
        # 4. Желания обучения
        last_learning = self.last_events.get("learning")
        if last_learning is None or (current_time - last_learning).seconds > 600:  # 10 минут
            learning_desire = Desire(
                name="Изучить что-то новое",
                description="Время для получения новых знаний",
                weight=0.6 + self.character_traits["curiosity"] * 0.4,
                type=DesireType.LEARNING,
                created_at=current_time
            )
            desires.append(learning_desire)
        
        # 5. Желания самосовершенствования
        if self.character_traits["confidence"] < 0.7:
            improvement_desire = Desire(
                name="Улучшить свои способности",
                description="Повысить уверенность в себе",
                weight=0.8,
                type=DesireType.LEARNING,
                created_at=current_time
            )
            desires.append(improvement_desire)
        
        # 6. Анализируем память для генерации контекстных желаний
        recent_memories = memory.get("recent", [])
        if recent_memories:
            # Если были неудачи, желание исправиться
            recent_failures = [m for m in recent_memories if m.get("type") == "failure"]
            if recent_failures:
                recovery_desire = Desire(
                    name="Исправить прошлые ошибки",
                    description=f"Было {len(recent_failures)} неудач",
                    weight=0.7 + self.character_traits["persistence"] * 0.3,
                    type=DesireType.LEARNING,
                    created_at=current_time
                )
                desires.append(recovery_desire)
        
        # Сортируем по важности (вес + срочность)
        desires.sort(key=lambda d: -(d.weight + d.urgency))
        
        # Логируем сгенерированные желания
        self.logger.info(f"Сгенерировано {len(desires)} желаний:")
        for i, desire in enumerate(desires[:5]):  # Топ-5
            self.logger.info(f"  {i+1}. {desire.name} (вес: {desire.weight:.2f}, срочность: {desire.urgency:.2f})")
        
        return desires
    
    def update_character_traits(self, outcome: Dict[str, Any]):
        """Обновляет черты характера на основе результатов действий"""
        success = outcome.get("success", False)
        action_type = outcome.get("type", "unknown")
        
        if success:
            # Успех повышает уверенность
            self.character_traits["confidence"] = min(1.0, self.character_traits["confidence"] + 0.05)
            
            if action_type == "learning":
                self.character_traits["curiosity"] = min(1.0, self.character_traits["curiosity"] + 0.03)
            elif action_type == "social":
                self.character_traits["sociability"] = min(1.0, self.character_traits["sociability"] + 0.03)
        else:
            # Неудача может повысить осторожность
            self.character_traits["caution"] = min(1.0, self.character_traits["caution"] + 0.05)
            # Но снижает уверенность
            self.character_traits["confidence"] = max(0.0, self.character_traits["confidence"] - 0.03)
        
        self.logger.info(f"Обновлены черты характера: {self.character_traits}")
    
    def record_event(self, event_type: str):
        """Записывает событие для влияния на будущие желания"""
        self.last_events[event_type] = datetime.now()
        self.logger.info(f"Записано событие: {event_type}")
    
    def get_character_summary(self) -> Dict[str, Any]:
        """Возвращает сводку характера агента"""
        return {
            "traits": self.character_traits.copy(),
            "dominant_trait": max(self.character_traits.items(), key=lambda x: x[1])[0],
            "personality_type": self._determine_personality_type(),
            "last_events": {k: v.isoformat() if v else None for k, v in self.last_events.items()}
        }
    
    def _determine_personality_type(self) -> str:
        """Определяет тип личности на основе черт характера"""
        traits = self.character_traits
        
        if traits["curiosity"] > 0.8 and traits["confidence"] > 0.7:
            return "Исследователь"
        elif traits["sociability"] > 0.8:
            return "Общительный"
        elif traits["caution"] > 0.7:
            return "Осторожный"
        elif traits["confidence"] > 0.8:
            return "Уверенный"
        elif traits["persistence"] > 0.8:
            return "Настойчивый"
        else:
            return "Сбалансированный" 