import os

from watchsync.command import Command
from watchsync.daemon.connector import Connector


class ReloadCommand(Command):
    name = "reload"
    description = "Reload daemon and apply config changes."

    def handle(self):
        if not os.path.exists(self.config.socket_file):
            self._error("Daemon is not running.")
            return 0
        daemon = Connector(self.config.socket_file)
        response = daemon.send("reload")
        self._success(f"Daemon response: {response}")
