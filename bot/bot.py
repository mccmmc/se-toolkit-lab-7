"""Telegram bot entry point with --test mode support."""

import argparse
import asyncio
import sys
from pathlib import Path

# Add bot directory to path so imports work
bot_dir = Path(__file__).parent
sys.path.insert(0, str(bot_dir))

from handlers.commands.commands import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
)
from handlers.intent_router import handle_natural_language


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Telegram bot with test mode")
    parser.add_argument(
        "--test",
        type=str,
        default=None,
        help="Test a command and print response to stdout (e.g. --test '/start')",
    )
    return parser.parse_args()


def route_command(command: str) -> str:
    """Route a command string to the appropriate handler.

    This is the core routing logic — same handlers work from
    --test mode, unit tests, or Telegram.
    """
    # Strip leading slash and normalize
    cmd = command.strip().lstrip("/").lower()

    handlers = {
        "start": handle_start,
        "help": handle_help,
        "health": handle_health,
        "labs": handle_labs,
    }

    if cmd in handlers:
        return handlers[cmd]()

    if cmd.startswith("scores"):
        # Extract lab name if provided (e.g. "/scores lab-04")
        parts = command.strip().split()
        lab_name = parts[1] if len(parts) > 1 else None
        return handle_scores(lab_name)

    return f"Unknown command: {command}. Use /help to see available commands."


async def route_message_async(text: str) -> str:
    """Route a user message — could be a slash command or natural language.

    Async version for --test mode.
    """
    text = text.strip()

    # Slash commands go to sync handlers
    if text.startswith("/"):
        return route_command(text)

    # Plain text goes to LLM intent router
    return await handle_natural_language(text)


def main():
    """Main entry point."""
    args = parse_args()

    if args.test:
        # Test mode: route message and print to stdout
        response = asyncio.run(route_message_async(args.test))
        print(response)
        sys.exit(0)

    # Telegram mode (implemented in later tasks)
    print("Telegram mode not yet implemented. Use --test mode for now.")
    print("Example: uv run bot.py --test '/start'")
    print("Example: uv run bot.py --test 'what labs are available'")


if __name__ == "__main__":
    main()
