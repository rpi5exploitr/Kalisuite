import sys
import subprocess
from collections import defaultdict
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QListWidget,
    QListWidgetItem,
    QStackedWidget,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QMessageBox,
)
from PyQt6.QtCore import Qt

from core.tool_registry import TOOL_REGISTRY
from modules.recon.nmap_module import NmapWidget
from modules.recon.arpscan_module import ArpScanWidget
from modules.recon.theharvester_module import TheHarvesterWidget
from modules.recon.nikto_module import NiktoWidget
from modules.exploitation.metasploit_module import MetasploitWidget
from modules.loadtest.siege_module import SiegeWidget
from modules.passwords.hydra_module import HydraWidget
from modules.passwords.john_module import JohnWidget
from modules.webapp.sqlmap_module import SqlmapWidget
from modules.webapp.gobuster_module import GobusterWidget
from modules.sniffing.tcpdump_module import TcpdumpWidget
from modules.wireless.aircrack_module import AircrackWidget
from modules.wireless.wash_module import WashWidget
from modules.wireless.kismet_module import KismetWidget
# Wireless tools
from modules.wireless.reaver_module import ReaverWidget
from modules.wireless.bully_module import BullyWidget
from modules.wireless.pixiewpc_module import PixiewpcWidget
# Bluetooth tool
from modules.bluetooth.spooftooph_module import SpoofToophWidget


class MainWindow(QMainWindow):
    """
    Main application window.
    Left sidebar lists tool categories / tools.
    Central panel shows the selected tool's UI.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("KaliSuite — by rpi5exploitr")
        self.resize(1000, 600)

        central = QWidget()
        self.setCentralWidget(central)

        # Main vertical layout: top area (sidebar + stack) and footer
        main_layout = QVBoxLayout(central)

        # Top horizontal layout containing the sidebar and the stacked widget
        top_layout = QHBoxLayout()
        main_layout.addLayout(top_layout)

        # Sidebar list
        self.sidebar = QListWidget()
        self.sidebar.setMaximumWidth(250)
        top_layout.addWidget(self.sidebar)

        # Stacked widget for tool UIs
        self.stack = QStackedWidget()
        top_layout.addWidget(self.stack)

        # Populate registry data
        self._tool_pages = {}
        self._populate_sidebar()

        # Connect selection change
        self.sidebar.currentItemChanged.connect(self._switch_tool)

        # Select first item by default
        if self.sidebar.count() > 0:
            self.sidebar.setCurrentRow(0)

        # Add a button that builds the .deb package
        self.build_deb_button = QPushButton("Build .deb Package")
        self.build_deb_button.clicked.connect(self._build_deb_package)
        # Place the button just above the footer
        main_layout.addWidget(self.build_deb_button)

        # Footer bar with attribution
        footer = QLabel("KaliSuite — made by rpi5exploitr")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("font-size: 10px; color: gray;")
        main_layout.addWidget(footer)

    def _populate_sidebar(self):
        """
        Build the list widget with categories as section headers
        and tools as child items.
        """
        # Group tools by category
        categories = defaultdict(list)
        for tool_key, meta in TOOL_REGISTRY.items():
            categories[meta["category"]].append((tool_key, meta["name"]))

        for cat, tools in sorted(categories.items()):
            # Add a non‑selectable category header
            cat_item = QListWidgetItem(cat.title())
            cat_item.setFlags(cat_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            cat_item.setBackground(Qt.GlobalColor.lightGray)
            self.sidebar.addItem(cat_item)

            for tool_key, tool_name in sorted(tools):
                tool_item = QListWidgetItem(f"  {tool_name}")
                tool_item.setData(Qt.ItemDataRole.UserRole, tool_key)
                self.sidebar.addItem(tool_item)

                # Instantiate the UI for the tool lazily
                if tool_key == "nmap":
                    widget = NmapWidget()
                elif tool_key == "arpscan":
                    widget = ArpScanWidget()
                elif tool_key == "theharvester":
                    widget = TheHarvesterWidget()
                elif tool_key == "nikto":
                    widget = NiktoWidget()
                elif tool_key == "metasploit":
                    widget = MetasploitWidget()
                elif tool_key == "siege":
                    widget = SiegeWidget()
                elif tool_key == "hydra":
                    widget = HydraWidget()
                elif tool_key == "john":
                    widget = JohnWidget()
                elif tool_key == "sqlmap":
                    widget = SqlmapWidget()
                elif tool_key == "gobuster":
                    widget = GobusterWidget()
                elif tool_key == "tcpdump":
                    widget = TcpdumpWidget()
                elif tool_key == "aircrack":
                    widget = AircrackWidget()
                elif tool_key == "wash":
                    widget = WashWidget()
                elif tool_key == "kismet":
                    widget = KismetWidget()
                elif tool_key == "reaver":
                    widget = ReaverWidget()
                elif tool_key == "bully":
                    widget = BullyWidget()
                elif tool_key == "pixiewps":
                    widget = PixiewpcWidget()
                elif tool_key == "spooftooph":
                    widget = SpoofToophWidget()
                else:
                    widget = QLabel(f"UI for '{tool_name}' not implemented yet.")
                self.stack.addWidget(widget)
                self._tool_pages[tool_key] = widget

    def _switch_tool(self, current: QListWidgetItem, previous: QListWidgetItem):
        """
        Show the widget associated with the selected tool.
        """
        if current is None:
            return
        tool_key = current.data(Qt.ItemDataRole.UserRole)
        if not tool_key:
            # Clicked on a category header; ignore.
            return
        widget = self._tool_pages.get(tool_key)
        if widget:
            self.stack.setCurrentWidget(widget)

    def _build_deb_package(self):
        """
        Run the create_deb_package.py script to build a .deb package.
        Output is shown to the user via a message box.
        """
        # Resolve the path to the packaging script (project root)
        script_path = Path(__file__).resolve().parent.parent / "create_deb_package.py"
        if not script_path.is_file():
            QMessageBox.critical(
                self,
                "Error",
                f"Packaging script not found:\n{script_path}",
            )
            return

        try:
            # Run the script; let it print its own progress.
            subprocess.check_call([sys.executable, str(script_path)])
            QMessageBox.information(
                self,
                "Success",
                "The .deb package was built successfully.\n"
                "Check the current directory for the generated .deb file.",
            )
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(
                self,
                "Packaging Failed",
                f"An error occurred while building the package:\n{e}",
            )


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
