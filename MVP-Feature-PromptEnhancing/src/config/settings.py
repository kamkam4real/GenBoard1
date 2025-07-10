"""Application configuration settings"""

class AppConfig:
    """Application configuration class"""
    
    PAGE_CONFIG = {
        "page_title": "ChatGPT Clone with DALL-E & VEO",
        "page_icon": "🤖",
        "layout": "wide",
        "initial_sidebar_state": "expanded"
    }
    
    # Chat settings
    CHAT_MODELS = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "gpt-4o"]
    DEFAULT_TEMPERATURE = 0.7
    MAX_TOKENS = 1000
    
    # Image settings
    IMAGE_SIZES = ["1024x1024", "1792x1024", "1024x1792"]
    IMAGE_QUALITIES = ["standard", "hd"]
    DALL_E_MODEL = "dall-e-3"
    
    # Video settings
    VIDEO_DURATIONS = [5,6,7,8]  # Duration in seconds as integers
    VIDEO_RESOLUTIONS = [720, 1080]  # Resolution height in pixels as integers
    VEO_MODEL = "veo-2.0-generate-001"
    
    # UI settings
    DATETIME_FORMAT = "%H:%M:%S"
    
    # API settings
    OPENAI_BASE_URL = "https://api.openai.com/v1"
    GOOGLE_API_BASE_URL = "https://aiplatform.googleapis.com/v1"