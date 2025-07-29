#!/usr/bin/env python3
"""
Тестирование веб-интерфейса ARK
"""

import requests
import json
import time
import websocket
import threading

BASE_URL = "http://localhost:8000"

def test_api_endpoints():
    """Тестирование API эндпоинтов"""
    print("🧪 Тестирование API эндпоинтов...")
    
    # Тест статуса
    try:
        response = requests.get(f"{BASE_URL}/api/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Статус: {data.get('consciousness_state')} - {data.get('emotion_state')}")
        else:
            print(f"❌ Ошибка статуса: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка получения статуса: {e}")
    
    # Тест истории чата
    try:
        response = requests.get(f"{BASE_URL}/api/chat_history")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ История чата: {len(data.get('messages', []))} сообщений")
        else:
            print(f"❌ Ошибка истории чата: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка получения истории чата: {e}")
    
    # Тест авто-отчета
    try:
        response = requests.get(f"{BASE_URL}/api/auto_report")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Авто-отчет: {data.get('report', 'N/A')}")
        else:
            print(f"❌ Ошибка авто-отчета: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка получения авто-отчета: {e}")
    
    # Тест reasoning chain
    try:
        response = requests.get(f"{BASE_URL}/api/reasoning_chain")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Reasoning Chain: {len(data.get('reasoning_chain', []))} шагов")
        else:
            print(f"❌ Ошибка reasoning chain: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка получения reasoning chain: {e}")
    
    # Тест изменения состояния
    try:
        response = requests.post(f"{BASE_URL}/api/change_state?consciousness_state=excited&emotion_state=excited")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Изменение состояния: {data.get('status')}")
        else:
            print(f"❌ Ошибка изменения состояния: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка изменения состояния: {e}")
    
    # Тест мета-мыслей
    try:
        response = requests.get(f"{BASE_URL}/api/meta_thoughts")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Мета-мысли: {data.get('status')}")
        else:
            print(f"❌ Ошибка мета-мыслей: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка получения мета-мыслей: {e}")
    
    # Тест архитектора
    try:
        response = requests.get(f"{BASE_URL}/api/architect/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Статус архитектора: {data.get('status')}")
        else:
            print(f"❌ Ошибка статуса архитектора: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка получения статуса архитектора: {e}")

def test_websocket():
    """Тестирование WebSocket соединения"""
    print("\n🔌 Тестирование WebSocket...")
    
    def on_message(ws, message):
        data = json.loads(message)
        print(f"📨 Получено сообщение: {data.get('type', 'unknown')}")
    
    def on_error(ws, error):
        print(f"❌ WebSocket ошибка: {error}")
    
    def on_close(ws, close_status_code, close_msg):
        print("🔌 WebSocket соединение закрыто")
    
    def on_open(ws):
        print("✅ WebSocket соединение установлено")
        # Отправляем тестовое сообщение
        test_message = {
            "type": "user_message",
            "message": "Привет, ARK! Как дела?"
        }
        ws.send(json.dumps(test_message))
    
    try:
        ws = websocket.WebSocketApp(
            "ws://localhost:8000/ws",
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )
        
        # Запускаем WebSocket в отдельном потоке
        wst = threading.Thread(target=ws.run_forever)
        wst.daemon = True
        wst.start()
        
        # Ждем немного для получения сообщений
        time.sleep(3)
        
        ws.close()
        print("✅ WebSocket тест завершен")
        
    except Exception as e:
        print(f"❌ Ошибка WebSocket: {e}")

def test_state_changes():
    """Тестирование изменений состояния"""
    print("\n🎛️ Тестирование изменений состояния...")
    
    states = [
        ("normal", "calm"),
        ("excited", "excited"),
        ("focused", "learning"),
        ("stressed", "concerned"),
        ("evolving", "creative"),
        ("reflecting", "curious")
    ]
    
    for consciousness, emotion in states:
        try:
            response = requests.post(f"{BASE_URL}/api/change_state?consciousness_state={consciousness}&emotion_state={emotion}")
            if response.status_code == 200:
                print(f"✅ Состояние изменено: {consciousness} + {emotion}")
            else:
                print(f"❌ Ошибка изменения состояния {consciousness} + {emotion}: {response.status_code}")
            time.sleep(0.5)  # Небольшая пауза между изменениями
        except Exception as e:
            print(f"❌ Ошибка изменения состояния {consciousness} + {emotion}: {e}")

def main():
    """Главная функция тестирования"""
    print("🚀 Запуск тестирования веб-интерфейса ARK")
    print("=" * 50)
    
    # Тестируем API эндпоинты
    test_api_endpoints()
    
    # Тестируем WebSocket
    test_websocket()
    
    # Тестируем изменения состояния
    test_state_changes()
    
    print("\n" + "=" * 50)
    print("✅ Тестирование завершено!")
    print(f"🌐 Веб-интерфейс доступен по адресу: {BASE_URL}")

if __name__ == "__main__":
    main() 