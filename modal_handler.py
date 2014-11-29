import bpy, blf
from bgl import glBegin, glVertex2f, glEnd, GL_POLYGON
from script_auto_complete.draw_functions import *
from script_auto_complete.text_editor_utils import *
from script_auto_complete.utils import *

class AutoCompletionManager:
    def __init__(self):
        self._handle = bpy.types.SpaceTextEditor.draw_handler_add(self.draw, (), "WINDOW", "POST_PIXEL")
        self.mouse_position = (0, 0)
        
    def free(self):
        bpy.types.SpaceTextEditor.draw_handler_remove(self._handle, "WINDOW")
        
    def update(self, event):
        self.mouse_position = (event.mouse_region_x, event.mouse_region_y)
        
    def draw(self):    
        textBox = AutoCompleteTextBox()
        textBox.draw()
        
        
class AutoCompleteTextBox:
    def __init__(self):
        editor_info = TextEditorInfo()
        self.editor_info = editor_info
        
    def draw(self):
        scale = self.editor_info.line_height / 20
        
        x, y = self.editor_info.cursor_position
        rectangle = Rectangle(x, y, 200 * scale, 150 * scale)
        rectangle.move_down(7 * scale)
    
        draw_rectangle(rectangle)
        draw_rectangle_border(rectangle, thickness = 5 * scale)
        
        inset = rectangle.get_inset_rectangle(10 * scale)
        draw_rectangle(inset, color = (0.7, 0.2, 0.2, 1.0))
        
        restore_opengl_defaults()
        
    def getCompleteLines(self):
        return ["bpy", "Operator", "Panel", "math"]
