#!usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from battery_notify.usage import Usage
from battery_notify.daemon import BatteryDaemon


def run_app() -> None:
    """ Run the battery-notify app. """
    bat_daemon = BatteryDaemon()
    usage = Usage()
    args: list = sys.argv
    args.pop(0)
    if len(args) > 1 or len(args) == 0:
        usage.help(1)
    bat_daemon.run(args[0])
