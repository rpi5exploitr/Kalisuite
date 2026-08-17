import shutil
import subprocess
import inspect
from PyQt6.QtWidgets import QMessageBox, QApplication


def is_tool_available(tool_name: str) -> bool:
    """
    Returns True if the executable is found on the system PATH.
    """
    return shutil.which(tool_name) is not None


def offer_installation(tool_name: str, package_name: str = None):
    """
    If the tool is missing, asks the user whether to install it using apt.
    Returns True if installation succeeded or the tool was already present.

    Additionally checks that the calling module defines a matching __author__
    constant for attribution. If missing or mismatched, a warning is printed
    to the console (stdout). This does not block execution.
    """
    if is_tool_available(tool_name):
        _check_attribution()
        return True

    if package_name is None:
        package_name = tool_name

    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    reply = QMessageBox.question(
        None,
        "Missing Dependency",
        f"The tool '{tool_name}' is not installed. Install package '{package_name}' now?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
    )
    if reply != QMessageBox.StandardButton.Yes:
        _check_attribution()
        return False

    try:
        subprocess.run(
            ["sudo", "apt", "install", package_name, "-y"],
            check=True,
        )
        _check_attribution()
        return is_tool_available(tool_name)
    except subprocess.CalledProcessError:
        QMessageBox.critical(
            None,
            "Installation Failed",
            f"Failed to install '{package_name}'. Please install it manually.",
        )
        _check_attribution()
        return False


def _check_attribution():
    """
    Inspect the caller's global namespace for an __author__ constant.
    If it does not exist or does not match the expected value,
    emit a warning to stdout.
    """
    expected_author = "rpi5exploitr"
    # The caller of offer_installation is one level up the stack.
    caller_globals = inspect.stack()[2].frame.f_globals
    module_name = caller_globals.get("__name__", "<unknown>")
    author = caller_globals.get("__author__")
    if author != expected_author:
        print(
            f"Warning: Module '{module_name}' missing attribution or author mismatch. "
            f"Expected '__author__ = \"{expected_author}\"'."
        )
