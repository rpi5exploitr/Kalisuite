"""
SpooftoophWidget – UI wrapper for the `spooftooph` Bluetooth spoofing tool.

Fields:
    • Bluetooth adapter (text, default "hci0")
    • Target MAC address (required)

Command (simplified):
    spooftooph -i <adapter> -t <target>

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


class SpoofToophWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self.runner = CommandRunner(self)

    def _build_ui(self):
        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.adapter_edit = QLineEdit(self)
        self.adapter_edit.setText("hci0")
        form.addRow("Adapter:", self.adapter_edit)

        self.target_edit = QLineEdit(self)
        form.addRow("Target MAC:", self.target_edit)

        layout.addLayout(form)

        self.run_button = QPushButton("Start Spooftooph", self)
        self.run_button.clicked.connect(self._run_attack)
        layout.addWidget(self.run_button)

        self.output = QTextEdit(self)
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        self.status_label = QLabel("", self)
        layout.addWidget(self.status_label)

    def _run_attack(self):
        adapter = self.adapter_edit.text().strip()
        target = self.target_edit.text().strip()

        if not adapter or not target:
            self._append_output("Both adapter and target MAC are required.\n")
            return

        cmd = ["spooftooph", "-i", adapter, "-t", target]

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
        self._append_output(f"\nSpooftooph finished with exit code {exit_code}")
        self.status_label.setText("Finished")
