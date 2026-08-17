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


class NmapWidget(QWidget):
    """
    UI wrapper for the nmap tool.
    Allows the user to specify a target IP/host and a scan type,
    then runs the constructed command and streams live output.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Verify nmap is present; offer to install if not.
        if not offer_installation("nmap"):
            raise RuntimeError("nmap is required but not installed.")

        self._build_ui()
        self.runner = CommandRunner()
        self.runner.output_line.connect(self._append_output)
        self.runner.finished.connect(self._on_finished)

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # ---- Target input ----
        target_layout = QHBoxLayout()
        target_label = QLabel("Target (IP/host):")
        self.target_edit = QLineEdit()
        target_layout.addWidget(target_label)
        target_layout.addWidget(self.target_edit)
        layout.addLayout(target_layout)

        # ---- Scan type selector ----
        scan_layout = QHBoxLayout()
        scan_label = QLabel("Scan type:")
        self.scan_combo = QComboBox()
        # Populate with the friendly names defined in the registry.
        scan_options = TOOL_REGISTRY["nmap"]["scan_types"]
        self._scan_map = {}  # friendly name -> actual flag string
        for friendly, flags in scan_options.items():
            self.scan_combo.addItem(friendly.title())
            self._scan_map[friendly.title()] = flags
        scan_layout.addWidget(scan_label)
        scan_layout.addWidget(self.scan_combo)
        layout.addLayout(scan_layout)

        # ---- Run button ----
        self.run_button = QPushButton("Run Scan")
        self.run_button.clicked.connect(self._run_scan)
        layout.addWidget(self.run_button, alignment=Qt.AlignmentFlag.AlignRight)

        # ---- Live output console ----
        self.output_console = QTextEdit()
        self.output_console.setReadOnly(True)
        layout.addWidget(self.output_console)

    def _run_scan(self):
        target = self.target_edit.text().strip()
        if not target:
            self._append_output("Error: Target field is empty.")
            return

        friendly_scan = self.scan_combo.currentText()
        scan_flags = self._scan_map.get(friendly_scan, "")

        template = TOOL_REGISTRY["nmap"]["command_template"]
        raw_cmd = template.format(scan_type=scan_flags, target=target)

        # Split into a list that subprocess can understand.
        command_list = shlex.split(raw_cmd)

        self.output_console.clear()
        self.run_button.setEnabled(False)
        self._append_output(f"Executing: {' '.join(command_list)}")
        self.runner.run(command_list)

    def _append_output(self, line: str):
        self.output_console.append(line)

    def _on_finished(self):
        self._append_output("\n--- Scan finished ---")
        self.run_button.setEnabled(True)
