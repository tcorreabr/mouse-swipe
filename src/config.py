import configparser
from swipe_button import SwipeButton

DEFAULT_IGNORE_DEVICES = {
    "mouse-swipe-virtual-device"
}

def _get_array(string, separator="+"):
    if string:
        return list(map(str.strip, string.split(separator)))
    else:
        return []

def read_config_file():
    swipe_buttons = []
    ignore_devices = DEFAULT_IGNORE_DEVICES.copy()

    config = configparser.ConfigParser()
    config.read("/etc/mouse-swipe.conf")

    if config.has_section("general"):
        ignore_devices.update(
            _get_array(
                config["general"].get("ignore_devices"),
                separator=","
            )
        )

    for button in config.sections():
        if not(button.startswith("BTN_")):
            continue

        swipe_button = SwipeButton(button)
        click = _get_array(config[button].get("click"))
        swipe_button.click = click if (len(click) > 0) else [button]
        swipe_button.freeze = config[button].getboolean("freeze", False)
        swipe_button.scroll = config[button].getboolean("scroll", False)
        swipe_button.delta = abs(config[button].getint("delta", 10))
        if not(swipe_button.scroll):
            swipe_button.swipe_left = _get_array(config[button].get("swipe_left"))
            swipe_button.swipe_right = _get_array(config[button].get("swipe_right"))
            swipe_button.swipe_up = _get_array(config[button].get("swipe_up"))
            swipe_button.swipe_down = _get_array(config[button].get("swipe_down"))

        swipe_buttons.append(swipe_button)

    return swipe_buttons, ignore_devices


