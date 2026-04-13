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
from handlers.keyboards import get_start_keyboard, get_help_keyboard, handle_callback
from config import BotConfig


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


def run_telegram_bot():
    """Run the bot in Telegram polling mode.

    Uses aiogram to connect to Telegram and route messages
    through the same handlers as --test mode.
    """
    from aiogram import Bot, Dispatcher, types
    from aiogram.filters import Command, CommandStart

    config = BotConfig()
    if not config.bot_token:
        print("Error: BOT_TOKEN is not set. Check .env.bot.secret or .env.docker.secret")
        sys.exit(1)

    bot = Bot(token=config.bot_token)
    dp = Dispatcher()

    @dp.message(CommandStart())
    async def cmd_start(message: types.Message):
        response = handle_start()
        await message.answer(response, reply_markup=get_start_keyboard())

    @dp.message(Command("help"))
    async def cmd_help(message: types.Message):
        response = handle_help()
        await message.answer(response, reply_markup=get_help_keyboard())

    @dp.message(Command("health"))
    async def cmd_health(message: types.Message):
        response = handle_health()
        await message.answer(response)

    @dp.message(Command("labs"))
    async def cmd_labs(message: types.Message):
        response = handle_labs()
        await message.answer(response)

    @dp.message(Command("scores"))
    async def cmd_scores(message: types.Message):
        # Extract lab from command args
        lab_name = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
        response = handle_scores(lab_name)
        await message.answer(response)

    @dp.callback_query(lambda c: c.data and c.data.startswith("cmd_"))
    async def handle_button_callback(callback: types.CallbackQuery):
        command = handle_callback(callback.data)
        if command:
            if command.startswith("/"):
                response = route_command(command)
            else:
                response = await route_message_async(command)
            await callback.message.answer(response)
        await callback.answer()

    @dp.message()
    async def handle_message(message: types.Message):
        response = await route_message_async(message.text)
        await message.answer(response)

    async def main():
        print("Application started", file=sys.stderr)
        await dp.start_polling(bot)

    asyncio.run(main())


def main():
    """Main entry point."""
    args = parse_args()

    if args.test:
        # Test mode: route message and print to stdout
        response = asyncio.run(route_message_async(args.test))
        print(response)
        sys.exit(0)

    # Telegram mode: polling
    run_telegram_bot()


if __name__ == "__main__":
    main()
