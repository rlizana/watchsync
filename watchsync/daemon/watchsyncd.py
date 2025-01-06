import json
import os
import socket
import sys

from watchsync import utils
from watchsync.config import Config
from watchsync.daemon.connector import Connector
from watchsync.daemon.watchsyncd_observer import WatchsyncdObserver
from watchsync.logger import logger as base_logger

logger = base_logger.getChild("WatchsyncDaemon")


class Watchsyncd:
    def __init__(self, config_file: str = ""):
        self.config = Config.get_config(config_file=config_file)
        logger.info(f"Using config file: {self.config.config_file}")
        self.socket_file = utils.path(self.config.socket_file)
        self.observer = WatchsyncdObserver(self.config)

    def loop(self):
        if os.path.exists(self.socket_file):
            conn = Connector(self.socket_file)
            if conn.is_alive():
                logger.error(
                    "Another process is trying to start the daemon but this "
                    "one is already started."
                )
                raise RuntimeError("Daemon is already running")
            os.remove(self.socket_file)
        logger.info(f"Create socket in {self.socket_file}")
        server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server_socket.bind(self.socket_file)
        server_socket.listen(1)
        try:
            self.running = True
            self.observer.start()
            logger.info("Daemon started")
            while self.running:
                conn, _ = server_socket.accept()
                data = conn.recv(1024)
                command = data.decode()
                if data:
                    logger.info(f"Received command: {command}")
                    response = self._call(command)
                    try:
                        conn.send(response.encode())
                    except BrokenPipeError:
                        pass
                conn.close()
        except KeyboardInterrupt:
            logger.info("Stopped by KeyboardInterrupt")
        except Exception as exception:
            logger.error(f"Error {exception}")
            raise exception
        finally:
            self.observer.stop()
            server_socket.close()
            os.unlink(self.socket_file)
            logger.info("Stopped")

    def _call(self, command: str):
        args = command.strip().lower().split(" ")
        cmd = args.pop(0)
        if not hasattr(self, f"command_{cmd}"):
            msg = f'Unknown command "{cmd}"'
            logger.error(msg)
            return msg
        return getattr(self, f"command_{cmd}")(*args)

    def command_stop(self):
        self.running = False
        logger.info("Stopping ...")
        return "Stoped"

    def command_status(self):
        return "OK"

    def command_reload(self):
        self.observer.restart()
        return "Reloaded"

    def command_info(self):
        return json.dumps(
            {
                "config": self.config.__dict__,
            }
        )


def main(config_file: str = ""):
    if not config_file:
        config_file = sys.argv[1] if len(sys.argv) > 1 else ""
    daemon = Watchsyncd(config_file)
    daemon.loop()


if __name__ == "__main__":
    main()
