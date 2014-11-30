import bpy, re, keyword
from bgl import glBegin, glVertex2f, glEnd, GL_POLYGON
from script_auto_complete.draw_functions import *
from script_auto_complete.text_editor_utils import *
from script_auto_complete.utils import *
from script_auto_complete.operators.operator_hub import *
from script_auto_complete.operators.extend_word_operators import *


show_event_types = ["PERIOD"] + list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
hide_event_types = ["RET", "LEFTMOUSE", "LEFT_ARROW", "RIGHT_ARROW"]

class AutoCompletionManager:
    def __init__(self):
        self._handle = bpy.types.SpaceTextEditor.draw_handler_add(self.draw, (), "WINDOW", "POST_PIXEL")
        self.auto_complete_box = AutoCompleteTextBox()
        
    def free(self):
        bpy.types.SpaceTextEditor.draw_handler_remove(self._handle, "WINDOW")
        
    def update(self, event):
        event_used = False
        event_used = self.auto_complete_box.update(event) or event_used
        
        if not event_used:
            if event.type in show_event_types and event.value == "PRESS" and is_event_current_region(event):
                self.auto_complete_box.hide = False
                self.auto_complete_box.selected_index = 0
                update_word_list()
            if event.type in hide_event_types:
                self.auto_complete_box.hide = True
        
        return event_used
        
    def draw(self):    
        self.auto_complete_box.draw()
        
        
class AutoCompleteTextBox:
    def __init__(self):
        self.selected_index = 0
        self.top_index = 3
        self.line_amount = 8
        
        self.hide = True
        
    def update(self, event):
        if not is_event_current_region(event):
            self.hide = True
        if self.hide: return False
        
        if event.value == "PRESS":
            if event.type == "DOWN_ARROW":
                self.selected_index += 1
                return True
            if event.type == "UP_ARROW":
                self.selected_index -= 1
                return True
            if event.type == "TAB":
                self.execute_selected_operator()
                self.hide = True
                return True
        
        if event.type in ["MOUSEMOVE", "LEFTMOUSE"]:
            editor_info = TextEditorInfo()
            line_rectangles = self.get_draw_rectangles(editor_info)[2]
            for i, line_rectangle in enumerate(line_rectangles):
                if line_rectangle.contains(event.mouse_region_x, event.mouse_region_y):
                    self.selected_index = self.top_index + i
                    if event.value == "PRESS" and event.type == "LEFTMOUSE":
                        self.execute_selected_operator()
                        self.hide = True
                    return True
        return False
        
    def execute_selected_operator(self):
        try:
            operator = self.selected_operator
            operator.execute(bpy.context.space_data.text)
        except: pass
        
    @property
    def bottom_index(self):
        return self.top_index + get_line_amount() - 1
         
    def draw(self):
        if self.hide: return
        
        editor_info = TextEditorInfo()
        scale = editor_info.scale
        text_size = 100 * scale
        border_thickness = 3 * scale
        
        box_rectangle, inner_rectangle, line_rectangles, text_rectangles = self.get_draw_rectangles(editor_info)
    
        draw_rectangle(box_rectangle)
        
        operators = get_text_operators()
        self.correct_index(len(operators))
        for i, operator in enumerate(operators):
            if i < self.top_index or i > self.bottom_index: continue
            
            index = i - self.top_index
            if i == self.selected_index:
                draw_rectangle(line_rectangles[index], color = (0.95, 0.95, 0.95, 1.0))
            draw_text_on_rectangle(operator.display_name, text_rectangles[index], size = text_size, align = operator.align)
        
        draw_rectangle_border(box_rectangle, thickness = border_thickness)
        restore_opengl_defaults()
        
    def get_draw_rectangles(self, editor_info):
        scale = editor_info.scale
        
        padding = 8 * scale
        element_height = 21 * scale
        real_element_height = 20 * scale
        box_width = 200 * scale
        move_down_distance = 10 * scale
        
        x, y = editor_info.cursor_position
        # the box in which the operators are displayed
        box_rectangle = Rectangle(x, y, box_width, get_line_amount() * element_height + 2 * padding)
        box_rectangle.move_down(move_down_distance)
        
        # box rectangle with applied padding, to get a few pixels between the text and the border line
        inner_rectangle = box_rectangle.get_inset_rectangle(padding)
        
        line_rectangles = []
        text_rectangles = []
        for i in range(get_line_amount()):
            # rectangle that is drawn to highlight this operator
            line_rectangles.append(Rectangle(
                box_rectangle.left,
                box_rectangle.top - i*element_height - element_height / 4,
                box_rectangle.width,
                element_height))
            # rectangle to draw the text in
            text_rectangles.append(Rectangle(
                inner_rectangle.left,
                inner_rectangle.top - i*element_height,
                inner_rectangle.width,
                real_element_height))
                
        return box_rectangle, inner_rectangle, line_rectangles, text_rectangles
      
    @property
    def selected_operator(self):
        operators = get_text_operators()
        self.correct_index(len(operators))
        try: return operators[self.selected_index]
        except: return None
        
    def correct_index(self, amount):
        self.selected_index = clamp(self.selected_index, 0, amount - 1)
        self.top_index = clamp(self.top_index, 0, amount - 1)
        self.top_index = clamp(self.top_index, self.selected_index - get_line_amount() + 1, self.selected_index)
      
def get_line_amount():
    return get_addon_preferences().line_amount
def get_addon_preferences():
    return bpy.context.user_preferences.addons["script_auto_complete"].preferences
    
def is_event_current_region(event):
    region = bpy.context.region
    viewport = Rectangle(0, region.height, region.width, region.height)
    return viewport.contains(event.mouse_region_x, event.mouse_region_y)
