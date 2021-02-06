import time
import _thread
import cherrypy
from jinja2 import Environment, FileSystemLoader

from FullscreenTabletTracker import Fullscreen_Window


strokes = []
env = Environment(loader=FileSystemLoader(searchpath='./'), 
                  autoescape=True)
index_template = env.get_template('index.html')
Y_OFFSET = -20


class App(object):
    @cherrypy.expose
    def index(self):
        with open('index.html', 'r', encoding='utf-8') as f:
            return f.read()
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def poll(self, stroke_idx):
        x = 0
        while int(stroke_idx) == len(strokes) and x < 30:
            time.sleep(0.3)
            x += 1
        return strokes
    

if __name__ == '__main__':
    def run():
        cherrypy.server.socket_host = '0.0.0.0'
        cherrypy.server.thread_pool = 1
        cherrypy.config.update({'global': {'engine.autoreload.on': False}})
        cherrypy.quickstart(App())
    _thread.start_new_thread(run, ())
    
    def fn(points):
        points = [(x, max(0, y+Y_OFFSET)) for x, y in points]
        strokes.append(points)
    w = Fullscreen_Window(fn)
    w.tk.mainloop()
