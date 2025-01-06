import subprocess

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
        cmd = f"poetry run watchsyncd {self.config.config_file}"
        self._debug(f'Execute command "{cmd}"')
        process = subprocess.Popen(
            cmd.split(" "),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
        )
        self._success(f"Daemon started PID {process.pid}")
