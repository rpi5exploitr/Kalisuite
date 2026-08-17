"""
PixiewpcWidget – UI wrapper for the `pixiewps` (Pixie Dust) attack tool.

Fields:
    • Interface (text, default "wlan0mon")
    • BSSID / MAC address of the target AP (required)
    • ESSID (SSID) of the target AP (required)
    • Pin (optional, used for resume)

Command (simplified):
    pixiewps -i <interface> -b <bssid> -e <essid> [--pin <pin>]

The widget streams live output using the project's CommandRunner.
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QLabel,
)
from core.runner import CommandRunner

__author__ = "rpi5exploitr"


class PixiewpcWidget(QWidget):
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

        self.essid_edit = QLineEdit(self)
        form.addRow("ESSID (SSID):", self.essid_edit)

        self.pin_edit = QLineEdit(self)
        form.addRow("Pin (optional):", self.pin_edit)

        layout.addLayout(form)

        self.run_button = QPushButton("Start PixieDust Attack", self)
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
        essid = self.essid_edit.text().strip()
        pin = self.pin_edit.text().strip()

        if not interface or not bssid or not essid:
            self._append_output("Interface, BSSID, and ESSID are required.\n")
            return

        cmd = ["pixiewps", "-i", interface, "-b", bssid, "-e", essid]
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
        self._append_output(f"\nPixiewpc finished with exit code {exit_code}")
        self.status_label.setText("Finished")
