"""
ReaverWidget – UI wrapper for the `reaver` WPS brute‑force tool.

Fields:
    • Interface (text, default "wlan0mon")
    • BSSID / MAC address of the target AP (required)
    • Channel (number, optional)
    • Pin (optional, used for resume)

Command (simplified):
    reaver -i <interface> -b <bssid> [-c <channel>] [--pin <pin>] -vv

The widget streams live output using the project's CommandRunner.
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QPushButton,
    QTextEdit,
    QLabel,
)
from core.runner import CommandRunner

__author__ = "rpi5exploitr"


class ReaverWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self.runner = CommandRunner(self)

    def _build_ui(self):
        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.interface_edit = QLineEdit(self)
        self.interface_edit.setText("wlan0mon")
        form.addRow("Interface:", self.interface_edit)

        self.bssid_edit = QLineEdit(self)
        form.addRow("BSSID (MAC):", self.bssid_edit)

        self.channel_spin = QSpinBox(self)
        self.channel_spin.setRange(0, 165)
        self.channel_spin.setSpecialValueText("Auto")
        form.addRow("Channel:", self.channel_spin)

        self.pin_edit = QLineEdit(self)
        form.addRow("Pin (optional):", self.pin_edit)

        layout.addLayout(form)

        self.run_button = QPushButton("Start Reaver", self)
        self.run_button.clicked.connect(self._run_attack)
        layout.addWidget(self.run_button)

        self.output = QTextEdit(self)
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        self.status_label = QLabel("", self)
        layout.addWidget(self.status_label)

    def _run_attack(self):
        interface = self.interface_edit.text().strip()
        bssid = self.bssid_edit.text().strip()
        channel = self.channel_spin.value()
        pin = self.pin_edit.text().strip()

        if not interface or not bssid:
            self._append_output("Interface and BSSID are required.\n")
            return

        cmd = ["reaver", "-i", interface, "-b", bssid, "-vv"]
        if channel != 0:
            cmd += ["-c", str(channel)]
        if pin:
            cmd += ["--pin", pin]

        self.output.clear()
        self._append_output(f"Running: {' '.join(cmd)}\n")
        self.runner.run(cmd)

    def _append_output(self, text: str):
        self.output.append(text)

    # Signals from CommandRunner
    def handle_stdout(self, line: str):
        self._append_output(line.rstrip())

    def handle_stderr(self, line: str):
        self._append_output(line.rstrip())

    def handle_finished(self, exit_code: int):
        self._append_output(f"\nReaver finished with exit code {exit_code}")
        self.status_label.setText("Finished")
