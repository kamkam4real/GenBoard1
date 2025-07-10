"""UI components for the Streamlit app"""
import streamlit as st
from ..utils.logger import app_logger
from ..utils.tracer import tracer
from ..utils.global_counter import global_counter

class UIComponents:
    """Reusable UI components"""
    
    @tracer.trace_user_action("render_header")
    def render_header(self):
        """Render the main header - exact same as app.py but with video"""
        app_logger.log_system_event("header_rendered", {})
        st.title("🤖 ChatGPT Clone with DALL-E & VEO")
        st.markdown("---")
    
    @tracer.trace_user_action("render_mode_selector")
    def render_mode_selector(self):
        """Render mode selection tabs"""
        app_logger.log_user_action("mode_selector_rendered", {
            "current_mode": st.session_state.mode
        })
        
        # Mode selection
        mode = st.selectbox(
            "Choose Mode:",
            ["chat", "image", "video", "enhance"],  # Added enhance mode
            format_func=lambda x: {
                "chat": "💬 Chat with AI", 
                "image": "🎨 Generate Images", 
                "video": "🎬 Generate Videos",
                "enhance": "🎯 Enhance Video Prompts"  # New mode
            }[x],
            index=["chat", "image", "video", "enhance"].index(st.session_state.mode)
        )
        
        if mode != st.session_state.mode:
            st.session_state.mode = mode
            app_logger.log_user_action("mode_changed", {
                "new_mode": mode,
                "previous_mode": st.session_state.mode
            })
            st.rerun()
    
    @tracer.trace_user_action("render_sidebar")
    def render_sidebar(self):
        """Render the sidebar with common controls - exact same as app.py"""
        app_logger.log_system_event("sidebar_rendered", {})
        
        st.sidebar.header("Settings")
        
        # API Key management in sidebar
        if st.sidebar.button("Change API Keys"):
            app_logger.log_user_action("change_api_keys_clicked", {})
            st.session_state.api_key = ""
            st.session_state.client = None
            st.session_state.google_api_key = ""
            st.session_state.messages = []
            st.rerun()
        
        # Clear chat button
        if st.sidebar.button("Clear History"):
            message_count = len(st.session_state.messages)
            app_logger.log_user_action("clear_history_clicked", {
                "cleared_message_count": message_count
            })
            st.session_state.messages = []
            st.rerun()
    
    @tracer.trace_user_action("render_statistics")
    def render_statistics(self):
        """Render usage statistics - now with enhanced global stats and video stats"""
        if st.session_state.messages:
            st.sidebar.markdown("---")
            st.sidebar.header("📊 Session Statistics")
            
            total_messages = len(st.session_state.messages)
            chat_messages = len([m for m in st.session_state.messages if m.get("type") == "chat"])
            image_generations = len([m for m in st.session_state.messages if m.get("type") == "image"])
            video_generations = len([m for m in st.session_state.messages if m.get("type") == "video"])
            
            st.sidebar.metric("Session Items", total_messages)
            st.sidebar.metric("Session Chats", chat_messages)
            st.sidebar.metric("Session Images", image_generations)
            st.sidebar.metric("Session Videos", video_generations)
            
        # Always show global statistics
        st.sidebar.markdown("---")
        st.sidebar.header("🌍 Global Statistics")
        
        global_stats = global_counter.get_statistics()
        
        col1, col2, col3, col4 = st.columns(4)  # Added one more column
        
        with col1:
            st.metric("💬 Total Chats", global_stats["total_chats"])
        with col2:
            st.metric("🎨 Total Images", global_stats["total_images"]) 
        with col3:
            st.metric("🎬 Total Videos", global_stats["total_videos"])
        
        if global_stats["total_videos"] > 0:
            # Total video duration using the new formatted method
            total_duration_formatted = global_counter.get_formatted_total_duration()
            st.sidebar.metric("Total Video Duration", total_duration_formatted)
            
            # Show specific duration counts prominently
            videos_5s = global_stats["videos_5s"]
            videos_8s = global_stats["videos_8s"]
            
            if videos_5s > 0:
                st.sidebar.metric("5-second Videos", videos_5s)
            
            if videos_8s > 0:
                st.sidebar.metric("8-second Videos", videos_8s)
        
        if global_stats.get("first_used"):
            first_used = global_stats["first_used"][:10]  # Just the date part
            st.sidebar.text(f"First used: {first_used}")
        
        app_logger.log_system_event("statistics_displayed", {
            "session_stats": {
                "total_messages": len(st.session_state.messages) if st.session_state.messages else 0,
                "chat_messages": len([m for m in st.session_state.messages if m.get("type") == "chat"]) if st.session_state.messages else 0,
                "image_generations": len([m for m in st.session_state.messages if m.get("type") == "image"]) if st.session_state.messages else 0,
                "video_generations": len([m for m in st.session_state.messages if m.get("type") == "video"]) if st.session_state.messages else 0
            },
            "global_stats": global_stats
        })
    
    @tracer.trace_user_action("render_footer")
    def render_footer(self):
        """Render the footer - updated with VEO"""
        app_logger.log_system_event("footer_rendered", {})
        st.markdown("---")
        st.markdown(
            """
            <div style='text-align: center; color: #666; font-size: 0.8em;'>
                Built with ❤️ using Streamlit | Powered by OpenAI GPT & DALL-E & Google VEO
            </div>
            """, 
            unsafe_allow_html=True
        )