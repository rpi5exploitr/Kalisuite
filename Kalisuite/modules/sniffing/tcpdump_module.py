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


class TcpdumpWidget(QWidget):
    """
    UI wrapper for the tcpdump packet capture tool.

    Fields:
        • Interface (text, default "eth0")
        • Filter expression (text, optional, placeholder "e.g. host 10.0.4.8 or port 443")
        • Packet count limit (number, default 100) – maps to -c flag
        • Save to file checkbox + filename field (adds -w <file> when checked,
          otherwise prints to console)

    Command:
        sudo tcpdump -i <interface> -c <count> [-w <file>] [<filter>]

    Uses CommandRunner to stream output live.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Verify tcpdump is present; offer to install if not.
        if not offer_installation("tcpdump"):
            raise RuntimeError("tcpdump is required but not installed.")

        self._build_ui()
        self.runner = CommandRunner()
        self.runner.output_line.connect(self._append_output)
        self.runner.finished.connect(self._on_finished)

    # -------------------------------------------------------------------------
    # UI construction
    # -------------------------------------------------------------------------
    def _build_ui(self):
        layout = QVBoxLayout(self)

        # ---- Interface ----
        iface_layout = QHBoxLayout()
        iface_label = QLabel("Interface:")
        self.iface_edit = QLineEdit()
        self.iface_edit.setText("eth0")
        iface_layout.addWidget(iface_label)
        iface_layout.addWidget(self.iface_edit)
        layout.addLayout(iface_layout)

        # ---- Packet count ----
        count_layout = QHBoxLayout()
        count_label = QLabel("Packet count limit:")
        self.count_edit = QLineEdit()
        self.count_edit.setText("100")
        count_layout.addWidget(count_label)
        count_layout.addWidget(self.count_edit)
        layout.addLayout(count_layout)

        # ---- Filter expression (optional) ----
        filter_layout = QHBoxLayout()
        filter_label = QLabel("Filter expression:")
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText(
            "e.g. host 10.0.4.8 or port 443"
        )
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_edit)
        layout.addLayout(filter_layout)

        # ---- Save to file checkbox + filename ----
        save_layout = QHBoxLayout()
        self.save_checkbox = QCheckBox("Save to file")
        self.save_checkbox.stateChanged.connect(self._toggle_save)
        self.file_edit = QLineEdit()
        self.file_edit.setPlaceholderText("output.pcap")
        self.file_edit.setEnabled(False)
        save_layout.addWidget(self.save_checkbox)
        save_layout.addWidget(self.file_edit)
        layout.addLayout(save_layout)

        # ---- Run button ----
        self.run_button = QPushButton("Start Capture")
        self.run_button.clicked.connect(self._run_capture)
        layout.addWidget(self.run_button, alignment=Qt.AlignmentFlag.AlignRight)

        # ---- Output console ----
        self.output_console = QTextEdit()
        self.output_console.setReadOnly(True)
        layout.addWidget(self.output_console)

    def _toggle_save(self, state):
        """Enable/disable filename field based on checkbox."""
        enabled = state == Qt.CheckState.Checked
        self.file_edit.setEnabled(enabled)
        if not enabled:
            self.file_edit.clear()

    # -------------------------------------------------------------------------
    # Execution
    # -------------------------------------------------------------------------
    def _run_capture(self):
        interface = self.iface_edit.text().strip()
        if not interface:
            self._append_output("Error: Interface field is empty.")
            return

        count = self.count_edit.text().strip()
        if not count.isdigit() or int(count) <= 0:
            self._append_output(
                "Error: Packet count must be a positive integer."
            )
            return

        filter_expr = self.filter_edit.text().strip()

        save_flag = ""
        if self.save_checkbox.isChecked():
            filename = self.file_edit.text().strip()
            if not filename:
                self._append_output(
                    "Error: Filename must be provided when 'Save to file' is checked."
                )
                return
            save_flag = f"-w {shlex.quote(filename)}"

        # Build command from registry template.
        template = TOOL_REGISTRY["tcpdump"]["command_template"]
        raw_cmd = template.format(
            interface=shlex.quote(interface),
            count=count,
            save_flag=save_flag,
            filter=filter_expr,
        )
        command_list = shlex.split(raw_cmd)

        # Reset UI
        self.output_console.clear()
        self.run_button.setEnabled(False)
        self._append_output(f"Executing: {' '.join(command_list)}")
        self.runner.run(command_list)

    def _append_output(self, text: str):
        """Append a line to the scrolling console."""
        self.output_console.append(text)

    # -------------------------------------------------------------------------
    # Post‑run handling
    # -------------------------------------------------------------------------
    def _on_finished(self):
        self._append_output("\n--- Capture finished ---")
        self.run_button.setEnabled(True)
