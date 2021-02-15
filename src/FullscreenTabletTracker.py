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
DEVICE_NAME = Path(expanduser(environ['TABLET_DEVICE_NAME']))


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

        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        self.device = [i for i in devices if i.name == DEVICE_NAME]
        _thread.start_new_thread(self.listen, ())
        
    def listen(self):
        xx = 0
        dev = InputDevice(self.device)
        for event in dev.read_loop():
            if event.type == ecodes.EV_ABS:
                if event.code == ecodes.ABS_X:
                    self.__x = event.value
                    xx += 1
                    if xx % 2 == 0:
                        self.motion(self.__x, self.__y)
                elif event.code == ecodes.ABS_Y:
                    self.__y = event.value
                    xx += 1
                    if xx % 2 == 0:
                        self.motion(self.__x, self.__y)
            elif event.type == ecodes.EV_KEY:
                if event.code == ecodes.BTN_TOUCH:
                    self.on_mouse_up_down(event.value)

    def motion(self, x, y):
        if self.mouse_down:
            self.points.append((x, y))
        self.on_motion(x, y)
        
    def on_mouse_up_down(self, value):
        if self.points:
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
