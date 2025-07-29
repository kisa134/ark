#!/usr/bin/env python3
"""
Тест исправлений в когнитивной архитектуре
"""

import asyncio
import sys
from pathlib import Path

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from mind.cognitive_architecture import EmotionEngine, Dispatcher, ReasoningTask
from datetime import datetime


async def test_emotion_engine():
    """Тест исправлений в EmotionEngine"""
    print("🧠 Тестирование EmotionEngine...")
    
    emotion_engine = EmotionEngine()
    
    # Тест 1: Проверка get_emotional_state без ошибок
    try:
        state = emotion_engine.get_emotional_state()
        print(f"  ✅ get_emotional_state работает: {state}")
    except Exception as e:
        print(f"  ❌ Ошибка в get_emotional_state: {e}")
        return False
    
    # Тест 2: Проверка _calculate_stability с пустыми данными
    try:
        stability = emotion_engine._calculate_stability()
        print(f"  ✅ _calculate_stability работает: {stability}")
    except Exception as e:
        print(f"  ❌ Ошибка в _calculate_stability: {e}")
        return False
    
    # Тест 3: Добавление тестовых данных
    try:
        emotion_engine.recent_triggers = [
            {"dominant_emotion": "joy", "timestamp": datetime.now()},
            {"dominant_emotion": "trust", "timestamp": datetime.now()},
            {"dominant_emotion": "joy", "timestamp": datetime.now()}
        ]
        stability = emotion_engine._calculate_stability()
        print(f"  ✅ _calculate_stability с данными: {stability}")
    except Exception as e:
        print(f"  ❌ Ошибка в _calculate_stability с данными: {e}")
        return False
    
    return True


def test_dispatcher():
    """Тест исправлений в Dispatcher"""
    print("🚦 Тестирование Dispatcher...")
    
    dispatcher = Dispatcher()
    
    # Тест 1: Создание задачи
    try:
        task = {"type": "reasoning", "data": "test"}
        task_id = dispatcher.schedule_reasoning(task, 1)
        print(f"  ✅ Задача создана: {task_id}")
    except Exception as e:
        print(f"  ❌ Ошибка создания задачи: {e}")
        return False
    
    # Тест 2: Получение задачи
    try:
        next_task = dispatcher.get_next_task()
        if next_task:
            print(f"  ✅ Задача получена: {next_task.task_id}")
        else:
            print("  ⚠️ Очередь пуста")
    except Exception as e:
        print(f"  ❌ Ошибка получения задачи: {e}")
        return False
    
    # Тест 3: Статус диспетчера
    try:
        status = dispatcher.get_dispatcher_status()
        print(f"  ✅ Статус диспетчера: {status}")
    except Exception as e:
        print(f"  ❌ Ошибка получения статуса: {e}")
        return False
    
    return True


def test_reasoning_task():
    """Тест класса ReasoningTask"""
    print("📋 Тестирование ReasoningTask...")
    
    # Тест 1: Создание задачи
    try:
        task1 = ReasoningTask(priority=1, task_id="task1", task_data={"test": "data1"})
        task2 = ReasoningTask(priority=2, task_id="task2", task_data={"test": "data2"})
        print(f"  ✅ Задачи созданы: {task1.task_id}, {task2.task_id}")
    except Exception as e:
        print(f"  ❌ Ошибка создания задач: {e}")
        return False
    
    # Тест 2: Сравнение задач
    try:
        result = task1 < task2  # task1 имеет более высокий приоритет
        print(f"  ✅ Сравнение задач: task1 < task2 = {result}")
    except Exception as e:
        print(f"  ❌ Ошибка сравнения задач: {e}")
        return False
    
    return True


async def main():
    """Основная функция тестирования"""
    print("🔧 Тестирование исправлений в когнитивной архитектуре")
    print("=" * 60)
    
    # Тест EmotionEngine
    emotion_success = await test_emotion_engine()
    
    # Тест Dispatcher
    dispatcher_success = test_dispatcher()
    
    # Тест ReasoningTask
    reasoning_success = test_reasoning_task()
    
    print("\n" + "=" * 60)
    print("📊 Результаты тестирования:")
    print(f"  EmotionEngine: {'✅ Успешно' if emotion_success else '❌ Ошибка'}")
    print(f"  Dispatcher: {'✅ Успешно' if dispatcher_success else '❌ Ошибка'}")
    print(f"  ReasoningTask: {'✅ Успешно' if reasoning_success else '❌ Ошибка'}")
    
    if emotion_success and dispatcher_success and reasoning_success:
        print("\n🎉 Все тесты прошли успешно!")
        return True
    else:
        print("\n⚠️ Некоторые тесты не прошли")
        return False


if __name__ == "__main__":
    asyncio.run(main()) 