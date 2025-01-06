from cleo.application import Application

from watchsync.__version__ import APP_NAME, __version__
from watchsync.commands.file_add import FileAddCommand
from watchsync.commands.file_del import FileDelCommand
from watchsync.commands.file_list import FileListCommand
from watchsync.commands.file_sync import WatchSyncCommand
from watchsync.commands.help_list import HelpListCommand
from watchsync.commands.reload import ReloadCommand
from watchsync.commands.start import StartCommand
from watchsync.commands.status import StatusCommand
from watchsync.commands.stop import StopCommand
from watchsync.commands.storage_add import StorageAddCommand
from watchsync.commands.storage_del import StorageDelCommand
from watchsync.commands.storage_list import StorageListCommand
from watchsync.commands.version import VersionCommand


def create_app():
    app = Application(APP_NAME, __version__)
    help_list_command = HelpListCommand()
    app._default_command = help_list_command.name
    app.add(help_list_command)

    app.add(FileAddCommand())
    app.add(FileDelCommand())
    app.add(FileListCommand())
    app.add(WatchSyncCommand())
    app.add(ReloadCommand())
    app.add(StartCommand())
    app.add(StatusCommand())
    app.add(StopCommand())
    app.add(StorageAddCommand())
    app.add(StorageDelCommand())
    app.add(StorageListCommand())
    app.add(VersionCommand())
    return app


def main():
    app = create_app()
    app.run()


if __name__ == "__main__":
    main()
