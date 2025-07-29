#!/usr/bin/env python3
"""
Auto Reporter System
Automatically generates and sends reports about system status
"""

import time
import logging
import threading
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from body.embodied_feedback import embodied_feedback, ConsciousnessState, EmotionState


class AutoReporter:
    """Automatic reporting system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._reporting = False
        self._report_thread = None
        self.report_interval = 60  # seconds
        
        # Report storage
        self.reports_dir = Path("logs/reports")
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def start_reporting(self):
        """Start automatic reporting"""
        if self._reporting:
            return
        
        self._reporting = True
        self._report_thread = threading.Thread(target=self._report_loop, daemon=True)
        self._report_thread.start()
        self.logger.info("Auto-reporting started")
    
    def stop_reporting(self):
        """Stop automatic reporting"""
        self._reporting = False
        if self._report_thread:
            self._report_thread.join(timeout=1)
        self.logger.info("Auto-reporting stopped")
    
    def _report_loop(self):
        """Main reporting loop"""
        while self._reporting:
            try:
                self._generate_report()
                time.sleep(self.report_interval)
            except Exception as e:
                self.logger.error(f"Error in report loop: {e}")
                time.sleep(10)
    
    def _generate_report(self):
        """Generate current status report"""
        try:
            # Get embodied feedback data
            feedback = embodied_feedback.get_feedback_summary()
            
            # Create report
            report = {
                "timestamp": datetime.now().isoformat(),
                "status": "active",
                "feedback": feedback,
                "system_health": self._get_system_health(),
                "consciousness_state": feedback.get("consciousness_state", "unknown"),
                "emotion_state": feedback.get("emotion_state", "unknown")
            }
            
            # Save report
            self._save_report(report)
            
            # Log summary
            self.logger.info(f"Report generated: {report['consciousness_state']} - {report['emotion_state']}")
            
        except Exception as e:
            self.logger.error(f"Failed to generate report: {e}")
    
    def _get_system_health(self) -> Dict[str, Any]:
        """Get system health metrics"""
        try:
            # This would include more detailed system metrics
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Failed to get system health: {e}")
            return {"status": "unknown", "error": str(e)}
    
    def _save_report(self, report: Dict[str, Any]):
        """Save report to file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"report_{timestamp}.json"
            filepath = self.reports_dir / filename
            
            import json
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            self.logger.error(f"Failed to save report: {e}")
    
    def get_latest_report(self) -> Optional[Dict[str, Any]]:
        """Get the latest report"""
        try:
            report_files = list(self.reports_dir.glob("report_*.json"))
            if not report_files:
                return None
            
            latest_file = max(report_files, key=lambda x: x.stat().st_mtime)
            
            import json
            with open(latest_file, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            self.logger.error(f"Failed to get latest report: {e}")
            return None


# Global instance
auto_reporter = AutoReporter() 