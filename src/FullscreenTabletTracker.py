import evdev
import _thread
from tkinter import *
from pathlib import Path
from os import environ
from os.path import expanduser
from dotenv import load_dotenv
from evdev import InputDevice, categorize, ecodes

from constants import RESOLUTION


load_dotenv(override=True)
DEVICE_NAME = environ['TABLET_DEVICE_NAME'].strip()
print("SEARCHING FOR DEVICE NAME:", DEVICE_NAME)


class FullscreenTabletTracker:
    def __init__(self, on_draw_end, on_motion):
        self.on_draw_end = on_draw_end
        self.on_motion = on_motion
        
        self.tk = Tk()
        self.tk.geometry('%sx%s' % RESOLUTION)
        # This just maximizes it so we can see the window. It's nothing to do with fullscreen.
        self.tk.attributes('-zoomed', True)
        self.frame = Frame(self.tk)
        self.frame.pack()
        
        self.state = False
        self.tk.bind("<F11>", self.toggle_fullscreen)
        self.tk.bind("<Escape>", self.end_fullscreen)
        self.toggle_fullscreen()
        
        self.points = []
        self.mouse_down = False

        print("ENUMERATING DEVICES!")
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        self.device = [i for i in devices if i.name == DEVICE_NAME][0]
        self.__max_x = float(self.device.capabilities()[ecodes.EV_ABS][0].max)
        self.__max_y = float(self.device.capabilities()[ecodes.EV_ABS][1].max)

        print("USING DEVICE:", self.device)
        _thread.start_new_thread(self.listen, ())
        
    def listen(self):
        self.__x = None
        self.__y = None

        dev = InputDevice(self.device)
        for event in dev.read_loop():
            if event.type == ecodes.EV_ABS:
                if event.code == ecodes.ABS_X:
                    self.__x = round(int(event.value) / self.__max_x * RESOLUTION[0])
                    print("ABS_X!")
                elif event.code == ecodes.ABS_Y:
                    self.__y = round(int(event.value) / self.__max_y * RESOLUTION[1])
                    print("ABS_Y!")
                print("EV_ABS!!!", event.code)
            elif event.type == ecodes.EV_KEY:
                #if event.code == ecodes.BTN_TOUCH:
                self.on_mouse_up_down(bool(int(event.value)))
                print("EV_KEY!!!", bool(int(event.value)))
            elif event.type == ecodes.SYN_REPORT and self.__x is not None and self.__y is not None:
                self.motion(self.__x, self.__y)
                self.__x = None
                self.__y = None
                print("SYN_REPORT!!!", bool(int(event.value)))

            print(categorize(event), event.type, event.code, event.value)

    def motion(self, x, y):
        if self.mouse_down:
            self.points.append((x, y))
        self.on_motion(x, y)
        
    def on_mouse_up_down(self, value):
        if self.points:
            print("ON DRAW END:", self.points)
            self.on_draw_end(self.points)
        self.points = []
        self.mouse_down = value

    def toggle_fullscreen(self, event=None):
        self.state = not self.state  # Just toggling the boolean
        self.tk.attributes("-fullscreen", self.state)

    def end_fullscreen(self, event=None):
        self.state = False
        self.tk.attributes("-fullscreen", False)

        # NOTE ME!
        raise SystemExit()


if __name__ == '__main__':
    def fn(points):
        print(points)
    w = FullscreenTabletTracker(fn)
    w.tk.mainloop()
