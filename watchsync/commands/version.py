from watchsync.__version__ import APP_NAME, __version__
from watchsync.command import Command


class VersionCommand(Command):
    name = "version"
    description = "Show version."
    check_config = False

    def handle(self):
        self._info(f"{APP_NAME} {__version__}")
