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
        im = Image.new(mode='RGB', size=RESOLUTION, color=255)
        draw = ImageDraw.Draw(im)
        draw.line(self.__strokes, outline=0, width=3)
        draw.ellipse(self.__strokes[0], fill=(255, 0, 0), width=3)
        draw.ellipse(self.__strokes[-1], fill=(0, 0, 255), width=5)
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
