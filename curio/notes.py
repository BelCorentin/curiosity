"""Local parsing of curiosity notes — powers flashcards and the browser.

Notes follow the skill's format: YAML frontmatter, one `# Title`, a `> Seed`
blockquote, then `## The riddle`, `## What I learned`, `## 🔭 Zoom out`,
`## Open threads`, `## Log` sections (any subset may be present).
"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass, field
from pathlib import Path

from .config import Config


@dataclass
class Note:
    path: Path
    title: str
    seed: str = ""
    sections: dict[str, str] = field(default_factory=dict)

    @property
    def body(self) -> str:
        return strip_frontmatter(self.path.read_text())

    def section(self, *names: str) -> str:
        """First matching section by loose name (case/emoji-insensitive)."""
        for want in names:
            for key, text in self.sections.items():
                if want.lower() in key.lower():
                    return text
        return ""


@dataclass
class Flashcard:
    title: str
    front: str
    back: str
    note_path: Path


def strip_frontmatter(text: str) -> str:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4 :].lstrip("\n")
    return text


def parse_note(path: Path) -> Note:
    body = strip_frontmatter(path.read_text())
    title = path.stem
    m = re.search(r"^# (.+)$", body, re.MULTILINE)
    if m:
        title = m.group(1).strip()

    seed = ""
    m = re.search(r"^> Seed.*?:\s*\*?\"?(.+?)\"?\*?\s*$", body, re.MULTILINE)
    if m:
        seed = m.group(1).strip()

    sections: dict[str, str] = {}
    parts = re.split(r"^## (.+)$", body, flags=re.MULTILINE)
    # parts = [preamble, heading1, text1, heading2, text2, ...]
    for i in range(1, len(parts) - 1, 2):
        sections[parts[i].strip()] = parts[i + 1].strip()

    return Note(path=path, title=title, seed=seed, sections=sections)


def list_notes(cfg: Config) -> list[Note]:
    if not cfg.notes_dir.is_dir():
        return []
    notes = []
    for path in sorted(cfg.notes_dir.glob("*.md")):
        if path.name.startswith("_") or path.name == cfg.map_file:
            continue
        try:
            notes.append(parse_note(path))
        except OSError:
            continue
    return notes


def make_flashcards(notes: list[Note]) -> list[Flashcard]:
    cards = []
    for note in notes:
        back = note.section("what i learned")
        if not back:
            continue
        front = note.seed or note.section("riddle") or note.title
        cards.append(
            Flashcard(title=note.title, front=front, back=back, note_path=note.path)
        )
    return cards


def shuffled_flashcards(cfg: Config) -> list[Flashcard]:
    cards = make_flashcards(list_notes(cfg))
    random.shuffle(cards)
    return cards
