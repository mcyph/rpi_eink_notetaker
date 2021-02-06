import sys
import _thread
from tkinter import *
from pynput import mouse


class Fullscreen_Window:
    def __init__(self, on_draw_end):
        self.on_draw_end = on_draw_end
        
        self.tk = Tk()
        self.tk.geometry('1920x1080')
        # This just maximizes it so we can see the window. It's nothing to do with fullscreen.
        self.tk.attributes('-zoomed', True)
        self.frame = Frame(self.tk)
        self.frame.pack()
        
        self.state = False
        self.tk.bind("<F11>", self.toggle_fullscreen)
        self.tk.bind("<Escape>", self.end_fullscreen)
        #self.tk.bind("<B1-Motion>", self.motion)
        #self.tk.bind("<Button-1>", self.release)
        #self.tk.bind("<ButtonRelease-1>", self.release)
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


if __name__ == '__main__':
    def fn(points):
        print(points)
    w = Fullscreen_Window(fn)
    w.tk.mainloop()
