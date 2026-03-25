import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

def load_env_safely() -> bool:
    """
    Safely load environment variables from .env file
    Returns True if loaded successfully, False otherwise
    """
    try:
        # Load from .env file in the project root
        env_path = Path(__file__).parent.parent / '.env'
        return load_dotenv(env_path, override=True)
    except Exception as e:
        print(f"Warning: Could not load .env file: {e}")
        return False

def get_api_key(key_name: str, required: bool = True) -> Optional[str]:

    load_env_safely()
    
    # Get value
    value = os.getenv(key_name)
    
    if required and not value:
        raise ValueError(f"Required API key '{key_name}' not found in environment variables")

    return value
