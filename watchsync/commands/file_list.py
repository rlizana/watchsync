from watchsync.command import Command


class FileListCommand(Command):
    name = "file list"
    description = "List all files."

    def handle(self):
        if not self.config.files:
            self._warn("No files found.")
            return
        table = self.table()
        table.set_headers(["Name", "Storages", "Excludes"])
        for name, file in self.config.files.items():
            table.add_rows(
                [
                    [
                        name,
                        "\n".join(file["storages"]),
                        "\n".join(file["excludes"]),
                    ]
                ]
            )
        table.render()
