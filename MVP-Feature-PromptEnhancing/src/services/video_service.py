"""Video service for handling VEO video generation"""
import streamlit as st
import requests
from datetime import datetime
from io import BytesIO
import time
from google import genai
from google.genai import types
from ..utils.logger import app_logger
from ..utils.tracer import tracer
from ..utils.global_counter import global_counter

class VideoService:
    """Handle video generation with Google VEO"""
    
    @staticmethod
    @tracer.trace_api_call("veo", "veo-2.0-generate-001")
    def generate_video(api_key, prompt, duration=5, resolution=720):
        """Generate video using VEO API"""
        try:
            client = genai.Client(api_key=api_key)
            
            # Map resolution to aspect ratio if needed
            aspect_ratio = "16:9"  # Default aspect ratio
            
            app_logger.log_user_action("video_generation_started", {
                "model": "veo-2.0-generate-001",
                "duration": duration,
                "resolution": resolution,
                "aspect_ratio": aspect_ratio,
                "prompt_length": len(prompt)
            })
            
            operation = client.models.generate_videos(
                model="veo-2.0-generate-001",
                prompt=prompt,
                config=types.GenerateVideosConfig(
                    person_generation="dont_allow",  # "dont_allow" or "allow_adult"
                    duration_seconds=duration,
                    aspect_ratio=aspect_ratio,  # "16:9" or "9:16"
                ),
            )

            # Wait for the operation to complete with better error handling
            poll_count = 0
            max_polls = 60  # Maximum number of polls (20 minutes at 20-second intervals)
            
            while not operation.done and poll_count < max_polls:
                time.sleep(20)
                try:
                    operation = client.operations.get(operation)
                    poll_count += 1
                    
                    app_logger.log_system_event("video_generation_polling", {
                        "poll_count": poll_count,
                        "operation_done": operation.done,
                        "operation_name": getattr(operation, 'name', 'unknown')
                    })
                    
                    # Check if operation failed
                    if hasattr(operation, 'error') and operation.error:
                        app_logger.log_error("video_generation_operation_error", 
                                           str(operation.error), {
                                               "poll_count": poll_count
                                           })
                        return f"Error: Video generation failed - {operation.error}"
                    
                except Exception as poll_error:
                    app_logger.log_error("video_generation_polling_error", 
                                       str(poll_error), {
                                           "poll_count": poll_count
                                       })
                    return f"Error: Failed to check generation status - {poll_error}"

            # Check if we timed out
            if poll_count >= max_polls:
                app_logger.log_error("video_generation_timeout", 
                                   "Video generation timed out", {
                                       "max_polls": max_polls,
                                       "total_wait_minutes": (max_polls * 20) / 60
                                   })
                return "Error: Video generation timed out after 20 minutes"

            # Check if operation completed successfully
            if not operation.done:
                return "Error: Video generation did not complete"
            
            # Check if operation has response
            if not hasattr(operation, 'response') or operation.response is None:
                app_logger.log_error("video_generation_no_response", 
                                   "Operation completed but has no response", {
                                       "operation_done": operation.done,
                                       "poll_count": poll_count
                                   })
                return "Error: Video generation completed but no response received"
            
            # Check if response has generated_videos
            if not hasattr(operation.response, 'generated_videos') or operation.response.generated_videos is None:
                app_logger.log_error("video_generation_no_videos", 
                                   "Response has no generated_videos", {
                                       "response_type": type(operation.response).__name__,
                                       "response_attrs": dir(operation.response)
                                   })
                return "Error: No videos were generated in the response"

            # Process the generated videos
            generated_videos = operation.response.generated_videos
            if len(generated_videos) == 0:
                return "Error: No videos were generated"
            
            for n, generated_video in enumerate(generated_videos):
                try:
                    # Check if generated_video has video attribute
                    if not hasattr(generated_video, 'video') or generated_video.video is None:
                        app_logger.log_error("video_generation_no_video_file", 
                                           f"Generated video {n} has no video file", {
                                               "video_index": n,
                                               "video_attrs": dir(generated_video)
                                           })
                        continue
                    
                    # Download the video file
                    video_file = client.files.download(file=generated_video.video)
                    
                    # Save locally and return the file path
                    filename = f"video_{int(time.time())}_{n}.mp4"
                    
                    # Check if video_file has save method
                    if hasattr(video_file, 'save'):
                        video_file.save(filename)
                    else:
                        # Alternative: write the content directly
                        with open(filename, 'wb') as f:
                            f.write(video_file)
                    
                    # Increment global counter with duration
                    global_video_count = global_counter.increment_video_count(duration)
                    
                    app_logger.log_user_action("video_saved", {
                        "filename": filename,
                        "video_index": n,
                        "poll_count": poll_count,
                        "duration_seconds": duration,
                        "global_video_count": global_video_count
                    })
                    
                    # Return the local file path for the first successful video
                    return filename
                    
                except Exception as save_error:
                    app_logger.log_error("video_save_error", 
                                       str(save_error), {
                                           "video_index": n,
                                           "filename": f"video_{int(time.time())}_{n}.mp4"
                                       })
                    continue
                
            return "Error: Failed to save any generated videos"
            
        except Exception as e:
            app_logger.log_error("video_generation_error", str(e), {
                "duration": duration,
                "resolution": resolution,
                "prompt_length": len(prompt),
                "error_type": type(e).__name__
            })
            return f"Error: {str(e)}"
    
    @staticmethod
    @tracer.trace_user_action("download_video")
    def download_video(url):
        """Download video from URL"""
        try:
            # For local files, read the file content
            if url.startswith('video_'):
                with open(url, 'rb') as f:
                    content = f.read()
                    
                app_logger.log_user_action("video_downloaded", {
                    "source": "local_file",
                    "filename": url,
                    "file_size_bytes": len(content)
                })
                
                return BytesIO(content)
            else:
                response = requests.get(url)
                
                app_logger.log_user_action("video_downloaded", {
                    "source": "url",
                    "url_domain": url.split('/')[2] if '/' in url else "unknown",
                    "response_size_bytes": len(response.content)
                })
                
                return BytesIO(response.content)
        except Exception as e:
            app_logger.log_error("video_download_error", str(e), {"url": url})
            return None
    
    @tracer.trace_user_action("render_video_settings")
    def render_video_settings(self):
        """Render video settings in sidebar - using integers for duration and resolution"""
        st.sidebar.subheader("Video Settings")
        
        duration = st.sidebar.selectbox(
            "Duration (seconds):",
            [5, 6, 7, 8],
            help="Choose the video duration in seconds"
        )
        
        resolution = st.sidebar.selectbox(
            "Resolution (height):",
            [720, 1080],
            help="Choose the video resolution height in pixels"
        )
        
        # Display global video statistics
        st.sidebar.markdown("---")
        st.sidebar.subheader("📊 Global Video Stats")
        
        video_stats = global_counter.get_statistics()
        
        # Global counters
        st.sidebar.metric("Total Videos Generated", video_stats["total_videos"])
        
        if video_stats["total_videos"] > 0:
            # Total duration using the new method
            total_duration_formatted = global_counter.get_formatted_total_duration()
            st.sidebar.metric("Total Duration", total_duration_formatted)
            
            # Average duration
            avg_duration = video_stats["average_video_duration_seconds"]
            st.sidebar.metric("Average Duration", f"{avg_duration:.1f}s")
            
            # Specific duration counts
            st.sidebar.markdown("**Duration Breakdown:**")
            videos_5s = video_stats["videos_5s"]
            videos_8s = video_stats["videos_8s"]
            
            # Display specific 5s and 8s counts prominently
            if videos_5s > 0:
                st.sidebar.metric("5-second Videos", videos_5s)
            
            if videos_8s > 0:
                st.sidebar.metric("8-second Videos", videos_8s)
            
            # Show all duration breakdown
            if video_stats["video_count_by_duration"]:
                st.sidebar.markdown("**All Durations:**")
                for dur, count in sorted(video_stats["video_count_by_duration"].items()):
                    st.sidebar.text(f"{dur}s: {count} videos")
        
        app_logger.log_user_action("video_settings_configured", {
            "duration": duration,
            "resolution": resolution,
            "global_video_count": video_stats["total_videos"],
            "videos_5s": video_stats["videos_5s"],
            "videos_8s": video_stats["videos_8s"],
            "total_duration_seconds": video_stats["total_video_duration_seconds"]
        })
        
        return duration, resolution
    
    @tracer.trace_user_action("display_video_history")
    def display_video_history(self):
        """Display video generation history - enhanced to show optimized prompts"""
        videos = [m for m in st.session_state.messages if m.get("type") in ["video", "enhanced_prompt"]]
        app_logger.log_system_event("video_history_displayed", {
            "video_count": len([m for m in videos if m.get("type") == "video"]),
            "enhanced_prompt_count": len([m for m in videos if m.get("type") == "enhanced_prompt"])
        })
        
        # Show previous generations and enhanced prompts
        for message in st.session_state.messages:
            if message.get("type") == "video":
                st.markdown(f"**Prompt:** {message['prompt']}")
                
                # Display duration info if available
                if message.get("duration"):
                    st.markdown(f"**Duration:** {message['duration']} seconds")
                
                # Display global video number if available
                if message.get("global_video_number"):
                    st.markdown(f"**Global Video #:** {message['global_video_number']}")
                
                if message.get("video_url"):
                    # Handle both local files and URLs
                    if message["video_url"].startswith('video_'):
                        # Local file
                        st.video(message["video_url"])
                    else:
                        # URL
                        st.video(message["video_url"])
                    
                    # Download button
                    try:
                        video_data = self.download_video(message["video_url"])
                        if video_data:
                            st.download_button(
                                label="📥 Download Video",
                                data=video_data,
                                file_name=f"generated_video_{message['timestamp'].replace(':', '-')}.mp4",
                                mime="video/mp4"
                            )
                    except:
                        pass
                else:
                    st.error(f"Failed to generate video: {message.get('error', 'Unknown error')}")
                
                st.caption(f"*Generated at {message['timestamp']}*")
                st.markdown("---")
            
            elif message.get("type") == "enhanced_prompt":
                # Display enhanced prompt with special styling
                st.markdown("### 🎯 Enhanced Prompt Ready for Generation")
                
                with st.container():
                    st.markdown("**Optimized Prompt:**")
                    st.code(message["prompt"], language="text")
                    
                    # Show enhancement summary if available
                    if message.get("enhancement_data"):
                        with st.expander("View Enhancement Details"):
                            for stage, data in message["enhancement_data"].items():
                                if stage != "initial_idea":
                                    st.markdown(f"**{stage.title()}:** {data}")
                    
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        if st.button(f"🎬 Generate Video", key=f"gen_{message['timestamp']}"):
                            # Pre-fill the video generation with this prompt
                            st.session_state.enhanced_prompt_to_use = message["prompt"]
                            st.rerun()
                    
                    st.caption(f"*Enhanced at {message['timestamp']}*")
                    st.markdown("---")

    @tracer.trace_user_action("handle_video_generation")
    def handle_video_generation(self, duration, resolution):
        """Handle video generation input - enhanced to support optimized prompts"""
        st.markdown("### Generate New Video")
        
        # Check if there's an enhanced prompt to use
        default_prompt = ""
        if hasattr(st.session_state, 'enhanced_prompt_to_use'):
            default_prompt = st.session_state.enhanced_prompt_to_use
            st.info("🎯 Using enhanced prompt from optimization tool")
            del st.session_state.enhanced_prompt_to_use
        
        video_prompt = st.text_area(
            "Describe the video you want to generate:",
            value=default_prompt,
            placeholder="A serene ocean scene with gentle waves under a sunset sky, with seagulls flying in the distance...",
            height=100
        )
        
        # Show prompt enhancement option
        if not default_prompt:
            col1, col2 = st.columns([1, 1])
            with col2:
                if st.button("🎯 Optimize this prompt"):
                    # Switch to enhancement mode with current prompt
                    st.session_state.mode = "enhance"
                    if video_prompt.strip():
                        # Start enhancement with current prompt
                        from .prompt_enhancing import PromptEnhancementService
                        enhancement_service = PromptEnhancementService()
                        enhancement_service.start_enhancement_flow(video_prompt)
                    st.rerun()
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🎬 Generate Video", disabled=not video_prompt.strip()):
                if video_prompt.strip():
                    app_logger.log_user_action("video_generation_requested", {
                        "duration": duration,
                        "resolution": resolution,
                        "prompt_length": len(video_prompt),
                        "prompt_preview": video_prompt[:50] + "..." if len(video_prompt) > 50 else video_prompt
                    })
                    
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    
                    with st.spinner("Generating video... This may take several minutes."):
                        try:
                            # For VEO, we need a Google Cloud API key
                            google_api_key = st.session_state.get('google_api_key', '')
                            if not google_api_key:
                                error_msg = "Google Cloud API key is required for video generation. Please add it in settings."
                                st.error(error_msg)
                                app_logger.log_error("video_generation_no_key", error_msg, {})
                                return
                            
                            start_time = time.time()
                            video_url = self.generate_video(
                                google_api_key,
                                video_prompt, 
                                duration=duration,
                                resolution=resolution
                            )
                            generation_time = time.time() - start_time
                            
                            if video_url.startswith("Error"):
                                st.session_state.messages.append({
                                    "type": "video",
                                    "prompt": video_prompt,
                                    "duration": duration,
                                    "error": video_url,
                                    "timestamp": timestamp
                                })
                                st.error(video_url)
                                
                                app_logger.log_user_action("video_generation_failed", {
                                    "error": video_url,
                                    "generation_time_seconds": round(generation_time, 3),
                                    "duration": duration
                                })
                            else:
                                # Get the current global video count and stats
                                current_global_count = global_counter.get_video_count()
                                video_stats = global_counter.get_statistics()
                                
                                st.session_state.messages.append({
                                    "type": "video",
                                    "prompt": video_prompt,
                                    "video_url": video_url,
                                    "duration": duration,
                                    "global_video_number": current_global_count,
                                    "timestamp": timestamp
                                })
                                
                                # Enhanced success message with duration-specific info
                                success_msg = f"✅ Video generated successfully! (Global Video #{current_global_count})"
                                if duration == 5:
                                    success_msg += f" | Total 5s videos: {video_stats['videos_5s']}"
                                elif duration == 8:
                                    success_msg += f" | Total 8s videos: {video_stats['videos_8s']}"
                                
                                st.success(success_msg)
                                
                                app_logger.log_user_action("video_generation_completed", {
                                    "generation_time_seconds": round(generation_time, 3),
                                    "filename": video_url,
                                    "duration": duration,
                                    "global_video_number": current_global_count,
                                    "total_duration_seconds": video_stats["total_video_duration_seconds"],
                                    "videos_5s": video_stats["videos_5s"],
                                    "videos_8s": video_stats["videos_8s"]
                                })
                                
                                st.rerun()
                                
                        except Exception as e:
                            generation_time = time.time() - start_time
                            error_msg = f"Error generating video: {str(e)}"
                            st.session_state.messages.append({
                                "type": "video",
                                "prompt": video_prompt,
                                "duration": duration,
                                "error": error_msg,
                                "timestamp": timestamp
                            })
                            st.error(error_msg)
                            
                            app_logger.log_error("video_generation_exception", str(e), {
                                "prompt_length": len(video_prompt),
                                "generation_time_seconds": round(generation_time, 3),
                                "duration": duration
                            })
    
    @tracer.trace_user_action("render_video_interface")
    def render_video_interface(self):
        """Render the complete video generation interface - same as existing pattern"""
        app_logger.log_system_event("video_interface_rendered", {})
        
        duration, resolution = self.render_video_settings()
        
        # Display video generation history
        st.subheader("🎬 Video Generation")
        
        self.display_video_history()
        self.handle_video_generation(duration, resolution)