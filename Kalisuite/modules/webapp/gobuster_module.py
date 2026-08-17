__author__ = "rpi5exploitr"

import os
import shlex
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
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


class GobusterWidget(QWidget):
    """
    UI wrapper for the gobuster tool.

    Fields:
        • Target URL (required)
        • Wordlist path (required, browse button, defaults to
          /usr/share/wordlists/dirb/common.txt if present)
        • Extensions (optional, comma‑separated, e.g. "php,html,txt")

    Command:
        gobuster dir -u <url> -w <wordlist> [-x <extensions>]
    """

    DEFAULT_WORDLIST = "/usr/share/wordlists/dirb/common.txt"

    def __init__(self, parent=None):
        super().__init__(parent)

        # Verify gobuster is present; offer to install if not.
        if not offer_installation("gobuster"):
            raise RuntimeError("gobuster is required but not installed.")

        self._build_ui()
        self.runner = CommandRunner()
        self.runner.output_line.connect(self._append_output)
        self.runner.finished.connect(self._on_finished)

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # ---- Target URL ----
        url_layout = QHBoxLayout()
        url_label = QLabel("Target URL:")
        self.url_edit = QLineEdit()
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_edit)
        layout.addLayout(url_layout)

        # ---- Wordlist ----
        wl_layout = QHBoxLayout()
        wl_label = QLabel("Wordlist:")
        self.wl_edit = QLineEdit()
        # Use default if file exists
        if os.path.isfile(self.DEFAULT_WORDLIST):
            self.wl_edit.setText(self.DEFAULT_WORDLIST)
        wl_browse = QPushButton("Browse")
        wl_browse.clicked.connect(self._browse_wordlist)
        wl_layout.addWidget(wl_label)
        wl_layout.addWidget(self.wl_edit)
        wl_layout.addWidget(wl_browse)
        layout.addLayout(wl_layout)

        # ---- Extensions (optional) ----
        ext_layout = QHBoxLayout()
        ext_label = QLabel("Extensions (comma‑separated):")
        self.ext_edit = QLineEdit()
        ext_layout.addWidget(ext_label)
        ext_layout.addWidget(self.ext_edit)
        layout.addLayout(ext_layout)

        # ---- Run button ----
        self.run_button = QPushButton("Run Scan")
        self.run_button.clicked.connect(self._run_scan)
        layout.addWidget(self.run_button, alignment=Qt.AlignmentFlag.AlignRight)

        # ---- Output console ----
        self.output_console = QTextEdit()
        self.output_console.setReadOnly(True)
        layout.addWidget(self.output_console)

    def _browse_wordlist(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select wordlist", "", "All Files (*)"
        )
        if filename:
            self.wl_edit.setText(filename)

    def _run_scan(self):
        url = self.url_edit.text().strip()
        wordlist = self.wl_edit.text().strip()
        extensions = self.ext_edit.text().strip()

        if not url:
            self._append_output("Error: Target URL is required.")
            return
        if not wordlist:
            self._append_output("Error: Wordlist file is required.")
            return
        if not os.path.isfile(wordlist):
            self._append_output("Error: Specified wordlist file does not exist.")
            return

        ext_flag = f"-x {extensions}" if extensions else ""

        template = TOOL_REGISTRY["gobuster"]["command_template"]
        raw_cmd = template.format(url=url, wordlist=wordlist, ext_flag=ext_flag)

        command_list = shlex.split(raw_cmd)

        # Reset UI
        self.output_console.clear()
        self.run_button.setEnabled(False)
        self._append_output(f"Executing: {' '.join(command_list)}")
        self.runner.run(command_list)

    def _append_output(self, text: str):
        self.output_console.append(text)

    def _on_finished(self):
        self._append_output("\n--- gobuster scan finished ---")
        self.run_button.setEnabled(True)
