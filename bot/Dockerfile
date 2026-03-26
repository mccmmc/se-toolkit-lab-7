# Bot Dockerfile using uv for dependency management
# See: https://docs.astral.sh/uv/guides/integration/docker/

ARG REGISTRY_PREFIX=harbor.pg.innopolis.university/docker-hub-cache/
FROM ${REGISTRY_PREFIX}astral/uv:python3.14-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Copy root project files for dependency resolution
COPY pyproject.toml uv.lock ./

# Copy bot pyproject.toml for reference
COPY bot/pyproject.toml ./bot/

# Sync dependencies (includes bot dependencies from root pyproject.toml)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

# Copy bot source code
COPY bot/ ./bot/

# ---
# Stage 2: runtime image
# ---

ARG REGISTRY_PREFIX=harbor.pg.innopolis.university/docker-hub-cache/
FROM ${REGISTRY_PREFIX}python:3.14.2-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8

# Create non-root user
RUN groupadd --system --gid 999 nonroot \
    && useradd --system --gid 999 --uid 999 --create-home nonroot

# Copy application from builder
COPY --from=builder --chown=nonroot:nonroot /app /app

# Add venv to PATH
ENV PATH="/app/.venv/bin:$PATH"

USER nonroot

WORKDIR /app

# Run the bot
CMD ["python", "bot/bot.py"]
