"""
Эмоциональная обработка - Psyche Level
Обработка эмоций и эмоциональных состояний
"""

import logging
import time
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from collections import deque
import math

from config import consciousness_config

@dataclass
class EmotionalMemory:
    """Эмоциональная память"""
    timestamp: float
    emotion_type: str
    intensity: float  # 0.0 - 1.0
    context: Dict[str, Any]
    duration: float

class EmotionalProcessingCore:
    """
    Ядро эмоциональной обработки
    Обрабатывает эмоции, поддерживает эмоциональную память
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Эмоциональная память
        self._emotional_memory: deque = deque(maxlen=consciousness_config.EMOTIONAL_MEMORY_SIZE)
        
        # Текущее эмоциональное состояние
        self._current_emotions = {
            "joy": 0.0,
            "sadness": 0.0,
            "anger": 0.0,
            "fear": 0.0,
            "surprise": 0.0,
            "disgust": 0.0,
            "trust": 0.0,
            "anticipation": 0.0
        }
        
        # Эмоциональные паттерны
        self._emotional_patterns = {
            "stress_response": {"fear": 0.7, "anger": 0.3},
            "success_response": {"joy": 0.8, "trust": 0.6},
            "failure_response": {"sadness": 0.6, "fear": 0.4},
            "curiosity_response": {"anticipation": 0.7, "surprise": 0.3}
        }
        
        # История эмоциональных изменений
        self._emotion_history: deque = deque(maxlen=1000)
    
    def process_emotion(self, emotion_type: str, intensity: float, context: Dict[str, Any]):
        """
        Обработка эмоции
        
        Args:
            emotion_type: Тип эмоции
            intensity: Интенсивность (0.0 - 1.0)
            context: Контекст эмоции
        """
        try:
            # Валидация эмоции
            if emotion_type not in self._current_emotions:
                self.logger.warning(f"Неизвестный тип эмоции: {emotion_type}")
                return
            
            if not 0.0 <= intensity <= 1.0:
                self.logger.warning(f"Некорректная интенсивность эмоции: {intensity}")
                intensity = max(0.0, min(1.0, intensity))
            
            # Обновление текущего эмоционального состояния
            old_intensity = self._current_emotions[emotion_type]
            self._current_emotions[emotion_type] = intensity
            
            # Сохранение в эмоциональную память
            memory = EmotionalMemory(
                timestamp=time.time(),
                emotion_type=emotion_type,
                intensity=intensity,
                context=context,
                duration=0.0
            )
            self._emotional_memory.append(memory)
            
            # Запись в историю изменений
            self._emotion_history.append({
                "timestamp": time.time(),
                "emotion": emotion_type,
                "old_intensity": old_intensity,
                "new_intensity": intensity,
                "change": intensity - old_intensity,
                "context": context
            })
            
            self.logger.info(f"Обработана эмоция: {emotion_type} (интенсивность: {intensity})")
            
        except Exception as e:
            self.logger.error(f"Ошибка обработки эмоции: {e}")
    
    def apply_emotional_pattern(self, pattern_name: str, intensity: float = 1.0):
        """
        Применение эмоционального паттерна
        
        Args:
            pattern_name: Название паттерна
            intensity: Общая интенсивность паттерна
        """
        if pattern_name not in self._emotional_patterns:
            self.logger.warning(f"Неизвестный эмоциональный паттерн: {pattern_name}")
            return
        
        pattern = self._emotional_patterns[pattern_name]
        context = {"pattern": pattern_name, "intensity": intensity}
        
        for emotion, base_intensity in pattern.items():
            actual_intensity = base_intensity * intensity
            self.process_emotion(emotion, actual_intensity, context)
    
    def get_current_emotional_state(self) -> Dict[str, float]:
        """Получение текущего эмоционального состояния"""
        return self._current_emotions.copy()
    
    def get_emotional_memory(self, limit: int = 100) -> List[EmotionalMemory]:
        """Получение эмоциональной памяти"""
        return list(self._emotional_memory)[-limit:]
    
    def get_emotion_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Получение истории эмоций"""
        return list(self._emotion_history)[-limit:]
    
    def get_dominant_emotion(self) -> Optional[str]:
        """Получение доминирующей эмоции"""
        if not self._current_emotions:
            return None
        
        dominant_emotion = max(self._current_emotions.items(), key=lambda x: x[1])
        return dominant_emotion[0] if dominant_emotion[1] > 0.1 else None
    
    def get_emotional_stability(self) -> float:
        """
        Получение эмоциональной стабильности
        Возвращает значение от 0.0 до 1.0
        """
        if not self._emotion_history:
            return 1.0
        
        # Анализируем последние изменения эмоций
        recent_changes = list(self._emotion_history)[-50:]
        if not recent_changes:
            return 1.0
        
        # Вычисляем среднее изменение
        total_change = sum(abs(change["change"]) for change in recent_changes)
        avg_change = total_change / len(recent_changes)
        
        # Стабильность обратно пропорциональна среднему изменению
        stability = max(0.0, 1.0 - avg_change)
        return stability
    
    def get_emotional_summary(self) -> Dict[str, Any]:
        """Получение эмоционального резюме"""
        dominant_emotion = self.get_dominant_emotion()
        stability = self.get_emotional_stability()
        
        return {
            "current_emotions": self._current_emotions,
            "dominant_emotion": dominant_emotion,
            "emotional_stability": stability,
            "memory_size": len(self._emotional_memory),
            "history_size": len(self._emotion_history),
            "timestamp": time.time()
        }
    
    def decay_emotions(self, decay_rate: float = 0.1):
        """
        Затухание эмоций со временем
        
        Args:
            decay_rate: Скорость затухания (0.0 - 1.0)
        """
        decay_rate = max(0.0, min(1.0, decay_rate))
        
        for emotion in self._current_emotions:
            current_intensity = self._current_emotions[emotion]
            new_intensity = current_intensity * (1.0 - decay_rate)
            self._current_emotions[emotion] = max(0.0, new_intensity)
    
    def reset_emotions(self):
        """Сброс всех эмоций"""
        for emotion in self._current_emotions:
            self._current_emotions[emotion] = 0.0
    
    def export_emotional_state(self) -> str:
        """Экспорт эмоционального состояния"""
        state = {
            "current_emotions": self._current_emotions,
            "emotional_memory": [
                {
                    "timestamp": memory.timestamp,
                    "emotion_type": memory.emotion_type,
                    "intensity": memory.intensity,
                    "context": memory.context,
                    "duration": memory.duration
                }
                for memory in self._emotional_memory
            ],
            "emotion_history": list(self._emotion_history),
            "timestamp": time.time()
        }
        return json.dumps(state, indent=2)
    
    def import_emotional_state(self, state_data: str):
        """Импорт эмоционального состояния"""
        try:
            state = json.loads(state_data)
            
            # Восстанавливаем текущие эмоции
            if "current_emotions" in state:
                self._current_emotions = state["current_emotions"]
            
            # Восстанавливаем эмоциональную память
            if "emotional_memory" in state:
                self._emotional_memory.clear()
                for memory_data in state["emotional_memory"]:
                    memory = EmotionalMemory(
                        timestamp=memory_data["timestamp"],
                        emotion_type=memory_data["emotion_type"],
                        intensity=memory_data["intensity"],
                        context=memory_data["context"],
                        duration=memory_data["duration"]
                    )
                    self._emotional_memory.append(memory)
            
            # Восстанавливаем историю эмоций
            if "emotion_history" in state:
                self._emotion_history.clear()
                for history_item in state["emotion_history"]:
                    self._emotion_history.append(history_item)
            
            self.logger.info("Эмоциональное состояние успешно импортировано")
            
        except Exception as e:
            self.logger.error(f"Ошибка импорта эмоционального состояния: {e}")
    
    def get_emotional_core_status(self) -> Dict[str, Any]:
        """Получение статуса эмоционального ядра"""
        return {
            "status": "operational",
            "memory_size": len(self._emotional_memory),
            "history_size": len(self._emotion_history),
            "dominant_emotion": self.get_dominant_emotion(),
            "emotional_stability": self.get_emotional_stability(),
            "current_emotions": self._current_emotions,
            "timestamp": time.time()
        }
    
    def get_memory_size(self) -> int:
        """Получение размера эмоциональной памяти"""
        return len(self._emotional_memory) + len(self._emotion_history)
    
    def process_input(self, user_input: str) -> Dict[str, Any]:
        """
        Обработка пользовательского ввода для эмоционального анализа
        
        Args:
            user_input: Ввод пользователя
            
        Returns:
            Dict с эмоциональным анализом
        """
        try:
            # Простой анализ тона ввода
            input_lower = user_input.lower()
            
            # Определение эмоционального тона
            emotional_indicators = {
                "joy": ["радость", "счастье", "отлично", "великолепно", "супер", "круто"],
                "sadness": ["грусть", "печаль", "плохо", "ужасно", "отстой"],
                "anger": ["злость", "гнев", "раздражение", "бесит", "ненавижу"],
                "fear": ["страх", "боюсь", "опасно", "страшно", "тревога"],
                "surprise": ["удивительно", "неожиданно", "вау", "ого"],
                "trust": ["доверие", "веришь", "надеюсь", "уверен"],
                "anticipation": ["ожидание", "жду", "интересно", "любопытно"]
            }
            
            # Анализ эмоционального тона
            detected_emotions = {}
            for emotion, indicators in emotional_indicators.items():
                intensity = 0.0
                for indicator in indicators:
                    if indicator in input_lower:
                        intensity += 0.3
                if intensity > 0.0:
                    detected_emotions[emotion] = min(1.0, intensity)
            
            # Если эмоции не обнаружены, используем нейтральное состояние
            if not detected_emotions:
                detected_emotions = {"trust": 0.3}
            
            # Применяем обнаруженные эмоции
            for emotion, intensity in detected_emotions.items():
                self.process_emotion(emotion, intensity, {"input": user_input})
            
            return {
                "detected_emotions": detected_emotions,
                "dominant_emotion": self.get_dominant_emotion(),
                "emotional_stability": self.get_emotional_stability(),
                "response_tone": "positive" if detected_emotions.get("joy", 0) > 0.5 else "neutral"
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка обработки эмоционального ввода: {e}")
            return {
                "detected_emotions": {"trust": 0.3},
                "dominant_emotion": "trust",
                "emotional_stability": 0.5,
                "response_tone": "neutral"
            } 