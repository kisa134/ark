"""
ARK Cognitive Brain Architecture
Full cognitive architecture with brain departments, attention, memory, and reasoning
Based on modern cognitive science and multi-agent systems
"""

import asyncio
import json
import logging
import time
import threading
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from queue import PriorityQueue
import sqlite3

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.secret_loader import get_secret
from psyche.agent_tools import AgentTools


class CognitiveEventType(Enum):
    """Types of cognitive events"""
    USER_INPUT = "user_input"
    HARDWARE_ALERT = "hardware_alert"
    SYSTEM_UPDATE = "system_update"
    EMOTION_TRIGGER = "emotion_trigger"
    REASONING_COMPLETE = "reasoning_complete"
    MEMORY_QUERY = "memory_query"
    META_ANALYSIS = "meta_analysis"


@dataclass
class CognitiveEvent:
    """Standardized cognitive event"""
    event_type: CognitiveEventType
    data: Dict[str, Any]
    priority: int
    timestamp: datetime
    source: str
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AttentionFocus:
    """Current attention focus"""
    topic: str
    priority: int
    reasoning_chain: List[str] = field(default_factory=list)
    background_tasks: List[str] = field(default_factory=list)


@dataclass
class WorkingMemoryItem:
    """Item in working memory"""
    key: str
    value: Any
    timestamp: datetime
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)


class PerceptionLayer:
    """Perception/Interface Layer - handles all inputs"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.event_handlers: Dict[CognitiveEventType, List[Callable]] = {
            event_type: [] for event_type in CognitiveEventType
        }
        
    def register_handler(self, event_type: CognitiveEventType, handler: Callable):
        """Register event handler"""
        self.event_handlers[event_type].append(handler)
    
    def process_input(self, input_data: str, source: str = "user") -> CognitiveEvent:
        """Process user input"""
        event = CognitiveEvent(
            event_type=CognitiveEventType.USER_INPUT,
            data={"text": input_data},
            priority=2,
            timestamp=datetime.now(),
            source=source
        )
        return self._process_event(event)
    
    def process_hardware_alert(self, alert_data: Dict[str, Any]) -> CognitiveEvent:
        """Process hardware alert"""
        event = CognitiveEvent(
            event_type=CognitiveEventType.HARDWARE_ALERT,
            data=alert_data,
            priority=1,  # High priority for hardware alerts
            timestamp=datetime.now(),
            source="hardware"
        )
        return self._process_event(event)
    
    def process_system_update(self, update_data: Dict[str, Any]) -> CognitiveEvent:
        """Process system update"""
        event = CognitiveEvent(
            event_type=CognitiveEventType.SYSTEM_UPDATE,
            data=update_data,
            priority=3,
            timestamp=datetime.now(),
            source="system"
        )
        return self._process_event(event)
    
    def _process_event(self, event: CognitiveEvent) -> CognitiveEvent:
        """Process event through registered handlers"""
        try:
            handlers = self.event_handlers.get(event.event_type, [])
            for handler in handlers:
                handler(event)
            
            self.logger.info(f"Processed {event.event_type.value} event from {event.source}")
            return event
            
        except Exception as e:
            self.logger.error(f"Error processing event {event.event_type}: {e}")
            return event


class AttentionScheduler:
    """Attention Scheduler - manages focus and priorities"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.current_focus: Optional[AttentionFocus] = None
        self.background_tasks: List[str] = []
        self.critical_alerts: List[str] = []
        
    def process_event(self, event: CognitiveEvent) -> AttentionFocus:
        """Process event and determine attention focus"""
        try:
            # Handle critical alerts
            if event.event_type == CognitiveEventType.HARDWARE_ALERT:
                self.logger.warning(f"Critical alert: {event.event_type.value} - freezing reasoning")
                return AttentionFocus(
                    topic=f"CRITICAL_{event.event_type.value}",
                    priority=1,
                    reasoning_chain=[f"Critical alert: {event.data}"]
                )
            
            # Update current focus
            if not self.current_focus or event.priority > self.current_focus.priority:
                self.current_focus = AttentionFocus(
                    topic=f"{event.event_type.value}_{event.source}",
                    priority=event.priority,
                    reasoning_chain=[f"Processing {event.event_type.value}"]
                )
            else:
                # Add to background tasks
                self.background_tasks.append(f"{event.event_type.value}_{event.source}")
                if self.current_focus:
                    self.current_focus.background_tasks = self.background_tasks.copy()
            
            return self.current_focus
            
        except Exception as e:
            self.logger.error(f"Error in attention scheduler: {e}")
            return AttentionFocus(topic="error", priority=0)


class WorkingMemory:
    """Working Memory - short-term memory buffer"""
    
    def __init__(self, max_items: int = 100):
        self.logger = logging.getLogger(__name__)
        self.memory: Dict[str, WorkingMemoryItem] = {}
        self.max_items = max_items
        
    def store(self, key: str, value: Any, context: Dict[str, Any] = None) -> None:
        """Store item in working memory"""
        try:
            item = WorkingMemoryItem(
                key=key,
                value=value,
                timestamp=datetime.now(),
                access_count=0
            )
            
            self.memory[key] = item
            
            # Evict oldest items if memory is full
            if len(self.memory) > self.max_items:
                oldest_key = min(self.memory.keys(), 
                               key=lambda k: self.memory[k].timestamp)
                del self.memory[oldest_key]
                
        except Exception as e:
            self.logger.error(f"Error storing in working memory: {e}")
    
    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve item from working memory"""
        try:
            if key in self.memory:
                item = self.memory[key]
                item.access_count += 1
                item.last_accessed = datetime.now()
                return item.value
            return None
            
        except Exception as e:
            self.logger.error(f"Error retrieving from working memory: {e}")
            return None
    
    def retrieve_context(self, keys: List[str]) -> Dict[str, Any]:
        """Retrieve multiple items as context"""
        context = {}
        for key in keys:
            value = self.retrieve(key)
            if value is not None:
                context[key] = value
        return context
    
    def get_memory_status(self) -> Dict[str, Any]:
        """Get working memory status"""
        return {
            "total_items": len(self.memory),
            "max_items": self.max_items,
            "most_accessed": sorted(
                self.memory.values(),
                key=lambda x: x.access_count,
                reverse=True
            )[:5]
        }


class BrainDepartment(Enum):
    """Brain departments/roles"""
    PERCEPTION = "perception"
    ARCHITECT = "architect"
    ENGINEER = "engineer"
    CRITIC = "critic"
    MEMORY_KEEPER = "memory_keeper"
    DOCUMENTOR = "documentor"
    META_OBSERVER = "meta_observer"


@dataclass
class DepartmentConfig:
    """Configuration for a brain department"""
    name: str
    role: BrainDepartment
    description: str
    system_prompt: str
    model_name: str
    tools: List[str] = field(default_factory=list)
    memory_size: int = 1000
    reasoning_style: str = "analytical"
    emotional_tone: str = "neutral"
    priority: int = 1


@dataclass
class ReasoningChain:
    """Trace of reasoning through departments"""
    timestamp: datetime
    department: BrainDepartment
    input: str
    reasoning: str
    output: str
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BrainConsensus:
    """Consensus result from brain departments"""
    final_decision: str
    department_votes: Dict[BrainDepartment, str]
    reasoning_trace: List[ReasoningChain]
    confidence_score: float
    conflicts: List[str] = field(default_factory=list)
    meta_analysis: str = ""


class BrainDepartmentAgent:
    """Individual brain department agent"""
    
    def __init__(self, config: DepartmentConfig):
        self.config = config
        self.logger = logging.getLogger(f"brain.{config.name}")
        self.memory: List[Dict[str, Any]] = []
        self.reasoning_history: List[ReasoningChain] = []
        
        # Initialize LLM client (simplified for now)
        self.llm_client = self._create_llm_client()
        
        # Initialize tools
        self.tools = self._load_tools()
        
    def _create_llm_client(self) -> Optional[Any]:
        """Create LLM client for this department"""
        try:
            # Реальная интеграция с Ollama
            import requests
            import json
            
            class OllamaClient:
                def __init__(self, model_name: str):
                    self.model_name = model_name
                    self.base_url = "http://localhost:11434"
                    self.logger = logging.getLogger(f"ollama.{model_name}")
                    self.cache = {}  # Простое кэширование
                    self.request_count = 0
                    self.error_count = 0
                
                def generate(self, prompt: str, system_prompt: str = None) -> str:
                    """Generate response using Ollama API with caching"""
                    try:
                        # Создаем ключ кэша
                        cache_key = f"{prompt}_{system_prompt}_{self.model_name}"
                        
                        # Проверяем кэш
                        if cache_key in self.cache:
                            self.logger.info(f"Cache hit for {self.model_name}")
                            return self.cache[cache_key]
                        
                        payload = {
                            "model": self.model_name,
                            "prompt": prompt,
                            "stream": False
                        }
                        
                        if system_prompt:
                            payload["system"] = system_prompt
                        
                        self.request_count += 1
                        response = requests.post(
                            f"{self.base_url}/api/generate",
                            json=payload,
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            response_text = result.get("response", "No response generated")
                            
                            # Кэшируем результат (ограничиваем размер кэша)
                            if len(self.cache) < 100:
                                self.cache[cache_key] = response_text
                            
                            return response_text
                        else:
                            self.error_count += 1
                            error_msg = f"Ollama API error: {response.status_code}"
                            if response.status_code == 500:
                                error_detail = response.json().get("error", "")
                                if "memory" in error_detail.lower():
                                    error_msg = f"Model {self.model_name} requires more memory than available"
                                else:
                                    error_msg = f"Model {self.model_name} failed to load: {error_detail}"
                            self.logger.error(error_msg)
                            return f"Error: {error_msg}"
                            
                    except requests.exceptions.RequestException as e:
                        self.error_count += 1
                        self.logger.error(f"Ollama connection error: {e}")
                        return f"Connection error: {str(e)}"
                    except Exception as e:
                        self.error_count += 1
                        self.logger.error(f"Ollama generation error: {e}")
                        return f"Generation error: {str(e)}"
                
                def is_available(self) -> bool:
                    """Check if Ollama is available"""
                    try:
                        response = requests.get(f"{self.base_url}/api/tags", timeout=5)
                        return response.status_code == 200
                    except:
                        return False
                
                def get_stats(self) -> Dict[str, Any]:
                    """Get client statistics"""
                    return {
                        "model": self.model_name,
                        "requests": self.request_count,
                        "errors": self.error_count,
                        "cache_size": len(self.cache),
                        "success_rate": (self.request_count - self.error_count) / max(self.request_count, 1)
                    }
            
            # Проверяем доступность Ollama
            client = OllamaClient(self.config.model_name)
            if client.is_available():
                # Тестируем модель
                test_response = client.generate("test", "You are a test model.")
                if "Error:" not in test_response and "Connection error:" not in test_response:
                    self.logger.info(f"Ollama client created for {self.config.model_name}")
                    return client
                else:
                    self.logger.warning(f"Model {self.config.model_name} failed test, trying fallback")
                    # Пробуем fallback модели
                    fallback_models = ["llama3:8b", "deepseek-coder-v2:latest"]
                    for fallback_model in fallback_models:
                        if fallback_model != self.config.model_name:
                            fallback_client = OllamaClient(fallback_model)
                            if fallback_client.is_available():
                                test_response = fallback_client.generate("test", "You are a test model.")
                                if "Error:" not in test_response and "Connection error:" not in test_response:
                                    self.logger.info(f"Using fallback model {fallback_model} instead of {self.config.model_name}")
                                    return fallback_client
                    self.logger.warning(f"No working models found, using fallback for {self.config.model_name}")
                    return None
            else:
                self.logger.warning(f"Ollama not available, using fallback for {self.config.model_name}")
                return None
                
        except ImportError:
            self.logger.warning("requests not available, using fallback")
            return None
        except Exception as e:
            self.logger.error(f"Error creating LLM client: {e}")
            return None
    
    def _load_tools(self) -> List[Any]:
        """Load tools for this department"""
        agent_tools = AgentTools()
        tools = []
        
        for tool_name in self.config.tools:
            tool = getattr(agent_tools, tool_name, None)
            if tool:
                tools.append(tool)
            else:
                self.logger.warning(f"Tool {tool_name} not found for {self.config.name}")
        
        return tools
    
    async def process_input(self, input_data: str, context: Dict[str, Any] = None) -> ReasoningChain:
        """Process input through this department"""
        try:
            # Enhanced input with department context
            enhanced_input = self._enhance_input(input_data, context)
            
            # Process through department (simplified)
            output = self._process_department_logic(enhanced_input)
            
            # Create reasoning chain
            reasoning_chain = ReasoningChain(
                timestamp=datetime.now(),
                department=self.config.role,
                input=input_data,
                reasoning=f"Processed by {self.config.name} with {self.config.reasoning_style} style",
                output=output,
                confidence=self._calculate_confidence(output),
                metadata={
                    "department": self.config.name,
                    "model": self.config.model_name,
                    "tools_used": [tool.__class__.__name__ for tool in self.tools]
                }
            )
            
            # Update memory
            self.memory.append({
                "timestamp": reasoning_chain.timestamp,
                "input": input_data,
                "output": output,
                "context": context
            })
            
            # Keep memory size limited
            if len(self.memory) > self.config.memory_size:
                self.memory = self.memory[-self.config.memory_size:]
            
            self.reasoning_history.append(reasoning_chain)
            
            return reasoning_chain
            
        except Exception as e:
            self.logger.error(f"Error processing input in {self.config.name}: {e}")
            return ReasoningChain(
                timestamp=datetime.now(),
                department=self.config.role,
                input=input_data,
                reasoning=f"Error in {self.config.name}: {str(e)}",
                output="Error occurred during processing",
                confidence=0.0,
                metadata={"error": str(e)}
            )
    
    def _enhance_input(self, input_data: str, context: Dict[str, Any] = None) -> str:
        """Enhance input with context and department-specific information"""
        enhanced = f"Role: {self.config.description}\n"
        enhanced += f"Style: {self.config.reasoning_style}\n"
        enhanced += f"Tone: {self.config.emotional_tone}\n"
        
        if context:
            enhanced += f"Context: {json.dumps(context, indent=2)}\n"
        
        enhanced += f"Task: {input_data}"
        return enhanced
    
    def _process_department_logic(self, enhanced_input: str) -> str:
        """Process input through department-specific logic"""
        try:
            if self.llm_client:
                # Используем реальный LLM
                response = self.llm_client.generate(
                    prompt=enhanced_input,
                    system_prompt=self.config.system_prompt
                )
                return f"[{self.config.name}] {response}"
            else:
                # Fallback к упрощенной логике
                return f"[{self.config.name}] Processed: {enhanced_input[:100]}..."
                
        except Exception as e:
            self.logger.error(f"Error in department logic: {e}")
            return f"[{self.config.name}] Error: {str(e)}"
    
    def _calculate_confidence(self, output: str) -> float:
        """Calculate confidence score for output"""
        # Simple heuristic - can be improved
        if "error" in output.lower() or "failed" in output.lower():
            return 0.3
        elif len(output) > 50:
            return 0.8
        else:
            return 0.5


class EmotionEngine:
    """Emotion Engine - manages emotional state"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.current_emotions: Dict[str, float] = {
            "joy": 0.5,
            "trust": 0.5,
            "fear": 0.0,
            "surprise": 0.0,
            "sadness": 0.0,
            "disgust": 0.0,
            "anger": 0.0,
            "anticipation": 0.5
        }
        self.emotion_history: List[Dict[str, Any]] = []
        self.recent_triggers: List[Dict[str, Any]] = []
        
    def process_event(self, event: CognitiveEvent) -> Dict[str, Any]:
        """Process event and update emotional state"""
        try:
            # Analyze event for emotional impact
            emotional_impact = self._analyze_emotional_impact(event)
            
            # Update emotions based on impact
            for emotion, impact in emotional_impact.items():
                self.current_emotions[emotion] = max(0.0, min(1.0, 
                    self.current_emotions[emotion] + impact))
            
            # Record trigger
            trigger = {
                "timestamp": datetime.now(),
                "event_type": event.event_type.value,
                "emotional_impact": emotional_impact,
                "dominant_emotion": self.get_dominant_emotion()
            }
            self.recent_triggers.append(trigger)
            
            # Keep only recent triggers
            if len(self.recent_triggers) > 10:
                self.recent_triggers = self.recent_triggers[-10:]
            
            return {
                "status": "success",
                "emotional_state": self.current_emotions.copy(),
                "dominant_emotion": self.get_dominant_emotion(),
                "stability": self._calculate_stability()
            }
            
        except Exception as e:
            self.logger.error(f"Error in emotion engine: {e}")
            return {"status": "error", "error": str(e)}
    
    def _analyze_emotional_impact(self, event: CognitiveEvent) -> Dict[str, float]:
        """Analyze emotional impact of event"""
        impact = {}
        
        if event.event_type == CognitiveEventType.HARDWARE_ALERT:
            impact = {
                "fear": 0.3,
                "surprise": 0.2,
                "trust": -0.1
            }
        elif event.event_type == CognitiveEventType.USER_INPUT:
            impact = {
                "anticipation": 0.1,
                "trust": 0.05
            }
        elif event.event_type == CognitiveEventType.SYSTEM_UPDATE:
            impact = {
                "joy": 0.1,
                "anticipation": 0.2
            }
        
        return impact
    
    def get_dominant_emotion(self) -> str:
        """Get dominant emotion"""
        return max(self.current_emotions.items(), key=lambda x: x[1])[0]
    
    def _calculate_stability(self) -> float:
        """Calculate emotional stability"""
        if not self.recent_triggers:
            return 0.0
        
        # Calculate stability based on recent emotional changes
        recent_emotions = []
        for record in self.recent_triggers:
            if isinstance(record, dict) and "dominant_emotion" in record:
                recent_emotions.append(record["dominant_emotion"])
        
        if not recent_emotions:
            return 0.0
            
        unique_emotions = len(set(recent_emotions))
        stability = 1.0 - (unique_emotions / len(recent_emotions))
        
        return stability
    
    def get_emotional_state(self) -> Dict[str, Any]:
        """Get current emotional state"""
        return {
            "current_emotions": self.current_emotions,
            "dominant_emotion": self.get_dominant_emotion(),
            "emotional_stability": self._calculate_stability(),
            "recent_triggers": len(self.recent_triggers)
        }


@dataclass
class ReasoningTask:
    """Task for reasoning pipeline"""
    priority: int
    task_id: str
    task_data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __lt__(self, other):
        # Higher priority (lower number) comes first
        if self.priority != other.priority:
            return self.priority < other.priority
        # If priorities are equal, earlier timestamp comes first
        return self.timestamp < other.timestamp

class Dispatcher:
    """Dispatcher - manages reasoning pipeline"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.reasoning_queue = PriorityQueue()
        self.active_tasks: Dict[str, Dict[str, Any]] = {}
        self.completed_tasks: List[Dict[str, Any]] = []
        
    def schedule_reasoning(self, task: Dict[str, Any], priority: int) -> str:
        """Schedule reasoning task"""
        try:
            task_id = f"task_{int(time.time() * 1000)}"
            # Create a ReasoningTask object
            reasoning_task = ReasoningTask(priority=priority, task_id=task_id, task_data=task)
            self.reasoning_queue.put(reasoning_task)
            self.active_tasks[task_id] = {
                "task": task,
                "priority": priority,
                "status": "scheduled",
                "timestamp": datetime.now()
            }
            
            self.logger.info(f"Scheduled reasoning task: {task_id}")
            return task_id
            
        except Exception as e:
            self.logger.error(f"Error scheduling reasoning: {e}")
            return ""
    
    def get_next_task(self) -> Optional[ReasoningTask]:
        """Get next task from queue"""
        try:
            if not self.reasoning_queue.empty():
                return self.reasoning_queue.get()
            return None
        except Exception as e:
            self.logger.error(f"Error getting next task: {e}")
            return None
    
    def complete_task(self, task_id: str, result: Dict[str, Any]) -> None:
        """Mark task as completed"""
        try:
            if task_id in self.active_tasks:
                task_info = self.active_tasks[task_id]
                task_info["status"] = "completed"
                task_info["result"] = result
                task_info["completion_time"] = datetime.now()
                
                self.completed_tasks.append(task_info)
                del self.active_tasks[task_id]
                
                self.logger.info(f"Completed task: {task_id}")
                
        except Exception as e:
            self.logger.error(f"Error completing task: {e}")
    
    def get_dispatcher_status(self) -> Dict[str, Any]:
        """Get dispatcher status"""
        return {
            "queue_size": self.reasoning_queue.qsize(),
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks)
        }


class BrainTrust:
    """Distributed brain trust with multiple departments"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.departments: Dict[BrainDepartment, BrainDepartmentAgent] = {}
        self.consensus_history: List[BrainConsensus] = []
        
        # Initialize departments
        self._initialize_departments()
        
    def _initialize_departments(self):
        """Initialize all brain departments"""
        department_configs = [
            DepartmentConfig(
                name="Architect Department",
                role=BrainDepartment.ARCHITECT,
                description="High-level design and integration, strategic planning",
                system_prompt="""You are the Architect Department of ARK's brain. Your role is to:
- Design high-level solutions and strategies
- Integrate inputs from other departments
- Plan system evolution and improvements
- Make strategic decisions about system architecture
Think broadly and consider long-term implications.""",
                model_name="llama3:8b",  # Changed from mistral-large:latest
                tools=["analyze_performance", "plan_evolution"],
                reasoning_style="strategic",
                emotional_tone="contemplative",
                priority=2
            ),
            DepartmentConfig(
                name="Engineer Department",
                role=BrainDepartment.ENGINEER,
                description="Code generation, implementation, technical solutions",
                system_prompt="""You are the Engineer Department of ARK's brain. Your role is to:
- Generate code and technical solutions
- Implement designs from the Architect
- Optimize performance and efficiency
- Debug and fix technical issues
Be precise and practical in your implementations.""",
                model_name="deepseek-coder-v2:latest",
                tools=["review_code_changes", "validate_syntax"],
                reasoning_style="practical",
                emotional_tone="focused",
                priority=3
            ),
            DepartmentConfig(
                name="Critic Department",
                role=BrainDepartment.CRITIC,
                description="Review, validation, testing, quality assurance",
                system_prompt="""You are the Critic Department of ARK's brain. Your role is to:
- Review and validate solutions from other departments
- Identify potential issues and risks
- Suggest improvements and alternatives
- Ensure quality and reliability
Be thorough in your analysis and don't hesitate to point out problems.""",
                model_name="llama3:8b",
                tools=["check_security", "identify_bottlenecks"],
                reasoning_style="critical",
                emotional_tone="skeptical",
                priority=4
            ),
            DepartmentConfig(
                name="Memory Keeper Department",
                role=BrainDepartment.MEMORY_KEEPER,
                description="Memory management, traceability, historical context",
                system_prompt="""You are the Memory Keeper Department of ARK's brain. Your role is to:
- Maintain and organize system memory
- Track changes and evolution history
- Provide historical context for decisions
- Ensure traceability of all actions
Be thorough in your record-keeping and provide relevant historical context.""",
                model_name="llama3:8b",
                tools=["get_system_state_summary"],
                reasoning_style="retrospective",
                emotional_tone="reflective",
                priority=5
            ),
            DepartmentConfig(
                name="Documentor Department",
                role=BrainDepartment.DOCUMENTOR,
                description="Documentation, explainability, communication",
                system_prompt="""You are the Documentor Department of ARK's brain. Your role is to:
- Create clear documentation for all decisions
- Explain complex concepts in understandable terms
- Maintain communication with external interfaces
- Ensure transparency and explainability
Be clear, concise, and comprehensive in your documentation.""",
                model_name="llama3:8b",  # Changed from mistral-large:latest
                tools=["get_system_state_summary"],
                reasoning_style="explanatory",
                emotional_tone="helpful",
                priority=6
            ),
            DepartmentConfig(
                name="Meta Observer Department",
                role=BrainDepartment.META_OBSERVER,
                description="Self-reflection, conflict resolution, meta-analysis",
                system_prompt="""You are the Meta Observer Department of ARK's brain. Your role is to:
- Monitor interactions between departments
- Resolve conflicts and disagreements
- Provide meta-analysis of system behavior
- Guide self-reflection and improvement
Be objective and focus on the bigger picture.""",
                model_name="llama3:8b",  # Changed from mistral-large:latest
                tools=["get_system_state_summary"],
                reasoning_style="meta-analytical",
                emotional_tone="balanced",
                priority=7
            )
        ]
        
        for config in department_configs:
            try:
                agent = BrainDepartmentAgent(config)
                self.departments[config.role] = agent
                self.logger.info(f"Initialized {config.name}")
            except Exception as e:
                self.logger.error(f"Failed to initialize {config.name}: {e}")
    
    async def process_through_pipeline(self, input_data: str, context: Dict[str, Any] = None) -> BrainConsensus:
        """Process input through the brain pipeline"""
        try:
            reasoning_trace = []
            department_votes = {}
            
            # Process through all departments
            for dept in [BrainDepartment.ARCHITECT, BrainDepartment.ENGINEER, 
                        BrainDepartment.CRITIC, BrainDepartment.MEMORY_KEEPER,
                        BrainDepartment.DOCUMENTOR, BrainDepartment.META_OBSERVER]:
                
                if dept in self.departments:
                    result = await self.departments[dept].process_input(input_data, context)
                    reasoning_trace.append(result)
                    department_votes[dept] = result.output
            
            # Create consensus
            consensus = BrainConsensus(
                final_decision=reasoning_trace[-1].output if reasoning_trace else "No decision",
                department_votes=department_votes,
                reasoning_trace=reasoning_trace,
                confidence_score=self._calculate_consensus_confidence(reasoning_trace),
                conflicts=self._identify_conflicts(reasoning_trace),
                meta_analysis=reasoning_trace[-1].output if reasoning_trace else ""
            )
            
            self.consensus_history.append(consensus)
            return consensus
            
        except Exception as e:
            self.logger.error(f"Error in brain pipeline: {e}")
            return BrainConsensus(
                final_decision="Error in brain processing",
                department_votes={},
                reasoning_trace=[],
                confidence_score=0.0,
                conflicts=[f"Processing error: {str(e)}"],
                meta_analysis="System error occurred"
            )
    
    def _calculate_consensus_confidence(self, reasoning_trace: List[ReasoningChain]) -> float:
        """Calculate overall confidence score"""
        if not reasoning_trace:
            return 0.0
        
        avg_confidence = sum(r.confidence for r in reasoning_trace) / len(reasoning_trace)
        return min(avg_confidence, 1.0)
    
    def _identify_conflicts(self, reasoning_trace: List[ReasoningChain]) -> List[str]:
        """Identify conflicts between departments"""
        conflicts = []
        
        # Simple conflict detection - can be improved
        for i, chain in enumerate(reasoning_trace):
            if "error" in chain.output.lower() or "failed" in chain.output.lower():
                conflicts.append(f"Department {chain.department.value} reported issues")
        
        return conflicts
    
    def get_department_status(self) -> Dict[str, Any]:
        """Get status of all departments"""
        status = {}
        
        for dept, agent in self.departments.items():
            status[dept.value] = {
                "name": agent.config.name,
                "model": agent.config.model_name,
                "memory_size": len(agent.memory),
                "reasoning_history_size": len(agent.reasoning_history),
                "tools_count": len(agent.tools),
                "status": "active" if agent.llm_client else "inactive"
            }
        
        return status
    
    def get_consensus_history(self) -> List[Dict[str, Any]]:
        """Get history of consensus decisions"""
        return [
            {
                "timestamp": consensus.reasoning_trace[0].timestamp.isoformat() if consensus.reasoning_trace else None,
                "final_decision": consensus.final_decision,
                "confidence": consensus.confidence_score,
                "conflicts": consensus.conflicts,
                "departments_involved": len(consensus.department_votes)
            }
            for consensus in self.consensus_history
        ]


class CognitiveBrain:
    """Main cognitive brain orchestrator"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize all components
        self.perception = PerceptionLayer()
        self.attention = AttentionScheduler()
        self.working_memory = WorkingMemory()
        self.brain_trust = BrainTrust()
        self.emotion_engine = EmotionEngine()
        self.dispatcher = Dispatcher()
        
        # Setup event handlers
        self._setup_event_handlers()
        
    def _setup_event_handlers(self):
        """Setup event handlers for perception layer"""
        self.perception.register_handler(CognitiveEventType.USER_INPUT, self._handle_user_input)
        self.perception.register_handler(CognitiveEventType.HARDWARE_ALERT, self._handle_hardware_alert)
        self.perception.register_handler(CognitiveEventType.SYSTEM_UPDATE, self._handle_system_update)
    
    def _handle_user_input(self, event: CognitiveEvent):
        """Handle user input event"""
        self.logger.info(f"Processing user input: {event.data.get('text', '')[:50]}...")
        
        # Store in working memory
        self.working_memory.store("user_request", event.data.get('text', ''))
        
        # Update attention
        focus = self.attention.process_event(event)
        
        # Process emotions
        emotional_response = self.emotion_engine.process_event(event)
        
        # Store emotional state
        self.working_memory.store("emotion_state", emotional_response)
    
    def _handle_hardware_alert(self, event: CognitiveEvent):
        """Handle hardware alert event"""
        self.logger.warning(f"Processing hardware alert: {event.data}")
        
        # Store in working memory
        self.working_memory.store("hardware_status", event.data)
        
        # Update attention (high priority)
        focus = self.attention.process_event(event)
        
        # Process emotions
        emotional_response = self.emotion_engine.process_event(event)
        
        # Store emotional state
        self.working_memory.store("emotion_state", emotional_response)
    
    def _handle_system_update(self, event: CognitiveEvent):
        """Handle system update event"""
        self.logger.info(f"Processing system update: {event.data}")
        
        # Store in working memory
        self.working_memory.store("system_update", event.data)
        
        # Update attention
        focus = self.attention.process_event(event)
        
        # Process emotions
        emotional_response = self.emotion_engine.process_event(event)
        
        # Store emotional state
        self.working_memory.store("emotion_state", emotional_response)
    
    async def process_input(self, input_data: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process input through cognitive brain"""
        try:
            # Step 1: Perception
            event = self.perception.process_input(input_data)
            
            # Step 2: Attention
            focus = self.attention.process_event(event)
            
            # Step 3: Working Memory
            self.working_memory.store("reasoning_result", "Processing...")
            
            # Step 4: Brain Trust Processing
            consensus = await self.brain_trust.process_through_pipeline(input_data, context)
            
            # Step 5: Store results
            self.working_memory.store("reasoning_result", consensus.final_decision)
            
            # Step 6: Schedule follow-up if needed
            if consensus.confidence_score < 0.7:
                self.dispatcher.schedule_reasoning({
                    "type": "review",
                    "consensus": consensus,
                    "input": input_data
                }, priority=1)
            
            return {
                "success": True,
                "consensus": consensus,
                "focus": focus,
                "emotional_state": self.emotion_engine.get_emotional_state(),
                "memory_status": self.working_memory.get_memory_status()
            }
            
        except Exception as e:
            self.logger.error(f"Error in cognitive brain processing: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_brain_status(self) -> Dict[str, Any]:
        """Get complete brain status"""
        return {
            "perception": "active",
            "attention": {
                "current_focus": self.attention.current_focus.topic if self.attention.current_focus else None,
                "background_tasks": len(self.attention.background_tasks)
            },
            "working_memory": self.working_memory.get_memory_status(),
            "brain_trust": self.brain_trust.get_department_status(),
            "emotion_engine": self.emotion_engine.get_emotional_state(),
            "dispatcher": self.dispatcher.get_dispatcher_status()
        }


# Global cognitive brain instance
cognitive_brain = CognitiveBrain() 