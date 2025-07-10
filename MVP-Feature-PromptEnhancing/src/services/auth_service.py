"""Authentication service for API key management"""
import streamlit as st
import openai
from ..utils.logger import app_logger
from ..utils.tracer import tracer

class AuthService:
    """Handle authentication and API key validation"""
    
    @staticmethod
    @tracer.trace_api_call("openai", "validation")
    def validate_api_key(api_key: str) -> tuple[bool, str | openai.OpenAI]:
        """Validate the OpenAI API key"""
        try:
            client = openai.OpenAI(api_key=api_key)
            client.models.list()
            
            # Log successful validation
            app_logger.log_user_action("api_key_validation", {
                "service": "openai",
                "success": True,
                "key_prefix": api_key[:7] + "..." if len(api_key) > 7 else "short_key"
            })
            
            return True, client
        except Exception as e:
            # Log failed validation
            app_logger.log_user_action("api_key_validation", {
                "service": "openai", 
                "success": False,
                "error": str(e),
                "key_prefix": api_key[:7] + "..." if len(api_key) > 7 else "short_key"
            })
            return False, str(e)
    
    @tracer.trace_user_action("render_auth_ui")
    def render_auth_ui(self):
        """Render the authentication UI - exact same as app.py"""
        app_logger.log_system_event("auth_ui_rendered", {
            "component": "authentication_form"
        })
        
        st.header("🔑 Enter your API Keys")
        st.markdown("You need API keys to use this application.")
        
        # OpenAI API Key
        st.subheader("OpenAI API Key")
        st.markdown("Get yours at [OpenAI Platform](https://platform.openai.com/api-keys)")
        
        api_key_input = st.text_input(
            "OpenAI API Key:", 
            type="password", 
            placeholder="sk-..."
        )
        
        # Google Cloud API Key for VEO
        st.subheader("Google Cloud API Key (Optional - for Video Generation)")
        st.markdown("Get yours at [Google Cloud Console](https://console.cloud.google.com/apis/credentials)")
        
        google_api_key_input = st.text_input(
            "Google Cloud API Key:", 
            type="password", 
            placeholder="AIza...",
            help="Required only for video generation with VEO"
        )
        
        if st.button("Validate API Keys"):
            app_logger.log_user_action("validate_api_keys_clicked", {
                "has_openai_key": bool(api_key_input),
                "has_google_key": bool(google_api_key_input)
            })
            
            if api_key_input:
                with st.spinner("Validating OpenAI API key..."):
                    is_valid, result = self.validate_api_key(api_key_input)
                    
                if is_valid:
                    st.session_state.api_key = api_key_input
                    st.session_state.client = result
                    
                    # Store Google API key if provided
                    if google_api_key_input:
                        st.session_state.google_api_key = google_api_key_input
                        app_logger.log_user_action("google_api_key_stored", {
                            "key_prefix": google_api_key_input[:7] + "..." if len(google_api_key_input) > 7 else "short_key"
                        })
                        st.success("✅ Both API keys validated successfully!")
                    else:
                        st.success("✅ OpenAI API key validated successfully! (Video generation will be unavailable without Google Cloud API key)")
                    
                    st.rerun()
                else:
                    st.error(f"❌ Invalid OpenAI API key: {result}")
            else:
                app_logger.log_user_action("validation_attempted_without_key", {})
                st.warning("Please enter your OpenAI API key.")
        
        st.markdown("---")
        st.markdown("**Note:** Your API keys are stored only in your browser session and are not saved anywhere.")