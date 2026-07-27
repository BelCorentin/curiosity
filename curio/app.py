"""curio — the curiosity game as a terminal app."""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.containers import Center, Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import (
    Button,
    Footer,
    Input,
    Label,
    ListItem,
    ListView,
    LoadingIndicator,
    Markdown,
    MarkdownViewer,
    Static,
)

from .backend import Game
from .config import Config, load_config, load_progress
from .notes import Flashcard, Note, list_notes, shuffled_flashcards

BANNER = "🔭  c u r i o"


# --------------------------------------------------------------------------- home


class HomeScreen(Screen):
    BINDINGS = [("q", "app.quit", "Quit")]

    def compose(self) -> ComposeResult:
        cfg: Config = self.app.cfg  # type: ignore[attr-defined]
        yield Center(Label(BANNER, id="banner"))
        yield Center(Static("", id="stats"))
        with Center():
            with Vertical(id="menu"):
                yield Button("🎯  Riddle from my questions", id="mine", variant="primary")
                yield Button("🌍  Surprise me — a poorly understood fact", id="surprise", variant="success")
                yield Button("🔁  Revisit an old topic", id="revisit")
                yield Button("🃏  Flashcards", id="flash")
                yield Button("📚  Browse my notes", id="browse")
        yield Footer()

    def on_screen_resume(self) -> None:
        self.refresh_stats()

    def on_mount(self) -> None:
        self.refresh_stats()

    def refresh_stats(self) -> None:
        cfg: Config = self.app.cfg  # type: ignore[attr-defined]
        progress = load_progress(cfg)
        streak = progress.streak if progress.streak_alive else 0
        n_topics = len(progress.topics)
        last = progress.last_played or "never"
        self.query_one("#stats", Static).update(
            f"🔥 streak [b]{streak}[/b]   ·   🧠 [b]{n_topics}[/b] topics   ·   last played [b]{last}[/b]"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "mine" | "surprise" | "revisit":
                self.app.push_screen(PlayScreen(event.button.id))
            case "flash":
                self.app.push_screen(FlashScreen())
            case "browse":
                self.app.push_screen(BrowseScreen())


# --------------------------------------------------------------------------- play


class PlayScreen(Screen):
    BINDINGS = [("escape", "back", "End round")]

    def __init__(self, mode: str):
        super().__init__()
        self.mode = mode
        self.game: Game | None = None

    def compose(self) -> ComposeResult:
        yield Static(f"— {self.mode} —", id="play-title")
        yield VerticalScroll(id="chat")
        yield Static("", id="status")
        yield Input(placeholder="your answer… (esc to end round)", id="msg", disabled=True)
        yield Footer()

    def on_mount(self) -> None:
        self.run_worker(self._start(), exclusive=True)

    async def _start(self) -> None:
        self._set_status("connecting to Claude…")
        self.game = Game(self.app.cfg, self.mode)  # type: ignore[attr-defined]
        try:
            await self.game.connect()
        except Exception as exc:
            await self._bubble(f"**Could not start Claude session:** {exc}", "claude")
            self._set_status("")
            return
        await self._stream("Let's play — start today's round.")

    async def _stream(self, text: str) -> None:
        assert self.game is not None
        self._set_status("thinking…")
        self.query_one("#msg", Input).disabled = True
        async for event in self.game.send(text):
            if event.kind == "text":
                await self._bubble(event.payload, "claude")
                self._set_status("thinking…")
            elif event.kind == "tool":
                self._set_status(f"⚙ {event.payload}…")
            elif event.kind == "error":
                await self._bubble(f"**Error:** {event.payload}", "claude")
        self._set_status("")
        box = self.query_one("#msg", Input)
        box.disabled = False
        box.focus()

    async def _bubble(self, text: str, who: str) -> None:
        chat = self.query_one("#chat", VerticalScroll)
        bubble = Markdown(text, classes=f"bubble {who}")
        await chat.mount(bubble)
        chat.scroll_end(animate=False)

    def _set_status(self, text: str) -> None:
        self.query_one("#status", Static).update(text)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip()
        if not text:
            return
        event.input.value = ""
        await self._bubble(text, "user")
        self.run_worker(self._stream(text), exclusive=True)

    def action_back(self) -> None:
        self.app.pop_screen()

    async def on_unmount(self) -> None:
        if self.game is not None:
            await self.game.close()


# --------------------------------------------------------------------- flashcards


class FlashScreen(Screen):
    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
        ("space", "flip", "Flip"),
        ("n,right", "next_card", "Next"),
        ("p,left", "prev_card", "Previous"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.cards: list[Flashcard] = []
        self.index = 0
        self.flipped = False

    def compose(self) -> ComposeResult:
        yield Static("", id="flash-counter")
        with Center(id="flash-center"):
            with Vertical(id="card"):
                yield Static("", id="card-title")
                yield VerticalScroll(Markdown("", id="card-body"), id="card-scroll")
                yield Static("space — flip · n/p — next/prev", id="card-hint")
        yield Footer()

    def on_mount(self) -> None:
        self.cards = shuffled_flashcards(self.app.cfg)  # type: ignore[attr-defined]
        if not self.cards:
            self.query_one("#card-title", Static).update("No notes yet")
            self.query_one("#card-body", Markdown).update(
                "Play a few rounds first — flashcards are built from your saved notes."
            )
            return
        self.show_card()

    def show_card(self) -> None:
        card = self.cards[self.index]
        side = "answer" if self.flipped else "question"
        self.query_one("#flash-counter", Static).update(
            f"🃏 {self.index + 1}/{len(self.cards)} · {side}"
        )
        self.query_one("#card-title", Static).update(card.title)
        body = card.back if self.flipped else card.front
        self.query_one("#card-body", Markdown).update(body)
        self.query_one("#card", Vertical).set_class(self.flipped, "flipped")

    def action_flip(self) -> None:
        if not self.cards:
            return
        self.flipped = not self.flipped
        self.show_card()

    def action_next_card(self) -> None:
        if not self.cards:
            return
        self.index = (self.index + 1) % len(self.cards)
        self.flipped = False
        self.show_card()

    def action_prev_card(self) -> None:
        if not self.cards:
            return
        self.index = (self.index - 1) % len(self.cards)
        self.flipped = False
        self.show_card()


# ------------------------------------------------------------------------ browse


class BrowseScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Back")]

    def compose(self) -> ComposeResult:
        yield Static("📚  your curiosity universe", id="browse-title")
        yield ListView(id="note-list")
        yield Footer()

    def on_mount(self) -> None:
        self.notes = list_notes(self.app.cfg)  # type: ignore[attr-defined]
        lv = self.query_one("#note-list", ListView)
        for note in self.notes:
            lv.append(ListItem(Label(f"🧠  {note.title}")))
        if not self.notes:
            lv.append(ListItem(Label("no notes yet — play a round!")))
        lv.index = 0
        lv.focus()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if not self.notes:
            return
        index = self.query_one("#note-list", ListView).index or 0
        self.app.push_screen(NoteScreen(self.notes[index]))


class NoteScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Back")]

    def __init__(self, note: Note):
        super().__init__()
        self.note = note

    def compose(self) -> ComposeResult:
        yield MarkdownViewer(self.note.body, show_table_of_contents=False)
        yield Footer()


# --------------------------------------------------------------------------- app


class CurioApp(App):
    CSS_PATH = "app.tcss"
    TITLE = "curio"

    def __init__(self) -> None:
        super().__init__()
        self.cfg = load_config()

    def on_mount(self) -> None:
        self.push_screen(HomeScreen())


def main() -> None:
    CurioApp().run()


if __name__ == "__main__":
    main()
