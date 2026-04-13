"""LLM client with tool-calling support."""

import asyncio
import json
import sys
from openai import AsyncOpenAI

from config import BotConfig

# Tool definitions — 9 backend endpoints as LLM function schemas
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_items",
            "description": "List all labs and tasks. Use this when the user asks about available labs, tasks, or wants to browse the catalog.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_learners",
            "description": "List enrolled students and their groups. Use when the user asks about students, learners, or enrollment.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_scores",
            "description": "Get score distribution (4 buckets: 0-25, 26-50, 51-75, 76-100) for a lab. Use when the user asks about score distribution or histogram.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'. If the user says 'lab 4', use 'lab-04'.",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_pass_rates",
            "description": "Get per-task average scores and attempt counts for a lab. Use when the user asks about pass rates, task performance, or scores for a specific lab.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01', 'lab-04'. If the user says 'lab 4', use 'lab-04'.",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_timeline",
            "description": "Get submissions per day for a lab. Use when the user asks about activity over time, daily submissions, or timeline.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01'.",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_groups",
            "description": "Get per-group average scores and student counts for a lab. Use when the user asks about group performance, compares groups, or asks which group is best.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01'.",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_learners",
            "description": "Get top N learners by average score for a lab. Use when the user asks about top students, leaderboard, or best performers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01'.",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of top learners to return. Default 10.",
                    },
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_completion_rate",
            "description": "Get completion rate (percentage of learners who scored >= 60) for a lab. Use when the user asks about completion rate, how many students passed, or overall lab success.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab": {
                        "type": "string",
                        "description": "Lab identifier, e.g. 'lab-01'.",
                    }
                },
                "required": ["lab"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "trigger_sync",
            "description": "Trigger ETL data sync from the autochecker. Use only when the user explicitly asks to sync or refresh data.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]

SYSTEM_PROMPT = """You are an LMS assistant. Your job is to help users get information about labs, tasks, students, and scores.

You have access to tools that fetch data from the backend. When you need information, call the appropriate tool(s). After receiving tool results, analyze the data and provide a clear, concise answer.

Rules:
- Always call tools when you need data — don't guess or make up numbers.
- For multi-step questions (e.g. "which lab has the lowest pass rate?"), call tools sequentially: first get_items to find labs, then get_pass_rates for each.
- If the user sends a greeting, respond warmly and mention your capabilities.
- If the user sends gibberish or something you can't help with, politely explain what you can do.
- If the user mentions a lab ambiguously (e.g. "lab 4"), ask what they want to know about it, or proactively show available info.
- Format numbers nicely (1 decimal place for percentages).
- Keep responses concise but informative."""


class LLMClient:
    """Async LLM client with tool-calling loop."""

    def __init__(self, config: BotConfig | None = None):
        self.config = config or BotConfig()
        self.client = AsyncOpenAI(
            api_key=self.config.llm_api_key,
            base_url=self.config.llm_api_base_url,
        )
        self.model = self.config.llm_api_model

    async def route(self, user_message: str) -> str:
        """Main entry point: send message to LLM, execute tool calls, return final answer.

        Implements the tool-calling loop:
        1. Send user message + tool definitions to LLM
        2. If LLM calls tools, execute them and feed results back
        3. Repeat until LLM produces final text response
        """
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]

        max_iterations = 10
        for iteration in range(max_iterations):
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
            )

            choice = response.choices[0]
            message = choice.message

            # If LLM produced text response (no tool calls) — we're done
            if not message.tool_calls:
                return message.content or "I'm sorry, I couldn't process your request."

            # Execute tool calls
            messages.append(message)  # assistant message with tool_calls

            for tool_call in message.tool_calls:
                fn_name = tool_call.function.name
                fn_args = json.loads(tool_call.function.arguments)

                print(
                    f"[tool] LLM called: {fn_name}({json.dumps(fn_args)})",
                    file=sys.stderr,
                )

                result = await self._execute_tool(fn_name, fn_args)
                result_str = json.dumps(result, default=str)

                print(
                    f"[tool] Result: {len(result_str)} chars",
                    file=sys.stderr,
                )

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result_str,
                    }
                )

        return "I'm sorry, the request took too many steps. Please try a simpler question."

    async def _execute_tool(self, name: str, args: dict) -> list | dict:
        """Execute a tool function and return its result."""
        from services.api_client import APIClient

        api = APIClient(self.config)

        tool_map = {
            "get_items": lambda: api.get_items(),
            "get_learners": lambda: api._request("GET", "/learners/"),
            "get_scores": lambda: api._request(
                "GET", "/analytics/scores", params={"lab": args["lab"]}
            ),
            "get_pass_rates": lambda: api.get_pass_rates(args["lab"]),
            "get_timeline": lambda: api._request(
                "GET", "/analytics/timeline", params={"lab": args["lab"]}
            ),
            "get_groups": lambda: api._request(
                "GET", "/analytics/groups", params={"lab": args["lab"]}
            ),
            "get_top_learners": lambda: api._request(
                "GET",
                "/analytics/top-learners",
                params={"lab": args["lab"], "limit": str(args.get("limit", 10))},
            ),
            "get_completion_rate": lambda: api._request(
                "GET", "/analytics/completion-rate", params={"lab": args["lab"]}
            ),
            "trigger_sync": lambda: api._request("POST", "/pipeline/sync"),
        }

        if name not in tool_map:
            return {"error": f"Unknown tool: {name}"}

        try:
            return await asyncio.to_thread(tool_map[name])
        except Exception as e:
            return {"error": str(e)}
