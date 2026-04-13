# Bot Development Plan

## Overview

This document outlines the development plan for building a Telegram bot that interacts with the LMS backend. The bot will support slash commands (`/start`, `/help`, `/health`, `/labs`, `/scores`) and natural language queries routed through an LLM.

## Architecture

### Layer 1: Handlers (No Telegram Dependency)
All command logic is implemented as plain Python functions in `bot/handlers/`. These functions take input parameters and return text strings. This design allows testing without Telegram — via `--test` mode or unit tests. The same functions are called from both the CLI test mode and the Telegram bot.

### Layer 2: Services
- **API Client** (`bot/services/api_client.py`): Wraps HTTP calls to the LMS backend. Handles Bearer token authentication, error handling, and response parsing.
- **LLM Client** (`bot/services/llm_client.py`): Wraps calls to an LLM API for intent recognition. The LLM will be given tool descriptions for each backend endpoint and will decide which tool to call based on user input.

### Layer 3: Telegram Integration
The Telegram bot (`bot.py`) will use `aiogram` to receive messages and route them to handlers. In test mode (`--test`), the routing logic is called directly without Telegram.

## Task Breakdown

### Task 1: Plan and Scaffold (Current)
- Create project structure (`bot/`, `bot/handlers/`, `bot/services/`)
- Implement `--test` mode in `bot.py`
- Create placeholder handlers for all commands
- Write this development plan
- Verify: `uv run bot.py --test "/start"` prints welcome message

### Task 2: Backend Integration
- Implement real API client in `bot/services/api_client.py`
- Update `/health` handler to call backend `/health` endpoint
- Update `/labs` handler to call backend `/items` endpoint and format lab list
- Update `/scores` handler to call backend `/analytics` endpoint
- Add error handling for backend failures (friendly messages, no crashes)
- Verify: All commands return real data from the backend

### Task 3: Intent-Based Natural Language Routing
- Implement LLM client with tool descriptions for all 9 backend endpoints
- Create intent router that sends user text to LLM and executes the chosen tool
- Update handlers to use LLM routing for non-command messages
- Verify: Plain text queries like "what labs are available" return correct data

### Task 4: Containerize and Deploy
- Create `Dockerfile` for the bot
- Add bot service to `docker-compose.yml`
- Configure environment variables for container networking (use service names, not `localhost`)
- Deploy to VM and verify in Telegram
- Document deployment process in README

## Key Decisions

1. **Testable handlers first** — This avoids the "works in Telegram but I can't debug it" problem.
2. **Environment-based config** — Secrets come from `.env` files, not hardcoded. Same pattern works locally and in Docker.
3. **LLM tool use over regex routing** — The LLM reads tool descriptions and decides which to call. This is more flexible and maintainable than keyword matching.
