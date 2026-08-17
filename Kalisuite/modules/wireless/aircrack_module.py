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


class AircrackWidget(QWidget):
    """
    UI wrapper for the airodump-ng tool (part of the aircrack‑ng suite).

    Fields:
        • Monitor interface (default "wlan0mon")
        • Channel (optional, e.g. "6")
        • Output file prefix (optional, adds --write <prefix>)
    Command:
        sudo airodump-ng <interface> [-c <channel>] [--write <prefix>]

    The command runs continuously; a "Stop" button is provided to terminate
    the process.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Verify airodump-ng is present; offer to install if not.
        if not offer_installation("airodump-ng"):
            raise RuntimeError("airodump-ng is required but not installed.")

        self._build_ui()
        self.runner = CommandRunner()
        self.runner.output_line.connect(self._append_output)
        self.runner.finished.connect(self._on_finished)

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # Prominent legal/ethical note
        note = QLabel(
            "Only scan/capture on networks you own or have explicit authorization to test."
        )
        note.setWordWrap(True)
        note.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(note)

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

        # ---- Output file prefix (optional) ----
        prefix_layout = QHBoxLayout()
        prefix_label = QLabel("Output file prefix (optional):")
        self.prefix_edit = QLineEdit()
        prefix_layout.addWidget(prefix_label)
        prefix_layout.addWidget(self.prefix_edit)
        layout.addLayout(prefix_layout)

        # ---- Control buttons ----
        btn_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Capture")
        self.start_button.clicked.connect(self._start_capture)
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self._stop_capture)
        self.stop_button.setEnabled(False)
        btn_layout.addWidget(self.start_button)
        btn_layout.addWidget(self.stop_button)
        layout.addLayout(btn_layout)

        # ---- Output console ----
        self.output_console = QTextEdit()
        self.output_console.setReadOnly(True)
        layout.addWidget(self.output_console)

    def _start_capture(self):
        interface = self.iface_edit.text().strip()
        if not interface:
            self._append_output("Error: Monitor interface is required.")
            return

        channel = self.channel_edit.text().strip()
        prefix = self.prefix_edit.text().strip()

        channel_opt = f"-c {shlex.quote(channel)}" if channel else ""
        write_opt = f"--write {shlex.quote(prefix)}" if prefix else ""

        template = TOOL_REGISTRY["aircrack"]["command_template"]
        raw_cmd = template.format(
            interface=shlex.quote(interface),
            channel_opt=channel_opt,
            write_opt=write_opt,
        )

        command_list = shlex.split(raw_cmd)

        # Reset UI state
        self.output_console.clear()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self._append_output(f"Executing: {' '.join(command_list)}")
        self.runner.run(command_list)

    def _stop_capture(self):
        """
        Terminates the running airodump-ng process.
        """
        self.runner.terminate()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def _append_output(self, text: str):
        self.output_console.append(text)

    def _on_finished(self):
        self._append_output("\n--- Capture stopped ---")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
