"""Logging utilities for the application"""
import logging
import sys
from datetime import datetime
from pathlib import Path
import json
from typing import Dict, Any, Optional
import streamlit as st

class AppLogger:
    """Application logger with structured logging"""
    
    def __init__(self, name: str = "ai_creative_studio"):
        self.name = name
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """Setup the logger with appropriate handlers and formatters"""
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.INFO)
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Create logs directory if it doesn't exist
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # File handler for detailed logs
        file_handler = logging.FileHandler(
            logs_dir / f"{self.name}_{datetime.now().strftime('%Y%m%d')}.log"
        )
        file_handler.setLevel(logging.INFO)
        
        # Console handler for immediate feedback
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.WARNING)
        
        # Formatter with timestamp and structured data
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def _get_session_id(self) -> str:
        """Get or create a session ID for tracking"""
        if 'session_id' not in st.session_state:
            st.session_state.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        return st.session_state.session_id
    
    def _create_log_entry(self, action: str, details: Dict[str, Any], level: str = "INFO") -> Dict[str, Any]:
        """Create a structured log entry"""
        return {
            "timestamp": datetime.now().isoformat(),
            "session_id": self._get_session_id(),
            "action": action,
            "level": level,
            "details": details,
            "user_agent": st.context.headers.get("User-Agent", "Unknown") if hasattr(st, 'context') else "Unknown"
        }
    
    def log_user_action(self, action: str, details: Dict[str, Any]):
        """Log user actions"""
        log_entry = self._create_log_entry(action, details, "INFO")
        self.logger.info(json.dumps(log_entry))
    
    def log_api_call(self, service: str, model: str, prompt_length: int, response_time: float, success: bool, error: Optional[str] = None):
        """Log API calls with performance metrics"""
        details = {
            "service": service,
            "model": model,
            "prompt_length": prompt_length,
            "response_time_seconds": round(response_time, 3),
            "success": success
        }
        
        if error:
            details["error"] = error
            
        log_entry = self._create_log_entry("api_call", details, "ERROR" if error else "INFO")
        
        if error:
            self.logger.error(json.dumps(log_entry))
        else:
            self.logger.info(json.dumps(log_entry))
        
        # Append log entry to session state
        if 'app_logs' not in st.session_state:
            st.session_state.app_logs = []
        st.session_state.app_logs.append(log_entry)
        
        # Keep only last 1000 logs to prevent memory issues
        if len(st.session_state.app_logs) > 1000:
            st.session_state.app_logs = st.session_state.app_logs[-1000:]
    
    def log_error(self, error_type: str, error_message: str, context: Dict[str, Any]):
        """Log errors with context"""
        details = {
            "error_type": error_type,
            "error_message": error_message,
            "context": context
        }
        
        log_entry = self._create_log_entry("error", details, "ERROR")
        self.logger.error(json.dumps(log_entry))
    
    def log_system_event(self, event: str, details: Dict[str, Any]):
        """Log system events"""
        log_entry = self._create_log_entry("system_event", details, "INFO")
        self.logger.info(json.dumps(log_entry))

# Global logger instance
app_logger = AppLogger()