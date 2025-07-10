"""Image service for handling DALL-E image generation"""
import streamlit as st
import requests
from datetime import datetime
from io import BytesIO
import time
from ..utils.logger import app_logger
from ..utils.tracer import tracer
from ..utils.global_counter import global_counter

class ImageService:
    """Handle image generation with DALL-E"""
    
    @staticmethod
    @tracer.trace_api_call("dalle", "dall-e-3")
    def generate_image(client, prompt, size="1024x1024", quality="standard", n=1):
        """Generate image using DALL-E"""
        try:
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality=quality,
                n=n
            )
            
            # Increment global image counter
            global_image_count = global_counter.increment_image_count()
            
            app_logger.log_user_action("image_generated", {
                "model": "dall-e-3",
                "size": size,
                "quality": quality,
                "prompt_length": len(prompt),
                "global_image_count": global_image_count
            })
            
            return response.data[0].url
        except Exception as e:
            app_logger.log_error("image_generation_error", str(e), {
                "model": "dall-e-3",
                "size": size,
                "quality": quality,
                "prompt_length": len(prompt)
            })
            return f"Error: {str(e)}"
    
    @staticmethod
    @tracer.trace_user_action("download_image")
    def download_image(url):
        """Download image from URL"""
        try:
            response = requests.get(url)
            app_logger.log_user_action("image_downloaded", {
                "url_domain": url.split('/')[2] if '/' in url else "unknown",
                "response_size_bytes": len(response.content)
            })
            return BytesIO(response.content)
        except Exception as e:
            app_logger.log_error("image_download_error", str(e), {"url": url})
            return None
    
    @tracer.trace_user_action("render_image_settings")
    def render_image_settings(self):
        """Render image settings in sidebar - exact same as app.py"""
        st.sidebar.subheader("Image Settings")
        
        image_size = st.sidebar.selectbox(
            "Image Size:",
            ["1024x1024", "1792x1024", "1024x1792"]
        )
        
        image_quality = st.sidebar.selectbox(
            "Quality:",
            ["standard", "hd"]
        )
        
        # Display global image statistics
        st.sidebar.markdown("---")
        st.sidebar.subheader("📊 Global Image Stats")
        
        image_stats = global_counter.get_statistics()
        st.sidebar.metric("Total Images Generated", image_stats["total_images"])
        
        app_logger.log_user_action("image_settings_configured", {
            "size": image_size,
            "quality": image_quality,
            "global_image_count": image_stats["total_images"]
        })
        
        return image_size, image_quality
    
    @tracer.trace_user_action("display_image_history")
    def display_image_history(self):
        """Display image generation history - exact same as app.py"""
        images = [m for m in st.session_state.messages if m.get("type") == "image"]
        app_logger.log_system_event("image_history_displayed", {
            "image_count": len(images)
        })
        
        # Show previous generations
        for message in st.session_state.messages:
            if message.get("type") == "image":
                st.markdown(f"**Prompt:** {message['prompt']}")
                
                # Display global image number if available
                if message.get("global_image_number"):
                    st.markdown(f"**Global Image #:** {message['global_image_number']}")
                
                if message.get("image_url"):
                    st.image(message["image_url"], caption=message["prompt"])
                    
                    # Download button
                    try:
                        img_data = self.download_image(message["image_url"])
                        if img_data:
                            st.download_button(
                                label="📥 Download Image",
                                data=img_data,
                                file_name=f"generated_image_{message['timestamp'].replace(':', '-')}.png",
                                mime="image/png"
                            )
                    except:
                        pass
                else:
                    st.error(f"Failed to generate image: {message.get('error', 'Unknown error')}")
                
                st.caption(f"*Generated at {message['timestamp']}*")
                st.markdown("---")
    
    @tracer.trace_user_action("handle_image_generation")
    def handle_image_generation(self, image_size, image_quality):
        """Handle image generation input - exact same as app.py"""
        st.markdown("### Generate New Image")
        image_prompt = st.text_area(
            "Describe the image you want to generate:",
            placeholder="A beautiful sunset over mountains with a lake in the foreground...",
            height=100
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🎨 Generate Image", disabled=not image_prompt.strip()):
                if image_prompt.strip():
                    app_logger.log_user_action("image_generation_started", {
                        "size": image_size,
                        "quality": image_quality,
                        "prompt_length": len(image_prompt),
                        "prompt_preview": image_prompt[:50] + "..." if len(image_prompt) > 50 else image_prompt
                    })
                    
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    
                    with st.spinner("Generating image... This may take a few moments."):
                        try:
                            start_time = time.time()
                            image_url = self.generate_image(
                                st.session_state.client, 
                                image_prompt, 
                                size=image_size,
                                quality=image_quality
                            )
                            generation_time = time.time() - start_time
                            
                            if image_url.startswith("Error"):
                                st.session_state.messages.append({
                                    "type": "image",
                                    "prompt": image_prompt,
                                    "error": image_url,
                                    "timestamp": timestamp
                                })
                                st.error(image_url)
                                
                                app_logger.log_user_action("image_generation_failed", {
                                    "error": image_url,
                                    "generation_time_seconds": round(generation_time, 3)
                                })
                            else:
                                # Get the current global image count
                                current_global_count = global_counter.get_image_count()
                                
                                st.session_state.messages.append({
                                    "type": "image",
                                    "prompt": image_prompt,
                                    "image_url": image_url,
                                    "global_image_number": current_global_count,
                                    "timestamp": timestamp
                                })
                                st.success(f"✅ Image generated successfully! (Global Image #{current_global_count})")
                                
                                app_logger.log_user_action("image_generation_completed", {
                                    "generation_time_seconds": round(generation_time, 3),
                                    "image_url_domain": image_url.split('/')[2] if '/' in image_url else "unknown",
                                    "global_image_number": current_global_count
                                })
                                
                                st.rerun()
                                
                        except Exception as e:
                            generation_time = time.time() - start_time
                            error_msg = f"Error generating image: {str(e)}"
                            st.session_state.messages.append({
                                "type": "image",
                                "prompt": image_prompt,
                                "error": error_msg,
                                "timestamp": timestamp
                            })
                            st.error(error_msg)
                            
                            app_logger.log_error("image_generation_exception", str(e), {
                                "prompt_length": len(image_prompt),
                                "generation_time_seconds": round(generation_time, 3)
                            })
    
    @tracer.trace_user_action("render_image_interface")
    def render_image_interface(self):
        """Render the complete image generation interface - exact same as app.py"""
        app_logger.log_system_event("image_interface_rendered", {})
        
        image_size, image_quality = self.render_image_settings()
        
        # Display image generation history
        st.subheader("🎨 Image Generation")
        
        self.display_image_history()
        self.handle_image_generation(image_size, image_quality)