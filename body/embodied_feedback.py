#!/usr/bin/env python3
"""
Embodied Feedback System
Provides visual and physical feedback for consciousness states
"""

import time
import logging
import threading
from enum import Enum
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

from body.sensors import Sensorium
from body.hardware_controller import hardware_controller
from body.openrgb_controller import OpenRGBController


class ConsciousnessState(Enum):
    """States of consciousness"""
    NORMAL = "normal"
    EXCITED = "excited"
    FOCUSED = "focused"
    STRESSED = "stressed"
    ERROR = "error"
    EVOLVING = "evolving"
    REFLECTING = "reflecting"
    LEARNING = "learning"


class EmotionState(Enum):
    """Emotional states"""
    CALM = "calm"
    EXCITED = "excited"
    LEARNING = "learning"
    CONCERNED = "concerned"
    FRUSTRATED = "frustrated"
    CREATIVE = "creative"
    CURIOUS = "curious"
    SATISFIED = "satisfied"


@dataclass
class VisualFeedback:
    """Visual feedback data"""
    emoji: str
    state: str
    emotion: str
    color: str
    intensity: float


class PhysicalMonitor:
    """Monitor physical system metrics"""
    
    def __init__(self):
        self.sensorium = Sensorium()
        self.logger = logging.getLogger(__name__)
    
    def get_physical_metrics(self):
        """Get current physical metrics"""
        try:
            metrics = self.sensorium.get_system_metrics()
            return metrics
        except Exception as e:
            self.logger.error(f"Failed to get physical metrics: {e}")
            return None


class RGBController:
    """Control RGB indicators using OpenRGB and sysfs"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.openrgb_controller = OpenRGBController()
        self.current_color = "blue"
        self.current_intensity = 0.3
    
    def set_color(self, color: str, intensity: float = 1.0):
        """Set RGB color"""
        try:
            success = self.openrgb_controller.set_color(color, intensity)
            if success:
                self.current_color = color
                self.current_intensity = intensity
                self.logger.info(f"RGB set to {color} with intensity {intensity}")
            return success
        except Exception as e:
            self.logger.error(f"Failed to set RGB color: {e}")
            return False
            
    def set_death_sequence(self):
        """Последовательность смерти - красный пульс и затухание"""
        try:
            self.logger.info("🔄 Начинаю последовательность смерти...")
            
            # Красный пульс
            for i in range(5):
                self.set_color("red", 1.0)
                time.sleep(0.5)
                self.set_color("red", 0.3)
                time.sleep(0.5)
            
            # Затухание
            for intensity in range(100, 0, -10):
                self.set_color("red", intensity / 100)
                time.sleep(0.1)
            
            # Полное выключение
            self.set_color("black", 0.0)
            
            self.logger.info("💀 Последовательность смерти завершена")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка в последовательности смерти: {e}")
    
    def set_state(self, consciousness_state: str, emotion_state: str):
        """Set RGB based on consciousness and emotion states"""
        return self.openrgb_controller.set_state(consciousness_state, emotion_state)
    
    def start_animation(self, animation_type: str = "pulse"):
        """Start RGB animation"""
        return self.openrgb_controller.start_animation(animation_type)
    
    def stop_animation(self):
        """Stop RGB animation"""
        return self.openrgb_controller.stop_animation()
    
    def get_status(self) -> Dict[str, Any]:
        """Get RGB status"""
        status = self.openrgb_controller.get_status()
        status.update({
            "color": self.current_color,
            "intensity": self.current_intensity,
            "available": True
        })
        return status
    
    def _color_name_to_rgb(self, color_name: str) -> Tuple[int, int, int]:
        """Convert color name to RGB values"""
        return self.openrgb_controller._color_name_to_rgb(color_name)


class EmbodiedFeedbackSystem:
    """Main embodied feedback system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.physical_monitor = PhysicalMonitor()
        self.rgb_controller = RGBController()
        
        # Current state
        self.consciousness_state = ConsciousnessState.NORMAL
        self.emotion_state = EmotionState.CALM
        
        # Monitoring thread
        self._monitoring = False
        self._monitor_thread = None
        
        # State mappings
        self.state_mappings = {
            (ConsciousnessState.NORMAL, EmotionState.CALM): VisualFeedback("😐", "normal", "calm", "blue", 0.3),
            (ConsciousnessState.EXCITED, EmotionState.EXCITED): VisualFeedback("😊", "excited", "excited", "yellow", 0.8),
            (ConsciousnessState.FOCUSED, EmotionState.LEARNING): VisualFeedback("🤔", "focused", "learning", "green", 0.6),
            (ConsciousnessState.STRESSED, EmotionState.CONCERNED): VisualFeedback("😟", "stressed", "concerned", "orange", 0.7),
            (ConsciousnessState.ERROR, EmotionState.FRUSTRATED): VisualFeedback("😤", "error", "frustrated", "red", 0.9),
            (ConsciousnessState.EVOLVING, EmotionState.CREATIVE): VisualFeedback("🤖", "evolving", "creative", "purple", 0.8),
            (ConsciousnessState.REFLECTING, EmotionState.CURIOUS): VisualFeedback("🧠", "reflecting", "curious", "cyan", 0.5),
            (ConsciousnessState.LEARNING, EmotionState.SATISFIED): VisualFeedback("📚", "learning", "satisfied", "green", 0.4),
        }
    
    def start_monitoring(self):
        """Start monitoring thread"""
        if self._monitoring:
            return
        
        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        self.logger.info("Embodied feedback monitoring started")
    
    def stop_monitoring(self):
        """Stop monitoring thread"""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1)
        self.logger.info("Embodied feedback monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self._monitoring:
            try:
                # Update physical feedback only if needed
                # self._update_physical_feedback()  # Temporarily disabled to prevent color override
                time.sleep(1)
            except Exception as e:
                self.logger.error(f"Error in monitor loop: {e}")
                time.sleep(5)
    
    def _update_physical_feedback(self):
        """Update physical feedback based on current state"""
        feedback = self.get_visual_feedback()
        
        # Update RGB only if color changed
        current_rgb = self.rgb_controller.get_status().get("current_colors", {}).get("all", [0, 0, 0])
        
        # Simple color mapping for comparison
        color_map = {
            "red": [255, 0, 0],
            "green": [0, 255, 0],
            "blue": [0, 0, 255],
            "yellow": [255, 255, 0],
            "purple": [128, 0, 128],
            "cyan": [0, 255, 255],
            "orange": [255, 165, 0],
            "pink": [255, 192, 203],
            "white": [255, 255, 255],
            "off": [0, 0, 0],
            "black": [0, 0, 0]
        }
        target_rgb = color_map.get(feedback.color.lower(), [0, 0, 0])
        
        if current_rgb != target_rgb:
            self.rgb_controller.set_color(feedback.color, feedback.intensity)
    
    def set_consciousness_state(self, consciousness: ConsciousnessState, emotion: EmotionState):
        """Set current consciousness and emotion state"""
        self.consciousness_state = consciousness
        self.emotion_state = emotion
        self.logger.info(f"State set to {consciousness.value} with emotion {emotion.value}")
        
        # Use new RGB controller with state-based color setting
        self.rgb_controller.set_state(consciousness.value, emotion.value)
    
    def get_visual_feedback(self) -> VisualFeedback:
        """Get current visual feedback"""
        key = (self.consciousness_state, self.emotion_state)
        if key in self.state_mappings:
            return self.state_mappings[key]
        
        # Default feedback
        return VisualFeedback("❓", "unknown", "unknown", "white", 0.5)
    
    def get_feedback_summary(self) -> Dict[str, Any]:
        """Get complete feedback summary"""
        visual = self.get_visual_feedback()
        physical = self.physical_monitor.get_physical_metrics()
        rgb = self.rgb_controller.get_status()
        
        return {
            "status": "active",
            "consciousness_state": self.consciousness_state.value,
            "emotion_state": self.emotion_state.value,
            "visual_feedback": {
                "emoji": visual.emoji,
                "state": visual.state,
                "emotion": visual.emotion,
                "color": visual.color,
                "intensity": visual.intensity
            },
            "physical_metrics": physical.__dict__ if physical else None,
            "rgb_status": rgb
        }


# Global instance
embodied_feedback = EmbodiedFeedbackSystem() 