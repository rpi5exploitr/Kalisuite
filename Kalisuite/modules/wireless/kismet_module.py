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


class KismetWidget(QWidget):
    """
    UI wrapper for the kismet tool (passive wireless detection/monitoring).

    Fields:
        • Monitor interface (text, default "wlan0mon")

    Command:
        kismet -c <interface>

    After starting, a label informs the user that the Kismet web UI is
    available at http://localhost:2501.

    Includes a Stop button that terminates the process via CommandRunner.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Verify kismet is present; offer to install if not.
        if not offer_installation("kismet"):
            raise RuntimeError("kismet is required but not installed.")

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

        # ---- Control buttons ----
        btn_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Kismet")
        self.start_button.clicked.connect(self._start_kismet)
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self._stop_kismet)
        self.stop_button.setEnabled(False)
        btn_layout.addWidget(self.start_button)
        btn_layout.addWidget(self.stop_button)
        layout.addLayout(btn_layout)

        # ---- Info label (hidden until started) ----
        self.info_label = QLabel(
            'Kismet web UI available at <a href="http://localhost:2501">http://localhost:2501</a>'
        )
        self.info_label.setOpenExternalLinks(True)
        self.info_label.setVisible(False)
        layout.addWidget(self.info_label)

        # ---- Output console ----
        self.output_console = QTextEdit()
        self.output_console.setReadOnly(True)
        layout.addWidget(self.output_console)

    def _start_kismet(self):
        interface = self.iface_edit.text().strip()
        if not interface:
            self._append_output("Error: Monitor interface is required.")
            return

        template = TOOL_REGISTRY["kismet"]["command_template"]
        raw_cmd = template.format(interface=shlex.quote(interface))

        command_list = shlex.split(raw_cmd)

        # Reset UI
        self.output_console.clear()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.info_label.setVisible(True)
        self._append_output(f"Executing: {' '.join(command_list)}")
        self.runner.run(command_list)

    def _stop_kismet(self):
        """Terminate the running kismet process."""
        self.runner.terminate()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.info_label.setVisible(False)

    def _append_output(self, text: str):
        """Append a line to the scrolling console."""
        self.output_console.append(text)

    def _on_finished(self):
        self._append_output("\n--- Kismet stopped ---")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.info_label.setVisible(False)
