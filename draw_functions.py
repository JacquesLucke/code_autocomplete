import bpy, blf
from bgl import glBegin, glVertex2f, glEnd, GL_POLYGON, glEnable, glDisable, GL_POLYGON_SMOOTH, GL_BLEND, glColor4f

def draw_rectangle(x1, y1, x2, y2, color = (0.8, 0.8, 0.8, 1.0)):
    glColor4f(*color)
    glEnable(GL_BLEND)
    
    glBegin(GL_POLYGON)
    glVertex2f(x1, y1)
    glVertex2f(x2, y1)
    glVertex2f(x2, y2)
    glVertex2f(x1, y2)
    glEnd()
    
    glDisable(GL_BLEND)
  
font_id = 0  
def draw_text(text = "", position = (0, 0), size = 20, align = "CENTER", color = (0.2, 0.2, 0.2, 1.0)):
    glColor4f(*color)
    blf.size(font_id, size, 72)
    dimensions = blf.dimensions(font_id, text)
    
    if align == "CENTER":
        position = (position[0] - dimensions[0] / 2, position[1] - dimensions[1] / 2)
        
    blf.position(font_id, position[0], position[1], 0)
    blf.draw(font_id, text)
    