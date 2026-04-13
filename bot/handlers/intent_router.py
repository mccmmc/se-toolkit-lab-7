"""Intent router — handles natural language messages via LLM."""

from services.llm_client import LLMClient
from services.api_client import APIClient, APIError
from config import BotConfig


async def handle_natural_language(user_message: str) -> str:
    """Route a natural language message through the LLM.

    The LLM decides which tool to call, executes it, and produces the final answer.
    """
    try:
        config = BotConfig()
        llm = LLMClient(config)
        return await llm.route(user_message)
    except Exception as e:
        # LLM unavailable — return helpful fallback
        return (
            f"I'm having trouble connecting to my brain right now ({e}). "
            "Try using slash commands like /health, /labs, or /scores lab-04 instead."
        )
