import bpy, re, keyword
from bgl import glBegin, glVertex2f, glEnd, GL_POLYGON
from script_auto_complete.draw_functions import *
from script_auto_complete.text_editor_utils import *
from script_auto_complete.utils import *
from script_auto_complete.text_operators import *

show_event_types = ["SPACE", "PERIOD"] + list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
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
            if event.type in show_event_types and event.value == "PRESS":
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
        if self.hide: return False
        
        if event.value == "PRESS":
            if event.type == "DOWN_ARROW":
                self.selected_index += 1
                return True
            if event.type == "UP_ARROW":
                self.selected_index -= 1
                return True
            if event.type == "TAB":
                operators = get_text_operators()
                operators[self.selected_index].execute(bpy.context.space_data.text)
                self.hide = True
                return True
        return False
        
    @property
    def bottom_index(self):
        return self.top_index + self.line_amount - 1
         
    def draw(self):
        if self.hide: return
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
        rectangle.move_down(10 * scale)
    
        draw_rectangle(rectangle)
        
        inner_rectangle = rectangle.get_inset_rectangle(padding)
        
        operators = get_text_operators()
        self.correct_index(operators)
        for i, operator in enumerate(operators):
            if i >= self.top_index and i < self.top_index + self.line_amount:
                index = i - self.top_index
                text_rectangle = Rectangle(inner_rectangle.left, inner_rectangle.top - index*element_height, inner_rectangle.width, real_element_height)
                if i == self.selected_index:
                    highlight_rectangle = Rectangle(rectangle.left, rectangle.top - index*element_height - element_height / 4, rectangle.width, element_height)
                    draw_rectangle(highlight_rectangle, color = (0.95, 0.95, 0.95, 1.0))
                draw_text_on_rectangle(operator.display_name, text_rectangle, size = text_size)
        
        draw_rectangle_border(rectangle, thickness = border_thickness)
        restore_opengl_defaults()
        
    def correct_index(self, operators):
        amount = len(operators)
        self.selected_index = clamp(self.selected_index, 0, amount - 1)
        self.top_index = clamp(self.top_index, 0, amount - 1)
        self.top_index = clamp(self.top_index, self.selected_index - self.line_amount + 1, self.selected_index)
        
  
def clamp(value, min_value, max_value):
    return min(max(value, min_value), max_value)
    
words = []
def update_word_list():
    global words
    words = []
    words.extend(find_all_existing_words())
    words.extend(keyword.kwlist)
    words = list(set(words))
    words.sort()

def find_all_existing_words():
    existing_words = []
    text = bpy.context.space_data.text.as_string()
    all_existing_words = set(re.sub("[^\w]", " ", text).split())
    for word in all_existing_words:
        if not word.isdigit(): existing_words.append(word)
    return existing_words
    
    
    
    
def get_text_operators():
    operators = []
    operators.extend(get_extend_word_operators())
    return operators
    
def get_extend_word_operators():
    operators = []
    word_start = get_word_start().upper()
    all_existing_words = words
    additional_existing_words = []
    for word in all_existing_words:
        if word.upper().startswith(word_start):
            operators.append(ExtendWordOperator(word))
        else:
            additional_existing_words.append(word)
    for word in additional_existing_words:
        operators.append(ExtendWordOperator(word))
    return operators
    
def get_word_start():
    text_block = bpy.context.space_data.text
    text_line = text_block.current_line
    text = text_line.body
    character_index = text_block.current_character
    return text[get_word_start_index(text, character_index):character_index]
    
def get_word_start_index(text, character_index):
    for i in reversed(range(0, character_index)):
        if text[i].upper() not in word_characters:
            return i + 1
    return 0
