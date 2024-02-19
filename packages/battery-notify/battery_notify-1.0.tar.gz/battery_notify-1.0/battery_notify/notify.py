#!usr/bin/python3
# -*- coding: utf-8 -*-

import time
import psutil
import notify2
from battery_notify.utils import Utils
from battery_notify.configs import Configs
from battery_notify.__metadata__ import Metadata


class BatteryNotify:

    def __init__(self):
        notify2.uninit()
        notify2.init('Battery Notify')
        self.utils = Utils()
        self.app: str = Metadata.app
        self.pixmaps_path: str = Metadata.pixmaps_path
        self.notify_summary: str = '⚡ BATTERY NOTIFY ⚡'
        self.notify_message: str = 'Battery level is:'
        self.battery_usage_message: str = ''
        self.battery_icon: str = f'{self.pixmaps_path}{self.app}.png'
        self.configs = Configs()
        self.config: dict = self.configs.read_file()

    def notify(self) -> None:
        """ Sends notifications over dbus. """
        while True:
            battery = psutil.sensors_battery()

            if not battery.power_plugged:
                self.battery_usage_message: str = (f"\nBattery usage time left: "
                                                   f"{self.utils.secs_to_hours(battery.secsleft)}")

            if battery.percent <= self.config['BATTERY_LEVEL'] and not battery.power_plugged:
                n = notify2.Notification(
                    self.notify_summary,
                    f"{self.notify_message} {battery.percent:.2f}%, {self.battery_usage_message}",
                    self.battery_icon)
                n.set_timeout(self.config['NOTIFICATION_STANDBY'] * 60000)
                n.show()
                self.utils.music_player()

            time.sleep(self.config['INTERVAL_TIME'])
