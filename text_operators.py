import bpy
from script_auto_complete.text_editor_utils import *
from script_auto_complete.expression_utils import *
        
        
class ExtendWordOperator:
    def __init__(self, target_word, additional_data = None):
        self.target_word = target_word
        self.display_name = target_word
        self.additional_data = additional_data
        self.align = "LEFT"
        
    def execute(self, text_block):
        text_block.replace_current_word(self.target_word)


class InsertTextOperator:
    def __init__(self, name, text):
        self.display_name = name
        self.insert_text = text
        self.align = "CENTER"
        
    def execute(self, text_block):
        text_block.insert(self.insert_text)
        
        
class DynamicSnippetOperator:
    def __init__(self, name, insert_snippet_function):
        self.display_name = name
        self.insert_snippet_function = insert_snippet_function
        self.align = "CENTER"
        
    def execute(self, text_block):
        self.insert_snippet_function(text_block)
        
        
def select_string_definition():
    text_block = bpy.context.space_data.text
    character_index = text_block.current_character
    line = text_block.current_line.body
    
    string_letter = get_string_definition_type(line, character_index)
    if string_letter is None: return
    start, end = get_range_surrounded_by_letter(line, string_letter, character_index)
    if start != end:
        set_selection_in_line(start, end)
 
def get_string_definition_type(text, current_index):
    string_letter = None
    for i in range(current_index):
        letter = text[i]
        if letter == '"':
            if string_letter == '"':
                string_letter = None
            elif string_letter is None: 
                string_letter = letter
        if letter == "'":
            if string_letter == "'":
                string_letter = None
            elif string_letter is None: 
                string_letter = letter
    return string_letter

def get_range_surrounded_by_letter(text, letter, current_index):
    text_before = text[:current_index]
    text_after = text[current_index:]
    
    start_index = text_before.rfind(letter) + 1
    end_index = text_after.find(letter) + len(text_before)
    
    if 0 < start_index < end_index:
        return start_index, end_index
    return current_index, current_index   
    
def set_selection_in_line(start, end):
    line = bpy.context.space_data.text.current_line_index
    set_selection(line, start, line, end)
    
def set_selection(start_line, start_character, end_line, end_character):
    set_text_cursor_position(start_line, start_character, select = False)
    set_text_cursor_position(end_line, end_character, select = True)
    
def set_text_cursor_position(line_index, character_index, select = False):
    current_line_index = bpy.context.space_data.text.current_line_index
    line_changes = abs(current_line_index - line_index)
    
    if current_line_index > line_index: move_direction = "PREVIOUS_LINE"
    else: move_direction = "NEXT_LINE"
    
    for i in range(line_changes):
        move_cursor(move_direction, select)
        
    move_cursor("LINE_BEGIN", select)
    for i in range(character_index):
        move_cursor("NEXT_CHARACTER", select)
        if bpy.context.space_data.text.select_end_character >= character_index: break
        
def move_cursor(type, select = False):
    if select: bpy.ops.text.move_select(type = type)
    else: bpy.ops.text.move(type = type)
          
        