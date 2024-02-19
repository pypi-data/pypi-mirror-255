"""Graphical user interface for WordSearch."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from tkinter import ttk
from tkinter.filedialog import asksaveasfile
from tkinter.messagebox import showerror

from wordfinderrz.word_search import WordSearch


class WordfinderrzApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("wordfinderrz")
        self.geometry("800x600")
        self.word_search: WordSearch | None = None
        self.side_pane = SidePane(self, self.create_word_search, self.save_word_search)
        self.side_pane.mount()
        self.preview_pane = PreviewPane(self, self.decrease_text_size, self.increase_text_size)
        self.preview_pane.mount()

    def create_word_search(self, event: tk.Event[tk.Button]) -> None:
        """Create a word search."""
        bank = self.side_pane.box_bank.get("0.0", tk.END).split()
        if len(bank) == 0:
            showerror(title="Error", message="Must populate bank.")
            return None
        self.word_search = WordSearch(
            bank=self.side_pane.box_bank.get("0.0", tk.END).split(),
            title=ttl if (ttl := self.side_pane.ent_title.get()) != "" else None,
            _b_shift=self.side_pane.scale.get(),
        )
        self.preview_pane.lbl_preview["text"] = str(self.word_search)

    def save_word_search(self, event: tk.Event[tk.Button]) -> None:
        """Save a word search as an HTML file."""
        if self.word_search is None:
            showerror(title="Error", message="Must create a word search before saving.")
            return None
        title = ttl if (ttl := self.side_pane.ent_title.get()) != "" else "Untitled"
        file = asksaveasfile(initialfile=f"{title}.html", defaultextension=".html")
        if file is not None:
            with file:
                file.write(self.word_search.to_html())

    def decrease_text_size(self, event: tk.Event[tk.Button]) -> None:
        self.preview_pane.font_size = self.preview_pane.font_size - 2 if self.preview_pane.font_size > 4 else 2
        self.preview_pane.lbl_preview["font"] = f"Courier {self.preview_pane.font_size}"

    def increase_text_size(self, event: tk.Event[tk.Button]) -> None:
        self.preview_pane.font_size += 2
        self.preview_pane.lbl_preview["font"] = f"Courier {self.preview_pane.font_size}"


class PreviewPane(tk.Frame):
    def __init__(
        self,
        master: tk.Tk | tk.Widget,
        decrease_text_size: Callable[[tk.Event[tk.Button]], None],
        increase_text_size: Callable[[tk.Event[tk.Button]], None],
    ) -> None:
        self.decrease_text_size = decrease_text_size
        self.increase_text_size = increase_text_size
        super().__init__(master)
        self.frm_text_size = tk.Frame(self, padx=10, pady=10)
        self.lbl_text_size = tk.Label(self.frm_text_size, text="Text Size")
        self.lbl_text_size.pack(side=tk.LEFT)
        self.btn_decrease_text_size = tk.Button(self.frm_text_size, text="-")
        self.btn_decrease_text_size.pack(side=tk.LEFT)
        self.btn_decrease_text_size.bind("<Button-1>", self.decrease_text_size)
        self.btn_increase_text_size = tk.Button(self.frm_text_size, text="+")
        self.btn_increase_text_size.pack(side=tk.LEFT)
        self.btn_increase_text_size.bind("<Button-1>", self.increase_text_size)
        self.frm_text_size.pack(anchor=tk.SE, side=tk.BOTTOM)
        self.lbl_preview = tk.Label(self, font="Courier 18", padx=25)
        self.font_size = 18
        self.lbl_preview.pack(expand=True, fill=tk.BOTH)

    def mount(self) -> None:
        self.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)


class SidePane(tk.Frame):
    def __init__(
        self,
        master: tk.Widget | tk.Tk,
        create_word_search: Callable[[tk.Event[tk.Button]], None],
        save_word_search: Callable[[tk.Event[tk.Button]], None],
    ) -> None:
        super().__init__(master, padx=10, pady=10)
        self.create_word_search = create_word_search
        self.save_word_search = save_word_search
        self.mount_title_entry()
        self.mount_buttons()
        self.mount_scale()
        self.mount_bank_text_box()

    def mount(self) -> None:
        self.pack(side=tk.LEFT, fill=tk.Y)

    def mount_title_entry(self) -> None:
        frm_title = tk.Frame(self, width=250)
        lbl_title = tk.Label(frm_title, text="Title:")
        self.ent_title = tk.Entry(frm_title)
        lbl_title.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        self.ent_title.pack(side=tk.LEFT)
        frm_title.pack(fill=tk.X)

    def mount_scale(self) -> None:
        frm_scale = tk.Frame(self)
        ttk.Label(frm_scale, text="Output Size").pack(side=tk.LEFT)
        self.scale = ttk.Scale(frm_scale, from_=-3, to=3, value=0.5)
        self.scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        frm_scale.pack(side=tk.BOTTOM, fill=tk.X)

    def mount_buttons(self) -> None:
        frm_buttons = tk.Frame(self)
        self.btn_create = tk.Button(frm_buttons, text="Create")
        self.btn_create.pack(side=tk.RIGHT)
        self.btn_create.bind("<Button-1>", self.create_word_search)
        self.btn_save = tk.Button(frm_buttons, text="Save")
        self.btn_save.pack(side=tk.RIGHT)
        self.btn_save.bind("<Button-1>", self.save_word_search)
        frm_buttons.pack(fill=tk.X, side=tk.BOTTOM)

    def mount_bank_text_box(self) -> None:
        frm_bank = tk.Frame(self)
        lbl_bank = tk.Label(frm_bank, text="Word Bank", padx=10, pady=10)
        self.box_bank = tk.Text(frm_bank, width=32, height=30, pady=10)
        lbl_bank.pack()
        self.box_bank.pack(fill=tk.Y, expand=True)
        frm_bank.pack(fill=tk.BOTH, side=tk.BOTTOM, expand=True)


if __name__ == "__main__":
    root = WordfinderrzApp()
    root.mainloop()
