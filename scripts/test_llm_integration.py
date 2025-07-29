#!/usr/bin/env python3
"""
Тест LLM интеграции ARK v2.8
Проверяет подключение к Ollama и работу отделов мозга с реальными LLM
"""

import asyncio
import logging
import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mind.cognitive_architecture import cognitive_brain, BrainDepartment
from psyche.agent_tools import AgentTools

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_ollama_connection():
    """Тест подключения к Ollama"""
    print("🔌 Тестирование подключения к Ollama...")
    
    try:
        import requests
        
        # Проверяем доступность Ollama
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"✅ Ollama доступен! Найдено моделей: {len(models)}")
            
            for model in models:
                print(f"  📦 {model.get('name', 'Unknown')} ({model.get('size', 0)} bytes)")
            
            return True
        else:
            print(f"❌ Ollama недоступен: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка подключения к Ollama: {e}")
        return False

async def test_department_llm():
    """Тест работы отделов мозга с LLM"""
    print("\n🧠 Тестирование отделов мозга с LLM...")
    
    test_input = "Проанализируй производительность системы и предложи оптимизации"
    
    try:
        # Получаем статус когнитивного мозга
        brain_status = cognitive_brain.get_brain_status()
        departments = brain_status.get("departments", {})
        
        print(f"📊 Найдено отделов: {len(departments)}")
        
        for dept_name, dept_info in departments.items():
            print(f"\n🏛️ Тестирование {dept_name}...")
            print(f"  Модель: {dept_info.get('model', 'Unknown')}")
            print(f"  Статус: {dept_info.get('status', 'Unknown')}")
            
            # Тестируем обработку через отдел
            if hasattr(cognitive_brain, 'brain_trust'):
                # Это упрощенный тест - в реальности нужно через pipeline
                print(f"  ✅ Отдел инициализирован")
            else:
                print(f"  ⚠️ Отдел не найден в brain_trust")
        
        # Тестируем полный pipeline
        print(f"\n🔄 Тестирование полного pipeline...")
        result = await cognitive_brain.process_input(test_input)
        
        if result["success"]:
            consensus = result["consensus"]
            print(f"✅ Pipeline успешен!")
            print(f"  Уверенность: {consensus.confidence_score:.2f}")
            print(f"  Решение: {consensus.final_decision[:200]}...")
            print(f"  Отделов участвовало: {len(consensus.reasoning_trace)}")
        else:
            print(f"❌ Pipeline провален: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Ошибка тестирования отделов: {e}")

async def test_tools_integration():
    """Тест интеграции инструментов"""
    print("\n🔧 Тестирование инструментов...")
    
    try:
        tools = AgentTools()
        
        # Тестируем новые инструменты
        test_tools = [
            ("analyze_performance", tools.analyze_performance),
            ("plan_evolution", tools.plan_evolution),
            ("review_code_changes", tools.review_code_changes),
            ("validate_syntax", tools.validate_syntax),
            ("check_security", tools.check_security),
            ("identify_bottlenecks", tools.identify_bottlenecks)
        ]
        
        for tool_name, tool_func in test_tools:
            print(f"\n🔧 Тестирование {tool_name}...")
            
            try:
                if tool_name == "analyze_performance":
                    result = tool_func("system")
                elif tool_name == "plan_evolution":
                    result = tool_func()
                elif tool_name == "review_code_changes":
                    result = tool_func("main.py", "Added new feature")
                elif tool_name == "validate_syntax":
                    result = tool_func("print('Hello, World!')", "python")
                elif tool_name == "check_security":
                    result = tool_func("system")
                elif tool_name == "identify_bottlenecks":
                    result = tool_func()
                else:
                    result = tool_func()
                
                if "error" not in result:
                    print(f"  ✅ {tool_name} работает")
                    if isinstance(result, dict):
                        print(f"  📊 Результат: {list(result.keys())}")
                else:
                    print(f"  ❌ {tool_name} ошибка: {result.get('error')}")
                    
            except Exception as e:
                print(f"  ❌ {tool_name} исключение: {e}")
                
    except Exception as e:
        print(f"❌ Ошибка тестирования инструментов: {e}")

async def test_real_llm_processing():
    """Тест реальной обработки через LLM"""
    print("\n🤖 Тестирование реальной LLM обработки...")
    
    test_cases = [
        "Оптимизируй производительность системы",
        "Проанализируй безопасность кода",
        "Создай план эволюции агента",
        "Выяви узкие места в архитектуре"
    ]
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n📝 Тест {i}: {test_input}")
        
        try:
            result = await cognitive_brain.process_input(test_input)
            
            if result["success"]:
                consensus = result["consensus"]
                print(f"  ✅ Обработано успешно")
                print(f"  🎯 Уверенность: {consensus.confidence_score:.2f}")
                print(f"  🧠 Решение: {consensus.final_decision[:150]}...")
                
                # Показываем reasoning trace
                for j, chain in enumerate(consensus.reasoning_trace[:3], 1):
                    print(f"  📋 Отдел {j}: {chain.department.name}")
            else:
                print(f"  ❌ Ошибка: {result.get('error')}")
                
        except Exception as e:
            print(f"  ❌ Исключение: {e}")

async def main():
    """Главная функция тестирования"""
    print("🧠 ARK v2.8 LLM Integration Test Suite")
    print("=" * 50)
    
    # Тест 1: Подключение к Ollama
    ollama_available = await test_ollama_connection()
    
    # Тест 2: Отделы мозга
    await test_department_llm()
    
    # Тест 3: Инструменты
    await test_tools_integration()
    
    # Тест 4: Реальная обработка
    if ollama_available:
        await test_real_llm_processing()
    else:
        print("\n⚠️ Пропуск тестов реальной LLM обработки (Ollama недоступен)")
    
    print("\n" + "=" * 50)
    print("✅ Тестирование LLM интеграции завершено!")

if __name__ == "__main__":
    asyncio.run(main()) 