"""Video prompt enhancement service for optimizing Veo 3 prompts through interactive conversation"""
import streamlit as st
from datetime import datetime
import json
import time
from typing import Dict, List, Optional
from ..utils.logger import app_logger
from ..utils.tracer import tracer
from ..utils.global_counter import global_counter

class PromptEnhancementService:
    """Handle video prompt optimization through multi-stage refinement"""
    
    # Refinement stages configuration
    REFINEMENT_STAGES = {
        "concept": {
            "title": "🎬 Concept & Setting",
            "description": "Define the basic concept, genre, and setting",
            "questions": [
                "What's the main genre or style? (cinematic, documentary, animation, etc.)",
                "Where does this take place? (location, time period, environment)",
                "What's the overall purpose or story goal?"
            ],
            "suggestions": [
                "Cinematic short film",
                "Documentary style",
                "Animation/CGI",
                "Music video aesthetic",
                "Commercial/advertising"
            ]
        },
        "mood": {
            "title": "🎨 Mood & Atmosphere",
            "description": "Set the emotional tone, lighting, and atmosphere",
            "questions": [
                "What emotions should viewers feel?",
                "What's the lighting style? (natural, dramatic, soft, etc.)",
                "How would you describe the overall atmosphere?"
            ],
            "suggestions": [
                "Warm and inviting",
                "Dark and mysterious",
                "Bright and energetic",
                "Calm and serene",
                "Tense and dramatic"
            ]
        },
        "subjects": {
            "title": "👥 Characters & Objects",
            "description": "Define the main subjects, their style and characteristics",
            "questions": [
                "Who or what are the main subjects?",
                "What's their visual style or appearance?",
                "How do they move or behave?"
            ],
            "suggestions": [
                "Realistic human characters",
                "Stylized/artistic figures",
                "Animals or creatures",
                "Objects and products",
                "Abstract elements"
            ]
        },
        "visual": {
            "title": "📹 Visual Details",
            "description": "Specify camera work, composition, and visual effects",
            "questions": [
                "What camera angles or movements?",
                "Any specific visual effects or transitions?",
                "What's the visual composition style?"
            ],
            "suggestions": [
                "Static wide shots",
                "Dynamic camera movement",
                "Close-up details",
                "Aerial/drone perspective",
                "Smooth transitions"
            ]
        },
        "polish": {
            "title": "✨ Final Polish",
            "description": "Refine for conciseness and cinematic language",
            "questions": [
                "Any specific technical requirements?",
                "Should we emphasize certain visual elements?",
                "Any final adjustments to the overall vision?"
            ],
            "suggestions": [
                "Add technical camera terms",
                "Emphasize color palette",
                "Include timing/pacing",
                "Specify resolution/format",
                "Add artistic references"
            ]
        }
    }
    
    # Example high-quality prompts for guidance
    EXAMPLE_PROMPTS = {
        "cinematic_nature": {
            "title": "Cinematic Nature Scene",
            "prompt": "A cinematic wide-angle shot of a misty forest at golden hour, with volumetric sunbeams filtering through ancient oak trees. Smooth camera push-in revealing a crystal-clear stream with gentle rapids. Natural color grading with warm highlights and cool shadows. Shot on 35mm film with shallow depth of field.",
            "tags": ["cinematic", "nature", "golden hour", "forest", "film"]
        },
        "urban_lifestyle": {
            "title": "Urban Lifestyle",
            "prompt": "Dynamic handheld camera following a young artist walking through vibrant city streets at sunset. Colorful street art and neon signs create bokeh in the background. Warm color palette with high contrast. Quick cuts between wide establishing shots and intimate close-ups of facial expressions.",
            "tags": ["urban", "lifestyle", "dynamic", "street", "portrait"]
        },
        "product_showcase": {
            "title": "Premium Product Showcase",
            "prompt": "Elegant macro photography of a luxury watch on marble surface. Slow 360-degree rotation with dramatic side lighting creating sharp shadows. Minimal composition with negative space. Cool color temperature with metallic highlights. Smooth motion with precise focus pulls revealing intricate details.",
            "tags": ["product", "luxury", "macro", "minimal", "commercial"]
        }
    }
    
    def __init__(self):
        """Initialize the prompt enhancement service"""
        self.init_enhancement_session()
    
    @tracer.trace_api_call("openai", "gpt-4")
    def get_enhancement_suggestion(self, client, stage: str, user_input: str, context: Dict) -> str:
        """Get AI enhancement suggestions for current stage"""
        try:
            stage_info = self.REFINEMENT_STAGES[stage]
            
            messages = [
                {
                    "role": "system",
                    "content": f"""You are a video prompt optimization expert for Veo 3 AI video generation. 
                    Current stage: {stage_info['title']} - {stage_info['description']}
                    
                    Help refine the user's input into professional video prompt language.
                    Focus on visual, technical, and cinematic terminology.
                    Be concise but descriptive. Suggest improvements while preserving the user's vision.
                    
                    Previous context: {json.dumps(context, indent=2)}"""
                },
                {
                    "role": "user", 
                    "content": f"Stage: {stage}\nUser input: {user_input}\n\nPlease suggest improvements and refinements for this stage."
                }
            ]
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=300
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            app_logger.log_error("enhancement_suggestion_error", str(e), {
                "stage": stage,
                "input_length": len(user_input)
            })
            return f"Error getting suggestion: {str(e)}"
    
    @tracer.trace_api_call("openai", "gpt-4")
    def generate_final_prompt(self, client, refinement_data: Dict) -> str:
        """Generate the final optimized prompt from all refinement stages"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": """You are a video prompt optimization expert for Veo 3 AI video generation.
                    
                    Create a single, cohesive, professional video prompt that combines all the refinement stages.
                    The prompt should be:
                    - Clear and specific
                    - Use professional cinematography language
                    - Be concise but comprehensive
                    - Ready for Veo 3 API use
                    - Include technical details when relevant
                    
                    Return ONLY the final prompt, no explanations."""
                },
                {
                    "role": "user",
                    "content": f"Combine these refinements into one optimized video prompt:\n\n{json.dumps(refinement_data, indent=2)}"
                }
            ]
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.3,
                max_tokens=400
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            app_logger.log_error("final_prompt_generation_error", str(e), {
                "refinement_stages": len(refinement_data)
            })
            return f"Error generating final prompt: {str(e)}"
    
    def init_enhancement_session(self):
        """Initialize a new prompt enhancement session"""
        if "enhancement_session" not in st.session_state:
            st.session_state.enhancement_session = {
                "active": False,
                "current_stage": "concept",
                "stages_data": {},
                "iteration_history": [],
                "start_time": None,
                "final_prompt": None
            }
    
    def start_enhancement_flow(self, initial_idea: str):
        """Start the enhancement flow with user's initial idea"""
        self.init_enhancement_session()
        
        # Increment global enhanced prompt counter with fallback
        try:
            enhanced_count = global_counter.increment_enhanced_prompt_count()
        except AttributeError:
            # Fallback if method doesn't exist
            enhanced_count = 1
            app_logger.log_error("missing_enhanced_prompt_counter", 
                               "increment_enhanced_prompt_count method not found", {})
        
        st.session_state.enhancement_session.update({
            "active": True,
            "current_stage": "concept",
            "stages_data": {"initial_idea": initial_idea},
            "iteration_history": [{
                "timestamp": datetime.now().isoformat(),
                "action": "session_started",
                "data": {"initial_idea": initial_idea}
            }],
            "start_time": datetime.now(),
            "final_prompt": None
        })
        
        app_logger.log_user_action("enhancement_session_started", {
            "initial_idea_length": len(initial_idea),
            "global_enhanced_count": enhanced_count
        })
        
        st.success("🚀 Enhancement flow started! Let's refine your idea step by step.")
        st.rerun()
    
    def process_stage_input(self, stage: str, user_input: str, use_ai_suggestion: bool = True):
        """Process user input for current stage"""
        session = st.session_state.enhancement_session
        
        # Store user input
        session["stages_data"][stage] = user_input
        
        # Add to iteration history
        session["iteration_history"].append({
            "timestamp": datetime.now().isoformat(),
            "action": "stage_completed",
            "stage": stage,
            "data": {"user_input": user_input}
        })
        
        app_logger.log_user_action("enhancement_stage_completed", {
            "stage": stage,
            "input_length": len(user_input),
            "use_ai_suggestion": use_ai_suggestion
        })
        
        # Get AI suggestion if requested
        ai_suggestion = None
        if use_ai_suggestion and st.session_state.get('client'):
            with st.spinner("Getting AI suggestions..."):
                ai_suggestion = self.get_enhancement_suggestion(
                    st.session_state.client,
                    stage,
                    user_input,
                    session["stages_data"]
                )
                
                session["iteration_history"].append({
                    "timestamp": datetime.now().isoformat(),
                    "action": "ai_suggestion",
                    "stage": stage,
                    "data": {"suggestion": ai_suggestion}
                })
        
        return ai_suggestion
    
    def advance_to_next_stage(self):
        """Move to the next refinement stage"""
        session = st.session_state.enhancement_session
        stages = list(self.REFINEMENT_STAGES.keys())
        current_index = stages.index(session["current_stage"])
        
        if current_index < len(stages) - 1:
            session["current_stage"] = stages[current_index + 1]
            app_logger.log_user_action("enhancement_stage_advanced", {
                "new_stage": session["current_stage"],
                "stage_index": current_index + 1
            })
        else:
            # All stages complete, generate final prompt
            self.generate_final_optimized_prompt()
    
    def generate_final_optimized_prompt(self):
        """Generate the final optimized prompt"""
        session = st.session_state.enhancement_session
        
        if st.session_state.get('client'):
            with st.spinner("Generating your final optimized prompt..."):
                final_prompt = self.generate_final_prompt(
                    st.session_state.client,
                    session["stages_data"]
                )
                
                session["final_prompt"] = final_prompt
                session["iteration_history"].append({
                    "timestamp": datetime.now().isoformat(),
                    "action": "final_prompt_generated",
                    "data": {"final_prompt": final_prompt}
                })
                
                app_logger.log_user_action("enhancement_final_prompt_generated", {
                    "prompt_length": len(final_prompt),
                    "stages_completed": len(session["stages_data"]) - 1  # Exclude initial_idea
                })
        else:
            st.error("AI client not available for final prompt generation")
    
    def export_session_data(self) -> Dict:
        """Export enhancement session data"""
        session = st.session_state.enhancement_session
        
        export_data = {
            "metadata": {
                "export_timestamp": datetime.now().isoformat(),
                "session_duration_minutes": (datetime.now() - session["start_time"]).total_seconds() / 60 if session["start_time"] else 0,
                "total_iterations": len(session["iteration_history"]),
                "stages_completed": len([k for k in session["stages_data"].keys() if k != "initial_idea"])
            },
            "initial_idea": session["stages_data"].get("initial_idea", ""),
            "final_prompt": session.get("final_prompt", ""),
            "refinement_stages": {k: v for k, v in session["stages_data"].items() if k != "initial_idea"},
            "iteration_history": session["iteration_history"]
        }
        
        return export_data
    
    @tracer.trace_user_action("render_example_prompts")
    def render_example_prompts(self):
        """Render example prompts section"""
        st.subheader("💡 Example High-Quality Prompts")
        st.markdown("Get inspired by these professionally crafted video prompts:")
        
        for key, example in self.EXAMPLE_PROMPTS.items():
            with st.expander(f"📝 {example['title']}"):
                st.markdown(f"**Prompt:**")
                st.code(example['prompt'], language="text")
                st.markdown(f"**Tags:** {', '.join(example['tags'])}")
                
                col1, col2 = st.columns([1, 3])
                with col1:
                    if st.button(f"Use as Template", key=f"template_{key}"):
                        self.start_enhancement_flow(example['prompt'])
                        app_logger.log_user_action("template_prompt_used", {
                            "template": key,
                            "template_title": example['title']
                        })
    
    @tracer.trace_user_action("render_enhancement_interface")
    def render_enhancement_interface(self):
        """Render the complete prompt enhancement interface"""
        self.init_enhancement_session()
        session = st.session_state.enhancement_session
        
        app_logger.log_system_event("enhancement_interface_rendered", {
            "session_active": session["active"],
            "current_stage": session.get("current_stage"),
            "has_final_prompt": bool(session.get("final_prompt"))
        })
        
        st.header("🎯 Video Prompt Optimizer")
        st.markdown("Transform your rough ideas into professional, AI-ready video prompts through guided refinement.")
        
        # Show example prompts
        self.render_example_prompts()
        
        st.markdown("---")
        
        # Check if session is active
        if not session["active"]:
            # Start new session
            st.subheader("🚀 Start Prompt Enhancement")
            
            initial_idea = st.text_area(
                "Describe your video idea (rough concept is fine):",
                placeholder="e.g., A peaceful scene of someone reading a book in a cozy cafe...",
                height=100,
                help="Don't worry about being perfect - we'll refine this together!"
            )
            
            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button("🎬 Start Enhancement", disabled=not initial_idea.strip()):
                    self.start_enhancement_flow(initial_idea)
        
        else:
            # Active session - show current stage
            current_stage = session["current_stage"]
            
            if session.get("final_prompt"):
                # Session complete - show results
                self.render_final_results()
            else:
                # Show current stage
                self.render_current_stage(current_stage)
            
            # Show progress and session controls
            st.markdown("---")
            self.render_session_controls()
    
    def render_current_stage(self, stage: str):
        """Render the current refinement stage"""
        stage_info = self.REFINEMENT_STAGES[stage]
        session = st.session_state.enhancement_session
        
        # Progress indicator
        stages = list(self.REFINEMENT_STAGES.keys())
        current_index = stages.index(stage)
        progress = (current_index) / len(stages)
        
        st.progress(progress, text=f"Stage {current_index + 1} of {len(stages)}")
        
        # Stage header
        st.subheader(stage_info["title"])
        st.markdown(stage_info["description"])
        
        # Show initial idea as context
        if "initial_idea" in session["stages_data"]:
            st.info(f"💡 **Your initial idea:** {session['stages_data']['initial_idea']}")
        
        # Stage questions
        st.markdown("**Consider these aspects:**")
        for question in stage_info["questions"]:
            st.markdown(f"• {question}")
        
        # Input methods
        input_method = st.radio(
            "How would you like to provide input?",
            ["Free text", "Guided selection"],
            key=f"input_method_{stage}",
            horizontal=True
        )
        
        user_input = ""
        
        if input_method == "Free text":
            user_input = st.text_area(
                f"Your input for {stage_info['title']}:",
                height=100,
                key=f"input_{stage}"
            )
        else:
            # Guided selection
            st.markdown("**Choose from suggestions (select multiple):**")
            selected_suggestions = []
            
            for suggestion in stage_info["suggestions"]:
                if st.checkbox(suggestion, key=f"suggestion_{stage}_{suggestion}"):
                    selected_suggestions.append(suggestion)
            
            # Additional custom input
            custom_input = st.text_input("Add custom details:", key=f"custom_{stage}")
            
            # Combine selections
            if selected_suggestions or custom_input:
                user_input = f"Selected: {', '.join(selected_suggestions)}"
                if custom_input:
                    user_input += f". Additional details: {custom_input}"
        
        # AI assistance toggle
        use_ai = st.checkbox("Get AI suggestions for refinement", value=True, key=f"ai_{stage}")
        
        # Action buttons
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("⬅️ Previous", disabled=current_index == 0):
                stages = list(self.REFINEMENT_STAGES.keys())
                session["current_stage"] = stages[current_index - 1]
                st.rerun()
        
        with col2:
            if st.button("➡️ Next", disabled=not user_input.strip()):
                if user_input.strip():
                    ai_suggestion = self.process_stage_input(stage, user_input, use_ai)
                    
                    if ai_suggestion and use_ai:
                        st.markdown("### 🤖 AI Suggestion:")
                        st.info(ai_suggestion)
                        
                        # Option to use AI suggestion
                        if st.button("Use AI suggestion instead"):
                            session["stages_data"][stage] = ai_suggestion
                    
                    self.advance_to_next_stage()
                    st.rerun()
    
    def render_final_results(self):
        """Render final results with export options"""
        session = st.session_state.enhancement_session
        
        st.subheader("🎉 Your Optimized Video Prompt")
        st.success("Enhancement complete! Here's your professional video prompt:")
        
        # Final prompt display
        st.markdown("### 📝 Final Prompt")
        final_prompt = session["final_prompt"]
        st.code(final_prompt, language="text")
        
        # Copy to clipboard button (using st.code with copy option)
        st.markdown("### 🎬 Ready to Generate")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🎥 Generate Video Now"):
                # Add prompt to video generation
                if "messages" not in st.session_state:
                    st.session_state.messages = []
                
                timestamp = datetime.now().strftime("%H:%M:%S")
                st.session_state.messages.append({
                    "type": "enhanced_prompt",
                    "prompt": final_prompt,
                    "enhancement_data": session["stages_data"],
                    "timestamp": timestamp
                })
                
                app_logger.log_user_action("enhanced_prompt_to_video", {
                    "prompt_length": len(final_prompt)
                })
                
                # Switch to video mode
                st.session_state.mode = "video"
                st.success("Prompt added to video generation! Switching to video mode...")
                time.sleep(1)
                st.rerun()
        
        with col2:
            # Export functionality
            export_data = self.export_session_data()
            export_json = json.dumps(export_data, indent=2)
            
            st.download_button(
                "📋 Export Session",
                export_json,
                file_name=f"prompt_enhancement_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        with col3:
            if st.button("🔄 Start New Enhancement"):
                session["active"] = False
                session["final_prompt"] = None
                st.rerun()
        
        # Show refinement summary
        st.markdown("### 📊 Enhancement Summary")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Stages Completed", len([k for k in session["stages_data"].keys() if k != "initial_idea"]))
            st.metric("Total Iterations", len(session["iteration_history"]))
        
        with col2:
            if session["start_time"]:
                duration = (datetime.now() - session["start_time"]).total_seconds() / 60
                st.metric("Session Duration", f"{duration:.1f} min")
    
    def render_session_controls(self):
        """Render session control panel"""
        session = st.session_state.enhancement_session
        
        st.subheader("🎛️ Session Controls")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 Save Progress"):
                export_data = self.export_session_data()
                st.session_state.saved_enhancement = export_data
                st.success("Progress saved!")
        
        with col2:
            if st.button("🔄 Reset Session"):
                # Use a simple confirmation with session state
                if "confirm_reset" not in st.session_state:
                    st.session_state.confirm_reset = False
                
                if not st.session_state.confirm_reset:
                    st.session_state.confirm_reset = True
                    st.warning("Click Reset Session again to confirm")
                else:
                    session["active"] = False
                    session["stages_data"] = {}
                    session["iteration_history"] = []
                    st.session_state.confirm_reset = False
                    st.success("Session reset!")
                    st.rerun()
        
        with col3:
            # Show iteration history
            if st.button("📜 View History"):
                st.session_state.show_history = not st.session_state.get("show_history", False)
        
        # Show history if toggled
        if st.session_state.get("show_history", False):
            st.markdown("### 🕐 Iteration History")
            for i, item in enumerate(reversed(session["iteration_history"])):
                with st.expander(f"{i+1}. {item['action']} - {item['timestamp'][:19]}"):
                    st.json(item)
