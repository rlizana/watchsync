from watchsync.command import Command
from watchsync.daemon.connector import Connector


class StatusCommand(Command):
    name = "status"
    description = "Show status daemon watchsync."

    def handle(self):
        daemon = Connector(self.config.socket_file)
        if daemon.is_alive():
            self._success("Daemon is running")
            return 0
        else:
            self._error("Daemon is stopped.")
            return 0
