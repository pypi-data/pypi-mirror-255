#!usr/bin/python3
# -*- coding: utf-8 -*-

import tomli
from pathlib import Path
from battery_notify.__metadata__ import Metadata


class Configs:

    def __init__(self):
        self.app: str = Metadata.app
        self.config_path: str = Metadata.config_path
        self.battery_usage_message: str = ''
        self.home: Path = Path.home()
        self.pidfile_path: Path = Path(self.home, '.run/')
        self.music_player_pidfile: Path = Path(self.pidfile_path, f'music_player.pid')
        self.config_file: Path = Path(f'{self.config_path}/config.toml')

    def read_file(self) -> dict:
        """ Reads TOML config file."""
        if self.config_file.is_file():
            with open(self.config_file, 'rb') as conf:
                return tomli.load(conf)
        else:
            raise Exception(f"Error: Failed to find '{self.config_file}' file.")
