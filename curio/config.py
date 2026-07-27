"""Configuration and progress state, shared with the Claude Code skill.

Reads the same ~/curiosity/config.json and <notes_dir>/_progress.json the skill
uses, so playing in the TUI and playing inside Claude Code accrete into the
same knowledge base.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

CONFIG_PATH = Path.home() / "curiosity" / "config.json"


@dataclass
class Topic:
    slug: str
    title: str
    note: str
    source_section: str = ""
    first_played: str = ""
    last_review: str = ""
    plays: int = 1
    confidence: float | None = None


@dataclass
class Progress:
    streak: int = 0
    last_played: str = ""
    topics: list[Topic] = field(default_factory=list)

    @property
    def streak_alive(self) -> bool:
        """Streak counts if last played today or yesterday."""
        if not self.last_played:
            return False
        try:
            last = date.fromisoformat(self.last_played)
        except ValueError:
            return False
        return (date.today() - last).days <= 1


@dataclass
class Config:
    questions_file: Path
    notes_dir: Path
    map_file: str

    @property
    def progress_path(self) -> Path:
        return self.notes_dir / "_progress.json"

    @property
    def map_path(self) -> Path:
        return self.notes_dir / self.map_file

    @property
    def workdir(self) -> Path:
        """Deepest common ancestor of the questions file and notes dir — the
        directory the Claude session runs in so both are reachable."""
        common = os.path.commonpath([self.questions_file.parent, self.notes_dir])
        return Path(common)


def load_config() -> Config:
    data: dict = {
        "questions_file": str(Path.home() / "curiosity" / "questions.md"),
        "notes_dir": str(Path.home() / "curiosity" / "notes"),
        "map_file": "MAP.md",
    }
    if CONFIG_PATH.exists():
        data.update(json.loads(CONFIG_PATH.read_text()))
    return Config(
        questions_file=Path(data["questions_file"]).expanduser(),
        notes_dir=Path(data["notes_dir"]).expanduser(),
        map_file=data["map_file"],
    )


def load_progress(cfg: Config) -> Progress:
    path = cfg.progress_path
    if not path.exists():
        return Progress()
    try:
        raw = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return Progress()
    topics = []
    for t in raw.get("topics", []):
        topics.append(
            Topic(
                slug=t.get("slug", ""),
                title=t.get("title", ""),
                note=t.get("note", ""),
                source_section=t.get("source_section", ""),
                first_played=t.get("first_played", ""),
                last_review=t.get("last_review", ""),
                plays=t.get("plays", 1),
                confidence=t.get("confidence"),
            )
        )
    return Progress(
        streak=raw.get("streak", 0),
        last_played=raw.get("last_played", ""),
        topics=topics,
    )
