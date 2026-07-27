from evdev import InputDevice, UInput, list_devices

def create_virtual_device():
    mouse, keyboard = None, None

    input_devices = [InputDevice(path) for path in list_devices()]

    for input_device in input_devices:
        if input_device.name == "mouse-swipe-virtual-device":
            continue

        try:
            capabilities = input_device.capabilities(verbose=True)
        except Exception:
            continue

        keys = capabilities.get(("EV_KEY", 1), [])
        rel_axes = capabilities.get(("EV_REL", 2), [])

        if mouse is None and ("BTN_RIGHT", 273) in keys:
            if ("REL_X", 0) in rel_axes and ("REL_Y", 1) in rel_axes:
                mouse = input_device

        if ("KEY_LEFTMETA", 125) in keys:
            keyboard = input_device

        if mouse and keyboard:
            break

    if not(mouse):
        raise Exception("No mouses found.")

    if not(keyboard):
        raise Exception("No keyboards found.")

    return UInput.from_device(mouse, keyboard, name="mouse-swipe-virtual-device")

def remove_virtual_device(virtual_device):
    try:
        if virtual_device:
            virtual_device.close()
    except Exception:
        pass
