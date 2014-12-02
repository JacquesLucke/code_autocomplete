import bpy
from script_auto_complete.text_editor_utils import *
        
word_characters = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_")
random_select_sequence = "random select sequence"
class ExtendWordOperator:
    def __init__(self, target_word, description = ""):
        self.target_word = target_word
        self.display_name = target_word
        self.description = description
        self.align = "LEFT"
        
    def execute(self, text_block):
        text_line = text_block.current_line
        character_index = text_block.current_character
        
        text = text_line.body
        word_start_index = get_word_start_index(text, character_index)
        
        new_text = text[:word_start_index] + self.target_word + random_select_sequence + text[character_index:]
        text_line.body = new_text
        select_text_by_replacing(random_select_sequence)
        
def get_word_start_index(text, character_index):
    for i in reversed(range(0, character_index)):
        if text[i].upper() not in word_characters:
            return i + 1
    return 0

class InsertTextOperator:
    def __init__(self, name, text, description = ""):
        self.display_name = name
        self.insert_text = text
        self.description = description
        self.align = "CENTER"
        
    def execute(self, text_block):
        line_index = text_block.current_line_index
        text_parts = []
        for i, text_line in enumerate(text_block.lines):
            text_parts.append(text_line.body)
            if i == line_index:
                text_parts.append(self.insert_text + random_select_sequence)
        text = "\n".join(text_parts)
        text_block.from_string(text)
        select_text_by_replacing(random_select_sequence)
        