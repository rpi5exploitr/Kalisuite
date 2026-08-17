__author__ = "rpi5exploitr"

import shlex
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QComboBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QHBoxLayout,
)
from PyQt6.QtCore import Qt

from core.runner import CommandRunner
from core.tool_registry import TOOL_REGISTRY
from core.installer import offer_installation


class TheHarvesterWidget(QWidget):
    """
    UI wrapper for theHarvester reconnaissance tool.

    Fields:
        • Domain (required)
        • Source (dropdown: all / google / bing / duckduckgo)
        • Limit (number, default 500)

    Command built from registry:
        theHarvester -d <domain> -b <source> -l <limit>
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Verify theHarvester is present; offer to install if not.
        if not offer_installation("theHarvester"):
            raise RuntimeError("theHarvester is required but not installed.")

        self._build_ui()
        self.runner = CommandRunner()
        self.runner.output_line.connect(self._append_output)
        self.runner.finished.connect(self._on_finished)

    # -------------------------------------------------------------------------
    # UI construction
    # -------------------------------------------------------------------------
    def _build_ui(self):
        layout = QVBoxLayout(self)

        # ---- Domain input ----
        domain_layout = QHBoxLayout()
        domain_label = QLabel("Domain:")
        self.domain_edit = QLineEdit()
        domain_layout.addWidget(domain_label)
        domain_layout.addWidget(self.domain_edit)
        layout.addLayout(domain_layout)

        # ---- Source selector ----
        source_layout = QHBoxLayout()
        source_label = QLabel("Source:")
        self.source_combo = QComboBox()
        # The source values correspond to the ones accepted by theHarvester.
        self.source_combo.addItem("all")
        self.source_combo.addItem("google")
        self.source_combo.addItem("bing")
        self.source_combo.addItem("duckduckgo")
        source_layout.addWidget(source_label)
        source_layout.addWidget(self.source_combo)
        layout.addLayout(source_layout)

        # ---- Limit input ----
        limit_layout = QHBoxLayout()
        limit_label = QLabel("Limit:")
        self.limit_edit = QLineEdit()
        self.limit_edit.setText("500")
        limit_layout.addWidget(limit_label)
        limit_layout.addWidget(self.limit_edit)
        layout.addLayout(limit_layout)

        # ---- Run button ----
        self.run_button = QPushButton("Run Harvest")
        self.run_button.clicked.connect(self._run_harvest)
        layout.addWidget(self.run_button, alignment=Qt.AlignmentFlag.AlignRight)

        # ---- Output console ----
        self.output_console = QTextEdit()
        self.output_console.setReadOnly(True)
        layout.addWidget(self.output_console)

    # -------------------------------------------------------------------------
    # Execution
    # -------------------------------------------------------------------------
    def _run_harvest(self):
        domain = self.domain_edit.text().strip()
        if not domain:
            self._append_output("Error: Domain field is required.")
            return

        source = self.source_combo.currentText().strip()
        limit = self.limit_edit.text().strip()

        if not limit.isdigit() or int(limit) <= 0:
            self._append_output("Error: Limit must be a positive integer.")
            return

        template = TOOL_REGISTRY["theharvester"]["command_template"]
        raw_cmd = template.format(domain=domain, source=source, limit=limit)
        command_list = shlex.split(raw_cmd)

        # Reset UI
        self.output_console.clear()
        self.run_button.setEnabled(False)
        self._append_output(f"Executing: {' '.join(command_list)}")
        self.runner.run(command_list)

    def _append_output(self, line: str):
        """Append a line to the scrolling console."""
        self.output_console.append(line)

    def _on_finished(self):
        self._append_output("\n--- Harvest finished ---")
        self.run_button.setEnabled(True)
