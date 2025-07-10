"""Chat service for handling ChatGPT interactions"""
import streamlit as st
from datetime import datetime
import time
from ..utils.logger import app_logger
from ..utils.tracer import tracer
from ..utils.global_counter import global_counter

class ChatService:
    """Handle chat interactions with OpenAI GPT models"""
    
    @staticmethod
    @tracer.trace_api_call("openai")
    def get_chatgpt_response(client, messages, model, temperature):
        """Get response from ChatGPT"""
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=1000,
                stream=True
            )
            return response
        except Exception as e:
            app_logger.log_error("chat_api_error", str(e), {
                "model": model,
                "temperature": temperature,
                "message_count": len(messages)
            })
            return f"Error: {str(e)}"
    
    @tracer.trace_user_action("render_chat_settings")
    def render_chat_settings(self):
        """Render chat settings in sidebar - exact same as app.py"""
        st.sidebar.subheader("Chat Settings")
        
        model = st.sidebar.selectbox(
            "Select Model:",
            ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "gpt-4o"]
        )
        
        temperature = st.sidebar.slider(
            "Temperature:",
            min_value=0.0,
            max_value=2.0,
            value=0.7,
            step=0.1
        )
        
        # Display global chat statistics
        st.sidebar.markdown("---")
        st.sidebar.subheader("📊 Global Chat Stats")
        
        chat_stats = global_counter.get_statistics()
        st.sidebar.metric("Total Chat Messages", chat_stats["total_chats"])
        
        # Log settings selection
        app_logger.log_user_action("chat_settings_configured", {
            "model": model,
            "temperature": temperature,
            "global_chat_count": chat_stats["total_chats"]
        })
        
        return model, temperature
    
    @tracer.trace_user_action("display_chat_messages")
    def display_chat_messages(self):
        """Display chat message history - exact same as app.py"""
        chat_container = st.container()
        
        messages = [m for m in st.session_state.messages if m.get("type") == "chat"]
        app_logger.log_system_event("chat_messages_displayed", {
            "message_count": len(messages)
        })
        
        with chat_container:
            for message in st.session_state.messages:
                if message.get("type") == "chat":
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])
                        if "timestamp" in message:
                            st.caption(f"*{message['timestamp']}*")
    
    @tracer.trace_user_action("handle_chat_input")
    def handle_chat_input(self, model, temperature):
        """Handle chat input - exact same as app.py"""
        if prompt := st.chat_input("What can I help you with?"):
            # Increment global chat counter
            global_chat_count = global_counter.increment_chat_count()
            
            # Log user input
            app_logger.log_user_action("chat_message_sent", {
                "model": model,
                "temperature": temperature,
                "prompt_length": len(prompt),
                "prompt_preview": prompt[:50] + "..." if len(prompt) > 50 else prompt,
                "global_chat_count": global_chat_count
            })
            
            # Add user message to chat history
            timestamp = datetime.now().strftime("%H:%M:%S")
            st.session_state.messages.append({
                "type": "chat",
                "role": "user", 
                "content": prompt,
                "timestamp": timestamp
            })
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
                st.caption(f"*{timestamp}*")
            
            # Get and display assistant response
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                
                # Prepare messages for API (without timestamps)
                chat_messages = [{"role": m["role"], "content": m["content"]} 
                               for m in st.session_state.messages if m.get("type") == "chat"]
                
                with st.spinner("Thinking..."):
                    try:
                        start_time = time.time()
                        response = self.get_chatgpt_response(st.session_state.client, chat_messages, model, temperature)
                        
                        if isinstance(response, str):
                            st.error(response)
                            app_logger.log_error("chat_response_error", response, {
                                "model": model,
                                "prompt_length": len(prompt)
                            })
                        else:
                            # Stream the response
                            full_response = ""
                            for chunk in response:
                                if chunk.choices[0].delta.content is not None:
                                    full_response += chunk.choices[0].delta.content
                                    message_placeholder.markdown(full_response + "▌")
                            
                            message_placeholder.markdown(full_response)
                            
                            # Add assistant response to chat history
                            response_timestamp = datetime.now().strftime("%H:%M:%S")
                            st.session_state.messages.append({
                                "type": "chat",
                                "role": "assistant", 
                                "content": full_response,
                                "timestamp": response_timestamp
                            })
                            
                            st.caption(f"*{response_timestamp}*")
                            
                            response_time = time.time() - start_time
                            app_logger.log_user_action("chat_response_received", {
                                "model": model,
                                "response_length": len(full_response),
                                "response_time_seconds": round(response_time, 3)
                            })
                            
                    except Exception as e:
                        app_logger.log_error("chat_processing_error", str(e), {
                            "model": model,
                            "prompt_length": len(prompt)
                        })
                        st.error(f"Error getting response: {str(e)}")
    
    @tracer.trace_user_action("render_chat_interface")
    def render_chat_interface(self):
        """Render the complete chat interface - exact same as app.py"""
        app_logger.log_system_event("chat_interface_rendered", {})
        
        model, temperature = self.render_chat_settings()
        self.display_chat_messages()
        self.handle_chat_input(model, temperature)