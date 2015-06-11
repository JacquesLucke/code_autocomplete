from bgl import *

class Rectangle:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.color = (0.8, 0.8, 0.8, 1.0)
        self.border_color = (0.1, 0.1, 0.1, 1.0)
        self.border_thickness = 0

    @property
    def width(self):
        return abs(self.x1 - self.x2)

    @property
    def height(self):
        return abs(self.y1 - self.y2)

    @property
    def left(self):
        return min(self.x1, self.x2)

    @property
    def bottom(self):
        return min(self.y1, self.y2)

    @property
    def center_y(self):
        return (self.y1 + self.y2) / 2

    def draw(self):
        glColor4f(*self.color)
        glEnable(GL_BLEND)
        glBegin(GL_POLYGON)
        glVertex2f(self.x1, self.y1)
        glVertex2f(self.x2, self.y1)
        glVertex2f(self.x2, self.y2)
        glVertex2f(self.x1, self.y2)
        glEnd()

        if self.border_thickness != 0:
            self.drawBorder()

    def drawBorder(self):
        thickness = self.border_thickness
        thickness = min(abs(self.x1 - self.x2) / 2, abs(self.y1 - self.y2) / 2, thickness)
        left, right = sorted([self.x1, self.x2])
        bottom, top = sorted([self.y1, self.y2])

        if thickness > 0:
            topBorder = Rectangle(left, top, right, top - thickness)
            bottomBorder = Rectangle(left, bottom + thickness, right, bottom)
        else:
            topBorder = Rectangle(left + thickness, top, right - thickness, top - thickness)
            bottomBorder = Rectangle(left + thickness, bottom + thickness, right - thickness, bottom)
        leftBorder = Rectangle(left, top, left + thickness, bottom)
        rightBorder = Rectangle(right - thickness, top, right, bottom)

        for border in (topBorder, bottomBorder, leftBorder, rightBorder):
            border.color = self.border_color
            border.draw()