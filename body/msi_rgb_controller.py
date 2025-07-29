#!/usr/bin/env python3
"""
MSI MYSTIC LIGHT RGB Controller
Управление RGB подсветкой MSI материнской платы
"""

import usb.core
import usb.util
import logging
from typing import Dict, List, Tuple, Optional
from enum import Enum

class RGBMode(Enum):
    STATIC = "static"
    BREATHING = "breathing"
    RAINBOW = "rainbow"
    OFF = "off"

class MSIRGBController:
    """Контроллер RGB подсветки MSI MYSTIC LIGHT"""
    
    # MSI MYSTIC LIGHT USB ID
    VENDOR_ID = 0x0db0
    PRODUCT_ID = 0x0076
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.device = None
        self.current_color = [0, 0, 0]
        self.current_mode = RGBMode.STATIC
        self.is_connected = False
        
        # Попытка подключения к устройству
        self._connect()
    
    def _connect(self) -> bool:
        """Подключение к MSI RGB устройству"""
        try:
            # Поиск устройства
            self.device = usb.core.find(idVendor=self.VENDOR_ID, idProduct=self.PRODUCT_ID)
            
            if self.device is None:
                self.logger.warning("MSI MYSTIC LIGHT устройство не найдено")
                return False
            
            # Сброс устройства
            self.device.reset()
            
            # Установка конфигурации
            self.device.set_configuration()
            
            # Получение интерфейса
            cfg = self.device.get_active_configuration()
            intf = cfg[(0, 0)]
            
            # Получение endpoint'ов
            self.ep_out = usb.util.find_descriptor(
                intf,
                custom_match=lambda e: 
                    usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT
            )
            
            self.ep_in = usb.util.find_descriptor(
                intf,
                custom_match=lambda e: 
                    usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN
            )
            
            if self.ep_out is None or self.ep_in is None:
                self.logger.error("Не удалось найти USB endpoints")
                return False
            
            self.is_connected = True
            self.logger.info("MSI MYSTIC LIGHT подключен успешно")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка подключения к MSI RGB: {e}")
            return False
    
    def _send_command(self, command: bytes) -> bool:
        """Отправка команды на устройство"""
        if not self.is_connected or self.device is None:
            return False
        
        try:
            self.device.write(self.ep_out.bEndpointAddress, command)
            return True
        except Exception as e:
            self.logger.error(f"Ошибка отправки команды: {e}")
            return False
    
    def set_color(self, r: int, g: int, b: int, mode: RGBMode = RGBMode.STATIC) -> bool:
        """Установка цвета RGB"""
        if not self.is_connected:
            self.logger.warning("Устройство не подключено")
            return False
        
        try:
            # Нормализация значений (0-255)
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            
            # Формирование команды для MSI MYSTIC LIGHT
            # Это примерная структура команды - может потребоваться настройка
            command = bytes([
                0x01,  # Заголовок команды
                0x02,  # Команда установки цвета
                r, g, b,  # RGB значения
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  # Дополнительные байты
                0xFF   # Завершающий байт
            ])
            
            success = self._send_command(command)
            if success:
                self.current_color = [r, g, b]
                self.current_mode = mode
                self.logger.info(f"Цвет установлен: RGB({r}, {g}, {b}) - {mode.value}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Ошибка установки цвета: {e}")
            return False
    
    def set_color_by_name(self, color_name: str, mode: RGBMode = RGBMode.STATIC) -> bool:
        """Установка цвета по имени"""
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
        
        if color_name.lower() in color_map:
            r, g, b = color_map[color_name.lower()]
            return self.set_color(r, g, b, mode)
        else:
            self.logger.warning(f"Неизвестный цвет: {color_name}")
            return False
    
    def get_status(self) -> Dict:
        """Получение статуса устройства"""
        return {
            "connected": self.is_connected,
            "device_name": "MSI MYSTIC LIGHT",
            "vendor_id": self.VENDOR_ID,
            "product_id": self.PRODUCT_ID,
            "current_color": self.current_color,
            "current_mode": self.current_mode.value,
            "device_info": {
                "manufacturer": "MSI",
                "product": "MYSTIC LIGHT",
                "serial": "7E2523022001" if self.is_connected else None
            }
        }
    
    def test_connection(self) -> bool:
        """Тест подключения к устройству"""
        if not self.is_connected:
            return False
        
        try:
            # Попытка чтения дескриптора устройства
            manufacturer = usb.util.get_string(self.device, self.device.iManufacturer)
            product = usb.util.get_string(self.device, self.device.iProduct)
            
            self.logger.info(f"Подключено к: {manufacturer} {product}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка тестирования подключения: {e}")
            return False
    
    def disconnect(self):
        """Отключение от устройства"""
        if self.device is not None:
            usb.util.dispose_resources(self.device)
            self.device = None
        
        self.is_connected = False
        self.logger.info("Отключено от MSI RGB устройства")

# Глобальный экземпляр контроллера
msi_rgb_controller = MSIRGBController()

def test_msi_rgb():
    """Тест MSI RGB контроллера"""
    controller = MSIRGBController()
    
    print("🔍 Тестирование MSI RGB контроллера...")
    
    # Проверка подключения
    if not controller.is_connected:
        print("❌ MSI RGB устройство не найдено")
        return False
    
    print("✅ MSI RGB устройство найдено")
    
    # Тест подключения
    if controller.test_connection():
        print("✅ Подключение к устройству успешно")
    else:
        print("❌ Ошибка подключения к устройству")
        return False
    
    # Тест установки цветов
    test_colors = [
        ("red", [255, 0, 0]),
        ("green", [0, 255, 0]),
        ("blue", [0, 0, 255]),
        ("yellow", [255, 255, 0])
    ]
    
    for color_name, rgb in test_colors:
        print(f"🎨 Тестирование цвета {color_name}...")
        if controller.set_color(*rgb):
            print(f"✅ Цвет {color_name} установлен")
        else:
            print(f"❌ Ошибка установки цвета {color_name}")
    
    # Получение статуса
    status = controller.get_status()
    print(f"📊 Статус: {status}")
    
    controller.disconnect()
    return True

if __name__ == "__main__":
    test_msi_rgb() 