import bpy, keyword
from script_auto_complete.text_editor_utils import *
from script_auto_complete.operators.text_operators import *
from script_auto_complete.operators.context_words import *


def get_context_word_operators():
    operators = []
    text_before = get_text_since_last_dot()
    word_start = get_word_start()
    pairs = get_before_after_pairs()
    for before, after_list in pairs.items():
        if text_before.endswith(before):
            for after in after_list:
                if after.startswith(word_start):
                    operators.append(ExtendWordOperator(after))
    return operators

def get_text_since_last_dot():
    text_block = bpy.context.space_data.text
    text_line = text_block.current_line
    character_index = text_block.current_character
    line = text_line.body[:character_index]
    index = line.rfind(".")
    if index > 0:
        line = line[:index]
    return line
    
def get_word_start():
    text_block = bpy.context.space_data.text
    text_line = text_block.current_line
    text = text_line.body
    character_index = text_block.current_character
    return text[get_word_start_index(text, character_index):character_index]
    
word_characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789"
def get_word_start_index(text, character_index):
    for i in reversed(range(0, character_index)):
        if text[i].upper() not in word_characters:
            return i + 1
    return 0
    