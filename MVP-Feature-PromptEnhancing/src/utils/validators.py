"""Input validation utilities"""
import re

class Validators:
    """Input validation utilities"""
    
    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """Validate OpenAI API key format"""
        if not api_key:
            return False
        
        # Basic format validation for OpenAI API keys
        pattern = r'^sk-[a-zA-Z0-9]{48}$'
        return bool(re.match(pattern, api_key))
    
    @staticmethod
    def validate_prompt(prompt: str, min_length: int = 1, max_length: int = 1000) -> tuple[bool, str]:
        """Validate user prompt"""
        if not prompt or not prompt.strip():
            return False, "Prompt cannot be empty"
        
        prompt = prompt.strip()
        
        if len(prompt) < min_length:
            return False, f"Prompt must be at least {min_length} characters long"
        
        if len(prompt) > max_length:
            return False, f"Prompt must be less than {max_length} characters long"
        
        return True, "Valid"
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for downloads"""
        # Remove invalid characters for filenames
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        return filename[:50]  # Limit length