__author__ = "rpi5exploitr"

import shlex
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QComboBox,
    QPushButton,
    QTextEdit,
    QFileDialog,
    QVBoxLayout,
    QHBoxLayout,
)
from PyQt6.QtCore import Qt

from core.runner import CommandRunner
from core.tool_registry import TOOL_REGISTRY
from core.installer import offer_installation


class JohnWidget(QWidget):
    """
    UI wrapper for John the Ripper.

    Fields:
        • Hash file (required, browse button)
        • Format (dropdown: auto / md5crypt / sha512crypt / nt / raw-md5)
        • Wordlist (optional, browse button)

    Command built from the registry:
        john --format=<format> [--wordlist=<wordlist>] <hashfile>
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Verify john is present; offer to install if not.
        if not offer_installation("john"):
            raise RuntimeError("john is required but not installed.")

        self._build_ui()
        self.runner = CommandRunner()
        self.runner.output_line.connect(self._append_output)
        self.runner.finished.connect(self._on_finished)

    # -------------------------------------------------------------------------
    # UI construction
    # -------------------------------------------------------------------------
    def _build_ui(self):
        layout = QVBoxLayout(self)

        # ---- Hash file ----
        hash_layout = QHBoxLayout()
        hash_label = QLabel("Hash file:")
        self.hash_edit = QLineEdit()
        hash_browse = QPushButton("Browse")
        hash_browse.clicked.connect(self._browse_hash_file)
        hash_layout.addWidget(hash_label)
        hash_layout.addWidget(self.hash_edit)
        hash_layout.addWidget(hash_browse)
        layout.addLayout(hash_layout)

        # ---- Format selector ----
        format_layout = QHBoxLayout()
        format_label = QLabel("Format:")
        self.format_combo = QComboBox()
        self.format_combo.addItems(
            ["auto", "md5crypt", "sha512crypt", "nt", "raw-md5"]
        )
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_combo)
        layout.addLayout(format_layout)

        # ---- Wordlist (optional) ----
        wl_layout = QHBoxLayout()
        wl_label = QLabel("Wordlist (optional):")
        self.wl_edit = QLineEdit()
        wl_browse = QPushButton("Browse")
        wl_browse.clicked.connect(self._browse_wordlist)
        wl_layout.addWidget(wl_label)
        wl_layout.addWidget(self.wl_edit)
        wl_layout.addWidget(wl_browse)
        layout.addLayout(wl_layout)

        # ---- Run button ----
        self.run_button = QPushButton("Run John")
        self.run_button.clicked.connect(self._run_john)
        layout.addWidget(self.run_button, alignment=Qt.AlignmentFlag.AlignRight)

        # ---- Output console ----
        self.output_console = QTextEdit()
        self.output_console.setReadOnly(True)
        layout.addWidget(self.output_console)

    # -------------------------------------------------------------------------
    # Helper slots
    # -------------------------------------------------------------------------
    def _browse_hash_file(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select hash file", "", "All Files (*)"
        )
        if filename:
            self.hash_edit.setText(filename)

    def _browse_wordlist(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select wordlist (optional)", "", "All Files (*)"
        )
        if filename:
            self.wl_edit.setText(filename)

    # -------------------------------------------------------------------------
    # Execution
    # -------------------------------------------------------------------------
    def _run_john(self):
        hashfile = self.hash_edit.text().strip()
        fmt = self.format_combo.currentText().strip()
        wordlist = self.wl_edit.text().strip()

        if not hashfile:
            self._append_output("Error: Hash file is required.")
            return

        # Base command from registry
        template = TOOL_REGISTRY["john"]["command_template"]
        # The template does not include wordlist; we'll add it conditionally.
        raw_cmd = template.format(format=fmt, hashfile=shlex.quote(hashfile))

        if wordlist:
            raw_cmd += f" --wordlist={shlex.quote(wordlist)}"

        command_list = shlex.split(raw_cmd)

        # Reset UI
        self.output_console.clear()
        self.run_button.setEnabled(False)
        self._append_output(f"Executing: {' '.join(command_list)}")
        self.runner.run(command_list)

    # -------------------------------------------------------------------------
    # UI output handling
    # -------------------------------------------------------------------------
    def _append_output(self, text: str):
        self.output_console.append(text)

    def _on_finished(self):
        self._append_output("\n--- John finished ---")
        self.run_button.setEnabled(True)
