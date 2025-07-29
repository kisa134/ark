#!/usr/bin/env python3
"""
Simple LED Controller using sysfs
Controls system LEDs for visual feedback
"""

import os
import logging
import subprocess
from typing import Dict, Any, List, Tuple
from pathlib import Path


class SysfsLEDController:
    """Control system LEDs via sysfs"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.led_path = Path("/sys/class/leds")
        self.available_leds = self._discover_leds()
        self.current_state = {}
        
        self.logger.info(f"Discovered {len(self.available_leds)} system LEDs")
    
    def _discover_leds(self) -> List[str]:
        """Discover available system LEDs"""
        leds = []
        if self.led_path.exists():
            for led_dir in self.led_path.iterdir():
                if led_dir.is_dir():
                    leds.append(led_dir.name)
        return leds
    
    def set_led_state(self, led_name: str, state: bool):
        """Set LED state (on/off)"""
        try:
            led_path = self.led_path / led_name / "brightness"
            if led_path.exists():
                value = "1" if state else "0"
                # Используем прямой вызов tee через shell
                cmd = f"echo '{value}' | sudo tee {led_path}"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    self.current_state[led_name] = state
                    self.logger.info(f"Set LED {led_name} to {'ON' if state else 'OFF'}")
                    return True
                else:
                    self.logger.error(f"Command failed: {result.stderr}")
                    return False
        except Exception as e:
            self.logger.error(f"Failed to set LED {led_name}: {e}")
            return False
    
    def set_all_leds(self, state: bool):
        """Set all LEDs to the same state"""
        success_count = 0
        for led in self.available_leds:
            if self.set_led_state(led, state):
                success_count += 1
        
        self.logger.info(f"Set {success_count}/{len(self.available_leds)} LEDs to {'ON' if state else 'OFF'}")
        return success_count
    
    def blink_led(self, led_name: str, duration: float = 1.0):
        """Blink LED for specified duration"""
        try:
            self.set_led_state(led_name, True)
            import time
            time.sleep(duration)
            self.set_led_state(led_name, False)
            return True
        except Exception as e:
            self.logger.error(f"Failed to blink LED {led_name}: {e}")
            return False
    
    def get_led_status(self) -> Dict[str, Any]:
        """Get current LED status"""
        status = {}
        for led in self.available_leds:
            try:
                brightness_path = self.led_path / led / "brightness"
                if brightness_path.exists():
                    with open(brightness_path, 'r') as f:
                        brightness = int(f.read().strip())
                    status[led] = {
                        "brightness": brightness,
                        "state": brightness > 0
                    }
            except Exception as e:
                self.logger.error(f"Failed to read LED {led}: {e}")
                status[led] = {"brightness": 0, "state": False}
        
        return status
    
    def set_color(self, color: str, intensity: float = 1.0):
        """Set LED color pattern based on color name"""
        color_patterns = {
            "blue": self._normal_pattern,
            "yellow": self._excited_pattern,
            "orange": self._stressed_pattern,
            "purple": self._evolving_pattern,
            "red": self._error_pattern,
            "green": self._normal_pattern,
            "off": self._off_pattern
        }
        
        pattern_func = color_patterns.get(color.lower(), self._normal_pattern)
        pattern_func()
        self.logger.info(f"Set LED pattern to {color} with intensity {intensity}")
        return True
    
    def set_consciousness_pattern(self, state: str):
        """Set LED pattern based on consciousness state"""
        patterns = {
            "normal": self._normal_pattern,
            "excited": self._excited_pattern,
            "stressed": self._stressed_pattern,
            "evolving": self._evolving_pattern,
            "error": self._error_pattern
        }
        
        if state in patterns:
            patterns[state]()
        else:
            self._normal_pattern()
    
    def _normal_pattern(self):
        """Normal state - gentle blue-like pattern"""
        # Use Caps Lock for normal state
        self.set_led_state("input19::capslock", True)
        self.set_led_state("input19::numlock", False)
        self.set_led_state("input19::scrolllock", False)
    
    def _excited_pattern(self):
        """Excited state - bright pattern"""
        # Use multiple LEDs for excited state
        self.set_led_state("input19::capslock", True)
        self.set_led_state("input19::numlock", True)
        self.set_led_state("input19::scrolllock", False)
    
    def _stressed_pattern(self):
        """Stressed state - warning pattern"""
        # Use Scroll Lock for warning
        self.set_led_state("input19::capslock", False)
        self.set_led_state("input19::numlock", False)
        self.set_led_state("input19::scrolllock", True)
    
    def _evolving_pattern(self):
        """Evolving state - creative pattern"""
        # Use multiple LEDs for creative state
        self.set_led_state("input19::capslock", True)
        self.set_led_state("input19::numlock", False)
        self.set_led_state("input19::scrolllock", True)
    
    def _error_pattern(self):
        """Error state - error pattern"""
        # Blink all LEDs for error
        self.set_led_state("input19::capslock", True)
        self.set_led_state("input19::numlock", True)
        self.set_led_state("input19::scrolllock", True)
    
    def _off_pattern(self):
        """Off pattern - all LEDs off"""
        self.set_all_leds(False)


# Global instance
sysfs_led_controller = SysfsLEDController() 