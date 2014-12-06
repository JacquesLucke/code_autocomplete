import bpy, blf
from bgl import glBegin, glVertex2f, glEnd, GL_POLYGON, glEnable, glDisable, GL_POLYGON_SMOOTH, GL_BLEND, glColor4f, GL_LINE_STRIP, glLineWidth, GL_LINES

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

def draw_text(text = "", position = (0, 0), size = 20, horizontal_align = "LEFT", vertical_align = "BOTTOM", color = (0.2, 0.2, 0.2, 1.0)):
    glColor4f(*color)
    set_text_size(size)
    dimensions = blf.dimensions(font_id, text)
    
    if horizontal_align == "CENTER":
        position = (position[0] - dimensions[0] / 2, position[1])
    if vertical_align == "TOP":
        position = (position[0], position[1] - dimensions[1])
        
    blf.position(font_id, int(position[0]), int(position[1]), 0)
    blf.draw(font_id, text)
    
def get_text_dimensions(text, size, font_id = font_id):
    set_text_size(size)
    return blf.dimensions(font_id, text)
    
def set_text_size(size, font_id = font_id):
    blf.size(font_id, int(size), 12)
    
def get_text_lines(text, size, width, font_id = font_id):
    lines = []
    while text != "":
        next_line = get_next_line(text, size, width, font_id)
        lines.append(next_line.strip())
        text = text[(len(next_line)):]
            
    return lines
   
def get_next_line(text, size, width, font_id = font_id):
    index = 0
    fitting_index = 0
    while index > -1:
        index = text.find(" ", index + 1)
        subtext = text[:index]
        dimensions = get_text_dimensions(subtext, size, font_id)
        if dimensions[0] <= width:
            fitting_index = index
        else:
            return text[:fitting_index]
    return text
   
def restore_opengl_defaults():
    glLineWidth(1)
    glDisable(GL_BLEND)
    glColor4f(0.0, 0.0, 0.0, 1.0)
    
    blf.disable(font_id, blf.ROTATION)
    blf.disable(font_id, blf.SHADOW)
    blf.disable(font_id, blf.KERNING_DEFAULT)
    