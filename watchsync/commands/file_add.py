import os

from cleo.helpers import argument, option

from watchsync import utils
from watchsync.command import Command


class FileAddCommand(Command):
    name = "file add"
    description = "Add a file for watch and sync."
    arguments = [
        argument(
            name="path",
            description="Local path to file or directory for watch and sync.",
            optional=False,
        ),
    ]
    options = [
        option(
            "storage",
            "st",
            description="Storage name where to sync files",
            flag=False,
            multiple=True,
        ),
        option(
            "del-storage",
            "dst",
            description="Remove file to storage",
            flag=False,
            multiple=True,
        ),
        option(
            "exclude",
            "e",
            description="Exclude files or directories from sync",
            flag=False,
            multiple=True,
        ),
        option(
            "del-exclude",
            "de",
            description="Remove exlude",
            flag=False,
            multiple=True,
        ),
    ]

    def handle(self):
        file_path = utils.path(self.argument("path"))
        if not os.path.exists(file_path):
            self._error(f'File "{file_path}" not exists')
            return 1
        action = "added" if file_path not in self.config.files else "modified"
        item = self.config.files.setdefault(
            file_path,
            {
                "storages": [],
                "excludes": [],
                "recursive": True,
            },
        )
        for storage in self.option("storage"):
            if storage not in self.config.storages:
                self._error(f'Storage "{storage}" not exists')
                return 2
            if storage not in item["storages"]:
                item["storages"].append(storage)
        for del_storage in self.option("del-storage"):
            if del_storage in item["storages"]:
                item["storages"].remove(del_storage)
        for exclude in self.option("exclude"):
            if exclude not in item["excludes"]:
                item["excludes"].append(exclude)
        for del_exclude in self.option("del-exclude"):
            if del_exclude in item["excludes"]:
                item["excludes"].remove(del_exclude)
        self.config.write()
        self._success(f'File "{file_path}" {action}.')
