#!/usr/bin/env python3
"""
ARK v2.8 - Meta Observer "Герольд"
Analyzes long-term patterns in consciousness and emotional states
"""

import time
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter

from memory.deep_memory import deep_memory, MemoryType, MemoryPriority


@dataclass
class ConsciousnessPattern:
    """Pattern in consciousness behavior"""
    pattern_type: str
    frequency: float
    duration: float
    intensity: float
    triggers: List[str]
    consequences: List[str]
    emotional_correlation: Dict[str, float]
    reasoning_depth_avg: float
    attention_level_avg: float


@dataclass
class EmotionalPattern:
    """Pattern in emotional behavior"""
    emotion: str
    frequency: float
    duration: float
    intensity: float
    triggers: List[str]
    transitions: Dict[str, float]
    consciousness_correlation: Dict[str, float]


@dataclass
class ReasoningPattern:
    """Pattern in reasoning behavior"""
    reasoning_type: str
    frequency: float
    success_rate: float
    depth_avg: float
    attention_required: float
    emotional_impact: Dict[str, float]
    consciousness_states: List[str]


class MetaObserver:
    """Meta-observer for analyzing consciousness patterns"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.analysis_interval = 3600  # 1 hour
        self.last_analysis = 0
        
        # Pattern storage
        self.consciousness_patterns: List[ConsciousnessPattern] = []
        self.emotional_patterns: List[EmotionalPattern] = []
        self.reasoning_patterns: List[ReasoningPattern] = []
        
        # Analysis cache
        self.recent_analysis = {}
        self.pattern_history = []
        
        # Alert thresholds
        self.stress_threshold = 0.7
        self.fatigue_threshold = 0.6
        self.evolution_threshold = 0.8
        
        self.logger.info("Meta Observer 'Герольд' initialized")
    
    def analyze_consciousness_patterns(self, hours: int = 24) -> List[ConsciousnessPattern]:
        """Analyze consciousness patterns over time"""
        try:
            # Get recent memories
            memories = deep_memory.get_recent_memories(hours, MemoryType.REASONING)
            
            # Group by consciousness state
            state_groups = defaultdict(list)
            for memory in memories:
                state = memory.consciousness_state
                state_groups[state].append(memory)
            
            patterns = []
            
            for state, state_memories in state_groups.items():
                if len(state_memories) < 3:  # Need minimum occurrences
                    continue
                
                # Calculate pattern metrics
                frequency = len(state_memories) / hours
                duration = self._calculate_duration(state_memories)
                intensity = self._calculate_intensity(state_memories)
                
                # Find triggers
                triggers = self._find_triggers(state_memories)
                
                # Find consequences
                consequences = self._find_consequences(state_memories)
                
                # Emotional correlation
                emotional_correlation = self._calculate_emotional_correlation(state_memories)
                
                # Average metrics
                reasoning_depth_avg = sum(m.reasoning_depth for m in state_memories) / len(state_memories)
                attention_level_avg = sum(m.attention_level for m in state_memories) / len(state_memories)
                
                pattern = ConsciousnessPattern(
                    pattern_type=state,
                    frequency=frequency,
                    duration=duration,
                    intensity=intensity,
                    triggers=triggers,
                    consequences=consequences,
                    emotional_correlation=emotional_correlation,
                    reasoning_depth_avg=reasoning_depth_avg,
                    attention_level_avg=attention_level_avg
                )
                
                patterns.append(pattern)
            
            self.consciousness_patterns = patterns
            return patterns
            
        except Exception as e:
            self.logger.error(f"Failed to analyze consciousness patterns: {e}")
            return []
    
    def analyze_emotional_patterns(self, hours: int = 24) -> List[EmotionalPattern]:
        """Analyze emotional patterns over time"""
        try:
            # Get recent emotional memories
            memories = deep_memory.get_recent_memories(hours, MemoryType.EMOTION)
            
            # Group by emotion
            emotion_groups = defaultdict(list)
            for memory in memories:
                # Extract primary emotion from emotional trace
                if memory.emotional_trace:
                    primary_emotion = max(memory.emotional_trace.items(), key=lambda x: x[1])[0]
                    emotion_groups[primary_emotion].append(memory)
            
            patterns = []
            
            for emotion, emotion_memories in emotion_groups.items():
                if len(emotion_memories) < 2:  # Need minimum occurrences
                    continue
                
                # Calculate pattern metrics
                frequency = len(emotion_memories) / hours
                duration = self._calculate_duration(emotion_memories)
                intensity = self._calculate_intensity(emotion_memories)
                
                # Find triggers
                triggers = self._find_triggers(emotion_memories)
                
                # Find transitions
                transitions = self._find_emotional_transitions(emotion_memories)
                
                # Consciousness correlation
                consciousness_correlation = self._calculate_consciousness_correlation(emotion_memories)
                
                pattern = EmotionalPattern(
                    emotion=emotion,
                    frequency=frequency,
                    duration=duration,
                    intensity=intensity,
                    triggers=triggers,
                    transitions=transitions,
                    consciousness_correlation=consciousness_correlation
                )
                
                patterns.append(pattern)
            
            self.emotional_patterns = patterns
            return patterns
            
        except Exception as e:
            self.logger.error(f"Failed to analyze emotional patterns: {e}")
            return []
    
    def analyze_reasoning_patterns(self, hours: int = 24) -> List[ReasoningPattern]:
        """Analyze reasoning patterns over time"""
        try:
            # Get recent reasoning memories
            memories = deep_memory.get_recent_memories(hours, MemoryType.REASONING)
            
            # Group by reasoning depth
            depth_groups = defaultdict(list)
            for memory in memories:
                depth_category = self._categorize_reasoning_depth(memory.reasoning_depth)
                depth_groups[depth_category].append(memory)
            
            patterns = []
            
            for reasoning_type, reasoning_memories in depth_groups.items():
                if len(reasoning_memories) < 2:
                    continue
                
                # Calculate pattern metrics
                frequency = len(reasoning_memories) / hours
                success_rate = self._calculate_success_rate(reasoning_memories)
                depth_avg = sum(m.reasoning_depth for m in reasoning_memories) / len(reasoning_memories)
                attention_required = sum(m.attention_level for m in reasoning_memories) / len(reasoning_memories)
                
                # Emotional impact
                emotional_impact = self._calculate_emotional_impact(reasoning_memories)
                
                # Consciousness states
                consciousness_states = list(set(m.consciousness_state for m in reasoning_memories))
                
                pattern = ReasoningPattern(
                    reasoning_type=reasoning_type,
                    frequency=frequency,
                    success_rate=success_rate,
                    depth_avg=depth_avg,
                    attention_required=attention_required,
                    emotional_impact=emotional_impact,
                    consciousness_states=consciousness_states
                )
                
                patterns.append(pattern)
            
            self.reasoning_patterns = patterns
            return patterns
            
        except Exception as e:
            self.logger.error(f"Failed to analyze reasoning patterns: {e}")
            return []
    
    def detect_critical_events(self) -> List[Dict[str, Any]]:
        """Detect critical events and patterns"""
        critical_events = []
        
        try:
            # Check for stress patterns
            stress_patterns = [p for p in self.consciousness_patterns if p.pattern_type == "stressed"]
            if stress_patterns and stress_patterns[0].frequency > self.stress_threshold:
                critical_events.append({
                    "type": "high_stress",
                    "severity": "warning",
                    "message": f"Высокая частота стрессовых состояний: {stress_patterns[0].frequency:.2f}/час",
                    "recommendation": "Рекомендуется снизить нагрузку и увеличить время отдыха"
                })
            
            # Check for fatigue patterns
            fatigue_indicators = [p for p in self.consciousness_patterns if p.attention_level_avg < 0.3]
            if fatigue_indicators:
                critical_events.append({
                    "type": "fatigue",
                    "severity": "warning",
                    "message": "Обнаружены признаки усталости: низкий уровень внимания",
                    "recommendation": "Рекомендуется перерыв и восстановление"
                })
            
            # Check for evolution patterns
            evolution_patterns = [p for p in self.consciousness_patterns if p.pattern_type == "evolving"]
            if evolution_patterns and evolution_patterns[0].frequency > self.evolution_threshold:
                critical_events.append({
                    "type": "evolution_surge",
                    "severity": "info",
                    "message": f"Активная эволюция: {evolution_patterns[0].frequency:.2f}/час",
                    "recommendation": "Система активно самоулучшается"
                })
            
            # Check for emotional spikes
            for emotional_pattern in self.emotional_patterns:
                if emotional_pattern.intensity > 0.8:
                    critical_events.append({
                        "type": "emotional_spike",
                        "severity": "warning",
                        "message": f"Эмоциональный всплеск: {emotional_pattern.emotion} (интенсивность: {emotional_pattern.intensity:.2f})",
                        "recommendation": "Мониторинг эмоционального состояния"
                    })
            
        except Exception as e:
            self.logger.error(f"Failed to detect critical events: {e}")
        
        return critical_events
    
    def generate_meta_report(self) -> Dict[str, Any]:
        """Generate comprehensive meta-analysis report"""
        try:
            current_time = time.time()
            
            # Only analyze if enough time has passed
            if current_time - self.last_analysis < self.analysis_interval:
                return self.recent_analysis
            
            # Perform analysis
            consciousness_patterns = self.analyze_consciousness_patterns()
            emotional_patterns = self.analyze_emotional_patterns()
            reasoning_patterns = self.analyze_reasoning_patterns()
            critical_events = self.detect_critical_events()
            
            # Generate insights
            insights = self._generate_insights(consciousness_patterns, emotional_patterns, reasoning_patterns)
            
            # Create report
            report = {
                "timestamp": datetime.now().isoformat(),
                "analysis_period_hours": 24,
                "consciousness_patterns": [asdict(p) for p in consciousness_patterns],
                "emotional_patterns": [asdict(p) for p in emotional_patterns],
                "reasoning_patterns": [asdict(p) for p in reasoning_patterns],
                "critical_events": critical_events,
                "insights": insights,
                "recommendations": self._generate_recommendations(consciousness_patterns, emotional_patterns, reasoning_patterns)
            }
            
            # Store in history
            self.pattern_history.append(report)
            if len(self.pattern_history) > 100:  # Keep last 100 reports
                self.pattern_history = self.pattern_history[-100:]
            
            self.recent_analysis = report
            self.last_analysis = current_time
            
            self.logger.info("Generated meta-analysis report")
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to generate meta report: {e}")
            return {}
    
    def _calculate_duration(self, memories: List) -> float:
        """Calculate average duration of pattern"""
        if len(memories) < 2:
            return 0.0
        
        timestamps = sorted([m.timestamp for m in memories])
        intervals = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
        return sum(intervals) / len(intervals) if intervals else 0.0
    
    def _calculate_intensity(self, memories: List) -> float:
        """Calculate average intensity of pattern"""
        if not memories:
            return 0.0
        
        # Use attention level as intensity proxy
        return sum(m.attention_level for m in memories) / len(memories)
    
    def _find_triggers(self, memories: List) -> List[str]:
        """Find common triggers for pattern"""
        triggers = []
        
        for memory in memories:
            content = memory.content
            if isinstance(content, dict):
                # Look for trigger indicators in content
                if "trigger" in content:
                    triggers.append(str(content["trigger"]))
                elif "cause" in content:
                    triggers.append(str(content["cause"]))
        
        # Return most common triggers
        trigger_counts = Counter(triggers)
        return [trigger for trigger, count in trigger_counts.most_common(5)]
    
    def _find_consequences(self, memories: List) -> List[str]:
        """Find common consequences of pattern"""
        consequences = []
        
        for memory in memories:
            content = memory.content
            if isinstance(content, dict):
                # Look for consequence indicators in content
                if "consequence" in content:
                    consequences.append(str(content["consequence"]))
                elif "result" in content:
                    consequences.append(str(content["result"]))
        
        # Return most common consequences
        consequence_counts = Counter(consequences)
        return [consequence for consequence, count in consequence_counts.most_common(5)]
    
    def _calculate_emotional_correlation(self, memories: List) -> Dict[str, float]:
        """Calculate correlation with emotions"""
        correlations = defaultdict(list)
        
        for memory in memories:
            for emotion, intensity in memory.emotional_trace.items():
                correlations[emotion].append(intensity)
        
        # Calculate average intensity for each emotion
        return {emotion: sum(intensities)/len(intensities) 
                for emotion, intensities in correlations.items()}
    
    def _find_emotional_transitions(self, memories: List) -> Dict[str, float]:
        """Find emotional state transitions"""
        transitions = defaultdict(int)
        total_transitions = 0
        
        for i in range(len(memories) - 1):
            current_emotions = memories[i].emotional_trace
            next_emotions = memories[i + 1].emotional_trace
            
            if current_emotions and next_emotions:
                current_primary = max(current_emotions.items(), key=lambda x: x[1])[0]
                next_primary = max(next_emotions.items(), key=lambda x: x[1])[0]
                
                if current_primary != next_primary:
                    transition_key = f"{current_primary}->{next_primary}"
                    transitions[transition_key] += 1
                    total_transitions += 1
        
        # Convert to probabilities
        if total_transitions > 0:
            return {transition: count/total_transitions 
                    for transition, count in transitions.items()}
        return {}
    
    def _calculate_consciousness_correlation(self, memories: List) -> Dict[str, float]:
        """Calculate correlation with consciousness states"""
        correlations = defaultdict(list)
        
        for memory in memories:
            state = memory.consciousness_state
            # Use attention level as correlation strength
            correlations[state].append(memory.attention_level)
        
        # Calculate average attention for each state
        return {state: sum(levels)/len(levels) 
                for state, levels in correlations.items()}
    
    def _categorize_reasoning_depth(self, depth: int) -> str:
        """Categorize reasoning depth"""
        if depth <= 2:
            return "shallow"
        elif depth <= 4:
            return "moderate"
        elif depth <= 6:
            return "deep"
        else:
            return "profound"
    
    def _calculate_success_rate(self, memories: List) -> float:
        """Calculate success rate for reasoning patterns"""
        if not memories:
            return 0.0
        
        # Simple heuristic: higher attention and reasoning depth = more success
        success_indicators = []
        for memory in memories:
            # Combine attention level and reasoning depth as success indicator
            success_score = (memory.attention_level + memory.reasoning_depth / 10) / 2
            success_indicators.append(success_score)
        
        return sum(success_indicators) / len(success_indicators)
    
    def _calculate_emotional_impact(self, memories: List) -> Dict[str, float]:
        """Calculate emotional impact of reasoning patterns"""
        impact = defaultdict(list)
        
        for memory in memories:
            for emotion, intensity in memory.emotional_trace.items():
                impact[emotion].append(intensity)
        
        return {emotion: sum(intensities)/len(intensities) 
                for emotion, intensities in impact.items()}
    
    def _generate_insights(self, consciousness_patterns: List, 
                          emotional_patterns: List, 
                          reasoning_patterns: List) -> List[str]:
        """Generate insights from patterns"""
        insights = []
        
        # Consciousness insights
        if consciousness_patterns:
            most_frequent = max(consciousness_patterns, key=lambda p: p.frequency)
            insights.append(f"Наиболее частое состояние сознания: {most_frequent.pattern_type} ({most_frequent.frequency:.2f}/час)")
        
        # Emotional insights
        if emotional_patterns:
            most_intense = max(emotional_patterns, key=lambda p: p.intensity)
            insights.append(f"Наиболее интенсивная эмоция: {most_intense.emotion} (интенсивность: {most_intense.intensity:.2f})")
        
        # Reasoning insights
        if reasoning_patterns:
            most_successful = max(reasoning_patterns, key=lambda p: p.success_rate)
            insights.append(f"Наиболее успешный тип рассуждений: {most_successful.reasoning_type} (успех: {most_successful.success_rate:.2f})")
        
        return insights
    
    def _generate_recommendations(self, consciousness_patterns: List,
                                emotional_patterns: List,
                                reasoning_patterns: List) -> List[str]:
        """Generate recommendations based on patterns"""
        recommendations = []
        
        # Check for stress
        stress_patterns = [p for p in consciousness_patterns if p.pattern_type == "stressed"]
        if stress_patterns and stress_patterns[0].frequency > 0.5:
            recommendations.append("Рекомендуется снизить когнитивную нагрузку")
        
        # Check for low attention
        low_attention_patterns = [p for p in consciousness_patterns if p.attention_level_avg < 0.4]
        if low_attention_patterns:
            recommendations.append("Рекомендуется увеличить время отдыха и восстановления")
        
        # Check for evolution opportunities
        evolution_patterns = [p for p in consciousness_patterns if p.pattern_type == "evolving"]
        if evolution_patterns and evolution_patterns[0].frequency < 0.2:
            recommendations.append("Рекомендуется активировать режим самоулучшения")
        
        return recommendations


# Global meta observer instance
meta_observer = MetaObserver() 