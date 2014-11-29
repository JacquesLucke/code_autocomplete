import bpy, blf
from bgl import glBegin, glVertex2f, glEnd, GL_POLYGON
from script_auto_complete.draw_functions import *
from script_auto_complete.text_editor_utils import *

class AutoCompletionManager:
    def __init__(self):
        self._handle = bpy.types.SpaceTextEditor.draw_handler_add(self.draw, (), "WINDOW", "POST_PIXEL")
        self.mouse_position = (0, 0)
        
    def free(self):
        bpy.types.SpaceTextEditor.draw_handler_remove(self._handle, "WINDOW")
        
    def update(self, event):
        self.mouse_position = (event.mouse_region_x, event.mouse_region_y)
        
    def draw(self):    
        editor_info = TextEditorInfo()
        
        x1, y1 = editor_info.cursor_position
        x2, y2 = editor_info.cursor_position
        y1 -= editor_info.line_height
        x2 += editor_info.character_width * 25
        y2 -= editor_info.line_height * 10
        
        draw_rectangle(x1, y1, x2, y2)
        
        #draw_text("Hello", self.cursor_position, 14, align = "LEFT")
