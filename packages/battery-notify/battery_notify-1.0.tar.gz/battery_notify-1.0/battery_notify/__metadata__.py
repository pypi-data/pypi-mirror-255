#!/usr/bin/python3
# -*- coding: utf-8 -*-


class Metadata:
    app: str = 'battery-notify'
    daemon: str = 'battery-daemon'
    author: str = 'dslackw'
    copyright: str = '2024'
    version_info: tuple = (1, 0)
    version: str = '{0}.{1}'.format(*version_info)
    config_path: str = f'/etc/{app}/'
    pixmaps_path: str = '/usr/share/pixmaps/'
    sounds_path: str = f'/usr/share/sounds/{app}/'
    xdg_autostart_path: str = '/etc/xdg/autostart/'
    license: str = 'GNU General Public License v3 (GPLv3)'
    email: str = 'dslackw@gmail.com'
    homepage: str = 'https://gitlab.com/dslackw/battery-notify'
