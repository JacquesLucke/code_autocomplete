import bpy
from mathutils import Vector
from .. graphics.list_box import ListItem, ListBox
from . exception import BlockEvent
from . event_utils import is_event
from . suggestions import complete
from .. settings import get_settings
import time

class AutocompleteHandler:
    def __init__(self):
        self.context_box = ListBox()
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
        s = get_settings().context_box
        self.context_box.font_size = s.font_size
        self.context_box.line_height = s.line_height
        self.context_box.width = s.width
        self.context_box.padding = s.padding
        self.context_box.position = Vector((200, 300))
    
        items = []
        for i, c in enumerate(self.completions):
            if not self.top_index <= i < self.top_index + self.draw_max: continue
            item = ListItem(c.name)
            item.active = self.active_index == i
            items.append(item)
            
        self.context_box.items = items
        self.context_box.draw()
            
        