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
        
        line_amount = 8
        padding = 8 * scale
        element_height = 21 * scale
        real_element_height = 20 * scale
        
        x, y = self.editor_info.cursor_position
        rectangle = Rectangle(x, y, 200 * scale, line_amount * element_height + 2 * padding)
        rectangle.move_down(7 * scale)
    
        draw_rectangle(rectangle)
        draw_rectangle_border(rectangle, thickness = 5 * scale)
        
        inner_rectangle = rectangle.get_inset_rectangle(padding)
        
        elements = self.get_complete_line_amount()[:line_amount]
        for i, line in enumerate(elements):
            rectangle = Rectangle(inner_rectangle.left, inner_rectangle.top - i*element_height, inner_rectangle.width, real_element_height)
            draw_rectangle(rectangle, color = (0.2, 0.3, 0.5, 1.0))
        
        restore_opengl_defaults()
        
    def get_complete_line_amount(self):
        return ["bpy", "Operator", "Panel", "math", "context", "active_object", "modifiers", "constraints"]
