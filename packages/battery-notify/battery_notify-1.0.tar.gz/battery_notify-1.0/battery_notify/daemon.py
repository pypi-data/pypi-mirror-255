#!usr/bin/python3
# -*- coding: utf-8 -*-

import psutil
import getpass
import subprocess
from pathlib import Path
from battery_notify.usage import Usage
from battery_notify.utils import Utils
from battery_notify.configs import Configs
from battery_notify.__metadata__ import Metadata


class BatteryDaemon:

    def __init__(self):
        self.configs = Configs()
        self.utils = Utils()
        self.utils.create_pidfile_path()
        self.app: str = Metadata.app
        self.battery_daemon: str = Metadata.daemon
        self.xdg_autostart_path: str = Metadata.xdg_autostart_path
        self.pidfile: Path = Path(self.configs.pidfile_path, f'{self.battery_daemon}.pid')
        self.daemon_pid: int = self.utils.pid_process(self.battery_daemon)
        self.audio_player_pid: int = 0
        self.autostart_disable_file: Path = Path(
            self.xdg_autostart_path, f'{self.app}.desktop.sample')
        self.autostart_enable_file: Path = Path(
            self.xdg_autostart_path, f'{self.app}.desktop')
        self.audio_player: str = self.configs.read_file()['AUDIO_PLAYER']
        if self.audio_player:
            self.audio_player_pid: int = int(self.utils.pid_process(self.audio_player))

    def run(self, arg: str) -> None:
        """ Calls the methods. """
        process: dict = {
            'help': self.usage,
            'info': self.utils.battery_information,
            'start': self.start,
            'stop': self.stop,
            'status': self.status,
            'restart': self.restart,
            'enable': self.autostart_enable,
            'disable': self.autostart_disable
        }
        try:
            process[arg]()
        except KeyError:
            self.usage(1)

    @staticmethod
    def usage(exit_code=0) -> None:
        """ Display the help cli menu. """
        usage = Usage()
        usage.help(exit_code)

    def start(self) -> None:
        """ Starts the battery-daemon and creates a PID file. """
        if self.utils.pid_process('dbus-daemon') == 0:
            raise SystemExit('D-BUS must be running to start battery-daemon')

        if self.daemon_pid == 0:
            print(f'{self.battery_daemon} starting...')
            p = subprocess.Popen(f"{self.battery_daemon} start", shell=True)
            self.daemon_pid: int = p.pid
            self.pidfile.write_text(str(self.daemon_pid), encoding='utf-8')
            print('started.')
        else:
            print(f'{self.battery_daemon} is already running (will not start it twice).')

    def stop(self) -> None:
        """ Stops the battery-daemon and remove the PID file. """
        if self.daemon_pid != 0:
            print(f'{self.battery_daemon} stopping...')
            p1 = psutil.Process(self.daemon_pid)
            p1.terminate()
            if self.pidfile.is_file():
                self.pidfile.unlink()
            self.daemon_pid: int = 0
            print('stopped.')
        else:
            print(f'{self.battery_daemon} is not running (nothing to stop here).')

        if self.audio_player_pid != 0:
            if self.configs.music_player_pidfile.is_file():
                self.configs.music_player_pidfile.unlink()
            p2 = psutil.Process(self.audio_player_pid)
            p2.terminate()

    def status(self) -> None:
        """ Prints the battery-daemon status. """
        if self.daemon_pid != 0:
            print(f'{self.battery_daemon} is currently running.')
        else:
            print(f'{self.battery_daemon} is not running.')

    def restart(self) -> None:
        """ Stops and starts the battery-daemon. """
        if self.daemon_pid != 0:
            self.stop()
            self.start()
        else:
            print(f'{self.battery_daemon} is not running (please use start instead).')

    def autostart_enable(self) -> None:
        """ Enable the autostart battery-daemon. """
        if getpass.getuser() == 'root':
            if self.autostart_disable_file.is_file():
                self.autostart_disable_file.rename(self.autostart_enable_file)
            else:
                print(f'{self.battery_daemon} autostart is already enabled.')
        else:
            print("You need 'root' privileges, use with 'sudo' command:")
            print(f'$ sudo {self.app} enable')

    def autostart_disable(self) -> None:
        """ Disable the autostart battery-daemon. """
        if getpass.getuser() == 'root':
            if self.autostart_enable_file.is_file():
                self.autostart_enable_file.rename(self.autostart_disable_file)
            else:
                print(f'{self.battery_daemon} autostart is already disabled.')
        else:
            print("You need 'root' privileges, use with 'sudo' command:")
            print(f'$ sudo {self.app} disable')
