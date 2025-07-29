#!/usr/bin/env python3
"""
Тестирование веб-интерфейса ARK
"""

import requests
import json
import time
import sys
from pathlib import Path

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_api_endpoints():
    """Тестирование всех API endpoints"""
    base_url = "http://localhost:8000"
    
    print("🔍 Тестирование API endpoints...")
    
    # Тест 1: Основной статус
    try:
        response = requests.get(f"{base_url}/api/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ /api/status: {data.get('status', 'unknown')}")
            print(f"   Сознание: {data.get('consciousness_state', 'unknown')}")
            print(f"   Эмоция: {data.get('emotion_state', 'unknown')}")
        else:
            print(f"❌ /api/status: {response.status_code}")
    except Exception as e:
        print(f"❌ /api/status: {e}")
    
    # Тест 2: Статус мозга
    try:
        response = requests.get(f"{base_url}/api/brain/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ /api/brain/status: {data.get('status', 'unknown')}")
        else:
            print(f"❌ /api/brain/status: {response.status_code}")
    except Exception as e:
        print(f"❌ /api/brain/status: {e}")
    
    # Тест 3: Статус эволюции
    try:
        response = requests.get(f"{base_url}/api/evolution_status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ /api/evolution_status: {data.get('status', 'unknown')}")
        else:
            print(f"❌ /api/evolution_status: {response.status_code}")
    except Exception as e:
        print(f"❌ /api/evolution_status: {e}")
    
    # Тест 4: Статус инструментов
    try:
        response = requests.get(f"{base_url}/api/tools_status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ /api/tools_status: {len(data.get('tools', []))} инструментов")
        else:
            print(f"❌ /api/tools_status: {response.status_code}")
    except Exception as e:
        print(f"❌ /api/tools_status: {e}")

def test_chat_functionality():
    """Тестирование функциональности чата"""
    base_url = "http://localhost:8000"
    
    print("\n💬 Тестирование чата...")
    
    # Тест отправки сообщения через WebSocket
    try:
        import websockets
        import asyncio
        
        async def test_websocket():
            try:
                uri = "ws://localhost:8000/ws"
                async with websockets.connect(uri) as websocket:
                    # Отправляем тестовое сообщение
                    message = {
                        "type": "user_message",
                        "text": "Привет! Как дела?",
                        "user_id": "test_user"
                    }
                    await websocket.send(json.dumps(message))
                    
                    # Ждем ответ
                    response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    data = json.loads(response)
                    print(f"✅ WebSocket чат работает: {data.get('type', 'unknown')}")
                    
            except Exception as e:
                print(f"❌ WebSocket чат: {e}")
        
        asyncio.run(test_websocket())
        
    except ImportError:
        print("⚠️  websockets не установлен, пропускаем WebSocket тест")
    except Exception as e:
        print(f"❌ WebSocket тест: {e}")

def test_html_interface():
    """Тестирование HTML интерфейса"""
    base_url = "http://localhost:8000"
    
    print("\n🌐 Тестирование HTML интерфейса...")
    
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            html = response.text
            if "ARK v2.8" in html:
                print("✅ HTML интерфейс загружается")
            else:
                print("⚠️  HTML загружается, но не содержит ожидаемого контента")
        else:
            print(f"❌ HTML интерфейс: {response.status_code}")
    except Exception as e:
        print(f"❌ HTML интерфейс: {e}")

def test_agent_communication():
    """Тестирование общения с агентом"""
    print("\n🤖 Тестирование общения с агентом...")
    
    try:
        from mind.cognitive_architecture import cognitive_brain
        
        # Тестируем обработку сообщения
        test_message = "Привет! Расскажи о себе"
        print(f"📝 Отправляем: {test_message}")
        
        # Обрабатываем через когнитивную архитектуру
        result = cognitive_brain.process_user_input(test_message)
        
        if result:
            print(f"✅ Агент ответил: {result.get('confidence', 0):.2f} уверенности")
            print(f"   Решение: {result.get('decision', 'Нет решения')[:100]}...")
        else:
            print("❌ Агент не ответил")
            
    except Exception as e:
        print(f"❌ Тест агента: {e}")

def main():
    """Основная функция тестирования"""
    print("🧠 Тестирование веб-интерфейса ARK v2.8")
    print("=" * 50)
    
    # Проверяем, запущен ли сервер
    try:
        response = requests.get("http://localhost:8000/api/status", timeout=2)
        if response.status_code == 200:
            print("✅ Веб-сервер запущен")
        else:
            print("❌ Веб-сервер не отвечает")
            return
    except:
        print("❌ Веб-сервер не доступен")
        print("Запустите: python web/chat_server.py")
        return
    
    # Запускаем тесты
    test_api_endpoints()
    test_html_interface()
    test_chat_functionality()
    test_agent_communication()
    
    print("\n" + "=" * 50)
    print("🎯 Тестирование завершено!")

if __name__ == "__main__":
    main() 