from watchsync.command import Command


class StorageListCommand(Command):
    name = "storage list"
    description = "List all storages."

    def handle(self):
        if not self.config.storages:
            self._warn("No storages found.")
            return
        table = self.table()
        table.set_headers(["Name", "Type", "Path", "Options"])
        for name, storage in self.config.storages.items():
            table.add_rows(
                [
                    [
                        name,
                        storage["type"],
                        storage["path"],
                        str(storage["options"]),
                    ]
                ]
            )
        table.render()
