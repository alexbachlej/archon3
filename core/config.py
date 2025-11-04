"""Configuration management"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    GPT5_MODEL: str = os.getenv("GPT5_MODEL", "gpt-5")
    GPT4O_MODEL: str = os.getenv("GPT4O_MODEL", "gpt-4o")
    CLAUDE_MODEL: str = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5-20250929")
    INPUT_DIR: str = "input"
    OUTPUT_DIR: str = "output"
    MAX_RETRIES: int = 3
    TEMPERATURE_ARCHITECT: float = 0.7
    TEMPERATURE_BUILDER: float = 0.3
    TEMPERATURE_VALIDATOR: float = 0.1
    TEMPERATURE_INTEGRATOR: float = 0.5
    
    @classmethod
    def validate(cls) -> bool:
        if not cls.OPENAI_API_KEY:
            print("⚠️  OPENAI_API_KEY not set")
            return False
        if not cls.ANTHROPIC_API_KEY:
            print("⚠️  ANTHROPIC_API_KEY not set")
            return False
        return True

config = Config()
