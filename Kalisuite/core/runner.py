import subprocess
from PyQt6.QtCore import QObject, pyqtSignal, QThread


class _Worker(QThread):
    """
    Internal QThread that runs a subprocess and emits each line of output.
    """
    output_line = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, command):
        super().__init__()
        self.command = command
        self.process = None  # Will hold the subprocess.Popen object

    def run(self):
        # Execute the command, merging stderr into stdout.
        self.process = subprocess.Popen(
            self.command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )

        # Stream output line‑by‑line.
        for line in self.process.stdout:
            self.output_line.emit(line.rstrip())
        self.process.wait()
        self.finished.emit()

    def stop(self):
        """
        Terminate the running subprocess (if any) and emit the finished signal.
        """
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except Exception:
                self.process.kill()
        # Ensure the thread finishes
        self.finished.emit()


class CommandRunner(QObject):
    """
    Generic class that runs any shell command via subprocess,
    streams stdout/stderr live, and exposes Qt signals for output.
    """
    output_line = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker = None

    def run(self, command):
        """
        Start the given command (list of strings or a single string).
        If a previous command is still running it will be terminated.
        """
        if self._worker is not None and self._worker.isRunning():
            # Gracefully stop the previous worker
            self._worker.stop()
            self._worker.wait()

        # Ensure command is a list for subprocess.Popen.
        if isinstance(command, str):
            command = command.split()

        self._worker = _Worker(command)
        self._worker.output_line.connect(self.output_line)
        self._worker.finished.connect(self.finished)
        self._worker.start()

    def terminate(self):
        """
        Public method to stop the currently running command (if any).
        """
        if self._worker is not None and self._worker.isRunning():
            self._worker.stop()
            self._worker.wait()
