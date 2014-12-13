import bpy
from script_auto_complete.text_editor_utils import *
        
        
class ExtendWordOperator:
    def __init__(self, target_word, description = "", additional_data = None):
        self.target_word = target_word
        self.display_name = target_word
        self.description = description
        self.additional_data = additional_data
        self.align = "LEFT"
        
    def execute(self, text_block):        
        word_start = get_word_start()
        delete_last_characters(len(word_start))
        bpy.ops.text.insert(text = self.target_word)


class InsertTextOperator:
    def __init__(self, name, text, description = ""):
        self.display_name = name
        self.insert_text = text
        self.description = description
        self.align = "CENTER"
        
    def execute(self, text_block):
        bpy.ops.text.insert(text = self.insert_text)
        
        

          
        