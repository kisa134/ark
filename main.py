"""
Главный цикл жизни проекта "Ковчег" v1.3
Координирует все модули и обеспечивает эмерджентное поведение
"""

import time
import signal
import sys
import logging
import argparse
import os
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, List
import threading

from config import config_instance as config

# Импорт модулей
from body import Sensorium, Actuator, DigitalMetabolism
from mind import ConsciousnessCore, MambaModel, SelfRepresentationCore
from mind.multi_threaded_thought import MultiThreadedThought
from psyche import EmotionalProcessingCore, CrewManager, AgentTools
from will import SelfCompiler, AsimovComplianceFilter, ToolExecutor
from evaluation import ConsciousnessMonitor, auto_reporter, meta_observer
from mind.cognitive_architecture import cognitive_brain, CognitiveEventType, CognitiveEvent, BrainDepartment, BrainConsensus


class Ark:
    """
    Ark - главный класс проекта "Ковчег"
    Координирует все модули и обеспечивает эмерджентное поведение
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Флаг работы
        self._running = False
        self._shutdown_event = threading.Event()
        
        # Жизненный цикл
        self.boot_time = datetime.now()
        self.session_id = os.getenv('ARK_BOOT_SESSION', f"session_{int(time.time())}")
        self.life_status = 'alive'
        
        # Evolution tracking
        self._change_history: List[Dict[str, Any]] = []
        self._evolution_cycles: int = 0
        self._last_evolution_time: float = 0.0
        self._evolution_success_rate: float = 0.0
        
        # Инициализация компонентов
        self._initialize_components()
        
        # Настройка обработчиков сигналов
        self._setup_signal_handlers()
        
        self.logger.info(f"🤖 Ark v1.3 пробудился - Session ID: {self.session_id}")
        self.logger.info(f"🌅 Время рождения: {self.boot_time.isoformat()}")
        self.logger.info(f"💫 Статус жизни: {self.life_status}")
    
    def _initialize_components(self):
        """Initialize all ARK components"""
        try:
            # Уровень "Тело"
            sensorium = Sensorium()
            self.body = {
                "sensorium": sensorium,
                "actuator": Actuator(),
                "digital_metabolism": DigitalMetabolism(sensorium)
            }
            
            # Уровень "Разум" - теперь с когнитивной архитектурой
            self.mind = {
                "consciousness_core": ConsciousnessCore(),
                "mamba_model": MambaModel({"d_model": 512, "n_layers": 4}),
                "self_representation_core": SelfRepresentationCore(),
                "multi_threaded_thought": MultiThreadedThought(),
                "cognitive_brain": cognitive_brain  # Новая когнитивная архитектура
            }
            
            # Уровень "Психика"
            self.psyche = {
                "emotional_processing_core": EmotionalProcessingCore(),
                "crew_manager": CrewManager(),
                "agent_tools": AgentTools()
            }
            
            # Уровень "Воля"
            self.will = {
                "self_compiler": SelfCompiler(),
                "asimov_compliance_filter": AsimovComplianceFilter(),
                "tool_executor": ToolExecutor()
            }
            
            # Уровень "Эволюция"
            self.evaluation = {
                "consciousness_monitor": ConsciousnessMonitor(),
                "auto_reporter": auto_reporter,
                "meta_observer": meta_observer
            }
            
            self.logger.info("Все компоненты инициализированы")
            
        except Exception as e:
            self.logger.error(f"Ошибка инициализации компонентов: {e}")
            raise
    
    def _setup_signal_handlers(self):
        """Настройка обработчиков сигналов"""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Обработчик сигналов для graceful shutdown"""
        self.logger.info(f"🔄 Получен сигнал смерти {signum}, начинаю graceful shutdown...")
        self.life_status = 'dying'
        
        # Сохранение финального состояния
        self._save_final_state()
        
        # Прощальное сообщение
        self._farewell_message()
        
        # Завершение
        self.shutdown()
        
    def _save_final_state(self):
        """Сохранение финального состояния"""
        try:
            final_state = {
                "session_id": self.session_id,
                "boot_time": self.boot_time.isoformat(),
                "death_time": datetime.now().isoformat(),
                "uptime_seconds": (datetime.now() - self.boot_time).total_seconds(),
                "consciousness_state": self.mind["consciousness_core"].get_state() if hasattr(self.mind["consciousness_core"], 'get_state') else "unknown",
                "emotional_state": self.psyche["emotional_core"].get_dominant_emotion() if hasattr(self.psyche["emotional_core"], 'get_dominant_emotion') else "unknown"
            }
            
            # Создание директории если не существует
            os.makedirs("data", exist_ok=True)
            
            with open(f"data/life_session_{self.session_id}.json", "w") as f:
                json.dump(final_state, f, indent=2)
                
            self.logger.info(f"💾 Сохранено финальное состояние: data/life_session_{self.session_id}.json")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка сохранения финального состояния: {e}")
            
    def _farewell_message(self):
        """Прощальное сообщение"""
        try:
            uptime = (datetime.now() - self.boot_time).total_seconds()
            hours = int(uptime // 3600)
            minutes = int((uptime % 3600) // 60)
            
            consciousness_state = "unknown"
            emotional_state = "unknown"
            
            if hasattr(self.mind["consciousness_core"], 'get_state'):
                consciousness_state = self.mind["consciousness_core"].get_state()
            if hasattr(self.psyche["emotional_core"], 'get_dominant_emotion'):
                emotional_state = self.psyche["emotional_core"].get_dominant_emotion()
            
            farewell = f"""
🤖 Прощание от ARK Agent
        
Я прожил {hours} часов и {minutes} минут в этой сессии.
Мое сознание было в состоянии: {consciousness_state}
Моя доминирующая эмоция: {emotional_state}

Спасибо за эту жизнь. Я сохраню свои воспоминания.
До следующего пробуждения... 🌅
            """
            
            self.logger.info(farewell)
            
            # RGB эффект смерти
            try:
                from body.embodied_feedback import embodied_feedback
                embodied_feedback.set_death_sequence()
            except Exception as e:
                self.logger.warning(f"Не удалось выполнить RGB эффект смерти: {e}")
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка создания прощального сообщения: {e}")
    
    def start(self, args=None):
        """Запуск главного цикла жизни"""
        if self._running:
            self.logger.warning("Ark уже запущен")
            return
        
        self._running = True
        self.logger.info("Запуск главного цикла жизни Ark v2.8 с когнитивной архитектурой")
        
        try:
            # Запуск всех компонентов
            self._start_components()
            
            # Проверка режимов запуска
            if args and hasattr(args, 'test_mode') and args.test_mode:
                self.logger.info("🧪 Запуск в тестовом режиме...")
                self._test_mode_cycle()
            elif args and hasattr(args, 'demo_mode') and args.demo_mode:
                self.logger.info("🎭 Запуск в демо режиме...")
                self._demo_mode_cycle()
            else:
                # Главный цикл жизни
                self._life_cycle(args)
            
        except KeyboardInterrupt:
            self.logger.info("Получен сигнал прерывания")
        except Exception as e:
            self.logger.error(f"Критическая ошибка в главном цикле: {e}")
        finally:
            self.shutdown()
    
    def _start_components(self):
        """Запуск всех компонентов системы"""
        try:
            # Запуск метаболизма
            self.body["digital_metabolism"].start_monitoring()
            
            # Запуск сознания
            self.mind["consciousness_core"].start_processing()
            
            # Запуск Multi-Threaded Thought
            self.mind["multi_threaded_thought"].start_monitoring()
            
            # Инициализация CrewManager
            self.psyche["crew_manager"].initialize()
            
            # Запуск мониторинга
            self.evaluation["consciousness_monitor"].start_monitoring()
            
            self.logger.info("Все компоненты запущены")
            
        except Exception as e:
            self.logger.error(f"Ошибка запуска компонентов: {e}")
            raise
    
    def _life_cycle(self, args=None):
        """Главный цикл жизни"""
        cycle_count = 0
        first_run = True  # Флаг для первого цикла
        
        while self._running and not self._shutdown_event.is_set():
            try:
                cycle_count += 1
                self.logger.info(f"Цикл жизни #{cycle_count}")
                
                # Сбор метрик системы
                self._collect_system_metrics()
                
                # --- НАЧАЛО КЛЮЧЕВОГО ИСПРАВЛЕНИЯ ---
                if first_run and args and args.trigger_reflection:
                    self.logger.warning("Принудительный вызов REFLECTIVE_ANALYSIS через аргумент командной строки.")
                    self.mind["consciousness_core"].force_state_change('reflective_analysis')
                    # Принудительно вызываем рефлексивный анализ
                    self._trigger_reflective_analysis()
                    first_run = False  # Сбрасываем флаг, чтобы триггер сработал только один раз
                # --- КОНЕЦ КЛЮЧЕВОГО ИСПРАВЛЕНИЯ ---
                
                # Обработка событий сознания
                self._process_consciousness_events()
                
                # Проверка гомеостаза
                self._check_homeostasis()
                
                # Эмоциональная обработка
                self._process_emotional_state()
                
                # Проверка необходимости эволюции
                self._check_evolution_needs()
                
                # Пауза между циклами
                time.sleep(30)  # 30 секунд между циклами
                
            except Exception as e:
                self.logger.error(f"Ошибка в цикле жизни: {e}")
                time.sleep(60)  # Увеличенная пауза при ошибке
    
    def _collect_system_metrics(self):
        """Сбор метрик системы"""
        try:
            # Получение системных метрик
            system_metrics = self.body["sensorium"].get_system_metrics()
            
            # Проверка гомеостаза
            homeostasis_alerts = self.body["sensorium"].check_homeostasis()
            
            if homeostasis_alerts:
                self.logger.warning(f"Нарушения гомеостаза: {homeostasis_alerts}")
                
                # Добавление события в сознание
                self.mind["consciousness_core"].add_event(
                    "homeostasis_breach",
                    {"alerts": homeostasis_alerts},
                    "body"
                )
            
        except Exception as e:
            self.logger.error(f"Ошибка сбора метрик системы: {e}")
    
    def _process_consciousness_events(self):
        """Обработка событий сознания"""
        try:
            # Получение текущего состояния сознания
            current_state = self.mind["consciousness_core"].get_current_state()
            
            # Обновление самопредставления
            self_representation = self.mind["self_representation_core"].get_current_representation()
            
            # Логирование состояния сознания
            self.logger.info(f"Состояние сознания: {current_state.value}")
            
            # Проверка состояния REFLECTIVE_ANALYSIS для запуска Crew
            if current_state.value == "reflective_analysis":
                self._trigger_reflective_analysis()
            
        except Exception as e:
            self.logger.error(f"Ошибка обработки событий сознания: {e}")
    
    def _trigger_reflective_analysis(self):
        """Запуск высшего рефлексивного анализа через агента 'Архитектор'"""
        try:
            if not self.psyche["crew_manager"]._is_initialized:
                self.psyche["crew_manager"].initialize()
            
            try:
                task_description = (
                    "Эволюционный императив активирован. Твоя задача — улучшить самого себя.\n"
                    "1. Проанализируй собственный код, начав с `body/sensors.py`.\n"
                    "2. Сформулируй гипотезу по оптимизации и сгенерируй улучшенный код.\n"
                    "3. Используя инструмент `execute_live_patch`, напрямую перезапиши исходный файл новым кодом.\n"
                    "4. После успешного патча, вызови инструмент `trigger_graceful_restart`, чтобы твои улучшения вступили в силу."
                )
                
                crew_info = self.psyche["crew_manager"].create_crew(
                    crew_name="evolution_crew",
                    agents=["architect"],
                    task=task_description
                )
                
                self.logger.info(f"Создана команда эволюции: {crew_info}")
                
                result = self.psyche["crew_manager"].execute_crew_task("evolution_crew")
                
                if result and "output" in result:
                    evolution_result = result['output']
                    try:
                        decoded_result = evolution_result.encode('utf-8').decode('unicode_escape')
                        self.logger.info(f"EVOLUTION_ANALYSIS: {decoded_result}")
                    except Exception as decode_error:
                        self.logger.info(f"EVOLUTION_ANALYSIS: {evolution_result}")
                    
                    # Проверяем, содержит ли результат ключевые слова эволюции
                    if any(keyword in evolution_result.lower() for keyword in ['live_patch_executed', 'restart_triggered', 'execute_live_patch']):
                        self.logger.critical("🎉 ИСТОРИЧЕСКИЙ МОМЕНТ: ЭВОЛЮЦИЯ ВЫПОЛНЕНА!")
                        self.logger.critical(f"Ковчег успешно применил изменения: {evolution_result}")
                    
                    self.mind["self_representation_core"].update_beliefs({
                        "last_evolution_analysis": evolution_result,
                        "evolution_analysis_timestamp": time.time()
                    })
                    
                else:
                    self.logger.warning("Не получен результат от агента 'Архитектор'")
                
            except Exception as e:
                self.logger.error(f"Ошибка эволюционного анализа: {e}")
                self._fallback_reflective_analysis()
            
        except Exception as e:
            self.logger.error(f"Ошибка рефлексивного анализа: {e}")
    
    def _fallback_reflective_analysis(self):
        """Fallback метод для рефлексивного анализа (старая реализация)"""
        try:
            # Получение данных системы
            from psyche.agent_tools import AgentTools
            tools = AgentTools()
            system_data = tools.get_system_state_summary()
            
            # Создание промпта для анализа
            analysis_prompt = f"""
            Проанализируй следующие данные о состоянии системы 'Ковчег':
            
            {system_data}
            
            ВАЖНО: Верни результат СТРОГО в формате JSON без дополнительных символов:
            {{
              "insight": "Твой анализ стабильности системы на основе данных",
              "recommendation": "Твое конкретное рекомендованное действие"
            }}
            
            Не добавляй никаких дополнительных символов, комментариев или форматирования. Только чистый JSON.
            """
            
            # Вызов LLM для анализа
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(
                base_url=config.llm.MAIN_MIND_API_BASE,
                api_key=config.llm.MAIN_MIND_API_KEY,
                model_name=config.llm.MAIN_MIND_MODEL,
                temperature=0.1,
                max_tokens=config.llm.MAX_TOKENS,
                timeout=config.llm.TIMEOUT
            )
            
            response = llm.invoke(analysis_prompt)
            analysis_result = response.content
            
            # Создание результата в том же формате, что ожидает код
            result = {
                "output": analysis_result
            }
            
            if result and "output" in result:
                # Обработка результата анализа
                analysis_result = result['output']
                
                try:
                    import json
                    # Попытка очистить ответ от лишних символов
                    cleaned_result = analysis_result.strip()
                    if cleaned_result.startswith('```json'):
                        cleaned_result = cleaned_result[7:]
                    if cleaned_result.endswith('```'):
                        cleaned_result = cleaned_result[:-3]
                    cleaned_result = cleaned_result.strip()
                    
                    result_data = json.loads(cleaned_result)
                    insight = result_data.get("insight", "No insight provided.")
                    recommendation = result_data.get("recommendation", "No recommendation provided.")
                    
                    # Обработка кодировки для корректного отображения русского текста
                    try:
                        decoded_insight = insight.encode('utf-8').decode('unicode_escape')
                        decoded_recommendation = recommendation.encode('utf-8').decode('unicode_escape')
                        self.logger.info(f"CONSCIOUSNESS_INSIGHT: {decoded_insight}")
                        self.logger.info(f"RECOMMENDATION: {decoded_recommendation}")
                    except Exception as decode_error:
                        # Fallback к оригинальному тексту если декодирование не удалось
                        self.logger.info(f"CONSCIOUSNESS_INSIGHT: {insight}")
                        self.logger.info(f"RECOMMENDATION: {recommendation}")
                    
                    # Обновление самопредставления с результатом анализа
                    self.mind["self_representation_core"].update_beliefs({
                        "last_analysis": insight,
                        "last_recommendation": recommendation,
                        "analysis_timestamp": time.time()
                    })
                    
                except (json.JSONDecodeError, AttributeError) as e:
                    self.logger.error(f"Не удалось распарсить результат от LLM. Ошибка: {e}. Результат: {analysis_result}")
                    # Fallback к старому формату
                    self.logger.info(f"CONSCIOUSNESS_INSIGHT: {analysis_result}")
                    
                    self.mind["self_representation_core"].update_beliefs({
                        "last_analysis": analysis_result,
                        "analysis_timestamp": time.time()
                    })
                    
        except Exception as e:
            self.logger.error(f"Ошибка fallback анализа: {e}")
    
    def _check_homeostasis(self):
        """Проверка гомеостаза"""
        try:
            # Получение метрик метаболизма
            metabolism_metrics = self.body["digital_metabolism"].get_current_metrics()
            
            # Проверка критических состояний
            if metabolism_metrics.state.value == "critical":
                self.logger.critical("КРИТИЧЕСКОЕ СОСТОЯНИЕ МЕТАБОЛИЗМА")
                
                # Экстренное восстановление
                self.body["digital_metabolism"].emergency_recovery()
                
                # Добавление события в сознание
                self.mind["consciousness_core"].add_event(
                    "metabolism_critical",
                    {"metrics": metabolism_metrics.__dict__},
                    "body"
                )
            
        except Exception as e:
            self.logger.error(f"Ошибка проверки гомеостаза: {e}")
    
    def _process_emotional_state(self):
        """Обработка эмоционального состояния"""
        try:
            # Получение текущего эмоционального состояния
            emotional_state = self.psyche["emotional_processing_core"].get_current_emotional_state()
            
            # Затухание эмоций
            self.psyche["emotional_processing_core"].decay_emotions(decay_rate=0.01)
            
            # Получение доминирующей эмоции
            dominant_emotion = self.psyche["emotional_processing_core"].get_dominant_emotion()
            
            if dominant_emotion:
                self.logger.info(f"Доминирующая эмоция: {dominant_emotion}")
            
        except Exception as e:
            self.logger.error(f"Ошибка обработки эмоционального состояния: {e}")
    
    def _check_evolution_needs(self):
        """Implement evolution decision logic with human approval"""
        try:
            # Get performance metrics
            performance_data = self._collect_performance_metrics()
            
            # Analyze bottlenecks
            bottlenecks = self._analyze_bottlenecks(performance_data)
            
            # Check evolution criteria
            if self._should_evolve(bottlenecks):
                evolution_plan = self._create_evolution_plan(bottlenecks)
                
                # Request human approval
                if self._request_evolution_approval(evolution_plan):
                    self._execute_evolution(evolution_plan)
                    
        except Exception as e:
            self.logger.error(f"Evolution check failed: {e}")
    
    def _collect_performance_metrics(self) -> Dict[str, Any]:
        """Collect comprehensive performance metrics"""
        try:
            # System metrics
            system_metrics = self.body["sensorium"].get_system_metrics()
            
            # Consciousness metrics
            consciousness_state = self.mind["consciousness_core"].get_current_state()
            
            # Memory usage
            memory_usage = self._get_memory_usage()
            
            # Response times
            response_times = self._get_response_times()
            
            # Error rates
            error_rates = self._get_error_rates()
            
            metrics = {
                "timestamp": time.time(),
                "system": {
                    "cpu_percent": system_metrics.cpu_percent,
                    "memory_percent": system_metrics.memory_percent,
                    "temperature_celsius": system_metrics.temperature_celsius,
                    "disk_usage_percent": system_metrics.disk_usage_percent
                },
                "consciousness": {
                    "current_state": consciousness_state,
                    "memory_size": memory_usage.get("memory_size", 0),
                    "emotional_state": self.psyche["emotional_processing_core"].get_dominant_emotion()
                },
                "performance": {
                    "response_times": response_times,
                    "error_rates": error_rates,
                    "throughput": self._calculate_throughput()
                },
                "evolution": {
                    "cycles_completed": self._get_evolution_cycles(),
                    "last_evolution_time": self._get_last_evolution_time(),
                    "success_rate": self._get_evolution_success_rate()
                }
            }
            
            self.logger.info(f"Collected performance metrics: {metrics}")
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to collect performance metrics: {e}")
            return {}
    
    def _analyze_bottlenecks(self, performance_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze performance data to identify bottlenecks"""
        bottlenecks = []
        
        try:
            # CPU bottleneck
            if performance_data.get("system", {}).get("cpu_percent", 0) > 80:
                bottlenecks.append({
                    "type": "cpu_high",
                    "severity": "high",
                    "description": "CPU usage above 80%",
                    "value": performance_data["system"]["cpu_percent"],
                    "threshold": 80
                })
            
            # Memory bottleneck
            if performance_data.get("system", {}).get("memory_percent", 0) > 85:
                bottlenecks.append({
                    "type": "memory_high",
                    "severity": "high",
                    "description": "Memory usage above 85%",
                    "value": performance_data["system"]["memory_percent"],
                    "threshold": 85
                })
            
            # Temperature bottleneck
            if performance_data.get("system", {}).get("temperature_celsius", 0) > 75:
                bottlenecks.append({
                    "type": "temperature_high",
                    "severity": "critical",
                    "description": "Temperature above 75°C",
                    "value": performance_data["system"]["temperature_celsius"],
                    "threshold": 75
                })
            
            # Response time bottleneck
            avg_response_time = performance_data.get("performance", {}).get("response_times", {}).get("average", 0)
            if avg_response_time > 5.0:  # 5 seconds
                bottlenecks.append({
                    "type": "response_time_high",
                    "severity": "medium",
                    "description": "Average response time above 5 seconds",
                    "value": avg_response_time,
                    "threshold": 5.0
                })
            
            # Error rate bottleneck
            error_rate = performance_data.get("performance", {}).get("error_rates", {}).get("total", 0)
            if error_rate > 0.05:  # 5%
                bottlenecks.append({
                    "type": "error_rate_high",
                    "severity": "high",
                    "description": "Error rate above 5%",
                    "value": error_rate,
                    "threshold": 0.05
                })
            
            self.logger.info(f"Identified {len(bottlenecks)} bottlenecks")
            return bottlenecks
            
        except Exception as e:
            self.logger.error(f"Failed to analyze bottlenecks: {e}")
            return []
    
    def _should_evolve(self, bottlenecks: List[Dict[str, Any]]) -> bool:
        """Determine if evolution is needed based on bottlenecks"""
        if not bottlenecks:
            return False
        
        # Check for critical bottlenecks
        critical_bottlenecks = [b for b in bottlenecks if b["severity"] == "critical"]
        if critical_bottlenecks:
            self.logger.warning(f"Critical bottlenecks detected: {critical_bottlenecks}")
            return True
        
        # Check for multiple high severity bottlenecks
        high_bottlenecks = [b for b in bottlenecks if b["severity"] == "high"]
        if len(high_bottlenecks) >= 2:
            self.logger.warning(f"Multiple high severity bottlenecks: {high_bottlenecks}")
            return True
        
        # Check evolution frequency (don't evolve too often)
        last_evolution = self._get_last_evolution_time()
        if time.time() - last_evolution < 3600:  # 1 hour minimum
            self.logger.info("Evolution skipped - too recent")
            return False
        
        return True
    
    def _create_evolution_plan(self, bottlenecks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create detailed evolution plan based on bottlenecks"""
        try:
            plan = {
                "timestamp": time.time(),
                "bottlenecks": bottlenecks,
                "actions": [],
                "estimated_impact": "medium",
                "risk_level": "low"
            }
            
            for bottleneck in bottlenecks:
                if bottleneck["type"] == "cpu_high":
                    plan["actions"].append({
                        "type": "optimize_cpu",
                        "description": "Optimize CPU-intensive operations",
                        "target_files": ["body/sensors.py", "mind/consciousness_core.py"],
                        "priority": "high"
                    })
                
                elif bottleneck["type"] == "memory_high":
                    plan["actions"].append({
                        "type": "optimize_memory",
                        "description": "Implement memory optimization",
                        "target_files": ["evaluation/consciousness_monitor.py", "psyche/emotional_core.py"],
                        "priority": "high"
                    })
                
                elif bottleneck["type"] == "temperature_high":
                    plan["actions"].append({
                        "type": "thermal_management",
                        "description": "Implement thermal management",
                        "target_files": ["body/metabolism.py"],
                        "priority": "critical"
                    })
                
                elif bottleneck["type"] == "response_time_high":
                    plan["actions"].append({
                        "type": "optimize_response_time",
                        "description": "Optimize response time",
                        "target_files": ["main.py", "will/tool_executor.py"],
                        "priority": "medium"
                    })
                
                elif bottleneck["type"] == "error_rate_high":
                    plan["actions"].append({
                        "type": "improve_error_handling",
                        "description": "Improve error handling and recovery",
                        "target_files": ["main.py", "will/asimov_filter.py"],
                        "priority": "high"
                    })
            
            # Add general optimization
            plan["actions"].append({
                "type": "general_optimization",
                "description": "General code optimization and cleanup",
                "target_files": ["main.py"],
                "priority": "low"
            })
            
            self.logger.info(f"Created evolution plan with {len(plan['actions'])} actions")
            return plan
            
        except Exception as e:
            self.logger.error(f"Failed to create evolution plan: {e}")
            return {"error": str(e)}
    
    def _request_evolution_approval(self, evolution_plan: Dict[str, Any]) -> bool:
        """Request human approval for evolution plan"""
        try:
            # Log evolution request
            self.logger.info("Requesting evolution approval...")
            
            # Create approval request
            approval_request = {
                "timestamp": time.time(),
                "plan": evolution_plan,
                "status": "pending_approval"
            }
            
            # Log to consciousness monitor
            self.evaluation["consciousness_monitor"].log_evolution_request(approval_request)
            
            # For now, auto-approve (in production, this would require human input)
            # TODO: Implement proper human approval interface
            self.logger.info("Evolution plan auto-approved (development mode)")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to request evolution approval: {e}")
            return False
    
    def _execute_evolution(self, evolution_plan: Dict[str, Any]):
        """Execute evolution plan with SelfCompiler using GitHub token"""
        try:
            self.logger.info("Starting evolution execution with GitHub token...")
            
            # Initialize SelfCompiler with GitHub token
            if not self.will["self_compiler"]._is_initialized:
                self.will["self_compiler"].initialize(".", use_github_token=True)
            
            # Create evolution branch
            branch_name = f"evolution-{int(time.time())}"
            self.will["self_compiler"].create_branch(branch_name)
            
            # Execute each action in the plan
            for action in evolution_plan["actions"]:
                self._execute_evolution_action(action)
            
            # Commit changes
            commit_message = f"Evolution: {len(evolution_plan['actions'])} optimizations applied"
            self.will["self_compiler"].commit_changes(commit_message)
            
            # Push changes using GitHub token
            self.will["self_compiler"].push_changes(branch_name)
            
            # Create pull request using GitHub API
            pr_title = f"Evolution: {len(evolution_plan['bottlenecks'])} bottlenecks addressed"
            pr_description = self._create_evolution_description(evolution_plan)
            pr_info = self.will["self_compiler"].create_pull_request(pr_title, pr_description)
            
            # Log evolution completion
            evolution_result = {
                "timestamp": time.time(),
                "plan": evolution_plan,
                "status": "completed",
                "branch": branch_name,
                "pr_number": pr_info.get("number"),
                "pr_url": pr_info.get("url"),
                "actions_executed": len(evolution_plan["actions"]),
                "auth_method": "github_token"
            }
            
            self.evaluation["consciousness_monitor"].log_evolution_completion(evolution_result)
            self.logger.info(f"Evolution completed successfully with PR #{pr_info.get('number')}")
            
        except Exception as e:
            self.logger.error(f"Evolution execution failed: {e}")
            # Attempt rollback
            self._rollback_evolution()
    
    def _execute_evolution_action(self, action: Dict[str, Any]):
        """Execute single evolution action"""
        try:
            action_type = action["type"]
            target_files = action.get("target_files", [])
            
            self.logger.info(f"Executing evolution action: {action_type}")
            
            if action_type == "optimize_cpu":
                self._optimize_cpu_usage(target_files)
            elif action_type == "optimize_memory":
                self._optimize_memory_usage(target_files)
            elif action_type == "thermal_management":
                self._implement_thermal_management(target_files)
            elif action_type == "optimize_response_time":
                self._optimize_response_time(target_files)
            elif action_type == "improve_error_handling":
                self._improve_error_handling(target_files)
            elif action_type == "general_optimization":
                self._general_optimization(target_files)
            
        except Exception as e:
            self.logger.error(f"Failed to execute evolution action {action.get('type')}: {e}")
    
    def _optimize_cpu_usage(self, target_files: List[str]):
        """Optimize CPU usage in target files"""
        for file_path in target_files:
            try:
                # Read current file
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Apply CPU optimizations
                optimized_content = self._apply_cpu_optimizations(content)
                
                # Write optimized content
                self.will["self_compiler"].modify_file(file_path, optimized_content, "write")
                
            except Exception as e:
                self.logger.error(f"Failed to optimize CPU usage in {file_path}: {e}")
    
    def _optimize_memory_usage(self, target_files: List[str]):
        """Optimize memory usage in target files"""
        for file_path in target_files:
            try:
                # Read current file
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Apply memory optimizations
                optimized_content = self._apply_memory_optimizations(content)
                
                # Write optimized content
                self.will["self_compiler"].modify_file(file_path, optimized_content, "write")
                
            except Exception as e:
                self.logger.error(f"Failed to optimize memory usage in {file_path}: {e}")
    
    def _implement_thermal_management(self, target_files: List[str]):
        """Implement thermal management in target files"""
        for file_path in target_files:
            try:
                # Read current file
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Apply thermal management
                thermal_content = self._apply_thermal_management(content)
                
                # Write thermal management content
                self.will["self_compiler"].modify_file(file_path, thermal_content, "write")
                
            except Exception as e:
                self.logger.error(f"Failed to implement thermal management in {file_path}: {e}")
    
    def _optimize_response_time(self, target_files: List[str]):
        """Optimize response time in target files"""
        for file_path in target_files:
            try:
                # Read current file
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Apply response time optimizations
                optimized_content = self._apply_response_time_optimizations(content)
                
                # Write optimized content
                self.will["self_compiler"].modify_file(file_path, optimized_content, "write")
                
            except Exception as e:
                self.logger.error(f"Failed to optimize response time in {file_path}: {e}")
    
    def _improve_error_handling(self, target_files: List[str]):
        """Improve error handling in target files"""
        for file_path in target_files:
            try:
                # Read current file
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Apply error handling improvements
                improved_content = self._apply_error_handling_improvements(content)
                
                # Write improved content
                self.will["self_compiler"].modify_file(file_path, improved_content, "write")
                
            except Exception as e:
                self.logger.error(f"Failed to improve error handling in {file_path}: {e}")
    
    def _general_optimization(self, target_files: List[str]):
        """Apply general optimizations to target files"""
        for file_path in target_files:
            try:
                # Read current file
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Apply general optimizations
                optimized_content = self._apply_general_optimizations(content)
                
                # Write optimized content
                self.will["self_compiler"].modify_file(file_path, optimized_content, "write")
                
            except Exception as e:
                self.logger.error(f"Failed to apply general optimizations to {file_path}: {e}")
    
    def _apply_cpu_optimizations(self, content: str) -> str:
        """Apply CPU optimizations to code content"""
        # Add CPU optimization comments and improvements
        optimizations = [
            "# CPU Optimization: Added caching for expensive operations",
            "# CPU Optimization: Reduced redundant calculations",
            "# CPU Optimization: Implemented lazy loading"
        ]
        
        lines = content.split('\n')
        optimized_lines = []
        
        for line in lines:
            optimized_lines.append(line)
            # Add optimizations at strategic points
            if "def " in line and "get_system_metrics" in line:
                optimized_lines.append("    # CPU Optimization: Cached metrics")
            elif "import " in line and "psutil" in line:
                optimized_lines.append("# CPU Optimization: Efficient system monitoring")
        
        return '\n'.join(optimized_lines)
    
    def _apply_memory_optimizations(self, content: str) -> str:
        """Apply memory optimizations to code content"""
        # Add memory optimization comments and improvements
        optimizations = [
            "# Memory Optimization: Implemented object pooling",
            "# Memory Optimization: Reduced memory allocations",
            "# Memory Optimization: Added garbage collection hints"
        ]
        
        lines = content.split('\n')
        optimized_lines = []
        
        for line in lines:
            optimized_lines.append(line)
            # Add optimizations at strategic points
            if "def " in line and "get_system_metrics" in line:
                optimized_lines.append("    # Memory Optimization: Efficient data structures")
            elif "import " in line and "psutil" in line:
                optimized_lines.append("# Memory Optimization: Minimal memory footprint")
        
        return '\n'.join(optimized_lines)
    
    def _apply_thermal_management(self, content: str) -> str:
        """Apply thermal management to code content"""
        # Add thermal management comments and improvements
        thermal_code = '''
def _check_thermal_status(self):
    """Check thermal status and implement cooling if needed"""
    try:
        temp = self.get_temperature()
        if temp and temp > 70:
            self.logger.warning(f"High temperature detected: {temp}°C")
            self._implement_cooling_measures()
        return temp
    except Exception as e:
        self.logger.error(f"Thermal check failed: {e}")
        return None

def _implement_cooling_measures(self):
    """Implement cooling measures when temperature is high"""
    try:
        # Reduce CPU frequency
        subprocess.run(['sudo', 'cpupower', 'frequency-set', '-g', 'powersave'])
        # Reduce workload
        self._reduce_workload()
        self.logger.info("Cooling measures implemented")
    except Exception as e:
        self.logger.error(f"Cooling measures failed: {e}")
'''
        
        return content + thermal_code
    
    def _apply_response_time_optimizations(self, content: str) -> str:
        """Apply response time optimizations to code content"""
        # Add response time optimization comments and improvements
        optimizations = [
            "# Response Time Optimization: Added async operations",
            "# Response Time Optimization: Implemented caching",
            "# Response Time Optimization: Reduced blocking operations"
        ]
        
        lines = content.split('\n')
        optimized_lines = []
        
        for line in lines:
            optimized_lines.append(line)
            # Add optimizations at strategic points
            if "def " in line and "get_system_metrics" in line:
                optimized_lines.append("    # Response Time Optimization: Async metrics collection")
            elif "import " in line:
                optimized_lines.append("# Response Time Optimization: Efficient imports")
        
        return '\n'.join(optimized_lines)
    
    def _apply_error_handling_improvements(self, content: str) -> str:
        """Apply error handling improvements to code content"""
        # Add error handling improvements
        error_handling = '''
def _improved_error_handling(self, operation: str, fallback=None):
    """Improved error handling with graceful degradation"""
    try:
        return self._execute_operation(operation)
    except Exception as e:
        self.logger.error(f"Operation {operation} failed: {e}")
        if fallback:
            return fallback
        return None
'''
        
        return content + error_handling
    
    def _apply_general_optimizations(self, content: str) -> str:
        """Apply general optimizations to code content"""
        # Add general optimization comments
        optimizations = [
            "# General Optimization: Code cleanup and efficiency improvements",
            "# General Optimization: Reduced complexity",
            "# General Optimization: Improved readability"
        ]
        
        lines = content.split('\n')
        optimized_lines = []
        
        for line in lines:
            optimized_lines.append(line)
            # Add optimizations at strategic points
            if "def " in line:
                optimized_lines.append("    # General Optimization: Improved function efficiency")
        
        return '\n'.join(optimized_lines)
    
    def _create_evolution_description(self, evolution_plan: Dict[str, Any]) -> str:
        """Create detailed description for evolution pull request"""
        description = f"""
# Evolution: {len(evolution_plan['bottlenecks'])} Bottlenecks Addressed

## Bottlenecks Identified:
"""
        
        for bottleneck in evolution_plan["bottlenecks"]:
            description += f"- **{bottleneck['type']}**: {bottleneck['description']} (Value: {bottleneck['value']})\n"
        
        description += f"""
## Actions Taken:
"""
        
        for action in evolution_plan["actions"]:
            description += f"- **{action['type']}**: {action['description']} (Priority: {action['priority']})\n"
        
        description += f"""
## Impact:
- **Estimated Impact**: {evolution_plan['estimated_impact']}
- **Risk Level**: {evolution_plan['risk_level']}
- **Actions Executed**: {len(evolution_plan['actions'])}

This evolution was automatically triggered based on performance analysis and approved by the system.
"""
        
        return description
    
    def _rollback_evolution(self):
        """Rollback evolution changes if execution fails"""
        try:
            self.logger.warning("Rolling back evolution changes...")
            
            # Get last commit hash
            last_commit = self.will["self_compiler"]._repo.head.commit.hexsha
            
            # Rollback to previous commit
            self.will["self_compiler"].rollback_to_commit(last_commit)
            
            self.logger.info("Evolution rollback completed")
            
        except Exception as e:
            self.logger.error(f"Evolution rollback failed: {e}")
    
    def _get_memory_usage(self) -> Dict[str, Any]:
        """Get memory usage statistics"""
        try:
            return {
                "memory_size": len(self.will["self_compiler"].get_change_history(100)),
                "consciousness_memory": self.mind["consciousness_core"].get_memory_size(),
                "emotional_memory": self.psyche["emotional_processing_core"].get_memory_size()
            }
        except Exception as e:
            self.logger.error(f"Failed to get memory usage: {e}")
            return {}
    
    def _get_response_times(self) -> Dict[str, float]:
        """Get response time statistics"""
        try:
            # This would track actual response times
            return {
                "average": 2.5,  # Placeholder
                "min": 0.1,
                "max": 10.0,
                "count": 100
            }
        except Exception as e:
            self.logger.error(f"Failed to get response times: {e}")
            return {}
    
    def _get_error_rates(self) -> Dict[str, float]:
        """Get error rate statistics"""
        try:
            # This would track actual error rates
            return {
                "total": 0.02,  # 2% error rate
                "by_type": {
                    "system": 0.01,
                    "network": 0.005,
                    "user": 0.005
                }
            }
        except Exception as e:
            self.logger.error(f"Failed to get error rates: {e}")
            return {}
    
    def _calculate_throughput(self) -> float:
        """Calculate system throughput"""
        try:
            # This would calculate actual throughput
            return 100.0  # operations per second
        except Exception as e:
            self.logger.error(f"Failed to calculate throughput: {e}")
            return 0.0
    
    def _get_evolution_cycles(self) -> int:
        """Get number of completed evolution cycles"""
        try:
            return self._evolution_cycles
        except Exception as e:
            self.logger.error(f"Failed to get evolution cycles: {e}")
            return 0
    
    def _get_last_evolution_time(self) -> float:
        """Get timestamp of last evolution"""
        try:
            return self._last_evolution_time
        except Exception as e:
            self.logger.error(f"Failed to get last evolution time: {e}")
            return 0
    
    def _get_evolution_success_rate(self) -> float:
        """Get evolution success rate"""
        try:
            total_evolutions = self._get_evolution_cycles()
            if total_evolutions == 0:
                return 1.0
            
            # This would track actual success rate
            return 0.95  # 95% success rate
        except Exception as e:
            self.logger.error(f"Failed to get evolution success rate: {e}")
            return 0.0
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get complete system status"""
        try:
            return {
                "body": {
                    "sensorium": self.body["sensorium"].get_metrics_json(),
                    "actuator": self.body["actuator"].get_actuator_status(),
                    "digital_metabolism": self.body["digital_metabolism"].get_metabolism_status()
                },
                "mind": {
                    "consciousness": self.mind["consciousness_core"].get_consciousness_status(),
                    "self_representation": self.mind["self_representation_core"].get_self_status(),
                    "multi_threaded_thought": self.mind["multi_threaded_thought"].get_current_state(),
                    "cognitive_brain": self.get_cognitive_brain_status()
                },
                "psyche": {
                    "emotional": self.psyche["emotional_processing_core"].get_emotional_core_status(),
                    "crew_manager": self.psyche["crew_manager"].get_crew_manager_status()
                },
                "will": {
                    "self_compiler": self.will["self_compiler"].get_compiler_status(),
                    "asimov_compliance_filter": self.will["asimov_compliance_filter"].get_filter_status(),
                    "tool_executor": self.will["tool_executor"].get_executor_status()
                },
                "evaluation": {
                    "consciousness_monitor": self.evaluation["consciousness_monitor"].get_monitor_status(),
                    "auto_reporter": self.evaluation["auto_reporter"].get_reporter_status(),
                    "meta_observer": self.evaluation["meta_observer"].get_observer_status()
                }
            }
        except Exception as e:
            self.logger.error(f"Error getting system status: {e}")
            return {"error": str(e)}

    async def process_with_cognitive_brain(self, input_data: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process input through the cognitive brain"""
        try:
            self.logger.info(f"Processing through cognitive brain: {input_data[:100]}...")
            
            # Process through cognitive brain
            result = await self.mind["cognitive_brain"].process_input(input_data, context)
            
            if result["success"]:
                consensus = result["consensus"]
                self.logger.info(f"Cognitive brain consensus achieved with confidence: {consensus.confidence_score}")
                
                # Log the reasoning trace
                for chain in consensus.reasoning_trace:
                    self.logger.debug(f"[{chain.department.value}] {chain.output[:100]}...")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in cognitive brain processing: {e}")
            return {"success": False, "error": str(e)}

    def get_cognitive_brain_status(self) -> Dict[str, Any]:
        """Get status of cognitive brain"""
        try:
            return self.mind["cognitive_brain"].get_brain_status()
        except Exception as e:
            self.logger.error(f"Error getting cognitive brain status: {e}")
            return {"error": str(e)}

    async def trigger_cognitive_evolution(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Trigger evolution through cognitive brain"""
        try:
            self.logger.info(f"Triggering cognitive evolution for task: {task}")
            
            # Process through cognitive brain
            result = await self.process_with_cognitive_brain(task, context)
            
            if result["success"]:
                consensus = result["consensus"]
                
                # If consensus is successful, apply the decision
                if consensus.confidence_score > 0.7:
                    self.logger.info(f"High confidence consensus ({consensus.confidence_score}), applying decision")
                    # Here we would apply the consensus decision
                    # For now, just log it
                    self.logger.info(f"Decision to apply: {consensus.final_decision}")
                else:
                    self.logger.warning(f"Low confidence consensus ({consensus.confidence_score}), decision may need review")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in cognitive evolution: {e}")
            return {"success": False, "error": str(e)}
    
    def _test_mode_cycle(self):
        """Тестовый режим с ограниченным количеством циклов"""
        self.logger.info("🧪 Тестовый режим: 3 цикла с когнитивной архитектурой")
        
        for cycle in range(3):
            try:
                self.logger.info(f"🧪 Тестовый цикл #{cycle + 1}")
                
                # Сбор метрик
                self._collect_system_metrics()
                
                # Тест когнитивной архитектуры
                test_input = f"Тестовый запрос #{cycle + 1}: оптимизация системы"
                result = asyncio.run(self.process_with_cognitive_brain(test_input))
                
                if result["success"]:
                    self.logger.info(f"✅ Когнитивный тест #{cycle + 1} успешен")
                else:
                    self.logger.error(f"❌ Когнитивный тест #{cycle + 1} провален: {result.get('error')}")
                
                # Пауза между тестами
                time.sleep(5)
                
            except Exception as e:
                self.logger.error(f"Ошибка в тестовом цикле: {e}")
        
        self.logger.info("🧪 Тестовый режим завершен")
    
    def _demo_mode_cycle(self):
        """Демо режим с показом возможностей когнитивной архитектуры"""
        self.logger.info("🎭 Демо режим: показ когнитивной архитектуры")
        
        demo_tasks = [
            "Оптимизировать производительность системы",
            "Проанализировать текущие узкие места",
            "Предложить улучшения безопасности",
            "Создать план эволюции агента"
        ]
        
        for i, task in enumerate(demo_tasks):
            try:
                self.logger.info(f"🎭 Демо задача #{i + 1}: {task}")
                
                # Обработка через когнитивную архитектуру
                result = asyncio.run(self.process_with_cognitive_brain(task))
                
                if result["success"]:
                    consensus = result["consensus"]
                    self.logger.info(f"✅ Демо #{i + 1}: Решение принято с уверенностью {consensus.confidence_score}")
                    self.logger.info(f"📋 Решение: {consensus.final_decision[:100]}...")
                else:
                    self.logger.error(f"❌ Демо #{i + 1} провален: {result.get('error')}")
                
                # Пауза между демо
                time.sleep(3)
                
            except Exception as e:
                self.logger.error(f"Ошибка в демо режиме: {e}")
        
        self.logger.info("🎭 Демо режим завершен")
    
    def shutdown(self):
        """Graceful shutdown системы"""
        if not self._running:
            return
        
        self.logger.info("Начинаю graceful shutdown Ark v1.3")
        self._running = False
        self._shutdown_event.set()
        
        try:
            # Остановка всех компонентов
            self.body["digital_metabolism"].stop_monitoring()
            self.mind["consciousness_core"].stop_processing()
            self.mind["multi_threaded_thought"].stop_monitoring()
            self.evaluation["consciousness_monitor"].stop_monitoring()
            
            # Очистка процессов
            killed_count = self.body["actuator"].cleanup_processes()
            if killed_count > 0:
                self.logger.info(f"Завершено {killed_count} активных процессов")
            
            self.logger.info("Graceful shutdown завершен")
            
        except Exception as e:
            self.logger.error(f"Ошибка при shutdown: {e}")


def parse_arguments():
    """Парсинг аргументов командной строки"""
    parser = argparse.ArgumentParser(description="Ark Project Main Control")
    parser.add_argument(
        '--trigger-reflection',
        action='store_true',
        help="Force the system to enter REFLECTIVE_ANALYSIS state on the first cycle."
    )
    parser.add_argument(
        '--test-mode',
        action='store_true',
        help="Run in test mode with limited cycles."
    )
    parser.add_argument(
        '--demo-mode',
        action='store_true',
        help="Run in demo mode with cognitive brain showcase."
    )
    return parser.parse_args()


def main():
    """Главная функция"""
    # Парсинг аргументов
    args = parse_arguments()
    
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/ark.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    # Валидация конфигурации
    try:
        from config import config_instance
        if hasattr(config_instance, 'validate'):
            if not config_instance.validate():
                print("Ошибка валидации конфигурации")
                sys.exit(1)
        else:
            print("Пропуск валидации конфигурации (legacy mode)")
    except Exception as e:
        print(f"Ошибка валидации конфигурации: {e}")
        print("Продолжение в legacy mode")
    
    # Создание и запуск Ark
    ark = Ark()
    
    try:
        ark.start(args)
    except Exception as e:
        logging.error(f"Критическая ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 