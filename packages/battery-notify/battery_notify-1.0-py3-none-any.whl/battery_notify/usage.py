#!usr/bin/python3
# -*- coding: utf-8 -*-

from battery_notify.__metadata__ import Metadata


class Usage:

    def __init__(self):
        self.app: str = Metadata.app
        self.version: str = Metadata.version
        self.config_path: str = Metadata.config_path

    def help(self, exit_code: int) -> None:
        """ Prints the help menu. """
        args: str = (f'Battery Notify - Version: {self.version}\n'
                     f'\nUsage: {self.app} [OPTIONS]\n'
                     '\nOptional arguments:\n'
                     '  help         Display this help and exit.\n'
                     '  info         Display battery information.\n'
                     '\nDaemon options:\n'
                     '  start        Start battery daemon.\n'
                     '  stop         Stop battery daemon.\n'
                     '  restart      Restart battery daemon.\n'
                     '  status       Display battery daemon status.\n'
                     '  enable       Enable autostart battery daemon.\n'
                     '  disable      Disable autostart battery daemon.\n'
                     
                     f'\nEdit the config file in {self.config_path}config.toml.')

        print(args)
        raise SystemExit(exit_code)
