from cleo.helpers import argument

from watchsync.command import Command


class FileDelCommand(Command):
    name = "file del"
    description = "Delete a file."
    arguments = [
        argument(
            name="path",
            description="Local path to.",
            optional=False,
        ),
        argument(
            name="storage",
            description="Storage name to sync files",
            default=False,
            optional=True,
        ),
    ]

    def handle(self):
        path = self.argument("path")
        if path not in self.config.files:
            self._error(f'File "{path}" not exists')
            return 1
        storage = self.argument("storage")
        if storage:
            if storage not in self.config.files[path]["storages"]:
                self._error(f'Storage "{storage}" not exists in "{path}".')
                return 2
            self.config.files[path]["storages"].remove(storage)
            self._success(f'Remove storage "{storage}" in file "{path}".')
        else:
            del self.config.files[path]
            self._success(f'File "{path}" removed.')
        self.config.write()
