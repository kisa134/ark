"""
Модуль "Тело" - низкоуровневое воплощение в Linux
Реализует гомеостаз, цифровой метаболизм и прямое взаимодействие с системой
"""

from .sensors import Sensorium
from .actuators import Actuator
from .metabolism import DigitalMetabolism

__all__ = ["Sensorium", "Actuator", "DigitalMetabolism"] 