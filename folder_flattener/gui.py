"""GUI interface for folder flattener using Tkinter."""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import threading
from typing import List

from .core import flatten_copy


class FolderFlattenerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Folder Flattener")
        self.root.geometry("600x500")
        self.root.resizable(True, True)

        # Variables
        self.sources: List[Path] = []
        self.destination: Path = None
        self.separator = tk.StringVar(value="__")

        self._create_widgets()

    def _create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Sources section
        ttk.Label(main_frame, text="Source Files/Folders:").grid(
            row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 5)
        )

        # Sources listbox with scrollbar
        sources_frame = ttk.Frame(main_frame)
        sources_frame.grid(
            row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10)
        )
        sources_frame.columnconfigure(0, weight=1)
        sources_frame.rowconfigure(0, weight=1)

        self.sources_listbox = tk.Listbox(sources_frame, height=8)
        self.sources_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        sources_scrollbar = ttk.Scrollbar(
            sources_frame, orient=tk.VERTICAL, command=self.sources_listbox.yview
        )
        sources_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.sources_listbox.configure(yscrollcommand=sources_scrollbar.set)

        # Buttons for sources
        sources_btn_frame = ttk.Frame(main_frame)
        sources_btn_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

        ttk.Button(sources_btn_frame, text="Browse Files...", command=self._browse_files).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Button(sources_btn_frame, text="Browse Folders...", command=self._browse_folders).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Button(sources_btn_frame, text="Clear Sources", command=self._clear_sources).pack(
            side=tk.LEFT
        )

        # Destination section
        ttk.Label(main_frame, text="Destination Folder:").grid(
            row=3, column=0, sticky=tk.W, pady=(10, 5)
        )

        dest_frame = ttk.Frame(main_frame)
        dest_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        dest_frame.columnconfigure(0, weight=1)

        self.dest_var = tk.StringVar()
        self.dest_entry = ttk.Entry(dest_frame, textvariable=self.dest_var, state="readonly")
        self.dest_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))

        ttk.Button(dest_frame, text="Choose Destination...", command=self._choose_destination).grid(
            row=0, column=1
        )

        # Separator section
        sep_frame = ttk.Frame(main_frame)
        sep_frame.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

        ttk.Label(sep_frame, text="Path Separator:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Entry(sep_frame, textvariable=self.separator, width=10).pack(side=tk.LEFT)

        # Progress section
        self.progress_var = tk.StringVar(value="Ready")
        ttk.Label(main_frame, textvariable=self.progress_var).grid(
            row=6, column=0, columnspan=2, sticky=tk.W, pady=(10, 5)
        )

        self.progress_bar = ttk.Progressbar(main_frame, mode="indeterminate")
        self.progress_bar.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # Action buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=8, column=0, columnspan=2, pady=(10, 0))

        self.flatten_btn = ttk.Button(
            btn_frame, text="Flatten & Rename", command=self._start_flatten
        )
        self.flatten_btn.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(btn_frame, text="Exit", command=self.root.quit).pack(side=tk.LEFT)

        # Configure grid weights for resizing
        main_frame.rowconfigure(1, weight=1)

    def _browse_files(self):
        """Browse and add files to sources."""
        filetypes = (("All files", "*.*"),)
        files = filedialog.askopenfilenames(title="Select files to flatten", filetypes=filetypes)
        for file in files:
            path = Path(file)
            if path not in self.sources:
                self.sources.append(path)
                self.sources_listbox.insert(tk.END, str(path))

    def _browse_folders(self):
        """Browse and add folders to sources."""
        folder = filedialog.askdirectory(title="Select folder to flatten")
        if folder:
            path = Path(folder)
            if path not in self.sources:
                self.sources.append(path)
                self.sources_listbox.insert(tk.END, str(path))

    def _clear_sources(self):
        """Clear all sources."""
        self.sources.clear()
        self.sources_listbox.delete(0, tk.END)

    def _choose_destination(self):
        """Choose destination folder."""
        folder = filedialog.askdirectory(title="Choose destination folder")
        if folder:
            self.destination = Path(folder)
            self.dest_var.set(str(self.destination))

    def _start_flatten(self):
        """Start the flattening process in a background thread."""
        if not self.sources:
            messagebox.showerror("Error", "Please select at least one source file or folder.")
            return

        if not self.destination:
            messagebox.showerror("Error", "Please choose a destination folder.")
            return

        # Disable the button and start progress
        self.flatten_btn.configure(state="disabled")
        self.progress_bar.start(10)
        self.progress_var.set("Flattening files...")

        # Run in background thread
        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(self._flatten_files)

        # Monitor the thread
        def check_completion():
            if future.done():
                try:
                    result = future.result()
                    self._on_flatten_complete(True, result)
                except Exception as e:
                    self._on_flatten_complete(False, str(e))
            else:
                self.root.after(100, check_completion)

        self.root.after(100, check_completion)

    def _flatten_files(self):
        """Perform the actual flattening operation."""
        sep = self.separator.get() or "__"
        flatten_copy(self.sources, self.destination, sep)
        return f"Successfully flattened {len(self.sources)} source(s)"

    def _on_flatten_complete(self, success: bool, message: str):
        """Handle completion of flattening operation."""
        self.progress_bar.stop()
        self.flatten_btn.configure(state="normal")

        if success:
            self.progress_var.set("✓ " + message)
            messagebox.showinfo("Success", message)
        else:
            self.progress_var.set("✗ Error occurred")
            messagebox.showerror("Error", f"Flattening failed: {message}")


def main():
    """Launch the GUI application."""
    root = tk.Tk()
    app = FolderFlattenerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
