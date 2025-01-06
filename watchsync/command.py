import logging
import os

from cleo.commands.command import Command as BaseCommand
from cleo.helpers import option
from cleo.io.io import IO
from cleo.io.outputs.output import Verbosity

from watchsync.config import Config
from watchsync.logger import logger


class Command(BaseCommand):
    def configure(self) -> None:
        self._definition.add_option(
            option(
                "config-file",
                "c",
                description="Set path to treytux config",
                default="~/.config/watchsync/config.yml",
                flag=False,
            )
        )
        self._definition.add_option(
            option(
                "socket-file",
                "s",
                description="Set path to treytux config",
                default="",
                flag=False,
            )
        )
        super().configure()

    def execute(self, io: IO) -> int:
        self._io = io
        verbosity = self.io.output.verbosity
        log_level = (
            logging.DEBUG if verbosity == Verbosity.VERBOSE else logging.INFO
        )
        logger.setLevel(log_level)
        self.config = Config(
            config_file=self.path(self.option("config-file")),
            socket_file=self.path(self.option("socket-file")),
        )
        self.add_style("error", fg="red", options=["bold"])
        self.add_style("info", fg="blue")
        self.add_style("debug", fg="cyan")
        self.add_style("warn", fg="yellow")
        self.add_style("success", fg="green")
        logger.info(f'Execute "{" ".join(io.input._tokens)}"')
        status_code = super().execute(io)
        return 0 if status_code is None else status_code

    def _error(self, txt):
        self.line(txt, "error")
        logger.error(txt)

    def _info(self, txt):
        self.line(txt, "info")
        logger.info(txt)

    def _warn(self, txt):
        self.line(txt, "warn")
        logger.warning(txt)

    def _success(self, txt):
        self.line(txt, "success")
        logger.info(txt)

    def _debug(self, txt):
        self.line(txt, "debug", verbosity=Verbosity.VERBOSE)
        logger.debug(txt)

    def path(self, *args):
        args = [a.replace("~", os.path.expanduser("~")) for a in args if a]
        if not args:
            return False
        return os.path.abspath(os.path.join(*args))
