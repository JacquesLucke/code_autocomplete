import bpy, keyword, inspect
from script_auto_complete.text_editor_utils import *
from script_auto_complete.text_operators import *

words = []

def get_extend_word_operators():
    operators = []
    word_start = get_word_start().upper()
    for word in words:
        if word.upper().startswith(word_start):
            operators.append(ExtendWordOperator(word))
    return operators
    
    
blender_names = ["register", "unregister", "default", "bl_info"]

def update_word_list():
    global words
    words = []
    words.extend(get_existing_words())
    words.extend(keyword.kwlist)
    words.extend(dir(__builtins__))
    words.extend(blender_names)
    words = list(set(words))
    words.sort(key = str.lower)
