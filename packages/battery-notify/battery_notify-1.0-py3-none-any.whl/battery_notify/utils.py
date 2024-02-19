#!usr/bin/python3
# -*- coding: utf-8 -*-

import psutil
import subprocess
from battery_notify.configs import Configs


class Utils:

    def __init__(self):
        self.configs = Configs()
        self.config: dict = self.configs.read_file()
        self.audio_player: str = self.config['AUDIO_PLAYER']
        self.audio_file: str = self.config['AUDIO_FILE']

    @staticmethod
    def pid_process(process_name: str) -> int:
        """ Returns the PID by process name. """
        for proc in psutil.process_iter():
            if process_name in proc.name():
                return proc.pid
        return 0

    @staticmethod
    def secs_to_hours(secs: int) -> str:
        """ Converts seconds to hh/mm/ss. """
        mm, ss = divmod(secs, 60)
        hh, mm = divmod(mm, 60)
        return "%d:%02d:%02d" % (hh, mm, ss)

    def battery_information(self) -> None:
        """ Prints all battery information. """
        battery = psutil.sensors_battery()

        if battery is None:
            raise SystemExit('Battery not found.')

        plugged: str = 'Charger plugged in: yes'
        status: str = 'Battery status: charging'
        print(f'Battery level is: {battery.percent:.2f}%')
        battery_usage_time_left: str = self.secs_to_hours(battery.secsleft)

        if not battery.power_plugged:
            print(f"Battery usage time left: {battery_usage_time_left}")
            plugged: str = 'Charger plugged in: no'
            status: str = 'Battery status: discharging'

        print(status)
        print(plugged)

    def music_player(self) -> None:
        """ Runs the music player and creates the PID file. """
        if self.audio_player and self.audio_file:
            p = subprocess.Popen(f"{self.audio_player} {self.audio_file}", shell=True)
            self.configs.music_player_pidfile.write_text(str(p.pid), encoding='utf-8')

    def create_pidfile_path(self) -> None:
        """ Creates a PID path. """
        if not self.configs.pidfile_path.is_dir():
            self.configs.pidfile_path.mkdir(parents=True, exist_ok=True)
