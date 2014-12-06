import bpy, re, keyword
from bgl import glBegin, glVertex2f, glEnd, GL_POLYGON
from script_auto_complete.draw_functions import *
from script_auto_complete.text_editor_utils import *
from script_auto_complete.utils import *
from script_auto_complete.operators.operator_hub import *
from script_auto_complete.operators.extend_word_operators import *
from script_auto_complete.documentation import *


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
        self.operator_line_rectangles = []
        
        self.hide = True
        
    def update(self, event):
        if self.hide or not is_event_current_region(event): return False
        
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
        if event.type in ["LEFTMOUSE", "MOUSEMOVE"] and event.value in ["PRESS", "RELEASE"]:
            for i, line_rectangle in enumerate(self.operator_line_rectangles):
                if line_rectangle.contains(event.mouse_region_x, event.mouse_region_y):
                    index = self.top_index + i
                    if self.selected_index == index and event.type == "LEFTMOUSE" and event.value == "RELEASE":
                        self.execute_selected_operator()
                        self.hide = True
                    else:
                        if event.value == "PRESS":
                            self.selected_index = index
                    return True
        if self.operator_box_rectangle.contains(event.mouse_region_x, event.mouse_region_y):
            if event.type == "WHEELUPMOUSE":
                self.selected_index -= 1
                return True
            if event.type == "WHEELDOWNMOUSE":
                self.selected_index += 1
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
        
        operators = get_text_operators()
        self.correct_index(len(operators))
        
        editor_info = TextEditorInfo()
        scale = editor_info.scale
        
        box_position_info = self.get_operator_box_position_info(editor_info)  
        operator_box_rectangle = self.draw_operator_box(box_position_info, operators, scale)
        
        
        active_operator = self.get_active_operator(operators)
        attribute_info_position = (operator_box_rectangle.right + 10 * scale, operator_box_rectangle.top)
        self.draw_attribute_info_box(attribute_info_position, getattr(active_operator, "additional_data", None), scale)
    
        restore_opengl_defaults()
    
    def get_operator_box_position_info(self, editor_info):
        x, y = editor_info.cursor_position
        if y < editor_info.height / 2:
            align = "Bottom"
            y += 10 * editor_info.scale
        else:
            align = "Top"
            y -= 10 * editor_info.scale
        return x, y, align
        
    def draw_operator_box(self, position_info, operators, scale):
        box_width = 300 * scale
        padding = 8 * scale
        background_color = (0.8, 0.8, 0.8, 1.0)
        text_color = (0.2, 0.2, 0.2, 1.0)
        selection_color = (1.0, 1.0, 1.0, 1.0)
        border_color = (0.05, 0.05, 0.05, 1.0)
        border_thickness = 3 * scale
        x, y, align = position_info
        element_height = 26 * scale
        text_size = 100 * scale
        box_height = min(len(operators), get_line_amount()) * element_height + 2 * padding
    
        if align == "Top":
            outer_rectangle = Rectangle(x, y, box_width, box_height)
        else: outer_rectangle = Rectangle(x, y + box_height, box_width, box_height)
        draw_rectangle(outer_rectangle, color = background_color)
        self.operator_box_rectangle = outer_rectangle
        
        padding_rectangle = outer_rectangle.get_inset_rectangle(padding)
        
        self.operator_line_rectangles = []
        for i, operator in enumerate(operators):
            if not self.top_index <= i <= self.bottom_index: continue
            draw_index = i - self.top_index
            line_rectangle = self.get_operator_line_rectangle(outer_rectangle, padding_rectangle, element_height, draw_index)
            if i == self.selected_index:
                draw_rectangle(line_rectangle, color = selection_color)
            text_draw_rectangle = self.get_text_draw_rectangle(padding_rectangle, element_height, draw_index)
            self.draw_operator_in_rectangle(operator, text_draw_rectangle, text_size, text_color)
            self.operator_line_rectangles.append(line_rectangle)
            
        draw_rectangle_border(outer_rectangle, color = border_color, thickness = border_thickness)
        
        return outer_rectangle
   
    def get_operator_line_rectangle(self, outer_rectangle, padding_rectangle, element_height, draw_index):
        line_rectangle = Rectangle(
            x = outer_rectangle.left,
            y = padding_rectangle.top - draw_index * element_height,
            width = outer_rectangle.width,
            height = element_height)
        return line_rectangle
        
    def get_text_draw_rectangle(self, padding_rectangle, element_height, draw_index):
        draw_rectangle = Rectangle(
            x = padding_rectangle.left,
            y = padding_rectangle.top - draw_index * element_height,
            width = padding_rectangle.width,
            height = element_height)
        return draw_rectangle
        
    def draw_operator_in_rectangle(self, operator, rectangle, text_size, color):
        text = operator.display_name
        position = (rectangle.left, rectangle.bottom + rectangle.height / 4)
        draw_text(text, position, text_size, color = color)
        
        
    def draw_attribute_info_box(self, position, attribute, scale):
        if isinstance(attribute, PropertyDocumentation):
            self.draw_property_info_box(position, attribute, scale)
        
    def draw_property_info_box(self, position, property, scale):
        box_width = 400 * scale
        box_height = 200 * scale
        padding = 8 * scale
        text_size = 100 * scale
        line_height = 25 * scale
        text_color = (0.2, 0.2, 0.2, 1.0)
        
        outer_rectangle = Rectangle(position[0], position[1], box_width, box_height)
        draw_rectangle(outer_rectangle)
        
        padding_rectangle = outer_rectangle.get_inset_rectangle(padding)
        
        text_x = padding_rectangle.left
        
        owner_text_y = padding_rectangle.top - line_height
        draw_text(str(property), (text_x, owner_text_y), size = text_size, color = text_color)
        
        type_text_y = padding_rectangle.top - 2 * line_height
        draw_text("  " + property.type, (text_x, type_text_y), size = text_size, color = text_color)
        
        description_y = padding_rectangle.top - 4 * line_height
        draw_text_block(property.description, (text_x, description_y), size = text_size, block_width = padding_rectangle.width, line_height = line_height, color = text_color)
   
    @property
    def selected_operator(self):
        operators = get_text_operators()
        return self.get_active_operator(operators)
        
    def get_active_operator(self, operators):
        self.correct_index(len(operators))
        try: return operators[self.selected_index]
        except: return None
        
    def correct_index(self, amount):
        self.selected_index = clamp(self.selected_index, 0, max(amount - 1, 0))
        self.top_index = clamp(self.top_index, 0, amount - 1)
        self.top_index = clamp(self.top_index, self.selected_index - get_line_amount() + 1, self.selected_index)
      
def get_line_amount():
    preferences = get_addon_preferences()
    if preferences is None: return 8
    else: return preferences.line_amount
def get_addon_preferences():
    addon = bpy.context.user_preferences.addons.get("script_auto_complete")
    if addon is None: return None
    else: return addon.preferences
      
    
def is_event_current_region(event):
    region = bpy.context.region
    viewport = Rectangle(0, region.height, region.width, region.height)
    return viewport.contains(event.mouse_region_x, event.mouse_region_y)
