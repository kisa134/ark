#!/usr/bin/env python3
"""
Тест новой архитектуры сознания
Проверяет работу MotivationalEngine и ConsciousnessCore
"""

import asyncio
import logging
import time
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Добавляем путь к проекту
import sys
sys.path.insert(0, '.')

from mind.motivational_engine import MotivationalEngine, Desire, DesireType
from mind.consciousness_core import ConsciousnessCore


async def test_motivational_engine():
    """Тестирует MotivationalEngine"""
    print("🧠 Тестирование MotivationalEngine")
    print("=" * 50)
    
    engine = MotivationalEngine()
    
    # Тест 1: Генерация желаний
    print("\n📝 Тест 1: Генерация желаний")
    
    # Симулируем разные состояния системы
    test_states = [
        {"temperature": 75, "cpu_usage": 60, "memory_usage": 70},  # Нормальное состояние
        {"temperature": 85, "cpu_usage": 95, "memory_usage": 90},  # Критическое состояние
        {"temperature": 45, "cpu_usage": 30, "memory_usage": 40}   # Идеальное состояние
    ]
    
    for i, state in enumerate(test_states, 1):
        print(f"\n  Состояние {i}: {state}")
        desires = engine.generate_desires(state, {"recent": []})
        
        print(f"  Сгенерировано желаний: {len(desires)}")
        for j, desire in enumerate(desires[:3], 1):
            print(f"    {j}. {desire.name} (вес: {desire.weight:.2f}, срочность: {desire.urgency:.2f})")
    
    # Тест 2: Обновление характера
    print("\n📝 Тест 2: Обновление характера")
    
    outcomes = [
        {"success": True, "type": "learning"},
        {"success": False, "type": "social"},
        {"success": True, "type": "maintenance"}
    ]
    
    for outcome in outcomes:
        print(f"  Исход: {outcome}")
        engine.update_character_traits(outcome)
        print(f"  Характер: {engine.character_traits}")
    
    # Тест 3: Сводка характера
    print("\n📝 Тест 3: Сводка характера")
    summary = engine.get_character_summary()
    print(f"  Тип личности: {summary['personality_type']}")
    print(f"  Доминирующая черта: {summary['dominant_trait']}")
    print(f"  Черты характера: {summary['traits']}")


async def test_consciousness_core():
    """Тестирует ConsciousnessCore"""
    print("\n🧠 Тестирование ConsciousnessCore")
    print("=" * 50)
    
    core = ConsciousnessCore()
    
    # Тест 1: Цикл сознания
    print("\n📝 Тест 1: Цикл сознания")
    
    for cycle in range(5):
        print(f"\n  Цикл {cycle + 1}:")
        result = await core.consciousness_cycle_step()
        
        print(f"    Цикл: {result['cycle']}")
        if 'primary_desire' in result:
            print(f"    Главное желание: {result['primary_desire']}")
            print(f"    Решение: {result['decision']}")
            print(f"    Успех: {result['outcome']['success']}")
        else:
            print(f"    Статус: {result['status']}")
    
    # Тест 2: Статус сознания
    print("\n📝 Тест 2: Статус сознания")
    status = core.get_consciousness_status()
    print(f"  Циклов: {status['cycle']}")
    print(f"  Текущие желания: {status['current_desires']}")
    print(f"  Мыслей: {status['recent_thoughts']}")
    print(f"  Решений: {status['recent_decisions']}")
    print(f"  Размер памяти: {status['memory_size']}")
    
    # Тест 3: Мысли и решения
    print("\n📝 Тест 3: Мысли и решения")
    
    thoughts = core.get_thoughts_summary()
    print(f"  Последние мысли ({len(thoughts)}):")
    for thought in thoughts[-3:]:
        print(f"    - {thought['content'][:50]}... ({thought['type']})")
    
    decisions = core.get_decisions_summary()
    print(f"  Последние решения ({len(decisions)}):")
    for decision in decisions[-3:]:
        print(f"    - {decision['action']} (уверенность: {decision['confidence']:.2f})")


async def test_consciousness_cycle():
    """Тестирует полный цикл сознания"""
    print("\n🧠 Тестирование полного цикла сознания")
    print("=" * 50)
    
    core = ConsciousnessCore()
    
    print("Запуск 10 циклов сознания...")
    
    for cycle in range(10):
        result = await core.consciousness_cycle_step()
        
        print(f"\n🔄 Цикл {cycle + 1}:")
        if 'primary_desire' in result:
            print(f"  🎯 Желание: {result['primary_desire']}")
            print(f"  ⚡ Действие: {result['decision']}")
            print(f"  ✅ Результат: {'Успех' if result['outcome']['success'] else 'Неудача'}")
            
            # Показываем характер
            traits = result['character_traits']
            dominant = max(traits.items(), key=lambda x: x[1])
            print(f"  🧠 Характер: {dominant[0]} ({dominant[1]:.2f})")
        else:
            print(f"  😴 Нет активных желаний")
        
        # Пауза между циклами
        await asyncio.sleep(1)
    
    # Финальная сводка
    print("\n📊 Финальная сводка:")
    status = core.get_consciousness_status()
    character = status['character']
    
    print(f"  Всего циклов: {status['cycle']}")
    print(f"  Тип личности: {character['personality_type']}")
    print(f"  Доминирующая черта: {character['dominant_trait']}")
    print(f"  Всего мыслей: {status['recent_thoughts']}")
    print(f"  Всего решений: {status['recent_decisions']}")


async def main():
    """Основная функция тестирования"""
    print("🧠 Тестирование новой архитектуры сознания")
    print("=" * 60)
    
    try:
        # Тест MotivationalEngine
        await test_motivational_engine()
        
        # Тест ConsciousnessCore
        await test_consciousness_core()
        
        # Тест полного цикла
        await test_consciousness_cycle()
        
        print("\n✅ Все тесты завершены успешно!")
        
    except Exception as e:
        print(f"\n❌ Ошибка в тестах: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 