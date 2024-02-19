#!usr/bin/python3
# -*- coding: utf-8 -*-

from daemon import daemon
from battery_notify.notify import BatteryNotify


def run_daemon() -> None:
    with daemon.DaemonContext():
        bat = BatteryNotify()
        bat.notify()
