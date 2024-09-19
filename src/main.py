#!/usr/bin/python3

import asyncio, copy, logging
from evdev import InputDevice, ecodes, list_devices
from systemd.journal import JournalHandler
from virtual_device import create_virtual_device, remove_virtual_device
from config import read_config_file
from mouse import Mouse

def get_mouses():
    logger.info("Searching for mouses..")

    global number_of_devices

    input_devices = [InputDevice(path) for path in list_devices()]
    number_of_devices = len(input_devices)
    mouses.clear()

    for input_device in input_devices:
        if input_device.name == "mouse-swipe-virtual-device":
            continue

        try:
            keys = input_device.capabilities(verbose=True)[("EV_KEY", 1)]
        except:
            continue

        if ("BTN_RIGHT", 273) in keys:
            logger.info("Mouse found: " + input_device.name)
            mouse = Mouse(input_device.name)
            mouse.input_device = input_device
            mouse.swipe_buttons = copy.deepcopy(config_swipe_buttons)
            mouse.input_device.grab()
            mouses.append(mouse)
            tasks.append(asyncio.create_task(task_handle_mouse_events(mouse)))

def ungrab_mouses():
    for mouse in mouses:
        try:
            if mouse.input_device:
                mouse.input_device.ungrab()
        except:
            pass

def emulate_event(type, code, value):
    virtual_device.write(type, code, value)
    if (code == ecodes.REL_WHEEL):
        virtual_device.write(type, ecodes.REL_WHEEL_HI_RES, 120 if value > 0 else -120)
    if (code == ecodes.REL_HWHEEL):
        virtual_device.write(type, ecodes.REL_HWHEEL_HI_RES, 120 if value > 0 else -120)
    virtual_device.syn()

def emulate_key_press(keys):
    for key in keys:
        virtual_device.write(ecodes.EV_KEY, ecodes.ecodes[key], 1)
    virtual_device.syn()

    for key in reversed(keys):
        virtual_device.write(ecodes.EV_KEY, ecodes.ecodes[key], 0)
    virtual_device.syn()

async def task_handle_mouse_events(mouse):
    async for event in mouse.input_device.async_read_loop():
        should_forward = True

        # By default, REL_WHEEL and REL_WHEEL_HI_RES are sent together in one sync.
        # Avoids emulating these two events separately causing duplicated (jumpy) scrolling.
        # Emulate REL_WHEEL_HI_RES properly on emulate_event instead.
        if event.code == ecodes.REL_WHEEL_HI_RES or event.code == ecodes.REL_HWHEEL_HI_RES:
            should_forward = False
        elif event.type == ecodes.EV_REL: # mouse movement or mouse wheel
            for swipe_button in mouse.swipe_buttons:
                if swipe_button.pressed:
                    if swipe_button.freeze:
                        should_forward = False

                    if event.code == ecodes.REL_X:
                        swipe_button.deltaX += event.value

                        if abs(swipe_button.deltaX) > swipe_button.delta and not(swipe_button.moved):
                            swipe_button.moved = True

                        if swipe_button.scroll and swipe_button.moved:
                            emulate_event(ecodes.EV_REL, ecodes.REL_HWHEEL, 1 if event.value > 0 else -1)
                    elif event.code == ecodes.REL_Y:
                        swipe_button.deltaY += event.value

                        if abs(swipe_button.deltaY) > swipe_button.delta and not(swipe_button.moved):
                            swipe_button.moved = True

                        if swipe_button.scroll and swipe_button.moved:
                            emulate_event(ecodes.EV_REL, ecodes.REL_WHEEL, -1 if event.value > 0 else 1)
        elif event.type == ecodes.EV_KEY:
            for swipe_button in mouse.swipe_buttons:
                if event.code == ecodes.ecodes[swipe_button.button]:
                    should_forward = False
                    swipe_button.pressed = event.value

                    if not(swipe_button.pressed):
                        if not(swipe_button.moved):
                            emulate_key_press(swipe_button.click)
                        elif not(swipe_button.scroll):
                            if abs(swipe_button.deltaX) > abs(swipe_button.deltaY):
                                emulate_key_press(swipe_button.swipe_right if swipe_button.deltaX > 0 else swipe_button.swipe_left)
                            else:
                                emulate_key_press(swipe_button.swipe_down if swipe_button.deltaY > 0 else swipe_button.swipe_up)

                        swipe_button.deltaX = 0
                        swipe_button.deltaY = 0
                        swipe_button.moved = False

        if should_forward:
            emulate_event(event.type, event.code, event.value)

async def task_detect_new_devices():
    while True:
        await asyncio.sleep(5)
        if len(list_devices()) > number_of_devices:
            # Cancel this task to trigger the cancelling of all tasks on gather
            tasks[0].cancel()
  
def cancel_tasks():
    for task in tasks:
        try:
            if not(task.done()) and not(task.cancelled()):
                task.cancel()
        except:
            pass

    for task in tasks:
        try:
            task.result()
        except:
            pass

async def run_tasks():
    try:            
        tasks.clear()
        tasks.append(asyncio.create_task(task_detect_new_devices()))
        get_mouses()
        await asyncio.gather(*tasks)
    except:
        pass
    finally:
        ungrab_mouses()
        cancel_tasks()

if __name__ == "__main__":
    mouses, tasks = [], []

    try:
        logger = logging.getLogger('mouse-swipe')
        logger.addHandler(JournalHandler())
        logger.setLevel(logging.INFO)
    except BaseException as e:
        print(e)
        quit()
        
    try:
        virtual_device = create_virtual_device()
        config_swipe_buttons = read_config_file()
    except Exception as e:
        logger.info(e)
        quit()

    while True:
        try:
            asyncio.run(run_tasks())
        except KeyboardInterrupt:
            print("Exiting..")
            break

    remove_virtual_device(virtual_device)
