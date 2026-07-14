---
name: curiosity
description: >-
  Daily curiosity game. Turns your own open life-questions into a fun daily riddle +
  mini-lesson + a "zoom out" that reframes the topic across history and makes you requestion
  things, then consolidates each bite into a wikilinked note so knowledge accretes. Use for
  "/curiosity", "curiosity quiz", "daily riddle", "teach me something". Interactive: play it
  turn-by-turn in the session, one exchange at a time — don't dump the whole thing.
---

# curiosity — daily riddle → lesson → zoom-out

Goal: **learn while having fun**, one small bite a day, and **consolidate** each bite into a
growing personal knowledge base (a "questions universe"). It's a GAME, not a lecture, and not a
test — play it live, one exchange at a time, and wait for the answer before revealing.

## Configuration (where files live)

Read `~/curiosity/config.json` if it exists:
```json
{
  "questions_file": "/abs/path/to/your-questions.md",
  "notes_dir": "/abs/path/to/notes-dir",
  "map_file": "MAP.md"
}
```
If it's absent, use defaults: `questions_file` = `~/curiosity/questions.md`,
`notes_dir` = `~/curiosity/notes/`, `map_file` = `MAP.md`.
**First run & no questions file** → create `~/curiosity/`, seed `questions.md` from the repo's
`examples/questions.example.md`, tell the user to fill it with their own curiosities, and stop.

State: `<notes_dir>/_progress.json` · Map/hub: `<notes_dir>/<map_file>` · one note per topic in `<notes_dir>`.

### `_progress.json` shape
```json
{
  "streak": 0,
  "last_played": "YYYY-MM-DD",
  "topics": [
    {"slug": "roman-collapse", "title": "Why Rome fell", "source_section": "Culture",
     "first_played": "YYYY-MM-DD", "plays": 1, "last_review": "YYYY-MM-DD", "note": "Why Rome fell.md"}
  ]
}
```

## Flow (each run)

1. **Load state.** Read config → `_progress.json` (init if absent) + the questions file. Get today's date.
   Update `streak` (increment if `last_played` was yesterday, reset to 1 on a gap, keep if same day).

2. **Pick the mode** (announce in one warm line, show the streak 🔥):
   - **New topic** (default): one unplayed seed. Prefer variety across the file's `#` sections; honor
     any hint the user gives ("something on history", "quick science one", "surprise me").
   - **Revisit** (~1 in 4 runs): re-open an old topic from a fresh angle to deepen it, pulling from its note.

3. **The riddle** (the fun hook — pick what fits): a guess-first riddle, a "true or false", a "which
   came first", a surprising stat to estimate, or a mini scenario. **ONE question, then stop and wait.**
   React to the guess honestly (right / close / off) — no pandering.

4. **The lesson** — after they guess, a **tight, accurate** explainer (~6–10 lines). Real facts only;
   where scholars disagree or it's uncertain, say so. Never invent studies, dates, or quotes to make a
   cleaner story. Cite the *kind* of evidence, not fake references.

5. **🔭 Zoom out** (the heart of it — replaces any quiz). Widen the lens: connect the topic to other
   eras, civilizations, or domains so it reframes their mental model. End on a **requestion** — an
   open, mind-opening question that makes them step back and doubt a tidy narrative (theirs or the
   culture's). This is the payload: perspective, not recall. NO testing them.

6. **Write the note** (the point — knowledge must persist). New topic → create `<Title>.md` in
   `notes_dir` (frontmatter below): the original question, the riddle, a crisp **What I learned**, the
   **🔭 Zoom out**, **Open threads** (what to dig next), and `[[wikilinks]]` to related topic notes so
   the universe connects. Revisit → append a dated bullet. Then update the map file (list the topic +
   one-line hook, and promote juicy open threads) and `_progress.json`.

7. **Close** — one line: streak, what got saved (as a `[[link]]`), and a teaser for tomorrow.

## Note frontmatter
```yaml
---
sticker: emoji//1f9e0
created: DD-MM-YYYY
type: personal-note
scope: curiosity
---
```
Then one `# H1` title, then the sections. Match the user's language (mirror the seed's language).

## Rules
- It's a GAME: one question at a time, wait, keep it light and genuinely curious.
- **No quiz.** The consolidation move is the **zoom-out reframe**, not a recall test.
- Accuracy over story. Flag uncertainty. Never fabricate facts to round out a narrative.
- One topic per run unless asked for more. Respect the streak.
- Everything explored MUST end up in a note — consolidation is the deliverable.
- Only write inside `notes_dir` + its `_progress.json`. Never edit the user's raw questions file.
