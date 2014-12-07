import bpy
from script_auto_complete.text_editor_utils import *
        
word_characters = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_")
random_select_sequence = "!*_*_*!"
class ExtendWordOperator:
    def __init__(self, target_word, description = "", additional_data = None):
        self.target_word = target_word
        self.display_name = target_word
        self.description = description
        self.additional_data = additional_data
        self.align = "LEFT"
        
    def execute(self, text_block):
        text_line = text_block.current_line
        character_index = text_block.current_character
        
        text = text_line.body
        word_start_index = get_word_start_index(text, character_index)
        
        new_text = text[:word_start_index] + self.target_word + text[character_index:]
        text_line.body = new_text
        set_text_cursor_position(text_block.current_line_index, len(text[:word_start_index] + self.target_word))


class InsertTextOperator:
    def __init__(self, name, text, description = ""):
        self.display_name = name
        self.insert_text = text
        self.description = description
        self.align = "CENTER"
        
    def execute(self, text_block):
        line_index = text_block.current_line_index
        character_index = text_block.current_character
        text_parts = []
        for i, text_line in enumerate(text_block.lines):
            if i == line_index:
                text_parts.append(text_line.body[:character_index] + self.insert_text + text_line.body[character_index:])
            else:
                text_parts.append(text_line.body + "\n")
        text = "".join(text_parts)
        text_block.from_string(text)
        
        set_text_cursor_position(line_index, character_index)
        
        

          
        