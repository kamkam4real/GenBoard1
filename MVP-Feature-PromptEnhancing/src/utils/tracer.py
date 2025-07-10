"""Traceability utilities for tracking user actions and system performance"""
import time
from functools import wraps
from typing import Callable, Any, Dict
import streamlit as st
from .logger import app_logger

class ActionTracer:
    """Trace and log user actions and system performance"""
    
    @staticmethod
    def trace_api_call(service: str, model: str = ""):
        """Decorator to trace API calls"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                start_time = time.time()
                prompt = kwargs.get('prompt', args[1] if len(args) > 1 else "")
                prompt_length = len(str(prompt))
                
                try:
                    result = func(*args, **kwargs)
                    response_time = time.time() - start_time
                    
                    # Log successful API call
                    app_logger.log_api_call(
                        service=service,
                        model=model or kwargs.get('model', 'unknown'),
                        prompt_length=prompt_length,
                        response_time=response_time,
                        success=True
                    )
                    
                    return result
                    
                except Exception as e:
                    response_time = time.time() - start_time
                    
                    # Log failed API call
                    app_logger.log_api_call(
                        service=service,
                        model=model or kwargs.get('model', 'unknown'),
                        prompt_length=prompt_length,
                        response_time=response_time,
                        success=False,
                        error=str(e)
                    )
                    
                    raise e
                    
            return wrapper
        return decorator
    
    @staticmethod
    def trace_user_action(action_name: str):
        """Decorator to trace user actions"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                start_time = time.time()
                
                # Extract relevant details from arguments
                details = {
                    "function": func.__name__,
                    "args_count": len(args),
                    "kwargs": list(kwargs.keys())
                }
                
                try:
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    
                    details.update({
                        "execution_time_seconds": round(execution_time, 3),
                        "success": True
                    })
                    
                    app_logger.log_user_action(action_name, details)
                    return result
                    
                except Exception as e:
                    execution_time = time.time() - start_time
                    
                    details.update({
                        "execution_time_seconds": round(execution_time, 3),
                        "success": False,
                        "error": str(e)
                    })
                    
                    app_logger.log_user_action(action_name, details)
                    raise e
                    
            return wrapper
        return decorator

# Global tracer instance
tracer = ActionTracer()