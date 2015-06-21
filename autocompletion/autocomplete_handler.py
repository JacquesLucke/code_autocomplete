import bpy
from mathutils import Vector
from .. graphics.rectangle import Rectangle
from . exception import BlockEvent
from . event_utils import is_event
from . suggestions import complete
import time

class AutocompleteHandler:
    def __init__(self):
        self.completions = []
        self.draw_max = 8
        self.top_index = 0
        self.active_index = 3
        
    def update(self, event, text_block):
        text = text_block.text_before_cursor
        
        if is_event(event, "DOWN_ARROW"): 
            self.active_index += 1
            raise BlockEvent()
        if is_event(event, "UP_ARROW", "RELEASE"):
            self.active_index -= 1
            raise BlockEvent()
        
        if event.value == "RELEASE" and event.type not in ("MOUSEMOVE", "INBETWEEN_MOUSEMOVE"):
            changed = False
            if len(text) > 0:
                c = text[-1]
                if c.isalpha() or c in "._" or text.endswith("import "):
                    self.update_completions(text_block)
                    changed = True
                    
            if not changed:
                self.completions = []
                
    def update_completions(self, text_block):
        self.completions = complete(text_block)
        
    def draw(self, text_block):
        items = []
        for i, c in enumerate(self.completions):
            if not self.top_index <= i < self.top_index + self.draw_max: continue
            item = ListItem(c.name)
            item.active = self.active_index == i
            items.append(item)
        if len(items) > 0:
            draw_list(items, Vector((200, 300)))
        
   
import blf
from bgl import *   
   
font = 1   
def draw_list(items, position, width = 200, line_spacing = 23, character_size = 80, padding = 5):
    blf.size(font, character_size, 12)
    
    height = len(items) * line_spacing + padding
    
    background = Rectangle(position.x, position.y, position.x + width, position.y - height)
    background.border_thickness = -1
    background.color = (1.0, 1.0, 1.0, 1.0)
    background.border_color = (0.9, 0.76, 0.4, 1.0)
    background.draw()
    
    offset_to_center = blf.dimensions(font, "i")[1] / 2
    
    for i, item in enumerate(items):
        y = position.y - i * line_spacing - padding / 2
        rec = Rectangle(background.left, y, background.right, y - line_spacing)
        rec.color = (0.93, 0.93, 0.93, 1.0)
        rec.border_color = (1.0, 0.8, 0.5, 1.0)
        rec.border_thickness = 1
        if item.active:
            rec.draw()
            
        glColor4f(0.1, 0.1, 0.1, 1.0)
        blf.position(font, position.x + padding, rec.center_y - offset_to_center, 0)
        blf.draw(font, item.text)
        
class ListItem:
    def __init__(self, text):
        self.text = text
        self.active = False
        self.alignment = "LEFT"