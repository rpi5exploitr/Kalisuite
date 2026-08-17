__author__ = "rpi5exploitr"

import shlex
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QComboBox,
    QCheckBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QHBoxLayout,
)
from PyQt6.QtCore import Qt

from core.runner import CommandRunner
from core.tool_registry import TOOL_REGISTRY
from core.installer import offer_installation


class SqlmapWidget(QWidget):
    """
    UI wrapper for the sqlmap tool.

    Fields:
        • Target URL (required, e.g. "http://example.com/page.php?id=1")
        • Risk level (dropdown 1‑3, default 1)
        • Level (dropdown 1‑5, default 1)
        • Batch mode checkbox (adds --batch, default checked)

    Command:
        sqlmap -u <url> --risk=<risk> --level=<level> [--batch]
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Verify sqlmap is present; offer to install if not.
        if not offer_installation("sqlmap"):
            raise RuntimeError("sqlmap is required but not installed.")

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
        self.url_edit.setPlaceholderText("e.g. http://example.com/page.php?id=1")
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_edit)
        layout.addLayout(url_layout)

        # ---- Risk level ----
        risk_layout = QHBoxLayout()
        risk_label = QLabel("Risk level:")
        self.risk_combo = QComboBox()
        self.risk_combo.addItems(["1", "2", "3"])
        self.risk_combo.setCurrentIndex(0)
        risk_layout.addWidget(risk_label)
        risk_layout.addWidget(self.risk_combo)
        layout.addLayout(risk_layout)

        # ---- Level ----
        level_layout = QHBoxLayout()
        level_label = QLabel("Level:")
        self.level_combo = QComboBox()
        self.level_combo.addItems(["1", "2", "3", "4", "5"])
        self.level_combo.setCurrentIndex(0)
        level_layout.addWidget(level_label)
        level_layout.addWidget(self.level_combo)
        layout.addLayout(level_layout)

        # ---- Batch mode checkbox ----
        batch_layout = QHBoxLayout()
        self.batch_checkbox = QCheckBox("Batch mode (--batch)")
        self.batch_checkbox.setChecked(True)
        batch_layout.addWidget(self.batch_checkbox)
        layout.addLayout(batch_layout)

        # ---- Run button ----
        self.run_button = QPushButton("Run Scan")
        self.run_button.clicked.connect(self._run_scan)
        layout.addWidget(self.run_button, alignment=Qt.AlignmentFlag.AlignRight)

        # ---- Output console ----
        self.output_console = QTextEdit()
        self.output_console.setReadOnly(True)
        layout.addWidget(self.output_console)

    def _run_scan(self):
        url = self.url_edit.text().strip()
        if not url:
            self._append_output("Error: Target URL is required.")
            return

        risk = self.risk_combo.currentText().strip()
        level = self.level_combo.currentText().strip()
        batch_flag = "--batch" if self.batch_checkbox.isChecked() else ""

        template = TOOL_REGISTRY["sqlmap"]["command_template"]
        raw_cmd = template.format(url=url, risk=risk, level=level, batch_flag=batch_flag)

        command_list = shlex.split(raw_cmd)

        # Reset UI
        self.output_console.clear()
        self.run_button.setEnabled(False)
        self._append_output(f"Executing: {' '.join(command_list)}")
        self.runner.run(command_list)

    def _append_output(self, text: str):
        self.output_console.append(text)

    def _on_finished(self):
        self._append_output("\n--- sqlmap scan finished ---")
        self.run_button.setEnabled(True)
