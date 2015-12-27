import blf
from bgl import *
from . utils import getDpi
from mathutils import Vector
from . rectangle import Rectangle

class ListItem:
    def __init__(self, text):
        self.text = text
        self.active = False
        self.alignment = "LEFT"
        self.data = None
        self.offset = 0


class ListBox:
    def __init__(self):
        self.items = []
        self.position = Vector((0, 0))
        self.width = 200
        self.line_height = 23
        self.font_size = 8
        self.padding = 5
        self.font = 1
        self.background_color = (1.0, 1.0, 1.0, 1.0)
        self.background_border_color = (0.9, 0.76, 0.4, 1.0)
        self.text_color = (0.1, 0.1, 0.1, 1.0)
        self.active_item_color = (0.95, 0.95, 1.0, 1.0)
        self.active_item_border_color = (1.0, 0.8, 0.5, 1.0)
        self.calc_height()

    def contains(self, point):
        background = self.get_background_rectangle()
        return background.contains(point)

    def get_item_under_point(self, point):
        for i, item in enumerate(self.items):
            rec = self.get_item_rectangle(i)
            if rec.contains(point): return item

    def draw(self):
        self.calc_height()
        self.draw_background()
        self.draw_items()

    def draw_background(self):
        background = self.get_background_rectangle()
        background.draw()

    def get_background_rectangle(self):
        self.calc_height()

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
        self.height = len(self.items) * self.line_height + self.padding

    def draw_items(self):
        for index in range(len(self.items)):
            self.draw_item(index)

    def draw_item(self, index):
        item = self.items[index]
        item_rec = self.get_item_rectangle(index)
        if item.active:
            item_rec.draw()
        self.draw_item_in_rectangle(item, item_rec)

    def get_item_rectangle(self, index):
        item_rec = Rectangle()
        item_rec.x1 = self.position.x
        item_rec.y1 = self.position.y - index * self.line_height - self.padding / 2
        item_rec.x2 = self.position.x + self.width
        item_rec.y2 = item_rec.y1 - self.line_height
        item_rec.color = self.active_item_color
        item_rec.border_color = self.active_item_border_color
        item_rec.border_thickness = -1
        return item_rec

    def draw_item_in_rectangle(self, item, rectangle):
        glColor4f(*self.text_color)
        blf.size(self.font, self.font_size, int(getDpi()))

        if item.alignment == "LEFT":
            x = rectangle.left + self.padding
        if item.alignment == "CENTER":
            x = rectangle.center.x - blf.dimensions(self.font, item.text)[0] / 2
        x += item.offset

        offset = blf.dimensions(self.font, "i")[1] / 2

        blf.position(self.font, x, rectangle.center.y - offset, 0)
        blf.draw(self.font, item.text)
