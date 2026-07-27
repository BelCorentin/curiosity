# 🔭 curiosity

A tiny [Claude Code](https://claude.com/claude-code) skill that turns *your own* open questions
about the world into a **daily game**: a riddle, a tight honest mini-lesson, and a **"zoom out"**
that reframes the topic across history and makes you step back and requestion things. Every bite
gets saved as a linked note, so over time you build a personal *universe* of what you've learned.

Not flashcards. Not a quiz. A daily 5-minute "huh, I never thought about it that way" — that sticks
because it lands in a note you own.

```
🏰 Riddle:  "Medieval peasants owned their land and lived free — true or false?"
   → you guess →
📚 Lesson:  serfs held land, didn't own it; the workday myth; what historians actually argue
🔭 Zoom out: progress isn't linear — Egypt vs Athens vs medieval vs 1800s factory.
            "When someone sells you a golden age — golden for whom?"
   → saved to notes/Was medieval life idyllic.md, linked into your map
```

## How it works

1. You keep a plain-text file of questions you're curious about (any topic, any language).
2. Run `/curiosity` in Claude Code. It picks one, plays it as a game, waits for your guesses.
3. It writes a consolidation note per topic and links it into a growing `MAP.md` hub.
4. Streak + history live in a small `_progress.json`. Come back tomorrow. 🔥

## Install

Requires [Claude Code](https://claude.com/claude-code) (runs on your existing subscription — no API key).

```bash
git clone https://github.com/BelCorentin/curiosity.git
# make the skill visible to Claude Code (copy or symlink):
mkdir -p ~/.claude/skills
ln -s "$(pwd)/curiosity/skills/curiosity" ~/.claude/skills/curiosity
```

Then start Claude Code and type `/curiosity`. On first run it creates `~/curiosity/`, drops a
starter `questions.md`, and asks you to fill it with your own curiosities.

## `curio` — the terminal app

The same game as a standalone TUI (built with [Textual](https://textual.textualize.io/) +
the [Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk)). Same config, same notes,
same streak — the skill and the app share all state.

```bash
uv tool install -e ~/git/curiosity   # or: uv tool install .
curio
```

- 🎯 **Riddle from my questions** — a fresh seed from your `questions.md`
- 🌍 **Surprise me** — a commonly-unknown / poorly-understood fact, off-file
- 🔁 **Revisit** — deepen an old topic from a new angle
- 🃏 **Flashcards** — random cards built locally from your saved notes (no Claude call)
- 📚 **Browse** — read your whole curiosity universe in-terminal

Auth reuses your `claude` CLI login (subscription) — no API key. Game rounds run a real
interactive Claude session that reads your questions, plays turn-by-turn, then writes the
note, map entry, and progress update itself.

## Configure (optional)

By default everything lives in `~/curiosity/` (`questions.md` + `notes/`). To point it elsewhere —
e.g. an Obsidian vault — create `~/curiosity/config.json`:

```json
{
  "questions_file": "/path/to/your-questions.md",
  "notes_dir": "/path/to/notes-dir",
  "map_file": "MAP.md"
}
```

See [`config.example.json`](config.example.json) and [`examples/questions.example.md`](examples/questions.example.md).

## Design principles

- **Accuracy over story.** It flags uncertainty and won't fabricate facts, dates, or studies to
  make a cleaner narrative.
- **Perspective, not recall.** The payload is the zoom-out reframe, not a memory test.
- **You own the output.** Plain markdown notes + a JSON you can read. No lock-in, no cloud.

## License

MIT — see [LICENSE](LICENSE). Made with Claude Code. PRs / new question-bank examples welcome.
