import threading
import time

from watchdog.events import FileSystemEventHandler

from watchsync import utils
from watchsync.logger import logger as base_logger

logger = base_logger.getChild("WatchsyncDaemon")


class WatchsyncdEventHandler(FileSystemEventHandler):
    def __init__(self, path, config):
        self.path = path
        self.config = config
        self.event_times = {}
        self.lock = threading.Lock()

    def on_modified(self, event):
        self.handle_event(event)

    def on_created(self, event):
        self.handle_event(event)

    def handle_event(self, event):
        if event.is_directory:
            return
        with self.lock:
            current_time = time.time()
            last_event_time = self.event_times.get(event.src_path, 0)
            if current_time - last_event_time > 1:
                logger.info(f"File changed: {event.src_path}")
                self.event_times[event.src_path] = current_time
                self.sync_file(event.src_path)

    def sync_file(self, file_path):
        for storage in self.config.files[self.path]["storages"]:
            storage_type = self.config.storages[storage]["type"]
            method = f"_sync_{storage_type}"
            if not hasattr(self, method):
                logger.error("Unknown storage type {storage_type}")
                continue
            getattr(self, method)(file_path, self.config.storages[storage])

    def _sync_rsync(self, file_path, storage):
        rsync_command = f'rsync -azP {self.path}/ {storage["path"]} --relative'
        for exclude in self.config.files[self.path]["excludes"]:
            rsync_command += f" --exclude {exclude}"
        logger.info(f"Rsync: {rsync_command}")
        utils.shell(rsync_command)
        logger.info(f"Rsync synced {file_path} to {storage}")
