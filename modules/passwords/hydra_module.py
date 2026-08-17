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


class HydraWidget(QWidget):
    """
    UI wrapper for the hydra password‑cracking tool.

    Fields:
        • Target (required)
        • Service (dropdown: ssh / ftp / http-post-form / telnet)
        • Username (required)
        • Password list file (required, browse button)
        • Threads (number, default 4)

    Command built from the registry:
        hydra -l <username> -P <wordlist> -t <threads> <target> <service>
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Verify hydra is present; offer to install if not.
        if not offer_installation("hydra"):
            raise RuntimeError("hydra is required but not installed.")

        self._build_ui()
        self.runner = CommandRunner()
        self.runner.output_line.connect(self._append_output)
        self.runner.finished.connect(self._on_finished)

    # -------------------------------------------------------------------------
    # UI construction
    # -------------------------------------------------------------------------
    def _build_ui(self):
        layout = QVBoxLayout(self)

        # ---- Target ----
        target_layout = QHBoxLayout()
        target_label = QLabel("Target:")
        self.target_edit = QLineEdit()
        target_layout.addWidget(target_label)
        target_layout.addWidget(self.target_edit)
        layout.addLayout(target_layout)

        # ---- Service selector ----
        service_layout = QHBoxLayout()
        service_label = QLabel("Service:")
        self.service_combo = QComboBox()
        self.service_combo.addItems(["ssh", "ftp", "http-post-form", "telnet"])
        service_layout.addWidget(service_label)
        service_layout.addWidget(self.service_combo)
        layout.addLayout(service_layout)

        # ---- Username ----
        user_layout = QHBoxLayout()
        user_label = QLabel("Username:")
        self.username_edit = QLineEdit()
        user_layout.addWidget(user_label)
        user_layout.addWidget(self.username_edit)
        layout.addLayout(user_layout)

        # ---- Password list (with Browse) ----
        pw_layout = QHBoxLayout()
        pw_label = QLabel("Password list:")
        self.pw_edit = QLineEdit()
        pw_browse = QPushButton("Browse")
        pw_browse.clicked.connect(self._browse_wordlist)
        pw_layout.addWidget(pw_label)
        pw_layout.addWidget(self.pw_edit)
        pw_layout.addWidget(pw_browse)
        layout.addLayout(pw_layout)

        # ---- Threads ----
        threads_layout = QHBoxLayout()
        threads_label = QLabel("Threads:")
        self.threads_edit = QLineEdit()
        self.threads_edit.setText("4")
        threads_layout.addWidget(threads_label)
        threads_layout.addWidget(self.threads_edit)
        layout.addLayout(threads_layout)

        # ---- Run button ----
        self.run_button = QPushButton("Run Attack")
        self.run_button.clicked.connect(self._run_attack)
        layout.addWidget(self.run_button, alignment=Qt.AlignmentFlag.AlignRight)

        # ---- Output console ----
        self.output_console = QTextEdit()
        self.output_console.setReadOnly(True)
        layout.addWidget(self.output_console)

    # -------------------------------------------------------------------------
    # Helper slots
    # -------------------------------------------------------------------------
    def _browse_wordlist(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select password list", "", "All Files (*)"
        )
        if filename:
            self.pw_edit.setText(filename)

    # -------------------------------------------------------------------------
    # Execution
    # -------------------------------------------------------------------------
    def _run_attack(self):
        target = self.target_edit.text().strip()
        service = self.service_combo.currentText().strip()
        username = self.username_edit.text().strip()
        wordlist = self.pw_edit.text().strip()
        threads = self.threads_edit.text().strip()

        # Basic validation
        if not target:
            self._append_output("Error: Target field is required.")
            return
        if not username:
            self._append_output("Error: Username field is required.")
            return
        if not wordlist:
            self._append_output("Error: Password list file is required.")
            return
        if not threads.isdigit() or int(threads) <= 0:
            self._append_output("Error: Threads must be a positive integer.")
            return

        template = TOOL_REGISTRY["hydra"]["command_template"]
        raw_cmd = template.format(
            username=username,
            wordlist=shlex.quote(wordlist),
            threads=threads,
            target=shlex.quote(target),
            service=service,
        )
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
        self._append_output("\n--- Hydra attack finished ---")
        self.run_button.setEnabled(True)
