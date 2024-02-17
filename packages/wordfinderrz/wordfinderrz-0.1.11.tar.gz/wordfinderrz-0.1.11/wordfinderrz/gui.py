"""Graphical user interface for WordSearch."""

from __future__ import annotations

import tkinter as tk
from tkinter.filedialog import asksaveasfile

from wordfinderrz import __version__
from wordfinderrz.word_search import WordSearch


class WordFinderrz:
    """Graphical user interface for WordSearch."""

    def __init__(self) -> None:
        """Create WordFinderrz app object."""
        self.root = tk.Tk()
        self.root.title("wordfinderrz")
        self.root.geometry("800x600")
        self.word_search: WordSearch | None = None
        self._compose_header_pane()
        self._compose_body()

    @property
    def title(self) -> str:
        """Return title of word search."""
        return ttl if (ttl := self.ent_title.get()) != "" else "Untitled"

    def _compose_header_pane(self) -> None:
        self.frm_header = tk.Frame(self.root, bg="black")
        self.frm_header.pack(fill=tk.X)
        lbl_wordmark = tk.Label(
            self.frm_header,
            text="wordfinderrz",
            font="Courier 20",
            bg="black",
            fg="white",
        )
        lbl_wordmark.grid(column=0, row=0, sticky="nw", padx=20, pady=15)
        lbl_version = tk.Label(
            self.frm_header, text=f"v{__version__}", bg="black", fg="gray"
        )
        lbl_version.grid(column=1, row=0, sticky="e")

    def _compose_body(self) -> None:
        self.frm_body = tk.Frame(self.root, bg="red")
        self.frm_body.pack(expand=True, fill=tk.BOTH)
        self._compose_side_pane()
        self._compose_preview_pane()

    def _compose_side_pane(self) -> None:
        self.frm_side_pane = tk.Frame(self.frm_body, padx=15, pady=15)

        # Create title entry field.
        frm_title = tk.Frame(self.frm_side_pane, width=240)
        lbl_title = tk.Label(frm_title, text="Title:")
        self.ent_title = tk.Entry(frm_title)
        lbl_title.pack(side=tk.LEFT, fill=tk.Y)
        self.ent_title.pack(side=tk.LEFT)
        frm_title.pack(fill=tk.X)

        # Create bank text box.
        frm_bank = tk.Frame(self.frm_side_pane)
        lbl_bank = tk.Label(frm_bank, text="Word Bank", padx=10, pady=10)
        self.box_bank = tk.Text(frm_bank, width=32, height=30, pady=10)
        lbl_bank.pack()
        self.box_bank.pack(fill=tk.Y, expand=True)
        frm_bank.pack(fill=tk.BOTH)

        # Create buttons.
        frm_buttons = tk.Frame(self.frm_side_pane)
        self.btn_create = tk.Button(frm_buttons, text="Create")
        self.btn_create.pack(side=tk.RIGHT)
        self.btn_create.bind("<Button-1>", self.create_word_search)
        self.btn_save = tk.Button(frm_buttons, text="Save")
        self.btn_save.pack(side=tk.RIGHT)
        self.btn_save.bind("<Button-1>", self.save_word_search)
        frm_buttons.pack(fill=tk.X)

        self.frm_side_pane.pack(side=tk.LEFT, fill=tk.Y)

    def create_word_search(self, event: tk.Event[tk.Button]) -> None:
        """Create a word search."""
        self.word_search = WordSearch(
            bank=self.box_bank.get("0.0", tk.END).split(),
            title=ttl if (ttl := self.ent_title.get()) != "" else None,
        )
        self.lbl_preview["text"] = str(self.word_search)

    def save_word_search(self, event: tk.Event[tk.Button]) -> None:
        """Save a word search as an HTML file."""
        if self.word_search is None:
            return None
        file = asksaveasfile(initialfile=f"{self.title}.html", defaultextension=".html")
        if file is not None:
            with file:
                file.write(self.word_search.to_html())

    def _compose_preview_pane(self) -> None:
        self.frm_body.columnconfigure(1, weight=4)
        self.frm_preview_pane = tk.Frame(self.frm_body)
        self.lbl_preview = tk.Label(
            self.frm_preview_pane,
            font="Courier 18",
            text=f"{'[Preview Pane]': >28}",
            padx=25,
            pady=80,
        )
        self.lbl_preview.pack(anchor=tk.NW)
        self.frm_preview_pane.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

    def start(self) -> None:
        """Start app."""
        self.root.mainloop()

def main() -> None:
    """Create and start app."""
    app = WordFinderrz()
    app.start()

if __name__ == "__main__":
    main()
