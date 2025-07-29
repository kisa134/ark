#!/usr/bin/env python3
"""
ARK Monitoring Console - Enhanced Interface with Embodied Feedback
Provides real-time monitoring, consciousness visualization, and manual control
"""

import os
import sys
import time
import json
import logging
import threading
from typing import Dict, Any, List, Optional
from pathlib import Path
import curses
import signal

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from body.embodied_feedback import embodied_feedback, ConsciousnessState, EmotionState
from evaluation.auto_reporter import auto_reporter
from evaluation.consciousness_monitor import ConsciousnessMonitor
from will.self_compiler import SelfCompiler
from psyche.crew import CrewManager
from main import Ark


class MonitoringConsole:
    """Enhanced monitoring console with embodied feedback"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize systems
        self.ark = None
        self.consciousness_monitor = None
        self.self_compiler = None
        self.crew_manager = None
        
        # Display settings
        self.refresh_rate = 1.0  # seconds
        self.running = False
        self.screen = None
        
        # Data storage
        self.current_data = {}
        self.historical_data = []
        self.alerts = []
        
        # Color pairs for curses
        self.colors = {
            'normal': 1,
            'warning': 2,
            'error': 3,
            'success': 4,
            'info': 5,
            'consciousness': 6,
            'physical': 7
        }
        
        self.logger.info("ARK Monitoring Console initialized")
    
    def initialize_systems(self):
        """Initialize all ARK systems"""
        try:
            # Initialize ARK
            self.ark = Ark()
            self.ark.initialize()
            
            # Initialize monitoring systems
            self.consciousness_monitor = ConsciousnessMonitor()
            self.self_compiler = SelfCompiler()
            self.crew_manager = CrewManager()
            
            # Start embodied feedback
            embodied_feedback.start_monitoring()
            
            # Start auto-reporting
            auto_reporter.start_reporting()
            
            self.logger.info("All systems initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize systems: {e}")
            return False
    
    def setup_curses(self):
        """Setup curses interface"""
        try:
            self.screen = curses.initscr()
            curses.start_color()
            curses.use_default_colors()
            curses.curs_set(0)  # Hide cursor
            curses.noecho()
            curses.cbreak()
            
            # Initialize color pairs
            curses.init_pair(1, curses.COLOR_WHITE, -1)      # Normal
            curses.init_pair(2, curses.COLOR_YELLOW, -1)     # Warning
            curses.init_pair(3, curses.COLOR_RED, -1)        # Error
            curses.init_pair(4, curses.COLOR_GREEN, -1)      # Success
            curses.init_pair(5, curses.COLOR_CYAN, -1)       # Info
            curses.init_pair(6, curses.COLOR_MAGENTA, -1)    # Consciousness
            curses.init_pair(7, curses.COLOR_BLUE, -1)       # Physical
            
            self.logger.info("Curses interface initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to setup curses: {e}")
            return False
    
    def cleanup_curses(self):
        """Cleanup curses interface"""
        if self.screen:
            curses.nocbreak()
            curses.echo()
            curses.curs_set(1)
            curses.endwin()
    
    def run(self):
        """Main console loop"""
        if not self.initialize_systems():
            print("Failed to initialize systems")
            return
        
        if not self.setup_curses():
            print("Failed to setup interface")
            return
        
        try:
            self.running = True
            
            # Start data collection thread
            data_thread = threading.Thread(target=self._data_collection_loop)
            data_thread.daemon = True
            data_thread.start()
            
            # Main display loop
            while self.running:
                try:
                    self._update_display()
                    time.sleep(self.refresh_rate)
                    
                except KeyboardInterrupt:
                    self.running = False
                    break
                except Exception as e:
                    self.logger.error(f"Display loop error: {e}")
                    time.sleep(1)
            
        finally:
            self.cleanup_curses()
            self._cleanup_systems()
    
    def _data_collection_loop(self):
        """Background data collection loop"""
        while self.running:
            try:
                # Collect current data
                self.current_data = self._collect_current_data()
                
                # Store historical data (keep last 100 entries)
                self.historical_data.append({
                    'timestamp': time.time(),
                    'data': self.current_data.copy()
                })
                
                if len(self.historical_data) > 100:
                    self.historical_data.pop(0)
                
                # Check for alerts
                self._check_alerts()
                
                time.sleep(0.5)  # Update every 500ms
                
            except Exception as e:
                self.logger.error(f"Data collection error: {e}")
                time.sleep(1)
    
    def _collect_current_data(self) -> Dict[str, Any]:
        """Collect current system data"""
        data = {
            'timestamp': time.time(),
            'embodied_feedback': {},
            'consciousness': {},
            'physical': {},
            'evolution': {},
            'crew': {},
            'alerts': []
        }
        
        try:
            # Embodied feedback data
            feedback_summary = embodied_feedback.get_feedback_summary()
            if feedback_summary.get('status') != 'no_data':
                data['embodied_feedback'] = feedback_summary
            
            # Visual feedback
            visual_feedback = embodied_feedback.get_visual_feedback()
            data['visual_feedback'] = visual_feedback
            
            # Consciousness data
            if self.consciousness_monitor:
                data['consciousness'] = self.consciousness_monitor.get_status()
            
            # Physical metrics
            if feedback_summary.get('physical_metrics'):
                data['physical'] = feedback_summary['physical_metrics']
            
            # Evolution data
            if self.self_compiler:
                data['evolution'] = self.self_compiler.get_compiler_stats()
            
            # Crew data
            if self.crew_manager:
                data['crew'] = self.crew_manager.get_crew_manager_status()
            
            # Auto-reporting data
            data['auto_reporting'] = auto_reporter.get_reporting_summary()
            
        except Exception as e:
            self.logger.error(f"Data collection error: {e}")
        
        return data
    
    def _check_alerts(self):
        """Check for new alerts"""
        try:
            current_data = self.current_data
            
            # Physical alerts
            physical = current_data.get('physical', {})
            if physical.get('cpu_temperature', 0) > 80:
                self._add_alert('warning', f"High CPU temperature: {physical['cpu_temperature']}°C")
            
            if physical.get('memory_usage', 0) > 85:
                self._add_alert('warning', f"High memory usage: {physical['memory_usage']}%")
            
            # Consciousness alerts
            consciousness = current_data.get('consciousness', {})
            if consciousness.get('state') == 'error':
                self._add_alert('error', 'Consciousness error state detected')
            
            # Evolution alerts
            evolution = current_data.get('evolution', {})
            if evolution.get('rollbacks_performed', 0) > 5:
                self._add_alert('warning', f"Multiple rollbacks: {evolution['rollbacks_performed']}")
            
        except Exception as e:
            self.logger.error(f"Alert check error: {e}")
    
    def _add_alert(self, level: str, message: str):
        """Add new alert"""
        alert = {
            'timestamp': time.time(),
            'level': level,
            'message': message
        }
        
        # Keep only last 20 alerts
        self.alerts.append(alert)
        if len(self.alerts) > 20:
            self.alerts.pop(0)
    
    def _update_display(self):
        """Update the display"""
        if not self.screen:
            return
        
        try:
            self.screen.clear()
            height, width = self.screen.getmaxyx()
            
            # Header
            self._draw_header(width)
            
            # Main content
            content_height = height - 4  # Reserve space for header and footer
            self._draw_main_content(content_height, width)
            
            # Footer
            self._draw_footer(width, height)
            
            self.screen.refresh()
            
        except Exception as e:
            self.logger.error(f"Display update error: {e}")
    
    def _draw_header(self, width: int):
        """Draw header section"""
        header = "🤖 ARK Monitoring Console - Embodied Digital Organism"
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        self.screen.addstr(0, 0, header[:width-1], curses.color_pair(self.colors['info']))
        self.screen.addstr(1, 0, f"Time: {timestamp} | Status: {'🟢 Active' if self.running else '🔴 Inactive'}")
        
        # Separator
        self.screen.addstr(2, 0, "=" * width)
    
    def _draw_main_content(self, height: int, width: int):
        """Draw main content area"""
        if not self.current_data:
            self.screen.addstr(3, 0, "No data available")
            return
        
        row = 3
        
        # Visual feedback section
        visual = self.current_data.get('visual_feedback', {})
        if visual:
            self._draw_visual_feedback(row, width, visual)
            row += 4
        
        # Physical metrics section
        physical = self.current_data.get('physical', {})
        if physical:
            self._draw_physical_metrics(row, width, physical)
            row += 6
        
        # Consciousness section
        consciousness = self.current_data.get('consciousness', {})
        if consciousness:
            self._draw_consciousness_section(row, width, consciousness)
            row += 4
        
        # Evolution section
        evolution = self.current_data.get('evolution', {})
        if evolution:
            self._draw_evolution_section(row, width, evolution)
            row += 4
        
        # Alerts section
        if self.alerts:
            self._draw_alerts_section(row, width)
    
    def _draw_visual_feedback(self, row: int, width: int, visual: Dict[str, Any]):
        """Draw visual feedback section"""
        emoji = visual.get('emoji', '🤖')
        state = visual.get('state', 'unknown')
        emotion = visual.get('emotion', 'unknown')
        color = visual.get('color', '#00FF00')
        alerts = visual.get('alerts', 0)
        
        title = f"🎭 Embodied Feedback"
        self.screen.addstr(row, 0, title, curses.color_pair(self.colors['consciousness']))
        
        status_line = f"State: {emoji} {state} | Emotion: {emotion} | Alerts: {alerts}"
        self.screen.addstr(row + 1, 2, status_line)
        
        # Color indicator
        color_indicator = f"RGB: {'🟢' if visual.get('rgb_enabled') else '⚫'} {'Enabled' if visual.get('rgb_enabled') else 'Disabled'}"
        self.screen.addstr(row + 2, 2, color_indicator)
    
    def _draw_physical_metrics(self, row: int, width: int, physical: Dict[str, Any]):
        """Draw physical metrics section"""
        title = f"💻 Physical Metrics"
        self.screen.addstr(row, 0, title, curses.color_pair(self.colors['physical']))
        
        cpu_usage = physical.get('cpu_usage', 0)
        memory_usage = physical.get('memory_usage', 0)
        cpu_temp = physical.get('cpu_temperature', 0)
        gpu_temp = physical.get('gpu_temperature')
        disk_usage = physical.get('disk_usage', 0)
        
        # CPU and Memory
        self.screen.addstr(row + 1, 2, f"CPU: {cpu_usage:.1f}% | Memory: {memory_usage:.1f}%")
        
        # Temperature
        temp_line = f"CPU Temp: {cpu_temp:.1f}°C"
        if gpu_temp:
            temp_line += f" | GPU Temp: {gpu_temp:.1f}°C"
        self.screen.addstr(row + 2, 2, temp_line)
        
        # Disk and Network
        network_activity = physical.get('network_activity', 0)
        self.screen.addstr(row + 3, 2, f"Disk: {disk_usage:.1f}% | Network: {network_activity:.1f} MB/s")
        
        # Health indicators
        health_color = curses.color_pair(self.colors['normal'])
        if cpu_temp > 80 or memory_usage > 85:
            health_color = curses.color_pair(self.colors['warning'])
        
        health_status = "🟢 Healthy"
        if cpu_temp > 80:
            health_status = "🟡 Warning"
        if cpu_temp > 90 or memory_usage > 95:
            health_status = "🔴 Critical"
        
        self.screen.addstr(row + 4, 2, f"Health: {health_status}", health_color)
    
    def _draw_consciousness_section(self, row: int, width: int, consciousness: Dict[str, Any]):
        """Draw consciousness section"""
        title = f"🧠 Consciousness"
        self.screen.addstr(row, 0, title, curses.color_pair(self.colors['consciousness']))
        
        state = consciousness.get('state', 'unknown')
        attention = consciousness.get('attention_level', 0)
        memory = consciousness.get('memory_usage', 0)
        reasoning = consciousness.get('reasoning_activity', 0)
        
        self.screen.addstr(row + 1, 2, f"State: {state}")
        self.screen.addstr(row + 2, 2, f"Attention: {attention:.1%} | Memory: {memory:.1%} | Reasoning: {reasoning:.1%}")
        
        # Evolution progress
        evolution_progress = consciousness.get('evolution_progress', 0)
        self.screen.addstr(row + 3, 2, f"Evolution Progress: {evolution_progress:.1%}")
    
    def _draw_evolution_section(self, row: int, width: int, evolution: Dict[str, Any]):
        """Draw evolution section"""
        title = f"🧬 Evolution"
        self.screen.addstr(row, 0, title, curses.color_pair(self.colors['info']))
        
        commits = evolution.get('commits_created', 0)
        branches = evolution.get('branches_created', 0)
        files_modified = evolution.get('files_modified', 0)
        prs_created = evolution.get('prs_created', 0)
        rollbacks = evolution.get('rollbacks_performed', 0)
        
        self.screen.addstr(row + 1, 2, f"Commits: {commits} | Branches: {branches} | Files: {files_modified}")
        self.screen.addstr(row + 2, 2, f"PRs: {prs_created} | Rollbacks: {rollbacks}")
        
        # Status indicator
        status_color = curses.color_pair(self.colors['success'])
        if rollbacks > 5:
            status_color = curses.color_pair(self.colors['warning'])
        if rollbacks > 10:
            status_color = curses.color_pair(self.colors['error'])
        
        status = "🟢 Stable" if rollbacks <= 2 else "🟡 Unstable" if rollbacks <= 5 else "🔴 Critical"
        self.screen.addstr(row + 3, 2, f"Status: {status}", status_color)
    
    def _draw_alerts_section(self, row: int, width: int):
        """Draw alerts section"""
        if not self.alerts:
            return
        
        title = f"🚨 Recent Alerts"
        self.screen.addstr(row, 0, title, curses.color_pair(self.colors['error']))
        
        # Show last 5 alerts
        recent_alerts = self.alerts[-5:]
        for i, alert in enumerate(recent_alerts):
            if row + i + 1 >= curses.LINES - 2:  # Don't overflow
                break
            
            timestamp = time.strftime("%H:%M:%S", time.localtime(alert['timestamp']))
            level_icon = "🔴" if alert['level'] == 'error' else "🟡" if alert['level'] == 'warning' else "🔵"
            
            alert_line = f"{level_icon} {timestamp}: {alert['message']}"
            color = curses.color_pair(self.colors[alert['level']])
            
            self.screen.addstr(row + i + 1, 2, alert_line[:width-3], color)
    
    def _draw_footer(self, width: int, height: int):
        """Draw footer section"""
        footer = "Press 'q' to quit | 'r' to refresh | 's' to show status | 'h' for help"
        self.screen.addstr(height - 2, 0, "=" * width)
        self.screen.addstr(height - 1, 0, footer[:width-1])
    
    def _cleanup_systems(self):
        """Cleanup all systems"""
        try:
            # Stop monitoring
            embodied_feedback.stop_monitoring()
            auto_reporter.stop_reporting()
            
            # Stop ARK
            if self.ark:
                self.ark.shutdown()
            
            self.logger.info("All systems cleaned up")
            
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")
    
    def handle_input(self, key: str):
        """Handle user input"""
        if key == 'q':
            self.running = False
        elif key == 'r':
            # Force refresh
            pass
        elif key == 's':
            self._show_detailed_status()
        elif key == 'h':
            self._show_help()
    
    def _show_detailed_status(self):
        """Show detailed system status"""
        if not self.screen:
            return
        
        # Clear screen and show detailed status
        self.screen.clear()
        
        status_data = {
            'embodied_feedback': embodied_feedback.get_feedback_summary(),
            'auto_reporting': auto_reporter.get_reporting_summary(),
            'consciousness': self.consciousness_monitor.get_status() if self.consciousness_monitor else {},
            'evolution': self.self_compiler.get_compiler_stats() if self.self_compiler else {},
            'crew': self.crew_manager.get_crew_manager_status() if self.crew_manager else {}
        }
        
        # Display detailed status
        row = 0
        for system, data in status_data.items():
            self.screen.addstr(row, 0, f"=== {system.upper()} ===")
            row += 1
            
            for key, value in data.items():
                self.screen.addstr(row, 2, f"{key}: {value}")
                row += 1
            
            row += 1
        
        self.screen.addstr(row, 0, "Press any key to continue...")
        self.screen.refresh()
        self.screen.getch()
    
    def _show_help(self):
        """Show help information"""
        if not self.screen:
            return
        
        self.screen.clear()
        
        help_text = [
            "=== ARK Monitoring Console Help ===",
            "",
            "Controls:",
            "  q - Quit",
            "  r - Refresh display",
            "  s - Show detailed status",
            "  h - Show this help",
            "",
            "Sections:",
            "  🎭 Embodied Feedback - Visual state and emotions",
            "  💻 Physical Metrics - Hardware monitoring",
            "  🧠 Consciousness - Cognitive state",
            "  🧬 Evolution - Self-modification status",
            "  🚨 Alerts - System warnings and errors",
            "",
            "Colors:",
            "  🟢 Green - Normal/Healthy",
            "  🟡 Yellow - Warning",
            "  🔴 Red - Error/Critical",
            "  🔵 Blue - Info",
            "  🟣 Purple - Consciousness",
            "",
            "Press any key to continue..."
        ]
        
        for i, line in enumerate(help_text):
            if i < curses.LINES - 1:
                self.screen.addstr(i, 0, line)
        
        self.screen.refresh()
        self.screen.getch()


def main():
    """Main function"""
    console = MonitoringConsole()
    
    try:
        console.run()
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        console._cleanup_systems()


if __name__ == "__main__":
    main() 