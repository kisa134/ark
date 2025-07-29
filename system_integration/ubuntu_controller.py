#!/usr/bin/env python3
"""
ARK v2.8 - Ubuntu System Integration Controller
Глубокая интеграция с операционной системой Ubuntu
"""

import os
import sys
import subprocess
import psutil
import json
import time
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UbuntuSystemController:
    """Контроллер для глубокой интеграции с Ubuntu"""
    
    def __init__(self):
        self.system_info = {}
        self.running_processes = {}
        self.system_services = {}
        self.network_interfaces = {}
        self.disk_usage = {}
        self.memory_usage = {}
        self.cpu_usage = {}
        self.active_users = {}
        self.installed_packages = {}
        self.system_logs = []
        self.security_status = {}
        
    def get_system_overview(self) -> Dict[str, Any]:
        """Получить полный обзор системы"""
        try:
            return {
                "os_info": self.get_os_info(),
                "hardware_info": self.get_hardware_info(),
                "network_info": self.get_network_info(),
                "process_info": self.get_process_info(),
                "service_info": self.get_service_info(),
                "user_info": self.get_user_info(),
                "package_info": self.get_package_info(),
                "security_info": self.get_security_info(),
                "performance_metrics": self.get_performance_metrics()
            }
        except Exception as e:
            logger.error(f"Ошибка получения обзора системы: {e}")
            return {"error": str(e)}
    
    def get_os_info(self) -> Dict[str, Any]:
        """Получить информацию об ОС"""
        try:
            # Основная информация об ОС
            os_info = {
                "distribution": self._run_command("lsb_release -d | cut -f2"),
                "version": self._run_command("lsb_release -r | cut -f2"),
                "codename": self._run_command("lsb_release -c | cut -f2"),
                "kernel": self._run_command("uname -r"),
                "architecture": self._run_command("uname -m"),
                "hostname": self._run_command("hostname"),
                "uptime": self._run_command("uptime -p"),
                "boot_time": self._run_command("who -b | awk '{print $3, $4}'"),
                "timezone": self._run_command("timedatectl | grep 'Time zone' | awk '{print $3}'"),
                "language": self._run_command("locale | grep LANG | cut -d= -f2")
            }
            return os_info
        except Exception as e:
            logger.error(f"Ошибка получения информации об ОС: {e}")
            return {"error": str(e)}
    
    def get_hardware_info(self) -> Dict[str, Any]:
        """Получить информацию о железе"""
        try:
            hardware_info = {
                "cpu": self._get_cpu_info(),
                "memory": self._get_memory_info(),
                "disk": self._get_disk_info(),
                "network": self._get_network_hardware_info(),
                "gpu": self._get_gpu_info(),
                "usb": self._get_usb_info(),
                "pci": self._get_pci_info()
            }
            return hardware_info
        except Exception as e:
            logger.error(f"Ошибка получения информации о железе: {e}")
            return {"error": str(e)}
    
    def get_network_info(self) -> Dict[str, Any]:
        """Получить сетевую информацию"""
        try:
            network_info = {
                "interfaces": self._get_network_interfaces(),
                "connections": self._get_network_connections(),
                "routing": self._get_routing_info(),
                "dns": self._get_dns_info(),
                "firewall": self._get_firewall_info(),
                "ports": self._get_open_ports()
            }
            return network_info
        except Exception as e:
            logger.error(f"Ошибка получения сетевой информации: {e}")
            return {"error": str(e)}
    
    def get_process_info(self) -> Dict[str, Any]:
        """Получить информацию о процессах"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return {
                "total_processes": len(processes),
                "top_processes": sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:10],
                "system_processes": [p for p in processes if p['cpu_percent'] > 1.0],
                "user_processes": [p for p in processes if p['cpu_percent'] <= 1.0]
            }
        except Exception as e:
            logger.error(f"Ошибка получения информации о процессах: {e}")
            return {"error": str(e)}
    
    def get_service_info(self) -> Dict[str, Any]:
        """Получить информацию о службах"""
        try:
            services = {
                "systemd_services": self._get_systemd_services(),
                "running_services": self._get_running_services(),
                "failed_services": self._get_failed_services(),
                "enabled_services": self._get_enabled_services()
            }
            return services
        except Exception as e:
            logger.error(f"Ошибка получения информации о службах: {e}")
            return {"error": str(e)}
    
    def get_user_info(self) -> Dict[str, Any]:
        """Получить информацию о пользователях"""
        try:
            users = []
            for user in psutil.users():
                users.append({
                    "name": user.name,
                    "terminal": user.terminal,
                    "host": user.host,
                    "started": user.started
                })
            
            return {
                "active_users": users,
                "total_users": len(users),
                "system_users": self._get_system_users(),
                "user_groups": self._get_user_groups()
            }
        except Exception as e:
            logger.error(f"Ошибка получения информации о пользователях: {e}")
            return {"error": str(e)}
    
    def get_package_info(self) -> Dict[str, Any]:
        """Получить информацию о пакетах"""
        try:
            return {
                "installed_packages": self._get_installed_packages(),
                "upgradable_packages": self._get_upgradable_packages(),
                "package_sources": self._get_package_sources(),
                "recent_updates": self._get_recent_updates()
            }
        except Exception as e:
            logger.error(f"Ошибка получения информации о пакетах: {e}")
            return {"error": str(e)}
    
    def get_security_info(self) -> Dict[str, Any]:
        """Получить информацию о безопасности"""
        try:
            return {
                "firewall_status": self._get_firewall_status(),
                "antivirus_status": self._get_antivirus_status(),
                "security_updates": self._get_security_updates(),
                "vulnerabilities": self._get_vulnerabilities(),
                "failed_logins": self._get_failed_logins(),
                "suspicious_activity": self._get_suspicious_activity()
            }
        except Exception as e:
            logger.error(f"Ошибка получения информации о безопасности: {e}")
            return {"error": str(e)}
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Получить метрики производительности"""
        try:
            return {
                "cpu_usage": psutil.cpu_percent(interval=1),
                "memory_usage": dict(psutil.virtual_memory()._asdict()),
                "disk_usage": self._get_disk_usage(),
                "network_io": self._get_network_io(),
                "load_average": self._get_load_average(),
                "temperature": self._get_temperature()
            }
        except Exception as e:
            logger.error(f"Ошибка получения метрик производительности: {e}")
            return {"error": str(e)}
    
    def execute_system_command(self, command: str, sudo: bool = False) -> Dict[str, Any]:
        """Выполнить системную команду"""
        try:
            if sudo:
                command = f"sudo {command}"
            
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "command": command
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Timeout expired",
                "command": command
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "command": command
            }
    
    def manage_service(self, service_name: str, action: str) -> Dict[str, Any]:
        """Управление службами"""
        actions = {
            "start": f"systemctl start {service_name}",
            "stop": f"systemctl stop {service_name}",
            "restart": f"systemctl restart {service_name}",
            "enable": f"systemctl enable {service_name}",
            "disable": f"systemctl disable {service_name}",
            "status": f"systemctl status {service_name}"
        }
        
        if action not in actions:
            return {"success": False, "error": f"Неизвестное действие: {action}"}
        
        return self.execute_system_command(actions[action], sudo=True)
    
    def install_package(self, package_name: str) -> Dict[str, Any]:
        """Установить пакет"""
        command = f"apt install -y {package_name}"
        return self.execute_system_command(command, sudo=True)
    
    def remove_package(self, package_name: str) -> Dict[str, Any]:
        """Удалить пакет"""
        command = f"apt remove -y {package_name}"
        return self.execute_system_command(command, sudo=True)
    
    def update_system(self) -> Dict[str, Any]:
        """Обновить систему"""
        commands = [
            "apt update",
            "apt upgrade -y",
            "apt autoremove -y"
        ]
        
        results = []
        for cmd in commands:
            result = self.execute_system_command(cmd, sudo=True)
            results.append(result)
        
        return {
            "success": all(r["success"] for r in results),
            "results": results
        }
    
    def monitor_system_realtime(self, duration: int = 60) -> Dict[str, Any]:
        """Мониторинг системы в реальном времени"""
        start_time = time.time()
        metrics = []
        
        while time.time() - start_time < duration:
            metric = {
                "timestamp": time.time(),
                "cpu": psutil.cpu_percent(),
                "memory": psutil.virtual_memory().percent,
                "disk": psutil.disk_usage('/').percent,
                "network": self._get_network_io()
            }
            metrics.append(metric)
            time.sleep(1)
        
        return {
            "duration": duration,
            "metrics": metrics,
            "average_cpu": sum(m["cpu"] for m in metrics) / len(metrics),
            "average_memory": sum(m["memory"] for m in metrics) / len(metrics)
        }
    
    # Вспомогательные методы
    def _run_command(self, command: str) -> str:
        """Выполнить команду и вернуть результат"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return result.stdout.strip()
        except Exception as e:
            logger.error(f"Ошибка выполнения команды {command}: {e}")
            return ""
    
    def _get_cpu_info(self) -> Dict[str, Any]:
        """Получить информацию о CPU"""
        try:
            cpu_info = {
                "model": self._run_command("cat /proc/cpuinfo | grep 'model name' | head -1 | cut -d: -f2").strip(),
                "cores": psutil.cpu_count(),
                "physical_cores": psutil.cpu_count(logical=False),
                "frequency": psutil.cpu_freq().current if psutil.cpu_freq() else 0,
                "usage_per_core": [psutil.cpu_percent(interval=1, percpu=True)]
            }
            return cpu_info
        except Exception as e:
            logger.error(f"Ошибка получения информации о CPU: {e}")
            return {"error": str(e)}
    
    def _get_memory_info(self) -> Dict[str, Any]:
        """Получить информацию о памяти"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            return {
                "total": memory.total,
                "available": memory.available,
                "used": memory.used,
                "free": memory.free,
                "percent": memory.percent,
                "swap_total": swap.total,
                "swap_used": swap.used,
                "swap_free": swap.free
            }
        except Exception as e:
            logger.error(f"Ошибка получения информации о памяти: {e}")
            return {"error": str(e)}
    
    def _get_disk_info(self) -> Dict[str, Any]:
        """Получить информацию о дисках"""
        try:
            disks = {}
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disks[partition.device] = {
                        "mountpoint": partition.mountpoint,
                        "filesystem": partition.fstype,
                        "total": usage.total,
                        "used": usage.used,
                        "free": usage.free,
                        "percent": usage.percent
                    }
                except PermissionError:
                    continue
            
            return disks
        except Exception as e:
            logger.error(f"Ошибка получения информации о дисках: {e}")
            return {"error": str(e)}
    
    def _get_network_hardware_info(self) -> Dict[str, Any]:
        """Получить информацию о сетевом оборудовании"""
        try:
            interfaces = {}
            for interface, addresses in psutil.net_if_addrs().items():
                interfaces[interface] = {
                    "addresses": [addr.address for addr in addresses],
                    "netmask": [addr.netmask for addr in addresses if addr.netmask],
                    "broadcast": [addr.broadcast for addr in addresses if addr.broadcast]
                }
            
            return interfaces
        except Exception as e:
            logger.error(f"Ошибка получения сетевой информации: {e}")
            return {"error": str(e)}
    
    def _get_gpu_info(self) -> Dict[str, Any]:
        """Получить информацию о GPU"""
        try:
            # Попытка получить информацию о NVIDIA GPU
            nvidia_info = self._run_command("nvidia-smi --query-gpu=name,memory.total,memory.used --format=csv,noheader,nounits")
            
            if nvidia_info:
                return {"nvidia": nvidia_info.split('\n')}
            else:
                return {"message": "NVIDIA GPU не обнаружен"}
        except Exception as e:
            logger.error(f"Ошибка получения информации о GPU: {e}")
            return {"error": str(e)}
    
    def _get_usb_info(self) -> Dict[str, Any]:
        """Получить информацию о USB устройствах"""
        try:
            usb_devices = self._run_command("lsusb")
            return {"devices": usb_devices.split('\n') if usb_devices else []}
        except Exception as e:
            logger.error(f"Ошибка получения USB информации: {e}")
            return {"error": str(e)}
    
    def _get_pci_info(self) -> Dict[str, Any]:
        """Получить информацию о PCI устройствах"""
        try:
            pci_devices = self._run_command("lspci")
            return {"devices": pci_devices.split('\n') if pci_devices else []}
        except Exception as e:
            logger.error(f"Ошибка получения PCI информации: {e}")
            return {"error": str(e)}
    
    def _get_network_interfaces(self) -> Dict[str, Any]:
        """Получить сетевые интерфейсы"""
        try:
            interfaces = {}
            for interface, addresses in psutil.net_if_addrs().items():
                interfaces[interface] = {
                    "addresses": [addr.address for addr in addresses],
                    "netmask": [addr.netmask for addr in addresses if addr.netmask],
                    "broadcast": [addr.broadcast for addr in addresses if addr.broadcast]
                }
            return interfaces
        except Exception as e:
            logger.error(f"Ошибка получения сетевых интерфейсов: {e}")
            return {"error": str(e)}
    
    def _get_network_connections(self) -> List[Dict[str, Any]]:
        """Получить сетевые соединения"""
        try:
            connections = []
            for conn in psutil.net_connections():
                connections.append({
                    "fd": conn.fd,
                    "family": conn.family,
                    "type": conn.type,
                    "laddr": conn.laddr,
                    "raddr": conn.raddr,
                    "status": conn.status,
                    "pid": conn.pid
                })
            return connections
        except Exception as e:
            logger.error(f"Ошибка получения сетевых соединений: {e}")
            return []
    
    def _get_routing_info(self) -> Dict[str, Any]:
        """Получить информацию о маршрутизации"""
        try:
            routing_table = self._run_command("ip route show")
            return {"routes": routing_table.split('\n') if routing_table else []}
        except Exception as e:
            logger.error(f"Ошибка получения информации о маршрутизации: {e}")
            return {"error": str(e)}
    
    def _get_dns_info(self) -> Dict[str, Any]:
        """Получить DNS информацию"""
        try:
            resolv_conf = self._run_command("cat /etc/resolv.conf")
            return {"resolv_conf": resolv_conf.split('\n') if resolv_conf else []}
        except Exception as e:
            logger.error(f"Ошибка получения DNS информации: {e}")
            return {"error": str(e)}
    
    def _get_firewall_info(self) -> Dict[str, Any]:
        """Получить информацию о файрволе"""
        try:
            ufw_status = self._run_command("ufw status")
            return {"ufw_status": ufw_status}
        except Exception as e:
            logger.error(f"Ошибка получения информации о файрволе: {e}")
            return {"error": str(e)}
    
    def _get_open_ports(self) -> List[Dict[str, Any]]:
        """Получить открытые порты"""
        try:
            open_ports = []
            for conn in psutil.net_connections():
                if conn.status == 'LISTEN':
                    open_ports.append({
                        "port": conn.laddr.port,
                        "address": conn.laddr.ip,
                        "pid": conn.pid
                    })
            return open_ports
        except Exception as e:
            logger.error(f"Ошибка получения открытых портов: {e}")
            return []
    
    def _get_systemd_services(self) -> List[Dict[str, Any]]:
        """Получить systemd службы"""
        try:
            services = self._run_command("systemctl list-units --type=service --all")
            return [{"service": line} for line in services.split('\n') if line.strip()]
        except Exception as e:
            logger.error(f"Ошибка получения systemd служб: {e}")
            return []
    
    def _get_running_services(self) -> List[str]:
        """Получить запущенные службы"""
        try:
            running = self._run_command("systemctl list-units --type=service --state=running")
            return [line for line in running.split('\n') if line.strip()]
        except Exception as e:
            logger.error(f"Ошибка получения запущенных служб: {e}")
            return []
    
    def _get_failed_services(self) -> List[str]:
        """Получить неудачные службы"""
        try:
            failed = self._run_command("systemctl list-units --type=service --state=failed")
            return [line for line in failed.split('\n') if line.strip()]
        except Exception as e:
            logger.error(f"Ошибка получения неудачных служб: {e}")
            return []
    
    def _get_enabled_services(self) -> List[str]:
        """Получить включенные службы"""
        try:
            enabled = self._run_command("systemctl list-unit-files --type=service --state=enabled")
            return [line for line in enabled.split('\n') if line.strip()]
        except Exception as e:
            logger.error(f"Ошибка получения включенных служб: {e}")
            return []
    
    def _get_system_users(self) -> List[str]:
        """Получить системных пользователей"""
        try:
            users = self._run_command("cat /etc/passwd | grep -E ':/bin/(false|nologin)' | cut -d: -f1")
            return [user for user in users.split('\n') if user.strip()]
        except Exception as e:
            logger.error(f"Ошибка получения системных пользователей: {e}")
            return []
    
    def _get_user_groups(self) -> Dict[str, List[str]]:
        """Получить группы пользователей"""
        try:
            groups = self._run_command("cat /etc/group")
            return {"groups": [group for group in groups.split('\n') if group.strip()]}
        except Exception as e:
            logger.error(f"Ошибка получения групп пользователей: {e}")
            return {"error": str(e)}
    
    def _get_installed_packages(self) -> List[str]:
        """Получить установленные пакеты"""
        try:
            packages = self._run_command("dpkg --list | grep '^ii' | awk '{print $2}'")
            return [pkg for pkg in packages.split('\n') if pkg.strip()]
        except Exception as e:
            logger.error(f"Ошибка получения установленных пакетов: {e}")
            return []
    
    def _get_upgradable_packages(self) -> List[str]:
        """Получить обновляемые пакеты"""
        try:
            upgradable = self._run_command("apt list --upgradable 2>/dev/null | grep -v 'WARNING'")
            return [pkg for pkg in upgradable.split('\n') if pkg.strip()]
        except Exception as e:
            logger.error(f"Ошибка получения обновляемых пакетов: {e}")
            return []
    
    def _get_package_sources(self) -> List[str]:
        """Получить источники пакетов"""
        try:
            sources = self._run_command("cat /etc/apt/sources.list")
            return [source for source in sources.split('\n') if source.strip() and not source.startswith('#')]
        except Exception as e:
            logger.error(f"Ошибка получения источников пакетов: {e}")
            return []
    
    def _get_recent_updates(self) -> List[str]:
        """Получить недавние обновления"""
        try:
            updates = self._run_command("cat /var/log/apt/history.log | grep 'Commandline: apt' | tail -10")
            return [update for update in updates.split('\n') if update.strip()]
        except Exception as e:
            logger.error(f"Ошибка получения недавних обновлений: {e}")
            return []
    
    def _get_firewall_status(self) -> Dict[str, Any]:
        """Получить статус файрвола"""
        try:
            ufw_status = self._run_command("ufw status")
            return {"status": ufw_status}
        except Exception as e:
            logger.error(f"Ошибка получения статуса файрвола: {e}")
            return {"error": str(e)}
    
    def _get_antivirus_status(self) -> Dict[str, Any]:
        """Получить статус антивируса"""
        try:
            # Проверяем наличие ClamAV
            clamav_status = self._run_command("clamscan --version")
            return {"clamav": clamav_status if clamav_status else "Не установлен"}
        except Exception as e:
            logger.error(f"Ошибка получения статуса антивируса: {e}")
            return {"error": str(e)}
    
    def _get_security_updates(self) -> List[str]:
        """Получить обновления безопасности"""
        try:
            security_updates = self._run_command("apt list --upgradable 2>/dev/null | grep security")
            return [update for update in security_updates.split('\n') if update.strip()]
        except Exception as e:
            logger.error(f"Ошибка получения обновлений безопасности: {e}")
            return []
    
    def _get_vulnerabilities(self) -> List[str]:
        """Получить уязвимости"""
        try:
            # Простая проверка через apt
            vulnerabilities = self._run_command("apt list --upgradable 2>/dev/null | grep -E '(security|critical)'")
            return [vuln for vuln in vulnerabilities.split('\n') if vuln.strip()]
        except Exception as e:
            logger.error(f"Ошибка получения уязвимостей: {e}")
            return []
    
    def _get_failed_logins(self) -> List[str]:
        """Получить неудачные попытки входа"""
        try:
            failed_logins = self._run_command("grep 'Failed password' /var/log/auth.log | tail -10")
            return [login for login in failed_logins.split('\n') if login.strip()]
        except Exception as e:
            logger.error(f"Ошибка получения неудачных попыток входа: {e}")
            return []
    
    def _get_suspicious_activity(self) -> List[str]:
        """Получить подозрительную активность"""
        try:
            suspicious = self._run_command("grep -E '(error|warning|critical)' /var/log/syslog | tail -10")
            return [activity for activity in suspicious.split('\n') if activity.strip()]
        except Exception as e:
            logger.error(f"Ошибка получения подозрительной активности: {e}")
            return []
    
    def _get_disk_usage(self) -> Dict[str, Any]:
        """Получить использование диска"""
        try:
            disk_usage = {}
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage[partition.mountpoint] = {
                        "total": usage.total,
                        "used": usage.used,
                        "free": usage.free,
                        "percent": usage.percent
                    }
                except PermissionError:
                    continue
            return disk_usage
        except Exception as e:
            logger.error(f"Ошибка получения использования диска: {e}")
            return {"error": str(e)}
    
    def _get_network_io(self) -> Dict[str, Any]:
        """Получить сетевой ввод-вывод"""
        try:
            net_io = psutil.net_io_counters()
            return {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv
            }
        except Exception as e:
            logger.error(f"Ошибка получения сетевого ввода-вывода: {e}")
            return {"error": str(e)}
    
    def _get_load_average(self) -> Dict[str, float]:
        """Получить среднюю нагрузку"""
        try:
            load_avg = psutil.getloadavg()
            return {
                "1min": load_avg[0],
                "5min": load_avg[1],
                "15min": load_avg[2]
            }
        except Exception as e:
            logger.error(f"Ошибка получения средней нагрузки: {e}")
            return {"error": str(e)}
    
    def _get_temperature(self) -> Dict[str, Any]:
        """Получить температуру"""
        try:
            # Попытка получить температуру через sensors
            temp = self._run_command("sensors | grep 'Core' | head -1 | awk '{print $3}'")
            return {"temperature": temp if temp else "Недоступно"}
        except Exception as e:
            logger.error(f"Ошибка получения температуры: {e}")
            return {"error": str(e)}

# Создание глобального экземпляра
ubuntu_controller = UbuntuSystemController()

if __name__ == "__main__":
    # Тестирование контроллера
    controller = UbuntuSystemController()
    
    print("🧠 ARK Ubuntu System Controller Test")
    print("=" * 50)
    
    # Тест получения обзора системы
    print("📊 Получение обзора системы...")
    overview = controller.get_system_overview()
    print(f"✅ Обзор получен: {len(overview)} разделов")
    
    # Тест выполнения команды
    print("🔧 Тест выполнения команды...")
    result = controller.execute_system_command("echo 'Hello ARK!'")
    print(f"✅ Команда выполнена: {result['success']}")
    
    # Тест мониторинга
    print("📈 Тест мониторинга (5 секунд)...")
    monitoring = controller.monitor_system_realtime(5)
    print(f"✅ Мониторинг завершен: {len(monitoring['metrics'])} метрик")
    
    print("🎉 Тестирование завершено!") 