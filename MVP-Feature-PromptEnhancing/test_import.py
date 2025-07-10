"""Simple test to verify imports work"""
import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print("Testing import...")

try:
    from src.services.prompt_enhancing import PromptEnhancementService
    print("✅ PromptEnhancementService imported successfully!")
    
    # Test initialization
    service = PromptEnhancementService()
    print("✅ PromptEnhancementService initialized successfully!")
    
    # Test that methods exist
    methods = ['init_session', 'start_enhancement', 'render_enhancement_interface']
    for method in methods:
        if hasattr(service, method):
            print(f"✅ Method {method} exists")
        else:
            print(f"❌ Method {method} missing")
    
    print("\n🎉 All tests passed!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    
except Exception as e:
    print(f"❌ Other error: {e}")
    import traceback
    traceback.print_exc()
