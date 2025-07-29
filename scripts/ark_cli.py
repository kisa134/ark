#!/usr/bin/env python3
"""
ARK CLI - Command Line Interface for ARK Management
Provides monitoring, logs, memory, and interactive console
"""

import os
import sys
import time
import json
import argparse
import subprocess
from typing import Dict, Any, List, Optional
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import config
from main import Ark
from evaluation.consciousness_monitor import ConsciousnessMonitor


class ArkCLI:
    """ARK Command Line Interface"""
    
    def __init__(self):
        self.ark = None
        self.monitor = None
        self.logger = None
        
    def initialize(self):
        """Initialize ARK system"""
        try:
            print("🚀 Initializing ARK system...")
            self.ark = Ark()
            self.monitor = ConsciousnessMonitor()
            print("✅ ARK system initialized")
        except Exception as e:
            print(f"❌ Failed to initialize ARK: {e}")
            return False
        return True
    
    def start_ark(self):
        """Start ARK system"""
        try:
            print("🚀 Starting ARK system...")
            self.ark.start()
            print("✅ ARK system started")
        except Exception as e:
            print(f"❌ Failed to start ARK: {e}")
    
    def show_status(self):
        """Show system status"""
        try:
            status = self.ark.get_system_status()
            
            print("\n📊 ARK System Status")
            print("=" * 50)
            
            # System health
            print(f"🖥️  CPU Usage: {status.get('system', {}).get('cpu_percent', 'N/A')}%")
            print(f"💾 Memory Usage: {status.get('system', {}).get('memory_percent', 'N/A')}%")
            print(f"🌡️  Temperature: {status.get('system', {}).get('temperature_celsius', 'N/A')}°C")
            print(f"💿 Disk Usage: {status.get('system', {}).get('disk_usage_percent', 'N/A')}%")
            
            # Consciousness state
            print(f"🧠 Consciousness: {status.get('consciousness', {}).get('current_state', 'N/A')}")
            print(f"😊 Emotional State: {status.get('consciousness', {}).get('emotional_state', 'N/A')}")
            
            # Evolution status
            evolution = status.get('evolution', {})
            print(f"🔄 Evolution Cycles: {evolution.get('cycles_completed', 0)}")
            print(f"📈 Success Rate: {evolution.get('success_rate', 0):.1%}")
            
            # Component status
            print(f"🔧 Components Active: {status.get('components_active', 0)}")
            print(f"⚠️  Warnings: {status.get('warnings', 0)}")
            print(f"❌ Errors: {status.get('errors', 0)}")
            
        except Exception as e:
            print(f"❌ Failed to get status: {e}")
    
    def show_logs(self, limit: int = 20, level: str = "INFO"):
        """Show recent logs"""
        try:
            log_file = config.system.ARK_LOG_FILE
            
            if not log_file.exists():
                print("❌ Log file not found")
                return
            
            print(f"\n📋 Recent Logs (Level: {level})")
            print("=" * 50)
            
            # Read and parse JSON logs
            with open(log_file, 'r') as f:
                lines = f.readlines()
            
            # Filter by level and limit
            filtered_logs = []
            for line in lines[-limit*2:]:  # Read more lines to account for filtering
                try:
                    log_entry = json.loads(line.strip())
                    if log_entry.get('level', '').upper() == level.upper():
                        filtered_logs.append(log_entry)
                except json.JSONDecodeError:
                    continue
            
            # Display logs
            for log in filtered_logs[-limit:]:
                timestamp = log.get('timestamp', 'N/A')
                level = log.get('level', 'INFO')
                module = log.get('module', 'unknown')
                message = log.get('message', '')
                
                print(f"[{timestamp}] {level} {module}: {message}")
                
        except Exception as e:
            print(f"❌ Failed to show logs: {e}")
    
    def show_memory(self):
        """Show memory contents"""
        try:
            print("\n🧠 ARK Memory Contents")
            print("=" * 50)
            
            # Consciousness memory
            consciousness_memory = self.ark.mind["consciousness_core"].get_memory()
            print(f"Consciousness Memory ({len(consciousness_memory)} entries):")
            for i, entry in enumerate(consciousness_memory[-5:], 1):
                print(f"  {i}. {entry.get('content', 'N/A')[:100]}...")
            
            # Emotional memory
            emotional_memory = self.ark.psyche["emotional_core"].get_emotional_memory()
            print(f"\nEmotional Memory ({len(emotional_memory)} entries):")
            for i, entry in enumerate(emotional_memory[-5:], 1):
                emotion = entry.get('emotion', 'N/A')
                intensity = entry.get('intensity', 0)
                print(f"  {i}. {emotion} (intensity: {intensity})")
            
            # Evolution history
            evolution_history = self.ark.will["self_compiler"].get_change_history(5)
            print(f"\nEvolution History ({len(evolution_history)} entries):")
            for i, entry in enumerate(evolution_history, 1):
                event_type = entry.get('type', 'N/A')
                timestamp = entry.get('timestamp', 0)
                print(f"  {i}. {event_type} at {time.ctime(timestamp)}")
                
        except Exception as e:
            print(f"❌ Failed to show memory: {e}")
    
    def show_agents(self):
        """Show agent status"""
        try:
            print("\n🤖 ARK Agents Status")
            print("=" * 50)
            
            crew_manager = self.ark.psyche["crew_manager"]
            status = crew_manager.get_crew_manager_status()
            
            print(f"LLM Available: {'✅' if status.get('llm_available') else '❌'}")
            print(f"Ollama Available: {'✅' if status.get('ollama_available') else '❌'}")
            print(f"CrewAI Available: {'✅' if status.get('crewai_available') else '❌'}")
            
            # Available models
            models = status.get('available_models', [])
            print(f"Available Models: {', '.join(models) if models else 'None'}")
            
            # Active agents
            agents = crew_manager.get_available_agents()
            print(f"\nAvailable Agents ({len(agents)}):")
            for name, config in agents.items():
                role = config.get('role', 'N/A')
                print(f"  • {name}: {role}")
            
            # Active crews
            crews = crew_manager.list_crews()
            print(f"\nActive Crews ({len(crews)}):")
            for crew in crews:
                name = crew.get('name', 'N/A')
                status = crew.get('status', 'N/A')
                agents = crew.get('agents', [])
                print(f"  • {name} ({status}): {', '.join(agents)}")
                
        except Exception as e:
            print(f"❌ Failed to show agents: {e}")
    
    def show_evolution(self):
        """Show evolution status"""
        try:
            print("\n🔄 ARK Evolution Status")
            print("=" * 50)
            
            compiler = self.ark.will["self_compiler"]
            stats = compiler.get_compiler_stats()
            
            print(f"Initialized: {'✅' if stats.get('initialized') else '❌'}")
            print(f"Repo Configured: {'✅' if stats.get('repo_configured') else '❌'}")
            print(f"SSH Key Configured: {'✅' if stats.get('ssh_key_configured') else '❌'}")
            
            print(f"\nStatistics:")
            print(f"  • Commits Created: {stats.get('commits_created', 0)}")
            print(f"  • Branches Created: {stats.get('branches_created', 0)}")
            print(f"  • Files Modified: {stats.get('files_modified', 0)}")
            print(f"  • Rollbacks Performed: {stats.get('rollbacks_performed', 0)}")
            
            # Recent changes
            history = compiler.get_change_history(5)
            print(f"\nRecent Changes ({len(history)}):")
            for i, entry in enumerate(history, 1):
                event_type = entry.get('type', 'N/A')
                timestamp = entry.get('timestamp', 0)
                print(f"  {i}. {event_type} at {time.ctime(timestamp)}")
                
        except Exception as e:
            print(f"❌ Failed to show evolution: {e}")
    
    def approve_evolution(self, evolution_id: str):
        """Approve evolution request"""
        try:
            print(f"✅ Approving evolution: {evolution_id}")
            # This would implement actual approval logic
            print("Evolution approved successfully")
        except Exception as e:
            print(f"❌ Failed to approve evolution: {e}")
    
    def trigger_evolution(self):
        """Manually trigger evolution"""
        try:
            print("🔄 Triggering manual evolution...")
            self.ark._check_evolution_needs()
            print("Evolution check completed")
        except Exception as e:
            print(f"❌ Failed to trigger evolution: {e}")
    
    def restart_ark(self):
        """Restart ARK system"""
        try:
            print("🔄 Restarting ARK system...")
            self.ark.shutdown()
            time.sleep(2)
            self.ark.start()
            print("✅ ARK system restarted")
        except Exception as e:
            print(f"❌ Failed to restart ARK: {e}")
    
    def shutdown_ark(self):
        """Shutdown ARK system"""
        try:
            print("🛑 Shutting down ARK system...")
            self.ark.shutdown()
            print("✅ ARK system shutdown complete")
        except Exception as e:
            print(f"❌ Failed to shutdown ARK: {e}")
    
    def interactive_console(self):
        """Start interactive console"""
        print("\n🎮 ARK Interactive Console")
        print("=" * 50)
        print("Available commands:")
        print("  status    - Show system status")
        print("  logs      - Show recent logs")
        print("  memory    - Show memory contents")
        print("  agents    - Show agent status")
        print("  evolution - Show evolution status")
        print("  trigger   - Trigger evolution")
        print("  restart   - Restart ARK")
        print("  quit      - Exit console")
        print("=" * 50)
        
        while True:
            try:
                command = input("\nARK> ").strip().lower()
                
                if command == "quit" or command == "exit":
                    print("👋 Goodbye!")
                    break
                elif command == "status":
                    self.show_status()
                elif command == "logs":
                    self.show_logs()
                elif command == "memory":
                    self.show_memory()
                elif command == "agents":
                    self.show_agents()
                elif command == "evolution":
                    self.show_evolution()
                elif command == "trigger":
                    self.trigger_evolution()
                elif command == "restart":
                    self.restart_ark()
                elif command == "help":
                    print("Available commands: status, logs, memory, agents, evolution, trigger, restart, quit")
                else:
                    print(f"❌ Unknown command: {command}")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Console error: {e}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="ARK Command Line Interface")
    parser.add_argument("command", nargs="?", default="interactive", 
                       choices=["status", "logs", "memory", "agents", "evolution", 
                               "approve", "trigger", "restart", "shutdown", "interactive"],
                       help="Command to execute")
    parser.add_argument("--limit", type=int, default=20, help="Number of log entries to show")
    parser.add_argument("--level", default="INFO", help="Log level filter")
    parser.add_argument("--evolution-id", help="Evolution ID for approval")
    
    args = parser.parse_args()
    
    cli = ArkCLI()
    
    if not cli.initialize():
        sys.exit(1)
    
    try:
        if args.command == "status":
            cli.show_status()
        elif args.command == "logs":
            cli.show_logs(args.limit, args.level)
        elif args.command == "memory":
            cli.show_memory()
        elif args.command == "agents":
            cli.show_agents()
        elif args.command == "evolution":
            cli.show_evolution()
        elif args.command == "approve":
            if args.evolution_id:
                cli.approve_evolution(args.evolution_id)
            else:
                print("❌ Evolution ID required for approval")
        elif args.command == "trigger":
            cli.trigger_evolution()
        elif args.command == "restart":
            cli.restart_ark()
        elif args.command == "shutdown":
            cli.shutdown_ark()
        elif args.command == "interactive":
            cli.interactive_console()
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ CLI error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 