import concurrent.futures

from cleo.helpers import argument

from watchsync import utils
from watchsync.command import Command
from watchsync.daemon.watchsyncd_event_handler import WatchsyncdEventHandler


class WatchSyncCommand(Command):
    name = "file sync"
    description = "Sync now a file or directory."
    arguments = [
        argument(
            name="file",
            description="File to sync or 'all' for all files.",
            optional=True,
            default="all",
        ),
    ]

    def handle(self):
        if self.argument("file") == "all":
            files = list(self.config.files.keys())
        else:
            files = [utils.path(self.argument("file"))]
        events = []
        for file in files:
            if file not in self.config.files:
                self._error(f'File "{file}" not exists.')
                return 1
            events.append(WatchsyncdEventHandler(file, self.config))
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(event.sync_file, event.path)
                for event in events
            ]
            for future in concurrent.futures.as_completed(futures):
                future.result()
