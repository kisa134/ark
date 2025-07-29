"""
CrewManager - Multi-Agent System with Ollama Integration
Implements CrewAI with local Ollama LLM and resource monitoring
"""

import time
import logging
import requests
import subprocess
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# CrewAI imports
try:
    from crewai import Crew, Agent, Task
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False
    print("Warning: CrewAI not available, using fallback mode")

from config import config
from config import get_secret


@dataclass
class OllamaModel:
    """Ollama model information"""
    name: str
    size: int
    modified_at: str
    digest: str


class OllamaManager:
    """Manages Ollama local LLM integration"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.base_url = get_secret("OLLAMA_BASE_URL", "http://localhost:11434")
        self.api_key = get_secret("OLLAMA_API_KEY", "ollama")
        self._available_models: List[OllamaModel] = []
        self._last_check = 0
        self._check_interval = 300  # 5 minutes
        
    def check_ollama_server(self) -> bool:
        """Check if Ollama server is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            self.logger.warning(f"Ollama server not available: {e}")
            return False
    
    def get_available_models(self) -> List[OllamaModel]:
        """Get list of available Ollama models"""
        current_time = time.time()
        
        # Cache models for 5 minutes
        if current_time - self._last_check < self._check_interval:
            return self._available_models
        
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                models = []
                
                for model in data.get("models", []):
                    models.append(OllamaModel(
                        name=model["name"],
                        size=model.get("size", 0),
                        modified_at=model.get("modified_at", ""),
                        digest=model.get("digest", "")
                    ))
                
                self._available_models = models
                self._last_check = current_time
                
                self.logger.info(f"Found {len(models)} Ollama models")
                return models
            else:
                self.logger.error(f"Failed to get models: {response.status_code}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error getting Ollama models: {e}")
            return []
    
    def check_model_available(self, model_name: str) -> bool:
        """Check if specific model is available"""
        models = self.get_available_models()
        return any(model.name == model_name for model in models)
    
    def get_system_resources(self) -> Dict[str, Any]:
        """Get system resources for LLM inference"""
        try:
            import psutil
            
            # GPU monitoring (if available)
            gpu_info = {}
            try:
                import subprocess
                result = subprocess.run(['nvidia-smi', '--query-gpu=memory.used,memory.total,utilization.gpu', '--format=csv,noheader,nounits'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    if lines:
                        parts = lines[0].split(', ')
                        gpu_info = {
                            "memory_used_mb": int(parts[0]),
                            "memory_total_mb": int(parts[1]),
                            "utilization_percent": int(parts[2])
                        }
            except Exception:
                pass
            
            return {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "memory_available_gb": psutil.virtual_memory().available / (1024**3),
                "gpu": gpu_info
            }
            
        except Exception as e:
            self.logger.error(f"Error getting system resources: {e}")
            return {}
    
    def create_llm_client(self, model_name: str = None) -> Optional[ChatOpenAI]:
        """Create LLM client for Ollama"""
        try:
            if not self.check_ollama_server():
                self.logger.error("Ollama server not available")
                return None
            
            # Get available models
            available_models = self.get_available_models()
            if not available_models:
                self.logger.error("No models available")
                return None
            
            # Use configured model or find first available
            target_model = model_name or get_secret("ARK_MAIN_MIND_MODEL", "llama3:8b")
            
            # Check if target model is available
            if not self.check_model_available(target_model):
                # Try to find alternative model
                alternative_models = ["llama3:8b", "deepseek-coder-v2:latest", "mistral-large:latest"]
                for alt_model in alternative_models:
                    if self.check_model_available(alt_model):
                        target_model = alt_model
                        self.logger.info(f"Using alternative model: {target_model}")
                        break
                else:
                    # Use first available model
                    target_model = available_models[0].name
                    self.logger.info(f"Using first available model: {target_model}")
            
            # Create LLM client
            llm = ChatOpenAI(
                base_url=f"{self.base_url}/v1",
                api_key=self.api_key,
                model_name=target_model,
                temperature=0.1,
                max_tokens=4096,
                timeout=30
            )
            
            self.logger.info(f"LLM client created for model: {target_model}")
            return llm
            
        except Exception as e:
            self.logger.error(f"Failed to create LLM client: {e}")
            return None


class CrewManager:
    """
    CrewManager - Multi-Agent System with Ollama Integration
    Manages CrewAI agents with local Ollama LLM
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._is_initialized = False
        self._llm: Optional[ChatOpenAI] = None
        self._ollama_manager = OllamaManager()
        
        # Agent configurations
        self._agent_configs = {
            "architect": {
                "role": "System Architect",
                "description": "Analyzes code architecture and implements self-improvement optimizations",
                "tools": ["get_system_state_summary", "analyze_performance", "execute_live_patch", "trigger_graceful_restart"]
            },
            "system_analyst": {
                "role": "System Analyst",
                "description": "Analyzes system performance and identifies optimization opportunities",
                "tools": ["get_system_state_summary", "analyze_performance", "identify_bottlenecks"]
            },
            "code_reviewer": {
                "role": "Code Reviewer", 
                "description": "Reviews code changes and ensures quality standards",
                "tools": ["review_code_changes", "validate_syntax", "check_security"]
            },
            "evolution_planner": {
                "role": "Evolution Planner",
                "description": "Plans system evolution and self-improvement strategies",
                "tools": ["plan_evolution", "create_improvement_plan", "assess_risks"]
            },
            "security_monitor": {
                "role": "Security Monitor",
                "description": "Monitors security and ethical compliance",
                "tools": ["check_security_status", "audit_actions", "validate_ethics"]
            }
        }
        
        self._agents: Dict[str, Any] = {}
        self._active_crews: Dict[str, Dict[str, Any]] = {}
        self._tools: List[Any] = []
        
    def initialize(self):
        """Initialize CrewManager with Ollama LLM"""
        try:
            self.logger.info("Initializing CrewManager...")
            
            # Check Ollama availability
            if not self._ollama_manager.check_ollama_server():
                raise RuntimeError("Ollama server not available - required for CrewManager")
            
            # Get available models
            models = self._ollama_manager.get_available_models()
            if not models:
                raise RuntimeError("No Ollama models available")
            
            self.logger.info(f"Available models: {[m.name for m in models]}")
            
            # Create LLM client
            self._llm = self._ollama_manager.create_llm_client()
            if not self._llm:
                # Fallback to simulation mode
                self.logger.warning("LLM client creation failed, using simulation mode")
                self._llm = None
            
            # Create agents (only if LLM is available)
            if self._llm:
                self._create_agents()
                self.logger.info("CrewManager successfully initialized with LLM")
            else:
                self.logger.info("CrewManager initialized in simulation mode")
            
            self._is_initialized = True
            
        except Exception as e:
            self.logger.error(f"CrewManager initialization failed: {e}")
            raise
    
    def _create_agents(self):
        """Create and configure agents"""
        self.logger.info("Creating agents...")
        
        # Check if LLM is available
        if not self._llm:
            self.logger.warning("LLM not available, creating fallback agents")
            return self._create_fallback_agents()
        
        # Get available tools
        from psyche.agent_tools import AgentTools
        agent_tools = AgentTools()
        self._tools = agent_tools.get_all_tools()
        available_tools_map = {tool.name: tool for tool in self._tools}
        
        created_agents = {}
        
        for agent_name, config in self._agent_configs.items():
            agent_tools_names = config.get('tools', [])
            agent_tools_list = [available_tools_map[name] for name in agent_tools_names if name in available_tools_map]
            
            if not agent_tools_list:
                self.logger.warning(f"No tools found for agent '{agent_name}', creating fallback")
                created_agents[agent_name] = self._create_fallback_agent(agent_name, config)
                continue
            
            try:
                # Create prompt template
                prompt_template = ChatPromptTemplate.from_messages([
                    ("system", f"You are {config['role']}. {config['description']}. Your task is to perform your role flawlessly using available tools."),
                    MessagesPlaceholder(variable_name="chat_history", optional=True),
                    ("human", "{input}"),
                    MessagesPlaceholder(variable_name="agent_scratchpad"),
                ])
                
                # Create agent
                agent = create_openai_functions_agent(
                    llm=self._llm,
                    tools=agent_tools_list,
                    prompt=prompt_template
                )
                
                # Create executor
                agent_executor = AgentExecutor(
                    agent=agent,
                    tools=agent_tools_list,
                    verbose=True,
                    handle_parsing_errors=True,
                    logger=self.logger
                )
                
                created_agents[agent_name] = agent_executor
                self.logger.info(f"Agent '{agent_name}' created with {len(agent_tools_list)} tools")
                
            except Exception as e:
                self.logger.error(f"Failed to create agent '{agent_name}': {e}")
                created_agents[agent_name] = self._create_fallback_agent(agent_name, config)
        
        self._agents = created_agents
        return created_agents
    
    def _create_fallback_agents(self):
        """Create simple fallback agents without LLM"""
        self.logger.info("Creating fallback agents...")
        created_agents = {}
        
        for agent_name, config in self._agent_configs.items():
            created_agents[agent_name] = self._create_fallback_agent(agent_name, config)
        
        return created_agents
    
    def _create_fallback_agent(self, agent_name: str, config: Dict[str, Any]):
        """Create a simple fallback agent"""
        class FallbackAgent:
            def __init__(self, name, role, description):
                self.name = name
                self.role = role
                self.description = description
                self.logger = logging.getLogger(f"fallback_agent.{name}")
            
            def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
                """Simple fallback response"""
                user_input = input_data.get("input", "")
                
                # Simple response based on agent type
                if "architect" in self.name.lower():
                    response = f"Я {self.role}. Анализирую код и архитектуру. Вход: {user_input}"
                elif "analyst" in self.name.lower():
                    response = f"Я {self.role}. Провожу анализ данных. Вход: {user_input}"
                elif "researcher" in self.name.lower():
                    response = f"Я {self.role}. Исследую информацию. Вход: {user_input}"
                else:
                    response = f"Я {self.role}. Обрабатываю запрос: {user_input}"
                
                self.logger.info(f"Fallback response for {self.name}: {response}")
                
                return {
                    "output": response,
                    "agent_name": self.name,
                    "fallback": True
                }
        
        return FallbackAgent(
            name=agent_name,
            role=config.get('role', 'Assistant'),
            description=config.get('description', 'Fallback agent')
        )
    
    def create_crew(self, crew_name: str, agents: List[str], task: str) -> Dict[str, Any]:
        """
        Create CrewAI crew with specified agents and task
        
        Args:
            crew_name: Name of the crew
            agents: List of agent names to include
            task: Task description for the crew
            
        Returns:
            Crew information
        """
        if not self._is_initialized:
            raise RuntimeError("CrewManager not initialized")
        
        try:
            # Validate agents
            valid_agents = []
            for agent in agents:
                if agent in self._agent_configs:
                    valid_agents.append(agent)
                else:
                    self.logger.warning(f"Unknown agent: {agent}")
            
            if not valid_agents:
                raise ValueError("No valid agents for crew")
            
            # Create CrewAI crew if available
            if CREWAI_AVAILABLE:
                crew_agents = []
                for agent_name in valid_agents:
                    if agent_name in self._agents:
                        agent_config = self._agent_configs[agent_name]
                        crew_agent = Agent(
                            role=agent_config['role'],
                            goal=agent_config['description'],
                            backstory=f"You are {agent_config['role']} with expertise in {agent_config['description']}",
                            tools=self._get_agent_tools(agent_name),
                            verbose=True
                        )
                        crew_agents.append(crew_agent)
                
                # Create task
                crew_task = Task(
                    description=task,
                    agent=crew_agents[0] if crew_agents else None
                )
                
                # Create crew
                crew = Crew(
                    agents=crew_agents,
                    tasks=[crew_task],
                    verbose=True
                )
                
                crew_info = {
                    "name": crew_name,
                    "agents": valid_agents,
                    "task": task,
                    "status": "created",
                    "created_at": time.time(),
                    "crew_object": crew
                }
                
            else:
                # Fallback to legacy mode
                crew_info = {
                    "name": crew_name,
                    "agents": valid_agents,
                    "task": task,
                    "status": "created_legacy",
                    "created_at": time.time()
                }
            
            self._active_crews[crew_name] = crew_info
            self.logger.info(f"Created crew: {crew_name} with agents: {valid_agents}")
            
            return crew_info
            
        except Exception as e:
            self.logger.error(f"Crew creation failed: {e}")
            raise
    
    def execute_crew_task(self, crew_name: str) -> Dict[str, Any]:
        """
        Execute task with specified crew
        
        Args:
            crew_name: Name of the crew to execute
            
        Returns:
            Execution results
        """
        if not self._is_initialized:
            raise RuntimeError("CrewManager not initialized")
        
        if crew_name not in self._active_crews:
            raise ValueError(f"Crew '{crew_name}' not found")
        
        try:
            crew_info = self._active_crews[crew_name]
            
            # Check system resources before execution
            resources = self._ollama_manager.get_system_resources()
            self.logger.info(f"System resources before execution: {resources}")
            
            # Execute crew task
            if CREWAI_AVAILABLE and "crew_object" in crew_info:
                crew = crew_info["crew_object"]
                result = crew.kickoff()
                
                execution_info = {
                    "crew_name": crew_name,
                    "task": crew_info["task"],
                    "agents": crew_info["agents"],
                    "timestamp": time.time(),
                    "status": "completed",
                    "result": result,
                    "resources_before": resources,
                    "resources_after": self._ollama_manager.get_system_resources()
                }
                
            else:
                # Legacy execution
                execution_info = self._execute_legacy_task(crew_name)
            
            # Log execution
            self._log_execution_event(execution_info)
            
            return execution_info
            
        except Exception as e:
            self.logger.error(f"Crew execution failed: {e}")
            raise
    
    def _execute_legacy_task(self, crew_name: str) -> Dict[str, Any]:
        """Execute task in legacy mode without CrewAI"""
        crew_info = self._active_crews[crew_name]
        
        results = {}
        for agent_name in crew_info["agents"]:
            if agent_name in self._agents:
                try:
                    agent_executor = self._agents[agent_name]
                    result = agent_executor.invoke({"input": crew_info["task"]})
                    results[agent_name] = result
                except Exception as e:
                    self.logger.error(f"Agent {agent_name} execution failed: {e}")
                    results[agent_name] = {"error": str(e)}
        
        return {
            "crew_name": crew_name,
            "task": crew_info["task"],
            "agents": crew_info["agents"],
            "timestamp": time.time(),
            "status": "completed_legacy",
            "results": results
        }
    
    def _get_agent_tools(self, agent_name: str) -> List[Any]:
        """Get tools for specific agent"""
        if agent_name in self._agent_configs:
            tool_names = self._agent_configs[agent_name].get('tools', [])
            return [tool for tool in self._tools if tool.name in tool_names]
        return []
    
    def _log_execution_event(self, execution_info: Dict[str, Any]):
        """Log execution event to consciousness monitor"""
        try:
            from evaluation.consciousness_monitor import ConsciousnessMonitor
            monitor = ConsciousnessMonitor()
            monitor.log_crew_execution(execution_info)
        except Exception as e:
            self.logger.warning(f"Failed to log to consciousness monitor: {e}")
    
    def get_crew_status(self, crew_name: str) -> Dict[str, Any]:
        """Get status of specific crew"""
        if crew_name in self._active_crews:
            return self._active_crews[crew_name]
        return {"status": "not_found"}
    
    def list_crews(self) -> List[Dict[str, Any]]:
        """List all active crews"""
        return list(self._active_crews.values())
    
    def get_available_agents(self) -> Dict[str, Dict[str, Any]]:
        """Get available agents configuration"""
        return self._agent_configs
    
    def get_crew_manager_status(self) -> Dict[str, Any]:
        """Get overall CrewManager status"""
        return {
            "initialized": self._is_initialized,
            "llm_available": self._llm is not None,
            "ollama_available": self._ollama_manager.check_ollama_server(),
            "available_models": [m.name for m in self._ollama_manager.get_available_models()],
            "active_agents": len(self._agents),
            "active_crews": len(self._active_crews),
            "crewai_available": CREWAI_AVAILABLE,
            "system_resources": self._ollama_manager.get_system_resources()
        }


# Import for configuration
from config import config
from utils.secret_loader import get_secret 