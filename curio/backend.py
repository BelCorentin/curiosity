"""Claude Agent SDK wrapper — one interactive game session per PlayScreen.

Uses ClaudeSDKClient so the riddle → guess → lesson → note flow is one
conversation with context. Auth comes from the installed `claude` CLI login;
no API key needed.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
)

from .config import Config
from .prompts import build_system_prompt

TOOL_LABELS = {
    "Read": "reading",
    "Write": "writing note",
    "Edit": "updating note",
    "Glob": "scanning notes",
    "Grep": "searching",
}


@dataclass
class GameEvent:
    kind: str  # "text" | "tool" | "done" | "error"
    payload: str = ""


class Game:
    """One live game session against Claude."""

    def __init__(self, cfg: Config, mode: str):
        self.cfg = cfg
        options = ClaudeAgentOptions(
            system_prompt=build_system_prompt(cfg, mode),
            allowed_tools=["Read", "Write", "Edit", "Glob", "Grep"],
            permission_mode="acceptEdits",
            cwd=str(cfg.workdir),
        )
        self._client = ClaudeSDKClient(options=options)
        self._connected = False

    async def connect(self) -> None:
        await self._client.connect()
        self._connected = True

    async def close(self) -> None:
        if self._connected:
            self._connected = False
            await self._client.disconnect()

    async def send(self, text: str) -> AsyncIterator[GameEvent]:
        """Send one user turn, yield events until Claude's turn completes."""
        try:
            await self._client.query(text)
            async for message in self._client.receive_response():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock) and block.text.strip():
                            yield GameEvent("text", block.text)
                        elif isinstance(block, ToolUseBlock):
                            label = TOOL_LABELS.get(block.name, block.name.lower())
                            yield GameEvent("tool", label)
                elif isinstance(message, ResultMessage):
                    if message.is_error:
                        yield GameEvent("error", message.result or "session error")
            yield GameEvent("done")
        except Exception as exc:  # surface SDK/CLI failures in the UI
            yield GameEvent("error", str(exc))
