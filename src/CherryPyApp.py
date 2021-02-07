import time
import _thread
import cherrypy
from jinja2 import Environment, FileSystemLoader

from HandwrittenDocuments import HandwrittenDocuments
from FullscreenTabletTracker import FullscreenTabletTracker


env = Environment(loader=FileSystemLoader(searchpath='./template'),
                  autoescape=True)
Y_OFFSET = -20


class App(object):
    def __init__(self):
        self.__documents = HandwrittenDocuments()
        self.__current_document = None
        self.__current_page = None

    @cherrypy.expose
    def index(self):
        page_names = sorted(self.__documents, key=lambda x: x.lower())
        new_open_template = env.get_template('new_open.html')
        return new_open_template.render(
            page_names=page_names
        )

    @cherrypy.expose
    def add_page(self, page_name):
        # Add a new page to the document, then browse to it
        document = self.__documents[page_name]
        document.append()
        document.commit()
        raise cherrypy.HTTPRedirect('edit_page?page_name='+page_name+'&page_num='+str(len(document)-1))

    @cherrypy.expose
    def edit_page(self, page_name, page_num=None, submit_button=False):
        if submit_button and page_name not in self.__documents:
            document = self.__documents.create_new(page_name)
        else:
            document = self.__documents[page_name]

        if page_num is None:
            page_num = len(document)-1
        else:
            page_num = int(page_num)

        page = document[page_num]
        self.__current_document = document
        self.__current_page = page

        edit_page_template = env.get_template('edit_page.html')
        return edit_page_template.render(
            page_name=page_name,
            page_num=page_num,
            total_pages=len(document)
        )

    @cherrypy.expose
    def page_pdf(self, page_name):
        document = self.__documents[page_name]
        cherrypy.response.headers['Content-Type'] = 'application/pdf'
        return document.to_pdf().getvalue()

    @cherrypy.expose
    def undo(self, page_name, page_num):
        page_num = int(page_num)
        document = self.__documents[page_name]
        page = document[page_num]
        page.undo()
        document[self.__current_page.page_num] = page
        document.commit()
        return "ok"

    @cherrypy.expose
    def redo(self, page_name, page_num):
        page_num = int(page_num)
        document = self.__documents[page_name]
        page = document[page_num]
        page.redo()
        document[self.__current_page.page_num] = page
        document.commit()
        return "ok"
    
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def poll(self, page_name, page_num, stroke_idx):
        document = self.__documents[page_name]
        page = document[int(page_num)]
        strokes = page.get_strokes()

        x = 0
        while int(stroke_idx) == len(strokes) and x < 30:
            time.sleep(0.3)
            x += 1
        return strokes

    def append_stroke(self, stroke):
        if self.__current_page:
            self.__current_page.append(stroke)
            self.__current_document[self.__current_page.page_num] = self.__current_page
            self.__current_document.commit()


if __name__ == '__main__':
    APP = [None]

    def run():
        cherrypy.server.socket_host = '0.0.0.0'

        # I'm restricting to a single thread
        # without autoreload to conserve resources.
        #
        # When developing+viewing from multiple browsers
        # it makes sense to disable these lines
        cherrypy.server.thread_pool = 1
        cherrypy.config.update({
            'global': {
                'engine.autoreload.on': False
            }
        })

        APP[0] = App()
        cherrypy.quickstart(APP[0])

    def on_draw_end(stroke):
        stroke = [(x, max(0, y+Y_OFFSET)) for x, y in stroke]
        APP[0].append_stroke(stroke)

    _thread.start_new_thread(run, ())
    w = FullscreenTabletTracker(on_draw_end)
    w.tk.mainloop()
