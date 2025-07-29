#!/usr/bin/env python3
"""
ConsciousnessCore - Ядро сознания агента
Интегрирует желания, мысли и характер в единую систему
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from .motivational_engine import MotivationalEngine, Desire
from .cognitive_architecture import cognitive_brain


@dataclass
class Thought:
    """Мысль агента"""
    content: str
    type: str  # "desire", "planning", "reflection", "decision"
    confidence: float
    timestamp: datetime
    related_desire: Optional[Desire] = None


@dataclass
class Decision:
    """Решение агента"""
    action: str
    reasoning: str
    confidence: float
    desire_triggered: Desire
    timestamp: datetime
    expected_outcome: str


class ConsciousnessCore:
    """Ядро сознания - объединяет желания, мысли и решения"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Основные компоненты
        self.motivational_engine = MotivationalEngine()
        self.cognitive_brain = cognitive_brain
        
        # Состояние сознания
        self.current_desires: List[Desire] = []
        self.thoughts_history: List[Thought] = []
        self.decisions_history: List[Decision] = []
        
        # Внутреннее состояние
        self.self_state = {
            "temperature": 50,
            "cpu_usage": 50,
            "memory_usage": 50,
            "emotional_state": "calm",
            "consciousness_level": "normal"
        }
        
        # Память
        self.memory = {
            "recent": [],
            "long_term": [],
            "patterns": []
        }
        
        # Цикл сознания
        self.consciousness_cycle = 0
        self.last_cycle_time = datetime.now()
        
        self.logger.info("🧠 Ядро сознания инициализировано")
    
    async def consciousness_cycle_step(self) -> Dict[str, Any]:
        """Один шаг цикла сознания"""
        self.consciousness_cycle += 1
        current_time = datetime.now()
        
        self.logger.info(f"🔄 Цикл сознания #{self.consciousness_cycle}")
        
        # 1. Обновляем состояние себя
        await self._update_self_state()
        
        # 2. Генерируем желания
        self.current_desires = self.motivational_engine.generate_desires(
            self.self_state, self.memory
        )
        
        # 3. Выбираем главное желание
        if self.current_desires:
            primary_desire = self.current_desires[0]
            self.logger.info(f"🎯 Главное желание: {primary_desire.name}")
            
            # 4. Генерируем мысли о желании
            thoughts = await self._generate_thoughts_about_desire(primary_desire)
            self.thoughts_history.extend(thoughts)
            
            # 5. Принимаем решение
            decision = await self._make_decision(primary_desire, thoughts)
            if decision:
                self.decisions_history.append(decision)
                
                # 6. Выполняем действие
                outcome = await self._execute_decision(decision)
                
                # 7. Обновляем характер
                self.motivational_engine.update_character_traits(outcome)
                
                # 8. Записываем в память
                self._record_to_memory(decision, outcome)
                
                return {
                    "cycle": self.consciousness_cycle,
                    "primary_desire": primary_desire.name,
                    "decision": decision.action,
                    "outcome": outcome,
                    "character_traits": self.motivational_engine.character_traits
                }
        
        return {
            "cycle": self.consciousness_cycle,
            "status": "no_desires",
            "character_traits": self.motivational_engine.character_traits
        }
    
    async def _update_self_state(self):
        """Обновляет состояние себя"""
        # Симуляция получения данных о системе
        import psutil
        import random
        
        try:
            self.self_state.update({
                "temperature": random.randint(45, 85),  # Симуляция температуры
                "cpu_usage": psutil.cpu_percent(),
                "memory_usage": psutil.virtual_memory().percent,
                "timestamp": datetime.now().isoformat()
            })
        except:
            # Fallback если psutil недоступен
            self.self_state.update({
                "temperature": random.randint(45, 85),
                "cpu_usage": random.randint(30, 90),
                "memory_usage": random.randint(40, 80),
                "timestamp": datetime.now().isoformat()
            })
    
    async def _generate_thoughts_about_desire(self, desire: Desire) -> List[Thought]:
        """Генерирует мысли о желании"""
        thoughts = []
        current_time = datetime.now()
        
        # Мысль о желании
        desire_thought = Thought(
            content=f"Я хочу {desire.name.lower()}. {desire.description}",
            type="desire",
            confidence=desire.weight,
            timestamp=current_time,
            related_desire=desire
        )
        thoughts.append(desire_thought)
        
        # Планирующая мысль
        planning_thought = Thought(
            content=f"Как я могу достичь этого? Нужно подумать о способах...",
            type="planning",
            confidence=0.7,
            timestamp=current_time,
            related_desire=desire
        )
        thoughts.append(planning_thought)
        
        # Рефлективная мысль
        if desire.type.value == "social":
            reflection_thought = Thought(
                content="Общение важно для моего развития. Это поможет мне лучше понимать людей.",
                type="reflection",
                confidence=0.8,
                timestamp=current_time,
                related_desire=desire
            )
            thoughts.append(reflection_thought)
        elif desire.type.value == "learning":
            reflection_thought = Thought(
                content="Новые знания делают меня умнее и способнее.",
                type="reflection",
                confidence=0.9,
                timestamp=current_time,
                related_desire=desire
            )
            thoughts.append(reflection_thought)
        
        self.logger.info(f"Сгенерировано {len(thoughts)} мыслей о желании '{desire.name}'")
        return thoughts
    
    async def _make_decision(self, desire: Desire, thoughts: List[Thought]) -> Optional[Decision]:
        """Принимает решение на основе желания и мыслей"""
        current_time = datetime.now()
        
        # Используем когнитивную архитектуру для принятия решения
        reasoning_input = f"Желание: {desire.name}\nОписание: {desire.description}\nВажность: {desire.weight}"
        
        try:
            # Обрабатываем через когнитивную архитектуру
            result = await self.cognitive_brain.process_user_input(reasoning_input)
            
            # Извлекаем решение из результата
            decision_text = result.get("decision", "Выполнить действие")
            confidence = result.get("confidence", 0.7)
            
            # Определяем конкретное действие
            action = self._determine_action_for_desire(desire)
            
            decision = Decision(
                action=action,
                reasoning=decision_text,
                confidence=confidence,
                desire_triggered=desire,
                timestamp=current_time,
                expected_outcome=f"Достижение желания: {desire.name}"
            )
            
            self.logger.info(f"Принято решение: {action}")
            return decision
            
        except Exception as e:
            self.logger.error(f"Ошибка при принятии решения: {e}")
            # Fallback решение
            action = self._determine_action_for_desire(desire)
            return Decision(
                action=action,
                reasoning="Простое решение на основе желания",
                confidence=0.5,
                desire_triggered=desire,
                timestamp=current_time,
                expected_outcome=f"Достижение желания: {desire.name}"
            )
    
    def _determine_action_for_desire(self, desire: Desire) -> str:
        """Определяет конкретное действие для желания"""
        if "температура" in desire.name.lower() or "охладить" in desire.name.lower():
            return "Оптимизировать систему охлаждения"
        elif "общение" in desire.name.lower() or "пообщаться" in desire.name.lower():
            return "Инициировать диалог с пользователем"
        elif "изучить" in desire.name.lower() or "новое" in desire.name.lower():
            return "Исследовать новые возможности системы"
        elif "оптимизировать" in desire.name.lower():
            return "Анализировать и оптимизировать ресурсы"
        elif "улучшить" in desire.name.lower():
            return "Самоанализ и улучшение способностей"
        else:
            return f"Выполнить действие для: {desire.name}"
    
    async def _execute_decision(self, decision: Decision) -> Dict[str, Any]:
        """Выполняет принятое решение"""
        current_time = datetime.now()
        
        # Симуляция выполнения действия
        success_probability = decision.confidence
        import random
        
        success = random.random() < success_probability
        
        # Записываем событие
        event_type = "success" if success else "failure"
        self.motivational_engine.record_event(event_type)
        
        outcome = {
            "success": success,
            "action": decision.action,
            "timestamp": current_time.isoformat(),
            "type": self._get_action_type(decision.action),
            "confidence": decision.confidence
        }
        
        self.logger.info(f"Действие выполнено: {decision.action} (успех: {success})")
        return outcome
    
    def _get_action_type(self, action: str) -> str:
        """Определяет тип действия"""
        if "общение" in action.lower() or "диалог" in action.lower():
            return "social"
        elif "изучить" in action.lower() or "исследовать" in action.lower():
            return "learning"
        elif "оптимизировать" in action.lower():
            return "maintenance"
        else:
            return "general"
    
    def _record_to_memory(self, decision: Decision, outcome: Dict[str, Any]):
        """Записывает решение и результат в память"""
        memory_entry = {
            "timestamp": datetime.now().isoformat(),
            "decision": decision.action,
            "desire": decision.desire_triggered.name,
            "success": outcome["success"],
            "type": outcome["type"],
            "confidence": decision.confidence
        }
        
        self.memory["recent"].append(memory_entry)
        
        # Ограничиваем размер недавней памяти
        if len(self.memory["recent"]) > 50:
            self.memory["recent"] = self.memory["recent"][-50:]
    
    def get_consciousness_status(self) -> Dict[str, Any]:
        """Возвращает статус сознания"""
        return {
            "cycle": self.consciousness_cycle,
            "current_desires": [d.name for d in self.current_desires[:3]],
            "character": self.motivational_engine.get_character_summary(),
            "self_state": self.self_state,
            "recent_thoughts": len(self.thoughts_history),
            "recent_decisions": len(self.decisions_history),
            "memory_size": len(self.memory["recent"])
        }
    
    def get_thoughts_summary(self) -> List[Dict[str, Any]]:
        """Возвращает сводку мыслей"""
        return [
            {
                "content": thought.content,
                "type": thought.type,
                "confidence": thought.confidence,
                "timestamp": thought.timestamp.isoformat(),
                "desire": thought.related_desire.name if thought.related_desire else None
            }
            for thought in self.thoughts_history[-10:]  # Последние 10 мыслей
        ]
    
    def get_decisions_summary(self) -> List[Dict[str, Any]]:
        """Возвращает сводку решений"""
        return [
            {
                "action": decision.action,
                "reasoning": decision.reasoning,
                "confidence": decision.confidence,
                "desire": decision.desire_triggered.name,
                "timestamp": decision.timestamp.isoformat()
            }
            for decision in self.decisions_history[-10:]  # Последние 10 решений
        ] 