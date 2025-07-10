"""Session state management utilities"""
import streamlit as st

class SessionManager:
    """Manage Streamlit session state"""
    
    def __init__(self):
        self.session_keys = [
            'messages', 'api_key', 'client', 'mode'
        ]
    
    def initialize_session(self):
        """Initialize session state variables"""
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "api_key" not in st.session_state:
            st.session_state.api_key = ""
        if "client" not in st.session_state:
            st.session_state.client = None
        if "mode" not in st.session_state:
            st.session_state.mode = "chat"
    
    def get(self, key: str, default=None):
        """Get value from session state"""
        return st.session_state.get(key, default)
    
    def set(self, key: str, value):
        """Set value in session state"""
        st.session_state[key] = value
    
    def append_message(self, message: dict):
        """Append message to session messages"""
        if "messages" not in st.session_state:
            st.session_state.messages = []
        st.session_state.messages.append(message)
    
    def clear_messages(self):
        """Clear all messages from session"""
        st.session_state.messages = []
    
    def clear_session(self):
        """Clear entire session state"""
        for key in self.session_keys:
            if key in st.session_state:
                del st.session_state[key]
        self.initialize_session()
    
    def get_statistics(self):
        """Get session statistics"""
        messages = self.get('messages', [])
        return {
            'total_messages': len(messages),
            'chat_messages': len([m for m in messages if m.get('type') == 'chat']),
            'image_generations': len([m for m in messages if m.get('type') == 'image'])
        }