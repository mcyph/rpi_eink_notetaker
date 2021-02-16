import evdev
from time import sleep
from os import environ, system
from os.path import expanduser
from dotenv import load_dotenv


load_dotenv(override=True)
DEVICE_NAME = environ['TABLET_DEVICE_NAME'].strip()
TABLET_COMMAND = expanduser(environ['TABLET_COMMAND'])
OTHER_COMMAND = expanduser(environ['OTHER_COMMAND'])
KILL_TABLET_COMMAND = environ['KILL_TABLET_COMMAND']
KILL_OTHER_COMMAND = environ['KILL_OTHER_COMMAND']


def tablet_exists():
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    return bool([i for i in devices if i.name == DEVICE_NAME])


if __name__ == '__main__':
    MODE_NONE = None
    MODE_TABLET = 1
    MODE_OTHER = 2

    current_mode = None

    while True:
        _tablet_exists = tablet_exists()

        if _tablet_exists:
            if current_mode == MODE_TABLET:
                # Do nothing
                pass
            elif current_mode == MODE_OTHER:
                system(KILL_OTHER_COMMAND)
                system(TABLET_COMMAND)
            elif current_mode == MODE_NONE:
                system(TABLET_COMMAND)
            else:
                raise Exception()

            current_mode = MODE_TABLET
        else:
            if current_mode == MODE_OTHER:
                # Do nothing
                pass
            elif current_mode == MODE_TABLET:
                system(KILL_TABLET_COMMAND)
                system(OTHER_COMMAND)
            elif current_mode == MODE_NONE:
                system(OTHER_COMMAND)
            else:
                raise Exception()

            current_mode = MODE_OTHER

        sleep(5)
