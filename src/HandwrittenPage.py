import copy
from PIL import Image, ImageDraw

from constants import RESOLUTION


class HandwrittenPage:
    def __init__(self, strokes=None):
        self.__strokes = strokes or []

    def get_strokes(self):
        return copy.deepcopy(self.__strokes)

    def get_image(self):
        im = Image.new(mode='RGB', size=RESOLUTION, color=255)
        draw = ImageDraw.Draw(im)
        draw.line(self.__strokes, outline=0, width=3)
        draw.ellipse(self.__strokes[0], fill=(255, 0, 0), width=3)
        draw.ellipse(self.__strokes[-1], fill=(0, 0, 255), width=5)
        return im

    def append(self, stroke):
        self.__strokes.append(stroke)

    def insert(self, idx, stroke):
        self.__strokes.insert(idx, stroke)
