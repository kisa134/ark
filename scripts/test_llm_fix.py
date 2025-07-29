#!/usr/bin/env python3
"""
Быстрый тест исправления LLM проблем
"""

import asyncio
import sys
from pathlib import Path

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from mind.cognitive_architecture import BrainDepartmentAgent, DepartmentConfig, BrainDepartment


async def test_llm_fix():
    """Тест исправления LLM проблем"""
    print("🔧 Тестирование исправления LLM проблем")
    print("=" * 50)
    
    # Тестируем каждый отдел с исправленными моделями
    test_configs = [
        {
            "name": "Architect Department",
            "role": BrainDepartment.ARCHITECT,
            "model": "llama3:8b"
        },
        {
            "name": "Engineer Department", 
            "role": BrainDepartment.ENGINEER,
            "model": "deepseek-coder-v2:latest"
        },
        {
            "name": "Critic Department",
            "role": BrainDepartment.CRITIC,
            "model": "llama3:8b"
        },
        {
            "name": "Memory Keeper Department",
            "role": BrainDepartment.MEMORY_KEEPER,
            "model": "llama3:8b"
        },
        {
            "name": "Documentor Department",
            "role": BrainDepartment.DOCUMENTOR,
            "model": "llama3:8b"
        },
        {
            "name": "Meta Observer Department",
            "role": BrainDepartment.META_OBSERVER,
            "model": "llama3:8b"
        }
    ]
    
    for config_data in test_configs:
        print(f"\n🧠 Тестирование {config_data['name']}...")
        
        try:
            config = DepartmentConfig(
                name=config_data["name"],
                role=config_data["role"],
                description="Test department",
                system_prompt="You are a test department. Respond briefly.",
                model_name=config_data["model"]
            )
            
            agent = BrainDepartmentAgent(config)
            
            # Тестируем генерацию
            result = await agent.process_input("Hello, test message")
            
            if result and hasattr(result, 'output'):
                print(f"  ✅ Успешно: {result.output[:100]}...")
                print(f"  📊 Уверенность: {result.confidence:.2f}")
            else:
                print(f"  ❌ Ошибка: Нет результата")
                
        except Exception as e:
            print(f"  ❌ Ошибка: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Тестирование завершено!")


if __name__ == "__main__":
    asyncio.run(test_llm_fix()) 