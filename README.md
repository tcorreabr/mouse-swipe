# mouse-swipe

Swipe gestures support for mouse buttons through [Systemd](https://systemd.io/) service that intercepts and emulates input device events. Only up, down, left and right swipes are supported. You can also configure buttons to emulate vertical and horizontal scroll while they're pressed.

Since it operates at [evdev](https://en.wikipedia.org/wiki/Evdev) level, it works on [X11](https://x.org/wiki/) and [Wayland](https://wayland.freedesktop.org/).

The default configuration works fine on [Gnome](https://www.gnome.org/) desktop, activating the overview and switching workspaces through right mouse button swipes. For integration with other desktops edit the config file (/etc/mouse-swipe.conf) and restart the service (systemctl restart mouse-swipe.service).

## Requirements

- [python-systemd](https://github.com/systemd/python-systemd/)
- [python-evdev](https://github.com/gvalkov/python-evdev)

## Installation

```shell
git clone https://gitlab.com/tcorreabr/mouse-swipe
sudo mouse-swipe/install
```

To uninstall:

```shell
sudo mouse-swipe/uninstall
```

If you have edited the /etc/mouse-swipe.conf file, you might want to make a backup of it before uninstalling.




