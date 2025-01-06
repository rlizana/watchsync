from watchdog.observers import Observer

from watchsync.daemon.watchsyncd_event_handler import WatchsyncdEventHandler
from watchsync.logger import logger as base_logger

logger = base_logger.getChild("WatchsyncDaemon")


class WatchsyncdObserver:
    def __init__(self, config):
        self.config = config
        self.observers = {}

    def stop(self):
        for path in list(self.observers.keys()):
            observer = self.observers.pop(path, None)
            if observer:
                logger.info(f"Stoping observer for {path}")
                observer.stop()
                observer.join()

    def start(self):
        for path, file in self.config.files.items():
            logger.info(f"Initializing observer for {path}")
            self.observers[path] = Observer()
            self.observers[path].schedule(
                WatchsyncdEventHandler(path, self.config),
                path=path,
                recursive=file.get("recursive", True),
            )
            self.observers[path].start()

    def restart(self):
        self.stop()
        self.config.read()
        self.start()
