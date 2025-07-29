#!/usr/bin/env python3
"""
OpenRGB Controller with API support
Controls RGB devices via OpenRGB API and system LEDs
"""

import logging
import time
import subprocess
import threading
import math
from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path
import json

try:
    from openrgb import OpenRGBClient
    from openrgb.utils import RGBColor
    OPENRGB_AVAILABLE = True
except ImportError:
    OPENRGB_AVAILABLE = False
    print("OpenRGB Python library not available, using system LEDs only")

from .sysfs_rgb_controller import SysfsLEDController


class OpenRGBController:
    """Advanced RGB Controller with OpenRGB API support"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.openrgb_client = None
        self.sysfs_controller = SysfsLEDController()
        self.current_color = "blue"
        self.current_intensity = 0.3
        self.animation_thread = None
        self.animation_running = False
        
        # Цветовая схема состояний
        self.color_scheme = {
            "normal": {"color": "blue", "intensity": 0.3},
            "excited": {"color": "yellow", "intensity": 0.8},
            "stressed": {"color": "orange", "intensity": 0.7},
            "evolving": {"color": "purple", "intensity": 0.8},
            "creative": {"color": "purple", "intensity": 0.8},
            "concerned": {"color": "orange", "intensity": 0.7},
            "calm": {"color": "blue", "intensity": 0.3},
            "learning": {"color": "green", "intensity": 0.6},
            "critical": {"color": "red", "intensity": 1.0}
        }
        
        self._init_openrgb()
        
    def _init_openrgb(self):
        """Initialize OpenRGB client"""
        if not OPENRGB_AVAILABLE:
            self.logger.warning("OpenRGB Python library not available")
            return
            
        try:
            # Попробуем подключиться к OpenRGB серверу
            self.openrgb_client = OpenRGBClient()
            self.logger.info("OpenRGB client initialized successfully")
            
            # Получим список устройств
            devices = self.openrgb_client.get_devices()
            self.logger.info(f"Found {len(devices)} OpenRGB devices")
            
            for device in devices:
                self.logger.info(f"Device: {device.name} ({device.type})")
                
        except Exception as e:
            self.logger.warning(f"Failed to connect to OpenRGB server: {e}")
            self.logger.info("Falling back to system LED control")
            self.openrgb_client = None
    
    def set_color(self, color: str, intensity: float = 1.0):
        """Set RGB color across all available devices"""
        self.current_color = color
        self.current_intensity = intensity
        
        try:
            # Попробуем OpenRGB API
            if self.openrgb_client:
                self._set_openrgb_color(color, intensity)
            
            # Всегда используем системные LED как fallback
            self._set_sysfs_color(color, intensity)
            
            self.logger.info(f"RGB set to {color} with intensity {intensity}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set RGB color: {e}")
            return False
    
    def _set_openrgb_color(self, color: str, intensity: float):
        """Set color via OpenRGB API"""
        if not self.openrgb_client:
            return
            
        try:
            rgb_color = self._color_name_to_rgb(color)
            # Применяем интенсивность
            rgb_color = tuple(int(c * intensity) for c in rgb_color)
            
            devices = self.openrgb_client.get_devices()
            for device in devices:
                try:
                    # Устанавливаем цвет для всего устройства
                    device.set_color(RGBColor(*rgb_color))
                    self.logger.debug(f"Set {device.name} to {color}")
                except Exception as e:
                    self.logger.warning(f"Failed to set color for {device.name}: {e}")
                    
        except Exception as e:
            self.logger.error(f"OpenRGB color setting failed: {e}")
    
    def _set_sysfs_color(self, color: str, intensity: float):
        """Set color via sysfs LED control"""
        try:
            self.sysfs_controller.set_color(color, intensity)
        except Exception as e:
            self.logger.error(f"Sysfs color setting failed: {e}")
    
    def _color_name_to_rgb(self, color_name: str) -> Tuple[int, int, int]:
        """Convert color name to RGB values"""
        color_map = {
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "blue": (0, 0, 255),
            "yellow": (255, 255, 0),
            "orange": (255, 165, 0),
            "purple": (128, 0, 128),
            "pink": (255, 192, 203),
            "cyan": (0, 255, 255),
            "white": (255, 255, 255),
            "off": (0, 0, 0),
            "black": (0, 0, 0)
        }
        return color_map.get(color_name.lower(), (0, 0, 255))
    
    def set_state(self, consciousness_state: str, emotion_state: str):
        """Set RGB based on consciousness and emotion states"""
        # Определяем цвет на основе состояний
        if consciousness_state == "excited" or emotion_state == "excited":
            color_info = self.color_scheme["excited"]
        elif consciousness_state == "stressed" or emotion_state == "concerned":
            color_info = self.color_scheme["stressed"]
        elif consciousness_state == "evolving" or emotion_state == "creative":
            color_info = self.color_scheme["evolving"]
        elif consciousness_state == "normal" or emotion_state == "calm":
            color_info = self.color_scheme["normal"]
        else:
            color_info = self.color_scheme["normal"]
        
        return self.set_color(color_info["color"], color_info["intensity"])
    
    def start_animation(self, animation_type: str = "pulse"):
        """Start RGB animation"""
        if self.animation_running:
            self.stop_animation()
            
        self.animation_running = True
        self.animation_thread = threading.Thread(
            target=self._animation_loop,
            args=(animation_type,),
            daemon=True
        )
        self.animation_thread.start()
        self.logger.info(f"Started {animation_type} animation")
    
    def stop_animation(self):
        """Stop RGB animation"""
        self.animation_running = False
        if self.animation_thread:
            self.animation_thread.join(timeout=1)
        self.logger.info("Animation stopped")
    
    def _animation_loop(self, animation_type: str):
        """Animation loop"""
        if animation_type == "pulse":
            self._pulse_animation()
        elif animation_type == "breathing":
            self._breathing_animation()
        elif animation_type == "rainbow":
            self._rainbow_animation()
    
    def _pulse_animation(self):
        """Pulse animation"""
        while self.animation_running:
            for intensity in [0.1, 0.3, 0.5, 0.7, 0.9, 0.7, 0.5, 0.3, 0.1]:
                if not self.animation_running:
                    break
                self.set_color(self.current_color, intensity)
                time.sleep(0.1)
    
    def _breathing_animation(self):
        """Breathing animation"""
        while self.animation_running:
            for i in range(0, 100, 2):
                if not self.animation_running:
                    break
                intensity = 0.1 + (0.8 * (1 + math.sin(i * 0.1)) / 2)
                self.set_color(self.current_color, intensity)
                time.sleep(0.05)
    
    def _rainbow_animation(self):
        """Rainbow animation"""
        colors = ["red", "orange", "yellow", "green", "blue", "purple"]
        while self.animation_running:
            for color in colors:
                if not self.animation_running:
                    break
                self.set_color(color, 0.8)
                time.sleep(0.5)
    
    def get_status(self) -> Dict[str, Any]:
        """Get RGB status"""
        status = {
            "current_color": self.current_color,
            "current_intensity": self.current_intensity,
            "animation_running": self.animation_running,
            "openrgb_available": self.openrgb_client is not None,
            "sysfs_leds": len(self.sysfs_controller.available_leds)
        }
        
        if self.openrgb_client:
            try:
                devices = self.openrgb_client.get_devices()
                status["openrgb_devices"] = len(devices)
                status["device_names"] = [d.name for d in devices]
            except:
                status["openrgb_devices"] = 0
                status["device_names"] = []
        
        return status
    
    def test_all_colors(self):
        """Test all available colors"""
        colors = ["red", "green", "blue", "yellow", "orange", "purple", "white"]
        for color in colors:
            self.logger.info(f"Testing color: {color}")
            self.set_color(color, 0.5)
            time.sleep(1)
        
        # Вернемся к нормальному состоянию
        self.set_color("blue", 0.3) 