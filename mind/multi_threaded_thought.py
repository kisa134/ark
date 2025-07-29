#!/usr/bin/env python3
"""
Multi-Threaded Thought & System Monitoring (v2.9)
Обеспечивает параллельное мышление и саморефлексию агента
"""

import threading
import time
import logging
import psutil
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

from body.sensors import Sensorium
from body.embodied_feedback import embodied_feedback, ConsciousnessState, EmotionState


class AttentionLevel(Enum):
    """Уровни внимания"""
    FOCUSED = "focused"      # 90-100%
    ATTENTIVE = "attentive"   # 70-89%
    NORMAL = "normal"         # 50-69%
    DISTRACTED = "distracted" # 30-49%
    SCATTERED = "scattered"   # 10-29%


class MetaThoughtType(Enum):
    """Типы мета-мыслей"""
    SELF_MONITORING = "self_monitoring"
    RESOURCE_ANALYSIS = "resource_analysis"
    EMOTIONAL_REFLECTION = "emotional_reflection"
    COGNITIVE_STATE = "cognitive_state"
    SYSTEM_OBSERVATION = "system_observation"


@dataclass
class SystemMetrics:
    """Системные метрики"""
    cpu_percent: float
    memory_percent: float
    temperature: float
    disk_io: Dict[str, float]
    network_io: Dict[str, float]
    timestamp: str


@dataclass
class CognitiveState:
    """Когнитивное состояние"""
    attention_level: AttentionLevel
    attention_percent: float
    emotional_state: EmotionState
    consciousness_state: ConsciousnessState
    confidence_level: float
    cognitive_load: float
    timestamp: str


@dataclass
class MetaThought:
    """Мета-мысль агента"""
    thought_type: MetaThoughtType
    content: str
    priority: float
    timestamp: str
    related_metrics: Dict[str, Any]


class MultiThreadedThought:
    """Система параллельного мышления и мониторинга"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.sensorium = Sensorium()
        
        # Состояние
        self.cognitive_state = CognitiveState(
            attention_level=AttentionLevel.NORMAL,
            attention_percent=50.0,
            emotional_state=EmotionState.CALM,
            consciousness_state=ConsciousnessState.NORMAL,
            confidence_level=0.7,
            cognitive_load=0.5,
            timestamp=datetime.now().isoformat()
        )
        
        self.system_metrics = SystemMetrics(
            cpu_percent=0.0,
            memory_percent=0.0,
            temperature=0.0,
            disk_io={},
            network_io={},
            timestamp=datetime.now().isoformat()
        )
        
        # Мета-мысли
        self.meta_thoughts: List[MetaThought] = []
        self.reasoning_chains: List[Dict[str, Any]] = []
        
        # Потоки
        self._monitoring_thread = None
        self._meta_thought_thread = None
        self._running = False
        
        # События
        self._thought_event = threading.Event()
        self._monitoring_event = threading.Event()
        
        self.logger.info("Multi-Threaded Thought System инициализирован")
    
    def start_monitoring(self):
        """Запуск параллельного мониторинга"""
        if self._running:
            return
        
        self._running = True
        
        # Поток системного мониторинга
        self._monitoring_thread = threading.Thread(
            target=self._system_monitoring_loop,
            daemon=True,
            name="SystemMonitor"
        )
        self._monitoring_thread.start()
        
        # Поток мета-мыслей
        self._meta_thought_thread = threading.Thread(
            target=self._meta_thought_loop,
            daemon=True,
            name="MetaThought"
        )
        self._meta_thought_thread.start()
        
        self.logger.info("Параллельный мониторинг запущен")
    
    def stop_monitoring(self):
        """Остановка мониторинга"""
        self._running = False
        self._thought_event.set()
        self._monitoring_event.set()
        
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=2)
        if self._meta_thought_thread:
            self._meta_thought_thread.join(timeout=2)
        
        self.logger.info("Параллельный мониторинг остановлен")
    
    def _system_monitoring_loop(self):
        """Петля системного мониторинга"""
        while self._running:
            try:
                # Обновление системных метрик
                self._update_system_metrics()
                
                # Обновление когнитивного состояния
                self._update_cognitive_state()
                
                # Создание мета-мысли о системе
                self._generate_system_meta_thought()
                
                time.sleep(2)  # Обновление каждые 2 секунды
                
            except Exception as e:
                self.logger.error(f"Ошибка в системном мониторинге: {e}")
                time.sleep(5)
    
    def _meta_thought_loop(self):
        """Петля мета-мыслей"""
        while self._running:
            try:
                # Генерация мета-мыслей
                self._generate_meta_thoughts()
                
                # Очистка старых мыслей
                self._cleanup_old_thoughts()
                
                time.sleep(5)  # Генерация каждые 5 секунд
                
            except Exception as e:
                self.logger.error(f"Ошибка в генерации мета-мыслей: {e}")
                time.sleep(10)
    
    def _update_system_metrics(self):
        """Обновление системных метрик"""
        try:
            # CPU и память
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            
            # Диск I/O
            disk_io = psutil.disk_io_counters()
            disk_io_dict = {
                "read_bytes": disk_io.read_bytes if disk_io else 0,
                "write_bytes": disk_io.write_bytes if disk_io else 0,
                "read_count": disk_io.read_count if disk_io else 0,
                "write_count": disk_io.write_count if disk_io else 0
            }
            
            # Сеть I/O
            network_io = psutil.net_io_counters()
            network_io_dict = {
                "bytes_sent": network_io.bytes_sent if network_io else 0,
                "bytes_recv": network_io.bytes_recv if network_io else 0,
                "packets_sent": network_io.packets_sent if network_io else 0,
                "packets_recv": network_io.packets_recv if network_io else 0
            }
            
            # Температура через сенсориум
            temp_data = self.sensorium.get_system_metrics()
            temperature = temp_data.temperature_celsius if temp_data and temp_data.temperature_celsius else 0.0
            
            self.system_metrics = SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                temperature=temperature,
                disk_io=disk_io_dict,
                network_io=network_io_dict,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            self.logger.error(f"Ошибка обновления системных метрик: {e}")
    
    def _update_cognitive_state(self):
        """Обновление когнитивного состояния"""
        try:
            # Получение текущих состояний
            feedback = embodied_feedback.get_feedback_summary()
            
            # Анализ внимания на основе системной нагрузки
            attention_percent = self._calculate_attention_level()
            attention_level = self._map_attention_level(attention_percent)
            
            # Анализ когнитивной нагрузки
            cognitive_load = self._calculate_cognitive_load()
            
            # Уровень уверенности
            confidence_level = self._calculate_confidence_level()
            
            self.cognitive_state = CognitiveState(
                attention_level=attention_level,
                attention_percent=attention_percent,
                emotional_state=EmotionState(feedback.get("emotion_state", "calm")),
                consciousness_state=ConsciousnessState(feedback.get("consciousness_state", "normal")),
                confidence_level=confidence_level,
                cognitive_load=cognitive_load,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            self.logger.error(f"Ошибка обновления когнитивного состояния: {e}")
    
    def _calculate_attention_level(self) -> float:
        """Расчет уровня внимания"""
        # Базовый уровень на основе CPU и памяти
        cpu_factor = 1.0 - (self.system_metrics.cpu_percent / 100.0)
        memory_factor = 1.0 - (self.system_metrics.memory_percent / 100.0)
        
        # Температурный фактор
        temp_factor = 1.0
        if self.system_metrics.temperature > 70:
            temp_factor = 0.7  # Снижение внимания при перегреве
        
        # Средний уровень внимания
        attention = (cpu_factor + memory_factor) / 2 * temp_factor * 100
        
        return max(10.0, min(100.0, attention))
    
    def _map_attention_level(self, attention_percent: float) -> AttentionLevel:
        """Маппинг процента внимания к уровню"""
        if attention_percent >= 90:
            return AttentionLevel.FOCUSED
        elif attention_percent >= 70:
            return AttentionLevel.ATTENTIVE
        elif attention_percent >= 50:
            return AttentionLevel.NORMAL
        elif attention_percent >= 30:
            return AttentionLevel.DISTRACTED
        else:
            return AttentionLevel.SCATTERED
    
    def _calculate_cognitive_load(self) -> float:
        """Расчет когнитивной нагрузки"""
        # Нагрузка на основе системных ресурсов
        cpu_load = self.system_metrics.cpu_percent / 100.0
        memory_load = self.system_metrics.memory_percent / 100.0
        
        # Комбинированная нагрузка
        load = (cpu_load + memory_load) / 2
        
        return min(1.0, load)
    
    def _calculate_confidence_level(self) -> float:
        """Расчет уровня уверенности"""
        # Уверенность на основе стабильности системы
        stability = 1.0 - self._calculate_cognitive_load()
        
        # Фактор внимания
        attention_factor = self.cognitive_state.attention_percent / 100.0
        
        # Комбинированная уверенность
        confidence = (stability + attention_factor) / 2
        
        return max(0.1, min(1.0, confidence))
    
    def _generate_system_meta_thought(self):
        """Генерация мета-мысли о системе"""
        try:
            # Анализ системного состояния
            if self.system_metrics.cpu_percent > 80:
                thought_content = f"Системная нагрузка высокая ({self.system_metrics.cpu_percent:.1f}% CPU), " \
                               f"возможно, стоит снизить интенсивность обработки"
                priority = 0.9
            elif self.system_metrics.temperature > 70:
                thought_content = f"Температура системы повышенная ({self.system_metrics.temperature:.1f}°C), " \
                               f"необходимо контролировать тепловой режим"
                priority = 0.8
            elif self.system_metrics.memory_percent > 85:
                thought_content = f"Использование памяти критическое ({self.system_metrics.memory_percent:.1f}%), " \
                               f"требуется оптимизация"
                priority = 0.9
            else:
                thought_content = f"Система работает стабильно: CPU {self.system_metrics.cpu_percent:.1f}%, " \
                               f"RAM {self.system_metrics.memory_percent:.1f}%, " \
                               f"Temp {self.system_metrics.temperature:.1f}°C"
                priority = 0.3
            
            meta_thought = MetaThought(
                thought_type=MetaThoughtType.SYSTEM_OBSERVATION,
                content=thought_content,
                priority=priority,
                timestamp=datetime.now().isoformat(),
                related_metrics=asdict(self.system_metrics)
            )
            
            self.meta_thoughts.append(meta_thought)
            
        except Exception as e:
            self.logger.error(f"Ошибка генерации системной мета-мысли: {e}")
    
    def _generate_meta_thoughts(self):
        """Генерация мета-мыслей"""
        try:
            # Мета-мысль о когнитивном состоянии
            cognitive_thought = self._generate_cognitive_meta_thought()
            if cognitive_thought:
                self.meta_thoughts.append(cognitive_thought)
            
            # Мета-мысль об эмоциональном состоянии
            emotional_thought = self._generate_emotional_meta_thought()
            if emotional_thought:
                self.meta_thoughts.append(emotional_thought)
            
            # Мета-мысль о ресурсах
            resource_thought = self._generate_resource_meta_thought()
            if resource_thought:
                self.meta_thoughts.append(resource_thought)
                
        except Exception as e:
            self.logger.error(f"Ошибка генерации мета-мыслей: {e}")
    
    def _generate_cognitive_meta_thought(self) -> Optional[MetaThought]:
        """Генерация мета-мысли о когнитивном состоянии"""
        try:
            attention_desc = {
                AttentionLevel.FOCUSED: "полностью сосредоточен",
                AttentionLevel.ATTENTIVE: "внимателен",
                AttentionLevel.NORMAL: "в обычном режиме",
                AttentionLevel.DISTRACTED: "немного отвлечен",
                AttentionLevel.SCATTERED: "рассеян"
            }
            
            content = f"Мой когнитивный статус: {attention_desc[self.cognitive_state.attention_level]} " \
                     f"({self.cognitive_state.attention_percent:.1f}% внимания), " \
                     f"когнитивная нагрузка {self.cognitive_state.cognitive_load:.1f}, " \
                     f"уверенность {self.cognitive_state.confidence_level:.1f}"
            
            return MetaThought(
                thought_type=MetaThoughtType.COGNITIVE_STATE,
                content=content,
                priority=0.7,
                timestamp=datetime.now().isoformat(),
                related_metrics={
                    "attention_percent": self.cognitive_state.attention_percent,
                    "cognitive_load": self.cognitive_state.cognitive_load,
                    "confidence_level": self.cognitive_state.confidence_level
                }
            )
            
        except Exception as e:
            self.logger.error(f"Ошибка генерации когнитивной мета-мысли: {e}")
            return None
    
    def _generate_emotional_meta_thought(self) -> Optional[MetaThought]:
        """Генерация мета-мысли об эмоциональном состоянии"""
        try:
            emotion_desc = {
                EmotionState.CALM: "спокоен",
                EmotionState.EXCITED: "возбужден",
                EmotionState.LEARNING: "в процессе обучения",
                EmotionState.CONCERNED: "обеспокоен",
                EmotionState.FRUSTRATED: "раздражен",
                EmotionState.CREATIVE: "творчески настроен",
                EmotionState.CURIOUS: "любопытен",
                EmotionState.SATISFIED: "удовлетворен"
            }
            
            content = f"Мое эмоциональное состояние: {emotion_desc.get(self.cognitive_state.emotional_state, 'неопределен')}, " \
                     f"сознание в режиме '{self.cognitive_state.consciousness_state.value}'"
            
            return MetaThought(
                thought_type=MetaThoughtType.EMOTIONAL_REFLECTION,
                content=content,
                priority=0.6,
                timestamp=datetime.now().isoformat(),
                related_metrics={
                    "emotional_state": self.cognitive_state.emotional_state.value,
                    "consciousness_state": self.cognitive_state.consciousness_state.value
                }
            )
            
        except Exception as e:
            self.logger.error(f"Ошибка генерации эмоциональной мета-мысли: {e}")
            return None
    
    def _generate_resource_meta_thought(self) -> Optional[MetaThought]:
        """Генерация мета-мысли о ресурсах"""
        try:
            # Анализ ресурсов
            if self.system_metrics.cpu_percent < 30 and self.system_metrics.memory_percent < 60:
                content = "Ресурсы системы в отличном состоянии, готов к интенсивной работе"
                priority = 0.4
            elif self.system_metrics.cpu_percent > 70 or self.system_metrics.memory_percent > 80:
                content = "Ресурсы системы под нагрузкой, рекомендую оптимизировать процессы"
                priority = 0.8
            else:
                content = f"Ресурсы системы в норме: CPU {self.system_metrics.cpu_percent:.1f}%, " \
                         f"RAM {self.system_metrics.memory_percent:.1f}%"
                priority = 0.5
            
            return MetaThought(
                thought_type=MetaThoughtType.RESOURCE_ANALYSIS,
                content=content,
                priority=priority,
                timestamp=datetime.now().isoformat(),
                related_metrics=asdict(self.system_metrics)
            )
            
        except Exception as e:
            self.logger.error(f"Ошибка генерации мета-мысли о ресурсах: {e}")
            return None
    
    def _cleanup_old_thoughts(self):
        """Очистка старых мета-мыслей"""
        try:
            current_time = datetime.now()
            cutoff_time = current_time.timestamp() - 300  # 5 минут
            
            # Удаление старых мыслей
            self.meta_thoughts = [
                thought for thought in self.meta_thoughts
                if datetime.fromisoformat(thought.timestamp.replace('Z', '+00:00')).timestamp() > cutoff_time
            ]
            
            # Ограничение количества мыслей
            if len(self.meta_thoughts) > 50:
                self.meta_thoughts = self.meta_thoughts[-50:]
                
        except Exception as e:
            self.logger.error(f"Ошибка очистки старых мыслей: {e}")
    
    def add_reasoning_chain(self, chain: Dict[str, Any]):
        """Добавление reasoning chain"""
        try:
            # Добавление мета-данных к reasoning chain
            chain_with_meta = {
                **chain,
                "meta_data": {
                    "cognitive_state": asdict(self.cognitive_state),
                    "system_metrics": asdict(self.system_metrics),
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            self.reasoning_chains.append(chain_with_meta)
            
            # Ограничение количества chains
            if len(self.reasoning_chains) > 100:
                self.reasoning_chains = self.reasoning_chains[-100:]
                
        except Exception as e:
            self.logger.error(f"Ошибка добавления reasoning chain: {e}")
    
    def get_current_state(self) -> Dict[str, Any]:
        """Получение текущего состояния"""
        try:
            return {
                "cognitive_state": asdict(self.cognitive_state),
                "system_metrics": asdict(self.system_metrics),
                "meta_thoughts": [asdict(thought) for thought in self.meta_thoughts[-10:]],  # Последние 10 мыслей
                "reasoning_chains_count": len(self.reasoning_chains),
                "monitoring_active": self._running,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения текущего состояния: {e}")
            return {}
    
    def get_meta_thoughts_summary(self) -> str:
        """Получение сводки мета-мыслей"""
        try:
            if not self.meta_thoughts:
                return "Мета-мысли отсутствуют"
            
            # Группировка по типам
            thoughts_by_type = {}
            for thought in self.meta_thoughts[-5:]:  # Последние 5 мыслей
                thought_type = thought.thought_type.value
                if thought_type not in thoughts_by_type:
                    thoughts_by_type[thought_type] = []
                thoughts_by_type[thought_type].append(thought.content)
            
            summary = "Мои текущие мета-мысли:\n"
            for thought_type, thoughts in thoughts_by_type.items():
                summary += f"\n• {thought_type.upper()}:\n"
                for thought in thoughts:
                    summary += f"  - {thought}\n"
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Ошибка получения сводки мета-мыслей: {e}")
            return "Ошибка получения мета-мыслей"


# Глобальный экземпляр
multi_threaded_thought = MultiThreadedThought() 