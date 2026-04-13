"""Configuration management — loads secrets from .env files."""

import os
from pathlib import Path


def load_env_file(env_path: Path) -> dict[str, str]:
    """Load key=value pairs from a .env file.
    
    Simple parser — no external dependencies needed.
    """
    config = {}
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    config[key.strip()] = value.strip()
    return config


class BotConfig:
    """Bot configuration loaded from environment variables."""
    
    def __init__(self):
        # Load from .env.bot.secret if it exists
        bot_dir = Path(__file__).parent
        env_file = bot_dir.parent / ".env.bot.secret"
        env_values = load_env_file(env_file)
        
        # Also check actual environment variables (for Docker deployment)
        self.bot_token = os.environ.get("BOT_TOKEN", env_values.get("BOT_TOKEN", ""))
        self.lms_api_base_url = os.environ.get(
            "LMS_API_BASE_URL", env_values.get("LMS_API_BASE_URL", "http://localhost:42002")
        )
        self.lms_api_key = os.environ.get(
            "LMS_API_KEY", env_values.get("LMS_API_KEY", "")
        )
        self.llm_api_key = os.environ.get(
            "LLM_API_KEY", env_values.get("LLM_API_KEY", "")
        )
    
    def is_configured(self) -> bool:
        """Check if required config is present."""
        return bool(self.bot_token and self.lms_api_base_url)
