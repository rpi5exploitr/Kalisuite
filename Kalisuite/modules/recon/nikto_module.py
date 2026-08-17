__author__ = "rpi5exploitr"

import shlex
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
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


class NiktoWidget(QWidget):
    """
    UI wrapper for the nikto web server scanner.

    Fields:
        • Target URL (required)
        • Port (number, default 80)
        • SSL checkbox (adds -ssl flag when checked)

    Command built from registry:
        nikto -h <target> -p <port> [ -ssl ]
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Verify nikto is present; offer to install if not.
        if not offer_installation("nikto"):
            raise RuntimeError("nikto is required but not installed.")

        self._build_ui()
        self.runner = CommandRunner()
        self.runner.output_line.connect(self._append_output)
        self.runner.finished.connect(self._on_finished)

    # -------------------------------------------------------------------------
    # UI construction
    # -------------------------------------------------------------------------
    def _build_ui(self):
        layout = QVBoxLayout(self)

        # ---- Target URL ----
        target_layout = QHBoxLayout()
        target_label = QLabel("Target URL:")
        self.target_edit = QLineEdit()
        target_layout.addWidget(target_label)
        target_layout.addWidget(self.target_edit)
        layout.addLayout(target_layout)

        # ---- Port ----
        port_layout = QHBoxLayout()
        port_label = QLabel("Port:")
        self.port_edit = QLineEdit()
        self.port_edit.setText("80")
        port_layout.addWidget(port_label)
        port_layout.addWidget(self.port_edit)
        layout.addLayout(port_layout)

        # ---- SSL checkbox ----
        ssl_layout = QHBoxLayout()
        self.ssl_checkbox = QCheckBox("Use SSL (-ssl)")
        ssl_layout.addWidget(self.ssl_checkbox)
        layout.addLayout(ssl_layout)

        # ---- Run button ----
        self.run_button = QPushButton("Run Scan")
        self.run_button.clicked.connect(self._run_scan)
        layout.addWidget(self.run_button, alignment=Qt.AlignmentFlag.AlignRight)

        # ---- Output console ----
        self.output_console = QTextEdit()
        self.output_console.setReadOnly(True)
        layout.addWidget(self.output_console)

    # -------------------------------------------------------------------------
    # Execution
    # -------------------------------------------------------------------------
    def _run_scan(self):
        target = self.target_edit.text().strip()
        if not target:
            self._append_output("Error: Target URL is required.")
            return

        port = self.port_edit.text().strip()
        if not port.isdigit() or int(port) <= 0:
            self._append_output("Error: Port must be a positive integer.")
            return

        ssl_flag = "-ssl" if self.ssl_checkbox.isChecked() else ""

        template = TOOL_REGISTRY["nikto"]["command_template"]
        raw_cmd = template.format(target=target, port=port, ssl_flag=ssl_flag)

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
        self._append_output("\n--- Scan finished ---")
        self.run_button.setEnabled(True)
