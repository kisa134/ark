#!/usr/bin/env python3
"""
ARK v2.8 - SystemD Integration Module
Интеграция с системными службами Ubuntu через systemd
"""

import subprocess
import json
import time
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class SystemDIntegration:
    """Интеграция с systemd службами"""
    
    def __init__(self):
        self.services_cache = {}
        self.last_update = 0
        self.cache_duration = 30  # секунды
        
    def get_all_services(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Получить все службы systemd"""
        if not force_refresh and time.time() - self.last_update < self.cache_duration:
            return self.services_cache
        
        try:
            # Получаем все службы
            result = subprocess.run(
                "systemctl list-units --type=service --all --no-pager",
                shell=True, capture_output=True, text=True
            )
            
            services = {}
            for line in result.stdout.split('\n'):
                if line.strip() and not line.startswith('UNIT'):
                    parts = line.split()
                    if len(parts) >= 4:
                        service_name = parts[0]
                        load_state = parts[1]
                        active_state = parts[2]
                        sub_state = parts[3]
                        
                        services[service_name] = {
                            "load_state": load_state,
                            "active_state": active_state,
                            "sub_state": sub_state,
                            "description": ' '.join(parts[4:]) if len(parts) > 4 else ""
                        }
            
            self.services_cache = services
            self.last_update = time.time()
            return services
            
        except Exception as e:
            logger.error(f"Ошибка получения служб: {e}")
            return {"error": str(e)}
    
    def get_service_status(self, service_name: str) -> Dict[str, Any]:
        """Получить статус конкретной службы"""
        try:
            result = subprocess.run(
                f"systemctl status {service_name}",
                shell=True, capture_output=True, text=True
            )
            
            status_info = {
                "service_name": service_name,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "is_active": result.returncode == 0
            }
            
            # Парсим дополнительную информацию
            if result.stdout:
                lines = result.stdout.split('\n')
                for line in lines:
                    if "Active:" in line:
                        status_info["active_status"] = line.strip()
                    elif "Loaded:" in line:
                        status_info["loaded_status"] = line.strip()
                    elif "Main PID:" in line:
                        status_info["main_pid"] = line.strip()
            
            return status_info
            
        except Exception as e:
            logger.error(f"Ошибка получения статуса службы {service_name}: {e}")
            return {"error": str(e), "service_name": service_name}
    
    def start_service(self, service_name: str) -> Dict[str, Any]:
        """Запустить службу"""
        try:
            result = subprocess.run(
                f"sudo systemctl start {service_name}",
                shell=True, capture_output=True, text=True
            )
            
            return {
                "service_name": service_name,
                "action": "start",
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
            
        except Exception as e:
            logger.error(f"Ошибка запуска службы {service_name}: {e}")
            return {"error": str(e), "service_name": service_name}
    
    def stop_service(self, service_name: str) -> Dict[str, Any]:
        """Остановить службу"""
        try:
            result = subprocess.run(
                f"sudo systemctl stop {service_name}",
                shell=True, capture_output=True, text=True
            )
            
            return {
                "service_name": service_name,
                "action": "stop",
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
            
        except Exception as e:
            logger.error(f"Ошибка остановки службы {service_name}: {e}")
            return {"error": str(e), "service_name": service_name}
    
    def restart_service(self, service_name: str) -> Dict[str, Any]:
        """Перезапустить службу"""
        try:
            result = subprocess.run(
                f"sudo systemctl restart {service_name}",
                shell=True, capture_output=True, text=True
            )
            
            return {
                "service_name": service_name,
                "action": "restart",
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
            
        except Exception as e:
            logger.error(f"Ошибка перезапуска службы {service_name}: {e}")
            return {"error": str(e), "service_name": service_name}
    
    def enable_service(self, service_name: str) -> Dict[str, Any]:
        """Включить службу (автозапуск)"""
        try:
            result = subprocess.run(
                f"sudo systemctl enable {service_name}",
                shell=True, capture_output=True, text=True
            )
            
            return {
                "service_name": service_name,
                "action": "enable",
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
            
        except Exception as e:
            logger.error(f"Ошибка включения службы {service_name}: {e}")
            return {"error": str(e), "service_name": service_name}
    
    def disable_service(self, service_name: str) -> Dict[str, Any]:
        """Отключить службу (автозапуск)"""
        try:
            result = subprocess.run(
                f"sudo systemctl disable {service_name}",
                shell=True, capture_output=True, text=True
            )
            
            return {
                "service_name": service_name,
                "action": "disable",
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
            
        except Exception as e:
            logger.error(f"Ошибка отключения службы {service_name}: {e}")
            return {"error": str(e), "service_name": service_name}
    
    def get_service_logs(self, service_name: str, lines: int = 50) -> Dict[str, Any]:
        """Получить логи службы"""
        try:
            result = subprocess.run(
                f"sudo journalctl -u {service_name} -n {lines} --no-pager",
                shell=True, capture_output=True, text=True
            )
            
            return {
                "service_name": service_name,
                "lines": lines,
                "success": result.returncode == 0,
                "logs": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения логов службы {service_name}: {e}")
            return {"error": str(e), "service_name": service_name}
    
    def get_failed_services(self) -> List[Dict[str, Any]]:
        """Получить неудачные службы"""
        try:
            result = subprocess.run(
                "systemctl list-units --type=service --state=failed --no-pager",
                shell=True, capture_output=True, text=True
            )
            
            failed_services = []
            for line in result.stdout.split('\n'):
                if line.strip() and not line.startswith('UNIT'):
                    parts = line.split()
                    if len(parts) >= 4:
                        service_name = parts[0]
                        failed_services.append({
                            "service_name": service_name,
                            "load_state": parts[1],
                            "active_state": parts[2],
                            "sub_state": parts[3],
                            "description": ' '.join(parts[4:]) if len(parts) > 4 else ""
                        })
            
            return failed_services
            
        except Exception as e:
            logger.error(f"Ошибка получения неудачных служб: {e}")
            return []
    
    def get_running_services(self) -> List[Dict[str, Any]]:
        """Получить запущенные службы"""
        try:
            result = subprocess.run(
                "systemctl list-units --type=service --state=running --no-pager",
                shell=True, capture_output=True, text=True
            )
            
            running_services = []
            for line in result.stdout.split('\n'):
                if line.strip() and not line.startswith('UNIT'):
                    parts = line.split()
                    if len(parts) >= 4:
                        service_name = parts[0]
                        running_services.append({
                            "service_name": service_name,
                            "load_state": parts[1],
                            "active_state": parts[2],
                            "sub_state": parts[3],
                            "description": ' '.join(parts[4:]) if len(parts) > 4 else ""
                        })
            
            return running_services
            
        except Exception as e:
            logger.error(f"Ошибка получения запущенных служб: {e}")
            return []
    
    def get_enabled_services(self) -> List[str]:
        """Получить включенные службы"""
        try:
            result = subprocess.run(
                "systemctl list-unit-files --type=service --state=enabled --no-pager",
                shell=True, capture_output=True, text=True
            )
            
            enabled_services = []
            for line in result.stdout.split('\n'):
                if line.strip() and not line.startswith('UNIT'):
                    parts = line.split()
                    if len(parts) >= 2:
                        service_name = parts[0]
                        enabled_services.append(service_name)
            
            return enabled_services
            
        except Exception as e:
            logger.error(f"Ошибка получения включенных служб: {e}")
            return []
    
    def create_service_file(self, service_name: str, service_config: Dict[str, Any]) -> Dict[str, Any]:
        """Создать файл службы"""
        try:
            service_content = f"""[Unit]
Description={service_config.get('description', 'ARK Service')}
After=network.target

[Service]
Type={service_config.get('type', 'simple')}
ExecStart={service_config.get('exec_start', '')}
User={service_config.get('user', 'root')}
Restart={service_config.get('restart', 'always')}
RestartSec={service_config.get('restart_sec', '5')}

[Install]
WantedBy=multi-user.target
"""
            
            service_file_path = f"/etc/systemd/system/{service_name}.service"
            
            # Создаем временный файл
            temp_file = f"/tmp/{service_name}.service"
            with open(temp_file, 'w') as f:
                f.write(service_content)
            
            # Копируем в systemd директорию
            result = subprocess.run(
                f"sudo cp {temp_file} {service_file_path}",
                shell=True, capture_output=True, text=True
            )
            
            if result.returncode == 0:
                # Перезагружаем systemd
                reload_result = subprocess.run(
                    "sudo systemctl daemon-reload",
                    shell=True, capture_output=True, text=True
                )
                
                return {
                    "service_name": service_name,
                    "action": "create",
                    "success": True,
                    "file_path": service_file_path,
                    "reload_success": reload_result.returncode == 0
                }
            else:
                return {
                    "service_name": service_name,
                    "action": "create",
                    "success": False,
                    "error": result.stderr
                }
                
        except Exception as e:
            logger.error(f"Ошибка создания службы {service_name}: {e}")
            return {"error": str(e), "service_name": service_name}
    
    def delete_service_file(self, service_name: str) -> Dict[str, Any]:
        """Удалить файл службы"""
        try:
            service_file_path = f"/etc/systemd/system/{service_name}.service"
            
            # Останавливаем службу если запущена
            stop_result = self.stop_service(service_name)
            
            # Удаляем файл
            result = subprocess.run(
                f"sudo rm -f {service_file_path}",
                shell=True, capture_output=True, text=True
            )
            
            if result.returncode == 0:
                # Перезагружаем systemd
                reload_result = subprocess.run(
                    "sudo systemctl daemon-reload",
                    shell=True, capture_output=True, text=True
                )
                
                return {
                    "service_name": service_name,
                    "action": "delete",
                    "success": True,
                    "stop_success": stop_result.get("success", False),
                    "reload_success": reload_result.returncode == 0
                }
            else:
                return {
                    "service_name": service_name,
                    "action": "delete",
                    "success": False,
                    "error": result.stderr
                }
                
        except Exception as e:
            logger.error(f"Ошибка удаления службы {service_name}: {e}")
            return {"error": str(e), "service_name": service_name}
    
    def get_system_status(self) -> Dict[str, Any]:
        """Получить общий статус системы"""
        try:
            return {
                "total_services": len(self.get_all_services()),
                "running_services": len(self.get_running_services()),
                "failed_services": len(self.get_failed_services()),
                "enabled_services": len(self.get_enabled_services()),
                "system_uptime": self._get_system_uptime(),
                "boot_time": self._get_boot_time()
            }
        except Exception as e:
            logger.error(f"Ошибка получения статуса системы: {e}")
            return {"error": str(e)}
    
    def _get_system_uptime(self) -> str:
        """Получить время работы системы"""
        try:
            result = subprocess.run(
                "uptime -p",
                shell=True, capture_output=True, text=True
            )
            return result.stdout.strip()
        except Exception as e:
            logger.error(f"Ошибка получения времени работы: {e}")
            return "Недоступно"
    
    def _get_boot_time(self) -> str:
        """Получить время загрузки"""
        try:
            result = subprocess.run(
                "who -b",
                shell=True, capture_output=True, text=True
            )
            return result.stdout.strip()
        except Exception as e:
            logger.error(f"Ошибка получения времени загрузки: {e}")
            return "Недоступно"

# Создание глобального экземпляра
systemd_integration = SystemDIntegration()

if __name__ == "__main__":
    # Тестирование интеграции
    integration = SystemDIntegration()
    
    print("🧠 ARK SystemD Integration Test")
    print("=" * 50)
    
    # Тест получения всех служб
    print("📊 Получение всех служб...")
    services = integration.get_all_services()
    print(f"✅ Найдено служб: {len(services)}")
    
    # Тест получения статуса системы
    print("📈 Получение статуса системы...")
    status = integration.get_system_status()
    print(f"✅ Статус получен: {status}")
    
    # Тест получения неудачных служб
    print("❌ Получение неудачных служб...")
    failed = integration.get_failed_services()
    print(f"✅ Неудачных служб: {len(failed)}")
    
    # Тест получения запущенных служб
    print("✅ Получение запущенных служб...")
    running = integration.get_running_services()
    print(f"✅ Запущенных служб: {len(running)}")
    
    print("🎉 Тестирование завершено!") 