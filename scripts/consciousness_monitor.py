#!/usr/bin/env python3
"""
ConsciousnessMonitor - Веб-интерфейс для мониторинга сознания агента
"""

import asyncio
import json
import logging
import time
import sys
from datetime import datetime
from typing import Dict, Any
import threading

# Добавляем путь к проекту
sys.path.insert(0, '.')

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn

from mind.consciousness_core import ConsciousnessCore

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ARK Consciousness Monitor")

# Глобальные переменные
consciousness_core = None
monitoring_active = False
connected_clients = []


@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске"""
    global consciousness_core
    consciousness_core = ConsciousnessCore()
    logger.info("🧠 Consciousness Monitor запущен")


@app.get("/")
async def get_monitor_page():
    """Главная страница мониторинга"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ARK Consciousness Monitor</title>
        <meta charset="utf-8">
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #1a1a1a; color: #fff; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { text-align: center; margin-bottom: 30px; }
            .status-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px; }
            .card { background: #2a2a2a; border-radius: 10px; padding: 20px; border: 1px solid #444; }
            .card h3 { margin-top: 0; color: #4CAF50; }
            .desire-item { background: #333; padding: 10px; margin: 5px 0; border-radius: 5px; border-left: 4px solid #4CAF50; }
            .thought-item { background: #333; padding: 10px; margin: 5px 0; border-radius: 5px; border-left: 4px solid #2196F3; }
            .decision-item { background: #333; padding: 10px; margin: 5px 0; border-radius: 5px; border-left: 4px solid #FF9800; }
            .trait-bar { background: #444; height: 20px; border-radius: 10px; margin: 5px 0; }
            .trait-fill { height: 100%; border-radius: 10px; background: linear-gradient(90deg, #4CAF50, #8BC34A); }
            .controls { text-align: center; margin: 20px 0; }
            .btn { background: #4CAF50; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin: 0 10px; }
            .btn:hover { background: #45a049; }
            .btn.stop { background: #f44336; }
            .btn.stop:hover { background: #da190b; }
            .log { background: #000; padding: 15px; border-radius: 5px; height: 300px; overflow-y: auto; font-family: monospace; font-size: 12px; }
            .log-entry { margin: 2px 0; }
            .log-info { color: #4CAF50; }
            .log-warning { color: #FF9800; }
            .log-error { color: #f44336; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🧠 ARK Consciousness Monitor</h1>
                <p>Мониторинг сознания агента в реальном времени</p>
            </div>
            
            <div class="controls">
                <button class="btn" onclick="startMonitoring()">▶️ Запустить сознание</button>
                <button class="btn stop" onclick="stopMonitoring()">⏹️ Остановить</button>
                <button class="btn" onclick="clearLog()">🗑️ Очистить лог</button>
            </div>
            
            <div class="status-grid">
                <div class="card">
                    <h3>🎯 Текущие желания</h3>
                    <div id="desires"></div>
                </div>
                
                <div class="card">
                    <h3>🧠 Характер</h3>
                    <div id="character"></div>
                </div>
                
                <div class="card">
                    <h3>💭 Последние мысли</h3>
                    <div id="thoughts"></div>
                </div>
                
                <div class="card">
                    <h3>⚡ Последние решения</h3>
                    <div id="decisions"></div>
                </div>
                
                <div class="card">
                    <h3>📊 Статистика</h3>
                    <div id="stats"></div>
                </div>
                
                <div class="card">
                    <h3>🌡️ Состояние системы</h3>
                    <div id="system-state"></div>
                </div>
            </div>
            
            <div class="card">
                <h3>📝 Лог сознания</h3>
                <div id="log" class="log"></div>
            </div>
        </div>
        
        <script>
            let ws = null;
            
            function connect() {
                ws = new WebSocket('ws://localhost:8080/ws');
                
                ws.onopen = function() {
                    addLog('🔗 Подключение к сознанию установлено', 'info');
                };
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    updateUI(data);
                };
                
                ws.onclose = function() {
                    addLog('❌ Соединение с сознанием потеряно', 'error');
                    setTimeout(connect, 5000);
                };
                
                ws.onerror = function(error) {
                    addLog('⚠️ Ошибка WebSocket: ' + error, 'error');
                };
            }
            
            function updateUI(data) {
                // Обновляем желания
                if (data.desires) {
                    const desiresDiv = document.getElementById('desires');
                    desiresDiv.innerHTML = data.desires.map(desire => 
                        `<div class="desire-item">
                            <strong>${desire.name}</strong><br>
                            <small>Вес: ${desire.weight.toFixed(2)}, Срочность: ${desire.urgency.toFixed(2)}</small>
                        </div>`
                    ).join('');
                }
                
                // Обновляем характер
                if (data.character) {
                    const characterDiv = document.getElementById('character');
                    characterDiv.innerHTML = Object.entries(data.character.traits).map(([trait, value]) => 
                        `<div>
                            <strong>${trait}:</strong>
                            <div class="trait-bar">
                                <div class="trait-fill" style="width: ${value * 100}%"></div>
                            </div>
                            <small>${(value * 100).toFixed(0)}%</small>
                        </div>`
                    ).join('');
                }
                
                // Обновляем мысли
                if (data.thoughts) {
                    const thoughtsDiv = document.getElementById('thoughts');
                    thoughtsDiv.innerHTML = data.thoughts.map(thought => 
                        `<div class="thought-item">
                            <small>${thought.timestamp}</small><br>
                            <strong>${thought.type}:</strong> ${thought.content.substring(0, 50)}...
                        </div>`
                    ).join('');
                }
                
                // Обновляем решения
                if (data.decisions) {
                    const decisionsDiv = document.getElementById('decisions');
                    decisionsDiv.innerHTML = data.decisions.map(decision => 
                        `<div class="decision-item">
                            <small>${decision.timestamp}</small><br>
                            <strong>${decision.action}</strong><br>
                            <small>Уверенность: ${(decision.confidence * 100).toFixed(0)}%</small>
                        </div>`
                    ).join('');
                }
                
                // Обновляем статистику
                if (data.stats) {
                    const statsDiv = document.getElementById('stats');
                    statsDiv.innerHTML = `
                        <div><strong>Циклов:</strong> ${data.stats.cycle}</div>
                        <div><strong>Мыслей:</strong> ${data.stats.recent_thoughts}</div>
                        <div><strong>Решений:</strong> ${data.stats.recent_decisions}</div>
                        <div><strong>Память:</strong> ${data.stats.memory_size} записей</div>
                    `;
                }
                
                // Обновляем состояние системы
                if (data.system_state) {
                    const systemDiv = document.getElementById('system-state');
                    systemDiv.innerHTML = `
                        <div><strong>Температура:</strong> ${data.system_state.temperature}°C</div>
                        <div><strong>CPU:</strong> ${data.system_state.cpu_usage}%</div>
                        <div><strong>RAM:</strong> ${data.system_state.memory_usage}%</div>
                        <div><strong>Эмоции:</strong> ${data.system_state.emotional_state}</div>
                    `;
                }
                
                // Добавляем в лог
                if (data.log) {
                    addLog(data.log.message, data.log.level);
                }
            }
            
            function addLog(message, level = 'info') {
                const logDiv = document.getElementById('log');
                const entry = document.createElement('div');
                entry.className = `log-entry log-${level}`;
                entry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
                logDiv.appendChild(entry);
                logDiv.scrollTop = logDiv.scrollHeight;
            }
            
            function startMonitoring() {
                if (ws && ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({action: 'start_monitoring'}));
                    addLog('▶️ Запуск мониторинга сознания', 'info');
                }
            }
            
            function stopMonitoring() {
                if (ws && ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({action: 'stop_monitoring'}));
                    addLog('⏹️ Остановка мониторинга', 'warning');
                }
            }
            
            function clearLog() {
                document.getElementById('log').innerHTML = '';
                addLog('🗑️ Лог очищен', 'info');
            }
            
            // Подключаемся при загрузке страницы
            connect();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint для реального времени"""
    await websocket.accept()
    connected_clients.append(websocket)
    
    try:
        while True:
            # Получаем сообщения от клиента
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get('action') == 'start_monitoring':
                await start_consciousness_monitoring(websocket)
            elif message.get('action') == 'stop_monitoring':
                await stop_consciousness_monitoring(websocket)
                
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
        logger.info("Клиент отключился")


async def start_consciousness_monitoring(websocket: WebSocket):
    """Запускает мониторинг сознания"""
    global monitoring_active
    monitoring_active = True
    
    # Отправляем начальное состояние
    await send_consciousness_update(websocket)
    
    # Запускаем цикл мониторинга
    while monitoring_active:
        try:
            # Выполняем один цикл сознания
            result = await consciousness_core.consciousness_cycle_step()
            
            # Отправляем обновление
            await send_consciousness_update(websocket, result)
            
            # Пауза между циклами
            await asyncio.sleep(2)
            
        except Exception as e:
            logger.error(f"Ошибка в цикле мониторинга: {e}")
            await websocket.send_text(json.dumps({
                "log": {"message": f"Ошибка: {e}", "level": "error"}
            }))
            break


async def stop_consciousness_monitoring(websocket: WebSocket):
    """Останавливает мониторинг сознания"""
    global monitoring_active
    monitoring_active = False
    await websocket.send_text(json.dumps({
        "log": {"message": "Мониторинг остановлен", "level": "warning"}
    }))


async def send_consciousness_update(websocket: WebSocket, cycle_result: Dict[str, Any] = None):
    """Отправляет обновление состояния сознания"""
    try:
        # Получаем текущее состояние
        status = consciousness_core.get_consciousness_status()
        thoughts = consciousness_core.get_thoughts_summary()
        decisions = consciousness_core.get_decisions_summary()
        
        # Формируем данные для отправки
        update_data = {
            "desires": [
                {
                    "name": desire.name,
                    "weight": desire.weight,
                    "urgency": desire.urgency,
                    "type": desire.type.value
                }
                for desire in consciousness_core.current_desires[:5]
            ],
            "character": status["character"],
            "thoughts": thoughts,
            "decisions": decisions,
            "stats": {
                "cycle": status["cycle"],
                "recent_thoughts": status["recent_thoughts"],
                "recent_decisions": status["recent_decisions"],
                "memory_size": status["memory_size"]
            },
            "system_state": status["self_state"]
        }
        
        # Добавляем результат цикла если есть
        if cycle_result:
            update_data["cycle_result"] = cycle_result
            update_data["log"] = {
                "message": f"Цикл {cycle_result['cycle']}: {cycle_result.get('primary_desire', 'Нет желаний')}",
                "level": "info"
            }
        
        await websocket.send_text(json.dumps(update_data))
        
    except Exception as e:
        logger.error(f"Ошибка отправки обновления: {e}")


@app.get("/api/consciousness/status")
async def get_consciousness_status():
    """API endpoint для получения статуса сознания"""
    if not consciousness_core:
        return {"error": "Consciousness core not initialized"}
    
    status = consciousness_core.get_consciousness_status()
    return status


@app.get("/api/consciousness/thoughts")
async def get_thoughts():
    """API endpoint для получения мыслей"""
    if not consciousness_core:
        return {"error": "Consciousness core not initialized"}
    
    thoughts = consciousness_core.get_thoughts_summary()
    return {"thoughts": thoughts}


@app.get("/api/consciousness/decisions")
async def get_decisions():
    """API endpoint для получения решений"""
    if not consciousness_core:
        return {"error": "Consciousness core not initialized"}
    
    decisions = consciousness_core.get_decisions_summary()
    return {"decisions": decisions}


if __name__ == "__main__":
    print("🧠 Запуск ARK Consciousness Monitor...")
    print("📊 Веб-интерфейс: http://localhost:8080")
    print("🔗 WebSocket: ws://localhost:8080/ws")
    
    uvicorn.run(
        "consciousness_monitor:app",
        host="0.0.0.0",
        port=8080,
        reload=True
    ) 