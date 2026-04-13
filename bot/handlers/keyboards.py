"""Inline keyboard layouts for Telegram."""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_start_keyboard() -> InlineKeyboardMarkup:
    """Keyboard shown after /start — common actions."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📚 Available labs", callback_data="cmd_labs"),
                InlineKeyboardButton(text="🏥 Health check", callback_data="cmd_health"),
            ],
            [
                InlineKeyboardButton(text="📊 Scores lab-04", callback_data="cmd_scores_lab04"),
                InlineKeyboardButton(text="🏆 Top learners", callback_data="cmd_top_lab04"),
            ],
        ]
    )


def get_help_keyboard() -> InlineKeyboardMarkup:
    """Keyboard shown with /help."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📚 Labs", callback_data="cmd_labs"),
                InlineKeyboardButton(text="📊 Scores lab-04", callback_data="cmd_scores_lab04"),
            ],
            [
                InlineKeyboardButton(text="👥 Groups lab-04", callback_data="cmd_groups_lab04"),
                InlineKeyboardButton(text="🏆 Top 5 lab-04", callback_data="cmd_top5_lab04"),
            ],
        ]
    )


def handle_callback(callback_data: str) -> str | None:
    """Handle inline keyboard callback queries.

    Returns a response string, or None if not recognized.
    """
    callback_map = {
        "cmd_labs": "/labs",
        "cmd_health": "/health",
        "cmd_scores_lab04": "/scores lab-04",
        "cmd_top_lab04": "who are the top 10 students in lab 4",
        "cmd_top5_lab04": "who are the top 5 students in lab 4",
        "cmd_groups_lab04": "how are groups performing in lab 4",
    }
    return callback_map.get(callback_data)
