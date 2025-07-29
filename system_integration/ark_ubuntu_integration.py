#!/usr/bin/env python3
"""
ARK v2.8 - Ubuntu Deep Integration Module
Глубокая интеграция с операционной системой Ubuntu
"""

import sys
import time
import json
import logging
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from system_integration.ubuntu_controller import UbuntuSystemController
from system_integration.systemd_integration import SystemDIntegration
from system_integration.network_security import NetworkSecurityIntegration

logger = logging.getLogger(__name__)

class ARKUbuntuIntegration:
    """Главный модуль интеграции ARK с Ubuntu"""
    
    def __init__(self):
        self.system_controller = UbuntuSystemController()
        self.systemd_integration = SystemDIntegration()
        self.network_security = NetworkSecurityIntegration()
        
        self.monitoring_active = False
        self.monitoring_thread = None
        self.monitoring_data = []
        
    def get_full_system_status(self) -> Dict[str, Any]:
        """Получить полный статус системы"""
        try:
            return {
                "timestamp": time.time(),
                "system_overview": self.system_controller.get_system_overview(),
                "systemd_status": self.systemd_integration.get_system_status(),
                "network_overview": self.network_security.get_network_overview(),
                "security_overview": self.network_security.get_security_overview(),
                "performance_metrics": self.system_controller.get_performance_metrics()
            }
        except Exception as e:
            logger.error(f"Ошибка получения полного статуса системы: {e}")
            return {"error": str(e)}
    
    def execute_system_command(self, command: str, sudo: bool = False) -> Dict[str, Any]:
        """Выполнить системную команду"""
        return self.system_controller.execute_system_command(command, sudo)
    
    def manage_service(self, service_name: str, action: str) -> Dict[str, Any]:
        """Управление службами"""
        return self.systemd_integration.manage_service(service_name, action)
    
    def configure_firewall(self, action: str, port: str = None, protocol: str = "tcp") -> Dict[str, Any]:
        """Настроить файрвол"""
        return self.network_security.configure_firewall(action, port, protocol)
    
    def scan_network(self, target: str = "localhost") -> Dict[str, Any]:
        """Сканировать сеть"""
        return self.network_security.scan_network(target)
    
    def install_package(self, package_name: str) -> Dict[str, Any]:
        """Установить пакет"""
        return self.system_controller.install_package(package_name)
    
    def remove_package(self, package_name: str) -> Dict[str, Any]:
        """Удалить пакет"""
        return self.system_controller.remove_package(package_name)
    
    def update_system(self) -> Dict[str, Any]:
        """Обновить систему"""
        return self.system_controller.update_system()
    
    def start_monitoring(self, duration: int = 3600) -> Dict[str, Any]:
        """Начать мониторинг системы"""
        if self.monitoring_active:
            return {"success": False, "error": "Мониторинг уже активен"}
        
        self.monitoring_active = True
        self.monitoring_data = []
        
        def monitoring_loop():
            start_time = time.time()
            while self.monitoring_active and (time.time() - start_time) < duration:
                try:
                    data_point = {
                        "timestamp": time.time(),
                        "system_metrics": self.system_controller.get_performance_metrics(),
                        "network_traffic": self.network_security.get_network_traffic(),
                        "active_services": len(self.systemd_integration.get_running_services())
                    }
                    self.monitoring_data.append(data_point)
                    time.sleep(5)  # Обновление каждые 5 секунд
                except Exception as e:
                    logger.error(f"Ошибка мониторинга: {e}")
                    time.sleep(5)
        
        self.monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        return {
            "success": True,
            "message": f"Мониторинг запущен на {duration} секунд",
            "duration": duration
        }
    
    def stop_monitoring(self) -> Dict[str, Any]:
        """Остановить мониторинг"""
        if not self.monitoring_active:
            return {"success": False, "error": "Мониторинг не активен"}
        
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        return {
            "success": True,
            "message": "Мониторинг остановлен",
            "data_points": len(self.monitoring_data)
        }
    
    def get_monitoring_data(self) -> List[Dict[str, Any]]:
        """Получить данные мониторинга"""
        return self.monitoring_data.copy()
    
    def analyze_system_health(self) -> Dict[str, Any]:
        """Анализ здоровья системы"""
        try:
            health_report = {
                "timestamp": time.time(),
                "overall_health": "good",
                "issues": [],
                "recommendations": []
            }
            
            # Проверка производительности
            performance = self.system_controller.get_performance_metrics()
            if "error" not in performance:
                cpu_usage = performance.get("cpu_usage", 0)
                memory_usage = performance.get("memory_usage", {}).get("percent", 0)
                
                if cpu_usage > 80:
                    health_report["issues"].append(f"Высокое использование CPU: {cpu_usage}%")
                    health_report["recommendations"].append("Проверьте процессы с высоким потреблением CPU")
                
                if memory_usage > 85:
                    health_report["issues"].append(f"Высокое использование памяти: {memory_usage}%")
                    health_report["recommendations"].append("Рассмотрите возможность увеличения RAM или оптимизации процессов")
            
            # Проверка служб
            failed_services = self.systemd_integration.get_failed_services()
            if failed_services:
                health_report["issues"].append(f"Неудачные службы: {len(failed_services)}")
                health_report["recommendations"].append("Проверьте и перезапустите неудачные службы")
            
            # Проверка безопасности
            security = self.network_security.get_security_overview()
            if "error" not in security:
                vulnerabilities = security.get("vulnerabilities", [])
                if vulnerabilities:
                    health_report["issues"].append(f"Найдены уязвимости: {len(vulnerabilities)}")
                    health_report["recommendations"].append("Установите обновления безопасности")
            
            # Определение общего состояния
            if len(health_report["issues"]) > 3:
                health_report["overall_health"] = "critical"
            elif len(health_report["issues"]) > 1:
                health_report["overall_health"] = "warning"
            else:
                health_report["overall_health"] = "good"
            
            return health_report
            
        except Exception as e:
            logger.error(f"Ошибка анализа здоровья системы: {e}")
            return {"error": str(e)}
    
    def optimize_system(self) -> Dict[str, Any]:
        """Оптимизация системы"""
        try:
            optimizations = []
            
            # Очистка кэша apt
            apt_clean = self.execute_system_command("apt clean", sudo=True)
            if apt_clean["success"]:
                optimizations.append("Очищен кэш apt")
            
            # Удаление неиспользуемых пакетов
            autoremove = self.execute_system_command("apt autoremove -y", sudo=True)
            if autoremove["success"]:
                optimizations.append("Удалены неиспользуемые пакеты")
            
            # Очистка временных файлов
            temp_clean = self.execute_system_command("find /tmp -type f -atime +7 -delete", sudo=True)
            if temp_clean["success"]:
                optimizations.append("Очищены старые временные файлы")
            
            # Очистка логов
            log_clean = self.execute_system_command("find /var/log -name '*.log' -mtime +30 -delete", sudo=True)
            if log_clean["success"]:
                optimizations.append("Очищены старые логи")
            
            return {
                "success": True,
                "optimizations": optimizations,
                "message": f"Выполнено {len(optimizations)} оптимизаций"
            }
            
        except Exception as e:
            logger.error(f"Ошибка оптимизации системы: {e}")
            return {"error": str(e)}
    
    def backup_system_config(self, backup_path: str = None) -> Dict[str, Any]:
        """Создать резервную копию конфигурации системы"""
        try:
            if not backup_path:
                backup_path = f"/tmp/ark_system_backup_{int(time.time())}.tar.gz"
            
            # Создаем список важных конфигурационных файлов
            config_files = [
                "/etc/passwd",
                "/etc/group",
                "/etc/shadow",
                "/etc/sudoers",
                "/etc/hosts",
                "/etc/resolv.conf",
                "/etc/fstab",
                "/etc/crontab",
                "/etc/ssh/sshd_config",
                "/etc/ufw/ufw.conf"
            ]
            
            # Создаем архив
            files_list = " ".join(config_files)
            result = self.execute_system_command(
                f"tar -czf {backup_path} {files_list}",
                sudo=True
            )
            
            if result["success"]:
                return {
                    "success": True,
                    "backup_path": backup_path,
                    "message": "Резервная копия создана успешно"
                }
            else:
                return {
                    "success": False,
                    "error": "Ошибка создания резервной копии"
                }
                
        except Exception as e:
            logger.error(f"Ошибка создания резервной копии: {e}")
            return {"error": str(e)}
    
    def restore_system_config(self, backup_path: str) -> Dict[str, Any]:
        """Восстановить конфигурацию системы из резервной копии"""
        try:
            if not Path(backup_path).exists():
                return {"success": False, "error": "Файл резервной копии не найден"}
            
            # Распаковываем архив
            result = self.execute_system_command(
                f"tar -xzf {backup_path} -C /",
                sudo=True
            )
            
            if result["success"]:
                return {
                    "success": True,
                    "message": "Конфигурация восстановлена успешно"
                }
            else:
                return {
                    "success": False,
                    "error": "Ошибка восстановления конфигурации"
                }
                
        except Exception as e:
            logger.error(f"Ошибка восстановления конфигурации: {e}")
            return {"error": str(e)}
    
    def get_system_recommendations(self) -> Dict[str, Any]:
        """Получить рекомендации по улучшению системы"""
        try:
            recommendations = []
            
            # Анализ производительности
            performance = self.system_controller.get_performance_metrics()
            if "error" not in performance:
                cpu_usage = performance.get("cpu_usage", 0)
                memory_usage = performance.get("memory_usage", {}).get("percent", 0)
                
                if cpu_usage > 70:
                    recommendations.append({
                        "category": "performance",
                        "priority": "high",
                        "title": "Высокое использование CPU",
                        "description": f"CPU используется на {cpu_usage}%",
                        "action": "Проверьте процессы с высоким потреблением ресурсов"
                    })
                
                if memory_usage > 80:
                    recommendations.append({
                        "category": "performance",
                        "priority": "high",
                        "title": "Высокое использование памяти",
                        "description": f"Память используется на {memory_usage}%",
                        "action": "Рассмотрите увеличение RAM или оптимизацию процессов"
                    })
            
            # Анализ безопасности
            security = self.network_security.get_security_overview()
            if "error" not in security:
                firewall = security.get("firewall", {})
                if not firewall.get("ufw", {}).get("enabled", False):
                    recommendations.append({
                        "category": "security",
                        "priority": "critical",
                        "title": "Файрвол отключен",
                        "description": "Система не защищена файрволом",
                        "action": "Включите UFW для защиты системы"
                    })
            
            # Анализ обновлений
            system_info = self.system_controller.get_os_info()
            if "error" not in system_info:
                recommendations.append({
                    "category": "maintenance",
                    "priority": "medium",
                    "title": "Регулярные обновления",
                    "description": "Убедитесь, что система регулярно обновляется",
                    "action": "Выполните apt update && apt upgrade"
                })
            
            return {
                "recommendations": recommendations,
                "total": len(recommendations),
                "critical": len([r for r in recommendations if r["priority"] == "critical"]),
                "high": len([r for r in recommendations if r["priority"] == "high"]),
                "medium": len([r for r in recommendations if r["priority"] == "medium"])
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения рекомендаций: {e}")
            return {"error": str(e)}

# Создание глобального экземпляра
ark_ubuntu_integration = ARKUbuntuIntegration()

if __name__ == "__main__":
    # Тестирование интеграции
    integration = ARKUbuntuIntegration()
    
    print("🧠 ARK Ubuntu Deep Integration Test")
    print("=" * 50)
    
    # Тест получения полного статуса
    print("📊 Получение полного статуса системы...")
    status = integration.get_full_system_status()
    print(f"✅ Статус получен: {len(status)} разделов")
    
    # Тест анализа здоровья системы
    print("🏥 Анализ здоровья системы...")
    health = integration.analyze_system_health()
    print(f"✅ Здоровье системы: {health.get('overall_health', 'unknown')}")
    
    # Тест получения рекомендаций
    print("💡 Получение рекомендаций...")
    recommendations = integration.get_system_recommendations()
    print(f"✅ Рекомендаций: {recommendations.get('total', 0)}")
    
    # Тест оптимизации
    print("⚡ Тест оптимизации системы...")
    optimization = integration.optimize_system()
    print(f"✅ Оптимизация: {optimization.get('message', 'Ошибка')}")
    
    print("🎉 Тестирование завершено!") 