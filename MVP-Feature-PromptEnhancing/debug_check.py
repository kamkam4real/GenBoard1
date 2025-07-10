"""Debug script to check if all imports work correctly"""
import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print(f"Current directory: {current_dir}")
print(f"Python path: {sys.path}")

# Test all imports
try:
    print("Testing imports...")
    
    from src.utils.logger import app_logger
    print("✅ Logger imported")
    
    from src.utils.tracer import tracer
    print("✅ Tracer imported")
    
    from src.utils.global_counter import global_counter
    print("✅ Global counter imported")
    
    from src.config.settings import AppConfig
    print("✅ Config imported")
    
    from src.services.auth_service import AuthService
    print("✅ Auth service imported")
    
    from src.services.chat_service import ChatService
    print("✅ Chat service imported")
    
    from src.services.image_service import ImageService
    print("✅ Image service imported")
    
    from src.services.video_service import VideoService
    print("✅ Video service imported")
    
    from src.services.prompt_enhancing import PromptEnhancementService
    print("✅ Prompt enhancement service imported")
    
    from src.ui.components import UIComponents
    print("✅ UI components imported")
    
    print("\n🎉 All imports successful!")
    
    # Test service initialization
    print("\nTesting service initialization...")
    
    auth_service = AuthService()
    print("✅ Auth service initialized")
    
    chat_service = ChatService()
    print("✅ Chat service initialized")
    
    image_service = ImageService()
    print("✅ Image service initialized")
    
    video_service = VideoService()
    print("✅ Video service initialized")
    
    prompt_enhancement_service = PromptEnhancementService()
    print("✅ Prompt enhancement service initialized")
    
    ui_components = UIComponents()
    print("✅ UI components initialized")
    
    print("\n🎉 All services initialized successfully!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
    
except Exception as e:
    print(f"❌ Other error: {e}")
    import traceback
    traceback.print_exc()
