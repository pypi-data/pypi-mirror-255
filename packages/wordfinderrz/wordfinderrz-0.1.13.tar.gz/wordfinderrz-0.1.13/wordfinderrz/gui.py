"""Graphical user interface for WordSearch."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import asksaveasfile
from tkinter.messagebox import showerror

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
        self.frm_header = tk.Frame(self.root, bg="black", padx=10, pady=12)
        lbl_wordmark = tk.Label(
            self.frm_header,
            text="wordfinderrz",
            font="Courier 20",
            bg="black",
            fg="white",
        )
        lbl_wordmark.pack(side=tk.LEFT)
        lbl_version = tk.Label(
            self.frm_header, text=f"v{__version__}", bg="black", fg="gray"
        )
        lbl_version.pack(side=tk.LEFT)
        self.frm_header.pack(fill=tk.X)

    def _compose_body(self) -> None:
        self.frm_body = tk.Frame(self.root, bg="red")
        self.frm_body.pack(expand=True, fill=tk.BOTH)
        self._compose_side_pane()
        self._compose_preview_pane()

    def _compose_side_pane(self) -> None:
        self.frm_side_pane = tk.Frame(self.frm_body, padx=10, pady=10)

        # Create title entry field.
        frm_title = tk.Frame(self.frm_side_pane, width=250)
        lbl_title = tk.Label(frm_title, text="Title:")
        self.ent_title = tk.Entry(frm_title)
        lbl_title.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        self.ent_title.pack(side=tk.LEFT)
        frm_title.pack(fill=tk.X)

        # Create buttons.
        frm_buttons = tk.Frame(self.frm_side_pane)
        self.btn_create = tk.Button(frm_buttons, text="Create")
        self.btn_create.pack(side=tk.RIGHT)
        self.btn_create.bind("<Button-1>", self.create_word_search)
        self.btn_save = tk.Button(frm_buttons, text="Save")
        self.btn_save.pack(side=tk.RIGHT)
        self.btn_save.bind("<Button-1>", self.save_word_search)
        frm_buttons.pack(fill=tk.X, side=tk.BOTTOM)

        # Create bank text box.
        frm_bank = tk.Frame(self.frm_side_pane)
        lbl_bank = tk.Label(frm_bank, text="Word Bank", padx=10, pady=10)
        self.box_bank = tk.Text(frm_bank, width=32, height=30, pady=10)
        lbl_bank.pack()
        self.box_bank.pack(fill=tk.Y, expand=True)
        frm_bank.pack(fill=tk.BOTH, side=tk.BOTTOM, expand=True)

        self.frm_side_pane.pack(side=tk.LEFT, fill=tk.Y)

    def create_word_search(self, event: tk.Event[tk.Button]) -> None:
        """Create a word search."""
        bank = self.box_bank.get("0.0", tk.END).split()
        if len(bank) == 0:
            showerror(title="Error", message="Must populate bank.")
            return None
        self.word_search = WordSearch(
            bank=self.box_bank.get("0.0", tk.END).split(),
            title=ttl if (ttl := self.ent_title.get()) != "" else None,
        )
        self.lbl_preview["text"] = str(self.word_search)

    def save_word_search(self, event: tk.Event[tk.Button]) -> None:
        """Save a word search as an HTML file."""
        if self.word_search is None:
            showerror(title="Error", message="Must create a word search before saving.")
            return None
        file = asksaveasfile(initialfile=f"{self.title}.html", defaultextension=".html")
        if file is not None:
            with file:
                file.write(self.word_search.to_html())

    def _compose_preview_pane(self) -> None:
        self.frm_preview_pane = tk.Frame(self.frm_body)
        self.frm_text_size = tk.Frame(self.frm_preview_pane, padx=10, pady=10)
        self.lbl_text_size = tk.Label(self.frm_text_size, text="Text Size")
        self.lbl_text_size.pack(side=tk.LEFT)
        self.btn_decrease_text_size = tk.Button(self.frm_text_size, text="-")
        self.btn_decrease_text_size.pack(side=tk.LEFT)
        self.btn_decrease_text_size.bind("<Button-1>", self.decrease_text_size)
        self.btn_increase_text_size = tk.Button(self.frm_text_size, text="+")
        self.btn_increase_text_size.pack(side=tk.LEFT)
        self.btn_increase_text_size.bind("<Button-1>", self.increase_text_size)
        self.frm_text_size.pack(anchor=tk.SE, side=tk.BOTTOM)
        self.lbl_preview = tk.Label(self.frm_preview_pane, font="Courier 18", padx=25)
        self.font_size = 18
        self.lbl_preview.pack(expand=True, fill=tk.BOTH)
        self.frm_preview_pane.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

    def decrease_text_size(self, event: tk.Event[tk.Button]) -> None:
        self.font_size = self.font_size - 2 if self.font_size > 4 else 2
        self.lbl_preview["font"] = f"Courier {self.font_size}"

    def increase_text_size(self, event: tk.Event[tk.Button]) -> None:
        self.font_size += 2
        self.lbl_preview["font"] = f"Courier {self.font_size}"

    def start(self) -> None:
        """Start app."""
        self.root.mainloop()


def main() -> None:
    """Create and start app."""
    app = WordFinderrz()
    app.start()


if __name__ == "__main__":
    main()
