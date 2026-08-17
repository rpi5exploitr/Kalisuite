"""
Entry point for the KaliSuite application.

This script ensures all Python dependencies listed in `requirements.txt`
are installed before launching the graphical user interface.

On Kali Linux the system Python environment is *externally managed*,
so a plain `pip install` will fail. The script now detects this
situation, prints a helpful message, and continues without aborting.
"""

import sys
import subprocess
import pathlib

def _ensure_dependencies() -> None:
    """Install missing Python dependencies.

    - Tries to install packages from ``requirements.txt`` using ``pip``.
    - If the installation fails because the environment is externally
      managed (PEP 668), a friendly instruction is printed suggesting
      the use of ``pipx`` or a virtual environment.
    - The function never raises an exception; it simply returns, allowing
      the GUI to start even when the dependencies are already satisfied
      or need to be installed manually.
    """
    req_path = pathlib.Path(__file__).with_name("requirements.txt")
    if not req_path.is_file():
        return  # No requirements file; nothing to install.

    # Run pip with captured output so we can analyse errors.
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", str(req_path)],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        # Successfully installed all requirements.
        return

    # Check for the “externally‑managed‑environment” message.
    if "externally-managed-environment" in result.stderr:
        print(
            "⚠️  Detected an externally managed Python environment.\n"
            "   Please install the required Python packages using one of the\n"
            "   following methods:\n"
            "   • APT (if a Kali package exists):\n"
            "       $ sudo apt install python3-pyqt6 python3-pymetasploit3\n"
            "   • pipx (recommended for user‑level installation):\n"
            "       $ pipx install -r requirements.txt\n"
            "   • A virtual environment:\n"
            "       $ python3 -m venv .venv && . .venv/bin/activate\n"
            "       $ pip install -r requirements.txt\n",
            file=sys.stderr,
        )
    else:
        # Any other installation error – just report it.
        print(
            f"Failed to install dependencies (exit code {result.returncode}):\n"
            f"{result.stderr}",
            file=sys.stderr,
        )
    # Do not abort; assume dependencies are either already satisfied or
    # will be handled by the user later.


# Install dependencies before importing any project modules.
_ensure_dependencies()

from ui.main_window import main

if __name__ == "__main__":
    main()
