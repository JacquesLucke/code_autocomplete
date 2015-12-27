import blf
import textwrap
from bgl import *
from . utils import getDpi
from mathutils import Vector
from . rectangle import Rectangle

class TextBox:
    def __init__(self):
        self.text = ""
        self.position = Vector((0, 0))
        self.width = 400
        self.background_color = (1.0, 1.0, 1.0, 1.0)
        self.background_border_color = (0.9, 0.76, 0.4, 1.0)
        self.text_color = (0.1, 0.1, 0.1, 1.0)
        self.font_size = 8
        self.font = 1
        self.line_height = 23
        self.padding = 5

    def draw(self):
        blf.size(self.font, self.font_size, int(getDpi()))

        self.calc_lines()
        background = self.get_background_rectangle()
        background.draw()

        glColor4f(*self.text_color)
        pos = self.position.copy()
        pos.x += self.padding
        pos.y -= self.padding - self.line_height / 2
        pos.y -= blf.dimensions(self.font, "i")[1] / 2
        for i, line in enumerate(self.lines):
            pos.y -= self.line_height
            blf.position(self.font, pos.x, pos.y, 0)
            blf.draw(self.font, line)

    def calc_lines(self):
        lines = self.text.split("\n")
        while len(lines) > 0:
            if lines[-1] != "": break
            del lines[-1]

        self.lines = lines

    def get_background_rectangle(self):
        self.calc_height()
        self.calc_width()
        background = Rectangle(
            x1 = self.position.x,
            y1 = self.position.y,
            x2 = self.position.x + self.width,
            y2 = self.position.y - self.height )
        background.border_thickness = -1
        background.color = self.background_color
        background.border_color = self.background_border_color
        return background

    def calc_height(self):
        self.height = 2 * self.padding + self.line_height * len(self.lines)

    def calc_width(self):
        widths = [blf.dimensions(self.font, line)[0] for line in self.lines]
        self.width = max(widths) + 2 * self.padding
