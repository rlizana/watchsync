from cleo.helpers import argument

from watchsync import utils
from watchsync.command import Command


class StorageAddCommand(Command):
    name = "storage add"
    description = "Add a storage."
    arguments = [
        argument(
            name="name",
            description="The name of the storage",
            optional=False,
        ),
        argument(
            name="type",
            description="The type of storage [rsync]",
            optional=False,
        ),
        argument(
            name="path",
            description="The path of storage",
            optional=False,
        ),
    ]

    def handle(self):
        if self.argument("name") in self.config.storages:
            self._error("Storage already exists.")
            return 1
        storage_type = self.argument("type")
        if not hasattr(self, f"_storage_add_{storage_type}"):
            self._error(f'Type "{storage_type}" not found.')
            return 2
        return getattr(self, f"_storage_add_{storage_type}")()

    def _storage_add_rsync(self):
        storage_path = utils.path(self.argument("path"))
        self.config.storages[self.argument("name")] = {
            "type": "rsync",
            "path": storage_path,
            "options": {},
        }
        self.config.write()
        self._success(f'Storage "{self.argument("name")}" added.')
