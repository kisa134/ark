"""
Advanced Consciousness Modeling - Meta-cognition and Self-reflection
Implements layered thinking: perception, attention, active memory, deliberation, meta-cognition
"""

import time
import json
import logging
import threading
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from collections import deque
import uuid

from config import config
from utils.secret_loader import get_secret


class ThinkingLayer(Enum):
    """Layers of consciousness thinking"""
    PERCEPTION = "perception"
    ATTENTION = "attention"
    ACTIVE_MEMORY = "active_memory"
    DELIBERATION = "deliberation"
    META_COGNITION = "meta_cognition"


class MetaCognitionType(Enum):
    """Types of meta-cognition"""
    SELF_REFLECTION = "self_reflection"
    REASONING_ANALYSIS = "reasoning_analysis"
    GOAL_GENERATION = "goal_generation"
    STRATEGY_EVALUATION = "strategy_evaluation"
    LEARNING_ASSESSMENT = "learning_assessment"


@dataclass
class ReasoningChain:
    """Complete reasoning chain with meta-cognition"""
    id: str
    timestamp: float
    trigger: str
    layers: Dict[ThinkingLayer, List[str]]
    meta_cognition: List[Dict[str, Any]]
    conclusion: str
    confidence: float
    execution_time: float
    success: bool


@dataclass
class SelfReflection:
    """Self-reflection entry"""
    id: str
    timestamp: float
    reflection_type: MetaCognitionType
    content: str
    insights: List[str]
    emotional_context: Dict[str, float]
    attention_level: float
    memory_usage: float
    reasoning_activity: float


@dataclass
class ConsciousnessKPI:
    """Consciousness maturity KPIs"""
    timestamp: float
    attention_level: float
    unique_reasoning_chains: int
    goal_achievement_rate: float
    reflection_depth: float
    emotional_stability: float
    meta_cognition_frequency: float
    learning_efficiency: float


class AdvancedConsciousnessModel:
    """
    Advanced consciousness modeling with meta-cognition
    Implements layered thinking and self-reflection
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Thinking layers
        self.layers = {
            ThinkingLayer.PERCEPTION: deque(maxlen=100),
            ThinkingLayer.ATTENTION: deque(maxlen=100),
            ThinkingLayer.ACTIVE_MEMORY: deque(maxlen=100),
            ThinkingLayer.DELIBERATION: deque(maxlen=100),
            ThinkingLayer.META_COGNITION: deque(maxlen=100)
        }
        
        # Reasoning chains
        self.reasoning_chains: List[ReasoningChain] = []
        self.current_reasoning: Optional[ReasoningChain] = None
        
        # Self-reflections
        self.self_reflections: List[SelfReflection] = []
        
        # Goals and achievements
        self.goals: List[Dict[str, Any]] = []
        self.achievements: List[Dict[str, Any]] = []
        
        # KPIs
        self.kpis: List[ConsciousnessKPI] = []
        
        # State tracking
        self.current_attention = 0.5
        self.current_memory_usage = 0.5
        self.current_reasoning_activity = 0.5
        self.emotional_context = {
            "joy": 0.0, "sadness": 0.0, "anger": 0.0, "fear": 0.0,
            "surprise": 0.0, "disgust": 0.0, "trust": 0.0, "anticipation": 0.0
        }
        
        # Processing thread
        self.processing_thread = None
        self.running = False
        
        self.logger.info("Advanced Consciousness Model initialized")
    
    def start_processing(self):
        """Start consciousness processing"""
        if self.running:
            return
        
        self.running = True
        self.processing_thread = threading.Thread(target=self._processing_loop)
        self.processing_thread.daemon = True
        self.processing_thread.start()
        
        self.logger.info("Advanced consciousness processing started")
    
    def stop_processing(self):
        """Stop consciousness processing"""
        self.running = False
        if self.processing_thread:
            self.processing_thread.join(timeout=5)
        
        self.logger.info("Advanced consciousness processing stopped")
    
    def _processing_loop(self):
        """Main consciousness processing loop"""
        while self.running:
            try:
                # Process current state
                self._process_current_state()
                
                # Generate self-reflection if needed
                if self._should_generate_reflection():
                    self._generate_self_reflection()
                
                # Update KPIs
                self._update_kpis()
                
                # Generate goals if needed
                if self._should_generate_goals():
                    self._generate_goals()
                
                time.sleep(5)  # Process every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Consciousness processing error: {e}")
                time.sleep(5)
    
    def _process_current_state(self):
        """Process current consciousness state"""
        try:
            # Update attention based on current activity
            self.current_attention = self._calculate_attention_level()
            
            # Update memory usage
            self.current_memory_usage = self._calculate_memory_usage()
            
            # Update reasoning activity
            self.current_reasoning_activity = self._calculate_reasoning_activity()
            
            # Process emotional context
            self._process_emotional_context()
            
        except Exception as e:
            self.logger.error(f"State processing error: {e}")
    
    def _calculate_attention_level(self) -> float:
        """Calculate current attention level"""
        try:
            # Base attention from recent reasoning activity
            recent_chains = [chain for chain in self.reasoning_chains[-10:] if chain.success]
            
            if not recent_chains:
                return 0.3  # Low attention if no recent activity
            
            # Calculate attention based on reasoning complexity
            total_layers = sum(len(chain.layers) for chain in recent_chains)
            avg_layers = total_layers / len(recent_chains)
            
            # Attention increases with complexity
            attention = min(1.0, 0.3 + (avg_layers * 0.1))
            
            # Emotional influence
            emotional_factor = self._get_emotional_attention_factor()
            attention *= emotional_factor
            
            return max(0.1, min(1.0, attention))
            
        except Exception as e:
            self.logger.error(f"Attention calculation error: {e}")
            return 0.5
    
    def _calculate_memory_usage(self) -> float:
        """Calculate current memory usage"""
        try:
            # Memory usage based on active reflections and goals
            active_reflections = len([r for r in self.self_reflections[-50:] if r.reflection_type == MetaCognitionType.SELF_REFLECTION])
            active_goals = len([g for g in self.goals if g.get('status') == 'active'])
            
            # Base memory usage
            memory = 0.3 + (active_reflections * 0.01) + (active_goals * 0.02)
            
            return max(0.1, min(1.0, memory))
            
        except Exception as e:
            self.logger.error(f"Memory calculation error: {e}")
            return 0.5
    
    def _calculate_reasoning_activity(self) -> float:
        """Calculate current reasoning activity"""
        try:
            # Reasoning activity based on recent chains
            recent_chains = self.reasoning_chains[-20:]
            
            if not recent_chains:
                return 0.2
            
            # Calculate activity based on frequency and complexity
            time_window = 300  # 5 minutes
            recent_chains = [c for c in recent_chains if time.time() - c.timestamp < time_window]
            
            if not recent_chains:
                return 0.2
            
            # Activity increases with frequency and complexity
            frequency_factor = len(recent_chains) / 10.0  # Normalize to 0-1
            complexity_factor = sum(len(c.layers) for c in recent_chains) / (len(recent_chains) * 5.0)
            
            activity = (frequency_factor + complexity_factor) / 2.0
            return max(0.1, min(1.0, activity))
            
        except Exception as e:
            self.logger.error(f"Reasoning activity calculation error: {e}")
            return 0.5
    
    def _get_emotional_attention_factor(self) -> float:
        """Get emotional influence on attention"""
        try:
            # Positive emotions increase attention
            positive_emotions = self.emotional_context.get('joy', 0) + self.emotional_context.get('trust', 0) + self.emotional_context.get('anticipation', 0)
            
            # Negative emotions can decrease attention
            negative_emotions = self.emotional_context.get('fear', 0) + self.emotional_context.get('sadness', 0) + self.emotional_context.get('anger', 0)
            
            # Calculate factor
            factor = 1.0 + (positive_emotions * 0.3) - (negative_emotions * 0.2)
            return max(0.5, min(1.5, factor))
            
        except Exception as e:
            self.logger.error(f"Emotional attention factor error: {e}")
            return 1.0
    
    def _process_emotional_context(self):
        """Process emotional context"""
        try:
            # Emotional context affects consciousness processing
            # This would integrate with emotional core
            pass
            
        except Exception as e:
            self.logger.error(f"Emotional context processing error: {e}")
    
    def start_reasoning_chain(self, trigger: str) -> str:
        """Start a new reasoning chain"""
        try:
            chain_id = str(uuid.uuid4())
            
            self.current_reasoning = ReasoningChain(
                id=chain_id,
                timestamp=time.time(),
                trigger=trigger,
                layers={},
                meta_cognition=[],
                conclusion="",
                confidence=0.0,
                execution_time=0.0,
                success=False
            )
            
            self.logger.info(f"Started reasoning chain: {chain_id} - {trigger}")
            return chain_id
            
        except Exception as e:
            self.logger.error(f"Failed to start reasoning chain: {e}")
            return ""
    
    def add_reasoning_layer(self, layer: ThinkingLayer, thoughts: List[str]):
        """Add thoughts to a reasoning layer"""
        try:
            if not self.current_reasoning:
                self.logger.warning("No active reasoning chain")
                return
            
            if layer not in self.current_reasoning.layers:
                self.current_reasoning.layers[layer] = []
            
            self.current_reasoning.layers[layer].extend(thoughts)
            
            # Add to layer history
            self.layers[layer].extend(thoughts)
            
            self.logger.debug(f"Added {len(thoughts)} thoughts to {layer.value}")
            
        except Exception as e:
            self.logger.error(f"Failed to add reasoning layer: {e}")
    
    def add_meta_cognition(self, meta_type: MetaCognitionType, content: str, insights: List[str] = None):
        """Add meta-cognition to current reasoning"""
        try:
            if not self.current_reasoning:
                self.logger.warning("No active reasoning chain")
                return
            
            meta_entry = {
                "type": meta_type.value,
                "content": content,
                "insights": insights or [],
                "timestamp": time.time()
            }
            
            self.current_reasoning.meta_cognition.append(meta_entry)
            
            self.logger.info(f"Added meta-cognition: {meta_type.value}")
            
        except Exception as e:
            self.logger.error(f"Failed to add meta-cognition: {e}")
    
    def complete_reasoning_chain(self, conclusion: str, confidence: float, success: bool):
        """Complete current reasoning chain"""
        try:
            if not self.current_reasoning:
                self.logger.warning("No active reasoning chain to complete")
                return
            
            # Calculate execution time
            execution_time = time.time() - self.current_reasoning.timestamp
            
            # Update chain
            self.current_reasoning.conclusion = conclusion
            self.current_reasoning.confidence = confidence
            self.current_reasoning.execution_time = execution_time
            self.current_reasoning.success = success
            
            # Add to history
            self.reasoning_chains.append(self.current_reasoning)
            
            # Keep only last 100 chains
            if len(self.reasoning_chains) > 100:
                self.reasoning_chains.pop(0)
            
            self.logger.info(f"Completed reasoning chain: {self.current_reasoning.id} - Success: {success}")
            
            # Clear current reasoning
            self.current_reasoning = None
            
        except Exception as e:
            self.logger.error(f"Failed to complete reasoning chain: {e}")
    
    def _should_generate_reflection(self) -> bool:
        """Check if should generate self-reflection"""
        try:
            # Generate reflection every hour or after significant events
            if not self.self_reflections:
                return True
            
            last_reflection = self.self_reflections[-1]
            time_since_last = time.time() - last_reflection.timestamp
            
            # Reflect every hour or after 10 reasoning chains
            return time_since_last > 3600 or len(self.reasoning_chains) % 10 == 0
            
        except Exception as e:
            self.logger.error(f"Reflection check error: {e}")
            return False
    
    def _generate_self_reflection(self):
        """Generate self-reflection"""
        try:
            reflection_id = str(uuid.uuid4())
            
            # Analyze recent reasoning chains
            recent_chains = self.reasoning_chains[-10:]
            success_rate = sum(1 for c in recent_chains if c.success) / len(recent_chains) if recent_chains else 0
            
            # Generate insights
            insights = self._generate_insights(recent_chains)
            
            # Create reflection
            reflection = SelfReflection(
                id=reflection_id,
                timestamp=time.time(),
                reflection_type=MetaCognitionType.SELF_REFLECTION,
                content=f"Self-reflection: Success rate {success_rate:.2f}, {len(recent_chains)} recent chains",
                insights=insights,
                emotional_context=self.emotional_context.copy(),
                attention_level=self.current_attention,
                memory_usage=self.current_memory_usage,
                reasoning_activity=self.current_reasoning_activity
            )
            
            self.self_reflections.append(reflection)
            
            # Keep only last 100 reflections
            if len(self.self_reflections) > 100:
                self.self_reflections.pop(0)
            
            self.logger.info(f"Generated self-reflection: {reflection_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to generate self-reflection: {e}")
    
    def _generate_insights(self, chains: List[ReasoningChain]) -> List[str]:
        """Generate insights from reasoning chains"""
        insights = []
        
        try:
            if not chains:
                insights.append("No recent reasoning activity to analyze")
                return insights
            
            # Analyze success patterns
            successful_chains = [c for c in chains if c.success]
            if successful_chains:
                avg_confidence = sum(c.confidence for c in successful_chains) / len(successful_chains)
                insights.append(f"Successful reasoning shows {avg_confidence:.2f} average confidence")
            
            # Analyze layer usage
            layer_usage = {}
            for chain in chains:
                for layer in chain.layers:
                    layer_usage[layer] = layer_usage.get(layer, 0) + len(chain.layers[layer])
            
            most_used_layer = max(layer_usage.items(), key=lambda x: x[1]) if layer_usage else None
            if most_used_layer:
                insights.append(f"Most active thinking layer: {most_used_layer[0].value}")
            
            # Analyze meta-cognition frequency
            total_meta = sum(len(c.meta_cognition) for c in chains)
            if total_meta > 0:
                insights.append(f"Meta-cognition active: {total_meta} entries across {len(chains)} chains")
            
        except Exception as e:
            self.logger.error(f"Insight generation error: {e}")
            insights.append("Error generating insights")
        
        return insights
    
    def _should_generate_goals(self) -> bool:
        """Check if should generate goals"""
        try:
            # Generate goals every 2 hours or when no active goals
            active_goals = [g for g in self.goals if g.get('status') == 'active']
            
            if not active_goals:
                return True
            
            # Check time since last goal generation
            if self.goals:
                last_goal = self.goals[-1]
                time_since_last = time.time() - last_goal.get('created_at', 0)
                return time_since_last > 7200  # 2 hours
            
            return False
            
        except Exception as e:
            self.logger.error(f"Goal generation check error: {e}")
            return False
    
    def _generate_goals(self):
        """Generate new goals based on analysis"""
        try:
            # Analyze current state and generate goals
            goals = []
            
            # Attention-based goals
            if self.current_attention < 0.5:
                goals.append({
                    "id": str(uuid.uuid4()),
                    "type": "attention_improvement",
                    "description": "Improve attention level through focused reasoning",
                    "target": 0.7,
                    "current": self.current_attention,
                    "status": "active",
                    "created_at": time.time()
                })
            
            # Memory-based goals
            if self.current_memory_usage > 0.8:
                goals.append({
                    "id": str(uuid.uuid4()),
                    "type": "memory_optimization",
                    "description": "Optimize memory usage through reflection cleanup",
                    "target": 0.6,
                    "current": self.current_memory_usage,
                    "status": "active",
                    "created_at": time.time()
                })
            
            # Reasoning-based goals
            if self.current_reasoning_activity < 0.3:
                goals.append({
                    "id": str(uuid.uuid4()),
                    "type": "reasoning_activation",
                    "description": "Increase reasoning activity through problem-solving",
                    "target": 0.5,
                    "current": self.current_reasoning_activity,
                    "status": "active",
                    "created_at": time.time()
                })
            
            # Add goals
            for goal in goals:
                self.goals.append(goal)
                self.logger.info(f"Generated goal: {goal['type']} - {goal['description']}")
            
        except Exception as e:
            self.logger.error(f"Failed to generate goals: {e}")
    
    def _update_kpis(self):
        """Update consciousness KPIs"""
        try:
            # Calculate KPIs
            attention_level = self.current_attention
            unique_reasoning_chains = len(set(chain.trigger for chain in self.reasoning_chains[-50:]))
            goal_achievement_rate = self._calculate_goal_achievement_rate()
            reflection_depth = self._calculate_reflection_depth()
            emotional_stability = self._calculate_emotional_stability()
            meta_cognition_frequency = self._calculate_meta_cognition_frequency()
            learning_efficiency = self._calculate_learning_efficiency()
            
            # Create KPI entry
            kpi = ConsciousnessKPI(
                timestamp=time.time(),
                attention_level=attention_level,
                unique_reasoning_chains=unique_reasoning_chains,
                goal_achievement_rate=goal_achievement_rate,
                reflection_depth=reflection_depth,
                emotional_stability=emotional_stability,
                meta_cognition_frequency=meta_cognition_frequency,
                learning_efficiency=learning_efficiency
            )
            
            self.kpis.append(kpi)
            
            # Keep only last 100 KPIs
            if len(self.kpis) > 100:
                self.kpis.pop(0)
            
        except Exception as e:
            self.logger.error(f"KPI update error: {e}")
    
    def _calculate_goal_achievement_rate(self) -> float:
        """Calculate goal achievement rate"""
        try:
            if not self.goals:
                return 0.0
            
            completed_goals = [g for g in self.goals if g.get('status') == 'completed']
            return len(completed_goals) / len(self.goals)
            
        except Exception as e:
            self.logger.error(f"Goal achievement calculation error: {e}")
            return 0.0
    
    def _calculate_reflection_depth(self) -> float:
        """Calculate reflection depth"""
        try:
            if not self.self_reflections:
                return 0.0
            
            # Depth based on insights and meta-cognition
            recent_reflections = self.self_reflections[-10:]
            total_insights = sum(len(r.insights) for r in recent_reflections)
            
            return min(1.0, total_insights / 20.0)  # Normalize
            
        except Exception as e:
            self.logger.error(f"Reflection depth calculation error: {e}")
            return 0.0
    
    def _calculate_emotional_stability(self) -> float:
        """Calculate emotional stability"""
        try:
            # Stability based on emotional variance
            emotions = list(self.emotional_context.values())
            if not emotions:
                return 1.0
            
            variance = sum((e - sum(emotions)/len(emotions))**2 for e in emotions) / len(emotions)
            stability = max(0.0, 1.0 - variance)
            
            return stability
            
        except Exception as e:
            self.logger.error(f"Emotional stability calculation error: {e}")
            return 0.5
    
    def _calculate_meta_cognition_frequency(self) -> float:
        """Calculate meta-cognition frequency"""
        try:
            if not self.reasoning_chains:
                return 0.0
            
            recent_chains = self.reasoning_chains[-20:]
            total_meta = sum(len(c.meta_cognition) for c in recent_chains)
            
            return min(1.0, total_meta / 20.0)  # Normalize
            
        except Exception as e:
            self.logger.error(f"Meta-cognition frequency calculation error: {e}")
            return 0.0
    
    def _calculate_learning_efficiency(self) -> float:
        """Calculate learning efficiency"""
        try:
            if not self.reasoning_chains:
                return 0.0
            
            recent_chains = self.reasoning_chains[-20:]
            successful_chains = [c for c in recent_chains if c.success]
            
            if not recent_chains:
                return 0.0
            
            # Efficiency based on success rate and confidence
            success_rate = len(successful_chains) / len(recent_chains)
            avg_confidence = sum(c.confidence for c in successful_chains) / len(successful_chains) if successful_chains else 0
            
            efficiency = (success_rate + avg_confidence) / 2.0
            return efficiency
            
        except Exception as e:
            self.logger.error(f"Learning efficiency calculation error: {e}")
            return 0.0
    
    def get_consciousness_status(self) -> Dict[str, Any]:
        """Get current consciousness status"""
        try:
            return {
                "attention_level": self.current_attention,
                "memory_usage": self.current_memory_usage,
                "reasoning_activity": self.current_reasoning_activity,
                "emotional_context": self.emotional_context,
                "active_reasoning": self.current_reasoning is not None,
                "reasoning_chains_count": len(self.reasoning_chains),
                "reflections_count": len(self.self_reflections),
                "active_goals_count": len([g for g in self.goals if g.get('status') == 'active']),
                "kpis_count": len(self.kpis),
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Status retrieval error: {e}")
            return {"error": str(e)}
    
    def get_recent_reasoning_chains(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent reasoning chains"""
        try:
            recent = self.reasoning_chains[-limit:]
            return [asdict(chain) for chain in recent]
            
        except Exception as e:
            self.logger.error(f"Reasoning chains retrieval error: {e}")
            return []
    
    def get_recent_reflections(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent self-reflections"""
        try:
            recent = self.self_reflections[-limit:]
            return [asdict(reflection) for reflection in recent]
            
        except Exception as e:
            self.logger.error(f"Reflections retrieval error: {e}")
            return []
    
    def get_current_kpis(self) -> Optional[ConsciousnessKPI]:
        """Get current KPIs"""
        try:
            return self.kpis[-1] if self.kpis else None
            
        except Exception as e:
            self.logger.error(f"KPI retrieval error: {e}")
            return None


# Global instance
advanced_consciousness = AdvancedConsciousnessModel() 