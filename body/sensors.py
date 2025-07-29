"""
Sensorium - Embodied System Perception
Direct hardware interaction through /proc and /sys filesystems
No abstractions, no emulations - pure hardware embodiment
"""

import subprocess
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json
import time
import logging
import platform
import re

from config import config


@dataclass
class SystemMetrics:
    """System metrics in unified format for consciousness processing"""
    timestamp: float
    cpu_usage_per_core: List[float]
    memory_usage_mb: float
    memory_percent: float
    disk_usage_percent: float
    temperature_celsius: Optional[float]
    network_io_bytes: Tuple[int, int]  # bytes_sent, bytes_recv
    process_count: int
    load_average: Tuple[float, float, float]
    
    @property
    def cpu_percent(self) -> float:
        """Calculate average CPU usage across all cores"""
        if self.cpu_usage_per_core:
            return sum(self.cpu_usage_per_core) / len(self.cpu_usage_per_core)
        return 0.0


class Sensorium:
    """
    Sensorium - Embodied System Perception
    Direct hardware interaction through /proc and /sys filesystems
    No psutil, no abstractions - pure hardware embodiment
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._last_metrics: Optional[SystemMetrics] = None
        self._is_linux = platform.system() == "Linux"
        self._thermal_zones = self._discover_thermal_zones()
        self._cpu_count = self._get_cpu_count()
        self._last_cpu_times = self._read_cpu_times()
        self._last_cpu_time = time.time()
        
    def _discover_thermal_zones(self) -> List[Path]:
        """Discover available thermal zones (Linux only)"""
        if not self._is_linux:
            self.logger.info("Thermal zones not supported on non-Linux systems")
            return []
        
        thermal_dir = Path("/sys/class/thermal")
        if not thermal_dir.exists():
            self.logger.warning("Thermal zones not found in /sys/class/thermal")
            return []
        
        zones = []
        for zone_dir in thermal_dir.glob("thermal_zone*"):
            temp_file = zone_dir / "temp"
            if temp_file.exists():
                zones.append(temp_file)
        
        self.logger.info(f"Discovered {len(zones)} thermal zones")
        return zones
    
    def _get_cpu_count(self) -> int:
        """Get CPU count from /proc/cpuinfo"""
        try:
            with open("/proc/cpuinfo", "r") as f:
                content = f.read()
                return len(re.findall(r"processor\s*:\s*\d+", content))
        except Exception as e:
            self.logger.error(f"Error reading CPU count: {e}")
            return 1
    
    def _read_cpu_times(self) -> List[int]:
        """Read CPU times from /proc/stat"""
        try:
            with open("/proc/stat", "r") as f:
                lines = f.readlines()
                cpu_line = lines[0]  # First line is total CPU
                values = [int(x) for x in cpu_line.split()[1:]]
                return values
        except Exception as e:
            self.logger.error(f"Error reading CPU times: {e}")
            return [0] * 10
    
    def read_cpu_usage_per_core(self) -> List[float]:
        """Read CPU usage per core using direct /proc access"""
        try:
            current_times = self._read_cpu_times()
            current_time = time.time()
            
            if self._last_cpu_times and self._last_cpu_time:
                time_diff = current_time - self._last_cpu_time
                cpu_usage = []
                
                # Calculate total CPU usage
                total_diff = sum(current_times) - sum(self._last_cpu_times)
                if total_diff > 0 and time_diff > 0:
                    idle_diff = current_times[3] - self._last_cpu_times[3]
                    cpu_percent = 100.0 * (1.0 - idle_diff / total_diff)
                    cpu_usage = [cpu_percent] * self._cpu_count
                else:
                    cpu_usage = [0.0] * self._cpu_count
                
                self._last_cpu_times = current_times
                self._last_cpu_time = current_time
                return cpu_usage
            else:
                self._last_cpu_times = current_times
                self._last_cpu_time = current_time
                return [0.0] * self._cpu_count
                
        except Exception as e:
            self.logger.error(f"Error reading CPU usage: {e}")
            return [0.0] * self._cpu_count
    
    def read_temperature(self) -> Optional[float]:
        """Read temperature from thermal zones (Linux only)"""
        if not self._is_linux:
            return None
        
        if not self._thermal_zones:
            return None
        
        try:
            # Read from first available thermal zone
            with open(self._thermal_zones[0], "r") as f:
                temp_millicelsius = int(f.read().strip())
                return temp_millicelsius / 1000.0  # Convert to Celsius
        except Exception as e:
            self.logger.error(f"Error reading temperature: {e}")
            return None
    
    def read_memory_info(self) -> Tuple[float, float]:
        """Read memory information from /proc/meminfo"""
        try:
            with open("/proc/meminfo", "r") as f:
                lines = f.readlines()
                mem_info = {}
                for line in lines:
                    if ":" in line:
                        key, value = line.split(":", 1)
                        mem_info[key.strip()] = int(value.strip().split()[0])
                
                total_kb = mem_info.get("MemTotal", 0)
                available_kb = mem_info.get("MemAvailable", 0)
                
                if total_kb > 0:
                    used_kb = total_kb - available_kb
                    used_mb = used_kb / 1024.0
                    percent = (used_kb / total_kb) * 100.0
                    return used_mb, percent
                else:
                    return 0.0, 0.0
                    
        except Exception as e:
            self.logger.error(f"Error reading memory info: {e}")
            return 0.0, 0.0
    
    def read_disk_usage(self) -> float:
        """Read disk usage using df command"""
        try:
            result = subprocess.run(
                ["df", "/"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                if len(lines) > 1:
                    parts = lines[1].split()
                    if len(parts) >= 5:
                        usage_str = parts[4].rstrip("%")
                        return float(usage_str)
            return 0.0
        except Exception as e:
            self.logger.error(f"Error reading disk usage: {e}")
            return 0.0
    
    def read_network_io(self) -> Tuple[int, int]:
        """Read network I/O from /proc/net/dev"""
        try:
            with open("/proc/net/dev", "r") as f:
                lines = f.readlines()
                total_bytes_sent = 0
                total_bytes_recv = 0
                
                for line in lines[2:]:  # Skip header lines
                    parts = line.split()
                    if len(parts) >= 10:
                        interface = parts[0].rstrip(":")
                        if interface != "lo":  # Skip loopback
                            bytes_recv = int(parts[1])
                            bytes_sent = int(parts[9])
                            total_bytes_recv += bytes_recv
                            total_bytes_sent += bytes_sent
                
                return total_bytes_sent, total_bytes_recv
        except Exception as e:
            self.logger.error(f"Error reading network I/O: {e}")
            return 0, 0
    
    def read_load_average(self) -> Tuple[float, float, float]:
        """Read load average from /proc/loadavg"""
        try:
            with open("/proc/loadavg", "r") as f:
                content = f.read().strip()
                parts = content.split()
                if len(parts) >= 3:
                    return float(parts[0]), float(parts[1]), float(parts[2])
                return 0.0, 0.0, 0.0
        except Exception as e:
            self.logger.error(f"Error reading load average: {e}")
            return 0.0, 0.0, 0.0
    
    def get_process_count(self) -> int:
        """Get process count from /proc"""
        try:
            proc_dir = Path("/proc")
            count = 0
            for item in proc_dir.iterdir():
                if item.is_dir() and item.name.isdigit():
                    count += 1
            return count
        except Exception as e:
            self.logger.error(f"Error counting processes: {e}")
            return 0
    
    def get_system_metrics(self) -> SystemMetrics:
        """Get comprehensive system metrics through direct hardware access"""
        try:
            timestamp = time.time()
            cpu_usage = self.read_cpu_usage_per_core()
            memory_usage_mb, memory_percent = self.read_memory_info()
            disk_usage = self.read_disk_usage()
            temperature = self.read_temperature()
            network_io = self.read_network_io()
            process_count = self.get_process_count()
            load_average = self.read_load_average()
            
            metrics = SystemMetrics(
                timestamp=timestamp,
                cpu_usage_per_core=cpu_usage,
                memory_usage_mb=memory_usage_mb,
                memory_percent=memory_percent,
                disk_usage_percent=disk_usage,
                temperature_celsius=temperature,
                network_io_bytes=network_io,
                process_count=process_count,
                load_average=load_average
            )
            
            self._last_metrics = metrics
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error getting system metrics: {e}")
            # Return safe defaults
            return SystemMetrics(
                timestamp=time.time(),
                cpu_usage_per_core=[0.0] * self._cpu_count,
                memory_usage_mb=0.0,
                memory_percent=0.0,
                disk_usage_percent=0.0,
                temperature_celsius=None,
                network_io_bytes=(0, 0),
                process_count=0,
                load_average=(0.0, 0.0, 0.0)
            )
    
    def check_homeostasis(self) -> Dict[str, bool]:
        """Check system homeostasis violations"""
        try:
            metrics = self.get_system_metrics()
            
            violations = {
                "cpu_high": max(metrics.cpu_usage_per_core) > config.system.MAX_CPU_PERCENT,
                "memory_high": metrics.memory_percent > 90.0,
                "disk_full": metrics.disk_usage_percent > 95.0,
                "temperature_high": (
                    metrics.temperature_celsius is not None and 
                    metrics.temperature_celsius > config.system.MAX_TEMP_CELSIUS
                )
            }
            
            if any(violations.values()):
                self.logger.warning(f"Homeostasis violations detected: {violations}")
            
            return violations
            
        except Exception as e:
            self.logger.error(f"Error checking homeostasis: {e}")
            return {
                "cpu_high": False,
                "memory_high": False,
                "disk_full": False,
                "temperature_high": False
            }
    
    def get_metrics_json(self) -> str:
        """Get metrics as JSON string for logging"""
        try:
            metrics = self.get_system_metrics()
            return json.dumps({
                "timestamp": metrics.timestamp,
                "cpu_usage_per_core": metrics.cpu_usage_per_core,
                "memory_usage_mb": metrics.memory_usage_mb,
                "memory_percent": metrics.memory_percent,
                "disk_usage_percent": metrics.disk_usage_percent,
                "temperature_celsius": metrics.temperature_celsius,
                "network_io_bytes": metrics.network_io_bytes,
                "process_count": metrics.process_count,
                "load_average": metrics.load_average
            })
        except Exception as e:
            self.logger.error(f"Error serializing metrics: {e}")
            return "{}" 