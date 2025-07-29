"""
Модуль "Личность" - эмоционально-социальное ядро
Реализует EmotionalProcessingCore, мультиагентные ансамбли и инструменты
"""

from .emotional_core import EmotionalProcessingCore
from .crew import CrewManager
from .agent_tools import AgentTools

__all__ = ["EmotionalProcessingCore", "CrewManager", "AgentTools"] 