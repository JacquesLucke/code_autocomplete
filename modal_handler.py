import bpy, blf
from bgl import glBegin, glVertex2f, glEnd, GL_POLYGON
from script_auto_complete.draw_functions import *
from script_auto_complete.text_editor_utils import *
from script_auto_complete.utils import *

class AutoCompletionManager:
    def __init__(self):
        self._handle = bpy.types.SpaceTextEditor.draw_handler_add(self.draw, (), "WINDOW", "POST_PIXEL")
        self.auto_complete_box = AutoCompleteTextBox()
        
    def free(self):
        bpy.types.SpaceTextEditor.draw_handler_remove(self._handle, "WINDOW")
        
    def update(self, event):
        event_used = self.auto_complete_box.update(event)
        return event_used
        
    def draw(self):    
        self.auto_complete_box.draw()
        
        
class AutoCompleteTextBox:
    def __init__(self):
        self.selected_index = 0
        self.top_index = 3
        self.line_amount = 8
        
    def update(self, event):
        if event.value == "PRESS":
            if event.type == "DOWN_ARROW":
                self.selected_index += 1
                return True
            if event.type == "UP_ARROW":
                self.selected_index -= 1
                return True
        return False
        
    @property
    def bottom_index(self):
        return self.top_index + self.line_amount - 1
         
    def draw(self):
        editor_info = TextEditorInfo()
        self.editor_info = editor_info
    
        scale = self.editor_info.line_height / 20
        
        padding = 8 * scale
        element_height = 21 * scale
        real_element_height = 20 * scale
        text_size = 100 * scale
        border_thickness = 3 * scale
        
        x, y = self.editor_info.cursor_position
        rectangle = Rectangle(x, y, 200 * scale, self.line_amount * element_height + 2 * padding)
        rectangle.move_down(7 * scale)
    
        draw_rectangle(rectangle)
        
        inner_rectangle = rectangle.get_inset_rectangle(padding)
        
        elements = self.get_complete_line_amount()
        self.correct_index(elements)
        for i, line in enumerate(elements):
            if i >= self.top_index and i < self.top_index + self.line_amount:
                index = i - self.top_index
                text_rectangle = Rectangle(inner_rectangle.left, inner_rectangle.top - index*element_height, inner_rectangle.width, real_element_height)
                if i == self.selected_index:
                    highlight_rectangle = Rectangle(rectangle.left, rectangle.top - index*element_height - element_height / 4, rectangle.width, element_height)
                    draw_rectangle(highlight_rectangle, color = (0.95, 0.95, 0.95, 1.0))
                draw_text_on_rectangle(line, text_rectangle, size = text_size)
        
        draw_rectangle_border(rectangle, thickness = border_thickness)
        restore_opengl_defaults()
        
    def correct_index(self, elements):
        amount = len(elements)
        self.selected_index = clamp(self.selected_index, 0, amount - 1)
        self.top_index = clamp(self.top_index, 0, amount - 1)
        self.top_index = clamp(self.top_index, self.selected_index - self.line_amount + 1, self.selected_index)
        
        
        
        
    def get_complete_line_amount(self):
        return ["bpy", "Operator", "Panel", "math", "context", "active_object", "modifiers", "constraints", "name", "object", "event", "draw"]
        
def clamp(value, min_value, max_value):
    return min(max(value, min_value), max_value)
