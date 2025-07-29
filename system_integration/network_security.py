#!/usr/bin/env python3
"""
ARK v2.8 - Network & Security Integration Module
Интеграция с сетью и безопасностью Ubuntu
"""

import subprocess
import json
import time
import logging
import socket
import psutil
from typing import Dict, List, Any, Optional
from pathlib import Path
import os

logger = logging.getLogger(__name__)

class NetworkSecurityIntegration:
    """Интеграция с сетью и безопасностью"""
    
    def __init__(self):
        self.network_cache = {}
        self.security_cache = {}
        self.last_update = 0
        self.cache_duration = 60  # секунды
        
    def get_network_overview(self) -> Dict[str, Any]:
        """Получить полный обзор сети"""
        try:
            return {
                "interfaces": self.get_network_interfaces(),
                "connections": self.get_network_connections(),
                "routing": self.get_routing_table(),
                "dns": self.get_dns_info(),
                "firewall": self.get_firewall_status(),
                "ports": self.get_open_ports(),
                "traffic": self.get_network_traffic(),
                "bandwidth": self.get_bandwidth_usage()
            }
        except Exception as e:
            logger.error(f"Ошибка получения обзора сети: {e}")
            return {"error": str(e)}
    
    def get_security_overview(self) -> Dict[str, Any]:
        """Получить полный обзор безопасности"""
        try:
            return {
                "firewall": self.get_firewall_status(),
                "antivirus": self.get_antivirus_status(),
                "updates": self.get_security_updates(),
                "vulnerabilities": self.get_vulnerabilities(),
                "failed_logins": self.get_failed_logins(),
                "suspicious_activity": self.get_suspicious_activity(),
                "ssl_certificates": self.get_ssl_certificates(),
                "user_permissions": self.get_user_permissions()
            }
        except Exception as e:
            logger.error(f"Ошибка получения обзора безопасности: {e}")
            return {"error": str(e)}
    
    def get_network_interfaces(self) -> Dict[str, Any]:
        """Получить сетевые интерфейсы"""
        try:
            interfaces = {}
            for interface, addresses in psutil.net_if_addrs().items():
                interface_info = {
                    "addresses": [],
                    "netmasks": [],
                    "broadcasts": []
                }
                
                for addr in addresses:
                    interface_info["addresses"].append(addr.address)
                    if addr.netmask:
                        interface_info["netmasks"].append(addr.netmask)
                    if addr.broadcast:
                        interface_info["broadcasts"].append(addr.broadcast)
                
                # Получаем статистику интерфейса
                try:
                    stats = psutil.net_if_stats()[interface]
                    interface_info["stats"] = {
                        "isup": stats.isup,
                        "duplex": stats.duplex,
                        "speed": stats.speed,
                        "mtu": stats.mtu
                    }
                except KeyError:
                    interface_info["stats"] = {"error": "Статистика недоступна"}
                
                interfaces[interface] = interface_info
            
            return interfaces
        except Exception as e:
            logger.error(f"Ошибка получения сетевых интерфейсов: {e}")
            return {"error": str(e)}
    
    def get_network_connections(self) -> List[Dict[str, Any]]:
        """Получить сетевые соединения"""
        try:
            connections = []
            for conn in psutil.net_connections():
                connection_info = {
                    "fd": conn.fd,
                    "family": conn.family,
                    "type": conn.type,
                    "laddr": f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                    "raddr": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                    "status": conn.status,
                    "pid": conn.pid
                }
                connections.append(connection_info)
            
            return connections
        except Exception as e:
            logger.error(f"Ошибка получения сетевых соединений: {e}")
            return []
    
    def get_routing_table(self) -> Dict[str, Any]:
        """Получить таблицу маршрутизации"""
        try:
            result = subprocess.run(
                "ip route show",
                shell=True, capture_output=True, text=True
            )
            
            routes = []
            for line in result.stdout.split('\n'):
                if line.strip():
                    routes.append(line.strip())
            
            return {
                "routes": routes,
                "default_gateway": self._get_default_gateway()
            }
        except Exception as e:
            logger.error(f"Ошибка получения таблицы маршрутизации: {e}")
            return {"error": str(e)}
    
    def get_dns_info(self) -> Dict[str, Any]:
        """Получить DNS информацию"""
        try:
            # Читаем resolv.conf
            result = subprocess.run(
                "cat /etc/resolv.conf",
                shell=True, capture_output=True, text=True
            )
            
            dns_servers = []
            search_domains = []
            
            for line in result.stdout.split('\n'):
                if line.startswith('nameserver'):
                    dns_servers.append(line.split()[1])
                elif line.startswith('search'):
                    search_domains = line.split()[1:]
            
            return {
                "dns_servers": dns_servers,
                "search_domains": search_domains,
                "resolv_conf": result.stdout
            }
        except Exception as e:
            logger.error(f"Ошибка получения DNS информации: {e}")
            return {"error": str(e)}
    
    def get_firewall_status(self) -> Dict[str, Any]:
        """Получить статус файрвола"""
        try:
            # Проверяем UFW
            ufw_result = subprocess.run(
                "ufw status",
                shell=True, capture_output=True, text=True
            )
            
            # Проверяем iptables
            iptables_result = subprocess.run(
                "sudo iptables -L -n",
                shell=True, capture_output=True, text=True
            )
            
            return {
                "ufw": {
                    "status": ufw_result.stdout,
                    "enabled": "Status: active" in ufw_result.stdout
                },
                "iptables": {
                    "rules": iptables_result.stdout,
                    "success": iptables_result.returncode == 0
                }
            }
        except Exception as e:
            logger.error(f"Ошибка получения статуса файрвола: {e}")
            return {"error": str(e)}
    
    def get_open_ports(self) -> List[Dict[str, Any]]:
        """Получить открытые порты"""
        try:
            open_ports = []
            for conn in psutil.net_connections():
                if conn.status == 'LISTEN':
                    port_info = {
                        "port": conn.laddr.port,
                        "address": conn.laddr.ip,
                        "protocol": "TCP" if conn.type == socket.SOCK_STREAM else "UDP",
                        "pid": conn.pid,
                        "process": self._get_process_name(conn.pid) if conn.pid else None
                    }
                    open_ports.append(port_info)
            
            return open_ports
        except Exception as e:
            logger.error(f"Ошибка получения открытых портов: {e}")
            return []
    
    def get_network_traffic(self) -> Dict[str, Any]:
        """Получить сетевой трафик"""
        try:
            net_io = psutil.net_io_counters()
            return {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv,
                "errin": net_io.errin,
                "errout": net_io.errout,
                "dropin": net_io.dropin,
                "dropout": net_io.dropout
            }
        except Exception as e:
            logger.error(f"Ошибка получения сетевого трафика: {e}")
            return {"error": str(e)}
    
    def get_bandwidth_usage(self) -> Dict[str, Any]:
        """Получить использование пропускной способности"""
        try:
            # Получаем статистику по интерфейсам
            interfaces = {}
            for interface in psutil.net_if_stats().keys():
                try:
                    # Используем ss для получения статистики
                    result = subprocess.run(
                        f"cat /sys/class/net/{interface}/statistics/rx_bytes",
                        shell=True, capture_output=True, text=True
                    )
                    rx_bytes = int(result.stdout.strip()) if result.stdout.strip() else 0
                    
                    result = subprocess.run(
                        f"cat /sys/class/net/{interface}/statistics/tx_bytes",
                        shell=True, capture_output=True, text=True
                    )
                    tx_bytes = int(result.stdout.strip()) if result.stdout.strip() else 0
                    
                    interfaces[interface] = {
                        "rx_bytes": rx_bytes,
                        "tx_bytes": tx_bytes,
                        "total_bytes": rx_bytes + tx_bytes
                    }
                except Exception:
                    continue
            
            return {"interfaces": interfaces}
        except Exception as e:
            logger.error(f"Ошибка получения использования пропускной способности: {e}")
            return {"error": str(e)}
    
    def get_antivirus_status(self) -> Dict[str, Any]:
        """Получить статус антивируса"""
        try:
            antivirus_status = {}
            
            # Проверяем ClamAV
            clamav_result = subprocess.run(
                "clamscan --version",
                shell=True, capture_output=True, text=True
            )
            antivirus_status["clamav"] = {
                "installed": clamav_result.returncode == 0,
                "version": clamav_result.stdout.strip() if clamav_result.stdout else None
            }
            
            # Проверяем другие антивирусы
            other_avs = ["chkrootkit", "rkhunter", "lynis"]
            for av in other_avs:
                result = subprocess.run(
                    f"which {av}",
                    shell=True, capture_output=True, text=True
                )
                antivirus_status[av] = {
                    "installed": result.returncode == 0,
                    "path": result.stdout.strip() if result.stdout else None
                }
            
            return antivirus_status
        except Exception as e:
            logger.error(f"Ошибка получения статуса антивируса: {e}")
            return {"error": str(e)}
    
    def get_security_updates(self) -> List[str]:
        """Получить обновления безопасности"""
        try:
            result = subprocess.run(
                "apt list --upgradable 2>/dev/null | grep -E '(security|critical)'",
                shell=True, capture_output=True, text=True
            )
            
            updates = []
            for line in result.stdout.split('\n'):
                if line.strip():
                    updates.append(line.strip())
            
            return updates
        except Exception as e:
            logger.error(f"Ошибка получения обновлений безопасности: {e}")
            return []
    
    def get_vulnerabilities(self) -> List[str]:
        """Получить уязвимости"""
        try:
            vulnerabilities = []
            
            # Проверяем уязвимости через apt
            apt_result = subprocess.run(
                "apt list --upgradable 2>/dev/null | grep -E '(security|critical|high)'",
                shell=True, capture_output=True, text=True
            )
            
            for line in apt_result.stdout.split('\n'):
                if line.strip():
                    vulnerabilities.append(f"APT: {line.strip()}")
            
            # Проверяем через lynis если установлен
            lynis_result = subprocess.run(
                "which lynis",
                shell=True, capture_output=True, text=True
            )
            
            if lynis_result.returncode == 0:
                lynis_scan = subprocess.run(
                    "sudo lynis audit system --quick",
                    shell=True, capture_output=True, text=True
                )
                
                if lynis_scan.stdout:
                    for line in lynis_scan.stdout.split('\n'):
                        if 'warning' in line.lower() or 'vulnerability' in line.lower():
                            vulnerabilities.append(f"Lynis: {line.strip()}")
            
            return vulnerabilities
        except Exception as e:
            logger.error(f"Ошибка получения уязвимостей: {e}")
            return []
    
    def get_failed_logins(self) -> List[str]:
        """Получить неудачные попытки входа"""
        try:
            failed_logins = []
            
            # Проверяем auth.log
            auth_result = subprocess.run(
                "grep 'Failed password' /var/log/auth.log | tail -20",
                shell=True, capture_output=True, text=True
            )
            
            for line in auth_result.stdout.split('\n'):
                if line.strip():
                    failed_logins.append(line.strip())
            
            # Проверяем btmp (неудачные попытки входа)
            btmp_result = subprocess.run(
                "lastb | head -10",
                shell=True, capture_output=True, text=True
            )
            
            for line in btmp_result.stdout.split('\n'):
                if line.strip() and not line.startswith('btmp'):
                    failed_logins.append(f"BTMP: {line.strip()}")
            
            return failed_logins
        except Exception as e:
            logger.error(f"Ошибка получения неудачных попыток входа: {e}")
            return []
    
    def get_suspicious_activity(self) -> List[str]:
        """Получить подозрительную активность"""
        try:
            suspicious = []
            
            # Проверяем системные логи
            syslog_result = subprocess.run(
                "grep -E '(error|warning|critical|alert)' /var/log/syslog | tail -20",
                shell=True, capture_output=True, text=True
            )
            
            for line in syslog_result.stdout.split('\n'):
                if line.strip():
                    suspicious.append(f"SYSLOG: {line.strip()}")
            
            # Проверяем kern.log
            kern_result = subprocess.run(
                "grep -E '(error|warning|critical)' /var/log/kern.log | tail -10",
                shell=True, capture_output=True, text=True
            )
            
            for line in kern_result.stdout.split('\n'):
                if line.strip():
                    suspicious.append(f"KERN: {line.strip()}")
            
            return suspicious
        except Exception as e:
            logger.error(f"Ошибка получения подозрительной активности: {e}")
            return []
    
    def get_ssl_certificates(self) -> List[Dict[str, Any]]:
        """Получить SSL сертификаты"""
        try:
            certificates = []
            
            # Ищем сертификаты в системе
            cert_paths = [
                "/etc/ssl/certs",
                "/etc/pki/tls/certs",
                "/usr/local/share/ca-certificates"
            ]
            
            for cert_path in cert_paths:
                if os.path.exists(cert_path):
                    result = subprocess.run(
                        f"find {cert_path} -name '*.crt' -o -name '*.pem' | head -10",
                        shell=True, capture_output=True, text=True
                    )
                    
                    for cert_file in result.stdout.split('\n'):
                        if cert_file.strip():
                            cert_info = {
                                "path": cert_file.strip(),
                                "type": "SSL Certificate"
                            }
                            
                            # Пытаемся получить информацию о сертификате
                            try:
                                openssl_result = subprocess.run(
                                    f"openssl x509 -in {cert_file.strip()} -text -noout | grep -E '(Subject:|Issuer:|Not After)' | head -3",
                                    shell=True, capture_output=True, text=True
                                )
                                
                                if openssl_result.stdout:
                                    cert_info["details"] = openssl_result.stdout.strip()
                            except Exception:
                                pass
                            
                            certificates.append(cert_info)
            
            return certificates
        except Exception as e:
            logger.error(f"Ошибка получения SSL сертификатов: {e}")
            return []
    
    def get_user_permissions(self) -> Dict[str, Any]:
        """Получить права пользователей"""
        try:
            permissions = {}
            
            # Получаем информацию о пользователях с sudo правами
            sudo_users = subprocess.run(
                "getent group sudo | cut -d: -f4",
                shell=True, capture_output=True, text=True
            )
            
            permissions["sudo_users"] = sudo_users.stdout.strip().split(',') if sudo_users.stdout.strip() else []
            
            # Получаем информацию о пользователях с root правами
            root_users = subprocess.run(
                "grep ':0:' /etc/passwd | cut -d: -f1",
                shell=True, capture_output=True, text=True
            )
            
            permissions["root_users"] = root_users.stdout.strip().split('\n') if root_users.stdout.strip() else []
            
            # Получаем информацию о группах
            groups = subprocess.run(
                "getent group | grep -E '(sudo|admin|wheel)'",
                shell=True, capture_output=True, text=True
            )
            
            permissions["privileged_groups"] = groups.stdout.strip().split('\n') if groups.stdout.strip() else []
            
            return permissions
        except Exception as e:
            logger.error(f"Ошибка получения прав пользователей: {e}")
            return {"error": str(e)}
    
    def configure_firewall(self, action: str, port: str = None, protocol: str = "tcp") -> Dict[str, Any]:
        """Настроить файрвол"""
        try:
            if action == "enable":
                result = subprocess.run(
                    "sudo ufw enable",
                    shell=True, capture_output=True, text=True
                )
            elif action == "disable":
                result = subprocess.run(
                    "sudo ufw disable",
                    shell=True, capture_output=True, text=True
                )
            elif action == "allow" and port:
                result = subprocess.run(
                    f"sudo ufw allow {port}/{protocol}",
                    shell=True, capture_output=True, text=True
                )
            elif action == "deny" and port:
                result = subprocess.run(
                    f"sudo ufw deny {port}/{protocol}",
                    shell=True, capture_output=True, text=True
                )
            else:
                return {"success": False, "error": "Неизвестное действие или отсутствует порт"}
            
            return {
                "action": action,
                "port": port,
                "protocol": protocol,
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
        except Exception as e:
            logger.error(f"Ошибка настройки файрвола: {e}")
            return {"error": str(e)}
    
    def scan_network(self, target: str = "localhost") -> Dict[str, Any]:
        """Сканировать сеть"""
        try:
            # Простое сканирование портов
            open_ports = []
            common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 3306, 5432, 8080]
            
            for port in common_ports:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    result = sock.connect_ex((target, port))
                    sock.close()
                    
                    if result == 0:
                        open_ports.append(port)
                except Exception:
                    continue
            
            return {
                "target": target,
                "open_ports": open_ports,
                "scan_time": time.time()
            }
            
        except Exception as e:
            logger.error(f"Ошибка сканирования сети: {e}")
            return {"error": str(e)}
    
    # Вспомогательные методы
    def _get_default_gateway(self) -> str:
        """Получить шлюз по умолчанию"""
        try:
            result = subprocess.run(
                "ip route | grep default | awk '{print $3}'",
                shell=True, capture_output=True, text=True
            )
            return result.stdout.strip()
        except Exception as e:
            logger.error(f"Ошибка получения шлюза по умолчанию: {e}")
            return "Недоступно"
    
    def _get_process_name(self, pid: int) -> str:
        """Получить имя процесса по PID"""
        try:
            process = psutil.Process(pid)
            return process.name()
        except Exception:
            return "Неизвестно"

# Создание глобального экземпляра
network_security = NetworkSecurityIntegration()

if __name__ == "__main__":
    # Тестирование интеграции
    integration = NetworkSecurityIntegration()
    
    print("🧠 ARK Network & Security Integration Test")
    print("=" * 50)
    
    # Тест получения обзора сети
    print("🌐 Получение обзора сети...")
    network_overview = integration.get_network_overview()
    print(f"✅ Обзор сети получен: {len(network_overview)} разделов")
    
    # Тест получения обзора безопасности
    print("🔒 Получение обзора безопасности...")
    security_overview = integration.get_security_overview()
    print(f"✅ Обзор безопасности получен: {len(security_overview)} разделов")
    
    # Тест сканирования сети
    print("🔍 Сканирование сети...")
    scan_result = integration.scan_network("localhost")
    print(f"✅ Сканирование завершено: {len(scan_result.get('open_ports', []))} открытых портов")
    
    print("🎉 Тестирование завершено!") 