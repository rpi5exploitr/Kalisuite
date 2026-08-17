__author__ = "rpi5exploitr"

import re
import shlex
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QComboBox,
    QPushButton,
    QTextEdit,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QHBoxLayout,
)
from PyQt6.QtCore import Qt

from core.runner import CommandRunner
from core.tool_registry import TOOL_REGISTRY
from core.installer import offer_installation


class ArpScanWidget(QWidget):
    """
    UI wrapper for the arp‑scan tool.
    Allows the user to specify:
      • Network interface (default: eth0)
      • Scan mode:
          – Local network  (uses --localnet)
          – Custom range   (user provides CIDR/IP range)
    Executes the constructed command and streams live output.
    Parses each result line (IP, MAC, Vendor) and displays it in a table
    alongside the raw console output.
    """

    _MAC_REGEX = re.compile(
        r"^([0-9a-fA-F]{2}[:-]){5}([0-9a-fA-F]{2})$"
    )  # simple MAC validation

    def __init__(self, parent=None):
        super().__init__(parent)

        # Verify arp‑scan is present; offer to install if not.
        if not offer_installation("arp-scan"):
            raise RuntimeError("arp-scan is required but not installed.")

        self._build_ui()
        self.runner = CommandRunner()
        self.runner.output_line.connect(self._handle_output_line)
        self.runner.finished.connect(self._on_finished)

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # ---- Interface input ----
        iface_layout = QHBoxLayout()
        iface_label = QLabel("Interface:")
        self.iface_edit = QLineEdit()
        self.iface_edit.setText("eth0")
        iface_layout.addWidget(iface_label)
        iface_layout.addWidget(self.iface_edit)
        layout.addLayout(iface_layout)

        # ---- Scan mode selector ----
        mode_layout = QHBoxLayout()
        mode_label = QLabel("Scan mode:")
        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Local network")
        self.mode_combo.addItem("Custom range")
        self.mode_combo.currentTextChanged.connect(self._mode_changed)
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.mode_combo)
        layout.addLayout(mode_layout)

        # ---- Custom range input (initially disabled) ----
        range_layout = QHBoxLayout()
        range_label = QLabel("CIDR / IP range:")
        self.range_edit = QLineEdit()
        self.range_edit.setPlaceholderText("e.g., 192.168.1.0/24")
        self.range_edit.setEnabled(False)
        range_layout.addWidget(range_label)
        range_layout.addWidget(self.range_edit)
        layout.addLayout(range_layout)

        # ---- Table for parsed results ----
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(3)
        self.result_table.setHorizontalHeaderLabels(["IP", "MAC", "Vendor"])
        self.result_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.result_table)

        # ---- Run button ----
        self.run_button = QPushButton("Run Scan")
        self.run_button.clicked.connect(self._run_scan)
        layout.addWidget(self.run_button, alignment=Qt.AlignmentFlag.AlignRight)

        # ---- Raw output console ----
        self.output_console = QTextEdit()
        self.output_console.setReadOnly(True)
        layout.addWidget(self.output_console)

    def _mode_changed(self, mode_text: str):
        """
        Enable the CIDR input only when the user selects "Custom range".
        """
        if mode_text == "Custom range":
            self.range_edit.setEnabled(True)
        else:
            self.range_edit.setEnabled(False)
            self.range_edit.clear()

    def _run_scan(self):
        interface = self.iface_edit.text().strip()
        if not interface:
            self._append_raw("Error: Interface field is empty.")
            return

        mode = self.mode_combo.currentText()
        scan_modes = TOOL_REGISTRY["arpscan"]["scan_modes"]
        mode_flag = scan_modes.get(mode, "")

        if mode == "Custom range":
            custom_range = self.range_edit.text().strip()
            if not custom_range:
                self._append_raw("Error: Custom range is required for this mode.")
                return
            mode_flag = custom_range  # replace placeholder with the actual range

        # Build command using the template
        template = TOOL_REGISTRY["arpscan"]["command_template"]
        raw_cmd = template.format(interface=interface, mode_flag=mode_flag)

        command_list = shlex.split(raw_cmd)

        # Reset UI
        self.result_table.setRowCount(0)
        self.output_console.clear()
        self.run_button.setEnabled(False)
        self._append_raw(f"Executing: {' '.join(command_list)}")
        self.runner.run(command_list)

    def _append_raw(self, text: str):
        """Append raw text to the scrolling console."""
        self.output_console.append(text)

    def _handle_output_line(self, line: str):
        """
        Called for each line emitted by CommandRunner.
        Displays the raw line and, when possible, parses it into the table.
        """
        self._append_raw(line)

        # Simple heuristic: arp‑scan result lines are of the form:
        #   <IP>\t<MAC>\t<Vendor>
        parts = line.split("\t")
        if len(parts) >= 3:
            ip, mac, vendor = parts[0].strip(), parts[1].strip(), parts[2].strip()
            # Basic validation to avoid header/footer lines.
            if self._is_valid_ip(ip) and self._MAC_REGEX.match(mac):
                row = self.result_table.rowCount()
                self.result_table.insertRow(row)
                self.result_table.setItem(row, 0, QTableWidgetItem(ip))
                self.result_table.setItem(row, 1, QTableWidgetItem(mac))
                self.result_table.setItem(row, 2, QTableWidgetItem(vendor))

    def _is_valid_ip(self, ip: str) -> bool:
        """
        Very light IPv4 validation.
        """
        parts = ip.split(".")
        if len(parts) != 4:
            return False
        try:
            return all(0 <= int(p) <= 255 for p in parts)
        except ValueError:
            return False

    def _on_finished(self):
        self._append_raw("\n--- Scan finished ---")
        self.run_button.setEnabled(True)
