from watchsync.command import Command
from watchsync.daemon.connector import Connector


class StopCommand(Command):
    name = "stop"
    description = "Stop daemon watchsync."

    def handle(self):
        daemon = Connector(self.config.socket_file)
        if not daemon.is_alive():
            self._error("Daemon is not running.")
            return 0
        response = daemon.send("stop")
        self._success(f"Daemon response: {response}")
