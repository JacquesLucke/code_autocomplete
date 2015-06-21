import bpy
import re
from mathutils import Vector
from .. graphics.list_box import ListItem, ListBox
from . exception import BlockEvent
from . event_utils import is_event
from . suggestions import complete
from .. settings import get_settings
import time

move_index_commands = {
    "DOWN_ARROW" : 1,
    "UP_ARROW" : -1,
    "PAGE_DOWN" : 4,
    "PAGE_UP" : -4,
    "END" : 10000,
    "HOME" : -10000 }

text_changing_types = ["BACK_SPACE", "PERIOD", "SPACE", "COMMA", "RET", 
    "ZERO", "ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN", "EIGHT", "NINE",
    "DEL", "SEMI_COLON", "MINUS", "RIGHT_BRACKET", "LEFT_BRACKET", "SLASH"] + \
    list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    
show_types = ["PERIOD", "ZERO", "ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN", "EIGHT", "NINE"] + \
    list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    
hide_types = ["BACK_SPACE", "DEL", "ESC", "RET"] 

    
class AutocompleteHandler:
    def __init__(self):
        self.context_box = ListBox()
        self.completions = []
        self.draw_max = 8
        self.top_index = 0
        self.active_index = 0
        self.reload_completions = False
        self.hide = True
        
    def update(self, event, text_block):        
    
        if (is_event(event, "TAB") or is_event(event, "RET", shift = True)) and not self.hide:
            if len(self.completions) > 0:
                c = self.completions[self.active_index]
                c.insert(text_block)
                self.hide = True
                raise BlockEvent()
                
        self.update_visibility(event, text_block)
        if self.hide: return
          
        if event.value == "PRESS" and event.type in text_changing_types:
            self.reload_completions = True
            
        if len(self.completions) > 0:
            self.move_active_index(event)
            
    def update_visibility(self, event, text_block):
        if self.hide:
            if event.type in show_types and event.value == "PRESS" and not (event.ctrl or event.alt):
                self.show()
            if is_event(event, "ESC", shift = True):
                self.show()
        else:
            if event.type in hide_types and event.value == "PRESS":
                self.hide = True
                
        text = text_block.text_before_cursor
        if is_event(event, "SPACE"): 
            if re.search("[import|from]\s*.?\s*$", text): self.show()
            else: self.hide = True
            
    def show(self):
        self.hide = False
        self.reload_completions = True
                
    def move_active_index(self, event):
        def move_with_keyboard():
            for key, amount in move_index_commands.items():
                if is_event(event, key):
                    self.change_active_index(amount)
                    raise BlockEvent()
        move_with_keyboard()
                
    def change_active_index(self, amount):
        index = self.active_index + amount
        index = min(max(index, 0), len(self.completions) - 1)
        if index < self.top_index:
            self.top_index = index
        if index > self.top_index + self.draw_max - 1:
            self.top_index = index - self.draw_max + 1
        if len(self.completions) < self.draw_max:
            self.top_index = 0
        self.active_index = index
                
    def update_completions(self, text_block):
        self.completions = complete(text_block)
        self.change_active_index(0)
        
    def draw(self, text_block):
        if self.hide: return
        
        if self.reload_completions:
            self.update_completions(text_block)
            self.reload_completions = False
    
        s = get_settings().context_box
        self.context_box.font_size = s.font_size
        self.context_box.line_height = s.line_height
        self.context_box.width = s.width
        self.context_box.padding = s.padding
        self.context_box.position = text_block.current_cursor_region_location
    
        items = []
        for i, c in enumerate(self.completions):
            if not self.top_index <= i < self.top_index + self.draw_max: continue
            item = ListItem(c.name)
            item.active = self.active_index == i
            item.data = c
            item.offset = 10 if c.type == "PARAMETER" else 0
            items.append(item)
            
        self.context_box.items = items
        if len(items) > 0:
            self.context_box.draw()
            
        