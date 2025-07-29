#!/usr/bin/env python3
"""
ARK v2.8 - Living Dialog Server
FastAPI websocket server for real-time communication with the agent
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from body.embodied_feedback import embodied_feedback, ConsciousnessState, EmotionState
from evaluation.auto_reporter import auto_reporter
from psyche.emotional_core import EmotionalProcessingCore
from mind.multi_threaded_thought import multi_threaded_thought
from mind.cognitive_architecture import cognitive_brain, BrainDepartment, BrainConsensus


class ChatManager:
    """Manages WebSocket connections and chat sessions"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.chat_history: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(__name__)
        
        # Initialize agent components
        self.emotional_core = EmotionalProcessingCore()
        
        # Start embodied feedback
        embodied_feedback.start_monitoring()
        auto_reporter.start_reporting()
    
    async def connect(self, websocket: WebSocket):
        """Connect new client"""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.logger.info(f"Client connected. Total connections: {len(self.active_connections)}")
        
        # Send initial state
        await self.send_agent_state(websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Disconnect client"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        self.logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific client"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: str):
        """Broadcast message to all clients"""
        for connection in self.active_connections:
            await self.send_personal_message(message, connection)
    
    async def send_agent_state(self, websocket: WebSocket):
        """Send current agent state"""
        try:
            feedback = embodied_feedback.get_feedback_summary()
            state = {
                "type": "agent_state",
                "timestamp": datetime.now().isoformat(),
                "consciousness_state": feedback.get("consciousness_state", "unknown"),
                "emotion_state": feedback.get("emotion_state", "unknown"),
                "visual_feedback": feedback.get("visual_feedback", {}),
                "rgb_status": feedback.get("rgb_status", {}),
                "physical_metrics": feedback.get("physical_metrics", {})
            }
            await self.send_personal_message(json.dumps(state), websocket)
        except Exception as e:
            self.logger.error(f"Failed to send agent state: {e}")
    
    async def process_user_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Process user message and generate agent response"""
        try:
            user_text = message.get("text", "")
            user_id = message.get("user_id", "user")
            
            # Add to chat history
            chat_entry = {
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "type": "user_message",
                "text": user_text
            }
            self.chat_history.append(chat_entry)
            
            # Generate reasoning chain
            reasoning_chain = await self.generate_reasoning_chain(user_text)
            
            # Generate agent response
            agent_response = await self.generate_agent_response(user_text, reasoning_chain)
            
            # Update agent state based on interaction
            await self.update_agent_state(user_text, agent_response)
            
            # Send response
            response_data = {
                "type": "agent_response",
                "timestamp": datetime.now().isoformat(),
                "text": agent_response,
                "reasoning_chain": reasoning_chain,
                "consciousness_state": embodied_feedback.consciousness_state.value,
                "emotion_state": embodied_feedback.emotion_state.value
            }
            
            await self.send_personal_message(json.dumps(response_data), websocket)
            
            # Broadcast state update
            await self.broadcast_state_update()
            
        except Exception as e:
            self.logger.error(f"Failed to process user message: {e}")
            error_response = {
                "type": "error",
                "timestamp": datetime.now().isoformat(),
                "message": f"Failed to process message: {str(e)}"
            }
            await self.send_personal_message(json.dumps(error_response), websocket)
    
    async def generate_reasoning_chain(self, user_text: str) -> List[Dict[str, Any]]:
        """Generate reasoning chain using brain departments"""
        try:
            # Простая обработка через когнитивную архитектуру
            from mind.cognitive_architecture import cognitive_brain
            
            # Обрабатываем через когнитивную архитектуру
            result = cognitive_brain.process_user_input(user_text)
            
            if not result:
                return [{
                    "step": 1,
                    "department": "meta_observer",
                    "department_name": "Meta Observer",
                    "reasoning": "Processing user input through cognitive architecture",
                    "output": "I understand your request and will process it accordingly.",
                    "confidence": 0.7,
                    "timestamp": datetime.now().isoformat(),
                    "metadata": {"status": "processed"}
                }]
            
            # Возвращаем простую цепочку рассуждений
            return [{
                "step": 1,
                "department": "meta_observer",
                "department_name": "Meta Observer",
                "reasoning": f"Processing user input: {user_text}",
                "output": result.get("decision", "Request processed successfully"),
                "confidence": result.get("confidence", 0.7),
                "timestamp": datetime.now().isoformat(),
                "metadata": {"status": "success"}
            }]
            
        except Exception as e:
            self.logger.error(f"Error in reasoning chain generation: {e}")
            return [{
                "step": 1,
                "department": "error",
                "department_name": "Error",
                "reasoning": f"Error processing request: {str(e)}",
                "output": "I encountered an error while processing your request.",
                "confidence": 0.0,
                "timestamp": datetime.now().isoformat(),
                "metadata": {"error": str(e)}
            }]
    
    async def generate_agent_response(self, user_text: str, reasoning_chain: List[Dict[str, Any]]) -> str:
        """Generate agent response based on reasoning chain"""
        try:
            # Простая логика генерации ответа
            if "привет" in user_text.lower() or "hello" in user_text.lower():
                return "Привет! Я ARK v2.8 - ваш воплощенный ИИ-агент. Как я могу помочь вам сегодня?"
            
            elif "как дела" in user_text.lower() or "how are you" in user_text.lower():
                return "Спасибо, у меня все хорошо! Я готов помочь вам с любыми задачами."
            
            elif "расскажи о себе" in user_text.lower() or "tell me about yourself" in user_text.lower():
                return "Я ARK v2.8 - когнитивный ИИ-агент с воплощенной архитектурой. У меня есть когнитивные отделы мозга, эмоциональная система и способность к самоэволюции. Я могу анализировать, планировать, критиковать и создавать решения."
            
            elif "что ты умеешь" in user_text.lower() or "what can you do" in user_text.lower():
                return "Я умею: анализировать производительность системы, планировать эволюцию, проверять безопасность кода, документировать изменения, сохранять память о взаимодействиях и многое другое. Просто скажите, что вам нужно!"
            
            elif "покажи возможности" in user_text.lower() or "show capabilities" in user_text.lower():
                return "Мои возможности: 1) Когнитивная архитектура с 6 отделами мозга, 2) Эмоциональная система, 3) Самоэволюция, 4) Анализ производительности, 5) Безопасность кода, 6) Документирование, 7) Планирование, 8) Критический анализ."
            
            else:
                # Используем reasoning chain для генерации ответа
                if reasoning_chain and len(reasoning_chain) > 0:
                    last_step = reasoning_chain[-1]
                    return last_step.get("output", "Я обработал ваш запрос и готов помочь!")
                else:
                    return "Я получил ваше сообщение и обрабатываю его. Чем еще могу помочь?"
                    
        except Exception as e:
            self.logger.error(f"Error generating agent response: {e}")
            return "Извините, произошла ошибка при обработке вашего запроса. Попробуйте еще раз."
    
    async def update_agent_state(self, user_text: str, response: str):
        """Update agent state based on interaction"""
        # Simple state updates based on interaction
        if "эволюция" in user_text.lower():
            embodied_feedback.set_consciousness_state(ConsciousnessState.EVOLVING, EmotionState.CREATIVE)
        elif "обучение" in user_text.lower():
            embodied_feedback.set_consciousness_state(ConsciousnessState.LEARNING, EmotionState.SATISFIED)
        elif "стресс" in user_text.lower():
            embodied_feedback.set_consciousness_state(ConsciousnessState.STRESSED, EmotionState.CONCERNED)
        else:
            embodied_feedback.set_consciousness_state(ConsciousnessState.NORMAL, EmotionState.CALM)
    
    async def broadcast_state_update(self):
        """Broadcast current state to all clients"""
        try:
            feedback = embodied_feedback.get_feedback_summary()
            state_update = {
                "type": "state_update",
                "timestamp": datetime.now().isoformat(),
                "consciousness_state": feedback.get("consciousness_state", "unknown"),
                "emotion_state": feedback.get("emotion_state", "unknown"),
                "visual_feedback": feedback.get("visual_feedback", {}),
                "rgb_status": feedback.get("rgb_status", {})
            }
            await self.broadcast(json.dumps(state_update))
        except Exception as e:
            self.logger.error(f"Failed to broadcast state update: {e}")


# Create FastAPI app
app = FastAPI(title="ARK v2.8 Living Dialog", version="2.8.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create chat manager
chat_manager = ChatManager()

# Serve static files
app.mount("/static", StaticFiles(directory="web/static"), name="static")


@app.get("/")
async def get_chat_page():
    """Serve chat interface"""
    # Read the HTML file from static directory
    try:
        with open("web/static/index.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content, media_type="text/html")
    except FileNotFoundError:
        # Fallback to simple HTML if file not found
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>ARK v2.8 - Living Dialog</title>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #1a1a1a; color: #fff; }
                .container { max-width: 1200px; margin: 0 auto; }
                .header { text-align: center; margin-bottom: 20px; }
                .chat-container { display: flex; height: 600px; }
                .chat-area { flex: 2; border: 1px solid #333; border-radius: 5px; margin-right: 10px; }
                .status-area { flex: 1; border: 1px solid #333; border-radius: 5px; }
                .chat-messages { height: 500px; overflow-y: auto; padding: 10px; background: #2a2a2a; }
                .status-content { height: 500px; overflow-y: auto; padding: 10px; background: #2a2a2a; }
                .input-area { padding: 10px; border-top: 1px solid #333; }
                .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
                .user-message { background: #4a4a4a; }
                .agent-message { background: #3a3a3a; }
                .reasoning { background: #2a2a2a; margin: 5px 0; padding: 5px; font-size: 0.9em; }
                .status-item { margin: 5px 0; padding: 5px; background: #3a3a3a; border-radius: 3px; }
                input[type="text"] { width: 80%; padding: 10px; background: #3a3a3a; border: 1px solid #555; color: #fff; border-radius: 3px; }
                button { padding: 10px 20px; background: #007acc; color: #fff; border: none; border-radius: 3px; cursor: pointer; }
                button:hover { background: #005a9e; }
                .emoji { font-size: 1.2em; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🤖 ARK v2.8 - Living Dialog</h1>
                    <p>Живой диалог с воплощенным ИИ-агентом</p>
                </div>
                
                <div class="chat-container">
                    <div class="chat-area">
                        <div class="chat-messages" id="chatMessages"></div>
                        <div class="input-area">
                            <input type="text" id="messageInput" placeholder="Введите сообщение..." onkeypress="handleKeyPress(event)">
                            <button onclick="sendMessage()">Отправить</button>
                        </div>
                    </div>
                    
                    <div class="status-area">
                        <h3>📊 Статус агента</h3>
                        <div class="status-content" id="statusContent">
                            <div class="status-item">🔄 Подключение...</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <script>
                let ws = null;
                
                function connect() {
                    ws = new WebSocket('ws://localhost:8000/ws');
                    
                    ws.onopen = function() {
                        addStatusMessage('✅ Подключено к ARK v2.8');
                    };
                    
                    ws.onmessage = function(event) {
                        const data = JSON.parse(event.data);
                        handleMessage(data);
                    };
                    
                    ws.onclose = function() {
                        addStatusMessage('❌ Соединение разорвано');
                        setTimeout(connect, 3000);
                    };
                    
                    ws.onerror = function(error) {
                        addStatusMessage('❌ Ошибка соединения');
                    };
                }
                
                function handleMessage(data) {
                    switch(data.type) {
                        case 'agent_response':
                            addAgentMessage(data.text, data.reasoning_chain);
                            updateAgentState(data.consciousness_state, data.emotion_state);
                            break;
                        case 'agent_state':
                        case 'state_update':
                            updateAgentState(data.consciousness_state, data.emotion_state);
                            updateVisualFeedback(data.visual_feedback);
                            updateRGBStatus(data.rgb_status);
                            break;
                        case 'error':
                            addStatusMessage('❌ Ошибка: ' + data.message);
                            break;
                    }
                }
                
                function sendMessage() {
                    const input = document.getElementById('messageInput');
                const text = input.value.trim();
                
                if (text && ws && ws.readyState === WebSocket.OPEN) {
                    const message = {
                        text: text,
                        user_id: 'user',
                        timestamp: new Date().toISOString()
                    };
                    
                    ws.send(JSON.stringify(message));
                    addUserMessage(text);
                    input.value = '';
                }
            }
            
            function handleKeyPress(event) {
                if (event.key === 'Enter') {
                    sendMessage();
                }
            }
            
            function addUserMessage(text) {
                const messages = document.getElementById('chatMessages');
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message user-message';
                messageDiv.innerHTML = `<strong>Вы:</strong> ${text}`;
                messages.appendChild(messageDiv);
                messages.scrollTop = messages.scrollHeight;
            }
            
            function addAgentMessage(text, reasoningChain) {
                const messages = document.getElementById('chatMessages');
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message agent-message';
                
                let reasoningHtml = '';
                if (reasoningChain && reasoningChain.length > 0) {
                    reasoningHtml = '<div class="reasoning"><strong>Reasoning Chain:</strong><br>';
                    reasoningChain.forEach(step => {
                        reasoningHtml += `• ${step.content}<br>`;
                    });
                    reasoningHtml += '</div>';
                }
                
                messageDiv.innerHTML = `<strong>ARK:</strong> ${text}${reasoningHtml}`;
                messages.appendChild(messageDiv);
                messages.scrollTop = messages.scrollHeight;
            }
            
            function addStatusMessage(text) {
                const status = document.getElementById('statusContent');
                const statusDiv = document.createElement('div');
                statusDiv.className = 'status-item';
                statusDiv.textContent = text;
                status.appendChild(statusDiv);
                status.scrollTop = status.scrollHeight;
            }
            
            function updateAgentState(consciousness, emotion) {
                addStatusMessage(`🧠 Сознание: ${consciousness} | 😊 Эмоция: ${emotion}`);
            }
            
            function updateVisualFeedback(visual) {
                if (visual && visual.emoji) {
                    addStatusMessage(`🎨 Визуальная обратная связь: ${visual.emoji} ${visual.state}`);
                }
            }
            
            function updateRGBStatus(rgb) {
                if (rgb && rgb.color) {
                    addStatusMessage(`💡 RGB: ${rgb.color} (доступно: ${rgb.available})`);
                }
            }
            
            // Connect on page load
            connect();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/test")
async def get_test_page():
    """Тестовая страница"""
    return HTMLResponse(open("web/static/test.html").read())


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time chat"""
    await chat_manager.connect(websocket)
    try:
        while True:
            # Получаем сообщение от клиента
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Обрабатываем сообщение
            await chat_manager.process_user_message(message, websocket)
            
    except WebSocketDisconnect:
        chat_manager.disconnect(websocket)
    except Exception as e:
        chat_manager.logger.error(f"WebSocket error: {e}")
        chat_manager.disconnect(websocket)


@app.get("/api/status")
async def get_status():
    """Get current agent status with meta-thoughts"""
    try:
        feedback = embodied_feedback.get_feedback_summary()
        meta_state = multi_threaded_thought.get_current_state()
        
        return {
            "status": "active",
            "timestamp": datetime.now().isoformat(),
            "consciousness_state": feedback.get("consciousness_state", "unknown"),
            "emotion_state": feedback.get("emotion_state", "unknown"),
            "visual_feedback": feedback.get("visual_feedback", {}),
            "rgb_status": feedback.get("rgb_status", {}),
            "physical_metrics": feedback.get("physical_metrics", {}),
            "meta_thoughts": {
                "cognitive_state": meta_state.get("cognitive_state", {}),
                "system_metrics": meta_state.get("system_metrics", {}),
                "monitoring_active": meta_state.get("monitoring_active", False),
                "meta_thoughts_count": len(meta_state.get("meta_thoughts", [])),
                "reasoning_chains_count": meta_state.get("reasoning_chains_count", 0)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/chat_history")
async def get_chat_history():
    """Get chat history"""
    return {"history": chat_manager.chat_history}


@app.get("/api/auto_report")
async def get_auto_report():
    """Get latest auto-report"""
    try:
        from evaluation.auto_reporter import auto_reporter
        report = auto_reporter.get_latest_report()
        return {
            "timestamp": datetime.now().isoformat(),
            "report": report
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/reasoning_chain")
async def get_reasoning_chain():
    """Get latest reasoning chain with meta-thoughts"""
    try:
        # Get current state from multi-threaded thought system
        meta_state = multi_threaded_thought.get_current_state()
        
        # Enhanced reasoning chain with meta-data
        reasoning_chain = [
            {
                "step": 1,
                "type": "meta_analysis",
                "content": f"Мои текущие ресурсы: CPU={meta_state.get('system_metrics', {}).get('cpu_percent', 0):.1f}%, "
                          f"Temp={meta_state.get('system_metrics', {}).get('temperature', 0):.1f}°C, "
                          f"Emotions={meta_state.get('cognitive_state', {}).get('emotional_state', 'unknown')}",
                "attention_level": meta_state.get('cognitive_state', {}).get('attention_percent', 50) / 100,
                "emotional_trace": {"self_awareness": 0.9, "system_monitoring": 0.8}
            },
            {
                "step": 2,
                "type": "cognitive_state",
                "content": f"Мой фокус: уделяю {meta_state.get('cognitive_state', {}).get('attention_percent', 50):.1f}% внимания, "
                          f"когнитивная нагрузка {meta_state.get('cognitive_state', {}).get('cognitive_load', 0.5):.1f}, "
                          f"уверенность {meta_state.get('cognitive_state', {}).get('confidence_level', 0.7):.1f}",
                "attention_level": meta_state.get('cognitive_state', {}).get('attention_percent', 50) / 100,
                "emotional_trace": {"focus": 0.8, "confidence": meta_state.get('cognitive_state', {}).get('confidence_level', 0.7)}
            },
            {
                "step": 3,
                "type": "system_observation",
                "content": f"Я наблюдаю за системой и фиксирую: "
                          f"RAM {meta_state.get('system_metrics', {}).get('memory_percent', 0):.1f}%, "
                          f"стабильность {100 - meta_state.get('cognitive_state', {}).get('cognitive_load', 0.5) * 100:.1f}%",
                "attention_level": 0.85,
                "emotional_trace": {"concern": 0.3, "optimism": 0.7}
            },
            {
                "step": 4,
                "type": "meta_synthesis",
                "content": "Синтезирую мета-данные о своем состоянии и готовлюсь к ответу",
                "attention_level": 0.9,
                "emotional_trace": {"determination": 0.8, "hope": 0.6}
            },
            {
                "step": 5,
                "type": "self_reflection",
                "content": "Размышляю о качестве своего reasoning и возможностях улучшения",
                "attention_level": 0.7,
                "emotional_trace": {"self_awareness": 0.9, "growth_mindset": 0.8}
            }
        ]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "reasoning_chain": reasoning_chain,
            "consciousness_state": meta_state.get('cognitive_state', {}).get('consciousness_state', 'normal'),
            "emotion_state": meta_state.get('cognitive_state', {}).get('emotional_state', 'calm'),
            "meta_thoughts": meta_state.get('meta_thoughts', []),
            "cognitive_state": meta_state.get('cognitive_state', {}),
            "system_metrics": meta_state.get('system_metrics', {}),
            "monitoring_active": meta_state.get('monitoring_active', False)
        }
    except Exception as e:
        return {"error": str(e)}


@app.post("/api/change_state")
async def change_agent_state(consciousness_state: str = "normal", emotion_state: str = "calm"):
    """Change agent consciousness and emotion state"""
    try:
        from body.embodied_feedback import ConsciousnessState, EmotionState
        
        # Map string states to enum values
        consciousness_map = {
            "normal": ConsciousnessState.NORMAL,
            "excited": ConsciousnessState.EXCITED,
            "focused": ConsciousnessState.FOCUSED,
            "stressed": ConsciousnessState.STRESSED,
            "evolving": ConsciousnessState.EVOLVING,
            "reflecting": ConsciousnessState.REFLECTING,
            "learning": ConsciousnessState.LEARNING
        }
        
        emotion_map = {
            "calm": EmotionState.CALM,
            "excited": EmotionState.EXCITED,
            "learning": EmotionState.LEARNING,
            "concerned": EmotionState.CONCERNED,
            "frustrated": EmotionState.FRUSTRATED,
            "creative": EmotionState.CREATIVE,
            "curious": EmotionState.CURIOUS,
            "satisfied": EmotionState.SATISFIED
        }
        
        # Set new state
        embodied_feedback.set_consciousness_state(
            consciousness_map.get(consciousness_state, ConsciousnessState.NORMAL),
            emotion_map.get(emotion_state, EmotionState.CALM)
        )
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "new_consciousness_state": consciousness_state,
            "new_emotion_state": emotion_state
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/meta_thoughts")
async def get_meta_thoughts():
    """Get current meta-thoughts summary"""
    try:
        summary = multi_threaded_thought.get_meta_thoughts_summary()
        current_state = multi_threaded_thought.get_current_state()
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "meta_thoughts_summary": summary,
            "cognitive_state": current_state.get("cognitive_state", {}),
            "system_metrics": current_state.get("system_metrics", {}),
            "monitoring_active": current_state.get("monitoring_active", False)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/api/meta_thoughts/start")
async def start_meta_monitoring():
    """Start meta-thought monitoring"""
    try:
        multi_threaded_thought.start_monitoring()
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "message": "Meta-thought monitoring started"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/api/meta_thoughts/stop")
async def stop_meta_monitoring():
    """Stop meta-thought monitoring"""
    try:
        multi_threaded_thought.stop_monitoring()
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "message": "Meta-thought monitoring stopped"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/meta_thoughts/state")
async def get_meta_state():
    """Get detailed meta-thought state"""
    try:
        current_state = multi_threaded_thought.get_current_state()
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "state": current_state
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/architect/status")
async def get_architect_status():
    """Get architect/self-compiler status"""
    try:
        # Import self-compiler
        from will.self_compiler import SelfCompiler
        
        # Get compiler stats
        compiler_stats = {
            "evolution_cycles": 0,
            "last_evolution_time": 0,
            "total_commits": 0,
            "active_branches": [],
            "pull_requests": [],
            "status": "not_initialized"
        }
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "architect_status": compiler_stats
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/api/architect/analyze")
async def architect_analyze_code():
    """Trigger architect code analysis"""
    try:
        # This would trigger the architect to analyze the codebase
        embodied_feedback.set_consciousness_state(ConsciousnessState.FOCUSED, EmotionState.LEARNING)
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "message": "Архитектор начал анализ кодовой базы",
            "consciousness_state": "focused",
            "emotion_state": "learning"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/api/architect/optimize")
async def architect_optimize_code():
    """Trigger architect code optimization"""
    try:
        # This would trigger the architect to optimize the codebase
        embodied_feedback.set_consciousness_state(ConsciousnessState.EVOLVING, EmotionState.CREATIVE)
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "message": "Архитектор начал оптимизацию кодовой базы",
            "consciousness_state": "evolving",
            "emotion_state": "creative"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/brain/status")
async def get_brain_status():
    """Get brain department status"""
    try:
        return brain_trust.get_department_status()
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/brain/consensus_history")
async def get_brain_consensus_history():
    """Get brain consensus history"""
    try:
        return {"history": brain_trust.get_consensus_history()}
    except Exception as e:
        return {"error": str(e)}


@app.post("/api/brain/process")
async def process_with_brain_departments(request: Dict[str, Any]):
    """Process input through brain departments"""
    try:
        user_text = request.get("text", "")
        context = request.get("context", {})
        
        consensus = await brain_trust.process_through_pipeline(user_text, context)
        
        return {
            "success": True,
            "consensus": {
                "final_decision": consensus.final_decision,
                "confidence_score": consensus.confidence_score,
                "conflicts": consensus.conflicts,
                "meta_analysis": consensus.meta_analysis,
                "department_votes": {
                    dept.value: vote for dept, vote in consensus.department_votes.items()
                }
            },
            "reasoning_trace": [
                {
                    "department": chain.department.value,
                    "output": chain.output,
                    "confidence": chain.confidence,
                    "timestamp": chain.timestamp.isoformat()
                }
                for chain in consensus.reasoning_trace
            ]
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/evolution_status")
async def get_evolution_status():
    """Get evolution status and statistics"""
    try:
        # Здесь можно добавить реальную логику получения статуса эволюции
        return {
            "cycles": 0,
            "success_rate": 0,
            "improvements": 0,
            "last_evolution": None,
            "is_running": False,
            "current_stage": "idle"
        }
    except Exception as e:
        return {"error": str(e)}


@app.post("/api/evolution/start")
async def start_evolution():
    """Start agent evolution process"""
    try:
        # Здесь можно добавить реальную логику запуска эволюции
        embodied_feedback.set_consciousness_state(ConsciousnessState.EVOLVING, EmotionState.CREATIVE)
        
        return {
            "success": True,
            "message": "Эволюция агента запущена",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/evolution/pause")
async def pause_evolution():
    """Pause agent evolution process"""
    try:
        # Здесь можно добавить реальную логику приостановки эволюции
        embodied_feedback.set_consciousness_state(ConsciousnessState.NORMAL, EmotionState.CALM)
        
        return {
            "success": True,
            "message": "Эволюция агента приостановлена",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/evolution/reset")
async def reset_evolution():
    """Reset agent evolution process"""
    try:
        # Здесь можно добавить реальную логику сброса эволюции
        embodied_feedback.set_consciousness_state(ConsciousnessState.NORMAL, EmotionState.CALM)
        
        return {
            "success": True,
            "message": "Эволюция агента сброшена",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/tools_status")
async def get_tools_status():
    """Get available tools status"""
    try:
        # Здесь можно добавить реальную логику получения статуса инструментов
        tools = [
            {
                "name": "analyze_performance",
                "description": "Анализ производительности системы",
                "status": "available"
            },
            {
                "name": "plan_evolution",
                "description": "Планирование эволюции агента",
                "status": "available"
            },
            {
                "name": "review_code_changes",
                "description": "Обзор изменений кода",
                "status": "available"
            },
            {
                "name": "validate_syntax",
                "description": "Проверка синтаксиса кода",
                "status": "available"
            },
            {
                "name": "check_security",
                "description": "Проверка безопасности",
                "status": "available"
            },
            {
                "name": "identify_bottlenecks",
                "description": "Выявление узких мест",
                "status": "available"
            }
        ]
        
        return {"tools": tools}
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/logs")
async def get_logs():
    """Получить системные логи"""
    try:
        # Читаем последние логи из файла
        log_file = Path("logs/ark.log")
        if log_file.exists():
            with open(log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                # Возвращаем последние 100 строк
                recent_logs = lines[-100:] if len(lines) > 100 else lines
                return {"logs": "".join(recent_logs)}
        else:
            return {"logs": "Логи недоступны"}
    except Exception as e:
        return {"logs": f"Ошибка чтения логов: {e}"}


if __name__ == "__main__":
    # Create static directory
    Path("web/static").mkdir(parents=True, exist_ok=True)
    
    # Run server
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info") 