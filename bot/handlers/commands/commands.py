"""Command handlers for the Telegram bot.

These are plain functions that take input and return text.
They don't depend on Telegram — same functions work from
--test mode, unit tests, or the Telegram bot.
"""

from services.api_client import APIClient, APIError
from config import BotConfig


def handle_start() -> str:
    """Handle /start command — welcome message."""
    return (
        "👋 Welcome to the LMS Bot!\n\n"
        "I can help you check system status, browse labs, and view scores.\n"
        "Use /help to see all available commands."
    )


def handle_help() -> str:
    """Handle /help command — list all commands."""
    return (
        "📋 Available commands:\n\n"
        "/start — Welcome message\n"
        "/help — Show this help\n"
        "/health — Check backend status\n"
        "/labs — List available labs\n"
        "/scores <lab> — View scores for a specific lab"
    )


def handle_health() -> str:
    """Handle /health command — check backend health."""
    try:
        config = BotConfig()
        api = APIClient(config)
        items = api.get_items()
        labs = [i for i in items if i.get("type") == "lab"]
        tasks = [i for i in items if i.get("type") == "task"]
        return f"✅ Backend is healthy. {len(labs)} labs, {len(tasks)} tasks available."
    except APIError as e:
        return f"❌ Backend error: {e.detail}"


def handle_labs() -> str:
    """Handle /labs command — list available labs."""
    try:
        config = BotConfig()
        api = APIClient(config)
        items = api.get_items()
        labs = [i for i in items if i.get("type") == "lab"]
        if not labs:
            return "📚 No labs found."
        lines = ["📚 Available labs:"]
        for lab in labs:
            lines.append(f"• {lab.get('title', 'Unknown')}")
        return "\n".join(lines)
    except APIError as e:
        return f"❌ Backend error: {e.detail}"


def handle_scores(lab_name: str | None = None) -> str:
    """Handle /scores command — view lab scores."""
    if not lab_name:
        return "📊 Scores: Please specify a lab (e.g. /scores lab-04)"

    try:
        config = BotConfig()
        api = APIClient(config)
        rates = api.get_pass_rates(lab_name)
        if not rates:
            return f"📊 No pass rate data found for '{lab_name}'. Try a lab ID (e.g. /scores 4)."
        lines = [f"📊 Pass rates for '{lab_name}':"]
        for rate in rates:
            task_name = rate.get("task_title", rate.get("task", "Unknown"))
            # API returns avg_score; handle both naming conventions
            score = rate.get("avg_score", rate.get("pass_rate", rate.get("rate", 0)))
            attempts = rate.get("attempts", rate.get("count", 0))
            lines.append(f"• {task_name}: {score:.1f}% ({attempts} attempts)")
        return "\n".join(lines)
    except APIError as e:
        return f"❌ Backend error: {e.detail}"
