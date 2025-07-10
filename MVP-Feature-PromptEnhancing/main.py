import streamlit as st
from datetime import datetime

# Import services
from src.services.auth_service import AuthService
from src.services.chat_service import ChatService
from src.services.image_service import ImageService
from src.services.video_service import VideoService
from src.services.prompt_enhancing import PromptEnhancementService  # Add prompt enhancement import
from src.ui.components import UIComponents
from src.config.settings import AppConfig
from src.utils.logger import app_logger

# Set page config
st.set_page_config(**AppConfig.PAGE_CONFIG)

# Log application startup
app_logger.log_system_event("application_started", {
    "timestamp": datetime.now().isoformat()
})

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "client" not in st.session_state:
    st.session_state.client = None
if "google_api_key" not in st.session_state:
    st.session_state.google_api_key = ""
if "mode" not in st.session_state:
    st.session_state.mode = "chat"

# Initialize services
auth_service = AuthService()
chat_service = ChatService()
image_service = ImageService()
video_service = VideoService()
prompt_enhancement_service = PromptEnhancementService()  # Initialize prompt enhancement service
ui_components = UIComponents()

# Log page load
app_logger.log_user_action("page_loaded", {
    "has_api_key": bool(st.session_state.api_key),
    "current_mode": st.session_state.mode,
    "message_count": len(st.session_state.messages)
})

# Render header
ui_components.render_header()

# API Key Section
if not st.session_state.api_key:
    auth_service.render_auth_ui()
else:
    # Render mode selector
    ui_components.render_mode_selector()
    
    # Render sidebar
    ui_components.render_sidebar()
    
    # Route to appropriate service based on mode
    if st.session_state.mode == "chat":
        chat_service.render_chat_interface()
    
    elif st.session_state.mode == "image":
        image_service.render_image_interface()
    
    elif st.session_state.mode == "video":
        video_service.render_video_interface()
    
    elif st.session_state.mode == "enhance":  # Add prompt enhancement routing
        prompt_enhancement_service.render_enhancement_interface()
    
    # Render statistics
    ui_components.render_statistics()

# Render footer
ui_components.render_footer()