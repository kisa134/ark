#!/usr/bin/env python3
"""
Монитор эволюции "Ковчега" - Внешний сторожевой процесс
Отслеживает запросы на перезапуск и управляет автономной эволюцией
"""

import os
import time
import signal
import subprocess
import logging
from pathlib import Path
from typing import Optional

class ArkEvolutionMonitor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.restart_flag_path = Path("temp/restart_requested.flag")
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        
        # Настройка логирования
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/evolution_monitor.log'),
                logging.StreamHandler()
            ]
        )
    
    def check_restart_request(self) -> bool:
        """Проверяет наличие запроса на перезапуск"""
        return self.restart_flag_path.exists()
    
    def handle_restart_request(self):
        """Обрабатывает запрос на перезапуск"""
        try:
            # Чтение причины перезапуска
            with open(self.restart_flag_path, 'r') as f:
                restart_info = f.read()
            
            self.logger.info(f"Обнаружен запрос на перезапуск: {restart_info}")
            
            # Создание резервной копии текущего состояния
            timestamp = int(time.time())
            backup_name = f"ark_backup_{timestamp}"
            backup_path = self.backup_dir / backup_name
            
            # Копирование текущего состояния
            import shutil
            shutil.copytree(".", backup_path, ignore=shutil.ignore_patterns(
                "logs/*", "temp/*", "backups/*", "__pycache__/*", "*.pyc"
            ))
            
            self.logger.info(f"Создана резервная копия: {backup_path}")
            
            # Удаление флага перезапуска
            self.restart_flag_path.unlink()
            
            # Перезапуск контейнера
            self.restart_container()
            
        except Exception as e:
            self.logger.error(f"Ошибка при обработке запроса на перезапуск: {e}")
    
    def restart_container(self):
        """Перезапускает контейнер 'Ковчега'"""
        try:
            self.logger.info("Инициирование перезапуска контейнера...")
            
            # Команда для перезапуска через docker-compose
            cmd = ["docker-compose", "restart", "ark"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("Контейнер успешно перезапущен")
            else:
                self.logger.error(f"Ошибка перезапуска контейнера: {result.stderr}")
                
        except Exception as e:
            self.logger.error(f"Ошибка при перезапуске контейнера: {e}")
    
    def monitor_evolution(self):
        """Основной цикл мониторинга эволюции"""
        self.logger.info("Монитор эволюции 'Ковчега' запущен")
        
        while True:
            try:
                # Проверка запроса на перезапуск
                if self.check_restart_request():
                    self.handle_restart_request()
                
                # Проверка состояния контейнера
                self.check_container_health()
                
                # Пауза между проверками
                time.sleep(5)
                
            except KeyboardInterrupt:
                self.logger.info("Монитор эволюции остановлен пользователем")
                break
            except Exception as e:
                self.logger.error(f"Ошибка в цикле мониторинга: {e}")
                time.sleep(10)
    
    def check_container_health(self):
        """Проверяет состояние контейнера"""
        try:
            cmd = ["docker-compose", "ps", "ark"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                if "Up" in result.stdout:
                    self.logger.debug("Контейнер 'Ковчег' работает нормально")
                else:
                    self.logger.warning("Контейнер 'Ковчег' не работает")
                    self.restart_container()
            else:
                self.logger.error(f"Ошибка проверки состояния контейнера: {result.stderr}")
                
        except Exception as e:
            self.logger.error(f"Ошибка при проверке состояния контейнера: {e}")

def main():
    """Главная функция"""
    monitor = ArkEvolutionMonitor()
    
    # Обработка сигналов для graceful shutdown
    def signal_handler(signum, frame):
        monitor.logger.info("Получен сигнал завершения, останавливаем монитор...")
        exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Запуск мониторинга
    monitor.monitor_evolution()

if __name__ == "__main__":
    main() 