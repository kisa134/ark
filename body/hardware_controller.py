#!/usr/bin/env python3
"""
ARK v2.8 - Hardware Controller
Auto-detection and control of RGB devices and hardware feedback
"""

import logging
import time
import subprocess
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

try:
    import psutil
except ImportError:
    psutil = None

try:
    import usb.core
    import usb.util
except ImportError:
    usb = None


class HardwareType(Enum):
    """Types of hardware devices"""
    RGB_STRIP = "rgb_strip"
    RGB_FAN = "rgb_fan"
    RGB_MOTHERBOARD = "rgb_motherboard"
    RGB_GPU = "rgb_gpu"
    RGB_RAM = "rgb_ram"
    RGB_CASE = "rgb_case"
    LED_INDICATOR = "led_indicator"


@dataclass
class HardwareDevice:
    """Hardware device information"""
    device_id: str
    device_type: HardwareType
    name: str
    vendor: str
    product: str
    capabilities: List[str]
    is_available: bool
    connection_type: str
    max_brightness: int
    color_modes: List[str]


class RGBController:
    """Advanced RGB controller with auto-detection"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.devices: List[HardwareDevice] = []
        self.current_colors: Dict[str, Tuple[int, int, int]] = {}
        self.current_brightness: Dict[str, int] = {}
        
        # Auto-detect hardware
        self._detect_hardware()
        
        self.logger.info(f"RGB Controller initialized with {len(self.devices)} devices")
    
    def _detect_hardware(self):
        """Auto-detect available RGB hardware"""
        try:
            # Check for OpenRGB
            if self._check_openrgb():
                self._detect_openrgb_devices()
            
            # Check for USB RGB devices
            if usb:
                self._detect_usb_devices()
            
            # Check for system LEDs
            self._detect_system_leds()
            
            # Check for GPU RGB
            self._detect_gpu_rgb()
            
            # Check for motherboard RGB
            self._detect_motherboard_rgb()
            
        except Exception as e:
            self.logger.error(f"Hardware detection failed: {e}")
    
    def _check_openrgb(self) -> bool:
        """Check if OpenRGB is available"""
        try:
            result = subprocess.run(["openrgb", "--version"], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _detect_openrgb_devices(self):
        """Detect devices through OpenRGB"""
        try:
            result = subprocess.run(["openrgb", "--list"], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.strip():
                        # Parse OpenRGB device output
                        parts = line.split()
                        if len(parts) >= 2:
                            device_id = parts[0]
                            device_name = ' '.join(parts[1:])
                            
                            device = HardwareDevice(
                                device_id=device_id,
                                device_type=self._guess_device_type(device_name),
                                name=device_name,
                                vendor="Unknown",
                                product=device_name,
                                capabilities=["rgb", "brightness"],
                                is_available=True,
                                connection_type="openrgb",
                                max_brightness=100,
                                color_modes=["static", "rainbow", "breathing"]
                            )
                            
                            self.devices.append(device)
                            
        except Exception as e:
            self.logger.error(f"OpenRGB detection failed: {e}")
    
    def _detect_usb_devices(self):
        """Detect USB RGB devices"""
        try:
            if not usb:
                return
            
            # Common RGB device vendors
            rgb_vendors = {
                0x1b1c: "Corsair",
                0x0b05: "ASUS",
                0x1462: "MSI",
                0x1043: "ASUS",
                0x0db0: "Gigabyte"
            }
            
            for device in usb.core.find(find_all=True):
                if device.idVendor in rgb_vendors:
                    try:
                        device_name = f"{rgb_vendors.get(device.idVendor, 'Unknown')} RGB Device"
                        
                        device_info = HardwareDevice(
                            device_id=f"usb_{device.idVendor:04x}_{device.idProduct:04x}",
                            device_type=self._guess_device_type(device_name),
                            name=device_name,
                            vendor=rgb_vendors.get(device.idVendor, "Unknown"),
                            product=f"Product {device.idProduct:04x}",
                            capabilities=["rgb"],
                            is_available=True,
                            connection_type="usb",
                            max_brightness=100,
                            color_modes=["static"]
                        )
                        
                        self.devices.append(device_info)
                        
                    except Exception as e:
                        self.logger.debug(f"Failed to process USB device: {e}")
                        
        except Exception as e:
            self.logger.error(f"USB detection failed: {e}")
    
    def _detect_system_leds(self):
        """Detect system LED indicators"""
        try:
            # Check for common LED paths
            led_paths = [
                "/sys/class/leds",
                "/proc/acpi/ibm/led",
                "/sys/devices/platform/thinkpad_acpi/leds"
            ]
            
            for led_path in led_paths:
                if Path(led_path).exists():
                    for led_dir in Path(led_path).iterdir():
                        if led_dir.is_dir():
                            device = HardwareDevice(
                                device_id=f"led_{led_dir.name}",
                                device_type=HardwareType.LED_INDICATOR,
                                name=f"System LED: {led_dir.name}",
                                vendor="System",
                                product="LED Indicator",
                                capabilities=["brightness"],
                                is_available=True,
                                connection_type="sysfs",
                                max_brightness=1,
                                color_modes=["static"]
                            )
                            
                            self.devices.append(device)
                            
        except Exception as e:
            self.logger.error(f"System LED detection failed: {e}")
    
    def _detect_gpu_rgb(self):
        """Detect GPU RGB capabilities"""
        try:
            # Check for NVIDIA GPU
            if Path("/proc/driver/nvidia").exists():
                device = HardwareDevice(
                    device_id="gpu_nvidia",
                    device_type=HardwareType.RGB_GPU,
                    name="NVIDIA GPU RGB",
                    vendor="NVIDIA",
                    product="GPU RGB",
                    capabilities=["rgb"],
                    is_available=True,
                    connection_type="nvidia",
                    max_brightness=100,
                    color_modes=["static"]
                )
                
                self.devices.append(device)
            
            # Check for AMD GPU
            if Path("/sys/class/drm").exists():
                for gpu_dir in Path("/sys/class/drm").glob("card*"):
                    if gpu_dir.exists():
                        device = HardwareDevice(
                            device_id=f"gpu_amd_{gpu_dir.name}",
                            device_type=HardwareType.RGB_GPU,
                            name=f"AMD GPU RGB: {gpu_dir.name}",
                            vendor="AMD",
                            product="GPU RGB",
                            capabilities=["rgb"],
                            is_available=True,
                            connection_type="amd",
                            max_brightness=100,
                            color_modes=["static"]
                        )
                        
                        self.devices.append(device)
                        
        except Exception as e:
            self.logger.error(f"GPU RGB detection failed: {e}")
    
    def _detect_motherboard_rgb(self):
        """Detect motherboard RGB capabilities"""
        try:
            # Check for common motherboard RGB interfaces
            rgb_paths = [
                "/sys/class/leds/rgb",
                "/sys/devices/platform/rgb",
                "/proc/acpi/ibm/kbd_backlight"
            ]
            
            for rgb_path in rgb_paths:
                if Path(rgb_path).exists():
                    device = HardwareDevice(
                        device_id="motherboard_rgb",
                        device_type=HardwareType.RGB_MOTHERBOARD,
                        name="Motherboard RGB",
                        vendor="System",
                        product="Motherboard RGB",
                        capabilities=["rgb", "brightness"],
                        is_available=True,
                        connection_type="sysfs",
                        max_brightness=100,
                        color_modes=["static", "rainbow"]
                    )
                    
                    self.devices.append(device)
                    break
                    
        except Exception as e:
            self.logger.error(f"Motherboard RGB detection failed: {e}")
    
    def _guess_device_type(self, device_name: str) -> HardwareType:
        """Guess device type from name"""
        name_lower = device_name.lower()
        
        if "fan" in name_lower:
            return HardwareType.RGB_FAN
        elif "gpu" in name_lower or "graphics" in name_lower:
            return HardwareType.RGB_GPU
        elif "ram" in name_lower or "memory" in name_lower:
            return HardwareType.RGB_RAM
        elif "motherboard" in name_lower or "board" in name_lower:
            return HardwareType.RGB_MOTHERBOARD
        elif "case" in name_lower:
            return HardwareType.RGB_CASE
        elif "led" in name_lower:
            return HardwareType.LED_INDICATOR
        else:
            return HardwareType.RGB_STRIP
    
    def set_color(self, color: str, intensity: float = 1.0, device_id: str = None):
        """Set color for RGB devices"""
        try:
            # Convert color name to RGB values
            rgb_values = self._color_name_to_rgb(color)
            brightness = int(intensity * 100)
            
            if device_id:
                # Set color for specific device
                self._set_device_color(device_id, rgb_values, brightness)
            else:
                # Set color for all devices
                for device in self.devices:
                    if device.is_available and "rgb" in device.capabilities:
                        self._set_device_color(device.device_id, rgb_values, brightness)
            
            # Update current state
            self.current_colors[device_id or "all"] = rgb_values
            self.current_brightness[device_id or "all"] = brightness
            
            self.logger.info(f"Set color {color} (RGB: {rgb_values}) with intensity {intensity}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set color: {e}")
            return False
    
    def _set_device_color(self, device_id: str, rgb_values: Tuple[int, int, int], brightness: int):
        """Set color for specific device"""
        try:
            device = next((d for d in self.devices if d.device_id == device_id), None)
            if not device:
                return
            
            if device.connection_type == "openrgb":
                self._set_openrgb_color(device_id, rgb_values, brightness)
            elif device.connection_type == "usb":
                self._set_usb_color(device_id, rgb_values, brightness)
            elif device.connection_type == "sysfs":
                self._set_sysfs_color(device_id, rgb_values, brightness)
            elif device.connection_type == "nvidia":
                self._set_nvidia_color(device_id, rgb_values, brightness)
            elif device.connection_type == "amd":
                self._set_amd_color(device_id, rgb_values, brightness)
                
        except Exception as e:
            self.logger.error(f"Failed to set color for device {device_id}: {e}")
    
    def _set_openrgb_color(self, device_id: str, rgb_values: Tuple[int, int, int], brightness: int):
        """Set color using OpenRGB"""
        try:
            r, g, b = rgb_values
            cmd = [
                "openrgb", "--device", device_id,
                "--mode", "static",
                "--color", f"{r},{g},{b}",
                "--brightness", str(brightness)
            ]
            
            subprocess.run(cmd, timeout=10, check=True)
            
        except Exception as e:
            self.logger.error(f"OpenRGB color setting failed: {e}")
    
    def _set_usb_color(self, device_id: str, rgb_values: Tuple[int, int, int], brightness: int):
        """Set color for USB device (simulated)"""
        # This would require specific USB device drivers
        self.logger.info(f"USB color setting simulated for {device_id}")
    
    def _set_sysfs_color(self, device_id: str, rgb_values: Tuple[int, int, int], brightness: int):
        """Set color using sysfs interface"""
        try:
            r, g, b = rgb_values
            
            # Try to set RGB values
            rgb_path = Path(f"/sys/class/leds/{device_id}/device/color")
            if rgb_path.exists():
                with open(rgb_path, 'w') as f:
                    f.write(f"{r} {g} {b}")
            
            # Try to set brightness
            brightness_path = Path(f"/sys/class/leds/{device_id}/brightness")
            if brightness_path.exists():
                with open(brightness_path, 'w') as f:
                    f.write(str(brightness))
                    
        except Exception as e:
            self.logger.error(f"Sysfs color setting failed: {e}")
    
    def _set_nvidia_color(self, device_id: str, rgb_values: Tuple[int, int, int], brightness: int):
        """Set color for NVIDIA GPU (simulated)"""
        # This would require NVIDIA GPU drivers with RGB support
        self.logger.info(f"NVIDIA color setting simulated for {device_id}")
    
    def _set_amd_color(self, device_id: str, rgb_values: Tuple[int, int, int], brightness: int):
        """Set color for AMD GPU (simulated)"""
        # This would require AMD GPU drivers with RGB support
        self.logger.info(f"AMD color setting simulated for {device_id}")
    
    def _color_name_to_rgb(self, color_name: str) -> Tuple[int, int, int]:
        """Convert color name to RGB values"""
        color_map = {
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "blue": (0, 0, 255),
            "yellow": (255, 255, 0),
            "purple": (128, 0, 128),
            "cyan": (0, 255, 255),
            "orange": (255, 165, 0),
            "pink": (255, 192, 203),
            "white": (255, 255, 255),
            "off": (0, 0, 0),
            "black": (0, 0, 0)
        }
        
        return color_map.get(color_name.lower(), (0, 0, 0))
    
    def get_device_status(self) -> Dict[str, Any]:
        """Get status of all devices"""
        return {
            "total_devices": len(self.devices),
            "available_devices": len([d for d in self.devices if d.is_available]),
            "devices": [
                {
                    "id": device.device_id,
                    "name": device.name,
                    "type": device.device_type.value,
                    "available": device.is_available,
                    "connection": device.connection_type,
                    "capabilities": device.capabilities
                }
                for device in self.devices
            ],
            "current_colors": self.current_colors,
            "current_brightness": self.current_brightness
        }
    
    def get_system_temperature(self) -> float:
        """Get system temperature for thermal management"""
        try:
            if psutil:
                # Get CPU temperature
                temps = psutil.sensors_temperatures()
                if temps:
                    # Get first available temperature
                    for name, entries in temps.items():
                        if entries:
                            return entries[0].current
                
                # Fallback to CPU usage as temperature proxy
                return psutil.cpu_percent(interval=1)
            
            return 0.0
            
        except Exception as e:
            self.logger.error(f"Failed to get system temperature: {e}")
            return 0.0
    
    def set_thermal_mode(self, temperature: float):
        """Set RGB based on thermal conditions"""
        try:
            if temperature > 80:
                # High temperature - red warning
                self.set_color("red", 0.9)
            elif temperature > 70:
                # Medium temperature - orange warning
                self.set_color("orange", 0.7)
            elif temperature > 60:
                # Elevated temperature - yellow warning
                self.set_color("yellow", 0.5)
            else:
                # Normal temperature - blue
                self.set_color("blue", 0.3)
                
        except Exception as e:
            self.logger.error(f"Failed to set thermal mode: {e}")


# Global hardware controller instance
hardware_controller = RGBController() 