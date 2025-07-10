"""Global counter utilities for persistent tracking across sessions"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import streamlit as st

class GlobalCounter:
    """Persistent counter that survives session resets"""
    
    def __init__(self, counter_file: str = "global_counters.json"):
        self.counter_file = Path(counter_file)
        self.counters = self._load_counters()
        # Initialize enhanced prompts in session state
        if "enhanced_prompts" not in st.session_state:
            st.session_state.enhanced_prompts = 0
    
    def _load_counters(self) -> Dict[str, Any]:
        """Load counters from file"""
        if self.counter_file.exists():
            try:
                with open(self.counter_file, 'r') as f:
                    data = json.load(f)
                    # Ensure all required keys exist
                    if "enhanced_prompts" not in data:
                        data["enhanced_prompts"] = 0
                    if "videos_6s" not in data:
                        data["videos_6s"] = 0
                    if "videos_7s" not in data:
                        data["videos_7s"] = 0
                    if "total_video_duration_seconds" not in data:
                        data["total_video_duration_seconds"] = 0
                    return data
            except (json.JSONDecodeError, IOError):
                return self._get_default_counters()
        return self._get_default_counters()
    
    def _get_default_counters(self) -> Dict[str, Any]:
        """Get default counter structure"""
        return {
            "videos_generated": 0,
            "images_generated": 0,
            "chat_messages": 0,
            "enhanced_prompts": 0,  # Add enhanced prompts counter
            "first_used": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "video_durations": [],  # Track all video durations
            "videos_5s": 0,  # Specific counter for 5s videos
            "videos_8s": 0,  # Specific counter for 8s videos
            "videos_6s": 0,  # Add 6s counter
            "videos_7s": 0,  # Add 7s counter
            "total_video_duration_seconds": 0  # Total duration of all videos
        }
    
    def _save_counters(self):
        """Save counters to file"""
        try:
            self.counters["last_updated"] = datetime.now().isoformat()
            with open(self.counter_file, 'w') as f:
                json.dump(self.counters, f, indent=2)
        except IOError as e:
            print(f"Error saving counters: {e}")
    
    def increment_video_count(self, duration: int) -> int:
        """Increment video counter and track duration"""
        self.counters["videos_generated"] += 1
        self.counters["video_durations"].append({
            "duration_seconds": duration,
            "generated_at": datetime.now().isoformat()
        })
        
        # Update total duration
        self.counters["total_video_duration_seconds"] = self.counters.get("total_video_duration_seconds", 0) + duration
        
        # Update specific duration counters
        duration_key = f"videos_{duration}s"
        self.counters[duration_key] = self.counters.get(duration_key, 0) + 1
        
        self._save_counters()
        return self.counters["videos_generated"]
    
    def increment_image_count(self) -> int:
        """Increment image counter"""
        self.counters["images_generated"] += 1
        self._save_counters()
        return self.counters["images_generated"]
    
    def increment_chat_count(self) -> int:
        """Increment chat counter"""
        self.counters["chat_messages"] += 1
        self._save_counters()
        return self.counters["chat_messages"]
    
    def increment_enhanced_prompt_count(self) -> int:
        """Increment enhanced prompt counter"""
        # Increment both session state and persistent counter
        st.session_state.enhanced_prompts = st.session_state.get("enhanced_prompts", 0) + 1
        self.counters["enhanced_prompts"] = self.counters.get("enhanced_prompts", 0) + 1
        self._save_counters()
        return self.counters["enhanced_prompts"]
    
    def get_video_count(self) -> int:
        """Get total video count"""
        return self.counters.get("videos_generated", 0)
    
    def get_image_count(self) -> int:
        """Get total image count"""
        return self.counters.get("images_generated", 0)
    
    def get_chat_count(self) -> int:
        """Get total chat count"""
        return self.counters.get("chat_messages", 0)
    
    def get_enhanced_prompt_count(self) -> int:
        """Get current enhanced prompt count"""
        return self.counters.get("enhanced_prompts", 0)
    
    def get_videos_5s_count(self) -> int:
        """Get total count of 5-second videos"""
        return self.counters.get("videos_5s", 0)
    
    def get_videos_8s_count(self) -> int:
        """Get total count of 8-second videos"""
        return self.counters.get("videos_8s", 0)
    
    def get_video_durations(self) -> list:
        """Get all video durations"""
        return self.counters.get("video_durations", [])
    
    def get_total_video_duration(self) -> int:
        """Get total duration of all videos generated (from stored counter)"""
        # Use the stored counter for efficiency, but verify with calculation if needed
        stored_total = self.counters.get("total_video_duration_seconds", 0)
        
        # Verify the stored total matches calculated total (for data integrity)
        calculated_total = sum(item["duration_seconds"] for item in self.get_video_durations())
        
        # If they don't match, recalculate and update
        if stored_total != calculated_total:
            self.counters["total_video_duration_seconds"] = calculated_total
            self._save_counters()
            return calculated_total
        
        return stored_total
    
    def get_average_video_duration(self) -> float:
        """Get average video duration"""
        durations = self.get_video_durations()
        if not durations:
            return 0.0
        total_duration = self.get_total_video_duration()
        return total_duration / len(durations)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics"""
        video_durations = self.get_video_durations()
        return {
            "total_videos": self.get_video_count(),
            "total_images": self.get_image_count(),
            "total_chats": self.get_chat_count(),
            "total_enhanced_prompts": self.get_enhanced_prompt_count(),  # Use persistent counter
            "total_video_duration_seconds": self.get_total_video_duration(),
            "videos_5s": self.get_videos_5s_count(),
            "videos_8s": self.get_videos_8s_count(),
            "videos_6s": self.counters.get("videos_6s", 0),
            "videos_7s": self.counters.get("videos_7s", 0),
            "average_video_duration_seconds": self.get_average_video_duration(),
            "video_count_by_duration": self._get_duration_breakdown(),
            "first_used": self.counters.get("first_used"),
            "last_updated": self.counters.get("last_updated"),
        }
    
    def _get_duration_breakdown(self) -> Dict[int, int]:
        """Get count of videos by duration"""
        durations = self.get_video_durations()
        breakdown = {}
        for item in durations:
            duration = item["duration_seconds"]
            breakdown[duration] = breakdown.get(duration, 0) + 1
        return breakdown
    
    def get_formatted_total_duration(self) -> str:
        """Get formatted total duration string"""
        total_seconds = self.get_total_video_duration()
        if total_seconds >= 60:
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            return f"{minutes}m {seconds}s"
        else:
            return f"{total_seconds}s"

# Global instance
global_counter = GlobalCounter()