import bpy, blf
from bgl import glBegin, glVertex2f, glEnd, GL_POLYGON
from script_auto_complete.draw_functions import *

class AutoCompletionManager:
    def __init__(self):
        self._handle = bpy.types.SpaceTextEditor.draw_handler_add(self.draw, (), "WINDOW", "POST_PIXEL")
        self.mouse_position = (0, 0)
        self.cursor_position = getCursorPosition(bpy.context)
        
    def free(self):
        bpy.types.SpaceTextEditor.draw_handler_remove(self._handle, "WINDOW")
        
    def update(self, event):
        self.mouse_position = (event.mouse_region_x, event.mouse_region_y)
        self.cursor_position = getCursorPosition(bpy.context)
        
    def draw(self):    
        self.cursor_position = getCursorPosition(bpy.context)
        x1, y1 = self.cursor_position
        x2, y2 = self.cursor_position
        y1 -= 5
        x2 += 50
        y2 -= 70
        
        draw_rectangle(x1, y1, x2, y2)
        
        #draw_text("Hello", self.cursor_position, 14, align = "LEFT")
        
def getCursorPosition(context):
    space = context.space_data
    region = context.region
    
    visible_lines = space.visible_lines
    top_line_index = space.top
    line_index = space.text.current_line_index
    character_index = space.text.current_character
    
    editor_height = region.height
    
    line_height = editor_height / visible_lines
    character_width = line_height * 0.436
    
    visible_line_index = line_index - top_line_index
    
    return (character_width * character_index, editor_height - line_height * visible_line_index - line_height / 2)
    