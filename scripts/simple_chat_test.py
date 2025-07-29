#!/usr/bin/env python3
"""
Простой тест общения с агентом ARK
"""

import requests
import json
import time
import sys
from pathlib import Path

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_chat_with_agent():
    """Тестирование общения с агентом через WebSocket"""
    print("🤖 Тестирование общения с агентом ARK")
    print("=" * 50)
    
    try:
        import websockets
        import asyncio
        
        async def chat_test():
            uri = "ws://localhost:8000/ws"
            
            try:
                async with websockets.connect(uri) as websocket:
                    print("✅ Подключились к WebSocket")
                    
                    # Ждем начальное состояние
                    initial_state = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    print("📊 Получили начальное состояние агента")
                    
                    # Отправляем тестовое сообщение
                    test_messages = [
                        "Привет! Как дела?",
                        "Расскажи о себе",
                        "Что ты умеешь делать?",
                        "Покажи свои возможности"
                    ]
                    
                    for i, message in enumerate(test_messages, 1):
                        print(f"\n📝 Тест {i}: {message}")
                        
                        # Отправляем сообщение
                        chat_message = {
                            "type": "user_message",
                            "text": message,
                            "user_id": "test_user"
                        }
                        await websocket.send(json.dumps(chat_message))
                        
                        # Ждем ответ
                        try:
                            response = await asyncio.wait_for(websocket.recv(), timeout=15.0)
                            data = json.loads(response)
                            
                            if data.get("type") == "agent_response":
                                print(f"✅ Агент ответил: {data.get('text', 'Нет текста')[:100]}...")
                            elif data.get("type") == "agent_state":
                                print(f"📊 Обновление состояния: {data.get('consciousness_state', 'unknown')}")
                            else:
                                print(f"📨 Получен ответ типа: {data.get('type', 'unknown')}")
                                
                        except asyncio.TimeoutError:
                            print("⏰ Таймаут ожидания ответа")
                        
                        # Пауза между сообщениями
                        await asyncio.sleep(2)
                    
                    print("\n✅ Тестирование завершено!")
                    
            except Exception as e:
                print(f"❌ Ошибка WebSocket: {e}")
        
        asyncio.run(chat_test())
        
    except ImportError:
        print("❌ websockets не установлен")
        print("Установите: pip install websockets")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def test_api_communication():
    """Тестирование API коммуникации"""
    print("\n🔌 Тестирование API коммуникации")
    print("=" * 30)
    
    base_url = "http://localhost:8000"
    
    # Тест 1: Статус агента
    try:
        response = requests.get(f"{base_url}/api/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Статус агента: {data.get('status', 'unknown')}")
            print(f"   Сознание: {data.get('consciousness_state', 'unknown')}")
            print(f"   Эмоция: {data.get('emotion_state', 'unknown')}")
        else:
            print(f"❌ Статус: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка статуса: {e}")
    
    # Тест 2: История чата
    try:
        response = requests.get(f"{base_url}/api/chat_history")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ История чата: {len(data.get('messages', []))} сообщений")
        else:
            print(f"❌ История чата: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка истории: {e}")
    
    # Тест 3: Инструменты
    try:
        response = requests.get(f"{base_url}/api/tools_status")
        if response.status_code == 200:
            data = response.json()
            tools = data.get('tools', [])
            print(f"✅ Доступно инструментов: {len(tools)}")
            for tool in tools[:3]:  # Показываем первые 3
                print(f"   - {tool.get('name', 'Unknown')}")
        else:
            print(f"❌ Инструменты: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка инструментов: {e}")

def main():
    """Основная функция"""
    print("🧠 Простой тест ARK v2.8")
    print("=" * 50)
    
    # Проверяем сервер
    try:
        response = requests.get("http://localhost:8000/api/status", timeout=2)
        if response.status_code == 200:
            print("✅ Сервер доступен")
        else:
            print("❌ Сервер не отвечает")
            return
    except:
        print("❌ Сервер недоступен")
        print("Запустите: python web/chat_server.py")
        return
    
    # Запускаем тесты
    test_api_communication()
    test_chat_with_agent()
    
    print("\n" + "=" * 50)
    print("🎯 Все тесты завершены!")

if __name__ == "__main__":
    main() 