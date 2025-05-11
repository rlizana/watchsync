import os
import time

from watchsync.command import Command
from watchsync.daemon.connector import Connector


class RestartCommand(Command):
    name = "restart"
    description = "Restart the daemon."

    def handle(self):
        if not os.path.exists(self.config.socket_file):
            self._error("Daemon is not running.")
            return 1
        daemon = Connector(self.config.socket_file)
        daemon.send("stop")
        for _ in range(10):
            time.sleep(1)
            if not os.path.exists(self.config.socket_file):
                break
        else:
            self._error("Failed to stop daemon.")
            return 2
        start_cmd = self.application.find("start")
        start_cmd.set_application(self.application)
        result = start_cmd.execute(self.io)
        if result == 0:
            self._success("Daemon restarted.")
        else:
            self._error("Failed to start daemon.")
        return result
