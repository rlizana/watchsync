import os
import subprocess
import sys

from watchsync.command import Command
from watchsync.daemon.connector import Connector


class StartCommand(Command):
    name = "start"
    description = "Start watchsync for watch changes in folders and files."

    def handle(self):
        daemon = Connector(self.config.socket_file)
        if daemon.is_alive():
            self._warn("Daemon is already running.")
            return
        daemon_executable = os.path.join(
            os.path.dirname(sys.executable), "watchsyncd"
        )
        if not os.path.exists(daemon_executable):
            raise FileNotFoundError(
                f"watchsyncd executable not found in {daemon_executable}"
            )
        cmd = f"{daemon_executable} {self.config.config_file}"
        self._debug(f'Execute command "{cmd}"')
        process = subprocess.Popen(
            cmd.split(" "),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
        )
        self._success(f"Daemon started PID {process.pid}")
