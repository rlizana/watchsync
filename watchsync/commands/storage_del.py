from cleo.helpers import argument

from watchsync.command import Command


class StorageDelCommand(Command):
    name = "storage del"
    description = "Del a storage."
    arguments = [
        argument(
            name="name",
            description="The name of the storage",
            optional=False,
        ),
    ]

    def handle(self):
        if self.argument("name") not in self.config.storages:
            self._error("Storage not exists.")
            return 1
        del self.config.storages[self.argument("name")]
        self.config.write()
        self._success(f'Storage "{self.argument("name")}" deleted.')
