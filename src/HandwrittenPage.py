import copy
from PIL import Image, ImageDraw

from constants import RESOLUTION


class HandwrittenPage:
    def __init__(self, page_num, strokes=None):
        self.page_num = page_num
        self.__strokes = strokes or []
        self.undo_index = len(self.__strokes)

    def get_strokes(self):
        return copy.deepcopy(self.__strokes[:self.undo_index])

    def get_image(self):
        im = Image.new(mode='RGB', size=RESOLUTION, color=(255, 255, 255))
        draw = ImageDraw.Draw(im)
        for stroke in self.__strokes:
            stroke = tuple([tuple(i) for i in stroke])
            draw.line(stroke, width=3, fill=(0, 0, 0))
            draw.ellipse((stroke[0][0]-2, stroke[0][1]-2, stroke[0][0]+2, stroke[0][1]+2), fill=(0, 0, 120))
            draw.ellipse((stroke[-1][0]-3, stroke[-1][1]-3, stroke[-1][0]+3, stroke[-1][1]+3), fill=(120, 0, 0))
        return im

    def undo(self):
        self.undo_index = self.undo_index-1
        if self.undo_index < 0:
            self.undo_index = 0

    def redo(self):
        self.undo_index = self.undo_index+1
        if self.undo_index > len(self.__strokes):
            self.undo_index -= 1

    def append(self, stroke):
        # TODO: make
        self.__strokes = self.__strokes[:self.undo_index]
        self.__strokes.append(stroke)
        self.undo_index = len(self.__strokes)

    def insert(self, idx, stroke):
        self.__strokes = self.__strokes[:self.undo_index]
        self.__strokes.insert(idx, stroke)
        self.undo_index = len(self.__strokes)
