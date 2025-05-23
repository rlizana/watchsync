import os

import yaml

from watchsync.utils import path


class Config:
    @classmethod
    def get_config(cls, config_file: str = "", use_defaults: bool = True):
        config_file_defaults = [
            path(config_file) if config_file else None,
            path("/etc/watchsync/config.yml"),
            path("~/.config/watchsync/config.yml"),
        ]
        if not use_defaults:
            config_file_defaults = [config_file_defaults[0]]
        for config_file in config_file_defaults:
            if config_file and os.path.exists(config_file):
                return Config(config_file=config_file)
        else:
            raise FileNotFoundError(f"Config file {config_file} not found.")

    def __init__(self, config_file: str, **args):
        self.config_file = config_file
        self.config_path = os.path.dirname(config_file)
        self.read()
        self.__dict__.update(args)

    def get(self, key: str, default=None):
        return getattr(self, key, default)

    def __str__(self) -> str:
        return str(self.__dict__)

    def __repr__(self) -> str:
        return self.__str__()

    def _safe_dict(self, data_dict: dict):
        data = data_dict.copy()
        if "config_file" in data:
            del data["config_file"]
        if "config_path" in data:
            del data["config_path"]
        return data

    def read(self):
        self.socket_file = path(self.config_path, "watchsyncd.socket")
        self.storages = {}
        self.files = {}
        if not os.path.exists(self.config_file):
            return False
        with open(self.config_file, "r", encoding="utf-8") as file:
            self.__dict__.update(self._safe_dict(yaml.safe_load(file) or {}))
        return True

    def write(self):
        config_dir = os.path.dirname(self.config_file)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        with open(self.config_file, "w", encoding="utf-8") as file:
            yaml.safe_dump(self._safe_dict(self.__dict__), file)
