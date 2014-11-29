import bpy, blf
from bgl import glBegin, glVertex2f, glEnd, GL_POLYGON, glEnable, glDisable, GL_POLYGON_SMOOTH, GL_BLEND, glColor4f, GL_LINE_STRIP, glLineWidth, GL_LINES

def draw_rectangle(rectangle, color = (0.8, 0.8, 0.8, 1.0)):
    glColor4f(*color)
    
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
def draw_text_on_rectangle(text, rectangle, color = (0.2, 0.2, 0.2, 1.0), size = 20):
    draw_text(text, position = (rectangle.left, rectangle.bottom + rectangle.height / 3), size = size, horizontal_align = "LEFT", vertical_align = "BOTTOM")

def draw_text(text = "", position = (0, 0), size = 20, horizontal_align = "CENTER", vertical_align = "BOTTOM", color = (0.2, 0.2, 0.2, 1.0)):
    glColor4f(*color)
    blf.size(font_id, int(size), 12)
    dimensions = blf.dimensions(font_id, text)
    
    if horizontal_align == "CENTER":
        position = (position[0] - dimensions[0] / 2, position[1] - dimensions[1] / 2)
    if vertical_align == "TOP":
        position = (position[0], position[1] - dimensions[1])
        
    blf.position(font_id, int(position[0]), int(position[1]), 0)
    blf.draw(font_id, text)
    
    
def restore_opengl_defaults():
    glLineWidth(1)
    glDisable(GL_BLEND)
    glColor4f(0.0, 0.0, 0.0, 1.0)
    
    blf.disable(font_id, blf.ROTATION)
    blf.disable(font_id, blf.SHADOW)
    blf.disable(font_id, blf.KERNING_DEFAULT)
    