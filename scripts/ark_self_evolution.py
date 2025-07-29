#!/usr/bin/env python3
"""
ARK Self-Evolution Agent
Launches ARK Agent in self-evolution mode with real-time documentation
"""

import asyncio
import json
import logging
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import requests

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import Ark
from utils.secret_loader import get_secret


class ARKSelfEvolutionAgent:
    """ARK Agent running in self-evolution mode with real-time documentation"""
    
    def __init__(self):
        self.app = FastAPI(title="ARK Self-Evolution Agent", version="2.8")
        self.setup_cors()
        self.setup_routes()
        
        self.ark_agent = None
        self.evolution_log: List[Dict[str, Any]] = []
        self.active_connections: List[WebSocket] = []
        self.evolution_active = False
        self.improvement_thread = None
        
        self.logger = logging.getLogger(__name__)
        
    def setup_cors(self):
        """Setup CORS middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def setup_routes(self):
        """Setup API routes"""
        
        @self.app.get("/")
        async def get_evolution_dashboard():
            return HTMLResponse(self.get_dashboard_html())
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await self.handle_websocket(websocket)
        
        @self.app.get("/api/agent/status")
        async def get_agent_status():
            return self.get_agent_status()
        
        @self.app.get("/api/evolution/log")
        async def get_evolution_log():
            return {"log": self.evolution_log}
        
        @self.app.post("/api/evolution/start")
        async def start_evolution():
            return await self.start_self_evolution()
        
        @self.app.post("/api/evolution/stop")
        async def stop_evolution():
            return await self.stop_self_evolution()
        
        @self.app.post("/api/agent/improve")
        async def trigger_improvement():
            return await self.trigger_agent_improvement()
        
        @self.app.get("/api/github/status")
        async def get_github_status():
            return self.get_github_status()
        
        @self.app.post("/api/github/commit")
        async def commit_improvements():
            return await self.commit_improvements()
    
    def get_dashboard_html(self) -> str:
        """Generate self-evolution dashboard HTML"""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>ARK Self-Evolution Agent</title>
    <meta charset="utf-8">
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #0a0a0a; color: #00ff00; }
        .container { max-width: 1400px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .status-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-bottom: 30px; }
        .status-card { background: #1a1a1a; padding: 20px; border-radius: 10px; border: 1px solid #333; }
        .evolution-log { background: #1a1a1a; padding: 20px; border-radius: 10px; border: 1px solid #333; height: 500px; overflow-y: auto; }
        .log-entry { margin-bottom: 10px; padding: 10px; background: #2a2a2a; border-radius: 5px; }
        .log-entry.info { border-left: 3px solid #00ff00; }
        .log-entry.warning { border-left: 3px solid #ffff00; }
        .log-entry.error { border-left: 3px solid #ff0000; }
        .log-entry.success { border-left: 3px solid #00ffff; }
        .controls { text-align: center; margin-bottom: 20px; }
        button { background: #00ff00; color: #000; border: none; padding: 10px 20px; margin: 5px; border-radius: 5px; cursor: pointer; }
        button:hover { background: #00cc00; }
        button:disabled { background: #666; cursor: not-allowed; }
        .metric { display: flex; justify-content: space-between; margin: 5px 0; }
        .metric-value { font-weight: bold; color: #00ffff; }
        .real-time { background: #1a1a1a; padding: 20px; border-radius: 10px; border: 1px solid #333; margin-top: 20px; }
        .github-status { background: #1a1a1a; padding: 20px; border-radius: 10px; border: 1px solid #333; margin-top: 20px; }
        .progress-bar { width: 100%; height: 20px; background: #333; border-radius: 10px; overflow: hidden; }
        .progress-fill { height: 100%; background: #00ff00; transition: width 0.3s; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 ARK Self-Evolution Agent</h1>
            <p>Autonomous Self-Improvement with Real-time Documentation</p>
        </div>
        
        <div class="controls">
            <button onclick="startEvolution()" id="startBtn">🚀 Start Self-Evolution</button>
            <button onclick="stopEvolution()" id="stopBtn" disabled>⏹️ Stop Evolution</button>
            <button onclick="triggerImprovement()" id="improveBtn">🔧 Trigger Improvement</button>
            <button onclick="commitImprovements()" id="commitBtn">💾 Commit Improvements</button>
            <button onclick="clearLog()" id="clearBtn">🗑️ Clear Log</button>
        </div>
        
        <div class="status-grid">
            <div class="status-card">
                <h3>🔄 Evolution Status</h3>
                <div id="evolutionStatus">Loading...</div>
            </div>
            <div class="status-card">
                <h3>🤖 Agent Status</h3>
                <div id="agentStatus">Loading...</div>
            </div>
            <div class="status-card">
                <h3>📊 Performance</h3>
                <div id="performanceStatus">Loading...</div>
            </div>
        </div>
        
        <div class="real-time">
            <h3>📊 Real-time Metrics</h3>
            <div id="realTimeMetrics">Loading...</div>
        </div>
        
        <div class="github-status">
            <h3>🔗 GitHub Integration</h3>
            <div id="githubStatus">Loading...</div>
        </div>
        
        <div class="evolution-log">
            <h3>📝 Self-Evolution Log</h3>
            <div id="evolutionLog">Waiting for evolution events...</div>
        </div>
    </div>
    
    <script>
        let ws = null;
        let evolutionActive = false;
        
        function connectWebSocket() {
            ws = new WebSocket(`ws://${window.location.host}/ws`);
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                handleWebSocketMessage(data);
            };
            ws.onclose = function() {
                setTimeout(connectWebSocket, 1000);
            };
        }
        
        function handleWebSocketMessage(data) {
            if (data.type === 'evolution_event') {
                addLogEntry(data.message, data.level || 'info');
            } else if (data.type === 'agent_status') {
                updateAgentStatus(data);
            } else if (data.type === 'evolution_status') {
                updateEvolutionStatus(data);
            } else if (data.type === 'performance_status') {
                updatePerformanceStatus(data);
            } else if (data.type === 'github_status') {
                updateGitHubStatus(data);
            } else if (data.type === 'real_time_metrics') {
                updateRealTimeMetrics(data);
            }
        }
        
        function addLogEntry(message, level) {
            const logDiv = document.getElementById('evolutionLog');
            const entry = document.createElement('div');
            entry.className = `log-entry ${level}`;
            entry.innerHTML = `<strong>[${new Date().toLocaleTimeString()}]</strong> ${message}`;
            logDiv.appendChild(entry);
            logDiv.scrollTop = logDiv.scrollHeight;
        }
        
        function updateAgentStatus(data) {
            const statusDiv = document.getElementById('agentStatus');
            statusDiv.innerHTML = `
                <div class="metric">
                    <span>Consciousness:</span>
                    <span class="metric-value">${data.consciousness_state}</span>
                </div>
                <div class="metric">
                    <span>Emotion:</span>
                    <span class="metric-value">${data.emotion_state}</span>
                </div>
                <div class="metric">
                    <span>Memory Size:</span>
                    <span class="metric-value">${data.memory_size}</span>
                </div>
                <div class="metric">
                    <span>Evolution Cycles:</span>
                    <span class="metric-value">${data.evolution_cycles}</span>
                </div>
            `;
        }
        
        function updateEvolutionStatus(data) {
            const statusDiv = document.getElementById('evolutionStatus');
            statusDiv.innerHTML = `
                <div class="metric">
                    <span>Status:</span>
                    <span class="metric-value">${data.status}</span>
                </div>
                <div class="metric">
                    <span>Cycles Completed:</span>
                    <span class="metric-value">${data.cycles_completed}</span>
                </div>
                <div class="metric">
                    <span>Success Rate:</span>
                    <span class="metric-value">${data.success_rate}%</span>
                </div>
                <div class="metric">
                    <span>Last Evolution:</span>
                    <span class="metric-value">${data.last_evolution}</span>
                </div>
            `;
        }
        
        function updatePerformanceStatus(data) {
            const statusDiv = document.getElementById('performanceStatus');
            statusDiv.innerHTML = `
                <div class="metric">
                    <span>CPU Usage:</span>
                    <span class="metric-value">${data.cpu_percent}%</span>
                </div>
                <div class="metric">
                    <span>Memory Usage:</span>
                    <span class="metric-value">${data.memory_percent}%</span>
                </div>
                <div class="metric">
                    <span>Temperature:</span>
                    <span class="metric-value">${data.temperature}°C</span>
                </div>
                <div class="metric">
                    <span>Response Time:</span>
                    <span class="metric-value">${data.response_time}ms</span>
                </div>
            `;
        }
        
        function updateGitHubStatus(data) {
            const statusDiv = document.getElementById('githubStatus');
            statusDiv.innerHTML = `
                <div class="metric">
                    <span>Repository:</span>
                    <span class="metric-value">${data.repository}</span>
                </div>
                <div class="metric">
                    <span>Branch:</span>
                    <span class="metric-value">${data.branch}</span>
                </div>
                <div class="metric">
                    <span>Last Commit:</span>
                    <span class="metric-value">${data.last_commit}</span>
                </div>
                <div class="metric">
                    <span>Status:</span>
                    <span class="metric-value">${data.status}</span>
                </div>
            `;
        }
        
        function updateRealTimeMetrics(data) {
            const metricsDiv = document.getElementById('realTimeMetrics');
            metricsDiv.innerHTML = `
                <div class="metric">
                    <span>CPU Usage:</span>
                    <span class="metric-value">${data.cpu_percent}%</span>
                </div>
                <div class="metric">
                    <span>Memory Usage:</span>
                    <span class="metric-value">${data.memory_percent}%</span>
                </div>
                <div class="metric">
                    <span>Temperature:</span>
                    <span class="metric-value">${data.temperature}°C</span>
                </div>
                <div class="metric">
                    <span>Response Time:</span>
                    <span class="metric-value">${data.response_time}ms</span>
                </div>
            `;
        }
        
        async function startEvolution() {
            try {
                const response = await fetch('/api/evolution/start', { method: 'POST' });
                const result = await response.json();
                if (result.success) {
                    evolutionActive = true;
                    document.getElementById('startBtn').disabled = true;
                    document.getElementById('stopBtn').disabled = false;
                    addLogEntry('Self-evolution process started', 'success');
                } else {
                    addLogEntry(`Failed to start evolution: ${result.error}`, 'error');
                }
            } catch (error) {
                addLogEntry(`Error starting evolution: ${error}`, 'error');
            }
        }
        
        async function stopEvolution() {
            try {
                const response = await fetch('/api/evolution/stop', { method: 'POST' });
                const result = await response.json();
                if (result.success) {
                    evolutionActive = false;
                    document.getElementById('startBtn').disabled = false;
                    document.getElementById('stopBtn').disabled = true;
                    addLogEntry('Self-evolution process stopped', 'warning');
                } else {
                    addLogEntry(`Failed to stop evolution: ${result.error}`, 'error');
                }
            } catch (error) {
                addLogEntry(`Error stopping evolution: ${error}`, 'error');
            }
        }
        
        async function triggerImprovement() {
            try {
                const response = await fetch('/api/agent/improve', { method: 'POST' });
                const result = await response.json();
                if (result.success) {
                    addLogEntry('Improvement triggered successfully', 'success');
                } else {
                    addLogEntry(`Failed to trigger improvement: ${result.error}`, 'error');
                }
            } catch (error) {
                addLogEntry(`Error triggering improvement: ${error}`, 'error');
            }
        }
        
        async function commitImprovements() {
            try {
                const response = await fetch('/api/github/commit', { method: 'POST' });
                const result = await response.json();
                if (result.success) {
                    addLogEntry('Improvements committed to GitHub', 'success');
                } else {
                    addLogEntry(`Failed to commit improvements: ${result.error}`, 'error');
                }
            } catch (error) {
                addLogEntry(`Error committing improvements: ${error}`, 'error');
            }
        }
        
        function clearLog() {
            document.getElementById('evolutionLog').innerHTML = '';
            addLogEntry('Log cleared', 'info');
        }
        
        // Initialize
        connectWebSocket();
        setInterval(async () => {
            try {
                const response = await fetch('/api/agent/status');
                const data = await response.json();
                updateAgentStatus(data);
            } catch (error) {
                console.error('Error updating status:', error);
            }
        }, 5000);
    </script>
</body>
</html>
        """
    
    async def handle_websocket(self, websocket: WebSocket):
        """Handle WebSocket connections"""
        await websocket.accept()
        self.active_connections.append(websocket)
        
        try:
            while True:
                # Keep connection alive and send updates
                await asyncio.sleep(1)
        except WebSocketDisconnect:
            self.active_connections.remove(websocket)
    
    async def broadcast_evolution_event(self, message: str, level: str = "info"):
        """Broadcast evolution event to all connected clients"""
        event = {
            "type": "evolution_event",
            "message": message,
            "level": level,
            "timestamp": datetime.now().isoformat()
        }
        
        self.evolution_log.append(event)
        
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(event))
            except Exception as e:
                self.logger.error(f"Failed to send evolution event: {e}")
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        if not self.ark_agent:
            return {"error": "Agent not initialized"}
        
        try:
            return {
                "consciousness_state": self.ark_agent.mind["consciousness_core"].get_current_state().value,
                "emotion_state": "calm",  # TODO: Get from emotional core
                "memory_size": self.ark_agent.mind["consciousness_core"].get_memory_size(),
                "evolution_cycles": self.ark_agent._evolution_cycles
            }
        except Exception as e:
            self.logger.error(f"Error getting agent status: {e}")
            return {"error": str(e)}
    
    def get_github_status(self) -> Dict[str, Any]:
        """Get GitHub integration status"""
        try:
            token = get_secret('GITHUB_FINE_TOKEN')
            repo_url = get_secret('GIT_REPO_URL')
            
            if not token or not repo_url:
                return {"status": "not_configured", "error": "GitHub not configured"}
            
            # Extract repo info from URL
            if 'github.com' in repo_url:
                parts = repo_url.replace('https://github.com/', '').split('/')
                if len(parts) >= 2:
                    owner = parts[0]
                    repo = parts[1].replace('.git', '')
                else:
                    return {"status": "error", "error": "Invalid repository URL"}
            else:
                return {"status": "error", "error": "Invalid repository URL"}
            
            return {
                "repository": f"{owner}/{repo}",
                "branch": "main",
                "last_commit": "Recent",
                "status": "connected"
            }
            
        except Exception as e:
            self.logger.error(f"Error getting GitHub status: {e}")
            return {"status": "error", "error": str(e)}
    
    async def start_self_evolution(self) -> Dict[str, Any]:
        """Start the self-evolution process"""
        try:
            if self.evolution_active:
                return {"success": False, "error": "Evolution already active"}
            
            await self.broadcast_evolution_event("Initializing ARK Agent for self-evolution...", "info")
            
            # Initialize ARK agent
            self.ark_agent = Ark()
            await self.broadcast_evolution_event("ARK Agent initialized successfully", "success")
            
            # Start evolution monitoring in background
            self.evolution_active = True
            self.improvement_thread = threading.Thread(target=self.run_self_evolution_loop, daemon=True)
            self.improvement_thread.start()
            
            await self.broadcast_evolution_event("Self-evolution monitoring started", "success")
            return {"success": True}
            
        except Exception as e:
            self.logger.error(f"Error starting self-evolution: {e}")
            await self.broadcast_evolution_event(f"Error starting self-evolution: {e}", "error")
            return {"success": False, "error": str(e)}
    
    async def stop_self_evolution(self) -> Dict[str, Any]:
        """Stop the self-evolution process"""
        try:
            self.evolution_active = False
            if self.ark_agent:
                self.ark_agent.shutdown()
            
            await self.broadcast_evolution_event("Self-evolution process stopped", "warning")
            return {"success": True}
            
        except Exception as e:
            self.logger.error(f"Error stopping self-evolution: {e}")
            return {"success": False, "error": str(e)}
    
    async def trigger_agent_improvement(self) -> Dict[str, Any]:
        """Trigger an improvement cycle"""
        try:
            if not self.ark_agent:
                return {"success": False, "error": "Agent not initialized"}
            
            await self.broadcast_evolution_event("Triggering improvement cycle...", "info")
            
            # Run improvement cycle
            improvement_result = await self.run_improvement_cycle()
            
            await self.broadcast_evolution_event(f"Improvement cycle completed: {improvement_result}", "success")
            return {"success": True, "result": improvement_result}
            
        except Exception as e:
            self.logger.error(f"Error triggering improvement: {e}")
            await self.broadcast_evolution_event(f"Error in improvement cycle: {e}", "error")
            return {"success": False, "error": str(e)}
    
    async def commit_improvements(self) -> Dict[str, Any]:
        """Commit improvements to GitHub"""
        try:
            await self.broadcast_evolution_event("Committing improvements to GitHub...", "info")
            
            # This would use the GitHub integration to commit changes
            # For now, we'll simulate the process
            commit_result = "Simulated commit to GitHub"
            
            await self.broadcast_evolution_event(f"Improvements committed: {commit_result}", "success")
            return {"success": True, "result": commit_result}
            
        except Exception as e:
            self.logger.error(f"Error committing improvements: {e}")
            await self.broadcast_evolution_event(f"Error committing improvements: {e}", "error")
            return {"success": False, "error": str(e)}
    
    def run_self_evolution_loop(self):
        """Run the self-evolution monitoring loop"""
        try:
            while self.evolution_active:
                # Collect current metrics
                metrics = self.collect_agent_metrics()
                
                # Analyze for improvements
                improvements = self.analyze_for_improvements(metrics)
                
                # Apply improvements if found
                if improvements:
                    asyncio.run(self.broadcast_evolution_event(f"Found {len(improvements)} potential improvements", "info"))
                    for improvement in improvements:
                        asyncio.run(self.broadcast_evolution_event(f"Applying improvement: {improvement}", "info"))
                        # Apply the improvement
                        self.apply_improvement(improvement)
                
                # Update evolution cycles
                if self.ark_agent:
                    self.ark_agent._evolution_cycles += 1
                    self.ark_agent._last_evolution_time = time.time()
                
                time.sleep(60)  # Check every minute
                
        except Exception as e:
            self.logger.error(f"Error in self-evolution loop: {e}")
            asyncio.run(self.broadcast_evolution_event(f"Self-evolution error: {e}", "error"))
    
    def collect_agent_metrics(self) -> Dict[str, Any]:
        """Collect current agent metrics"""
        try:
            if not self.ark_agent:
                return {}
            
            return {
                "timestamp": time.time(),
                "consciousness_state": self.ark_agent.mind["consciousness_core"].get_current_state().value,
                "memory_size": self.ark_agent.mind["consciousness_core"].get_memory_size(),
                "evolution_cycles": self.ark_agent._evolution_cycles,
                "performance_metrics": self.ark_agent._get_performance_metrics()
            }
        except Exception as e:
            self.logger.error(f"Error collecting metrics: {e}")
            return {}
    
    def analyze_for_improvements(self, metrics: Dict[str, Any]) -> List[str]:
        """Analyze metrics for potential improvements"""
        improvements = []
        
        try:
            # Check memory usage
            memory_size = metrics.get("memory_size", 0)
            if memory_size > 1000:
                improvements.append("Optimize memory management")
            
            # Check consciousness state
            consciousness_state = metrics.get("consciousness_state", "unknown")
            if consciousness_state == "idle":
                improvements.append("Activate additional processing capabilities")
            
            # Check evolution cycles
            evolution_cycles = metrics.get("evolution_cycles", 0)
            if evolution_cycles == 0:
                improvements.append("Initialize first evolution cycle")
            
            # Check performance metrics
            performance = metrics.get("performance_metrics", {})
            if performance:
                cpu_percent = performance.get("system", {}).get("cpu_percent", 0)
                if cpu_percent > 80:
                    improvements.append("Optimize processing efficiency")
                
                response_times = performance.get("performance", {}).get("response_times", {})
                avg_response = response_times.get("average", 0)
                if avg_response > 5.0:
                    improvements.append("Optimize processing pipeline")
            
        except Exception as e:
            self.logger.error(f"Error analyzing improvements: {e}")
        
        return improvements
    
    def apply_improvement(self, improvement: str):
        """Apply a specific improvement"""
        try:
            # This would implement the actual improvement logic
            # For now, we'll log the improvement
            self.logger.info(f"Applying improvement: {improvement}")
            
            # In a real implementation, this would:
            # 1. Generate code changes
            # 2. Test the changes
            # 3. Apply successful changes
            # 4. Update documentation
            
        except Exception as e:
            self.logger.error(f"Error applying improvement: {e}")
    
    async def run_improvement_cycle(self) -> str:
        """Run a single improvement cycle"""
        try:
            # This would trigger the actual self-improvement logic
            # For now, we'll simulate an improvement
            improvement_result = "Simulated improvement cycle completed"
            
            # In a real implementation, this would:
            # 1. Analyze current performance
            # 2. Identify bottlenecks
            # 3. Generate improvements
            # 4. Test improvements
            # 5. Apply successful improvements
            
            return improvement_result
            
        except Exception as e:
            self.logger.error(f"Error in improvement cycle: {e}")
            return f"Error: {e}"


def main():
    """Start the ARK Self-Evolution Agent"""
    agent = ARKSelfEvolutionAgent()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🚀 Starting ARK Self-Evolution Agent...")
    print("📊 Dashboard available at: http://localhost:8081")
    print("🔗 WebSocket endpoint: ws://localhost:8081/ws")
    print("🤖 Agent will continuously self-improve and document the process")
    
    # Start the server
    uvicorn.run(
        agent.app,
        host="0.0.0.0",
        port=8081,
        log_level="info"
    )


if __name__ == "__main__":
    main() 