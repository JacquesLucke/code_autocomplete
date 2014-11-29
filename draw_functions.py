import bpy, blf
from bgl import glBegin, glVertex2f, glEnd, GL_POLYGON, glEnable, glDisable, GL_POLYGON_SMOOTH, GL_BLEND, glColor4f

def draw_rectangle(rectangle, color = (0.8, 0.8, 0.8, 1.0)):
    glColor4f(*color)
    
    glBegin(GL_POLYGON)
    glVertex2f(rectangle.left, rectangle.top)
    glVertex2f(rectangle.right, rectangle.top)
    glVertex2f(rectangle.right, rectangle.bottom)
    glVertex2f(rectangle.left, rectangle.bottom)
    glEnd()
  
font_id = 1 
def draw_text(text = "", position = (0, 0), size = 20, horizontal_align = "CENTER", vertical_align = "BOTTOM", color = (0.2, 0.2, 0.2, 1.0)):
    glColor4f(*color)
    blf.size(font_id, int(size), 72)
    dimensions = blf.dimensions(font_id, text)
    
    if horizontal_align == "CENTER":
        position = (position[0] - dimensions[0] / 2, position[1] - dimensions[1] / 2)
    if vertical_align == "TOP":
        position = (position[0], position[1] - dimensions[1])
        
    blf.position(font_id, position[0], position[1], 0)
    blf.draw(font_id, text)
    