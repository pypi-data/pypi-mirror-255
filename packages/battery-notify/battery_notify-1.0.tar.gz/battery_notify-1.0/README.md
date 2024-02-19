## About

A battery monitor and notification app with sound for Linux systems.

## Usage

```bash
$ battery-notify start
battery-daemon starting...
started.

$ battery-notify stop
battery-daemon stopping...
stopped.

$ battery-notify status
battery-daemon is not running.

$ battery-notify info
Battery level is: 97.67%
Battery usage time left: 2:03:17
Battery status: discharging
Charger plugged: off
```


## Install

```bash
$ pip install battery-notify
```

## Install the data

Download the source code, unzip it, go into the source directory and run:

```bash
$ python3 data.py install
```

## Uninstall

```bash
$ pip uninstall battery-notify

$ python3 data.py uninstall 
```

## Config file

```bash
/etc/battery-notify/config.toml
```

## XDG desktop file

```bash
/etc/xdg/autostart/battery-notify.desktop.sample
```

## Pidfile

```bash
$HOME/.run/battery-notify.pid
$HOME/.run/music_player.pid
```
