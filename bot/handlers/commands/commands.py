"""Command handlers for the Telegram bot.

These are plain functions that take input and return text.
They don't depend on Telegram — same functions work from
--test mode, unit tests, or the Telegram bot.
"""


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
    """Handle /health command — check backend health.
    
    TODO (Task 2): Call backend /health endpoint and return real status.
    For now, returns placeholder.
    """
    return "🏥 Backend health: Not implemented yet (placeholder for Task 2)"


def handle_labs() -> str:
    """Handle /labs command — list available labs.
    
    TODO (Task 2): Call backend /items endpoint and return real lab list.
    For now, returns placeholder.
    """
    return "📚 Available labs: Not implemented yet (placeholder for Task 2)"


def handle_scores(lab_name: str | None = None) -> str:
    """Handle /scores command — view lab scores.
    
    TODO (Task 2): Call backend /analytics endpoint and return real scores.
    For now, returns placeholder.
    """
    if lab_name:
        return f"📊 Scores for {lab_name}: Not implemented yet (placeholder for Task 2)"
    return "📊 Scores: Please specify a lab (e.g. /scores lab-04)"
