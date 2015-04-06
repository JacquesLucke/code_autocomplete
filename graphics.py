import bpy, blf
from bgl import glBegin, glVertex2f, glEnd, GL_POLYGON, glEnable, glDisable, GL_POLYGON_SMOOTH, GL_BLEND, glColor4f, GL_LINE_STRIP, glLineWidth, GL_LINES, glViewport

def draw_rectangle(rectangle, color = (0.8, 0.8, 0.8, 1.0)):
    glColor4f(*color)
    glEnable(GL_BLEND)
    glBegin(GL_POLYGON)
    glVertex2f(rectangle.left, rectangle.top)
    glVertex2f(rectangle.right, rectangle.top)
    glVertex2f(rectangle.right, rectangle.bottom)
    glVertex2f(rectangle.left, rectangle.bottom)
    glEnd()
    
def draw_rectangle_border(rectangle, thickness = 1, color = (0.1, 0.1, 0.1, 1.0)):
    glColor4f(*color)
    
    d = thickness / 2.5
    
    glLineWidth(thickness)
    glBegin(GL_LINES)
    
    glVertex2f(rectangle.left - d, rectangle.top)
    glVertex2f(rectangle.right + d, rectangle.top)
    
    glVertex2f(rectangle.right, rectangle.top + d)
    glVertex2f(rectangle.right, rectangle.bottom - d)
    
    glVertex2f(rectangle.right + d, rectangle.bottom)
    glVertex2f(rectangle.left - d, rectangle.bottom)
    
    glVertex2f(rectangle.left, rectangle.bottom - d)
    glVertex2f(rectangle.left, rectangle.top + d)
    glEnd()
  
font_id = 1 
def draw_text_on_rectangle(text, rectangle, color = (0.2, 0.2, 0.2, 1.0), size = 20, align = "LEFT"):
    position = (rectangle.left, rectangle.bottom + rectangle.height / 3)
    if align == "CENTER":
        center = rectangle.center
        position = (center[0], rectangle.bottom + rectangle.height / 3)
    draw_text(text, position, size = size, horizontal_align = align, vertical_align = "BOTTOM")

def draw_text(text = "", position = (0, 0), size = 200, horizontal_align = "LEFT", vertical_align = "BOTTOM", color = (0.2, 0.2, 0.2, 1.0), font_id = font_id):
    
    set_text_size(size, font_id)
    dimensions = blf.dimensions(font_id, text)
    
    if horizontal_align == "CENTER":
        position = (position[0] - dimensions[0] / 2, position[1])
    if vertical_align == "TOP":
        position = (position[0], position[1] - dimensions[1])
    glColor4f(*color)    
    blf.position(font_id, int(position[0]), int(position[1]), 0)
    blf.draw(font_id, text)

def get_text_dimensions(text, size, font_id = font_id):
    set_text_size(size, font_id = font_id)
    return blf.dimensions(font_id, text)
    
def set_text_size(size, font_id = font_id):
    blf.size(font_id, int(size), 12)

   
def restore_opengl_defaults():
    glLineWidth(1)
    glDisable(GL_BLEND)
    glColor4f(0.0, 0.0, 0.0, 1.0)
    
class Rectangle:
    # (x, y) is the top left corner
    def __init__(self, x, y, width, height):
        self.left = x
        self.right = x + width
        self.top = y
        self.bottom = y - height
        
    def move_down(self, amount):
        self.top -= amount
        self.bottom -= amount
        
    @property
    def width(self):
        return self.right - self.left
    @property
    def height(self):
        return self.top - self.bottom
        
    @property
    def center(self):
        return [(self.left+self.right) / 2, (self.top+self.bottom) / 2]
        
    @property
    def top_left(self):
        return [self.left, self.top]
        
    def contains(self, x, y):
        return self.left <= x <= self.right and self.top >= y >= self.bottom
        
    def get_inset_rectangle(self, border):
        return Rectangle(self.left + border, self.top - border, self.width - 2*border, self.height - 2*border)
        
    def __repr__(self):
        return "(Left: "+str(self.left)+", Right: "+str(self.right)+", Top: "+str(self.top)+", Bottom: "+str(self.bottom)+")"
    
class Label:
    def __init__(self):
        self.text = ""
        self.width = 1000
        self.max_lines = 1
        self.text_size = 100
        self.line_height = 15
        self.color = (0.2, 0.2, 0.2, 1.0)
        self.font_id = 0
        
    def draw(self, position):
        lines = self.get_draw_lines()
        for i, line in enumerate(lines):
            line_start_position = (position[0], position[1] - i * self.line_height)
            draw_text(line, line_start_position, size = self.text_size, color = self.color, font_id = self.font_id)
            
    def get_draw_dimensions(self):
        lines = self.get_draw_lines()
        width = 0
        for line in lines:
            width = max(width, self.get_text_width(line))
        height = len(lines) * self.line_height
        return width, height
        
    def get_draw_lines(self):
        text_lines = self.get_wrapped_lines()
        draw_lines = text_lines[:self.max_lines]
        
        if len(text_lines) > self.max_lines:
            last_line = draw_lines[-1] + "..."
            if self.fits_in_line(last_line):
                draw_lines[-1] = last_line
            else: draw_lines[-1] = draw_lines[-1][:-3] + "..."
        
        return draw_lines
        
    def get_wrapped_lines(self):
        lines = []
        text = self.text
        while text != "":
            next_line = self.get_text_to_line_end(text)
            lines.append(next_line)
            text = text[len(next_line):]
            
        for i in range(1, len(lines)):
            lines[i] = lines[i].strip()
        return lines
            
    def get_text_to_line_end(self, text):
        index = 1
        fitting_index = 30
        while index > 0:
            index = text.find(" ", index + 1)
            if self.fits_in_line(text[:index]):
                fitting_index = index
            else:
                return text[:fitting_index]
        return text
        
    def fits_in_line(self, text):
        return self.get_text_width(text) <= self.width
    def get_text_width(self, text):
        return get_text_dimensions(text, self.text_size, font_id = self.font_id)[0]
    