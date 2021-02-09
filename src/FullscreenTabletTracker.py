import _thread
from tkinter import *
from pynput import mouse

from constants import RESOLUTION


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
        _thread.start_new_thread(self.listen, ())
        
    def listen(self):
        listener = mouse.Listener(on_move=self.motion, 
                                  on_click=self.on_click)
        listener.start()
        while True:
            listener.wait()
        
    def motion(self, x, y):
        if self.mouse_down:
            self.points.append((x, y))
        self.on_motion(x, y)
        
    def on_click(self, *args):
        if self.points:
            self.on_draw_end(self.points)
        self.points = []
        self.mouse_down = args[-1]
        
    def release(self, event):
        self.on_click(False)

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
