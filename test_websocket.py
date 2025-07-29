#!/usr/bin/env python3
"""
Тестовый скрипт для проверки WebSocket соединения с ARK
"""

import asyncio
import websockets
import json
import time

async def test_websocket():
    """Тестирование WebSocket соединения"""
    uri = "ws://localhost:8000/ws"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket соединение установлено")
            
            # Отправляем тестовое сообщение
            test_message = {
                "text": "привет",
                "user_id": "test_user"
            }
            
            print(f"📤 Отправляем сообщение: {test_message}")
            await websocket.send(json.dumps(test_message))
            
            # Ждем ответ
            print("⏳ Ожидаем ответ...")
            response = await websocket.recv()
            data = json.loads(response)
            
            print(f"📥 Получен ответ:")
            print(f"   Тип: {data.get('type')}")
            print(f"   Текст: {data.get('text')}")
            print(f"   Reasoning Chain: {len(data.get('reasoning_chain', []))} шагов")
            print(f"   Сознание: {data.get('consciousness_state')}")
            print(f"   Эмоция: {data.get('emotion_state')}")
            
            # Отправляем еще одно сообщение
            test_message2 = {
                "text": "как дела?",
                "user_id": "test_user"
            }
            
            print(f"\n📤 Отправляем второе сообщение: {test_message2}")
            await websocket.send(json.dumps(test_message2))
            
            # Ждем второй ответ
            print("⏳ Ожидаем второй ответ...")
            response2 = await websocket.recv()
            data2 = json.loads(response2)
            
            print(f"📥 Получен второй ответ:")
            print(f"   Тип: {data2.get('type')}")
            print(f"   Текст: {data2.get('text')}")
            print(f"   Reasoning Chain: {len(data2.get('reasoning_chain', []))} шагов")
            
            print("\n✅ Тест завершен успешно!")
            
    except Exception as e:
        print(f"❌ Ошибка WebSocket: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket()) 