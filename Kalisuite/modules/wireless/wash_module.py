__author__ = "rpi5exploitr"

import shlex
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QHBoxLayout,
)
from PyQt6.QtCore import Qt

from core.runner import CommandRunner
from core.tool_registry import TOOL_REGISTRY
from core.installer import offer_installation


class WashWidget(QWidget):
    """
    UI wrapper for the wash tool (WPS scanner from the reaver suite).

    Fields:
        • Monitor interface (text, default "wlan0mon")
        • Channel (text, optional)

    Command:
        sudo wash -i <interface> [-c <channel>]

    Streams live output via CommandRunner, same pattern as other modules.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Verify wash is present; offer to install if not.
        if not offer_installation("wash"):
            raise RuntimeError("wash is required but not installed.")

        self._build_ui()
        self.runner = CommandRunner()
        self.runner.output_line.connect(self._append_output)
        self.runner.finished.connect(self._on_finished)

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # ---- Monitor interface ----
        iface_layout = QHBoxLayout()
        iface_label = QLabel("Monitor interface:")
        self.iface_edit = QLineEdit()
        self.iface_edit.setText("wlan0mon")
        iface_layout.addWidget(iface_label)
        iface_layout.addWidget(self.iface_edit)
        layout.addLayout(iface_layout)

        # ---- Channel (optional) ----
        chan_layout = QHBoxLayout()
        chan_label = QLabel("Channel (optional):")
        self.channel_edit = QLineEdit()
        self.channel_edit.setPlaceholderText("e.g. 6 (empty = all channels)")
        chan_layout.addWidget(chan_label)
        chan_layout.addWidget(self.channel_edit)
        layout.addLayout(chan_layout)

        # ---- Run button ----
        self.run_button = QPushButton("Start Scan")
        self.run_button.clicked.connect(self._run_scan)
        layout.addWidget(self.run_button, alignment=Qt.AlignmentFlag.AlignRight)

        # ---- Output console ----
        self.output_console = QTextEdit()
        self.output_console.setReadOnly(True)
        layout.addWidget(self.output_console)

    def _run_scan(self):
        interface = self.iface_edit.text().strip()
        if not interface:
            self._append_output("Error: Monitor interface is required.")
            return

        channel = self.channel_edit.text().strip()
        channel_opt = f"-c {shlex.quote(channel)}" if channel else ""

        template = TOOL_REGISTRY["wash"]["command_template"]
        raw_cmd = template.format(interface=shlex.quote(interface), channel_opt=channel_opt)

        command_list = shlex.split(raw_cmd)

        # Reset UI
        self.output_console.clear()
        self.run_button.setEnabled(False)
        self._append_output(f"Executing: {' '.join(command_list)}")
        self.runner.run(command_list)

    def _append_output(self, text: str):
        """Append a line to the scrolling console."""
        self.output_console.append(text)

    def _on_finished(self):
        self._append_output("\n--- Wash scan finished ---")
        self.run_button.setEnabled(True)
