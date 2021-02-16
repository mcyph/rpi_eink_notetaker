import time
import _thread
import cherrypy
from jinja2 import Environment, FileSystemLoader

from HandwrittenDocuments import HandwrittenDocuments
from FullscreenTabletTracker import FullscreenTabletTracker
from FramebufferStrokeDisplay import FramebufferStrokeDisplay


env = Environment(loader=FileSystemLoader(searchpath='./template'),
                  autoescape=True)
Y_OFFSET_TOP = -20
Y_SCALE_FACTOR = 1.1


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

        fb_stroke_display.clear()
        fb_stroke_display.draw(self.__current_page.get_strokes(), [0, 0])
        fb_stroke_display.update()

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
    def four_page_pdf(self, page_name):
        document = self.__documents[page_name]
        cherrypy.response.headers['Content-Type'] = 'application/pdf'
        return document.to_pdf_4_to_page().getvalue()

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
        return page.get_strokes()

    def append_stroke(self, documents, stroke):
        #print("SENDING:", self.__current_page, stroke)
        if self.__current_page:
            # Can't use the instance of "HandwrittenDocument"
            # as the SQLite connection isn't threadsafe!
            current_document = documents[self.__current_document.name]
            current_page = current_document[self.__current_page.page_num]

            current_page.append(stroke)
            self.__current_page.append(stroke)  # sync in other thread, too
            current_document[current_page.page_num] = current_page
            current_document.commit()

            return current_page

    def get_strokes(self):
        current_page = self.__current_page
        if current_page:
            return current_page.get_strokes()
        else:
            return None


if __name__ == '__main__':
    APP = [None]
    DOCUMENTS = [None]

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
        DOCUMENTS[0] = HandwrittenDocuments()
        cherrypy.quickstart(APP[0])

    print("CREATING FB STROKE DISPLAY!")
    fb_stroke_display = FramebufferStrokeDisplay()
    print("CREATE OK - RUNNING SERVER!")
    _thread.start_new_thread(run, ())

    def on_draw_end(stroke):
        stroke = [(x, max(0, y+Y_OFFSET_TOP)) for x, y in stroke]
        stroke = [(x, y*Y_SCALE_FACTOR) for x, y in stroke]
        current_page = APP[0].append_stroke(DOCUMENTS[0], stroke)

    def on_motion(x, y):
        strokes = APP[0].get_strokes() or []
        fb_stroke_display.draw(strokes, [x, y])
        fb_stroke_display.update()

    print("RUNNING TABLET TRACKER!")
    w = FullscreenTabletTracker(on_draw_end, on_motion)
    w.tk.mainloop()
