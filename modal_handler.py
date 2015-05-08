import bpy, os
from . text_block import TextBlock
from . graphics import *
from . text_editor_utils import *
from . text_operators import *
from . operators.operator_hub import get_text_operators
from . operators.extend_word_operators import update_word_list
from . documentation import *

class BlockEvent(Exception):
    pass

show_event_types = ["BACK_SPACE", "PERIOD", "SPACE", "COMMA", "ZERO", "ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN", "EIGHT", "NINE",
    "DEL", "SEMI_COLON", "MINUS", "RIGHT_BRACKET", "LEFT_BRACKET", "SLASH"] + \
    list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
hide_event_types = ["RET", "LEFTMOUSE", "LEFT_ARROW", "RIGHT_ARROW"]

class ModalHandler:
    def __init__(self):
        self._handle = bpy.types.SpaceTextEditor.draw_handler_add(self.draw, (), "WINDOW", "POST_PIXEL")
        self.auto_complete_box = AutoCompleteTextBox()
        
    def free(self):
        bpy.types.SpaceTextEditor.draw_handler_remove(self._handle, "WINDOW")
        
    def update(self, event):
        region = get_region_under_mouse(event)
        if region is None: return
        
        update_functions = [self.auto_complete_box.update]
        try:
            for update_function in update_functions:
                update_function(event)
            return False
        except BlockEvent: return True
        
    def draw(self):    
        self.auto_complete_box.draw()
      
        
class AutoCompleteTextBox:
    def __init__(self):
        self.selected_index = 0
        self.top_index = 3
        self.line_amount = 8
        self.operator_line_rectangles = []
        self.operator_box_rectangle = Rectangle(0, 0, 0, 0)
        
        self.background_color = (1.0, 1.0, 1.0, 1.0)
        self.border_color = (0.9, 0.76, 0.4, 1.0)
        self.text_color = (0.1, 0.1, 0.1, 1.0)
        self.selection_color = (0.95, 0.95, 1.0, 1.0)
        self.selection_border_color = (1.0, 0.8, 0.5, 1.0)
        
        self.info_background_color = (0.95, 0.96, 0.97, 1.0)
        self.info_border_color = (1.0, 0.8, 0.5, 1.0)
        
        
        self.hide = True
        
    def update(self, event):
        self.update_show(event)
        if self.hide or not is_event_in_text_editor(event): return
        self.update_operator_selection(event)
        self.update_operator_execution(event)
        self.update_hide(event)
        
    def update_show(self, event):
        if self.hide and event.value == "PRESS" and not event.ctrl and is_event_in_text_editor(event):
            if event.type in show_event_types:
                self.show_reset()
            if event.type in ["LEFT_ALT", "RIGHT_ALT"]:
                self.show_reset()
                raise BlockEvent()
            
    def show_reset(self):
        self.hide = False
        self.selected_index = 0
        update_word_list(TextBlock(bpy.context.space_data.text))
            
    def update_hide(self, event):  
        if event.type in hide_event_types:
            self.hide = True
        if event.type in ["LEFT_ALT", "RIGHT_ALT"] and event.value == "PRESS":
            self.hide = True
        
    def update_operator_selection(self, event):
       self.move_selection_with_keys(event)
       self.move_selection_with_mouse_wheel(event)
       
    selection_move_keys = {
        "DOWN_ARROW" : 1,
        "UP_ARROW" : -1,
        "PAGE_DOWN" : 4,
        "PAGE_UP" : -4,
        "END" : 10000,
        "HOME" : -10000}
       
    def move_selection_with_keys(self, event):
        if event.value == "PRESS":
            for key, move in self.selection_move_keys.items():
                if event.type == key:
                    self.selected_index += move
                    raise BlockEvent()
                
    def move_selection_with_mouse_wheel(self, event):
        if self.operator_box_rectangle.contains(event.mouse_region_x, event.mouse_region_y):
            if event.type == "WHEELUPMOUSE":
                self.selected_index -= 1
                raise BlockEvent()
            if event.type == "WHEELDOWNMOUSE":
                self.selected_index += 1
                raise BlockEvent()
        
    def update_operator_execution(self, event):
        self.execute_if_tab_is_pressed(event)
        self.execute_on_mouse_click(event)   
                    
    def execute_if_tab_is_pressed(self, event):
        if event.type == "TAB" and event.value == "PRESS":
            self.execute_selected_operator()
            self.hide = True
            raise BlockEvent()
            
    def execute_on_mouse_click(self, event):
        if event.type == "LEFTMOUSE" and event.value == "PRESS":
            for i, line_rectangle in enumerate(self.operator_line_rectangles):
                if line_rectangle.contains(event.mouse_region_x, event.mouse_region_y):
                    self.selected_index = self.top_index + i
                    self.execute_selected_operator()
                    self.hide = True
                    raise BlockEvent()
        
    def execute_selected_operator(self):
        try:
            operator = self.selected_operator
            if operator:
                operator.execute(TextBlock(bpy.context.space_data.text))
        except Exception as e: print(e)
        
    @property
    def bottom_index(self):
        return self.top_index + get_line_amount() - 1
         
    def draw(self):
        if self.hide: return
        
        operators = get_text_operators(get_active_text_block())
        self.correct_index(len(operators))
        if len(operators) == 0: return
        active_operator = self.get_active_operator(operators)
        
        editor_info = TextEditorInfo()
        scale = editor_info.scale
        
        box_position_info = self.get_operator_box_position_info(editor_info)  
        operator_box_rectangle = self.draw_operator_box(box_position_info, operators, scale)
         
        attribute_info_position = (operator_box_rectangle.right + 10 * scale, operator_box_rectangle.top)
        self.draw_attribute_info_box(attribute_info_position, getattr(active_operator, "additional_data", None), scale)
    
        restore_opengl_defaults()
    
    def get_operator_box_position_info(self, editor_info):
        x, y = editor_info.cursor_position
        if y < editor_info.height / 3:
            align = "Bottom"
            y += 20 * editor_info.scale
        else:
            align = "Top"
            y -= 20 * editor_info.scale
        return x, y, align
        
    def draw_operator_box(self, position_info, operators, scale):
        box_width = 300 * scale
        padding = 8 * scale
        x, y, align = position_info
        line_height = 26 * scale
        text_size = 100 * scale
        box_height = min(len(operators), get_line_amount()) * line_height + 2 * padding
    
        if align == "Top":
            outer_rectangle = Rectangle(x, y, box_width, box_height)
        else: outer_rectangle = Rectangle(x, y + box_height, box_width, box_height)
        draw_rectangle(outer_rectangle, color = self.background_color)
        self.operator_box_rectangle = outer_rectangle
        
        padding_rectangle = outer_rectangle.get_inset_rectangle(padding)
        
        self.operator_line_rectangles = []
        for draw_index, operator in enumerate(operators[self.top_index:self.bottom_index+1]):
            operator_index = self.top_index + draw_index
            line_rectangle = self.get_operator_line_rectangle(outer_rectangle, padding_rectangle, line_height, draw_index)
            self.operator_line_rectangles.append(line_rectangle)
            
            if operator_index == self.selected_index:
                draw_rectangle(line_rectangle, color = self.selection_color)
                draw_rectangle_border(line_rectangle, thickness = 1, color = self.selection_border_color)
                
            operator_label = Label()
            operator_label.text = operator.display_name
            operator_label.color = self.text_color
            operator_label.text_size = text_size
            operator_label.max_lines = 1
            operator_label.font_id = 1
            
            label_position = [
                line_rectangle.left + padding,
                line_rectangle.top - line_height / 4 * 3 ]
            if operator.align == "CENTER": label_position[0] = line_rectangle.left + (line_rectangle.width - operator_label.get_draw_dimensions()[0]) / 2
            if operator.align == "INSET": label_position[0] = label_position[0] + padding
            operator_label.draw(label_position)
            
        draw_rectangle_border(outer_rectangle, color = self.border_color, thickness = 1)
        
        return outer_rectangle
   
    def get_operator_line_rectangle(self, outer_rectangle, padding_rectangle, line_height, draw_index):
        line_rectangle = Rectangle(
            x = outer_rectangle.left,
            y = padding_rectangle.top - draw_index * line_height,
            width = outer_rectangle.width,
            height = line_height)
        return line_rectangle
        
    def get_text_draw_rectangle(self, padding_rectangle, line_height, draw_index):
        draw_rectangle = Rectangle(
            x = padding_rectangle.left,
            y = padding_rectangle.top - draw_index * line_height,
            width = padding_rectangle.width,
            height = line_height)
        return draw_rectangle
        
    def draw_operator_in_rectangle(self, operator, rectangle, text_size, color):
        text = operator.display_name
        position = [rectangle.left, rectangle.bottom + rectangle.height / 4]
        if operator.align == "CENTER":
            dimensions = get_text_dimensions(text, text_size)
            position[0] += (rectangle.width - dimensions[0]) / 2
        draw_text(text, position, text_size, color = color)
        
        
    def draw_attribute_info_box(self, position, attribute, scale):
        if isinstance(attribute, PropertyDocumentation):
            self.draw_property_info_box(position, attribute, scale)
        elif isinstance(attribute, FunctionDocumentation):
            self.draw_function_info_box(position, attribute, scale)
        elif isinstance(attribute, WordDescription):
            self.draw_description_box(position, attribute, scale)
        elif isinstance(attribute, OperatorDocumentation):
            self.draw_operator_info_box(position, attribute, scale)
        
    def draw_property_info_box(self, position, property, scale):
        box_width = 400 * scale
        box_height = 300 * scale
        padding = 8 * scale
        text_size = 100 * scale
        line_height = 25 * scale
        
        owner_label = Label()
        owner_label.text = str(property)
        owner_label.color = self.text_color
        owner_label.text_size = text_size
        owner_label.max_lines = 1
        owner_label.font_id = 1
        owner_dimensions = owner_label.get_draw_dimensions()

        type_label = Label()
        type_label.text = "  " + property.type
        if property.is_readonly: type_label.text += "  -  readonly"
        type_label.color = self.text_color
        type_label.text_size = text_size
        type_label.max_lines = 1
        type_label.font_id = 1
        type_dimensions = type_label.get_draw_dimensions()
        
        box_width = max(350 * scale, owner_dimensions[0], type_dimensions[0])
        
        description_label = Label()
        description_label.text = property.description
        description_label.color = self.text_color
        description_label.text_size = text_size
        description_label.max_lines = 15
        description_label.font_id = 0
        description_label.line_height = line_height
        description_label.width = box_width
        description_line_amount = len(description_label.get_draw_lines())
        description_dimensions = description_label.get_draw_dimensions()
        
        
        box_width += 2 * padding
        box_height = owner_dimensions[1] + \
            type_dimensions[1] + \
            description_dimensions[1] + \
            line_height * 2.5
            
        if property.type == "Enum":
            enum_items_label = Label()
            enum_items_label.text = str(property.enum_items)
            enum_items_label.color = self.text_color
            enum_items_label.text_size = text_size * 0.9
            enum_items_label.max_lines = 15
            enum_items_label.font_id = 1
            enum_items_label.line_height = line_height * 0.9
            enum_items_label.width = box_width
            enum_items_dimensions = enum_items_label.get_draw_dimensions()
            
            box_height += enum_items_dimensions[1]
        
        outer_rectangle = Rectangle(position[0], position[1], box_width, box_height)
        draw_rectangle(outer_rectangle, color = self.info_background_color)
        
        
        owner_position = [
            outer_rectangle.left + padding,
            outer_rectangle.top - padding - line_height / 4 * 3 ]
        owner_label.draw(owner_position)
        
        type_position = [
            owner_position[0],
            owner_position[1] - line_height ]
        type_label.draw(type_position)
        
        description_position = [
            owner_position[0],
            type_position[1] - line_height * 1.5 ]
        description_label.draw(description_position)
        
        if property.type == "Enum":
            enum_items_position = [
                owner_position[0],
                description_position[1] - line_height * (description_line_amount + 0.5) ]
            enum_items_label.draw(enum_items_position)
        
        draw_rectangle_border(outer_rectangle, thickness = 1, color = self.info_border_color)
   
    def draw_function_info_box(self, position, function, scale):
        text_size = 100 * scale
        padding = 8 * scale
        box_height = 200 * scale
        line_height = 25 * scale
        
        owner_label = Label()
        owner_label.text = function.owner + "." + function.name + "(" + ", ".join(function.get_input_names()) + ")"
        owner_label.color = self.text_color
        owner_label.text_size = text_size
        owner_label.max_lines = 1
        owner_label.font_id = 1
        owner_dimensions = owner_label.get_draw_dimensions()
        
        return_label = Label()
        return_names = function.get_output_names()
        if len(return_names) == 0: return_label.text = " > None"
        else: return_label.text = " > " + ", ".join(return_names)
        return_label.color = self.text_color
        return_label.text_size = text_size
        return_label.max_lines = 1
        return_label.font_id = 1
        return_dimensions = return_label.get_draw_dimensions()
        
        box_width = max(350 * scale, owner_dimensions[0], return_dimensions[0])
        
        description_label = Label()
        description_label.text = function.description
        description_label.color = self.text_color
        description_label.text_size = text_size
        description_label.max_lines = 15
        description_label.font_id = 0
        description_label.line_height = line_height
        description_label.width = box_width
        description_line_amount = len(description_label.get_draw_lines())
        description_dimensions = description_label.get_draw_dimensions()
        
        box_width += 2 * padding
        box_height = owner_dimensions[1] + \
            return_dimensions[1] + \
            description_dimensions[1] + \
            2 * line_height
            
                
        outer_rectangle = Rectangle(position[0], position[1], box_width, box_height)
        draw_rectangle(outer_rectangle, color = self.info_background_color)
        
        owner_position = [
            outer_rectangle.left + padding,
            outer_rectangle.top - padding - line_height / 4 * 3 ]
        owner_label.draw(owner_position)
        
        return_position = [
            owner_position[0],
            owner_position[1] - line_height ]
        return_label.draw(return_position)
        
        description_position = [
            owner_position[0],
            return_position[1] - line_height * 1.5 ]
        description_label.draw(description_position)
        
        draw_rectangle_border(outer_rectangle, thickness = 1, color = self.info_border_color)
        
    def draw_description_box(self, position, word_description, scale):
        text_size = 100 * scale
        padding = 8 * scale
        line_height = 25 * scale
        box_width = 350 * scale
        
        description_label = Label()
        description_label.text = word_description.description
        description_label.color = self.text_color
        description_label.text_size = text_size
        description_label.max_lines = 15
        description_label.font_id = 0
        description_label.line_height = line_height
        description_label.width = box_width
        description_dimensions = description_label.get_draw_dimensions()
        
        box_width = 2 * padding + description_dimensions[0]
        box_height = 2 * padding + description_dimensions[1]
        outer_rectangle = Rectangle(position[0], position[1], box_width, box_height)
        draw_rectangle(outer_rectangle, color = self.info_background_color)
        
        description_position = [
            outer_rectangle.left + padding,
            outer_rectangle.top - padding - line_height / 4 * 3 ]
        description_label.draw(description_position)
        
        draw_rectangle_border(outer_rectangle, thickness = 1, color = self.info_border_color)
        
    def draw_operator_info_box(self, position, operator, scale):
        text_size = 100 * scale
        padding = 8 * scale
        line_height = 25 * scale
        box_width = 350 * scale
        
        header_label = Label()
        header_label.text = operator.name + "(...)"
        header_label.color = self.text_color
        header_label.text_size = text_size
        header_label.font_id = 1
        header_width = header_label.get_draw_dimensions()[0]
        
        box_width = max(500 * scale, header_width)
        
        
        description_label = Label()
        description_label.text = operator.description
        description_label.color = self.text_color
        description_label.max_lines = 15
        description_label.text_size = text_size
        description_label.font_id = 0
        description_label.line_height = line_height
        description_label.width = box_width
        description_dimensions = description_label.get_draw_dimensions()
        
        input_labels = []
        inputs_height = 0
        for input in operator.inputs:
            input_name_label = Label()
            input_name_label.text = input.name + "  -  " + input.type
            input_name_label.color = self.text_color
            input_name_label.text_size = text_size * 0.97
            input_name_label.font_id = 1
            
            input_description_label = Label()
            input_description_label.text = input.description
            input_description_label.text_size = text_size * 0.92
            input_description_label.color = self.text_color
            input_description_label.max_lines = 5
            input_description_label.line_height = line_height
            input_description_label.width = box_width - padding
            input_description_label.font_id = 0
            input_description_height = input_description_label.get_draw_dimensions()[1]
            
            input_labels.append((input_name_label, input_description_label, input_description_height))
            inputs_height += line_height * 1.3 + input_description_height
        
        box_width += 3 * padding
        box_height = 3 * padding + description_dimensions[1] + inputs_height + line_height
        
        outer_rectangle = Rectangle(position[0], position[1], box_width, box_height)
        draw_rectangle(outer_rectangle, color = self.info_background_color)
        
        header_position = [
            outer_rectangle.left + padding,
            outer_rectangle.top - padding - line_height / 4 * 3 ]
        header_label.draw(header_position)
        
        description_position = [
            header_position[0] + padding,
            header_position[1] - line_height * 1.2 ]
        description_label.draw(description_position)
        
        input_name_position = [ header_position[0], description_position[1] - description_dimensions[1] * 1.2 ]
        input_description_position = [ description_position[0], input_name_position[1] - line_height ]
        for input_name_label, input_description_label, input_description_height in input_labels:
            input_name_label.draw(input_name_position)
            input_description_label.draw(input_description_position)
            
            y_offset = line_height * 1.3 + input_description_height
            input_name_position[1] -= y_offset
            input_description_position[1] -= y_offset
            
        draw_rectangle_border(outer_rectangle, thickness = 1, color = self.info_border_color)
   
    @property
    def selected_operator(self):
        operators = get_text_operators(get_active_text_block())
        return self.get_active_operator(operators)
        
    def get_active_operator(self, operators):
        self.correct_index(len(operators))
        try: return operators[self.selected_index]
        except: return None
        
    def correct_index(self, amount):
        self.selected_index = clamp(self.selected_index, 0, max(amount - 1, 0))
        self.top_index = clamp(self.top_index, 0, max(amount - get_line_amount() - 1, 0))
        self.top_index = clamp(self.top_index, self.selected_index - get_line_amount() + 1, self.selected_index)
      
def get_line_amount():
    preferences = get_addon_preferences()
    if preferences is None: return 8
    else: return preferences.line_amount
def get_addon_preferences():
    addon = bpy.context.user_preferences.addons.get(get_addon_name())
    if addon is None: return None
    else: return addon.preferences
    
def clamp(value, min_value, max_value):
    return min(max(value, min_value), max_value)    
      
def get_active_text_block():
    return TextBlock(bpy.context.space_data.text)
    
def is_event_in_text_editor(event):
    area = get_area_under_mouse(event)
    if area is None: return False
    return area.type == "TEXT_EDITOR"
    
def get_region_under_mouse(event):
    x = event.mouse_prev_x
    y = event.mouse_prev_y
    for region in iterate_regions():
        if region.x < x < region.x + region.width and region.y < y < region.y + region.height:
            return region
    
def iterate_regions():
    for area in bpy.context.screen.areas:
        for region in area.regions:
            yield region  

def get_area_under_mouse(event):
    x = event.mouse_prev_x
    y = event.mouse_prev_y
    for area in bpy.context.screen.areas:
        if area.x < x < area.x + area.width and area.y < y < area.y + area.height:
            return area

def get_addon_name():
    return os.path.basename(os.path.dirname(__file__))            