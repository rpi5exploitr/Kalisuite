__author__ = "rpi5exploitr"

import shlex
import re
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


class SiegeWidget(QWidget):
    """
    UI wrapper for the siege load‑testing tool.

    Fields:
        • Target URL (required, placeholder)
        • Concurrent users (number, default 25)
        • Duration (text, default "30s")
        • Delay (number, default 1)

    Builds command:
        siege -c <concurrent> -t <duration> -d <delay> <url>

    Streams live output via CommandRunner and, after the run finishes,
    extracts the summary block (Transactions, Availability, etc.) and
    displays it in a dedicated panel above the raw console.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Verify siege is present; offer to install if not.
        if not offer_installation("siege"):
            raise RuntimeError("siege is required but not installed.")

        self._build_ui()
        self.runner = CommandRunner()
        self.runner.output_line.connect(self._handle_output_line)
        self.runner.finished.connect(self._on_finished)

        # Keep all lines so we can parse the summary after finish.
        self._output_lines = []

    # -------------------------------------------------------------------------
    # UI construction
    # -------------------------------------------------------------------------
    def _build_ui(self):
        layout = QVBoxLayout(self)

        # ---- Target URL ----
        url_layout = QHBoxLayout()
        url_label = QLabel("Target URL:")
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("only test servers you own")
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_edit)
        layout.addLayout(url_layout)

        # ---- Concurrent users ----
        conc_layout = QHBoxLayout()
        conc_label = QLabel("Concurrent users:")
        self.concurrent_edit = QLineEdit()
        self.concurrent_edit.setText("25")
        conc_layout.addWidget(conc_label)
        conc_layout.addWidget(self.concurrent_edit)
        layout.addLayout(conc_layout)

        # ---- Duration ----
        dur_layout = QHBoxLayout()
        dur_label = QLabel("Duration:")
        self.duration_edit = QLineEdit()
        self.duration_edit.setText("30s")
        dur_layout.addWidget(dur_label)
        dur_layout.addWidget(self.duration_edit)
        layout.addLayout(dur_layout)

        # ---- Delay ----
        delay_layout = QHBoxLayout()
        delay_label = QLabel("Delay (seconds):")
        self.delay_edit = QLineEdit()
        self.delay_edit.setText("1")
        delay_layout.addWidget(delay_label)
        delay_layout.addWidget(self.delay_edit)
        layout.addLayout(delay_layout)

        # ---- Summary panel (will be filled after run) ----
        self.summary_panel = QTextEdit()
        self.summary_panel.setReadOnly(True)
        self.summary_panel.setPlaceholderText("Summary will appear here after the run.")
        layout.addWidget(self.summary_panel)

        # ---- Run button ----
        self.run_button = QPushButton("Run Load Test")
        self.run_button.clicked.connect(self._run_test)
        layout.addWidget(self.run_button, alignment=Qt.AlignmentFlag.AlignRight)

        # ---- Raw output console ----
        self.output_console = QTextEdit()
        self.output_console.setReadOnly(True)
        layout.addWidget(self.output_console)

    # -------------------------------------------------------------------------
    # Execution
    # -------------------------------------------------------------------------
    def _run_test(self):
        url = self.url_edit.text().strip()
        if not url:
            self._append_raw("Error: Target URL is required.")
            return

        concurrent = self.concurrent_edit.text().strip()
        duration = self.duration_edit.text().strip()
        delay = self.delay_edit.text().strip()

        # Basic validation (numeric where appropriate)
        if not concurrent.isdigit() or int(concurrent) <= 0:
            self._append_raw("Error: Concurrent users must be a positive integer.")
            return
        if not delay.isdigit() or int(delay) < 0:
            self._append_raw("Error: Delay must be a non‑negative integer.")
            return
        if not duration:
            self._append_raw("Error: Duration is required.")
            return

        template = TOOL_REGISTRY["siege"]["command_template"]
        raw_cmd = template.format(
            concurrent=concurrent,
            duration=duration,
            delay=delay,
            url=url,
        )
        command_list = shlex.split(raw_cmd)

        # Reset UI
        self._output_lines.clear()
        self.summary_panel.clear()
        self.output_console.clear()
        self.run_button.setEnabled(False)
        self._append_raw(f"Executing: {' '.join(command_list)}")
        self.runner.run(command_list)

    def _append_raw(self, text: str):
        """Append raw text to the scrolling console."""
        self.output_console.append(text)

    def _handle_output_line(self, line: str):
        """Collect each line for later parsing and display it live."""
        self._output_lines.append(line)
        self._append_raw(line)

    # -------------------------------------------------------------------------
    # Post‑run processing
    # -------------------------------------------------------------------------
    def _on_finished(self):
        """Parse the final siege summary block and show it in the summary panel."""
        self._append_raw("\n--- Load test finished ---")
        self.run_button.setEnabled(True)

        # Siege prints a block that starts with "Transactions:" and ends at an empty line.
        summary_lines = []
        capture = False
        for line in self._output_lines:
            if line.startswith("Transactions:"):
                capture = True
            if capture:
                summary_lines.append(line)
                # The block typically ends with a line that starts with "----------------"
                if re.match(r"^-{2,}$", line.strip()):
                    # Stop after the separator line.
                    break

        if summary_lines:
            # Clean up any leading/trailing empty lines.
            cleaned = "\n".join(l.rstrip() for l in summary_lines if l.strip())
            self.summary_panel.setPlainText(cleaned)
        else:
            self.summary_panel.setPlainText("No summary block detected.")
